"""
Modelle für MCP-Server.

Dieses Modul definiert die Datenmodelle für MCP-Server.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime


class ServerStatus(str, Enum):
    """Status eines MCP-Servers."""
    
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    ERROR = "error"


class ServerType(str, Enum):
    """Typ eines MCP-Servers."""
    
    N8N = "n8n"
    OPENHANDS = "openhands"
    DOCKER = "docker"
    GENERATOR = "generator"
    LLM_COST_ANALYZER = "llm_cost_analyzer"
    PROMPT = "prompt"
    CUSTOM = "custom"


class ServerProtocol(str, Enum):
    """Protokoll eines MCP-Servers."""
    
    HTTP = "http"
    WEBSOCKET = "websocket"
    STDIO = "stdio"


class ServerTool(BaseModel):
    """Tool eines MCP-Servers."""
    
    name: str
    description: str
    parameter_schema: Dict[str, Any]


class ServerInfo(BaseModel):
    """Informationen über einen MCP-Server."""
    
    name: str
    description: str
    version: str
    type: ServerType
    protocol: ServerProtocol
    url: Optional[HttpUrl] = None
    status: ServerStatus = ServerStatus.UNKNOWN
    tools: List[ServerTool] = []
    last_seen: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    @validator("url", pre=True)
    def validate_url(cls, v):
        """Validiere die URL."""
        if v is None:
            return v
        if isinstance(v, str) and not v.startswith(("http://", "https://")):
            return f"http://{v}"
        return v


class ServerConfig(BaseModel):
    """Konfiguration eines MCP-Servers."""
    
    name: str
    description: str
    type: ServerType
    protocol: ServerProtocol
    url: Optional[HttpUrl] = None
    auth_token: Optional[str] = None
    enabled: bool = True
    auto_start: bool = False
    auto_restart: bool = False
    metadata: Dict[str, Any] = {}
    
    @validator("url", pre=True)
    def validate_url(cls, v):
        """Validiere die URL."""
        if v is None:
            return v
        if isinstance(v, str) and not v.startswith(("http://", "https://")):
            return f"http://{v}"
        return v


class ServerRegistry(BaseModel):
    """Registry von MCP-Servern."""
    
    servers: Dict[str, ServerConfig] = {}
    repositories: List[str] = []
    docker_hub_users: List[str] = []
    last_updated: Optional[datetime] = None