from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import ItemPago, PrecioItem, RolUsuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.items_pagos import ItemPagoCreate, ItemPagoOut, ItemPagoUpdate, PrecioItemCreate, PrecioItemOut, PrecioItemUpdate

router = APIRouter(prefix="/items-pago", tags=["items-pago"])


@router.get("", response_model=list[ItemPagoOut])
def list_items_pago(db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
    return db.query(ItemPago).order_by(ItemPago.descripcion.asc()).all()


@router.post("", response_model=ItemPagoOut, status_code=status.HTTP_201_CREATED)
def create_item_pago(body: ItemPagoCreate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    item = ItemPago(**body.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Codigo already exists")
    db.refresh(item)
    return item


@router.patch("/{id_item_pago}", response_model=ItemPagoOut)
def update_item_pago(
    id_item_pago: int,
    body: ItemPagoUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_role(RolUsuario.Admin)),
):
    item = db.get(ItemPago, id_item_pago)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Codigo already exists")
    db.refresh(item)
    return item


@router.get("/precios", response_model=list[PrecioItemOut])
def list_precios_item(
    item_id: int | None = Query(default=None),
    id_categoria: int | None = Query(default=None),
    fecha: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador)),
):
    q = db.query(PrecioItem)
    if item_id is not None:
        q = q.filter(PrecioItem.id_item_pago == item_id)
    if id_categoria is not None:
        q = q.filter(or_(PrecioItem.id_categoria == id_categoria, PrecioItem.id_categoria.is_(None)))
    if fecha is not None:
        q = q.filter(
            PrecioItem.vigencia_desde <= fecha,
            or_(PrecioItem.vigencia_hasta.is_(None), PrecioItem.vigencia_hasta >= fecha),
            PrecioItem.activo.is_(True),
        )
    return q.order_by(PrecioItem.vigencia_desde.desc()).all()


@router.post("/precios", response_model=PrecioItemOut, status_code=status.HTTP_201_CREATED)
def create_precio_item(body: PrecioItemCreate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin))):
    if body.vigencia_hasta is not None and body.vigencia_hasta < body.vigencia_desde:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid date range")
    if db.get(ItemPago, body.id_item_pago) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    overlap = (
        db.query(PrecioItem)
        .filter(
            PrecioItem.id_item_pago == body.id_item_pago,
            PrecioItem.id_categoria.is_(None) if body.id_categoria is None else PrecioItem.id_categoria == body.id_categoria,
            PrecioItem.activo.is_(True),
            and_(
                PrecioItem.vigencia_desde <= (body.vigencia_hasta or date.max),
                or_(PrecioItem.vigencia_hasta.is_(None), PrecioItem.vigencia_hasta >= body.vigencia_desde),
            ),
        )
        .first()
    )
    if overlap is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Overlapping active vigencia for item/categoria")

    precio = PrecioItem(**body.model_dump())
    db.add(precio)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Precio already exists for vigencia_desde")
    db.refresh(precio)
    return precio


@router.patch("/precios/{id_precio_item}", response_model=PrecioItemOut)
def update_precio_item(
    id_precio_item: int,
    body: PrecioItemUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_role(RolUsuario.Admin)),
):
    precio = db.get(PrecioItem, id_precio_item)
    if not precio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Precio not found")
    patch = body.model_dump(exclude_unset=True)
    if "vigencia_desde" in patch and patch.get("vigencia_hasta") is None and precio.vigencia_hasta is not None and patch["vigencia_desde"] > precio.vigencia_hasta:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid date range")
    if "vigencia_hasta" in patch and patch["vigencia_hasta"] is not None and patch["vigencia_hasta"] < (patch.get("vigencia_desde") or precio.vigencia_desde):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid date range")
    for k, v in patch.items():
        setattr(precio, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot update precio")
    db.refresh(precio)
    return precio
