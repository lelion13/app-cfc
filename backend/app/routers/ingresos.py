from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Jugador, Pago, RolUsuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.ingresos import IngresoResumenOut

router = APIRouter(prefix="/ingresos", tags=["ingresos"])


@router.get("/resumen", response_model=IngresoResumenOut)
def resumen_ingresos(
    anio: int | None = Query(default=None, ge=2000, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    id_categoria: int | None = None,
    id_item_pago: int | None = None,
    db: Session = Depends(get_db),
    _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador)),
):
    q = db.query(func.coalesce(func.sum(Pago.monto), 0), func.count(Pago.id_pago)).join(Jugador, Jugador.id_jugador == Pago.id_jugador)
    if anio is not None:
        q = q.filter(Pago.anio_correspondiente == anio)
    if mes is not None:
        q = q.filter(Pago.mes_correspondiente == mes)
    if id_categoria is not None:
        q = q.filter(Jugador.id_categoria == id_categoria)
    if id_item_pago is not None:
        q = q.filter(Pago.id_item_pago == id_item_pago)

    total, cantidad = q.one()
    return IngresoResumenOut(total_ingresos=float(total), cantidad_pagos=int(cantidad))
