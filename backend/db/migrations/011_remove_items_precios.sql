-- Elimina aranceles (items_pago / precios_item) y columnas asociadas en pagos.
-- Aplicar solo si no necesitás conservar vínculos históricos con ítems/precios.

ALTER TABLE pagos DROP CONSTRAINT IF EXISTS pagos_id_item_pago_fkey;
ALTER TABLE pagos DROP CONSTRAINT IF EXISTS pagos_id_precio_item_fkey;
DROP INDEX IF EXISTS ix_pagos_item_pago;
DROP INDEX IF EXISTS ix_pagos_precio_item;

ALTER TABLE pagos
  DROP COLUMN IF EXISTS id_item_pago,
  DROP COLUMN IF EXISTS id_precio_item,
  DROP COLUMN IF EXISTS descripcion_item_snapshot,
  DROP COLUMN IF EXISTS monto_snapshot;

DROP TABLE IF EXISTS precios_item CASCADE;
DROP TABLE IF EXISTS items_pago CASCADE;
