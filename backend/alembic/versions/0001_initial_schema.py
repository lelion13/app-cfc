"""Esquema inicial (modelos actuales).

Revision ID: 0001
Revises:
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rol_usuario') THEN
            CREATE TYPE rol_usuario AS ENUM ('Admin', 'Coordinador', 'Operador');
          END IF;
        END $$;
        """
    )

    rol_usuario = postgresql.ENUM("Admin", "Coordinador", "Operador", name="rol_usuario", create_type=False)

    op.create_table(
        "categorias",
        sa.Column("id_categoria", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id_categoria"),
        sa.UniqueConstraint("descripcion"),
    )

    op.create_table(
        "jugadores",
        sa.Column("id_jugador", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column("apellido", sa.Text(), nullable=False),
        sa.Column("fecha_nacimiento", sa.Date(), nullable=False),
        sa.Column("tipo_documento", sa.Text(), nullable=False),
        sa.Column("numero_documento", sa.Text(), nullable=False),
        sa.Column("domicilio", sa.Text(), nullable=True),
        sa.Column("nombre_tutor", sa.Text(), nullable=True),
        sa.Column("apellido_tutor", sa.Text(), nullable=True),
        sa.Column("celular_tutor", sa.Text(), nullable=True),
        sa.Column("mail_tutor", sa.Text(), nullable=True),
        sa.Column("id_categoria", sa.BigInteger(), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint(
            "tipo_documento IN ('DNI', 'LC', 'LE', 'PASAPORTE')",
            name="ck_jugadores_tipo_documento",
        ),
        sa.ForeignKeyConstraint(["id_categoria"], ["categorias.id_categoria"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id_jugador"),
        sa.UniqueConstraint("tipo_documento", "numero_documento", name="uq_jugadores_documento"),
    )
    op.create_index("ix_jugadores_id_categoria", "jugadores", ["id_categoria"], unique=False)
    op.create_index("ix_jugadores_activo", "jugadores", ["activo"], unique=False)
    op.create_index("ix_jugadores_apellido", "jugadores", ["apellido"], unique=False)

    op.create_table(
        "usuarios",
        sa.Column("id_usuario", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("rol", rol_usuario, nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id_usuario"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_usuarios_rol", "usuarios", ["rol"], unique=False)
    op.create_index("ix_usuarios_activo", "usuarios", ["activo"], unique=False)

    op.create_table(
        "fechas_partido",
        sa.Column("id_fecha_partido", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("fecha_partido", sa.Date(), nullable=False),
        sa.Column("es_local", sa.Boolean(), nullable=False),
        sa.Column("rival", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id_fecha_partido"),
        sa.UniqueConstraint("fecha_partido", name="uq_fechas_partido_fecha"),
    )
    op.create_index("ix_fechas_partido_fecha_partido", "fechas_partido", ["fecha_partido"], unique=False)

    op.create_table(
        "partidos",
        sa.Column("id_partido", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_fecha_partido", sa.BigInteger(), nullable=False),
        sa.Column("id_categoria", sa.BigInteger(), nullable=False),
        sa.Column("hora_partido", sa.Time(), nullable=True),
        sa.Column("goles_nuestro", sa.SmallInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("goles_rival", sa.SmallInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("goles_nuestro >= 0 AND goles_nuestro <= 99", name="ck_partidos_goles_nuestro"),
        sa.CheckConstraint("goles_rival >= 0 AND goles_rival <= 99", name="ck_partidos_goles_rival"),
        sa.ForeignKeyConstraint(["id_categoria"], ["categorias.id_categoria"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_fecha_partido"], ["fechas_partido.id_fecha_partido"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_partido"),
        sa.UniqueConstraint("id_fecha_partido", "id_categoria", name="uq_partidos_fecha_categoria"),
    )
    op.create_index("ix_partidos_id_fecha_partido", "partidos", ["id_fecha_partido"], unique=False)
    op.create_index("ix_partidos_id_categoria", "partidos", ["id_categoria"], unique=False)

    op.create_table(
        "goles_partido",
        sa.Column("id_gol", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_partido", sa.BigInteger(), nullable=False),
        sa.Column("id_jugador", sa.BigInteger(), nullable=False),
        sa.Column("goles", sa.SmallInteger(), nullable=False),
        sa.CheckConstraint("goles >= 1", name="ck_goles_partido_goles"),
        sa.ForeignKeyConstraint(["id_jugador"], ["jugadores.id_jugador"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_partido"], ["partidos.id_partido"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_gol"),
        sa.UniqueConstraint("id_partido", "id_jugador", name="uq_goles_partido_jugador"),
    )
    op.create_index("ix_goles_partido_id_partido", "goles_partido", ["id_partido"], unique=False)
    op.create_index("ix_goles_partido_id_jugador", "goles_partido", ["id_jugador"], unique=False)

    op.create_table(
        "pagos",
        sa.Column("id_pago", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_jugador", sa.BigInteger(), nullable=False),
        sa.Column("fecha_pago", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("mes_correspondiente", sa.SmallInteger(), nullable=False),
        sa.Column("anio_correspondiente", sa.SmallInteger(), nullable=False),
        sa.Column("metodo_pago", sa.Text(), nullable=False),
        sa.Column("comprobante_url", sa.Text(), nullable=True),
        sa.CheckConstraint("monto > 0", name="ck_pagos_monto"),
        sa.CheckConstraint("mes_correspondiente BETWEEN 1 AND 12", name="ck_pagos_mes"),
        sa.CheckConstraint("anio_correspondiente BETWEEN 2000 AND 2100", name="ck_pagos_anio"),
        sa.ForeignKeyConstraint(["id_jugador"], ["jugadores.id_jugador"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id_pago"),
        sa.UniqueConstraint("id_jugador", "mes_correspondiente", "anio_correspondiente", name="uq_pagos_periodo"),
    )
    op.create_index("ix_pagos_id_jugador", "pagos", ["id_jugador"], unique=False)
    op.create_index("ix_pagos_periodo", "pagos", ["anio_correspondiente", "mes_correspondiente"], unique=False)
    op.create_index("ix_pagos_fecha", "pagos", ["fecha_pago"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_pagos_fecha", table_name="pagos")
    op.drop_index("ix_pagos_periodo", table_name="pagos")
    op.drop_index("ix_pagos_id_jugador", table_name="pagos")
    op.drop_table("pagos")

    op.drop_index("ix_goles_partido_id_jugador", table_name="goles_partido")
    op.drop_index("ix_goles_partido_id_partido", table_name="goles_partido")
    op.drop_table("goles_partido")

    op.drop_index("ix_partidos_id_categoria", table_name="partidos")
    op.drop_index("ix_partidos_id_fecha_partido", table_name="partidos")
    op.drop_table("partidos")

    op.drop_index("ix_fechas_partido_fecha_partido", table_name="fechas_partido")
    op.drop_table("fechas_partido")

    op.drop_index("ix_usuarios_activo", table_name="usuarios")
    op.drop_index("ix_usuarios_rol", table_name="usuarios")
    op.drop_table("usuarios")

    op.drop_index("ix_jugadores_apellido", table_name="jugadores")
    op.drop_index("ix_jugadores_activo", table_name="jugadores")
    op.drop_index("ix_jugadores_id_categoria", table_name="jugadores")
    op.drop_table("jugadores")

    op.drop_table("categorias")

    op.execute("DROP TYPE IF EXISTS rol_usuario")
