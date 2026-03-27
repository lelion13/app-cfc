from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Categoria, RolUsuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.categorias import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaOut])
def list_categorias(q: str | None = Query(default=None, min_length=1, max_length=80), db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    qry = db.query(Categoria)
    if q:
        qry = qry.filter(Categoria.descripcion.ilike(f"%{q}%"))
    return qry.order_by(Categoria.descripcion.asc()).all()


@router.post("", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def create_categoria(body: CategoriaCreate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    cat = Categoria(descripcion=body.descripcion)
    db.add(cat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria already exists")
    db.refresh(cat)
    return cat


@router.get("/{id_categoria}", response_model=CategoriaOut)
def get_categoria(id_categoria: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    cat = db.get(Categoria, id_categoria)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return cat


@router.patch("/{id_categoria}", response_model=CategoriaOut)
def update_categoria(id_categoria: int, body: CategoriaUpdate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    cat = db.get(Categoria, id_categoria)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if body.descripcion is not None:
        cat.descripcion = body.descripcion
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria already exists")
    db.refresh(cat)
    return cat


@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(id_categoria: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    cat = db.get(Categoria, id_categoria)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(cat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria has jugadores")
    return None
