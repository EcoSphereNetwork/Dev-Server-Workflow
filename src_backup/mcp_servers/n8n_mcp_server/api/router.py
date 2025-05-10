"""
API-Router für den n8n MCP Server.

Dieses Modul definiert den API-Router für den n8n MCP Server.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response
import time
from typing import Dict, List, Any, Optional

from ..core.n8n_client import N8nClient
from ..core.auth import AuthManager
from ..core.audit import AuditLogger
from ..core.metrics import MetricsCollector
from ..models.workflow import Workflow, WorkflowList, WorkflowExecution, WorkflowExecutionList
from ..utils.logger import logger

# Erstelle Router
router = APIRouter()

# Erstelle n8n-Client
n8n_client = N8nClient()

# Erstelle Auth-Manager
auth_manager = AuthManager()

# Erstelle Audit-Logger
audit_logger = AuditLogger()

# Erstelle Metriken-Sammler
metrics_collector = MetricsCollector()


def get_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Erhalte den Token aus dem Authorization-Header.
    
    Args:
        authorization: Der Authorization-Header
        
    Returns:
        Der Token oder None, wenn kein Token gefunden wurde
    """
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return None


def authenticate(token: Optional[str] = Depends(get_token)) -> bool:
    """
    Authentifiziere einen Token.
    
    Args:
        token: Der zu authentifizierende Token
        
    Returns:
        True, wenn der Token gültig ist, sonst False
        
    Raises:
        HTTPException: Wenn der Token ungültig ist
    """
    if not auth_manager.authenticate(token):
        raise HTTPException(status_code=401, detail="Ungültiger Token")
    return True


def authorize(permission: str, token: Optional[str] = Depends(get_token)) -> bool:
    """
    Autorisiere einen Token für eine Berechtigung.
    
    Args:
        permission: Die zu überprüfende Berechtigung
        token: Der zu autorisierende Token
        
    Returns:
        True, wenn der Token die Berechtigung hat, sonst False
        
    Raises:
        HTTPException: Wenn der Token die Berechtigung nicht hat
    """
    if not auth_manager.authorize(token, permission):
        raise HTTPException(status_code=403, detail=f"Keine Berechtigung für: {permission}")
    return True


@router.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware zur Erfassung von Metriken.
    
    Args:
        request: Die Anfrage
        call_next: Die nächste Middleware
        
    Returns:
        Die Antwort
    """
    # Erfasse die Startzeit
    start_time = time.time()
    
    # Rufe die nächste Middleware auf
    response = await call_next(request)
    
    # Erfasse die Endzeit
    end_time = time.time()
    
    # Berechne die Antwortzeit
    response_time = end_time - start_time
    
    # Erfasse die Metriken
    metrics_collector.record_request(
        method=request.method,
        success=response.status_code < 400,
        response_time=response_time,
    )
    
    return response


@router.get("/health")
async def health_check():
    """Gesundheitscheck-Endpunkt."""
    return {"status": "ok"}


@router.get("/metrics")
async def get_metrics():
    """Metriken-Endpunkt."""
    # Aktualisiere die Workflow-Metriken
    try:
        workflows = await n8n_client.list_workflows()
        active_workflows = [w for w in workflows if w.get("active", False)]
        
        metrics_collector.update_workflow_metrics(
            total=len(workflows),
            active=len(active_workflows),
        )
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Workflow-Metriken: {e}")
    
    # Erhalte die Metriken im Prometheus-Format
    prometheus_metrics = metrics_collector.get_prometheus_metrics()
    
    # Gib die Metriken zurück
    return Response(content=prometheus_metrics, media_type="text/plain")


@router.get("/workflows", response_model=WorkflowList, dependencies=[Depends(lambda: authorize("workflows:list"))])
async def list_workflows(tags: Optional[str] = None, active: Optional[bool] = None):
    """
    Liste alle Workflows auf.
    
    Args:
        tags: Filter nach Tags (kommagetrennt)
        active: Filter nach aktiven Workflows
        
    Returns:
        Liste der Workflows
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="list_workflows",
            user=None,
            details={"tags": tags, "active": active},
        )
        
        # Konvertiere Tags in eine Liste
        tags_list = tags.split(",") if tags else None
        
        # Liste die Workflows auf
        workflows = await n8n_client.list_workflows(tags=tags_list, active=active)
        
        # Konvertiere die Workflows in Workflow-Objekte
        workflow_objects = []
        for workflow in workflows:
            workflow_objects.append(Workflow(**workflow))
        
        return WorkflowList(workflows=workflow_objects, total=len(workflow_objects))
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}", response_model=Workflow, dependencies=[Depends(lambda: authorize("workflows:get"))])
async def get_workflow(workflow_id: str):
    """
    Erhalte einen Workflow.
    
    Args:
        workflow_id: ID des Workflows
        
    Returns:
        Der Workflow
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="get_workflow",
            user=None,
            details={"workflow_id": workflow_id},
        )
        
        # Erhalte den Workflow
        workflow = await n8n_client.get_workflow(workflow_id)
        
        return Workflow(**workflow)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/run", dependencies=[Depends(lambda: authorize("workflows:run"))])
async def run_workflow(workflow_id: str, parameters: Optional[Dict[str, Any]] = None):
    """
    Führe einen Workflow aus.
    
    Args:
        workflow_id: ID des Workflows
        parameters: Parameter für den Workflow
        
    Returns:
        Das Ergebnis der Workflow-Ausführung
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="run_workflow",
            user=None,
            details={"workflow_id": workflow_id, "parameters": parameters},
        )
        
        # Führe den Workflow aus
        result = await n8n_client.run_workflow(workflow_id, parameters)
        
        # Erfasse die Metriken
        metrics_collector.record_workflow_execution(success=True)
        
        return result
    except Exception as e:
        # Erfasse die Metriken
        metrics_collector.record_workflow_execution(success=False)
        
        logger.error(f"Fehler beim Ausführen des Workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows", response_model=Workflow, dependencies=[Depends(lambda: authorize("workflows:create"))])
async def create_workflow(
    name: str,
    nodes: List[Dict[str, Any]],
    connections: List[Dict[str, Any]],
    active: bool = False,
    tags: Optional[List[str]] = None,
):
    """
    Erstelle einen Workflow.
    
    Args:
        name: Name des Workflows
        nodes: Knoten des Workflows
        connections: Verbindungen des Workflows
        active: Ob der Workflow aktiv sein soll
        tags: Tags für den Workflow
        
    Returns:
        Der erstellte Workflow
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="create_workflow",
            user=None,
            details={"name": name, "active": active, "tags": tags},
        )
        
        # Erstelle den Workflow
        workflow = await n8n_client.create_workflow(name, nodes, connections, active, tags)
        
        return Workflow(**workflow)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/workflows/{workflow_id}", response_model=Workflow, dependencies=[Depends(lambda: authorize("workflows:update"))])
async def update_workflow(
    workflow_id: str,
    name: Optional[str] = None,
    nodes: Optional[List[Dict[str, Any]]] = None,
    connections: Optional[List[Dict[str, Any]]] = None,
    active: Optional[bool] = None,
    tags: Optional[List[str]] = None,
):
    """
    Aktualisiere einen Workflow.
    
    Args:
        workflow_id: ID des Workflows
        name: Neuer Name des Workflows
        nodes: Neue Knoten des Workflows
        connections: Neue Verbindungen des Workflows
        active: Ob der Workflow aktiv sein soll
        tags: Neue Tags für den Workflow
        
    Returns:
        Der aktualisierte Workflow
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="update_workflow",
            user=None,
            details={"workflow_id": workflow_id, "name": name, "active": active, "tags": tags},
        )
        
        # Aktualisiere den Workflow
        workflow = await n8n_client.update_workflow(workflow_id, name, nodes, connections, active, tags)
        
        return Workflow(**workflow)
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflows/{workflow_id}", dependencies=[Depends(lambda: authorize("workflows:delete"))])
async def delete_workflow(workflow_id: str):
    """
    Lösche einen Workflow.
    
    Args:
        workflow_id: ID des Workflows
        
    Returns:
        Erfolgsmeldung
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="delete_workflow",
            user=None,
            details={"workflow_id": workflow_id},
        )
        
        # Lösche den Workflow
        success = await n8n_client.delete_workflow(workflow_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Fehler beim Löschen des Workflows")
        
        return {"message": f"Workflow {workflow_id} gelöscht"}
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/activate", response_model=Workflow, dependencies=[Depends(lambda: authorize("workflows:activate"))])
async def activate_workflow(workflow_id: str):
    """
    Aktiviere einen Workflow.
    
    Args:
        workflow_id: ID des Workflows
        
    Returns:
        Der aktivierte Workflow
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="activate_workflow",
            user=None,
            details={"workflow_id": workflow_id},
        )
        
        # Aktiviere den Workflow
        workflow = await n8n_client.activate_workflow(workflow_id)
        
        return Workflow(**workflow)
    except Exception as e:
        logger.error(f"Fehler beim Aktivieren des Workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/deactivate", response_model=Workflow, dependencies=[Depends(lambda: authorize("workflows:deactivate"))])
async def deactivate_workflow(workflow_id: str):
    """
    Deaktiviere einen Workflow.
    
    Args:
        workflow_id: ID des Workflows
        
    Returns:
        Der deaktivierte Workflow
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="deactivate_workflow",
            user=None,
            details={"workflow_id": workflow_id},
        )
        
        # Deaktiviere den Workflow
        workflow = await n8n_client.deactivate_workflow(workflow_id)
        
        return Workflow(**workflow)
    except Exception as e:
        logger.error(f"Fehler beim Deaktivieren des Workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))