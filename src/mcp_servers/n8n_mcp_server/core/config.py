"""
Konfigurationsmodul für den n8n MCP Server.

Dieses Modul definiert die Konfigurationseinstellungen für den n8n MCP Server.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseSettings, Field, validator

# Basisverzeichnis
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class N8nMCPSettings(BaseSettings):
    """Konfigurationseinstellungen für den n8n MCP Server."""
    
    # Allgemeine Einstellungen
    APP_NAME: str = "n8n-mcp-server"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server-Einstellungen
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=3456, env="PORT")
    
    # n8n-Einstellungen
    N8N_URL: str = Field(default="http://localhost:5678", env="N8N_URL")
    N8N_API_KEY: Optional[str] = Field(default=None, env="N8N_API_KEY")
    N8N_WEBHOOK_URL: Optional[str] = Field(default=None, env="N8N_WEBHOOK_URL")
    N8N_WEBHOOK_PATH: str = Field(default="/webhook", env="N8N_WEBHOOK_PATH")
    
    # Authentifizierungseinstellungen
    AUTH_ENABLED: bool = Field(default=False, env="AUTH_ENABLED")
    AUTH_TOKEN: Optional[str] = Field(default=None, env="AUTH_TOKEN")
    
    # Audit-Einstellungen
    AUDIT_ENABLED: bool = Field(default=True, env="AUDIT_ENABLED")
    AUDIT_LOG_FILE: Path = Field(default=BASE_DIR / "logs" / "n8n_mcp_audit.log", env="AUDIT_LOG_FILE")
    
    # Metriken-Einstellungen
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_ENDPOINT: str = Field(default="/metrics", env="METRICS_ENDPOINT")
    
    # Logging-Einstellungen
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Path = Field(default=BASE_DIR / "logs" / "n8n_mcp.log", env="LOG_FILE")
    
    # Workflow-Einstellungen
    WORKFLOW_CACHE_ENABLED: bool = Field(default=True, env="WORKFLOW_CACHE_ENABLED")
    WORKFLOW_CACHE_TTL: int = Field(default=300, env="WORKFLOW_CACHE_TTL")  # 5 Minuten
    
    @validator("AUDIT_LOG_FILE", "LOG_FILE")
    def create_directory(cls, v):
        """Erstelle das Verzeichnis, wenn es nicht existiert."""
        if isinstance(v, Path):
            v.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("N8N_WEBHOOK_URL")
    def set_webhook_url(cls, v, values):
        """Setze die Webhook-URL, wenn sie nicht angegeben ist."""
        if v is None:
            host = values.get("HOST", "0.0.0.0")
            port = values.get("PORT", 3456)
            webhook_path = values.get("N8N_WEBHOOK_PATH", "/webhook")
            
            # Wenn der Host 0.0.0.0 ist, verwende localhost
            if host == "0.0.0.0":
                host = "localhost"
            
            return f"http://{host}:{port}{webhook_path}"
        return v
    
    class Config:
        """Pydantic-Konfiguration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "N8N_MCP_"


# Erstelle die Einstellungen
settings = N8nMCPSettings()