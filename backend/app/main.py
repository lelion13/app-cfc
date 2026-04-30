from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, categorias, fechas_partido, ingresos, items_pagos, jugadores, pagos, partidos, usuarios


def create_app() -> FastAPI:
    app = FastAPI(title="Club Futbol MVP", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(categorias.router, prefix="/api/v1")
    app.include_router(ingresos.router, prefix="/api/v1")
    app.include_router(items_pagos.router, prefix="/api/v1")
    app.include_router(jugadores.router, prefix="/api/v1")
    app.include_router(pagos.router, prefix="/api/v1")
    app.include_router(fechas_partido.router, prefix="/api/v1")
    app.include_router(partidos.router, prefix="/api/v1")
    app.include_router(usuarios.router, prefix="/api/v1")
    return app


app = create_app()
