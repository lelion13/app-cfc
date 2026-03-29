-- Partidos del campeonato + goleadores por jugador (v8.1).

CREATE TABLE IF NOT EXISTS partidos (
  id_partido BIGSERIAL PRIMARY KEY,
  fecha_partido DATE NOT NULL,
  es_local BOOLEAN NOT NULL,
  rival TEXT NOT NULL,
  goles_rival SMALLINT NOT NULL DEFAULT 0 CHECK (goles_rival >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_partidos_fecha UNIQUE (fecha_partido)
);

CREATE INDEX IF NOT EXISTS ix_partidos_fecha ON partidos(fecha_partido);

CREATE TABLE IF NOT EXISTS goles_partido (
  id_gol BIGSERIAL PRIMARY KEY,
  id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON UPDATE CASCADE ON DELETE CASCADE,
  id_jugador BIGINT NOT NULL REFERENCES jugadores(id_jugador) ON UPDATE CASCADE ON DELETE RESTRICT,
  goles SMALLINT NOT NULL CHECK (goles >= 1),
  CONSTRAINT uq_goles_partido_jugador UNIQUE (id_partido, id_jugador)
);

CREATE INDEX IF NOT EXISTS ix_goles_partido_partido ON goles_partido(id_partido);
CREATE INDEX IF NOT EXISTS ix_goles_partido_jugador ON goles_partido(id_jugador);
