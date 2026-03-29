-- Partidos por categoría: FK a categorias, UNIQUE(fecha_partido, id_categoria).
-- ADVERTENCIA: borra filas existentes en partidos/goles_partido (no hay backfill automático).
-- Si necesitás conservar datos, asigná id_categoria manualmente antes de aplicar o adaptá el script.

BEGIN;

TRUNCATE TABLE partidos RESTART IDENTITY CASCADE;

ALTER TABLE partidos DROP CONSTRAINT IF EXISTS uq_partidos_fecha;

ALTER TABLE partidos
  ADD COLUMN id_categoria BIGINT NOT NULL REFERENCES categorias(id_categoria) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE partidos ADD CONSTRAINT uq_partidos_fecha_categoria UNIQUE (fecha_partido, id_categoria);

CREATE INDEX IF NOT EXISTS ix_partidos_categoria ON partidos(id_categoria);

COMMIT;
