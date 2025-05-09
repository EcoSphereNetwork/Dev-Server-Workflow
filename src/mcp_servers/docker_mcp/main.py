"""
Hauptmodul für den Docker MCP Server.

Dieses Modul bietet den Haupteinstiegspunkt für den Docker MCP Server.
"""

import os
import sys
import asyncio
import uvicorn
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import router
from .utils.logger import setup_logging
from .core.config import settings

# Konfiguriere Logging
logger = setup_logging()

# Erstelle FastAPI-App
app = FastAPI(
    title="Docker MCP Server",
    description="Ein MCP-Server für Docker-Operationen",
    version=settings.APP_VERSION,
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


def parse_args():
    """Parse die Kommandozeilenargumente."""
    parser = argparse.ArgumentParser(description="Docker MCP Server")
    parser.add_argument("--host", default=settings.HOST, help="Host")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port")
    parser.add_argument("--debug", action="store_true", help="Debug-Modus")
    return parser.parse_args()


def main():
    """Haupteinstiegspunkt."""
    # Parse die Argumente
    args = parse_args()
    
    # Starte den Server
    uvicorn.run(
        "src.mcp_servers.docker_mcp.main:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
    )


if __name__ == "__main__":
    main()