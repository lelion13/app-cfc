from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.models import FechaPartido, GolPartido, Partido, RolUsuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.fechas_partido import FechaPartidoCreate, FechaPartidoOut, FechaPartidoUpdate
from app.schemas.partidos import FechaPartidoDetailOut

router = APIRouter(prefix="/fechas-partido", tags=["fechas-partido"])

ALL_ROLES = (RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador)
DELETE_ROLES = (RolUsuario.Admin, RolUsuario.Coordinador)


@router.get("", response_model=list[FechaPartidoOut])
def list_fechas(db: Session = Depends(get_db), _user=Depends(require_role(*ALL_ROLES))):
    rows = db.query(FechaPartido).order_by(FechaPartido.fecha_partido.desc()).all()
    return rows


@router.get("/{id_fecha_partido}", response_model=FechaPartidoDetailOut)
def get_fecha(id_fecha_partido: int, db: Session = Depends(get_db), _user=Depends(require_role(*ALL_ROLES))):
    f = (
        db.query(FechaPartido)
        .options(
            joinedload(FechaPartido.partidos).joinedload(Partido.fecha_encuentro),
            joinedload(FechaPartido.partidos).joinedload(Partido.categoria),
            joinedload(FechaPartido.partidos).joinedload(Partido.goles).joinedload(GolPartido.jugador),
        )
        .filter(FechaPartido.id_fecha_partido == id_fecha_partido)
        .one_or_none()
    )
    if not f:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    partidos_sorted = sorted(f.partidos, key=lambda p: (p.categoria.descripcion,))
    from app.routers import partidos as partidos_mod

    return FechaPartidoDetailOut(
        id_fecha_partido=f.id_fecha_partido,
        fecha_partido=f.fecha_partido,
        es_local=f.es_local,
        rival=f.rival,
        created_at=f.created_at,
        updated_at=f.updated_at,
        partidos=[partidos_mod._to_out(p) for p in partidos_sorted],
    )


@router.post("", response_model=FechaPartidoOut, status_code=status.HTTP_201_CREATED)
def create_fecha(body: FechaPartidoCreate, db: Session = Depends(get_db), _user=Depends(require_role(*ALL_ROLES))):
    f = FechaPartido(fecha_partido=body.fecha_partido, es_local=body.es_local, rival=body.rival.strip())
    db.add(f)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una fecha de encuentro para esa fecha",
        ) from None
    db.refresh(f)
    return f


@router.patch("/{id_fecha_partido}", response_model=FechaPartidoOut)
def update_fecha(id_fecha_partido: int, body: FechaPartidoUpdate, db: Session = Depends(get_db), _user=Depends(require_role(*ALL_ROLES))):
    f = db.get(FechaPartido, id_fecha_partido)
    if not f:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    patch = body.model_dump(exclude_unset=True)
    if "rival" in patch and patch["rival"] is not None:
        patch["rival"] = str(patch["rival"]).strip()
    for k, v in patch.items():
        if v is not None:
            setattr(f, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una fecha de encuentro para esa fecha",
        ) from None
    db.refresh(f)
    return f


@router.delete("/{id_fecha_partido}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fecha(id_fecha_partido: int, db: Session = Depends(get_db), _user=Depends(require_role(*DELETE_ROLES))):
    f = db.get(FechaPartido, id_fecha_partido)
    if not f:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(f)
    db.commit()
    return None
