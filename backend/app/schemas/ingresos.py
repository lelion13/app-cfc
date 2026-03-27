from pydantic import BaseModel


class IngresoResumenOut(BaseModel):
    total_ingresos: float
    cantidad_pagos: int
