# Frontend (React + Tailwind)

## Configuración
1. Copiá `.env.example` a `.env`.
2. Instalá dependencias:
```bash
npm install
```
3. Ejecutá:
```bash
npm run dev
```

## Deploy (VPS Docker)
- Para dominio compartido con Traefik (`cfc.lionapp.cloud`), el frontend usa por defecto `/api/v1`.
- Si necesitás un backend externo, definí `VITE_API_BASE_URL` con la URL completa del API.
