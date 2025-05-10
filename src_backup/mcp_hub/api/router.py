"""
API-Router für den MCP Hub.

Dieses Modul definiert den API-Router für den MCP Hub.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..models.server import ServerConfig, ServerInfo, ServerStatus, ServerType, ServerProtocol
from ..core.manager import HubManager

# Erstelle Router
router = APIRouter(prefix="/api", tags=["MCP Hub"])

# Erstelle Hub-Manager
hub_manager = HubManager()


@router.get("/servers", response_model=List[ServerConfig])
async def list_servers():
    """Liste alle MCP-Server auf."""
    return hub_manager.list_servers()


@router.get("/servers/{server_name}", response_model=ServerConfig)
async def get_server(server_name: str):
    """Erhalte einen MCP-Server."""
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server nicht gefunden: {server_name}",
        )
    return server


@router.post("/servers", response_model=ServerConfig)
async def create_server(server: ServerConfig):
    """Erstelle einen MCP-Server."""
    # Überprüfe, ob der Server bereits existiert
    if hub_manager.registry_manager.get_server(server.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Server existiert bereits: {server.name}",
        )
    
    # Installiere den Server
    if not await hub_manager.install_server(server):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Installieren des Servers: {server.name}",
        )
    
    return server


@router.put("/servers/{server_name}", response_model=ServerConfig)
async def update_server(server_name: str, server: ServerConfig):
    """Aktualisiere einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    if not hub_manager.registry_manager.get_server(server_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server nicht gefunden: {server_name}",
        )
    
    # Überprüfe, ob der Name geändert wurde
    if server_name != server.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Servername kann nicht geändert werden: {server_name} -> {server.name}",
        )
    
    # Aktualisiere den Server
    hub_manager.registry_manager.add_server(server)
    
    return server


@router.delete("/servers/{server_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(server_name: str):
    """Lösche einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    if not hub_manager.registry_manager.get_server(server_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server nicht gefunden: {server_name}",
        )
    
    # Deinstalliere den Server
    if not await hub_manager.uninstall_server(server_name):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Deinstallieren des Servers: {server_name}",
        )


@router.post("/servers/{server_name}/start", response_model=ServerConfig)
async def start_server(server_name: str):
    """Starte einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server nicht gefunden: {server_name}",
        )
    
    # Starte den Server
    if not await hub_manager.start_server(server_name):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Starten des Servers: {server_name}",
        )
    
    return server


@router.post("/servers/{server_name}/stop", response_model=ServerConfig)
async def stop_server(server_name: str):
    """Stoppe einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server nicht gefunden: {server_name}",
        )
    
    # Stoppe den Server
    if not await hub_manager.stop_server(server_name):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Stoppen des Servers: {server_name}",
        )
    
    return server


@router.post("/servers/{server_name}/restart", response_model=ServerConfig)
async def restart_server(server_name: str):
    """Starte einen MCP-Server neu."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server nicht gefunden: {server_name}",
        )
    
    # Starte den Server neu
    if not await hub_manager.restart_server(server_name):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Neustarten des Servers: {server_name}",
        )
    
    return server


@router.get("/servers/{server_name}/status", response_model=ServerStatus)
async def get_server_status(server_name: str):
    """Erhalte den Status eines MCP-Servers."""
    # Überprüfe, ob der Server existiert
    if not hub_manager.registry_manager.get_server(server_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server nicht gefunden: {server_name}",
        )
    
    # Erhalte den Status des Servers
    return await hub_manager.get_server_status(server_name)


@router.get("/servers/{server_name}/info", response_model=ServerInfo)
async def get_server_info(server_name: str):
    """Erhalte Informationen über einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    if not hub_manager.registry_manager.get_server(server_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server nicht gefunden: {server_name}",
        )
    
    # Erhalte Informationen über den Server
    server_info = await hub_manager.get_server_info(server_name)
    if not server_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Abrufen der Serverinformationen: {server_name}",
        )
    
    return server_info


@router.get("/discover", response_model=List[ServerInfo])
async def discover_servers():
    """Entdecke MCP-Server im Netzwerk."""
    return await hub_manager.discover_servers()


@router.get("/repositories", response_model=List[str])
async def list_repositories():
    """Liste alle Repositories auf."""
    return hub_manager.list_repositories()


@router.post("/repositories", response_model=List[str])
async def add_repository(repo_url: str):
    """Füge ein Repository hinzu."""
    hub_manager.add_repository(repo_url)
    return hub_manager.list_repositories()


@router.delete("/repositories", response_model=List[str])
async def remove_repository(repo_url: str):
    """Entferne ein Repository."""
    hub_manager.remove_repository(repo_url)
    return hub_manager.list_repositories()


@router.get("/docker-hub-users", response_model=List[str])
async def list_docker_hub_users():
    """Liste alle Docker Hub-Benutzer auf."""
    return hub_manager.list_docker_hub_users()


@router.post("/docker-hub-users", response_model=List[str])
async def add_docker_hub_user(username: str):
    """Füge einen Docker Hub-Benutzer hinzu."""
    hub_manager.add_docker_hub_user(username)
    return hub_manager.list_docker_hub_users()


@router.delete("/docker-hub-users", response_model=List[str])
async def remove_docker_hub_user(username: str):
    """Entferne einen Docker Hub-Benutzer."""
    hub_manager.remove_docker_hub_user(username)
    return hub_manager.list_docker_hub_users()