"""
Workflow-Modelle für den n8n MCP Server.

Dieses Modul definiert die Datenmodelle für n8n-Workflows.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class WorkflowStatus(str, Enum):
    """Status eines Workflows."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"


class WorkflowNode(BaseModel):
    """Knoten eines Workflows."""
    
    id: str
    name: str
    type: str
    position: Dict[str, float]
    parameters: Dict[str, Any] = {}
    type_version: Optional[int] = None
    credentials: Optional[Dict[str, Any]] = None


class WorkflowConnection(BaseModel):
    """Verbindung eines Workflows."""
    
    node: str
    type: str
    index: int


class WorkflowConnections(BaseModel):
    """Verbindungen eines Workflows."""
    
    main: List[List[WorkflowConnection]] = []


class Workflow(BaseModel):
    """Workflow-Modell."""
    
    id: str
    name: str
    active: bool
    nodes: List[WorkflowNode]
    connections: Dict[str, WorkflowConnections] = {}
    settings: Dict[str, Any] = {}
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime


class WorkflowExecution(BaseModel):
    """Workflow-Ausführung."""
    
    id: str
    workflow_id: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    mode: str
    data: Dict[str, Any] = {}
    result_data: Dict[str, Any] = {}


class WorkflowList(BaseModel):
    """Workflow-Liste."""
    
    workflows: List[Workflow]
    total: int


class WorkflowExecutionList(BaseModel):
    """Workflow-Ausführungsliste."""
    
    executions: List[WorkflowExecution]
    total: int