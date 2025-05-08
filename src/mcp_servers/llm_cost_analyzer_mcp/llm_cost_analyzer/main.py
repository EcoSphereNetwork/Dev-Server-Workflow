"""
LLM Cost Analyzer - Hauptanwendung

Dieses Modul initialisiert die FastAPI-Anwendung und schließt alle Router ein.
"""

import logging
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.router import api_router
from .core.config import settings
from .utils.logger import setup_logging

# Richte Logging ein
setup_logging()
logger = logging.getLogger(__name__)

# Erstelle FastAPI-App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Füge CORS-Middleware hinzu
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schließe API-Router ein
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root-Endpunkt, der grundlegende Informationen über die API zurückgibt."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.PROJECT_DESCRIPTION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health-Check-Endpunkt."""
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Globaler Exception-Handler."""
    logger.exception(f"Unbehandelte Ausnahme: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut."},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "llm_cost_analyzer.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )