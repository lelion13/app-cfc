from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Numeric, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class RolUsuario(str, enum.Enum):
    Admin = "Admin"
    Coordinador = "Coordinador"


class Categoria(Base):
    __tablename__ = "categorias"
    id_categoria: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    jugadores: Mapped[list["Jugador"]] = relationship(back_populates="categoria")
    precios_item: Mapped[list["PrecioItem"]] = relationship(back_populates="categoria")


class Jugador(Base):
    __tablename__ = "jugadores"
    __table_args__ = (UniqueConstraint("tipo_documento", "numero_documento", name="uq_jugadores_documento"),)
    id_jugador: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    apellido: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    tipo_documento: Mapped[str] = mapped_column(Text, nullable=False)
    numero_documento: Mapped[str] = mapped_column(Text, nullable=False)
    domicilio: Mapped[str | None] = mapped_column(Text)
    nombre_tutor: Mapped[str | None] = mapped_column(Text)
    apellido_tutor: Mapped[str | None] = mapped_column(Text)
    celular_tutor: Mapped[str | None] = mapped_column(Text)
    mail_tutor: Mapped[str | None] = mapped_column(Text)
    id_categoria: Mapped[int] = mapped_column(BigInteger, ForeignKey("categorias.id_categoria", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true", index=True)
    categoria: Mapped[Categoria] = relationship(back_populates="jugadores")
    pagos: Mapped[list["Pago"]] = relationship(back_populates="jugador")


class Pago(Base):
    __tablename__ = "pagos"
    __table_args__ = (
        UniqueConstraint("id_jugador", "mes_correspondiente", "anio_correspondiente", name="uq_pagos_periodo"),
        CheckConstraint("monto > 0", name="ck_pagos_monto"),
        CheckConstraint("mes_correspondiente BETWEEN 1 AND 12", name="ck_pagos_mes"),
        CheckConstraint("anio_correspondiente BETWEEN 2000 AND 2100", name="ck_pagos_anio"),
    )
    id_pago: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_jugador: Mapped[int] = mapped_column(BigInteger, ForeignKey("jugadores.id_jugador", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, index=True)
    id_item_pago: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("items_pago.id_item_pago", onupdate="CASCADE", ondelete="SET NULL"), nullable=True, index=True)
    id_precio_item: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("precios_item.id_precio_item", onupdate="CASCADE", ondelete="SET NULL"), nullable=True, index=True)
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    descripcion_item_snapshot: Mapped[str | None] = mapped_column(Text)
    monto_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    mes_correspondiente: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    anio_correspondiente: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    metodo_pago: Mapped[str] = mapped_column(Text, nullable=False)
    comprobante_url: Mapped[str | None] = mapped_column(Text)
    jugador: Mapped[Jugador] = relationship(back_populates="pagos")
    item_pago: Mapped["ItemPago | None"] = relationship(back_populates="pagos")
    precio_item: Mapped["PrecioItem | None"] = relationship(back_populates="pagos")


class ItemPago(Base):
    __tablename__ = "items_pago"
    id_item_pago: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true", index=True)
    precios: Mapped[list["PrecioItem"]] = relationship(back_populates="item_pago")
    pagos: Mapped[list[Pago]] = relationship(back_populates="item_pago")


class PrecioItem(Base):
    __tablename__ = "precios_item"
    __table_args__ = (
        UniqueConstraint("id_item_pago", "id_categoria", "vigencia_desde", name="uq_precios_item_inicio"),
        CheckConstraint("monto > 0", name="ck_precios_item_monto"),
        CheckConstraint("vigencia_hasta IS NULL OR vigencia_hasta >= vigencia_desde", name="ck_precios_item_rango"),
    )
    id_precio_item: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_item_pago: Mapped[int] = mapped_column(BigInteger, ForeignKey("items_pago.id_item_pago", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, index=True)
    id_categoria: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("categorias.id_categoria", onupdate="CASCADE", ondelete="SET NULL"), nullable=True, index=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    vigencia_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true", index=True)
    item_pago: Mapped[ItemPago] = relationship(back_populates="precios")
    categoria: Mapped[Categoria | None] = relationship(back_populates="precios_item")
    pagos: Mapped[list[Pago]] = relationship(back_populates="precio_item")


class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario, name="rol_usuario"), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
