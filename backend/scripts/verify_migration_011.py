"""Verifica que la migración 011 dejó pagos sin columnas de ítem/precio y sin tablas de aranceles."""

from sqlalchemy import text

from app.db.session import engine


def main() -> None:
    forbidden = {"id_item_pago", "id_precio_item", "descripcion_item_snapshot", "monto_snapshot"}
    with engine.connect() as conn:
        names = {
            row[0]
            for row in conn.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'pagos'")
            )
        }
        leaked = sorted(forbidden & names)
        items_tbl = conn.execute(text("SELECT to_regclass('public.items_pago')")).scalar()
        precios_tbl = conn.execute(text("SELECT to_regclass('public.precios_item')")).scalar()
    print("forbidden_columns_still_on_pagos:", leaked)
    print("items_pago_table:", items_tbl)
    print("precios_item_table:", precios_tbl)


if __name__ == "__main__":
    main()
