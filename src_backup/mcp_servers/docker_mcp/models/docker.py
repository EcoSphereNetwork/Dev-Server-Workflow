"""
Docker-Modelle für den Docker MCP Server.

Dieses Modul definiert die Datenmodelle für Docker-Ressourcen.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ContainerStatus(str, Enum):
    """Status eines Containers."""
    
    RUNNING = "running"
    CREATED = "created"
    RESTARTING = "restarting"
    REMOVING = "removing"
    PAUSED = "paused"
    EXITED = "exited"
    DEAD = "dead"


class RestartPolicy(BaseModel):
    """Neustart-Richtlinie eines Containers."""
    
    name: str
    maximum_retry_count: int = 0


class PortMapping(BaseModel):
    """Port-Mapping eines Containers."""
    
    host_ip: str = "0.0.0.0"
    host_port: int
    container_port: int
    protocol: str = "tcp"


class Mount(BaseModel):
    """Mount eines Containers."""
    
    type: str
    source: str
    target: str
    read_only: bool = False
    consistency: str = "default"
    propagation: str = "rprivate"


class Container(BaseModel):
    """Container-Modell."""
    
    id: str
    name: str
    image: str
    status: ContainerStatus
    created: datetime
    ports: Dict[str, List[Dict[str, str]]] = {}
    labels: Dict[str, str] = {}
    command: Optional[List[str]] = None
    entrypoint: Optional[List[str]] = None
    env: List[str] = []
    volumes: Dict[str, Dict[str, Any]] = {}
    network_mode: str = "default"
    restart_policy: RestartPolicy = RestartPolicy(name="no")
    mounts: List[Mount] = []


class Image(BaseModel):
    """Image-Modell."""
    
    id: str
    tags: List[str] = []
    created: datetime
    size: int
    labels: Dict[str, str] = {}
    architecture: str = "amd64"
    os: str = "linux"
    author: str = ""
    comment: str = ""
    config: Dict[str, Any] = {}


class Network(BaseModel):
    """Netzwerk-Modell."""
    
    id: str
    name: str
    driver: str
    scope: str
    created: datetime
    labels: Dict[str, str] = {}
    containers: Dict[str, Dict[str, Any]] = {}
    options: Dict[str, str] = {}
    ipam: Dict[str, Any] = {}


class Volume(BaseModel):
    """Volume-Modell."""
    
    id: str
    name: str
    driver: str
    mountpoint: str
    created: datetime
    labels: Dict[str, str] = {}
    options: Dict[str, str] = {}
    scope: str = "local"


class ContainerList(BaseModel):
    """Container-Liste."""
    
    containers: List[Container]
    total: int


class ImageList(BaseModel):
    """Image-Liste."""
    
    images: List[Image]
    total: int


class NetworkList(BaseModel):
    """Netzwerk-Liste."""
    
    networks: List[Network]
    total: int


class VolumeList(BaseModel):
    """Volume-Liste."""
    
    volumes: List[Volume]
    total: int