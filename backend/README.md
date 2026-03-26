# Backend (FastAPI + PostgreSQL)

## Requisitos
- Python 3.11+
- PostgreSQL 14+

## Configuración
1. Copiá `.env.example` a `.env`.
2. Ejecutá `backend/db/schema.sql`.
3. Si la base ya existía, aplicá `backend/db/migrations/003_pagos_jugador_restrict.sql`.

## Instalar
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar
```bash
uvicorn app.main:app --reload
```
