"""
MCP-Server-Installer-Modul.

Dieses Modul bietet Funktionen zum Installieren, Starten und Stoppen von MCP-Servern.
"""

import os
import json
import logging
import subprocess
import asyncio
import shutil
import tempfile
import aiohttp
import docker
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime

from ..models.server import ServerConfig, ServerInfo, ServerStatus, ServerType, ServerProtocol
from ..utils.logger import logger
from ..core.config import settings


class InstallerManager:
    """MCP-Server-Installer-Manager-Klasse."""
    
    def __init__(self):
        """Initialisiere den Installer-Manager."""
        self.docker_client = None
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren des Docker-Clients: {e}")
    
    async def install_server(self, server: ServerConfig) -> bool:
        """
        Installiere einen MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich installiert wurde, sonst False
        """
        if server.type == ServerType.DOCKER:
            return await self._install_docker_server(server)
        elif server.type == ServerType.N8N:
            return await self._install_n8n_server(server)
        elif server.type == ServerType.OPENHANDS:
            return await self._install_openhands_server(server)
        elif server.type == ServerType.GENERATOR:
            return await self._install_generator_server(server)
        elif server.type == ServerType.LLM_COST_ANALYZER:
            return await self._install_llm_cost_analyzer_server(server)
        elif server.type == ServerType.PROMPT:
            return await self._install_prompt_server(server)
        else:
            logger.error(f"Nicht unterstützter Servertyp: {server.type}")
            return False
    
    async def _install_docker_server(self, server: ServerConfig) -> bool:
        """
        Installiere einen Docker-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich installiert wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle das Konfigurationsverzeichnis
            config_dir = settings.MCP_SERVER_CONFIG_DIR / server.name
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Erstelle die Konfigurationsdatei
            config_file = config_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(server.dict(), f, indent=2, default=str)
            
            # Ziehe das Docker-Image
            image_name = server.metadata.get("image_name", "ecosphere/docker-mcp-server:latest")
            logger.info(f"Ziehe Docker-Image: {image_name}")
            self.docker_client.images.pull(image_name)
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Installieren des Docker-MCP-Servers: {e}")
            return False
    
    async def _install_n8n_server(self, server: ServerConfig) -> bool:
        """
        Installiere einen n8n-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich installiert wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle das Konfigurationsverzeichnis
            config_dir = settings.MCP_SERVER_CONFIG_DIR / server.name
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Erstelle die Konfigurationsdatei
            config_file = config_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(server.dict(), f, indent=2, default=str)
            
            # Ziehe das Docker-Image
            image_name = server.metadata.get("image_name", "ecosphere/n8n-mcp-server:latest")
            logger.info(f"Ziehe Docker-Image: {image_name}")
            self.docker_client.images.pull(image_name)
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Installieren des n8n-MCP-Servers: {e}")
            return False
    
    async def _install_openhands_server(self, server: ServerConfig) -> bool:
        """
        Installiere einen OpenHands-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich installiert wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle das Konfigurationsverzeichnis
            config_dir = settings.MCP_SERVER_CONFIG_DIR / server.name
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Erstelle die Konfigurationsdatei
            config_file = config_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(server.dict(), f, indent=2, default=str)
            
            # Ziehe das Docker-Image
            image_name = server.metadata.get("image_name", "ecosphere/openhands-mcp-server:latest")
            logger.info(f"Ziehe Docker-Image: {image_name}")
            self.docker_client.images.pull(image_name)
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Installieren des OpenHands-MCP-Servers: {e}")
            return False
    
    async def _install_generator_server(self, server: ServerConfig) -> bool:
        """
        Installiere einen Generator-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich installiert wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle das Konfigurationsverzeichnis
            config_dir = settings.MCP_SERVER_CONFIG_DIR / server.name
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Erstelle die Konfigurationsdatei
            config_file = config_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(server.dict(), f, indent=2, default=str)
            
            # Ziehe das Docker-Image
            image_name = server.metadata.get("image_name", "ecosphere/generator-mcp-server:latest")
            logger.info(f"Ziehe Docker-Image: {image_name}")
            self.docker_client.images.pull(image_name)
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Installieren des Generator-MCP-Servers: {e}")
            return False
    
    async def _install_llm_cost_analyzer_server(self, server: ServerConfig) -> bool:
        """
        Installiere einen LLM-Cost-Analyzer-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich installiert wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle das Konfigurationsverzeichnis
            config_dir = settings.MCP_SERVER_CONFIG_DIR / server.name
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Erstelle die Konfigurationsdatei
            config_file = config_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(server.dict(), f, indent=2, default=str)
            
            # Ziehe das Docker-Image
            image_name = server.metadata.get("image_name", "ecosphere/llm-cost-analyzer-mcp-server:latest")
            logger.info(f"Ziehe Docker-Image: {image_name}")
            self.docker_client.images.pull(image_name)
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Installieren des LLM-Cost-Analyzer-MCP-Servers: {e}")
            return False
    
    async def _install_prompt_server(self, server: ServerConfig) -> bool:
        """
        Installiere einen Prompt-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich installiert wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle das Konfigurationsverzeichnis
            config_dir = settings.MCP_SERVER_CONFIG_DIR / server.name
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Erstelle die Konfigurationsdatei
            config_file = config_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(server.dict(), f, indent=2, default=str)
            
            # Ziehe das Docker-Image
            image_name = server.metadata.get("image_name", "ecosphere/prompt-mcp-server:latest")
            logger.info(f"Ziehe Docker-Image: {image_name}")
            self.docker_client.images.pull(image_name)
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Installieren des Prompt-MCP-Servers: {e}")
            return False
    
    async def uninstall_server(self, server: ServerConfig) -> bool:
        """
        Deinstalliere einen MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich deinstalliert wurde, sonst False
        """
        try:
            # Stoppe den Server
            await self.stop_server(server)
            
            # Entferne das Konfigurationsverzeichnis
            config_dir = settings.MCP_SERVER_CONFIG_DIR / server.name
            if config_dir.exists():
                shutil.rmtree(config_dir)
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Deinstallieren des Servers: {e}")
            return False
    
    async def start_server(self, server: ServerConfig) -> bool:
        """
        Starte einen MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich gestartet wurde, sonst False
        """
        if server.type == ServerType.DOCKER:
            return await self._start_docker_server(server)
        elif server.type == ServerType.N8N:
            return await self._start_n8n_server(server)
        elif server.type == ServerType.OPENHANDS:
            return await self._start_openhands_server(server)
        elif server.type == ServerType.GENERATOR:
            return await self._start_generator_server(server)
        elif server.type == ServerType.LLM_COST_ANALYZER:
            return await self._start_llm_cost_analyzer_server(server)
        elif server.type == ServerType.PROMPT:
            return await self._start_prompt_server(server)
        else:
            logger.error(f"Nicht unterstützter Servertyp: {server.type}")
            return False
    
    async def _start_docker_server(self, server: ServerConfig) -> bool:
        """
        Starte einen Docker-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich gestartet wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle die Container-Konfiguration
            container_name = f"mcp-{server.name}"
            image_name = server.metadata.get("image_name", "ecosphere/docker-mcp-server:latest")
            port = server.metadata.get("port", 3458)
            
            # Überprüfe, ob der Container bereits existiert
            try:
                container = self.docker_client.containers.get(container_name)
                
                # Überprüfe, ob der Container bereits läuft
                if container.status == "running":
                    logger.info(f"Container {container_name} läuft bereits")
                    return True
                
                # Starte den Container
                container.start()
                logger.info(f"Container {container_name} gestartet")
                return True
            except docker.errors.NotFound:
                # Container existiert nicht, erstelle ihn
                container = self.docker_client.containers.run(
                    image=image_name,
                    name=container_name,
                    ports={f"{port}/tcp": port},
                    detach=True,
                    restart_policy={"Name": "always"},
                    environment={
                        "MCP_SERVER_NAME": server.name,
                        "MCP_SERVER_DESCRIPTION": server.description,
                        "MCP_SERVER_PORT": str(port),
                    },
                )
                logger.info(f"Container {container_name} erstellt und gestartet")
                return True
        except Exception as e:
            logger.error(f"Fehler beim Starten des Docker-MCP-Servers: {e}")
            return False
    
    async def _start_n8n_server(self, server: ServerConfig) -> bool:
        """
        Starte einen n8n-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich gestartet wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle die Container-Konfiguration
            container_name = f"mcp-{server.name}"
            image_name = server.metadata.get("image_name", "ecosphere/n8n-mcp-server:latest")
            port = server.metadata.get("port", 3456)
            n8n_url = server.metadata.get("n8n_url", "http://localhost:5678")
            n8n_api_key = server.metadata.get("n8n_api_key", "")
            
            # Überprüfe, ob der Container bereits existiert
            try:
                container = self.docker_client.containers.get(container_name)
                
                # Überprüfe, ob der Container bereits läuft
                if container.status == "running":
                    logger.info(f"Container {container_name} läuft bereits")
                    return True
                
                # Starte den Container
                container.start()
                logger.info(f"Container {container_name} gestartet")
                return True
            except docker.errors.NotFound:
                # Container existiert nicht, erstelle ihn
                container = self.docker_client.containers.run(
                    image=image_name,
                    name=container_name,
                    ports={f"{port}/tcp": port},
                    detach=True,
                    restart_policy={"Name": "always"},
                    environment={
                        "MCP_SERVER_NAME": server.name,
                        "MCP_SERVER_DESCRIPTION": server.description,
                        "MCP_SERVER_PORT": str(port),
                        "N8N_URL": n8n_url,
                        "N8N_API_KEY": n8n_api_key,
                    },
                )
                logger.info(f"Container {container_name} erstellt und gestartet")
                return True
        except Exception as e:
            logger.error(f"Fehler beim Starten des n8n-MCP-Servers: {e}")
            return False
    
    async def _start_openhands_server(self, server: ServerConfig) -> bool:
        """
        Starte einen OpenHands-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich gestartet wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle die Container-Konfiguration
            container_name = f"mcp-{server.name}"
            image_name = server.metadata.get("image_name", "ecosphere/openhands-mcp-server:latest")
            port = server.metadata.get("port", 3457)
            openhands_url = server.metadata.get("openhands_url", "http://localhost:3000")
            openhands_api_key = server.metadata.get("openhands_api_key", "")
            
            # Überprüfe, ob der Container bereits existiert
            try:
                container = self.docker_client.containers.get(container_name)
                
                # Überprüfe, ob der Container bereits läuft
                if container.status == "running":
                    logger.info(f"Container {container_name} läuft bereits")
                    return True
                
                # Starte den Container
                container.start()
                logger.info(f"Container {container_name} gestartet")
                return True
            except docker.errors.NotFound:
                # Container existiert nicht, erstelle ihn
                container = self.docker_client.containers.run(
                    image=image_name,
                    name=container_name,
                    ports={f"{port}/tcp": port},
                    detach=True,
                    restart_policy={"Name": "always"},
                    environment={
                        "MCP_SERVER_NAME": server.name,
                        "MCP_SERVER_DESCRIPTION": server.description,
                        "MCP_SERVER_PORT": str(port),
                        "OPENHANDS_URL": openhands_url,
                        "OPENHANDS_API_KEY": openhands_api_key,
                    },
                )
                logger.info(f"Container {container_name} erstellt und gestartet")
                return True
        except Exception as e:
            logger.error(f"Fehler beim Starten des OpenHands-MCP-Servers: {e}")
            return False
    
    async def _start_generator_server(self, server: ServerConfig) -> bool:
        """
        Starte einen Generator-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich gestartet wurde, sonst False
        """
        # Implementiere die Logik zum Starten eines Generator-MCP-Servers
        # Hier könnte eine komplexere Logik implementiert werden
        
        return False
    
    async def _start_llm_cost_analyzer_server(self, server: ServerConfig) -> bool:
        """
        Starte einen LLM-Cost-Analyzer-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich gestartet wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle die Container-Konfiguration
            container_name = f"mcp-{server.name}"
            image_name = server.metadata.get("image_name", "ecosphere/llm-cost-analyzer-mcp-server:latest")
            port = server.metadata.get("port", 3459)
            
            # Überprüfe, ob der Container bereits existiert
            try:
                container = self.docker_client.containers.get(container_name)
                
                # Überprüfe, ob der Container bereits läuft
                if container.status == "running":
                    logger.info(f"Container {container_name} läuft bereits")
                    return True
                
                # Starte den Container
                container.start()
                logger.info(f"Container {container_name} gestartet")
                return True
            except docker.errors.NotFound:
                # Container existiert nicht, erstelle ihn
                container = self.docker_client.containers.run(
                    image=image_name,
                    name=container_name,
                    ports={f"{port}/tcp": port},
                    detach=True,
                    restart_policy={"Name": "always"},
                    environment={
                        "MCP_SERVER_NAME": server.name,
                        "MCP_SERVER_DESCRIPTION": server.description,
                        "MCP_SERVER_PORT": str(port),
                    },
                )
                logger.info(f"Container {container_name} erstellt und gestartet")
                return True
        except Exception as e:
            logger.error(f"Fehler beim Starten des LLM-Cost-Analyzer-MCP-Servers: {e}")
            return False
    
    async def _start_prompt_server(self, server: ServerConfig) -> bool:
        """
        Starte einen Prompt-MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich gestartet wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle die Container-Konfiguration
            container_name = f"mcp-{server.name}"
            image_name = server.metadata.get("image_name", "ecosphere/prompt-mcp-server:latest")
            port = server.metadata.get("port", 3460)
            
            # Überprüfe, ob der Container bereits existiert
            try:
                container = self.docker_client.containers.get(container_name)
                
                # Überprüfe, ob der Container bereits läuft
                if container.status == "running":
                    logger.info(f"Container {container_name} läuft bereits")
                    return True
                
                # Starte den Container
                container.start()
                logger.info(f"Container {container_name} gestartet")
                return True
            except docker.errors.NotFound:
                # Container existiert nicht, erstelle ihn
                container = self.docker_client.containers.run(
                    image=image_name,
                    name=container_name,
                    ports={f"{port}/tcp": port},
                    detach=True,
                    restart_policy={"Name": "always"},
                    environment={
                        "MCP_SERVER_NAME": server.name,
                        "MCP_SERVER_DESCRIPTION": server.description,
                        "MCP_SERVER_PORT": str(port),
                    },
                )
                logger.info(f"Container {container_name} erstellt und gestartet")
                return True
        except Exception as e:
            logger.error(f"Fehler beim Starten des Prompt-MCP-Servers: {e}")
            return False
    
    async def stop_server(self, server: ServerConfig) -> bool:
        """
        Stoppe einen MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich gestoppt wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Erstelle den Container-Namen
            container_name = f"mcp-{server.name}"
            
            # Überprüfe, ob der Container existiert
            try:
                container = self.docker_client.containers.get(container_name)
                
                # Überprüfe, ob der Container läuft
                if container.status != "running":
                    logger.info(f"Container {container_name} läuft nicht")
                    return True
                
                # Stoppe den Container
                container.stop()
                logger.info(f"Container {container_name} gestoppt")
                return True
            except docker.errors.NotFound:
                # Container existiert nicht
                logger.info(f"Container {container_name} existiert nicht")
                return True
        except Exception as e:
            logger.error(f"Fehler beim Stoppen des Servers: {e}")
            return False
    
    async def update_server(self, server: ServerConfig) -> bool:
        """
        Aktualisiere einen MCP-Server.
        
        Args:
            server: Die Serverkonfiguration
            
        Returns:
            True, wenn der Server erfolgreich aktualisiert wurde, sonst False
        """
        try:
            if not self.docker_client:
                logger.error("Docker-Client nicht initialisiert")
                return False
            
            # Stoppe den Server
            if not await self.stop_server(server):
                logger.error(f"Fehler beim Stoppen des Servers: {server.name}")
                return False
            
            # Ziehe das Docker-Image
            image_name = server.metadata.get("image_name", f"ecosphere/{server.type}-mcp-server:latest")
            logger.info(f"Ziehe Docker-Image: {image_name}")
            self.docker_client.images.pull(image_name)
            
            # Starte den Server
            if not await self.start_server(server):
                logger.error(f"Fehler beim Starten des Servers: {server.name}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Servers: {e}")
            return False