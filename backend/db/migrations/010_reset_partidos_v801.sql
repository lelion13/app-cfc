-- Reparación: esquema v8.01 completo para partidos (datos de prueba se pierden).
-- Usar si partidos quedó roto o a medias tras create_all sin migración 009.

BEGIN;

DROP TABLE IF EXISTS goles_partido CASCADE;
DROP TABLE IF EXISTS partidos CASCADE;

TRUNCATE TABLE fechas_partido RESTART IDENTITY CASCADE;

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
);

CREATE INDEX IF NOT EXISTS ix_partidos_fecha_ref ON partidos(id_fecha_partido);
CREATE INDEX IF NOT EXISTS ix_partidos_categoria ON partidos(id_categoria);

CREATE TABLE goles_partido (
  id_gol BIGSERIAL PRIMARY KEY,
  id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON UPDATE CASCADE ON DELETE CASCADE,
  id_jugador BIGINT NOT NULL REFERENCES jugadores(id_jugador) ON UPDATE CASCADE ON DELETE RESTRICT,
  goles SMALLINT NOT NULL CHECK (goles >= 1),
  CONSTRAINT uq_goles_partido_jugador UNIQUE (id_partido, id_jugador)
);

CREATE INDEX IF NOT EXISTS ix_goles_partido_partido ON goles_partido(id_partido);
CREATE INDEX IF NOT EXISTS ix_goles_partido_jugador ON goles_partido(id_jugador);

COMMIT;
