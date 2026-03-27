from pathlib import Path

import psycopg

from app.core.config import settings


def main() -> None:
    dsn = settings.database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    sql = Path("db/migrations/005_items_precios_snapshot.sql").read_text(encoding="utf-8")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    print("migration_005_applied")


if __name__ == "__main__":
    main()
