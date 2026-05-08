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

CREATE TABLE IF NOT EXISTS pagos (
  id_pago BIGSERIAL PRIMARY KEY,
  id_jugador BIGINT NOT NULL REFERENCES jugadores(id_jugador) ON UPDATE CASCADE ON DELETE RESTRICT,
  fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE,
  monto NUMERIC(12,2) NOT NULL CHECK (monto > 0),
  mes_correspondiente SMALLINT NOT NULL CHECK (mes_correspondiente BETWEEN 1 AND 12),
  anio_correspondiente SMALLINT NOT NULL CHECK (anio_correspondiente BETWEEN 2000 AND 2100),
  metodo_pago TEXT NOT NULL,
  comprobante_url TEXT,
  CONSTRAINT uq_pagos_periodo UNIQUE (id_jugador, mes_correspondiente, anio_correspondiente)
);

CREATE INDEX IF NOT EXISTS ix_pagos_jugador ON pagos(id_jugador);
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

CREATE TABLE IF NOT EXISTS partidos (
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

CREATE TABLE IF NOT EXISTS goles_partido (
  id_gol BIGSERIAL PRIMARY KEY,
  id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON UPDATE CASCADE ON DELETE CASCADE,
  id_jugador BIGINT NOT NULL REFERENCES jugadores(id_jugador) ON UPDATE CASCADE ON DELETE RESTRICT,
  goles SMALLINT NOT NULL CHECK (goles >= 1),
  CONSTRAINT uq_goles_partido_jugador UNIQUE (id_partido, id_jugador)
);

CREATE INDEX IF NOT EXISTS ix_goles_partido_partido ON goles_partido(id_partido);
CREATE INDEX IF NOT EXISTS ix_goles_partido_jugador ON goles_partido(id_jugador);
