from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.models import Jugador, Pago, RolUsuario
from app.db.session import get_db
from app.deps.auth import require_role
from app.schemas.pagos import PagoCreate, PagoOut, PagoUpdate

router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.get("", response_model=list[PagoOut])
def list_pagos(id_jugador: int | None = None, anio: int | None = Query(default=None, ge=2000, le=2100), mes: int | None = Query(default=None, ge=1, le=12), from_fecha: date | None = None, to_fecha: date | None = None, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
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
def create_pago(body: PagoCreate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    jugador = db.get(Jugador, body.id_jugador)
    if not jugador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jugador not found")
    data = body.model_dump()
    if data.get("fecha_pago") is None:
        data["fecha_pago"] = date.today()
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
def get_pago(id_pago: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    pago = db.query(Pago).options(joinedload(Pago.jugador)).filter(Pago.id_pago == id_pago).one_or_none()
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return pago


@router.patch("/{id_pago}", response_model=PagoOut)
def update_pago(id_pago: int, body: PagoUpdate, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador, RolUsuario.Operador))):
    pago = db.get(Pago, id_pago)
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    patch = body.model_dump(exclude_unset=True)
    for k, v in patch.items():
        setattr(pago, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pago already exists for period")
    return db.query(Pago).options(joinedload(Pago.jugador)).filter(Pago.id_pago == id_pago).one()


@router.delete("/{id_pago}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pago(id_pago: int, db: Session = Depends(get_db), _user=Depends(require_role(RolUsuario.Admin, RolUsuario.Coordinador))):
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
