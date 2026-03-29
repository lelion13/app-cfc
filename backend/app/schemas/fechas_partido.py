from datetime import date, datetime

from pydantic import BaseModel, Field


class FechaPartidoCreate(BaseModel):
    fecha_partido: date
    es_local: bool
    rival: str = Field(min_length=1, max_length=500)


class FechaPartidoUpdate(BaseModel):
    fecha_partido: date | None = None
    es_local: bool | None = None
    rival: str | None = Field(default=None, min_length=1, max_length=500)


class FechaPartidoOut(BaseModel):
    id_fecha_partido: int
    fecha_partido: date
    es_local: bool
    rival: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
