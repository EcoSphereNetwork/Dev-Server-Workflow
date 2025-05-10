"""
MCP Server Registry - Verwaltet die Registry von MCP Servern.

Diese Klasse bietet Funktionen zum Verwalten der Registry von MCP Servern.
"""

import os
import re
import json
import logging
import tempfile
import subprocess
import requests
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse

# Erstelle Logger
logger = logging.getLogger(__name__)


class MCPServerRegistry:
    """MCP Server Registry Klasse."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialisiere die MCP Server Registry.

        Args:
            cache_dir: Optionaler Pfad zum Cache-Verzeichnis
        """
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "mcp_registry_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.repositories = []
        self.docker_hub_users = []
        self.servers = {}

    def add_repository(self, repo_url: str) -> None:
        """
        Füge ein Repository zur Registry hinzu.

        Args:
            repo_url: Die URL des Repositories
        """
        if repo_url not in self.repositories:
            self.repositories.append(repo_url)

    def remove_repository(self, repo_url: str) -> None:
        """
        Entferne ein Repository aus der Registry.

        Args:
            repo_url: Die URL des Repositories
        """
        if repo_url in self.repositories:
            self.repositories.remove(repo_url)

    def add_docker_hub_user(self, username: str) -> None:
        """
        Füge einen Docker Hub Benutzer zur Registry hinzu.

        Args:
            username: Der Benutzername
        """
        if username not in self.docker_hub_users:
            self.docker_hub_users.append(username)

    def remove_docker_hub_user(self, username: str) -> None:
        """
        Entferne einen Docker Hub Benutzer aus der Registry.

        Args:
            username: Der Benutzername
        """
        if username in self.docker_hub_users:
            self.docker_hub_users.remove(username)

    def update(self) -> None:
        """Aktualisiere die Registry mit den neuesten MCP Servern aus den konfigurierten Repositories und Docker Hub Benutzern."""
        try:
            # Leere die aktuelle Registry
            self.servers = {}
            
            # Aktualisiere die Registry mit den konfigurierten Repositories
            for repo_url in self.repositories:
                self._update_from_repository(repo_url)
            
            # Aktualisiere die Registry mit den konfigurierten Docker Hub Benutzern
            for username in self.docker_hub_users:
                self._update_from_docker_hub(username)
        except Exception as e:
            logger.exception(f"Fehler bei der Aktualisierung der Registry: {e}")

    def _update_from_repository(self, repo_url: str) -> None:
        """
        Aktualisiere die Registry mit den MCP Servern aus einem Repository.

        Args:
            repo_url: Die URL des Repositories
        """
        try:
            # Parse die Repository-URL
            parsed_url = urlparse(repo_url)
            
            # Extrahiere den Repository-Namen
            repo_path = parsed_url.path.strip("/")
            repo_name = repo_path.split("/")[-1]
            
            # Erstelle den Cache-Pfad für das Repository
            repo_cache_dir = os.path.join(self.cache_dir, repo_name)
            
            # Klone oder aktualisiere das Repository
            if os.path.exists(repo_cache_dir):
                # Aktualisiere das Repository
                subprocess.run(["git", "pull"], cwd=repo_cache_dir, check=True)
            else:
                # Klone das Repository
                subprocess.run(["git", "clone", repo_url, repo_cache_dir], check=True)
            
            # Durchsuche das Repository nach MCP Servern
            self._scan_repository(repo_cache_dir, repo_url)
        except Exception as e:
            logger.exception(f"Fehler bei der Aktualisierung aus Repository {repo_url}: {e}")

    def _scan_repository(self, repo_dir: str, repo_url: str) -> None:
        """
        Durchsuche ein Repository nach MCP Servern.

        Args:
            repo_dir: Der Pfad zum Repository
            repo_url: Die URL des Repositories
        """
        try:
            # Durchsuche das Repository nach README.md-Dateien
            for root, dirs, files in os.walk(repo_dir):
                if "README.md" in files:
                    # Lese die README.md-Datei
                    with open(os.path.join(root, "README.md"), "r") as f:
                        readme_content = f.read()
                    
                    # Extrahiere MCP Server-Informationen aus der README.md-Datei
                    servers = self._extract_servers_from_readme(readme_content, repo_url)
                    
                    # Füge die Server zur Registry hinzu
                    for server_id, server_info in servers.items():
                        self.servers[server_id] = server_info
        except Exception as e:
            logger.exception(f"Fehler beim Scannen des Repositories {repo_dir}: {e}")

    def _extract_servers_from_readme(self, readme_content: str, repo_url: str) -> Dict[str, Dict[str, Any]]:
        """
        Extrahiere MCP Server-Informationen aus einer README.md-Datei.

        Args:
            readme_content: Der Inhalt der README.md-Datei
            repo_url: Die URL des Repositories

        Returns:
            Ein Dictionary mit MCP Server-Informationen
        """
        servers = {}
        
        try:
            # Suche nach Links zu MCP Servern
            # Format: [Server Name](https://github.com/username/repo) - Beschreibung
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)(?:\s*-\s*([^\n]+))?"
            for match in re.finditer(link_pattern, readme_content):
                server_name = match.group(1)
                server_url = match.group(2)
                server_description = match.group(3) or ""
                
                # Erstelle eine eindeutige ID für den Server
                server_id = server_url.split("/")[-1].lower()
                
                # Füge den Server zur Registry hinzu
                servers[server_id] = {
                    "id": server_id,
                    "name": server_name,
                    "url": server_url,
                    "description": server_description.strip(),
                    "source": "github",
                    "source_url": repo_url
                }
        except Exception as e:
            logger.exception(f"Fehler beim Extrahieren von Servern aus README: {e}")
        
        return servers

    def _update_from_docker_hub(self, username: str) -> None:
        """
        Aktualisiere die Registry mit den MCP Servern von Docker Hub.

        Args:
            username: Der Docker Hub Benutzername
        """
        try:
            # Rufe die Docker Hub API auf, um die Repositories des Benutzers zu erhalten
            url = f"https://hub.docker.com/v2/repositories/{username}/"
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse die Antwort
            data = response.json()
            
            # Extrahiere die Repositories
            repositories = data.get("results", [])
            
            # Durchsuche die Repositories nach MCP Servern
            for repo in repositories:
                repo_name = repo.get("name", "")
                
                # Prüfe, ob es sich um einen MCP Server handelt
                if "mcp" in repo_name.lower() or "server" in repo_name.lower():
                    # Erstelle eine eindeutige ID für den Server
                    server_id = f"docker-{username}-{repo_name}".lower()
                    
                    # Füge den Server zur Registry hinzu
                    self.servers[server_id] = {
                        "id": server_id,
                        "name": repo_name,
                        "url": f"https://hub.docker.com/r/{username}/{repo_name}",
                        "description": repo.get("description", ""),
                        "source": "docker_hub",
                        "source_url": f"https://hub.docker.com/u/{username}",
                        "docker_image": f"{username}/{repo_name}"
                    }
        except Exception as e:
            logger.exception(f"Fehler bei der Aktualisierung von Docker Hub für Benutzer {username}: {e}")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Suche nach MCP Servern in der Registry.

        Args:
            query: Die Suchanfrage

        Returns:
            Eine Liste von MCP Servern, die der Suchanfrage entsprechen
        """
        results = []
        
        try:
            # Normalisiere die Suchanfrage
            query = query.lower()
            
            # Durchsuche die Registry nach Servern, die der Suchanfrage entsprechen
            for server_id, server_info in self.servers.items():
                # Prüfe, ob die Suchanfrage im Server-Namen, der Beschreibung oder der ID enthalten ist
                if (query in server_id.lower() or
                    query in server_info.get("name", "").lower() or
                    query in server_info.get("description", "").lower()):
                    results.append(server_info)
        except Exception as e:
            logger.exception(f"Fehler bei der Suche nach MCP Servern: {e}")
        
        return results

    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        Hole Informationen über einen MCP Server.

        Args:
            server_id: Die ID des MCP Servers

        Returns:
            Ein Dictionary mit Informationen über den MCP Server, oder None, wenn der Server nicht gefunden wurde
        """
        return self.servers.get(server_id)