from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

RolUsuarioLiteral = Literal["Admin", "Coordinador"]


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=10, max_length=512)
    rol: RolUsuarioLiteral


class UserOut(BaseModel):
    id_usuario: int
    username: str
    rol: RolUsuarioLiteral
    activo: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    rol: RolUsuarioLiteral | None = None
    activo: bool | None = None
    password: str | None = Field(default=None, min_length=10, max_length=512)
