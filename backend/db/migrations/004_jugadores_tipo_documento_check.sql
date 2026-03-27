-- v5.1: Restringe tipo_documento a catálogo controlado.
-- Como no hay jugadores cargados, no requiere normalización previa.

ALTER TABLE jugadores DROP CONSTRAINT IF EXISTS ck_jugadores_tipo_documento;

ALTER TABLE jugadores
  ADD CONSTRAINT ck_jugadores_tipo_documento
  CHECK (tipo_documento IN ('DNI', 'LC', 'LE', 'PASAPORTE'));
