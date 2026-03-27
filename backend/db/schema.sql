CREATE TABLE IF NOT EXISTS categorias (
  id_categoria BIGSERIAL PRIMARY KEY,
  descripcion TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS jugadores (
  id_jugador BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  apellido TEXT NOT NULL,
  fecha_nacimiento DATE NOT NULL,
  tipo_documento TEXT NOT NULL,
  numero_documento TEXT NOT NULL,
  domicilio TEXT,
  nombre_tutor TEXT,
  apellido_tutor TEXT,
  celular_tutor TEXT,
  mail_tutor TEXT,
  id_categoria BIGINT NOT NULL REFERENCES categorias(id_categoria) ON UPDATE CASCADE ON DELETE RESTRICT,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT ck_jugadores_tipo_documento CHECK (tipo_documento IN ('DNI', 'LC', 'LE', 'PASAPORTE')),
  CONSTRAINT uq_jugadores_documento UNIQUE (tipo_documento, numero_documento)
);

CREATE INDEX IF NOT EXISTS ix_jugadores_categoria ON jugadores(id_categoria);
CREATE INDEX IF NOT EXISTS ix_jugadores_activo ON jugadores(activo);
CREATE INDEX IF NOT EXISTS ix_jugadores_apellido ON jugadores(apellido);

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

CREATE TABLE IF NOT EXISTS pagos (
  id_pago BIGSERIAL PRIMARY KEY,
  id_jugador BIGINT NOT NULL REFERENCES jugadores(id_jugador) ON UPDATE CASCADE ON DELETE RESTRICT,
  id_item_pago BIGINT REFERENCES items_pago(id_item_pago) ON UPDATE CASCADE ON DELETE SET NULL,
  id_precio_item BIGINT REFERENCES precios_item(id_precio_item) ON UPDATE CASCADE ON DELETE SET NULL,
  fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE,
  monto NUMERIC(12,2) NOT NULL CHECK (monto > 0),
  descripcion_item_snapshot TEXT,
  monto_snapshot NUMERIC(12,2),
  mes_correspondiente SMALLINT NOT NULL CHECK (mes_correspondiente BETWEEN 1 AND 12),
  anio_correspondiente SMALLINT NOT NULL CHECK (anio_correspondiente BETWEEN 2000 AND 2100),
  metodo_pago TEXT NOT NULL,
  comprobante_url TEXT,
  CONSTRAINT uq_pagos_periodo UNIQUE (id_jugador, mes_correspondiente, anio_correspondiente)
);

CREATE INDEX IF NOT EXISTS ix_pagos_jugador ON pagos(id_jugador);
CREATE INDEX IF NOT EXISTS ix_pagos_item_pago ON pagos(id_item_pago);
CREATE INDEX IF NOT EXISTS ix_pagos_precio_item ON pagos(id_precio_item);
CREATE INDEX IF NOT EXISTS ix_pagos_periodo ON pagos(anio_correspondiente, mes_correspondiente);
CREATE INDEX IF NOT EXISTS ix_pagos_fecha ON pagos(fecha_pago);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rol_usuario') THEN
    CREATE TYPE rol_usuario AS ENUM ('Admin', 'Coordinador', 'Operador');
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario BIGSERIAL PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  rol rol_usuario NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_usuarios_rol ON usuarios(rol);
CREATE INDEX IF NOT EXISTS ix_usuarios_activo ON usuarios(activo);
