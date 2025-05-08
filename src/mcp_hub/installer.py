"""
MCP Server Installer - Installiert und verwaltet MCP Server.

Diese Klasse bietet Funktionen zum Installieren und Verwalten von MCP Servern.
"""

import os
import re
import json
import logging
import shutil
import tempfile
import subprocess
import requests
from typing import Dict, List, Optional, Any, Union

# Erstelle Logger
logger = logging.getLogger(__name__)


class MCPServerInstaller:
    """MCP Server Installer Klasse."""

    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialisiere den MCP Server Installer.

        Args:
            temp_dir: Optionaler Pfad zum temporären Verzeichnis
        """
        self.temp_dir = temp_dir or os.path.join(tempfile.gettempdir(), "mcp_installer_temp")
        os.makedirs(self.temp_dir, exist_ok=True)

    def install(self, server_info: Dict[str, Any], target_dir: str) -> bool:
        """
        Installiere einen MCP Server.

        Args:
            server_info: Informationen über den zu installierenden MCP Server
            target_dir: Das Zielverzeichnis für die Installation

        Returns:
            True, wenn die Installation erfolgreich war, sonst False
        """
        try:
            # Erstelle das Zielverzeichnis, falls es nicht existiert
            os.makedirs(target_dir, exist_ok=True)
            
            # Bestimme die Installationsmethode basierend auf der Quelle
            source = server_info.get("source", "")
            
            if source == "github":
                return self._install_from_github(server_info, target_dir)
            elif source == "docker_hub":
                return self._install_from_docker_hub(server_info, target_dir)
            else:
                logger.error(f"Unbekannte Quelle: {source}")
                return False
        except Exception as e:
            logger.exception(f"Fehler bei der Installation von MCP Server: {e}")
            return False

    def _install_from_github(self, server_info: Dict[str, Any], target_dir: str) -> bool:
        """
        Installiere einen MCP Server von GitHub.

        Args:
            server_info: Informationen über den zu installierenden MCP Server
            target_dir: Das Zielverzeichnis für die Installation

        Returns:
            True, wenn die Installation erfolgreich war, sonst False
        """
        try:
            # Hole die Repository-URL
            repo_url = server_info.get("url", "")
            if not repo_url:
                logger.error("Keine Repository-URL angegeben")
                return False
            
            # Extrahiere den Repository-Namen
            repo_name = repo_url.split("/")[-1]
            
            # Erstelle den Pfad zum Zielverzeichnis
            server_dir = os.path.join(target_dir, repo_name)
            
            # Klone das Repository
            subprocess.run(["git", "clone", repo_url, server_dir], check=True)
            
            # Prüfe, ob das Repository erfolgreich geklont wurde
            if not os.path.exists(server_dir):
                logger.error(f"Repository konnte nicht geklont werden: {repo_url}")
                return False
            
            # Prüfe, ob eine package.json oder pyproject.toml vorhanden ist
            if os.path.exists(os.path.join(server_dir, "package.json")):
                # Installiere Node.js-Abhängigkeiten
                subprocess.run(["npm", "install"], cwd=server_dir, check=True)
            elif os.path.exists(os.path.join(server_dir, "pyproject.toml")):
                # Installiere Python-Abhängigkeiten
                subprocess.run(["pip", "install", "-e", "."], cwd=server_dir, check=True)
            elif os.path.exists(os.path.join(server_dir, "requirements.txt")):
                # Installiere Python-Abhängigkeiten
                subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=server_dir, check=True)
            
            return True
        except Exception as e:
            logger.exception(f"Fehler bei der Installation von GitHub: {e}")
            return False

    def _install_from_docker_hub(self, server_info: Dict[str, Any], target_dir: str) -> bool:
        """
        Installiere einen MCP Server von Docker Hub.

        Args:
            server_info: Informationen über den zu installierenden MCP Server
            target_dir: Das Zielverzeichnis für die Installation

        Returns:
            True, wenn die Installation erfolgreich war, sonst False
        """
        try:
            # Hole das Docker-Image
            docker_image = server_info.get("docker_image", "")
            if not docker_image:
                logger.error("Kein Docker-Image angegeben")
                return False
            
            # Extrahiere den Image-Namen
            image_name = docker_image.split("/")[-1]
            
            # Erstelle den Pfad zum Zielverzeichnis
            server_dir = os.path.join(target_dir, image_name)
            
            # Erstelle das Verzeichnis
            os.makedirs(server_dir, exist_ok=True)
            
            # Erstelle eine docker-compose.yml-Datei
            docker_compose_content = f"""version: '3'

services:
  {image_name}:
    image: {docker_image}
    container_name: mcp-{image_name}
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - .:/app
"""
            
            # Schreibe die docker-compose.yml-Datei
            with open(os.path.join(server_dir, "docker-compose.yml"), "w") as f:
                f.write(docker_compose_content)
            
            # Erstelle eine README.md-Datei
            readme_content = f"""# {server_info.get('name', image_name)}

{server_info.get('description', '')}

## Installation

```bash
docker-compose up -d
```

## Verwendung

Der Server ist unter http://localhost:8000 erreichbar.
"""
            
            # Schreibe die README.md-Datei
            with open(os.path.join(server_dir, "README.md"), "w") as f:
                f.write(readme_content)
            
            return True
        except Exception as e:
            logger.exception(f"Fehler bei der Installation von Docker Hub: {e}")
            return False

    def uninstall(self, server_info: Dict[str, Any]) -> bool:
        """
        Deinstalliere einen MCP Server.

        Args:
            server_info: Informationen über den zu deinstallierenden MCP Server

        Returns:
            True, wenn die Deinstallation erfolgreich war, sonst False
        """
        try:
            # Hole den Serverpfad
            server_path = server_info.get("path", "")
            if not server_path or not os.path.exists(server_path):
                logger.error(f"Serverpfad nicht gefunden: {server_path}")
                return False
            
            # Prüfe, ob eine docker-compose.yml vorhanden ist
            if os.path.exists(os.path.join(server_path, "docker-compose.yml")):
                # Stoppe den Server mit Docker Compose
                subprocess.run(["docker-compose", "down"], cwd=server_path, check=True)
            
            # Prüfe, ob eine Dockerfile vorhanden ist
            elif os.path.exists(os.path.join(server_path, "Dockerfile")):
                # Stoppe den Server mit Docker
                server_name = os.path.basename(server_path)
                subprocess.run(["docker", "stop", f"mcp-{server_name}"], check=True)
                subprocess.run(["docker", "rm", f"mcp-{server_name}"], check=True)
            
            # Lösche das Verzeichnis
            shutil.rmtree(server_path)
            
            return True
        except Exception as e:
            logger.exception(f"Fehler bei der Deinstallation von MCP Server: {e}")
            return False