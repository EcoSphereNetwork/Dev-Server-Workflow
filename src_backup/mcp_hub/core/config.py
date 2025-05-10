"""
Konfigurationsmodul für den MCP Hub.

Dieses Modul definiert die Konfigurationseinstellungen für den MCP Hub.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseSettings, Field, validator

# Basisverzeichnis
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class HubSettings(BaseSettings):
    """Konfigurationseinstellungen für den MCP Hub."""
    
    # Allgemeine Einstellungen
    APP_NAME: str = "mcp-hub"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Verzeichnisse
    CONFIG_DIR: Path = Field(default=BASE_DIR / "config")
    DATA_DIR: Path = Field(default=BASE_DIR / "data")
    LOGS_DIR: Path = Field(default=BASE_DIR / "logs")
    
    # MCP-Server-Einstellungen
    MCP_SERVER_REGISTRY_FILE: Path = Field(default=BASE_DIR / "config" / "mcp_server_registry.json")
    MCP_SERVER_CONFIG_DIR: Path = Field(default=BASE_DIR / "config" / "mcp_servers")
    
    # Repository-Einstellungen
    DEFAULT_REPOSITORIES: List[str] = Field(
        default=[
            "https://github.com/EcoSphereNetwork/mcp-server-registry",
        ]
    )
    
    # Docker-Hub-Einstellungen
    DEFAULT_DOCKER_HUB_USERS: List[str] = Field(
        default=[
            "ecosphere",
        ]
    )
    
    # Logging-Einstellungen
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    @validator("CONFIG_DIR", "DATA_DIR", "LOGS_DIR", "MCP_SERVER_REGISTRY_FILE", "MCP_SERVER_CONFIG_DIR")
    def create_directory(cls, v):
        """Erstelle das Verzeichnis, wenn es nicht existiert."""
        if isinstance(v, Path):
            if v.suffix:  # Wenn es eine Datei ist
                v.parent.mkdir(parents=True, exist_ok=True)
            else:  # Wenn es ein Verzeichnis ist
                v.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        """Pydantic-Konfiguration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "MCP_HUB_"


# Erstelle die Einstellungen
settings = HubSettings()