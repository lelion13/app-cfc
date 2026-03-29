"""One-off: validar esquema partidos vs v8.01. Ejecutar: python scripts/check_partidos_schema.py (cwd = backend)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text

from app.core.config import settings

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


def main() -> None:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        def cols(table: str) -> set[str]:
            q = text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :t
                ORDER BY ordinal_position
                """
            )
            return {r[0] for r in conn.execute(q, {"t": table}).fetchall()}

        fc = cols("fechas_partido")
        pc = cols("partidos")

        print("fechas_partido: OK" if fc == EXPECTED_FECHAS else "fechas_partido: INCOMPLETO")
        if fc != EXPECTED_FECHAS:
            print("  esperado:", sorted(EXPECTED_FECHAS))
            print("  actual:  ", sorted(fc))
            print("  falta:   ", sorted(EXPECTED_FECHAS - fc))
            print("  sobra:   ", sorted(fc - EXPECTED_FECHAS))

        print("partidos: OK" if pc == EXPECTED_PARTIDOS else "partidos: NO ACTUALIZADO / ROTO")
        if pc != EXPECTED_PARTIDOS:
            print("  esperado:", sorted(EXPECTED_PARTIDOS))
            print("  actual:  ", sorted(pc))
            print("  falta:   ", sorted(EXPECTED_PARTIDOS - pc))
            print("  sobra:   ", sorted(pc - EXPECTED_PARTIDOS))

        try:
            np = conn.execute(text("SELECT COUNT(*) FROM partidos")).scalar()
            nf = conn.execute(text("SELECT COUNT(*) FROM fechas_partido")).scalar()
            print(f"Filas: partidos={np}, fechas_partido={nf}")
        except Exception as e:
            print("Count error:", e)


if __name__ == "__main__":
    main()
