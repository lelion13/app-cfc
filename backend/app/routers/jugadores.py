from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.models import Categoria, Jugador, Pago, RolUsuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.common import Page
from app.schemas.jugadores import JugadorCreate, JugadorOut, JugadorUpdate

router = APIRouter(prefix="/jugadores", tags=["jugadores"])


@router.get("", response_model=Page[JugadorOut])
def list_jugadores(id_categoria: int | None = None, activo: bool | None = None, q: str | None = Query(default=None, min_length=1, max_length=80), page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    base = db.query(Jugador).options(joinedload(Jugador.categoria))
    if id_categoria is not None:
        base = base.filter(Jugador.id_categoria == id_categoria)
    if activo is not None:
        base = base.filter(Jugador.activo == activo)
    if q:
        like = f"%{q}%"
        base = base.filter((Jugador.nombre.ilike(like)) | (Jugador.apellido.ilike(like)) | (Jugador.numero_documento.ilike(like)) | (Jugador.tipo_documento.ilike(like)))
    total = base.count()
    items = base.order_by(Jugador.apellido.asc(), Jugador.nombre.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return Page(items=items, page=page, page_size=page_size, total=total)


@router.post("", response_model=JugadorOut, status_code=status.HTTP_201_CREATED)
def create_jugador(body: JugadorCreate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    if not db.get(Categoria, body.id_categoria):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria not found")
    jugador = Jugador(**body.model_dump())
    db.add(jugador)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Jugador already exists")
    db.refresh(jugador)
    return jugador


@router.get("/{id_jugador}", response_model=JugadorOut)
def get_jugador(id_jugador: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    jugador = db.query(Jugador).options(joinedload(Jugador.categoria)).filter(Jugador.id_jugador == id_jugador).one_or_none()
    if not jugador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return jugador


@router.patch("/{id_jugador}", response_model=JugadorOut)
def update_jugador(id_jugador: int, body: JugadorUpdate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    jugador = db.get(Jugador, id_jugador)
    if not jugador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = body.model_dump(exclude_unset=True)
    if "id_categoria" in data and not db.get(Categoria, data["id_categoria"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria not found")
    for k, v in data.items():
        setattr(jugador, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Jugador already exists")
    db.refresh(jugador)
    return db.query(Jugador).options(joinedload(Jugador.categoria)).filter(Jugador.id_jugador == id_jugador).one()


@router.delete("/{id_jugador}", status_code=status.HTTP_204_NO_CONTENT)
def delete_jugador(id_jugador: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    jugador = db.get(Jugador, id_jugador)
    if not jugador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if db.query(Pago).filter(Pago.id_jugador == id_jugador).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Jugador has pagos")
    db.delete(jugador)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Jugador has pagos")
    return None
