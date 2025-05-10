"""
MCP-Hub-Manager-Modul.

Dieses Modul bietet Funktionen zum Verwalten des MCP-Hubs.
"""

import os
import json
import logging
import subprocess
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime

from ..models.server import ServerConfig, ServerInfo, ServerStatus, ServerType, ServerProtocol
from ..utils.logger import logger
from ..core.config import settings
from ..core.registry import RegistryManager
from ..core.installer import InstallerManager


class HubManager:
    """MCP-Hub-Manager-Klasse."""
    
    def __init__(self):
        """Initialisiere den Hub-Manager."""
        self.registry_manager = RegistryManager()
        self.installer_manager = InstallerManager()
    
    async def start_server(self, server_name: str) -> bool:
        """
        Starte einen MCP-Server.
        
        Args:
            server_name: Der Name des Servers
            
        Returns:
            True, wenn der Server erfolgreich gestartet wurde, sonst False
        """
        server = self.registry_manager.get_server(server_name)
        if not server:
            logger.error(f"Server nicht gefunden: {server_name}")
            return False
        
        return await self.installer_manager.start_server(server)
    
    async def stop_server(self, server_name: str) -> bool:
        """
        Stoppe einen MCP-Server.
        
        Args:
            server_name: Der Name des Servers
            
        Returns:
            True, wenn der Server erfolgreich gestoppt wurde, sonst False
        """
        server = self.registry_manager.get_server(server_name)
        if not server:
            logger.error(f"Server nicht gefunden: {server_name}")
            return False
        
        return await self.installer_manager.stop_server(server)
    
    async def restart_server(self, server_name: str) -> bool:
        """
        Starte einen MCP-Server neu.
        
        Args:
            server_name: Der Name des Servers
            
        Returns:
            True, wenn der Server erfolgreich neu gestartet wurde, sonst False
        """
        server = self.registry_manager.get_server(server_name)
        if not server:
            logger.error(f"Server nicht gefunden: {server_name}")
            return False
        
        # Stoppe den Server
        if not await self.installer_manager.stop_server(server):
            logger.error(f"Fehler beim Stoppen des Servers: {server_name}")
            return False
        
        # Starte den Server
        return await self.installer_manager.start_server(server)
    
    async def install_server(self, server_config: ServerConfig) -> bool:
        """
        Installiere einen MCP-Server.
        
        Args:
            server_config: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich installiert wurde, sonst False
        """
        # Installiere den Server
        if not await self.installer_manager.install_server(server_config):
            logger.error(f"Fehler beim Installieren des Servers: {server_config.name}")
            return False
        
        # Füge den Server zur Registry hinzu
        self.registry_manager.add_server(server_config)
        
        return True
    
    async def uninstall_server(self, server_name: str) -> bool:
        """
        Deinstalliere einen MCP-Server.
        
        Args:
            server_name: Der Name des Servers
            
        Returns:
            True, wenn der Server erfolgreich deinstalliert wurde, sonst False
        """
        server = self.registry_manager.get_server(server_name)
        if not server:
            logger.error(f"Server nicht gefunden: {server_name}")
            return False
        
        # Deinstalliere den Server
        if not await self.installer_manager.uninstall_server(server):
            logger.error(f"Fehler beim Deinstallieren des Servers: {server_name}")
            return False
        
        # Entferne den Server aus der Registry
        self.registry_manager.remove_server(server_name)
        
        return True
    
    async def update_server(self, server_name: str) -> bool:
        """
        Aktualisiere einen MCP-Server.
        
        Args:
            server_name: Der Name des Servers
            
        Returns:
            True, wenn der Server erfolgreich aktualisiert wurde, sonst False
        """
        server = self.registry_manager.get_server(server_name)
        if not server:
            logger.error(f"Server nicht gefunden: {server_name}")
            return False
        
        return await self.installer_manager.update_server(server)
    
    async def get_server_status(self, server_name: str) -> ServerStatus:
        """
        Erhalte den Status eines MCP-Servers.
        
        Args:
            server_name: Der Name des Servers
            
        Returns:
            Der Status des Servers
        """
        server = self.registry_manager.get_server(server_name)
        if not server:
            logger.error(f"Server nicht gefunden: {server_name}")
            return ServerStatus.UNKNOWN
        
        return await self.registry_manager.check_server_status(server)
    
    async def get_server_info(self, server_name: str) -> Optional[ServerInfo]:
        """
        Erhalte Informationen über einen MCP-Server.
        
        Args:
            server_name: Der Name des Servers
            
        Returns:
            Die Serverinformationen oder None, wenn der Server nicht gefunden wurde
        """
        server = self.registry_manager.get_server(server_name)
        if not server:
            logger.error(f"Server nicht gefunden: {server_name}")
            return None
        
        return await self.registry_manager.get_server_info(server)
    
    async def discover_servers(self) -> List[ServerInfo]:
        """
        Entdecke MCP-Server im Netzwerk.
        
        Returns:
            Liste der entdeckten Server
        """
        return await self.registry_manager.discover_servers()
    
    def list_servers(self) -> List[ServerConfig]:
        """
        Liste alle MCP-Server in der Registry auf.
        
        Returns:
            Liste aller Serverkonfigurationen
        """
        return self.registry_manager.list_servers()
    
    def add_repository(self, repo_url: str) -> None:
        """
        Füge ein Repository zur Registry hinzu.
        
        Args:
            repo_url: Die URL des Repositories
        """
        self.registry_manager.add_repository(repo_url)
    
    def remove_repository(self, repo_url: str) -> None:
        """
        Entferne ein Repository aus der Registry.
        
        Args:
            repo_url: Die URL des Repositories
        """
        self.registry_manager.remove_repository(repo_url)
    
    def list_repositories(self) -> List[str]:
        """
        Liste alle Repositories in der Registry auf.
        
        Returns:
            Liste aller Repository-URLs
        """
        return self.registry_manager.registry.repositories
    
    def add_docker_hub_user(self, username: str) -> None:
        """
        Füge einen Docker Hub-Benutzer zur Registry hinzu.
        
        Args:
            username: Der Benutzername
        """
        self.registry_manager.add_docker_hub_user(username)
    
    def remove_docker_hub_user(self, username: str) -> None:
        """
        Entferne einen Docker Hub-Benutzer aus der Registry.
        
        Args:
            username: Der Benutzername
        """
        self.registry_manager.remove_docker_hub_user(username)
    
    def list_docker_hub_users(self) -> List[str]:
        """
        Liste alle Docker Hub-Benutzer in der Registry auf.
        
        Returns:
            Liste aller Benutzernamen
        """
        return self.registry_manager.registry.docker_hub_users