"""Cajas por usuario y rendiciones.

Revision ID: 0002
Revises: 0001
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_movimiento_caja') THEN
            CREATE TYPE tipo_movimiento_caja AS ENUM (
              'PAGO_ALTA',
              'PAGO_EDICION_AJUSTE',
              'PAGO_ELIMINACION',
              'RENDICION_AJUSTE'
            );
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_rendicion_caja') THEN
            CREATE TYPE estado_rendicion_caja AS ENUM ('CERRADA');
          END IF;
        END $$;
        """
    )

    op.add_column("pagos", sa.Column("created_by_user_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "pagos_created_by_user_id_fkey",
        "pagos",
        "usuarios",
        ["created_by_user_id"],
        ["id_usuario"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )
    op.create_index("ix_pagos_created_by_user_id", "pagos", ["created_by_user_id"], unique=False)

    op.create_table(
        "cajas_usuario",
        sa.Column("id_caja", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_usuario", sa.BigInteger(), nullable=False),
        sa.Column("saldo_actual", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuarios.id_usuario"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id_caja"),
        sa.UniqueConstraint("id_usuario"),
    )
    op.create_index("ix_cajas_usuario_id_usuario", "cajas_usuario", ["id_usuario"], unique=True)

    estado_rendicion = postgresql.ENUM("CERRADA", name="estado_rendicion_caja", create_type=False)
    op.create_table(
        "rendiciones_caja",
        sa.Column("id_rendicion", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_caja", sa.BigInteger(), nullable=False),
        sa.Column("estado", estado_rendicion, server_default=sa.text("'CERRADA'"), nullable=False),
        sa.Column("total_sistema", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("monto_contado", sa.Numeric(12, 2), nullable=True),
        sa.Column("ajuste_manual", sa.Numeric(12, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("motivo_ajuste", sa.Text(), nullable=True),
        sa.Column("comprobante_url", sa.Text(), nullable=True),
        sa.Column("cerrada_por", sa.BigInteger(), nullable=False),
        sa.Column("cerrada_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["cerrada_por"], ["usuarios.id_usuario"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_caja"], ["cajas_usuario.id_caja"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id_rendicion"),
    )
    op.create_index("ix_rendiciones_caja_id_caja", "rendiciones_caja", ["id_caja"], unique=False)
    op.create_index("ix_rendiciones_caja_estado", "rendiciones_caja", ["estado"], unique=False)
    op.create_index("ix_rendiciones_caja_cerrada_por", "rendiciones_caja", ["cerrada_por"], unique=False)
    op.create_index("ix_rendiciones_caja_cerrada_at", "rendiciones_caja", ["cerrada_at"], unique=False)

    tipo_mov = postgresql.ENUM(
        "PAGO_ALTA",
        "PAGO_EDICION_AJUSTE",
        "PAGO_ELIMINACION",
        "RENDICION_AJUSTE",
        name="tipo_movimiento_caja",
        create_type=False,
    )
    op.create_table(
        "movimientos_caja",
        sa.Column("id_movimiento", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_caja", sa.BigInteger(), nullable=False),
        sa.Column("id_pago", sa.BigInteger(), nullable=True),
        sa.Column("id_rendicion", sa.BigInteger(), nullable=True),
        sa.Column("tipo", tipo_mov, nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("metodo_pago", sa.Text(), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("monto != 0", name="ck_movimientos_caja_monto_no_cero"),
        sa.ForeignKeyConstraint(["created_by"], ["usuarios.id_usuario"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_caja"], ["cajas_usuario.id_caja"], onupdate="CASCADE", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_pago"], ["pagos.id_pago"], onupdate="CASCADE", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_rendicion"], ["rendiciones_caja.id_rendicion"], onupdate="CASCADE", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id_movimiento"),
    )
    op.create_index("ix_movimientos_caja_id_caja", "movimientos_caja", ["id_caja"], unique=False)
    op.create_index("ix_movimientos_caja_id_pago", "movimientos_caja", ["id_pago"], unique=False)
    op.create_index("ix_movimientos_caja_id_rendicion", "movimientos_caja", ["id_rendicion"], unique=False)
    op.create_index("ix_movimientos_caja_tipo", "movimientos_caja", ["tipo"], unique=False)
    op.create_index("ix_movimientos_caja_created_by", "movimientos_caja", ["created_by"], unique=False)
    op.create_index("ix_movimientos_caja_created_at", "movimientos_caja", ["created_at"], unique=False)

    op.execute(
        """
        INSERT INTO cajas_usuario (id_usuario, saldo_actual)
        SELECT u.id_usuario, 0
        FROM usuarios u
        LEFT JOIN cajas_usuario c ON c.id_usuario = u.id_usuario
        WHERE c.id_usuario IS NULL;
        """
    )

    op.execute(
        """
        WITH admin_fallback AS (
          SELECT id_usuario
          FROM usuarios
          ORDER BY
            CASE WHEN rol = 'Admin' THEN 0 ELSE 1 END,
            id_usuario
          LIMIT 1
        )
        UPDATE pagos p
        SET created_by_user_id = admin_fallback.id_usuario
        FROM admin_fallback
        WHERE p.created_by_user_id IS NULL;
        """
    )

    op.alter_column("pagos", "created_by_user_id", nullable=False)

    op.execute(
        """
        INSERT INTO movimientos_caja (id_caja, id_pago, tipo, monto, metodo_pago, descripcion, created_by)
        SELECT
          c.id_caja,
          p.id_pago,
          'PAGO_ALTA'::tipo_movimiento_caja,
          p.monto,
          p.metodo_pago,
          'Backfill inicial desde pagos existentes',
          p.created_by_user_id
        FROM pagos p
        JOIN cajas_usuario c ON c.id_usuario = p.created_by_user_id
        WHERE NOT EXISTS (
          SELECT 1 FROM movimientos_caja m WHERE m.id_pago = p.id_pago AND m.tipo = 'PAGO_ALTA'
        );
        """
    )

    op.execute(
        """
        UPDATE cajas_usuario c
        SET saldo_actual = COALESCE(m.total, 0)
        FROM (
          SELECT id_caja, SUM(monto) AS total
          FROM movimientos_caja
          WHERE id_rendicion IS NULL
          GROUP BY id_caja
        ) m
        WHERE c.id_caja = m.id_caja;
        """
    )


def downgrade() -> None:
    op.drop_index("ix_movimientos_caja_created_at", table_name="movimientos_caja")
    op.drop_index("ix_movimientos_caja_created_by", table_name="movimientos_caja")
    op.drop_index("ix_movimientos_caja_tipo", table_name="movimientos_caja")
    op.drop_index("ix_movimientos_caja_id_rendicion", table_name="movimientos_caja")
    op.drop_index("ix_movimientos_caja_id_pago", table_name="movimientos_caja")
    op.drop_index("ix_movimientos_caja_id_caja", table_name="movimientos_caja")
    op.drop_table("movimientos_caja")

    op.drop_index("ix_rendiciones_caja_cerrada_at", table_name="rendiciones_caja")
    op.drop_index("ix_rendiciones_caja_cerrada_por", table_name="rendiciones_caja")
    op.drop_index("ix_rendiciones_caja_estado", table_name="rendiciones_caja")
    op.drop_index("ix_rendiciones_caja_id_caja", table_name="rendiciones_caja")
    op.drop_table("rendiciones_caja")

    op.drop_index("ix_cajas_usuario_id_usuario", table_name="cajas_usuario")
    op.drop_table("cajas_usuario")

    op.drop_index("ix_pagos_created_by_user_id", table_name="pagos")
    op.drop_constraint("pagos_created_by_user_id_fkey", "pagos", type_="foreignkey")
    op.drop_column("pagos", "created_by_user_id")

    op.execute("DROP TYPE IF EXISTS tipo_movimiento_caja")
    op.execute("DROP TYPE IF EXISTS estado_rendicion_caja")

