"""
Inspecciona tablas clave vs esquema esperado (v8.01 partidos + fechas).
Uso:
  python scripts/inspect_db_schema.py
  python scripts/inspect_db_schema.py "postgresql+psycopg://user:pass@host/db?sslmode=require"
(cwd = backend)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text

EXPECTED_PARTIDOS = {
    "id_partido",
    "id_fecha_partido",
    "id_categoria",
    "hora_partido",
    "goles_nuestro",
    "goles_rival",
    "created_at",
    "updated_at",
}

EXPECTED_FECHAS = {
    "id_fecha_partido",
    "fecha_partido",
    "es_local",
    "rival",
    "created_at",
    "updated_at",
}

EXPECTED_GOLES = {"id_gol", "id_partido", "id_jugador", "goles"}


def table_exists(conn, name: str) -> bool:
    r = conn.execute(
        text("SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = :n"),
        {"n": name},
    ).scalar()
    return r is not None


def columns(conn, table: str) -> set[str]:
    q = text(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = :t
        ORDER BY ordinal_position
        """
    )
    return {r[0] for r in conn.execute(q, {"t": table}).fetchall()}


def main() -> None:
    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        from app.core.config import settings

        url = settings.database_url

    engine = create_engine(url)
    with engine.connect() as conn:
        print("=== Conexión OK ===\n")

        for tbl, expected, label in (
            ("fechas_partido", EXPECTED_FECHAS, "Fechas de encuentro (v8.01)"),
            ("partidos", EXPECTED_PARTIDOS, "Partidos por categoría (v8.01)"),
            ("goles_partido", EXPECTED_GOLES, "Goles por jugador"),
        ):
            if not table_exists(conn, tbl):
                print(f"[FALTA] Tabla `{tbl}` no existe — {label}")
                continue
            c = columns(conn, tbl)
            missing = expected - c
            extra = c - expected
            if not missing and not extra:
                print(f"[OK] {tbl}: columnas alineadas con {label}")
            else:
                print(f"[DESALINEADO] {tbl}")
                if missing:
                    print(f"   Faltan: {sorted(missing)}")
                if extra:
                    print(f"   Sobran (o extra): {sorted(extra)}")

        # Señales de esquema viejo en partidos
        if table_exists(conn, "partidos"):
            c = columns(conn, "partidos")
            legacy = {"fecha_partido", "es_local", "rival"} & c
            if legacy:
                print(f"\n[LEGACY] partidos aún tiene columnas del modelo anterior: {sorted(legacy)}")

        # Enum rol_usuario
        try:
            rows = conn.execute(
                text("SELECT enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname = 'rol_usuario' ORDER BY enumsortorder")
            ).fetchall()
            labels = [r[0] for r in rows]
            if labels:
                print(f"\n[ENUM] rol_usuario: {labels}")
                if "Operador" not in labels:
                    print("   [AVISO] Falta valor 'Operador' (migración 006) si usás ese rol en la app.")
        except Exception as e:
            print(f"\n[ENUM] No se pudo leer rol_usuario: {e}")

        print("\n=== Resumen ===")
        fechas_ok = table_exists(conn, "fechas_partido") and columns(conn, "fechas_partido") == EXPECTED_FECHAS
        partidos_ok = table_exists(conn, "partidos") and columns(conn, "partidos") == EXPECTED_PARTIDOS
        goles_ok = table_exists(conn, "goles_partido") and EXPECTED_GOLES <= columns(conn, "goles_partido")
        if fechas_ok and partidos_ok and goles_ok:
            print("Esquema de partidos v8.01: COMPLETO respecto a columnas esperadas.")
        else:
            print("Esquema: INCOMPLETO o mezcla con versiones anteriores. Revisá migraciones 007–010 y schema.sql.")


if __name__ == "__main__":
    main()
