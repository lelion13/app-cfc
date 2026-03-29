"""Aplica db/migrations/010_reset_partidos_v801.sql usando DATABASE_URL del .env (cwd = backend)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text

from app.core.config import settings

STMTS = [
    "DROP TABLE IF EXISTS goles_partido CASCADE",
    "DROP TABLE IF EXISTS partidos CASCADE",
    "TRUNCATE TABLE fechas_partido RESTART IDENTITY CASCADE",
    """
CREATE TABLE partidos (
  id_partido BIGSERIAL PRIMARY KEY,
  id_fecha_partido BIGINT NOT NULL REFERENCES fechas_partido(id_fecha_partido) ON UPDATE CASCADE ON DELETE CASCADE,
  id_categoria BIGINT NOT NULL REFERENCES categorias(id_categoria) ON UPDATE CASCADE ON DELETE RESTRICT,
  hora_partido TIME,
  goles_nuestro SMALLINT NOT NULL DEFAULT 0 CHECK (goles_nuestro >= 0 AND goles_nuestro <= 99),
  goles_rival SMALLINT NOT NULL DEFAULT 0 CHECK (goles_rival >= 0 AND goles_rival <= 99),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_partidos_fecha_categoria UNIQUE (id_fecha_partido, id_categoria)
)
""",
    "CREATE INDEX IF NOT EXISTS ix_partidos_fecha_ref ON partidos(id_fecha_partido)",
    "CREATE INDEX IF NOT EXISTS ix_partidos_categoria ON partidos(id_categoria)",
    """
CREATE TABLE goles_partido (
  id_gol BIGSERIAL PRIMARY KEY,
  id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON UPDATE CASCADE ON DELETE CASCADE,
  id_jugador BIGINT NOT NULL REFERENCES jugadores(id_jugador) ON UPDATE CASCADE ON DELETE RESTRICT,
  goles SMALLINT NOT NULL CHECK (goles >= 1),
  CONSTRAINT uq_goles_partido_jugador UNIQUE (id_partido, id_jugador)
)
""",
    "CREATE INDEX IF NOT EXISTS ix_goles_partido_partido ON goles_partido(id_partido)",
    "CREATE INDEX IF NOT EXISTS ix_goles_partido_jugador ON goles_partido(id_jugador)",
]


def main() -> None:
    engine = create_engine(settings.database_url)
    with engine.begin() as conn:
        for stmt in STMTS:
            conn.execute(text(stmt.strip()))
    print("010 aplicado: partidos/goles_partido recreados, fechas_partido vacía.")


if __name__ == "__main__":
    main()
