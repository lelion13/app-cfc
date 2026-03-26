-- Ensure jugadores with pagos cannot be deleted
ALTER TABLE pagos DROP CONSTRAINT IF EXISTS pagos_id_jugador_fkey;
ALTER TABLE pagos
  ADD CONSTRAINT pagos_id_jugador_fkey
  FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
  ON UPDATE CASCADE ON DELETE RESTRICT;
