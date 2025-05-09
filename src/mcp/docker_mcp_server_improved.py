#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import logging
import argparse
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Importiere die Basisklasse
from base_mcp_server import BaseMCPServer

class DockerMCPServer(BaseMCPServer):
    """
    MCP-Server für die Verwaltung von Docker-Containern.
    
    Diese Klasse implementiert einen MCP-Server, der Docker-Container
    verwalten kann.
    """
    
    def __init__(self, 
                 docker_network: str = None,
                 allowed_images: List[str] = None,
                 **kwargs):
        """
        Initialisiert den Docker MCP-Server.
        
        Args:
            docker_network: Name des Docker-Netzwerks
            allowed_images: Liste der erlaubten Docker-Images
            **kwargs: Weitere Argumente für die Basisklasse
        """
        super().__init__(
            name="docker-mcp-server",
            description="MCP-Server für die Verwaltung von Docker-Containern",
            version="1.0.0",
            **kwargs
        )
        
        # Docker-spezifische Konfiguration
        self.docker_network = docker_network or os.environ.get('DOCKER_NETWORK', 'dev-server-network')
        self.allowed_images = allowed_images or []
        
        # Lade erlaubte Images aus der Umgebung, falls nicht angegeben
        if not self.allowed_images and 'DOCKER_ALLOWED_IMAGES' in os.environ:
            self.allowed_images = os.environ['DOCKER_ALLOWED_IMAGES'].split(',')
        
        # Container-Cache
        self.containers = {}
    
    async def initialize(self):
        """
        Initialisiert den Server und prüft Docker-Abhängigkeiten.
        """
        await super().initialize()
        
        # Prüfe, ob Docker installiert ist und läuft
        if not DockerUtils.check_docker_installed():
            self.logger.error("Docker ist nicht installiert")
            raise RuntimeError("Docker ist nicht installiert")
        
        if not DockerUtils.check_docker_running():
            self.logger.error("Docker läuft nicht")
            raise RuntimeError("Docker läuft nicht")
        
        # Prüfe, ob das Docker-Netzwerk existiert, und erstelle es, falls nicht
        await self._ensure_docker_network()
        
        # Lade bestehende Container
        await self._load_containers()
    
    async def _ensure_docker_network(self):
        """
        Stellt sicher, dass das Docker-Netzwerk existiert.
        """
        try:
            # Führe den Befehl aus, um zu prüfen, ob das Netzwerk existiert
            process = await asyncio.create_subprocess_exec(
                'docker', 'network', 'inspect', self.docker_network,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                # Netzwerk existiert nicht, erstelle es
                self.logger.info(f"Docker-Netzwerk {self.docker_network} existiert nicht, erstelle es")
                
                create_process = await asyncio.create_subprocess_exec(
                    'docker', 'network', 'create', self.docker_network,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                create_stdout, create_stderr = await create_process.communicate()
                
                if create_process.returncode != 0:
                    self.logger.error(f"Fehler beim Erstellen des Docker-Netzwerks: {create_stderr.decode()}")
                    raise RuntimeError(f"Fehler beim Erstellen des Docker-Netzwerks: {create_stderr.decode()}")
                
                self.logger.info(f"Docker-Netzwerk {self.docker_network} erfolgreich erstellt")
            else:
                self.logger.info(f"Docker-Netzwerk {self.docker_network} existiert bereits")
        except Exception as e:
            self.logger.error(f"Fehler bei der Überprüfung des Docker-Netzwerks: {e}")
            raise
    
    async def _load_containers(self):
        """
        Lädt bestehende Docker-Container.
        """
        try:
            # Führe den Befehl aus, um alle Container zu listen
            process = await asyncio.create_subprocess_exec(
                'docker', 'ps', '-a', '--format', '{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Abrufen der Container: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Abrufen der Container: {stderr.decode()}")
            
            # Verarbeite die Ausgabe
            containers = stdout.decode().strip().split('\n')
            for container in containers:
                if not container:
                    continue
                
                parts = container.split('|')
                if len(parts) != 4:
                    continue
                
                container_id, name, image, status = parts
                
                # Speichere den Container im Cache
                self.containers[name] = {
                    'id': container_id,
                    'name': name,
                    'image': image,
                    'status': status,
                    'running': status.startswith('Up')
                }
            
            self.logger.info(f"{len(self.containers)} Docker-Container geladen")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Container: {e}")
            raise
    
    async def _load_tools(self):
        """
        Definiert die verfügbaren Tools für den Docker MCP-Server.
        """
        self.tools = [
            {
                "name": "list_containers",
                "description": "Listet alle Docker-Container auf",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "all": {
                            "type": "boolean",
                            "description": "Alle Container anzeigen (auch gestoppte)"
                        }
                    }
                }
            },
            {
                "name": "get_container",
                "description": "Ruft Informationen über einen Docker-Container ab",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name des Containers"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "start_container",
                "description": "Startet einen Docker-Container",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name des Containers"
                        },
                        "image": {
                            "type": "string",
                            "description": "Docker-Image"
                        },
                        "ports": {
                            "type": "array",
                            "description": "Port-Mappings (Format: 'host:container')",
                            "items": {
                                "type": "string"
                            }
                        },
                        "environment": {
                            "type": "object",
                            "description": "Umgebungsvariablen"
                        },
                        "volumes": {
                            "type": "array",
                            "description": "Volume-Mappings (Format: 'host:container')",
                            "items": {
                                "type": "string"
                            }
                        },
                        "command": {
                            "type": "string",
                            "description": "Befehl, der im Container ausgeführt werden soll"
                        }
                    },
                    "required": ["name", "image"]
                }
            },
            {
                "name": "stop_container",
                "description": "Stoppt einen Docker-Container",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name des Containers"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in Sekunden"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "restart_container",
                "description": "Startet einen Docker-Container neu",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name des Containers"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in Sekunden"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "remove_container",
                "description": "Entfernt einen Docker-Container",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name des Containers"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Container gewaltsam entfernen"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "get_container_logs",
                "description": "Ruft die Logs eines Docker-Containers ab",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name des Containers"
                        },
                        "tail": {
                            "type": "integer",
                            "description": "Anzahl der letzten Zeilen"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "execute_command",
                "description": "Führt einen Befehl in einem Docker-Container aus",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name des Containers"
                        },
                        "command": {
                            "type": "string",
                            "description": "Auszuführender Befehl"
                        }
                    },
                    "required": ["name", "command"]
                }
            },
            {
                "name": "list_images",
                "description": "Listet alle Docker-Images auf",
                "parameter_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "pull_image",
                "description": "Lädt ein Docker-Image herunter",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "image": {
                            "type": "string",
                            "description": "Docker-Image"
                        }
                    },
                    "required": ["image"]
                }
            }
        ]
        
        self.logger.info(f"MCP-Tools geladen: {len(self.tools)} Tools verfügbar")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft ein Tool auf.
        
        Args:
            tool_name: Name des Tools
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
            
        Raises:
            Exception: Wenn das Tool nicht gefunden wurde oder ein Fehler auftrat
        """
        self.logger.info(f"Tool-Aufruf: {tool_name} mit Argumenten: {json.dumps(arguments)}")
        
        # Rufe die entsprechende Methode auf
        method_name = f"_handle_{tool_name}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return await method(arguments)
        else:
            raise Exception(f"Tool nicht gefunden: {tool_name}")
    
    async def _handle_list_containers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Listet alle Docker-Container auf.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        all_containers = arguments.get("all", True)
        
        try:
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            # Filtere die Container
            containers = []
            for name, container in self.containers.items():
                if all_containers or container['running']:
                    containers.append(container)
            
            return {
                "containers": containers
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Auflisten der Container: {e}")
            raise
    
    async def _handle_get_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft Informationen über einen Docker-Container ab.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("Parameter name fehlt")
        
        try:
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            # Prüfe, ob der Container existiert
            if name not in self.containers:
                return {
                    "exists": False,
                    "message": f"Container {name} existiert nicht"
                }
            
            # Rufe detaillierte Informationen ab
            process = await asyncio.create_subprocess_exec(
                'docker', 'inspect', name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Abrufen der Container-Informationen: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Abrufen der Container-Informationen: {stderr.decode()}")
            
            # Parse die Ausgabe
            container_info = json.loads(stdout.decode())
            
            return {
                "exists": True,
                "container": self.containers[name],
                "details": container_info[0] if container_info else {}
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Container-Informationen: {e}")
            raise
    
    async def _handle_start_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Startet einen Docker-Container.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("Parameter name fehlt")
        
        image = arguments.get("image")
        if not image:
            raise ValueError("Parameter image fehlt")
        
        # Prüfe, ob das Image erlaubt ist
        if self.allowed_images and image not in self.allowed_images:
            raise ValueError(f"Docker-Image {image} ist nicht erlaubt")
        
        ports = arguments.get("ports", [])
        environment = arguments.get("environment", {})
        volumes = arguments.get("volumes", [])
        command = arguments.get("command", "")
        
        try:
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            # Prüfe, ob der Container bereits existiert
            if name in self.containers:
                # Prüfe, ob der Container bereits läuft
                if self.containers[name]['running']:
                    return {
                        "success": True,
                        "message": f"Container {name} läuft bereits",
                        "container": self.containers[name]
                    }
                
                # Starte den bestehenden Container
                process = await asyncio.create_subprocess_exec(
                    'docker', 'start', name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    self.logger.error(f"Fehler beim Starten des Containers: {stderr.decode()}")
                    raise RuntimeError(f"Fehler beim Starten des Containers: {stderr.decode()}")
                
                # Aktualisiere den Container-Cache
                await self._load_containers()
                
                return {
                    "success": True,
                    "message": f"Container {name} erfolgreich gestartet",
                    "container": self.containers[name]
                }
            
            # Erstelle den Container
            cmd = ['docker', 'run', '-d', '--name', name, '--network', self.docker_network]
            
            # Füge Port-Mappings hinzu
            for port in ports:
                cmd.extend(['-p', port])
            
            # Füge Umgebungsvariablen hinzu
            for key, value in environment.items():
                cmd.extend(['-e', f"{key}={value}"])
            
            # Füge Volume-Mappings hinzu
            for volume in volumes:
                cmd.extend(['-v', volume])
            
            # Füge das Image hinzu
            cmd.append(image)
            
            # Füge den Befehl hinzu, falls angegeben
            if command:
                cmd.extend(command.split())
            
            # Führe den Befehl aus
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Erstellen des Containers: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Erstellen des Containers: {stderr.decode()}")
            
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            return {
                "success": True,
                "message": f"Container {name} erfolgreich erstellt und gestartet",
                "container": self.containers[name]
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Starten des Containers: {e}")
            raise
    
    async def _handle_stop_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stoppt einen Docker-Container.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("Parameter name fehlt")
        
        timeout = arguments.get("timeout", 10)
        
        try:
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            # Prüfe, ob der Container existiert
            if name not in self.containers:
                return {
                    "success": False,
                    "message": f"Container {name} existiert nicht"
                }
            
            # Prüfe, ob der Container bereits gestoppt ist
            if not self.containers[name]['running']:
                return {
                    "success": True,
                    "message": f"Container {name} ist bereits gestoppt",
                    "container": self.containers[name]
                }
            
            # Stoppe den Container
            process = await asyncio.create_subprocess_exec(
                'docker', 'stop', '-t', str(timeout), name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Stoppen des Containers: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Stoppen des Containers: {stderr.decode()}")
            
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            return {
                "success": True,
                "message": f"Container {name} erfolgreich gestoppt",
                "container": self.containers[name]
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Stoppen des Containers: {e}")
            raise
    
    async def _handle_restart_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Startet einen Docker-Container neu.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("Parameter name fehlt")
        
        timeout = arguments.get("timeout", 10)
        
        try:
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            # Prüfe, ob der Container existiert
            if name not in self.containers:
                return {
                    "success": False,
                    "message": f"Container {name} existiert nicht"
                }
            
            # Starte den Container neu
            process = await asyncio.create_subprocess_exec(
                'docker', 'restart', '-t', str(timeout), name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Neustarten des Containers: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Neustarten des Containers: {stderr.decode()}")
            
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            return {
                "success": True,
                "message": f"Container {name} erfolgreich neu gestartet",
                "container": self.containers[name]
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Neustarten des Containers: {e}")
            raise
    
    async def _handle_remove_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entfernt einen Docker-Container.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("Parameter name fehlt")
        
        force = arguments.get("force", False)
        
        try:
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            # Prüfe, ob der Container existiert
            if name not in self.containers:
                return {
                    "success": False,
                    "message": f"Container {name} existiert nicht"
                }
            
            # Entferne den Container
            cmd = ['docker', 'rm']
            if force:
                cmd.append('-f')
            cmd.append(name)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Entfernen des Containers: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Entfernen des Containers: {stderr.decode()}")
            
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            return {
                "success": True,
                "message": f"Container {name} erfolgreich entfernt"
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Entfernen des Containers: {e}")
            raise
    
    async def _handle_get_container_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft die Logs eines Docker-Containers ab.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("Parameter name fehlt")
        
        tail = arguments.get("tail", 100)
        
        try:
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            # Prüfe, ob der Container existiert
            if name not in self.containers:
                return {
                    "success": False,
                    "message": f"Container {name} existiert nicht"
                }
            
            # Rufe die Logs ab
            process = await asyncio.create_subprocess_exec(
                'docker', 'logs', '--tail', str(tail), name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Abrufen der Container-Logs: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Abrufen der Container-Logs: {stderr.decode()}")
            
            return {
                "success": True,
                "logs": stdout.decode()
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Container-Logs: {e}")
            raise
    
    async def _handle_execute_command(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt einen Befehl in einem Docker-Container aus.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("Parameter name fehlt")
        
        command = arguments.get("command")
        if not command:
            raise ValueError("Parameter command fehlt")
        
        try:
            # Aktualisiere den Container-Cache
            await self._load_containers()
            
            # Prüfe, ob der Container existiert
            if name not in self.containers:
                return {
                    "success": False,
                    "message": f"Container {name} existiert nicht"
                }
            
            # Prüfe, ob der Container läuft
            if not self.containers[name]['running']:
                return {
                    "success": False,
                    "message": f"Container {name} läuft nicht"
                }
            
            # Führe den Befehl aus
            process = await asyncio.create_subprocess_exec(
                'docker', 'exec', name, *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Ausführen des Befehls: {e}")
            raise
    
    async def _handle_list_images(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Listet alle Docker-Images auf.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        try:
            # Führe den Befehl aus, um alle Images zu listen
            process = await asyncio.create_subprocess_exec(
                'docker', 'images', '--format', '{{.Repository}}:{{.Tag}}|{{.ID}}|{{.Size}}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Abrufen der Images: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Abrufen der Images: {stderr.decode()}")
            
            # Verarbeite die Ausgabe
            images = []
            for line in stdout.decode().strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) != 3:
                    continue
                
                name, id, size = parts
                
                images.append({
                    'name': name,
                    'id': id,
                    'size': size
                })
            
            return {
                "images": images
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Auflisten der Images: {e}")
            raise
    
    async def _handle_pull_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lädt ein Docker-Image herunter.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        image = arguments.get("image")
        if not image:
            raise ValueError("Parameter image fehlt")
        
        # Prüfe, ob das Image erlaubt ist
        if self.allowed_images and image not in self.allowed_images:
            raise ValueError(f"Docker-Image {image} ist nicht erlaubt")
        
        try:
            # Führe den Befehl aus, um das Image herunterzuladen
            process = await asyncio.create_subprocess_exec(
                'docker', 'pull', image,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Fehler beim Herunterladen des Images: {stderr.decode()}")
                raise RuntimeError(f"Fehler beim Herunterladen des Images: {stderr.decode()}")
            
            return {
                "success": True,
                "message": f"Image {image} erfolgreich heruntergeladen",
                "output": stdout.decode()
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Herunterladen des Images: {e}")
            raise


async def main():
    """
    Hauptfunktion zum Starten des Docker MCP-Servers.
    """
    parser = argparse.ArgumentParser(description='Docker MCP Server')
    parser = BaseMCPServer.add_common_arguments(parser)
    
    parser.add_argument('--docker-network', default=os.environ.get('DOCKER_NETWORK', 'dev-server-network'),
                        help='Name des Docker-Netzwerks (Standard: dev-server-network)')
    parser.add_argument('--allowed-images', nargs='+',
                        help='Liste der erlaubten Docker-Images')
    
    args = parser.parse_args()
    
    await DockerMCPServer.run_server(
        args,
        docker_network=args.docker_network,
        allowed_images=args.allowed_images
    )


if __name__ == "__main__":
    asyncio.run(main())