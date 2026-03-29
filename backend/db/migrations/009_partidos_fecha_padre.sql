-- v8.01: Fecha de encuentro (padre) y partidos por categoría (hijo).
-- ADVERTENCIA: TRUNCATE borra partidos y goles_partido. Conservar datos requiere script de backfill manual.

BEGIN;

CREATE TABLE IF NOT EXISTS fechas_partido (
  id_fecha_partido BIGSERIAL PRIMARY KEY,
  fecha_partido DATE NOT NULL,
  es_local BOOLEAN NOT NULL,
  rival TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_fechas_partido_fecha UNIQUE (fecha_partido)
);

CREATE INDEX IF NOT EXISTS ix_fechas_partido_fecha ON fechas_partido(fecha_partido);

TRUNCATE TABLE goles_partido RESTART IDENTITY;
TRUNCATE TABLE partidos RESTART IDENTITY;

ALTER TABLE partidos DROP CONSTRAINT IF EXISTS uq_partidos_fecha_categoria;

ALTER TABLE partidos DROP COLUMN IF EXISTS fecha_partido;
ALTER TABLE partidos DROP COLUMN IF EXISTS es_local;
ALTER TABLE partidos DROP COLUMN IF EXISTS rival;

ALTER TABLE partidos
  ADD COLUMN id_fecha_partido BIGINT NOT NULL REFERENCES fechas_partido(id_fecha_partido) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE partidos ADD COLUMN hora_partido TIME;
ALTER TABLE partidos
  ADD COLUMN goles_nuestro SMALLINT NOT NULL DEFAULT 0 CHECK (goles_nuestro >= 0 AND goles_nuestro <= 99);

ALTER TABLE partidos ADD CONSTRAINT uq_partidos_fecha_categoria UNIQUE (id_fecha_partido, id_categoria);

DROP INDEX IF EXISTS ix_partidos_fecha;
CREATE INDEX IF NOT EXISTS ix_partidos_fecha_ref ON partidos(id_fecha_partido);

COMMIT;
