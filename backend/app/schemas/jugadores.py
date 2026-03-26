from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator


class JugadorBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    apellido: str = Field(min_length=2, max_length=80)
    fecha_nacimiento: date
    tipo_documento: str = Field(min_length=1, max_length=30)
    numero_documento: str = Field(min_length=6, max_length=15)
    domicilio: str | None = Field(default=None, max_length=255)
    nombre_tutor: str | None = Field(default=None, max_length=80)
    apellido_tutor: str | None = Field(default=None, max_length=80)
    celular_tutor: str | None = Field(default=None, max_length=30)
    mail_tutor: EmailStr | None = None
    id_categoria: int
    activo: bool = True

    @field_validator("fecha_nacimiento")
    @classmethod
    def fecha_no_futura(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("fecha_nacimiento cannot be in the future")
        return v


class JugadorCreate(JugadorBase):
    pass


class JugadorUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    apellido: str | None = Field(default=None, min_length=2, max_length=80)
    fecha_nacimiento: date | None = None
    tipo_documento: str | None = Field(default=None, min_length=1, max_length=30)
    numero_documento: str | None = Field(default=None, min_length=6, max_length=15)
    domicilio: str | None = Field(default=None, max_length=255)
    nombre_tutor: str | None = Field(default=None, max_length=80)
    apellido_tutor: str | None = Field(default=None, max_length=80)
    celular_tutor: str | None = Field(default=None, max_length=30)
    mail_tutor: EmailStr | None = None
    id_categoria: int | None = None
    activo: bool | None = None

    @field_validator("fecha_nacimiento")
    @classmethod
    def fecha_no_futura(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("fecha_nacimiento cannot be in the future")
        return v


class CategoriaMini(BaseModel):
    id_categoria: int
    descripcion: str
    model_config = {"from_attributes": True}


class JugadorOut(BaseModel):
    id_jugador: int
    nombre: str
    apellido: str
    fecha_nacimiento: date
    tipo_documento: str
    numero_documento: str
    domicilio: str | None
    nombre_tutor: str | None
    apellido_tutor: str | None
    celular_tutor: str | None
    mail_tutor: EmailStr | None
    id_categoria: int
    activo: bool
    categoria: CategoriaMini | None = None
    model_config = {"from_attributes": True}
