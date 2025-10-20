# -*- coding: utf-8 -*-
"""
app.py
----------------------------------
App Factory principal de Tutorín.
- Crea la aplicación FastAPI
- Monta routers de análisis y resolución
- Configura CORS para frontend local o remoto
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers principales
from routes.analyze_prompt import router as analyze_router
from routes.solve import router as solve_router

# -------------------------------------------------------
# CREAR APP
# -------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title="Tutorín API",
        description="Backend educativo de Tutorín: análisis y resolución paso a paso.",
        version="1.0.0"
    )

    # CORS (permite llamadas desde frontend local y remoto)
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://tutorin.netlify.app",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------------------------------------------
    # RUTAS PRINCIPALES
    # ---------------------------------------------------
    app.include_router(analyze_router, prefix="/analyze", tags=["Analyze"])
    app.include_router(solve_router, prefix="/solve", tags=["Solve"])

    # Ruta raíz simple (útil para probar que el backend responde)
    @app.get("/")
    def root():
        return {
            "message": "👋 Hola, soy Tutorín API.",
            "status": "online",
            "routes": ["/analyze/text", "/solve"]
        }

    return app


# -------------------------------------------------------
# EJECUCIÓN DIRECTA
# -------------------------------------------------------
app = create_app()
