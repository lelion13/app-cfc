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
Con el stack levantado y la DB saludable, ejecutar desde el servidor:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < backend/db/schema.sql
```

Si migrás una base existente, aplicar los scripts en `backend/db/migrations/` según corresponda antes de exponer tráfico.
