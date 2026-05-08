# Backend (FastAPI + PostgreSQL)

## Requisitos
- Python 3.11+
- PostgreSQL 14+

## Configuración
1. Copiá `.env.example` a `.env` (`DATABASE_URL`, `JWT_SECRET`, etc.).
2. **Esquema de base de datos (Alembic)** — desde la carpeta `backend` con el venv activado:
   - Base **vacía**: `alembic upgrade head`
   - Base **ya creada** con el mismo esquema (p. ej. cargaste `db/schema.sql` antes): una sola vez `alembic stamp 0001` para alinear la tabla `alembic_version` sin volver a crear tablas.
3. Migraciones históricas en `backend/db/migrations/` quedan como referencia de cambios antiguos; el flujo nuevo es solo Alembic.

## Alembic (resumen)
```bash
cd backend
alembic current
alembic upgrade head
alembic revision -m "descripcion"  # luego editá upgrade/downgrade
```
En Docker (misma `DATABASE_URL` que el backend, típicamente host `db`):
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod run --rm backend alembic upgrade head
```

## Instalar
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Primer administrador (bootstrap)

1. Definí `SETUP_TOKEN` en `.env` (string largo y aleatorio; no lo subas al repo).
2. Con la base vacía (`usuarios` sin filas), el backend expone:
   - `GET /api/v1/auth/bootstrap-status` → `{ "allowed": true }` solo si no hay usuarios **y** `SETUP_TOKEN` está configurado (mínimo 8 caracteres).
   - `POST /api/v1/auth/bootstrap` con JSON `{ "username", "password", "setup_token" }` crea el primer usuario con rol `Admin`.
3. Tras el primer login, rotá o vaciá `SETUP_TOKEN` en el servidor (p. ej. Render) para deshabilitar el endpoint.

## Ejecutar
```bash
uvicorn app.main:app --reload
```

## Deploy (VPS Docker)
- `DATABASE_URL` debe apuntar al servicio `db` en Docker Compose (ej: `postgresql+psycopg://postgres:***@db:5432/club`).
- Configurá `CORS_ORIGINS` con el dominio final (ej: `https://cfc.lionapp.cloud`).
- Mantené `JWT_SECRET` y `SETUP_TOKEN` como secretos de entorno (no en git).
- El esquema se aplica con **Alembic** (`alembic upgrade head`); ver arriba.
