-- v8.0: agrega valor Operador al enum rol_usuario (idempotente).
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_enum e
    JOIN pg_type t ON e.enumtypid = t.oid
    WHERE t.typname = 'rol_usuario' AND e.enumlabel = 'Operador'
  ) THEN
    ALTER TYPE rol_usuario ADD VALUE 'Operador';
  END IF;
END $$;
