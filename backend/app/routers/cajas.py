from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.db.models import CajaUsuario, EstadoRendicionCaja, MovimientoCaja, RendicionCaja, RolUsuario, TipoMovimientoCaja, Usuario
from app.db.session import get_db
from app.deps.auth import get_current_user, require_role
from app.schemas.cajas import CajaResumenOut, CerrarRendicionIn, MovimientoCajaOut, RendicionCajaOut
from app.services.caja import ensure_caja_for_user

router = APIRouter(prefix="/cajas", tags=["cajas"])


def _build_caja_resumen(db: Session, caja: CajaUsuario) -> CajaResumenOut:
    total_pendiente = (
        db.query(func.coalesce(func.sum(MovimientoCaja.monto), 0))
        .filter(MovimientoCaja.id_caja == caja.id_caja, MovimientoCaja.id_rendicion.is_(None))
        .scalar()
        or Decimal("0")
    )
    cantidad_pendientes = (
        db.query(func.count(MovimientoCaja.id_movimiento))
        .filter(MovimientoCaja.id_caja == caja.id_caja, MovimientoCaja.id_rendicion.is_(None))
        .scalar()
        or 0
    )
    return CajaResumenOut(
        id_caja=caja.id_caja,
        id_usuario=caja.id_usuario,
        saldo_actual=float(caja.saldo_actual),
        created_at=caja.created_at,
        updated_at=caja.updated_at,
        usuario=caja.usuario,
        total_pendiente=float(total_pendiente),
        cantidad_pendientes=int(cantidad_pendientes),
    )


@router.get("/me", response_model=CajaResumenOut)
def get_my_caja(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    caja = ensure_caja_for_user(db, user.id_usuario)
    db.refresh(caja)
    return _build_caja_resumen(db, caja)


@router.get("", response_model=list[CajaResumenOut])
def list_cajas(db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    cajas = db.query(CajaUsuario).options(joinedload(CajaUsuario.usuario)).order_by(CajaUsuario.id_caja.asc()).all()
    return [_build_caja_resumen(db, caja) for caja in cajas]


@router.get("/{id_caja}/movimientos", response_model=list[MovimientoCajaOut])
def list_movimientos_caja(
    id_caja: int,
    only_pending: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    caja = db.query(CajaUsuario).filter(CajaUsuario.id_caja == id_caja).one_or_none()
    if not caja:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caja not found")
    if user.rol == RolUsuario.Operador and caja.id_usuario != user.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    q = db.query(MovimientoCaja).filter(MovimientoCaja.id_caja == id_caja)
    if only_pending:
        q = q.filter(MovimientoCaja.id_rendicion.is_(None))
    return q.order_by(MovimientoCaja.created_at.desc(), MovimientoCaja.id_movimiento.desc()).all()


@router.get("/{id_caja}/rendiciones", response_model=list[RendicionCajaOut])
def list_rendiciones_caja(
    id_caja: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    caja = db.query(CajaUsuario).filter(CajaUsuario.id_caja == id_caja).one_or_none()
    if not caja:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caja not found")
    if user.rol == RolUsuario.Operador and caja.id_usuario != user.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return (
        db.query(RendicionCaja)
        .filter(RendicionCaja.id_caja == id_caja)
        .order_by(RendicionCaja.cerrada_at.desc(), RendicionCaja.id_rendicion.desc())
        .all()
    )


@router.post("/{id_caja}/rendiciones/cerrar", response_model=RendicionCajaOut)
def cerrar_rendicion_caja(
    id_caja: int,
    body: CerrarRendicionIn,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador)),
):
    caja = db.query(CajaUsuario).filter(CajaUsuario.id_caja == id_caja).one_or_none()
    if not caja:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caja not found")

    ajuste_manual = Decimal(str(body.ajuste_manual))
    if ajuste_manual != 0 and not (body.motivo_ajuste and body.motivo_ajuste.strip()):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="motivo_ajuste is required when ajuste_manual is not zero")

    pendientes = (
        db.query(MovimientoCaja)
        .filter(MovimientoCaja.id_caja == caja.id_caja, MovimientoCaja.id_rendicion.is_(None))
        .order_by(MovimientoCaja.id_movimiento.asc())
        .all()
    )
    total_sistema = sum((m.monto for m in pendientes), Decimal("0"))
    monto_contado = Decimal(str(body.monto_contado)) if body.monto_contado is not None else None

    rendicion = RendicionCaja(
        id_caja=caja.id_caja,
        estado=EstadoRendicionCaja.Cerrada,
        total_sistema=total_sistema,
        monto_contado=monto_contado,
        ajuste_manual=ajuste_manual,
        motivo_ajuste=body.motivo_ajuste.strip() if body.motivo_ajuste else None,
        comprobante_url=str(body.comprobante_url) if body.comprobante_url else None,
        cerrada_por=user.id_usuario,
    )
    db.add(rendicion)
    db.flush()

    for mov in pendientes:
        mov.id_rendicion = rendicion.id_rendicion

    if ajuste_manual != 0:
        db.add(
            MovimientoCaja(
                id_caja=caja.id_caja,
                id_pago=None,
                id_rendicion=rendicion.id_rendicion,
                tipo=TipoMovimientoCaja.RendicionAjuste,
                monto=ajuste_manual,
                metodo_pago=None,
                descripcion=rendicion.motivo_ajuste,
                created_by=user.id_usuario,
            )
        )

    caja.saldo_actual = Decimal("0")
    db.commit()
    db.refresh(rendicion)
    return rendicion

