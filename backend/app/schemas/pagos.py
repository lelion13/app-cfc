from datetime import date

from pydantic import BaseModel, Field, HttpUrl


class PagoCreate(BaseModel):
    id_jugador: int
    fecha_pago: date | None = None
    monto: float = Field(gt=0)
    mes_correspondiente: int = Field(ge=1, le=12)
    anio_correspondiente: int = Field(ge=2000, le=2100)
    metodo_pago: str = Field(min_length=1, max_length=80)
    comprobante_url: HttpUrl | None = None


class PagoUpdate(BaseModel):
    fecha_pago: date | None = None
    monto: float | None = Field(default=None, gt=0)
    mes_correspondiente: int | None = Field(default=None, ge=1, le=12)
    anio_correspondiente: int | None = Field(default=None, ge=2000, le=2100)
    metodo_pago: str | None = Field(default=None, min_length=1, max_length=80)
    comprobante_url: HttpUrl | None = None


class JugadorMini(BaseModel):
    id_jugador: int
    nombre: str
    apellido: str
    model_config = {"from_attributes": True}


class PagoOut(BaseModel):
    id_pago: int
    id_jugador: int
    fecha_pago: date
    monto: float
    mes_correspondiente: int
    anio_correspondiente: int
    metodo_pago: str
    comprobante_url: str | None
    jugador: JugadorMini | None = None
    model_config = {"from_attributes": True}
