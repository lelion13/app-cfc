from sqlalchemy import text

from app.db.session import engine


def main() -> None:
    required = {"id_item_pago", "id_precio_item", "descripcion_item_snapshot", "monto_snapshot"}
    with engine.connect() as conn:
        names = {
            row[0]
            for row in conn.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'pagos'")
            )
        }
        missing = sorted(required - names)
        tables = conn.execute(
            text("SELECT to_regclass('public.items_pago'), to_regclass('public.precios_item')")
        ).fetchone()
    print("missing_columns:", missing)
    print("tables:", tables)


if __name__ == "__main__":
    main()
