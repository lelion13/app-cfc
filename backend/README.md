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
