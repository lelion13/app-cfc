from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import RolUsuario, Usuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.usuarios import UserCreate, UserOut, UserUpdate
from app.security.passwords import hash_password

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    return db.query(Usuario).order_by(Usuario.username.asc()).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    user = Usuario(username=body.username, password_hash=hash_password(body.password), rol=body.rol)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    db.refresh(user)
    return user


@router.patch("/{id_usuario}", response_model=UserOut)
def update_user(id_usuario: int, body: UserUpdate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    user = db.get(Usuario, id_usuario)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = body.model_dump(exclude_unset=True)
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id_usuario: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    user = db.get(Usuario, id_usuario)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(user)
    db.commit()
    return None
