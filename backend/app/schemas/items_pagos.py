from datetime import date

from pydantic import BaseModel, Field


class ItemPagoCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=80)
    descripcion: str = Field(min_length=1, max_length=255)
    activo: bool = True


class ItemPagoUpdate(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=80)
    descripcion: str | None = Field(default=None, min_length=1, max_length=255)
    activo: bool | None = None


class ItemPagoOut(BaseModel):
    id_item_pago: int
    codigo: str
    descripcion: str
    activo: bool
    model_config = {"from_attributes": True}


class PrecioItemCreate(BaseModel):
    id_item_pago: int
    id_categoria: int | None = None
    monto: float = Field(gt=0)
    vigencia_desde: date
    vigencia_hasta: date | None = None
    activo: bool = True


class PrecioItemUpdate(BaseModel):
    monto: float | None = Field(default=None, gt=0)
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None
    activo: bool | None = None


class PrecioItemOut(BaseModel):
    id_precio_item: int
    id_item_pago: int
    id_categoria: int | None
    monto: float
    vigencia_desde: date
    vigencia_hasta: date | None
    activo: bool
    model_config = {"from_attributes": True}
