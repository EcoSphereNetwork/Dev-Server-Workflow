"""
API router for the Prompt MCP Server.

This module defines the main API router and includes all sub-routers.
"""

from fastapi import APIRouter

from .endpoints import chat, models, templates, optimize

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(models.router, prefix="/models", tags=["Models"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(optimize.router, prefix="/optimize", tags=["Optimize"])
