from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import CajaUsuario, MovimientoCaja, Pago, TipoMovimientoCaja, Usuario


def ensure_caja_for_user(db: Session, user_id: int) -> CajaUsuario:
    caja = db.query(CajaUsuario).filter(CajaUsuario.id_usuario == user_id).one_or_none()
    if caja is not None:
        return caja
    caja = CajaUsuario(id_usuario=user_id, saldo_actual=Decimal("0"))
    db.add(caja)
    db.flush()
    return caja


def assert_pago_not_rendido(db: Session, pago_id: int) -> None:
    rendered_count = (
        db.query(func.count(MovimientoCaja.id_movimiento))
        .filter(MovimientoCaja.id_pago == pago_id, MovimientoCaja.id_rendicion.is_not(None))
        .scalar()
        or 0
    )
    if rendered_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pago already included in closed rendicion",
        )


def add_pago_movimiento(
    db: Session,
    *,
    pago: Pago,
    actor: Usuario,
    amount: Decimal,
    tipo: TipoMovimientoCaja,
    descripcion: str | None = None,
) -> None:
    if amount == 0:
        return
    caja = ensure_caja_for_user(db, pago.created_by_user_id)
    caja.saldo_actual = (caja.saldo_actual or Decimal("0")) + amount
    movimiento = MovimientoCaja(
        id_caja=caja.id_caja,
        id_pago=pago.id_pago,
        tipo=tipo,
        monto=amount,
        metodo_pago=pago.metodo_pago,
        descripcion=descripcion,
        created_by=actor.id_usuario,
    )
    db.add(movimiento)

