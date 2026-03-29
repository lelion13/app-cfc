from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.schemas.fechas_partido import FechaPartidoOut


class GoleadorLineIn(BaseModel):
    id_jugador: int
    goles: int = Field(ge=1, le=99)


class CategoriaPartidoOut(BaseModel):
    id_categoria: int
    descripcion: str

    model_config = {"from_attributes": True}


class FechaResumenOut(BaseModel):
    id_fecha_partido: int
    fecha_partido: date
    es_local: bool
    rival: str

    model_config = {"from_attributes": True}


class PartidoCreate(BaseModel):
    id_fecha_partido: int
    id_categoria: int
    hora_partido: time | None = None
    goles_nuestro: int = Field(default=0, ge=0, le=99)
    goles_rival: int = Field(default=0, ge=0, le=99)
    goleadores: list[GoleadorLineIn] = Field(default_factory=list)


class PartidoUpdate(BaseModel):
    hora_partido: time | None = None
    goles_nuestro: int | None = Field(default=None, ge=0, le=99)
    goles_rival: int | None = Field(default=None, ge=0, le=99)
    goleadores: list[GoleadorLineIn] | None = None


class GoleadorLineOut(BaseModel):
    id_jugador: int
    nombre: str
    apellido: str
    goles: int


class PartidoOut(BaseModel):
    id_partido: int
    id_fecha_partido: int
    id_categoria: int
    hora_partido: time | None
    goles_nuestro: int
    goles_rival: int
    categoria: CategoriaPartidoOut
    fecha: FechaResumenOut
    goleadores: list[GoleadorLineOut]
    created_at: datetime
    updated_at: datetime


class FechaPartidoDetailOut(FechaPartidoOut):
    partidos: list[PartidoOut]


class GoleadorTorneoOut(BaseModel):
    id_jugador: int
    nombre: str
    apellido: str
    goles_totales: int
