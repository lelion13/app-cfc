# Backend (FastAPI + PostgreSQL)

## Requisitos
- Python 3.11+
- PostgreSQL 14+

## Configuración
1. Copiá `.env.example` a `.env`.
2. Ejecutá `backend/db/schema.sql`.
3. Si la base ya existía, aplicá `backend/db/migrations/003_pagos_jugador_restrict.sql`.
4. Para pagos tabulados por ítem/precio, aplicá también `backend/db/migrations/005_items_precios_snapshot.sql`.
5. Para el rol `Operador` (v8.0), aplicá `backend/db/migrations/006_rol_operador.sql` en bases que ya tengan el enum `rol_usuario` con solo `Admin`/`Coordinador`. En instalaciones nuevas desde `schema.sql` actualizado, el enum ya incluye `Operador`.
6. Para partidos del campeonato (v8.1), aplicá `backend/db/migrations/007_partidos_goles.sql` si la base no tiene aún las tablas `partidos` y `goles_partido`.
7. Para asociar cada partido a una categoría (v8.2), aplicá `backend/db/migrations/008_partidos_categoria.sql` en bases que ya tengan `partidos` sin `id_categoria`. **La migración trunca** `partidos` y `goles_partido`.
8. Para fechas de encuentro y partidos por categoría (v8.01), aplicá `backend/db/migrations/009_partidos_fecha_padre.sql` en bases que aún tengan `partidos` con columnas `fecha_partido`/`rival` en la fila del partido. **La migración trunca** `partidos` y `goles_partido`. En instalaciones nuevas desde `schema.sql` actualizado, existen `fechas_partido` y `partidos` enlazados con `id_fecha_partido`, `hora_partido` y `goles_nuestro`.
9. Si `partidos` quedó roto o a medias (por ejemplo `create_all` creó `fechas_partido` pero no alteró `partidos`), aplicá `backend/db/migrations/010_reset_partidos_v801.sql` con psql, o desde `backend` ejecutá `python scripts/apply_010_reset_partidos.py`. **Elimina** tablas `goles_partido` y `partidos`, las recrea con el esquema v8.01 y **vacía** `fechas_partido` (solo datos de partidos/fechas).

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

## Deploy (Render + Neon)
- `DATABASE_URL` debe apuntar a Neon con SSL (`...?sslmode=require`).
- Configurá `CORS_ORIGINS` con tu dominio Vercel (ej: `https://app-cfc-theta.vercel.app`).
- Mantené `JWT_SECRET` y `SETUP_TOKEN` como secretos de entorno (no en git).
