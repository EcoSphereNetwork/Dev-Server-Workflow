"""
API-Router für den Docker MCP Server.

Dieses Modul definiert den API-Router für den Docker MCP Server.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response
from fastapi.responses import JSONResponse
import time
from typing import Dict, List, Any, Optional

from ..core.docker_executor import DockerExecutor
from ..core.auth import AuthManager
from ..core.audit import AuditLogger
from ..core.metrics import MetricsCollector
from ..models.docker import Container, Image, Network, Volume, ContainerList, ImageList, NetworkList, VolumeList
from ..utils.logger import logger

# Erstelle Router
router = APIRouter()

# Erstelle Docker-Executor
docker_executor = DockerExecutor()

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
    # Aktualisiere die Docker-Metriken
    try:
        containers = docker_executor.list_containers(all=True)
        containers_running = len([c for c in containers if c["status"] == "running"])
        images = docker_executor.list_images()
        networks = docker_executor.list_networks()
        volumes = docker_executor.list_volumes()
        
        metrics_collector.update_docker_metrics(
            containers_total=len(containers),
            containers_running=containers_running,
            images_total=len(images),
            networks_total=len(networks),
            volumes_total=len(volumes),
        )
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Docker-Metriken: {e}")
    
    # Erhalte die Metriken im Prometheus-Format
    prometheus_metrics = metrics_collector.get_prometheus_metrics()
    
    # Gib die Metriken zurück
    return Response(content=prometheus_metrics, media_type="text/plain")


@router.get("/containers", response_model=ContainerList, dependencies=[Depends(lambda: authorize("containers:list"))])
async def list_containers(all: bool = False):
    """
    Liste alle Container auf.
    
    Args:
        all: Ob alle Container aufgelistet werden sollen
        
    Returns:
        Liste der Container
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="list_containers",
            user=None,
            details={"all": all},
        )
        
        # Liste die Container auf
        containers = docker_executor.list_containers(all=all)
        
        # Konvertiere die Container in Container-Objekte
        container_objects = []
        for container in containers:
            container_objects.append(Container(**container))
        
        return ContainerList(containers=container_objects, total=len(container_objects))
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Container: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/containers/{container_id}", response_model=Container, dependencies=[Depends(lambda: authorize("containers:get"))])
async def get_container(container_id: str):
    """
    Erhalte einen Container.
    
    Args:
        container_id: ID oder Name des Containers
        
    Returns:
        Der Container
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="get_container",
            user=None,
            details={"container_id": container_id},
        )
        
        # Erhalte den Container
        container = docker_executor.get_container(container_id)
        
        return Container(**container)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Containers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/containers/{container_id}/start", dependencies=[Depends(lambda: authorize("containers:start"))])
async def start_container(container_id: str):
    """
    Starte einen Container.
    
    Args:
        container_id: ID oder Name des Containers
        
    Returns:
        Erfolgsmeldung
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="start_container",
            user=None,
            details={"container_id": container_id},
        )
        
        # Starte den Container
        success = docker_executor.start_container(container_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Fehler beim Starten des Containers")
        
        return {"message": f"Container {container_id} gestartet"}
    except Exception as e:
        logger.error(f"Fehler beim Starten des Containers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/containers/{container_id}/stop", dependencies=[Depends(lambda: authorize("containers:stop"))])
async def stop_container(container_id: str):
    """
    Stoppe einen Container.
    
    Args:
        container_id: ID oder Name des Containers
        
    Returns:
        Erfolgsmeldung
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="stop_container",
            user=None,
            details={"container_id": container_id},
        )
        
        # Stoppe den Container
        success = docker_executor.stop_container(container_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Fehler beim Stoppen des Containers")
        
        return {"message": f"Container {container_id} gestoppt"}
    except Exception as e:
        logger.error(f"Fehler beim Stoppen des Containers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/containers/{container_id}/restart", dependencies=[Depends(lambda: authorize("containers:restart"))])
async def restart_container(container_id: str):
    """
    Starte einen Container neu.
    
    Args:
        container_id: ID oder Name des Containers
        
    Returns:
        Erfolgsmeldung
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="restart_container",
            user=None,
            details={"container_id": container_id},
        )
        
        # Starte den Container neu
        success = docker_executor.restart_container(container_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Fehler beim Neustarten des Containers")
        
        return {"message": f"Container {container_id} neu gestartet"}
    except Exception as e:
        logger.error(f"Fehler beim Neustarten des Containers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/containers/{container_id}", dependencies=[Depends(lambda: authorize("containers:remove"))])
async def remove_container(container_id: str, force: bool = False):
    """
    Entferne einen Container.
    
    Args:
        container_id: ID oder Name des Containers
        force: Ob der Container gewaltsam entfernt werden soll
        
    Returns:
        Erfolgsmeldung
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="remove_container",
            user=None,
            details={"container_id": container_id, "force": force},
        )
        
        # Entferne den Container
        success = docker_executor.remove_container(container_id, force=force)
        
        if not success:
            raise HTTPException(status_code=500, detail="Fehler beim Entfernen des Containers")
        
        return {"message": f"Container {container_id} entfernt"}
    except Exception as e:
        logger.error(f"Fehler beim Entfernen des Containers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images", response_model=ImageList, dependencies=[Depends(lambda: authorize("images:list"))])
async def list_images():
    """
    Liste alle Images auf.
    
    Returns:
        Liste der Images
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="list_images",
            user=None,
            details={},
        )
        
        # Liste die Images auf
        images = docker_executor.list_images()
        
        # Konvertiere die Images in Image-Objekte
        image_objects = []
        for image in images:
            image_objects.append(Image(**image))
        
        return ImageList(images=image_objects, total=len(image_objects))
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{image_id}", response_model=Image, dependencies=[Depends(lambda: authorize("images:get"))])
async def get_image(image_id: str):
    """
    Erhalte ein Image.
    
    Args:
        image_id: ID oder Name des Images
        
    Returns:
        Das Image
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="get_image",
            user=None,
            details={"image_id": image_id},
        )
        
        # Erhalte das Image
        image = docker_executor.get_image(image_id)
        
        return Image(**image)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/images/{image_name}/pull", dependencies=[Depends(lambda: authorize("images:pull"))])
async def pull_image(image_name: str):
    """
    Ziehe ein Image.
    
    Args:
        image_name: Name des Images
        
    Returns:
        Erfolgsmeldung
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="pull_image",
            user=None,
            details={"image_name": image_name},
        )
        
        # Ziehe das Image
        success = docker_executor.pull_image(image_name)
        
        if not success:
            raise HTTPException(status_code=500, detail="Fehler beim Ziehen des Images")
        
        return {"message": f"Image {image_name} gezogen"}
    except Exception as e:
        logger.error(f"Fehler beim Ziehen des Images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/images/{image_id}", dependencies=[Depends(lambda: authorize("images:remove"))])
async def remove_image(image_id: str, force: bool = False):
    """
    Entferne ein Image.
    
    Args:
        image_id: ID oder Name des Images
        force: Ob das Image gewaltsam entfernt werden soll
        
    Returns:
        Erfolgsmeldung
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="remove_image",
            user=None,
            details={"image_id": image_id, "force": force},
        )
        
        # Entferne das Image
        success = docker_executor.remove_image(image_id, force=force)
        
        if not success:
            raise HTTPException(status_code=500, detail="Fehler beim Entfernen des Images")
        
        return {"message": f"Image {image_id} entfernt"}
    except Exception as e:
        logger.error(f"Fehler beim Entfernen des Images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/networks", response_model=NetworkList, dependencies=[Depends(lambda: authorize("networks:list"))])
async def list_networks():
    """
    Liste alle Netzwerke auf.
    
    Returns:
        Liste der Netzwerke
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="list_networks",
            user=None,
            details={},
        )
        
        # Liste die Netzwerke auf
        networks = docker_executor.list_networks()
        
        # Konvertiere die Netzwerke in Network-Objekte
        network_objects = []
        for network in networks:
            network_objects.append(Network(**network))
        
        return NetworkList(networks=network_objects, total=len(network_objects))
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Netzwerke: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/networks/{network_id}", response_model=Network, dependencies=[Depends(lambda: authorize("networks:get"))])
async def get_network(network_id: str):
    """
    Erhalte ein Netzwerk.
    
    Args:
        network_id: ID oder Name des Netzwerks
        
    Returns:
        Das Netzwerk
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="get_network",
            user=None,
            details={"network_id": network_id},
        )
        
        # Erhalte das Netzwerk
        network = docker_executor.get_network(network_id)
        
        return Network(**network)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Netzwerks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/volumes", response_model=VolumeList, dependencies=[Depends(lambda: authorize("volumes:list"))])
async def list_volumes():
    """
    Liste alle Volumes auf.
    
    Returns:
        Liste der Volumes
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="list_volumes",
            user=None,
            details={},
        )
        
        # Liste die Volumes auf
        volumes = docker_executor.list_volumes()
        
        # Konvertiere die Volumes in Volume-Objekte
        volume_objects = []
        for volume in volumes:
            volume_objects.append(Volume(**volume))
        
        return VolumeList(volumes=volume_objects, total=len(volume_objects))
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Volumes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/volumes/{volume_id}", response_model=Volume, dependencies=[Depends(lambda: authorize("volumes:get"))])
async def get_volume(volume_id: str):
    """
    Erhalte ein Volume.
    
    Args:
        volume_id: ID oder Name des Volumes
        
    Returns:
        Das Volume
    """
    try:
        # Protokolliere das Audit-Ereignis
        audit_logger.log(
            event="get_volume",
            user=None,
            details={"volume_id": volume_id},
        )
        
        # Erhalte das Volume
        volume = docker_executor.get_volume(volume_id)
        
        return Volume(**volume)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Volumes: {e}")
        raise HTTPException(status_code=500, detail=str(e))