from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class UsuarioCajaOut(BaseModel):
    id_usuario: int
    username: str
    rol: str
    model_config = {"from_attributes": True}


class CajaResumenOut(BaseModel):
    id_caja: int
    id_usuario: int
    saldo_actual: float
    created_at: datetime
    updated_at: datetime
    usuario: UsuarioCajaOut | None = None
    total_pendiente: float
    cantidad_pendientes: int


class MovimientoCajaOut(BaseModel):
    id_movimiento: int
    id_caja: int
    id_pago: int | None
    id_rendicion: int | None
    tipo: str
    monto: float
    metodo_pago: str | None
    descripcion: str | None
    created_by: int
    created_at: datetime
    model_config = {"from_attributes": True}


class RendicionCajaOut(BaseModel):
    id_rendicion: int
    id_caja: int
    estado: str
    total_sistema: float
    monto_contado: float | None
    ajuste_manual: float
    motivo_ajuste: str | None
    comprobante_url: str | None
    cerrada_por: int
    cerrada_at: datetime
    model_config = {"from_attributes": True}


class CerrarRendicionIn(BaseModel):
    monto_contado: float | None = Field(default=None, gt=0)
    ajuste_manual: float = 0
    motivo_ajuste: str | None = Field(default=None, max_length=500)
    comprobante_url: HttpUrl | None = None

