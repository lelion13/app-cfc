from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.models import Categoria, FechaPartido, GolPartido, Jugador, Partido, RolUsuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.partidos import (
    CategoriaPartidoOut,
    FechaResumenOut,
    GoleadorLineIn,
    GoleadorLineOut,
    GoleadorTorneoOut,
    PartidoCreate,
    PartidoOut,
    PartidoUpdate,
)

router = APIRouter(prefix="/partidos", tags=["partidos"])

ALL_ROLES = (RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador)
DELETE_ROLES = (RolUsuario.Admin, RolUsuario.Coordinador)


def _sum_goleadores_lines(lines: list[GoleadorLineIn]) -> int:
    return sum(line.goles for line in lines)


def _sum_goles_atribuidos_db(db: Session, id_partido: int) -> int:
    r = db.query(func.coalesce(func.sum(GolPartido.goles), 0)).filter(GolPartido.id_partido == id_partido).scalar()
    return int(r or 0)


def _to_out(partido: Partido) -> PartidoOut:
    fe = partido.fecha_encuentro
    goleadores = [
        GoleadorLineOut(id_jugador=g.id_jugador, nombre=g.jugador.nombre, apellido=g.jugador.apellido, goles=g.goles)
        for g in sorted(partido.goles, key=lambda x: (x.jugador.apellido, x.jugador.nombre))
    ]
    cat = partido.categoria
    return PartidoOut(
        id_partido=partido.id_partido,
        id_fecha_partido=partido.id_fecha_partido,
        id_categoria=partido.id_categoria,
        hora_partido=partido.hora_partido,
        goles_nuestro=partido.goles_nuestro,
        goles_rival=partido.goles_rival,
        categoria=CategoriaPartidoOut(id_categoria=cat.id_categoria, descripcion=cat.descripcion),
        fecha=FechaResumenOut(
            id_fecha_partido=fe.id_fecha_partido,
            fecha_partido=fe.fecha_partido,
            es_local=fe.es_local,
            rival=fe.rival,
        ),
        goleadores=goleadores,
        created_at=partido.created_at,
        updated_at=partido.updated_at,
    )


def _validate_and_replace_goles(db: Session, partido: Partido, lines: list[GoleadorLineIn]) -> None:
    seen: set[int] = set()
    for line in lines:
        if line.id_jugador in seen:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Duplicate id_jugador in goleadores")
        seen.add(line.id_jugador)
        j = db.get(Jugador, line.id_jugador)
        if not j:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Jugador {line.id_jugador} not found")
        if j.id_categoria != partido.id_categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Jugador {line.id_jugador} no pertenece a la categoría del partido",
            )
    db.query(GolPartido).filter(GolPartido.id_partido == partido.id_partido).delete(synchronize_session=False)
    for line in lines:
        db.add(GolPartido(id_partido=partido.id_partido, id_jugador=line.id_jugador, goles=line.goles))


def _assert_atribuidos_vs_nuestro(db: Session, partido: Partido) -> None:
    total_attr = _sum_goles_atribuidos_db(db, partido.id_partido)
    if total_attr > partido.goles_nuestro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La suma de goles asignados a jugadores no puede superar los goles del equipo (contador)",
        )


def _load_partido(db: Session, id_partido: int) -> Partido | None:
    return (
        db.query(Partido)
        .options(
            joinedload(Partido.fecha_encuentro),
            joinedload(Partido.categoria),
            joinedload(Partido.goles).joinedload(GolPartido.jugador),
        )
        .filter(Partido.id_partido == id_partido)
        .one_or_none()
    )


@router.get("/goleadores", response_model=list[GoleadorTorneoOut])
def list_goleadores_campeonato(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    db: Session = Depends(get_db),
    _user=Depends(require_role(*ALL_ROLES)),
):
    q = (
        db.query(
            Jugador.id_jugador,
            Jugador.nombre,
            Jugador.apellido,
            func.sum(GolPartido.goles).label("goles_totales"),
        )
        .join(GolPartido, GolPartido.id_jugador == Jugador.id_jugador)
        .join(Partido, Partido.id_partido == GolPartido.id_partido)
        .join(FechaPartido, FechaPartido.id_fecha_partido == Partido.id_fecha_partido)
    )
    if fecha_desde is not None:
        q = q.filter(FechaPartido.fecha_partido >= fecha_desde)
    if fecha_hasta is not None:
        q = q.filter(FechaPartido.fecha_partido <= fecha_hasta)
    rows = (
        q.group_by(Jugador.id_jugador, Jugador.nombre, Jugador.apellido)
        .having(func.sum(GolPartido.goles) > 0)
        .order_by(func.sum(GolPartido.goles).desc(), Jugador.apellido.asc(), Jugador.nombre.asc())
        .all()
    )
    return [GoleadorTorneoOut(id_jugador=r.id_jugador, nombre=r.nombre, apellido=r.apellido, goles_totales=int(r.goles_totales)) for r in rows]


@router.get("", response_model=list[PartidoOut])
def list_partidos(
    id_fecha_partido: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _user=Depends(require_role(*ALL_ROLES)),
):
    q = db.query(Partido).options(
        joinedload(Partido.fecha_encuentro),
        joinedload(Partido.categoria),
        joinedload(Partido.goles).joinedload(GolPartido.jugador),
    )
    if id_fecha_partido is not None:
        q = q.filter(Partido.id_fecha_partido == id_fecha_partido)
    rows = q.order_by(Partido.id_partido.asc()).all()
    return [_to_out(p) for p in rows]


@router.get("/{id_partido}", response_model=PartidoOut)
def get_partido(id_partido: int, db: Session = Depends(get_db), _user=Depends(require_role(*ALL_ROLES))):
    p = _load_partido(db, id_partido)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return _to_out(p)


@router.post("", response_model=PartidoOut, status_code=status.HTTP_201_CREATED)
def create_partido(body: PartidoCreate, db: Session = Depends(get_db), _user=Depends(require_role(*ALL_ROLES))):
    if not db.get(FechaPartido, body.id_fecha_partido):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fecha de encuentro no encontrada")
    if not db.get(Categoria, body.id_categoria):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    if _sum_goleadores_lines(body.goleadores) > body.goles_nuestro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La suma de goles por jugador no puede superar goles_nuestro",
        )
    p = Partido(
        id_fecha_partido=body.id_fecha_partido,
        id_categoria=body.id_categoria,
        hora_partido=body.hora_partido,
        goles_nuestro=body.goles_nuestro,
        goles_rival=body.goles_rival,
    )
    db.add(p)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un partido para esa fecha y categoría",
        ) from None
    _validate_and_replace_goles(db, p, body.goleadores)
    _assert_atribuidos_vs_nuestro(db, p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot save partido") from None
    p2 = _load_partido(db, p.id_partido)
    assert p2 is not None
    return _to_out(p2)


@router.patch("/{id_partido}", response_model=PartidoOut)
def update_partido(id_partido: int, body: PartidoUpdate, db: Session = Depends(get_db), _user=Depends(require_role(*ALL_ROLES))):
    p = db.get(Partido, id_partido)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    patch = body.model_dump(exclude_unset=True)
    goleadores_in = patch.pop("goleadores", None)

    new_goles_nuestro = patch["goles_nuestro"] if "goles_nuestro" in patch else p.goles_nuestro
    if goleadores_in is not None:
        lines = [GoleadorLineIn(**x) for x in goleadores_in]
        future_sum_attr = _sum_goleadores_lines(lines)
    else:
        lines = []
        future_sum_attr = _sum_goles_atribuidos_db(db, id_partido)

    if new_goles_nuestro < future_sum_attr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede dejar goles_nuestro por debajo de los goles asignados a jugadores",
        )

    for k, v in patch.items():
        setattr(p, k, v)
    if goleadores_in is not None:
        _validate_and_replace_goles(db, p, lines)

    db.flush()
    _assert_atribuidos_vs_nuestro(db, p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al guardar el partido",
        ) from None
    p2 = _load_partido(db, id_partido)
    assert p2 is not None
    return _to_out(p2)


@router.delete("/{id_partido}", status_code=status.HTTP_204_NO_CONTENT)
def delete_partido(id_partido: int, db: Session = Depends(get_db), _user=Depends(require_role(*DELETE_ROLES))):
    p = db.get(Partido, id_partido)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(p)
    db.commit()
    return None
