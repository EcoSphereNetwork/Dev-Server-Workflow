"""
API-Router für den LLM Cost Analyzer.

Dieses Modul definiert den Haupt-API-Router und schließt alle Unter-Router ein.
"""

from fastapi import APIRouter

from .endpoints import analyze, estimate, models

# Erstelle Haupt-API-Router
api_router = APIRouter()

# Schließe Unter-Router ein
api_router.include_router(analyze.router, prefix="/analyze", tags=["Analyze"])
api_router.include_router(estimate.router, prefix="/estimate", tags=["Estimate"])
api_router.include_router(models.router, prefix="/models", tags=["Models"])