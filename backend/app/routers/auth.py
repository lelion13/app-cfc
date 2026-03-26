from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Usuario
from app.db.session import get_db
from app.deps.auth import get_current_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.usuarios import UserOut
from app.security.jwt import create_access_token
from app.security.passwords import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


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
