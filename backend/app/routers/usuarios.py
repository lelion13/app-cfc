from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import RolUsuario, Usuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.usuarios import UserCreate, UserOut, UserUpdate
from app.services.caja import ensure_caja_for_user
from app.security.passwords import hash_password

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    return db.query(Usuario).order_by(Usuario.username.asc()).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    user = Usuario(username=body.username, password_hash=hash_password(body.password), rol=RolUsuario(body.rol))
    db.add(user)
    try:
        db.flush()
        ensure_caja_for_user(db, user.id_usuario)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    db.refresh(user)
    return user


@router.patch("/{id_usuario}", response_model=UserOut)
def update_user(
    id_usuario: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(RolUsuario.Admin)),
):
    user = db.get(Usuario, id_usuario)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = body.model_dump(exclude_unset=True)
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))
    new_rol = RolUsuario(data["rol"]) if "rol" in data else user.rol
    new_activo = data["activo"] if "activo" in data else user.activo
    if user.rol == RolUsuario.Admin and user.activo and (new_rol != RolUsuario.Admin or new_activo is False):
        others = (
            db.query(Usuario)
            .filter(
                Usuario.id_usuario != id_usuario,
                Usuario.rol == RolUsuario.Admin,
                Usuario.activo.is_(True),
            )
            .count()
        )
        if others == 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot remove last admin")
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(RolUsuario.Admin)),
):
    user = db.get(Usuario, id_usuario)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if user.id_usuario == current_user.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete self")
    if user.rol == RolUsuario.Admin and user.activo:
        others = (
            db.query(Usuario)
            .filter(
                Usuario.id_usuario != id_usuario,
                Usuario.rol == RolUsuario.Admin,
                Usuario.activo.is_(True),
            )
            .count()
        )
        if others == 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot remove last admin")
    db.delete(user)
    db.commit()
    return None
