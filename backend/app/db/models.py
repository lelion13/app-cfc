from __future__ import annotations

import enum
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Numeric, SmallInteger, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class RolUsuario(str, enum.Enum):
    Admin = "Admin"
    Coordinador = "Coordinador"
    Operador = "Operador"


class Categoria(Base):
    __tablename__ = "categorias"
    id_categoria: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    jugadores: Mapped[list["Jugador"]] = relationship(back_populates="categoria")
    partidos: Mapped[list["Partido"]] = relationship(back_populates="categoria")


class Jugador(Base):
    __tablename__ = "jugadores"
    __table_args__ = (
        UniqueConstraint("tipo_documento", "numero_documento", name="uq_jugadores_documento"),
        CheckConstraint("tipo_documento IN ('DNI', 'LC', 'LE', 'PASAPORTE')", name="ck_jugadores_tipo_documento"),
    )
    id_jugador: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    apellido: Mapped[str] = mapped_column(Text, nullable=False, index=True)
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
    goles_partido: Mapped[list["GolPartido"]] = relationship(back_populates="jugador")


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
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    mes_correspondiente: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    anio_correspondiente: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    metodo_pago: Mapped[str] = mapped_column(Text, nullable=False)
    comprobante_url: Mapped[str | None] = mapped_column(Text)
    jugador: Mapped[Jugador] = relationship(back_populates="pagos")


class FechaPartido(Base):
    __tablename__ = "fechas_partido"
    __table_args__ = (UniqueConstraint("fecha_partido", name="uq_fechas_partido_fecha"),)
    id_fecha_partido: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fecha_partido: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    es_local: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rival: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    partidos: Mapped[list["Partido"]] = relationship(back_populates="fecha_encuentro")


class Partido(Base):
    __tablename__ = "partidos"
    __table_args__ = (
        UniqueConstraint("id_fecha_partido", "id_categoria", name="uq_partidos_fecha_categoria"),
        CheckConstraint("goles_nuestro >= 0 AND goles_nuestro <= 99", name="ck_partidos_goles_nuestro"),
        CheckConstraint("goles_rival >= 0 AND goles_rival <= 99", name="ck_partidos_goles_rival"),
    )
    id_partido: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_fecha_partido: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("fechas_partido.id_fecha_partido", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, index=True
    )
    id_categoria: Mapped[int] = mapped_column(BigInteger, ForeignKey("categorias.id_categoria", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, index=True)
    hora_partido: Mapped[time | None] = mapped_column(Time, nullable=True)
    goles_nuestro: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")
    goles_rival: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    fecha_encuentro: Mapped["FechaPartido"] = relationship(back_populates="partidos")
    categoria: Mapped["Categoria"] = relationship(back_populates="partidos")
    goles: Mapped[list["GolPartido"]] = relationship(back_populates="partido", cascade="all, delete-orphan")


class GolPartido(Base):
    __tablename__ = "goles_partido"
    __table_args__ = (
        UniqueConstraint("id_partido", "id_jugador", name="uq_goles_partido_jugador"),
        CheckConstraint("goles >= 1", name="ck_goles_partido_goles"),
    )
    id_gol: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_partido: Mapped[int] = mapped_column(BigInteger, ForeignKey("partidos.id_partido", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, index=True)
    id_jugador: Mapped[int] = mapped_column(BigInteger, ForeignKey("jugadores.id_jugador", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, index=True)
    goles: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    partido: Mapped[Partido] = relationship(back_populates="goles")
    jugador: Mapped[Jugador] = relationship(back_populates="goles_partido")


class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario, name="rol_usuario"), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
