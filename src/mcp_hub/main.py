"""
Hauptmodul für den MCP Hub.

Dieses Modul bietet den Haupteinstiegspunkt für den MCP Hub.
"""

import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import router
from .utils.logger import setup_logging
from .core.config import settings

# Konfiguriere Logging
logger = setup_logging()

# Erstelle FastAPI-App
app = FastAPI(
    title="MCP Hub",
    description="Ein Hub für MCP-Server",
    version="0.1.0",
)

# Konfiguriere CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Füge Router hinzu
app.include_router(router)


@app.get("/health")
async def health_check():
    """Gesundheitscheck-Endpunkt."""
    return {"status": "ok"}


def main():
    """Haupteinstiegspunkt."""
    # Starte den Server
    uvicorn.run(
        "src.mcp_hub.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()