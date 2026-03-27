from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.models import ItemPago, Jugador, Pago, PrecioItem, RolUsuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.pagos import PagoCreate, PagoOut, PagoUpdate

router = APIRouter(prefix="/pagos", tags=["pagos"])

LEGACY_ITEM_DESC = "Legacy"


def _resolve_precio_vigente(db: Session, *, id_item_pago: int, id_categoria: int | None, fecha_pago: date) -> PrecioItem | None:
    return (
        db.query(PrecioItem)
        .filter(
            PrecioItem.id_item_pago == id_item_pago,
            PrecioItem.activo.is_(True),
            PrecioItem.vigencia_desde <= fecha_pago,
            or_(PrecioItem.vigencia_hasta.is_(None), PrecioItem.vigencia_hasta >= fecha_pago),
            or_(PrecioItem.id_categoria == id_categoria, PrecioItem.id_categoria.is_(None)),
        )
        .order_by(
            case((PrecioItem.id_categoria == id_categoria, 0), else_=1),
            PrecioItem.vigencia_desde.desc(),
        )
        .first()
    )


@router.get("", response_model=list[PagoOut])
def list_pagos(id_jugador: int | None = None, anio: int | None = Query(default=None, ge=2000, le=2100), mes: int | None = Query(default=None, ge=1, le=12), from_fecha: date | None = None, to_fecha: date | None = None, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    qry = db.query(Pago).options(joinedload(Pago.jugador))
    if id_jugador is not None:
        qry = qry.filter(Pago.id_jugador == id_jugador)
    if anio is not None:
        qry = qry.filter(Pago.anio_correspondiente == anio)
    if mes is not None:
        qry = qry.filter(Pago.mes_correspondiente == mes)
    if from_fecha is not None:
        qry = qry.filter(Pago.fecha_pago >= from_fecha)
    if to_fecha is not None:
        qry = qry.filter(Pago.fecha_pago <= to_fecha)
    return qry.order_by(Pago.fecha_pago.desc()).all()


@router.post("", response_model=PagoOut, status_code=status.HTTP_201_CREATED)
def create_pago(body: PagoCreate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    jugador = db.get(Jugador, body.id_jugador)
    if not jugador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jugador not found")
    data = body.model_dump()
    if data.get("fecha_pago") is None:
        data["fecha_pago"] = date.today()
    fecha_pago = data["fecha_pago"]

    item: ItemPago | None = None
    precio: PrecioItem | None = None
    if body.id_item_pago is not None:
        item = db.get(ItemPago, body.id_item_pago)
        if item is None or not item.activo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de pago not found")
        precio = _resolve_precio_vigente(
            db,
            id_item_pago=body.id_item_pago,
            id_categoria=jugador.id_categoria,
            fecha_pago=fecha_pago,
        )

    final_monto: Decimal
    if body.monto is not None:
        final_monto = Decimal(str(body.monto))
    else:
        if body.id_item_pago is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="id_item_pago is required when monto is omitted")
        if precio is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No active precio for selected item/date")
        final_monto = precio.monto

    data["monto"] = final_monto
    data["descripcion_item_snapshot"] = item.descripcion if item else LEGACY_ITEM_DESC
    data["monto_snapshot"] = final_monto
    data["id_precio_item"] = precio.id_precio_item if precio else None
    pago = Pago(**data)
    db.add(pago)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pago already exists for period")
    db.refresh(pago)
    return db.query(Pago).options(joinedload(Pago.jugador)).filter(Pago.id_pago == pago.id_pago).one()


@router.get("/{id_pago}", response_model=PagoOut)
def get_pago(id_pago: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    pago = db.query(Pago).options(joinedload(Pago.jugador)).filter(Pago.id_pago == id_pago).one_or_none()
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return pago


@router.patch("/{id_pago}", response_model=PagoOut)
def update_pago(id_pago: int, body: PagoUpdate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    pago = db.get(Pago, id_pago)
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    patch = body.model_dump(exclude_unset=True)
    for k, v in patch.items():
        setattr(pago, k, v)

    if "monto" in patch and patch["monto"] is not None:
        pago.monto_snapshot = Decimal(str(patch["monto"]))
        if pago.descripcion_item_snapshot is None:
            pago.descripcion_item_snapshot = LEGACY_ITEM_DESC

    if "id_item_pago" in patch and patch["id_item_pago"] is not None:
        item = db.get(ItemPago, patch["id_item_pago"])
        if item is None or not item.activo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de pago not found")
        pago.descripcion_item_snapshot = item.descripcion
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pago already exists for period")
    return db.query(Pago).options(joinedload(Pago.jugador)).filter(Pago.id_pago == id_pago).one()


@router.delete("/{id_pago}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pago(id_pago: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    pago = db.get(Pago, id_pago)
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(pago)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete pago")
    return None
