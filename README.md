# Club de Fútbol MVP

Monorepo con:
- `backend`: FastAPI + PostgreSQL
- `frontend`: React + Tailwind

## Backend
Ver `backend/README.md`.

## Frontend
Ver `frontend/README.md`.

## Deploy VPS (Docker + Traefik + GHCR)

El proyecto incluye:
- `docker-compose.prod.yml` con servicios `db`, `backend`, `frontend`.
- Imágenes en GHCR:
  - `ghcr.io/lelion13/app-cfc-backend`
  - `ghcr.io/lelion13/app-cfc-frontend`
- Workflow: `.github/workflows/publish-ghcr.yml`

### Variables de producción
1. Copiar `.env.prod.example` a `.env.prod`.
2. Ajustar secretos reales (`POSTGRES_PASSWORD`, `JWT_SECRET`, etc).

### Inicialización de base de datos (primer deploy)
Con el stack levantado y la DB saludable, migrá con Alembic (la imagen `backend` incluye `alembic/`):

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod run --rm backend alembic upgrade head
```

Si la base **ya tenía** el mismo esquema creado a mano (`schema.sql`), alineá solo la versión sin recrear tablas:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod run --rm backend alembic stamp 0001
```

`backend/db/schema.sql` sigue como referencia legible; el flujo operativo es **Alembic** (`backend/README.md`).

### Routing Traefik (dominio único)
- Frontend y backend comparten `https://cfc.lionapp.cloud`.
- Backend atiende: `/api`, `/health`, `/docs`, `/openapi.json`.
- Frontend excluye explícitamente esos prefijos/rutas para evitar que `/api` responda HTML.

### Despliegue operativo (`latest`)
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod pull
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
```

Smoke check mínimo:
```bash
curl -s https://cfc.lionapp.cloud/api/v1/auth/bootstrap-status
```
Debe responder JSON (no HTML).
