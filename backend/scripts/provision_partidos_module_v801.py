"""
Crea o reemplaza el módulo partidos v8.01 en una base PostgreSQL (Neon, local, etc.).
Requisitos: tablas public.categorias y public.jugadores ya existentes.
Uso (desde backend):
  python scripts/provision_partidos_module_v801.py "postgresql+psycopg://USER:PASS@HOST/DB?sslmode=require"
Borra datos en goles_partido, partidos y fechas_partido.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text

REQUIRED = ("categorias", "jugadores")

STMTS = [
    "DROP TABLE IF EXISTS goles_partido CASCADE",
    "DROP TABLE IF EXISTS partidos CASCADE",
    "DROP TABLE IF EXISTS fechas_partido CASCADE",
    """
CREATE TABLE fechas_partido (
  id_fecha_partido BIGSERIAL PRIMARY KEY,
  fecha_partido DATE NOT NULL,
  es_local BOOLEAN NOT NULL,
  rival TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_fechas_partido_fecha UNIQUE (fecha_partido)
)
""",
    "CREATE INDEX ix_fechas_partido_fecha ON fechas_partido(fecha_partido)",
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
    "CREATE INDEX ix_partidos_fecha_ref ON partidos(id_fecha_partido)",
    "CREATE INDEX ix_partidos_categoria ON partidos(id_categoria)",
    """
CREATE TABLE goles_partido (
  id_gol BIGSERIAL PRIMARY KEY,
  id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON UPDATE CASCADE ON DELETE CASCADE,
  id_jugador BIGINT NOT NULL REFERENCES jugadores(id_jugador) ON UPDATE CASCADE ON DELETE RESTRICT,
  goles SMALLINT NOT NULL CHECK (goles >= 1),
  CONSTRAINT uq_goles_partido_jugador UNIQUE (id_partido, id_jugador)
)
""",
    "CREATE INDEX ix_goles_partido_partido ON goles_partido(id_partido)",
    "CREATE INDEX ix_goles_partido_jugador ON goles_partido(id_jugador)",
]


def table_exists(conn, name: str) -> bool:
    r = conn.execute(
        text("SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = :n"),
        {"n": name},
    ).scalar()
    return r is not None


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python scripts/provision_partidos_module_v801.py DATABASE_URL", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1].strip()
    engine = create_engine(url)
    with engine.connect() as conn:
        missing = [t for t in REQUIRED if not table_exists(conn, t)]
        if missing:
            print(f"Error: faltan tablas requeridas: {missing}. Aplicá schema.sql base antes.", file=sys.stderr)
            sys.exit(1)
    with engine.begin() as conn:
        for stmt in STMTS:
            conn.execute(text(stmt.strip()))
    print("OK: fechas_partido, partidos y goles_partido creados (v8.01). Datos anteriores de esas tablas eliminados.")


if __name__ == "__main__":
    main()
