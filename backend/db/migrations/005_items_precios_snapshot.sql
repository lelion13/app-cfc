-- v6.0: agrega items tabulados y precios versionados con snapshot histórico en pagos.

CREATE TABLE IF NOT EXISTS items_pago (
  id_item_pago BIGSERIAL PRIMARY KEY,
  codigo TEXT NOT NULL UNIQUE,
  descripcion TEXT NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS ix_items_pago_codigo ON items_pago(codigo);
CREATE INDEX IF NOT EXISTS ix_items_pago_activo ON items_pago(activo);

CREATE TABLE IF NOT EXISTS precios_item (
  id_precio_item BIGSERIAL PRIMARY KEY,
  id_item_pago BIGINT NOT NULL REFERENCES items_pago(id_item_pago) ON UPDATE CASCADE ON DELETE CASCADE,
  id_categoria BIGINT REFERENCES categorias(id_categoria) ON UPDATE CASCADE ON DELETE SET NULL,
  monto NUMERIC(12,2) NOT NULL CHECK (monto > 0),
  vigencia_desde DATE NOT NULL,
  vigencia_hasta DATE,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT uq_precios_item_inicio UNIQUE (id_item_pago, id_categoria, vigencia_desde),
  CONSTRAINT ck_precios_item_rango CHECK (vigencia_hasta IS NULL OR vigencia_hasta >= vigencia_desde)
);

CREATE INDEX IF NOT EXISTS ix_precios_item_item ON precios_item(id_item_pago);
CREATE INDEX IF NOT EXISTS ix_precios_item_categoria ON precios_item(id_categoria);
CREATE INDEX IF NOT EXISTS ix_precios_item_activo ON precios_item(activo);
CREATE INDEX IF NOT EXISTS ix_precios_item_desde ON precios_item(vigencia_desde);
CREATE INDEX IF NOT EXISTS ix_precios_item_hasta ON precios_item(vigencia_hasta);

ALTER TABLE pagos ADD COLUMN IF NOT EXISTS id_item_pago BIGINT;
ALTER TABLE pagos ADD COLUMN IF NOT EXISTS id_precio_item BIGINT;
ALTER TABLE pagos ADD COLUMN IF NOT EXISTS descripcion_item_snapshot TEXT;
ALTER TABLE pagos ADD COLUMN IF NOT EXISTS monto_snapshot NUMERIC(12,2);

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'pagos_id_item_pago_fkey'
  ) THEN
    ALTER TABLE pagos
      ADD CONSTRAINT pagos_id_item_pago_fkey
      FOREIGN KEY (id_item_pago) REFERENCES items_pago(id_item_pago)
      ON UPDATE CASCADE ON DELETE SET NULL;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'pagos_id_precio_item_fkey'
  ) THEN
    ALTER TABLE pagos
      ADD CONSTRAINT pagos_id_precio_item_fkey
      FOREIGN KEY (id_precio_item) REFERENCES precios_item(id_precio_item)
      ON UPDATE CASCADE ON DELETE SET NULL;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_pagos_item_pago ON pagos(id_item_pago);
CREATE INDEX IF NOT EXISTS ix_pagos_precio_item ON pagos(id_precio_item);

-- Backfill mínimo legacy
UPDATE pagos
SET descripcion_item_snapshot = COALESCE(descripcion_item_snapshot, 'Legacy'),
    monto_snapshot = COALESCE(monto_snapshot, monto)
WHERE descripcion_item_snapshot IS NULL OR monto_snapshot IS NULL;
