"""
MCP-Server-Registry-Modul.

Dieses Modul bietet Funktionen zum Verwalten der Registry von MCP-Servern.
"""

import os
import re
import json
import logging
import tempfile
import subprocess
import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from ..models.server import ServerRegistry, ServerConfig, ServerInfo, ServerStatus, ServerType, ServerProtocol
from ..utils.logger import logger
from ..core.config import settings


class RegistryManager:
    """MCP-Server-Registry-Manager-Klasse."""
    
    def __init__(self, registry_file: Optional[Path] = None):
        """
        Initialisiere den Registry-Manager.
        
        Args:
            registry_file: Pfad zur Registry-Datei
        """
        self.registry_file = registry_file or settings.MCP_SERVER_REGISTRY_FILE
        self.registry = self._load_registry()
    
    def _load_registry(self) -> ServerRegistry:
        """
        Lade die Registry aus der Registry-Datei.
        
        Returns:
            Die geladene Registry
        """
        try:
            if self.registry_file.exists():
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                
                # Konvertiere das Dictionary in ein ServerRegistry-Objekt
                return ServerRegistry.parse_obj(data)
            else:
                # Erstelle eine neue Registry
                registry = ServerRegistry(
                    repositories=settings.DEFAULT_REPOSITORIES,
                    docker_hub_users=settings.DEFAULT_DOCKER_HUB_USERS,
                    last_updated=datetime.now(),
                )
                
                # Speichere die Registry
                self._save_registry(registry)
                
                return registry
        except Exception as e:
            logger.error(f"Fehler beim Laden der Registry: {e}")
            
            # Erstelle eine neue Registry
            registry = ServerRegistry(
                repositories=settings.DEFAULT_REPOSITORIES,
                docker_hub_users=settings.DEFAULT_DOCKER_HUB_USERS,
                last_updated=datetime.now(),
            )
            
            # Speichere die Registry
            self._save_registry(registry)
            
            return registry
    
    def _save_registry(self, registry: Optional[ServerRegistry] = None) -> None:
        """
        Speichere die Registry in der Registry-Datei.
        
        Args:
            registry: Die zu speichernde Registry
        """
        try:
            registry = registry or self.registry
            
            # Stelle sicher, dass das Verzeichnis existiert
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Speichere die Registry
            with open(self.registry_file, "w") as f:
                json.dump(registry.dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Registry: {e}")
    
    def add_repository(self, repo_url: str) -> None:
        """
        Füge ein Repository zur Registry hinzu.
        
        Args:
            repo_url: Die URL des Repositories
        """
        if repo_url not in self.registry.repositories:
            self.registry.repositories.append(repo_url)
            self.registry.last_updated = datetime.now()
            self._save_registry()
    
    def remove_repository(self, repo_url: str) -> None:
        """
        Entferne ein Repository aus der Registry.
        
        Args:
            repo_url: Die URL des Repositories
        """
        if repo_url in self.registry.repositories:
            self.registry.repositories.remove(repo_url)
            self.registry.last_updated = datetime.now()
            self._save_registry()
    
    def add_docker_hub_user(self, username: str) -> None:
        """
        Füge einen Docker Hub-Benutzer zur Registry hinzu.
        
        Args:
            username: Der Benutzername
        """
        if username not in self.registry.docker_hub_users:
            self.registry.docker_hub_users.append(username)
            self.registry.last_updated = datetime.now()
            self._save_registry()
    
    def remove_docker_hub_user(self, username: str) -> None:
        """
        Entferne einen Docker Hub-Benutzer aus der Registry.
        
        Args:
            username: Der Benutzername
        """
        if username in self.registry.docker_hub_users:
            self.registry.docker_hub_users.remove(username)
            self.registry.last_updated = datetime.now()
            self._save_registry()
    
    def add_server(self, server: ServerConfig) -> None:
        """
        Füge einen MCP-Server zur Registry hinzu.
        
        Args:
            server: Die Serverkonfiguration
        """
        self.registry.servers[server.name] = server
        self.registry.last_updated = datetime.now()
        self._save_registry()
    
    def remove_server(self, server_name: str) -> None:
        """
        Entferne einen MCP-Server aus der Registry.
        
        Args:
            server_name: Der Name des Servers
        """
        if server_name in self.registry.servers:
            del self.registry.servers[server_name]
            self.registry.last_updated = datetime.now()
            self._save_registry()
    
    def get_server(self, server_name: str) -> Optional[ServerConfig]:
        """
        Erhalte einen MCP-Server aus der Registry.
        
        Args:
            server_name: Der Name des Servers
            
        Returns:
            Die Serverkonfiguration oder None, wenn der Server nicht gefunden wurde
        """
        return self.registry.servers.get(server_name)
    
    def list_servers(self) -> List[ServerConfig]:
        """
        Liste alle MCP-Server in der Registry auf.
        
        Returns:
            Liste aller Serverkonfigurationen
        """
        return list(self.registry.servers.values())
    
    async def discover_servers(self) -> List[ServerInfo]:
        """
        Entdecke MCP-Server im Netzwerk.
        
        Returns:
            Liste der entdeckten Server
        """
        # Implementiere die Logik zur Entdeckung von MCP-Servern
        # Hier könnte eine komplexere Logik implementiert werden
        
        discovered_servers = []
        
        # Entdecke Server über HTTP
        discovered_servers.extend(await self._discover_http_servers())
        
        # Entdecke Server über Docker
        discovered_servers.extend(await self._discover_docker_servers())
        
        return discovered_servers
    
    async def _discover_http_servers(self) -> List[ServerInfo]:
        """
        Entdecke MCP-Server über HTTP.
        
        Returns:
            Liste der entdeckten Server
        """
        discovered_servers = []
        
        # Definiere die zu scannenden Ports
        ports = [3456, 3457, 3458, 3459, 3460, 8000, 8080]
        
        # Definiere die zu scannenden Hosts
        hosts = ["localhost", "127.0.0.1"]
        
        # Scanne die Hosts und Ports
        async with aiohttp.ClientSession() as session:
            for host in hosts:
                for port in ports:
                    url = f"http://{host}:{port}/health"
                    try:
                        async with session.get(url, timeout=1) as response:
                            if response.status == 200:
                                # Versuche, die Serverinformationen zu erhalten
                                try:
                                    data = await response.json()
                                    
                                    # Erstelle ein ServerInfo-Objekt
                                    server_info = ServerInfo(
                                        name=data.get("name", f"mcp-server-{host}-{port}"),
                                        description=data.get("description", "Entdeckter MCP-Server"),
                                        version=data.get("version", "0.1.0"),
                                        type=ServerType(data.get("type", "custom")),
                                        protocol=ServerProtocol.HTTP,
                                        url=f"http://{host}:{port}",
                                        status=ServerStatus.ONLINE,
                                        last_seen=datetime.now(),
                                    )
                                    
                                    discovered_servers.append(server_info)
                                except Exception as e:
                                    logger.error(f"Fehler beim Parsen der Serverinformationen: {e}")
                    except Exception as e:
                        # Ignoriere Fehler beim Scannen
                        pass
        
        return discovered_servers
    
    async def _discover_docker_servers(self) -> List[ServerInfo]:
        """
        Entdecke MCP-Server über Docker.
        
        Returns:
            Liste der entdeckten Server
        """
        discovered_servers = []
        
        # Implementiere die Logik zur Entdeckung von MCP-Servern über Docker
        # Hier könnte eine komplexere Logik implementiert werden
        
        return discovered_servers
    
    async def check_server_status(self, server: ServerConfig) -> ServerStatus:
        """
        Überprüfe den Status eines MCP-Servers.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            Der Status des Servers
        """
        if server.protocol == ServerProtocol.HTTP:
            return await self._check_http_server_status(server)
        elif server.protocol == ServerProtocol.WEBSOCKET:
            return await self._check_websocket_server_status(server)
        else:
            return ServerStatus.UNKNOWN
    
    async def _check_http_server_status(self, server: ServerConfig) -> ServerStatus:
        """
        Überprüfe den Status eines HTTP-MCP-Servers.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            Der Status des Servers
        """
        if not server.url:
            return ServerStatus.UNKNOWN
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{server.url}/health", timeout=5) as response:
                    if response.status == 200:
                        return ServerStatus.ONLINE
                    else:
                        return ServerStatus.ERROR
        except Exception as e:
            logger.error(f"Fehler beim Überprüfen des Serverstatus: {e}")
            return ServerStatus.OFFLINE
    
    async def _check_websocket_server_status(self, server: ServerConfig) -> ServerStatus:
        """
        Überprüfe den Status eines WebSocket-MCP-Servers.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            Der Status des Servers
        """
        if not server.url:
            return ServerStatus.UNKNOWN
        
        try:
            # Konvertiere HTTP-URL zu WebSocket-URL
            ws_url = server.url.replace("http://", "ws://").replace("https://", "wss://")
            
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(f"{ws_url}/ws", timeout=5) as ws:
                    return ServerStatus.ONLINE
        except Exception as e:
            logger.error(f"Fehler beim Überprüfen des Serverstatus: {e}")
            return ServerStatus.OFFLINE
    
    async def get_server_info(self, server: ServerConfig) -> Optional[ServerInfo]:
        """
        Erhalte Informationen über einen MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            Die Serverinformationen oder None, wenn der Server nicht erreichbar ist
        """
        if server.protocol == ServerProtocol.HTTP:
            return await self._get_http_server_info(server)
        elif server.protocol == ServerProtocol.WEBSOCKET:
            return await self._get_websocket_server_info(server)
        else:
            return None
    
    async def _get_http_server_info(self, server: ServerConfig) -> Optional[ServerInfo]:
        """
        Erhalte Informationen über einen HTTP-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            Die Serverinformationen oder None, wenn der Server nicht erreichbar ist
        """
        if not server.url:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                # Versuche, die Serverinformationen über den Health-Endpunkt zu erhalten
                async with session.get(f"{server.url}/health", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Erstelle ein ServerInfo-Objekt
                        server_info = ServerInfo(
                            name=data.get("name", server.name),
                            description=data.get("description", server.description),
                            version=data.get("version", "0.1.0"),
                            type=server.type,
                            protocol=server.protocol,
                            url=server.url,
                            status=ServerStatus.ONLINE,
                            last_seen=datetime.now(),
                            metadata=data,
                        )
                        
                        # Versuche, die Tools über den MCP-Endpunkt zu erhalten
                        try:
                            payload = {
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": "mcp.listTools",
                                "params": {}
                            }
                            
                            headers = {}
                            if server.auth_token:
                                headers["Authorization"] = f"Bearer {server.auth_token}"
                            
                            async with session.post(f"{server.url}/mcp", json=payload, headers=headers, timeout=5) as mcp_response:
                                if mcp_response.status == 200:
                                    mcp_data = await mcp_response.json()
                                    
                                    if "result" in mcp_data:
                                        tools = mcp_data["result"]
                                        server_info.tools = tools
                        except Exception as e:
                            logger.error(f"Fehler beim Abrufen der Tools: {e}")
                        
                        return server_info
                    else:
                        return None
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Serverinformationen: {e}")
            return None
    
    async def _get_websocket_server_info(self, server: ServerConfig) -> Optional[ServerInfo]:
        """
        Erhalte Informationen über einen WebSocket-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            Die Serverinformationen oder None, wenn der Server nicht erreichbar ist
        """
        # Implementiere die Logik zum Abrufen von Informationen über einen WebSocket-MCP-Server
        # Hier könnte eine komplexere Logik implementiert werden
        
        return None