"""
LLM Cost Analyzer MCP Server - Hauptanwendung

Dieses Modul initialisiert die FastAPI-Anwendung und schließt alle Router ein.
"""

import logging
from typing import Dict, Any

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.router import api_router
from .core.config import settings
from .core.llm_selector import LLMSelector
from .core.task_cost_estimator import TaskCostEstimator
from .utils.logger import setup_logging
from .mcp_interface import get_mcp_interface

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
        "mcp_compatible": True,
        "mcp_version": "1.0",
        "mcp_endpoint": "/api/v1/ws/mcp",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health-Check-Endpunkt."""
    return {"status": "ok"}


@app.get("/mcp-info", tags=["MCP"])
async def mcp_info() -> Dict[str, Any]:
    """MCP-Informationsendpunkt."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.PROJECT_DESCRIPTION,
        "mcp_compatible": True,
        "mcp_version": "1.0",
        "mcp_endpoint": "/api/v1/ws/mcp",
        "capabilities": [
            "analyze_complexity",
            "estimate_cost",
            "generate_report",
            "list_models"
        ],
        "supported_models": {
            "local": True,
            "cloud": True
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Globaler Exception-Handler."""
    logger.exception(f"Unbehandelte Ausnahme: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut."},
    )


# Erstelle Abhängigkeiten
def get_llm_selector():
    """Hole LLM-Selektor-Abhängigkeit."""
    return LLMSelector()


def get_task_cost_estimator(
    llm_selector: LLMSelector = Depends(get_llm_selector),
):
    """Hole Aufgabenkostenrechner-Abhängigkeit."""
    return TaskCostEstimator(llm_selector)


# Initialisiere MCP Interface
@app.on_event("startup")
async def startup_event():
    """Startup-Event-Handler."""
    llm_selector = get_llm_selector()
    task_cost_estimator = get_task_cost_estimator(llm_selector)
    get_mcp_interface(llm_selector, task_cost_estimator)
    logger.info("MCP Interface initialisiert")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "llm_cost_analyzer_mcp.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )