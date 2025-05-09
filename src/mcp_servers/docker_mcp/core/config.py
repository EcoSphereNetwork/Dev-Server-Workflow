"""
Konfigurationsmodul für den Docker MCP Server.

Dieses Modul definiert die Konfigurationseinstellungen für den Docker MCP Server.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseSettings, Field, validator

# Basisverzeichnis
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class DockerMCPSettings(BaseSettings):
    """Konfigurationseinstellungen für den Docker MCP Server."""
    
    # Allgemeine Einstellungen
    APP_NAME: str = "docker-mcp-server"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server-Einstellungen
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=3458, env="PORT")
    
    # Docker-Einstellungen
    DOCKER_HOST: Optional[str] = Field(default=None, env="DOCKER_HOST")
    DOCKER_API_VERSION: Optional[str] = Field(default=None, env="DOCKER_API_VERSION")
    DOCKER_TLS_VERIFY: bool = Field(default=False, env="DOCKER_TLS_VERIFY")
    DOCKER_CERT_PATH: Optional[str] = Field(default=None, env="DOCKER_CERT_PATH")
    
    # Authentifizierungseinstellungen
    AUTH_ENABLED: bool = Field(default=False, env="AUTH_ENABLED")
    AUTH_TOKEN: Optional[str] = Field(default=None, env="AUTH_TOKEN")
    
    # Audit-Einstellungen
    AUDIT_ENABLED: bool = Field(default=True, env="AUDIT_ENABLED")
    AUDIT_LOG_FILE: Path = Field(default=BASE_DIR / "logs" / "docker_mcp_audit.log", env="AUDIT_LOG_FILE")
    
    # Metriken-Einstellungen
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_ENDPOINT: str = Field(default="/metrics", env="METRICS_ENDPOINT")
    
    # Logging-Einstellungen
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Path = Field(default=BASE_DIR / "logs" / "docker_mcp.log", env="LOG_FILE")
    
    @validator("AUDIT_LOG_FILE", "LOG_FILE")
    def create_directory(cls, v):
        """Erstelle das Verzeichnis, wenn es nicht existiert."""
        if isinstance(v, Path):
            v.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        """Pydantic-Konfiguration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "DOCKER_MCP_"


# Erstelle die Einstellungen
settings = DockerMCPSettings()