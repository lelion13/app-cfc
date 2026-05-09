import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import RolUsuario, Usuario
from app.db.session import get_db
from app.deps.auth import get_current_user
from app.schemas.auth import BootstrapRequest, BootstrapStatusOut, LoginRequest, TokenResponse
from app.schemas.usuarios import UserOut
from app.services.caja import ensure_caja_for_user
from app.security.jwt import create_access_token
from app.security.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _setup_token_configured() -> bool:
    return bool(settings.setup_token and len(settings.setup_token.strip()) >= 8)


@router.get("/bootstrap-status", response_model=BootstrapStatusOut)
def bootstrap_status(db: Session = Depends(get_db)) -> BootstrapStatusOut:
    n = db.query(func.count(Usuario.id_usuario)).scalar() or 0
    allowed = n == 0 and _setup_token_configured()
    return BootstrapStatusOut(allowed=allowed)


@router.post("/bootstrap", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def bootstrap(body: BootstrapRequest, db: Session = Depends(get_db)) -> Usuario:
    n = db.query(func.count(Usuario.id_usuario)).scalar() or 0
    if n > 0 or not _setup_token_configured():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bootstrap not available")
    try:
        token_ok = secrets.compare_digest(body.setup_token, settings.setup_token or "")
    except ValueError:
        token_ok = False
    if not token_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user = Usuario(username=body.username, password_hash=hash_password(body.password), rol=RolUsuario.Admin)
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


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(Usuario).filter(Usuario.username == body.username).one_or_none()
    if not user or not user.activo or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(sub=str(user.id_usuario), username=user.username, rol=user.rol.value)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: Usuario = Depends(get_current_user)) -> Usuario:
    return user
