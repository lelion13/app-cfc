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

## Deploy (Vercel)
- Definí `VITE_API_BASE_URL` apuntando al backend Render con `/api/v1`.
  - Ejemplo: `https://app-cfc.onrender.com/api/v1`
- Luego hacé redeploy para que tome la variable nueva.
