"""
MCP Hub Manager - Hauptklasse für den MCP Hub.

Diese Klasse bietet Funktionen zum Suchen, Installieren und Verwalten von MCP Servern.
"""

import os
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any, Union

from .registry import MCPServerRegistry
from .installer import MCPServerInstaller

# Erstelle Logger
logger = logging.getLogger(__name__)


class MCPHubManager:
    """MCP Hub Manager Klasse."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialisiere den MCP Hub Manager.

        Args:
            config_path: Optionaler Pfad zur Konfigurationsdatei
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "config", "hub_config.json")
        self.registry = MCPServerRegistry()
        self.installer = MCPServerInstaller()
        self.config = self._load_config()
        self.installed_servers = self._load_installed_servers()

    def _load_config(self) -> Dict[str, Any]:
        """
        Lade die Konfiguration aus der Konfigurationsdatei.

        Returns:
            Die Konfiguration
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    return json.load(f)
            else:
                # Erstelle Standardkonfiguration
                config = {
                    "repositories": [
                        "https://github.com/punkpeye/awesome-mcp-servers",
                        "https://github.com/appcypher/awesome-mcp-servers"
                    ],
                    "docker_hub_users": [
                        "mcp"
                    ],
                    "local_servers_path": os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_servers"),
                    "auto_update": True,
                    "update_interval_hours": 24
                }
                
                # Erstelle Konfigurationsverzeichnis, falls es nicht existiert
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                
                # Speichere Standardkonfiguration
                with open(self.config_path, "w") as f:
                    json.dump(config, f, indent=2)
                
                return config
        except Exception as e:
            logger.exception(f"Fehler beim Laden der Konfiguration: {e}")
            return {
                "repositories": [],
                "docker_hub_users": [],
                "local_servers_path": os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_servers"),
                "auto_update": False,
                "update_interval_hours": 24
            }

    def _save_config(self) -> None:
        """Speichere die Konfiguration in der Konfigurationsdatei."""
        try:
            # Erstelle Konfigurationsverzeichnis, falls es nicht existiert
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Speichere Konfiguration
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.exception(f"Fehler beim Speichern der Konfiguration: {e}")

    def _load_installed_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        Lade die installierten MCP Server.

        Returns:
            Ein Dictionary mit den installierten MCP Servern
        """
        installed_servers = {}
        
        try:
            # Durchsuche das lokale Serververzeichnis
            local_servers_path = self.config.get("local_servers_path", "")
            if os.path.exists(local_servers_path):
                for server_dir in os.listdir(local_servers_path):
                    server_path = os.path.join(local_servers_path, server_dir)
                    if os.path.isdir(server_path):
                        # Prüfe, ob es sich um einen MCP Server handelt
                        if self._is_mcp_server(server_path):
                            server_info = self._get_server_info(server_path)
                            if server_info:
                                installed_servers[server_dir] = server_info
        except Exception as e:
            logger.exception(f"Fehler beim Laden der installierten MCP Server: {e}")
        
        return installed_servers

    def _is_mcp_server(self, server_path: str) -> bool:
        """
        Prüfe, ob es sich bei dem angegebenen Pfad um einen MCP Server handelt.

        Args:
            server_path: Der zu prüfende Pfad

        Returns:
            True, wenn es sich um einen MCP Server handelt, sonst False
        """
        # Prüfe, ob eine Dockerfile oder docker-compose.yml vorhanden ist
        if os.path.exists(os.path.join(server_path, "Dockerfile")) or os.path.exists(os.path.join(server_path, "docker-compose.yml")):
            return True
        
        # Prüfe, ob eine main.py oder server.py vorhanden ist
        if os.path.exists(os.path.join(server_path, "main.py")) or os.path.exists(os.path.join(server_path, "server.py")):
            return True
        
        # Prüfe, ob ein Unterverzeichnis mit dem Namen des Servers existiert
        server_name = os.path.basename(server_path)
        if os.path.exists(os.path.join(server_path, server_name)):
            return True
        
        return False

    def _get_server_info(self, server_path: str) -> Optional[Dict[str, Any]]:
        """
        Hole Informationen über einen MCP Server.

        Args:
            server_path: Der Pfad zum MCP Server

        Returns:
            Ein Dictionary mit Informationen über den MCP Server, oder None, wenn keine Informationen gefunden wurden
        """
        try:
            # Prüfe, ob eine package.json oder pyproject.toml vorhanden ist
            if os.path.exists(os.path.join(server_path, "package.json")):
                with open(os.path.join(server_path, "package.json"), "r") as f:
                    package_info = json.load(f)
                    return {
                        "name": package_info.get("name", ""),
                        "version": package_info.get("version", ""),
                        "description": package_info.get("description", ""),
                        "type": "nodejs",
                        "path": server_path
                    }
            elif os.path.exists(os.path.join(server_path, "pyproject.toml")):
                # Einfache Extraktion von Informationen aus pyproject.toml
                with open(os.path.join(server_path, "pyproject.toml"), "r") as f:
                    content = f.read()
                    name = ""
                    version = ""
                    description = ""
                    
                    # Extrahiere Name
                    name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
                    if name_match:
                        name = name_match.group(1)
                    
                    # Extrahiere Version
                    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
                    if version_match:
                        version = version_match.group(1)
                    
                    # Extrahiere Beschreibung
                    description_match = re.search(r'description\s*=\s*"([^"]+)"', content)
                    if description_match:
                        description = description_match.group(1)
                    
                    return {
                        "name": name,
                        "version": version,
                        "description": description,
                        "type": "python",
                        "path": server_path
                    }
            
            # Fallback: Verwende den Verzeichnisnamen als Servernamen
            server_name = os.path.basename(server_path)
            return {
                "name": server_name,
                "version": "unknown",
                "description": "",
                "type": "unknown",
                "path": server_path
            }
        except Exception as e:
            logger.exception(f"Fehler beim Abrufen von Serverinformationen: {e}")
            return None

    def update_registry(self) -> None:
        """Aktualisiere die Registry mit den neuesten MCP Servern aus den konfigurierten Repositories."""
        try:
            # Aktualisiere die Registry mit den konfigurierten Repositories
            for repo_url in self.config.get("repositories", []):
                self.registry.add_repository(repo_url)
            
            # Aktualisiere die Registry mit den konfigurierten Docker Hub Benutzern
            for docker_hub_user in self.config.get("docker_hub_users", []):
                self.registry.add_docker_hub_user(docker_hub_user)
            
            # Aktualisiere die Registry
            self.registry.update()
        except Exception as e:
            logger.exception(f"Fehler bei der Aktualisierung der Registry: {e}")

    def search_servers(self, query: str) -> List[Dict[str, Any]]:
        """
        Suche nach MCP Servern in der Registry.

        Args:
            query: Die Suchanfrage

        Returns:
            Eine Liste von MCP Servern, die der Suchanfrage entsprechen
        """
        try:
            # Suche in der Registry
            return self.registry.search(query)
        except Exception as e:
            logger.exception(f"Fehler bei der Suche nach MCP Servern: {e}")
            return []

    def install_server(self, server_id: str) -> bool:
        """
        Installiere einen MCP Server.

        Args:
            server_id: Die ID des zu installierenden MCP Servers

        Returns:
            True, wenn die Installation erfolgreich war, sonst False
        """
        try:
            # Hole Serverinformationen aus der Registry
            server_info = self.registry.get_server(server_id)
            if not server_info:
                logger.error(f"MCP Server {server_id} nicht gefunden")
                return False
            
            # Installiere den Server
            success = self.installer.install(server_info, self.config.get("local_servers_path", ""))
            if success:
                # Aktualisiere die Liste der installierten Server
                self.installed_servers = self._load_installed_servers()
                return True
            else:
                logger.error(f"Fehler bei der Installation von MCP Server {server_id}")
                return False
        except Exception as e:
            logger.exception(f"Fehler bei der Installation von MCP Server {server_id}: {e}")
            return False

    def uninstall_server(self, server_id: str) -> bool:
        """
        Deinstalliere einen MCP Server.

        Args:
            server_id: Die ID des zu deinstallierenden MCP Servers

        Returns:
            True, wenn die Deinstallation erfolgreich war, sonst False
        """
        try:
            # Prüfe, ob der Server installiert ist
            if server_id not in self.installed_servers:
                logger.error(f"MCP Server {server_id} ist nicht installiert")
                return False
            
            # Hole Serverinformationen
            server_info = self.installed_servers[server_id]
            
            # Deinstalliere den Server
            success = self.installer.uninstall(server_info)
            if success:
                # Aktualisiere die Liste der installierten Server
                self.installed_servers = self._load_installed_servers()
                return True
            else:
                logger.error(f"Fehler bei der Deinstallation von MCP Server {server_id}")
                return False
        except Exception as e:
            logger.exception(f"Fehler bei der Deinstallation von MCP Server {server_id}: {e}")
            return False

    def start_server(self, server_id: str) -> bool:
        """
        Starte einen MCP Server.

        Args:
            server_id: Die ID des zu startenden MCP Servers

        Returns:
            True, wenn der Start erfolgreich war, sonst False
        """
        try:
            # Prüfe, ob der Server installiert ist
            if server_id not in self.installed_servers:
                logger.error(f"MCP Server {server_id} ist nicht installiert")
                return False
            
            # Hole Serverinformationen
            server_info = self.installed_servers[server_id]
            
            # Starte den Server
            server_path = server_info.get("path", "")
            if not server_path or not os.path.exists(server_path):
                logger.error(f"Serverpfad für {server_id} nicht gefunden")
                return False
            
            # Prüfe, ob eine docker-compose.yml vorhanden ist
            if os.path.exists(os.path.join(server_path, "docker-compose.yml")):
                # Starte den Server mit Docker Compose
                subprocess.run(["docker-compose", "up", "-d"], cwd=server_path, check=True)
                return True
            
            # Prüfe, ob eine Dockerfile vorhanden ist
            elif os.path.exists(os.path.join(server_path, "Dockerfile")):
                # Baue und starte den Server mit Docker
                subprocess.run(["docker", "build", "-t", f"mcp-{server_id}", "."], cwd=server_path, check=True)
                subprocess.run(["docker", "run", "-d", "--name", f"mcp-{server_id}", f"mcp-{server_id}"], check=True)
                return True
            
            # Prüfe, ob es sich um einen Python-Server handelt
            elif server_info.get("type") == "python":
                # Starte den Server mit Python
                subprocess.Popen(["python", "main.py"], cwd=server_path)
                return True
            
            # Prüfe, ob es sich um einen Node.js-Server handelt
            elif server_info.get("type") == "nodejs":
                # Starte den Server mit Node.js
                subprocess.Popen(["npm", "start"], cwd=server_path)
                return True
            
            else:
                logger.error(f"Unbekannter Servertyp für {server_id}")
                return False
        except Exception as e:
            logger.exception(f"Fehler beim Starten von MCP Server {server_id}: {e}")
            return False

    def stop_server(self, server_id: str) -> bool:
        """
        Stoppe einen MCP Server.

        Args:
            server_id: Die ID des zu stoppenden MCP Servers

        Returns:
            True, wenn der Stopp erfolgreich war, sonst False
        """
        try:
            # Prüfe, ob der Server installiert ist
            if server_id not in self.installed_servers:
                logger.error(f"MCP Server {server_id} ist nicht installiert")
                return False
            
            # Hole Serverinformationen
            server_info = self.installed_servers[server_id]
            
            # Stoppe den Server
            server_path = server_info.get("path", "")
            if not server_path or not os.path.exists(server_path):
                logger.error(f"Serverpfad für {server_id} nicht gefunden")
                return False
            
            # Prüfe, ob eine docker-compose.yml vorhanden ist
            if os.path.exists(os.path.join(server_path, "docker-compose.yml")):
                # Stoppe den Server mit Docker Compose
                subprocess.run(["docker-compose", "down"], cwd=server_path, check=True)
                return True
            
            # Prüfe, ob eine Dockerfile vorhanden ist
            elif os.path.exists(os.path.join(server_path, "Dockerfile")):
                # Stoppe den Server mit Docker
                subprocess.run(["docker", "stop", f"mcp-{server_id}"], check=True)
                subprocess.run(["docker", "rm", f"mcp-{server_id}"], check=True)
                return True
            
            # Für Python- und Node.js-Server: Finde und beende den Prozess
            else:
                # Hier müsste eine Prozesssuche und -beendigung implementiert werden
                # Dies ist plattformabhängig und kann komplex sein
                logger.warning(f"Automatisches Stoppen für {server_id} nicht implementiert")
                return False
        except Exception as e:
            logger.exception(f"Fehler beim Stoppen von MCP Server {server_id}: {e}")
            return False

    def list_installed_servers(self) -> List[Dict[str, Any]]:
        """
        Liste alle installierten MCP Server auf.

        Returns:
            Eine Liste aller installierten MCP Server
        """
        return list(self.installed_servers.values())

    def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """
        Hole den Status eines MCP Servers.

        Args:
            server_id: Die ID des MCP Servers

        Returns:
            Ein Dictionary mit dem Status des MCP Servers
        """
        try:
            # Prüfe, ob der Server installiert ist
            if server_id not in self.installed_servers:
                return {"status": "not_installed", "error": f"MCP Server {server_id} ist nicht installiert"}
            
            # Hole Serverinformationen
            server_info = self.installed_servers[server_id]
            
            # Prüfe, ob der Server läuft
            server_path = server_info.get("path", "")
            if not server_path or not os.path.exists(server_path):
                return {"status": "error", "error": f"Serverpfad für {server_id} nicht gefunden"}
            
            # Prüfe, ob eine docker-compose.yml vorhanden ist
            if os.path.exists(os.path.join(server_path, "docker-compose.yml")):
                # Prüfe den Status mit Docker Compose
                result = subprocess.run(["docker-compose", "ps", "-q"], cwd=server_path, capture_output=True, text=True)
                if result.stdout.strip():
                    return {"status": "running", "type": "docker-compose"}
                else:
                    return {"status": "stopped", "type": "docker-compose"}
            
            # Prüfe, ob eine Dockerfile vorhanden ist
            elif os.path.exists(os.path.join(server_path, "Dockerfile")):
                # Prüfe den Status mit Docker
                result = subprocess.run(["docker", "ps", "-q", "-f", f"name=mcp-{server_id}"], capture_output=True, text=True)
                if result.stdout.strip():
                    return {"status": "running", "type": "docker"}
                else:
                    return {"status": "stopped", "type": "docker"}
            
            # Für Python- und Node.js-Server: Prüfe, ob der Prozess läuft
            else:
                # Hier müsste eine Prozesssuche implementiert werden
                # Dies ist plattformabhängig und kann komplex sein
                return {"status": "unknown", "type": server_info.get("type", "unknown")}
        except Exception as e:
            logger.exception(f"Fehler beim Abrufen des Status von MCP Server {server_id}: {e}")
            return {"status": "error", "error": str(e)}

    def add_repository(self, repo_url: str) -> bool:
        """
        Füge ein Repository zur Konfiguration hinzu.

        Args:
            repo_url: Die URL des Repositories

        Returns:
            True, wenn das Repository hinzugefügt wurde, sonst False
        """
        try:
            # Prüfe, ob das Repository bereits in der Konfiguration ist
            if repo_url in self.config.get("repositories", []):
                logger.warning(f"Repository {repo_url} ist bereits in der Konfiguration")
                return False
            
            # Füge das Repository zur Konfiguration hinzu
            if "repositories" not in self.config:
                self.config["repositories"] = []
            self.config["repositories"].append(repo_url)
            
            # Speichere die Konfiguration
            self._save_config()
            
            # Aktualisiere die Registry
            self.registry.add_repository(repo_url)
            
            return True
        except Exception as e:
            logger.exception(f"Fehler beim Hinzufügen des Repositories {repo_url}: {e}")
            return False

    def remove_repository(self, repo_url: str) -> bool:
        """
        Entferne ein Repository aus der Konfiguration.

        Args:
            repo_url: Die URL des Repositories

        Returns:
            True, wenn das Repository entfernt wurde, sonst False
        """
        try:
            # Prüfe, ob das Repository in der Konfiguration ist
            if repo_url not in self.config.get("repositories", []):
                logger.warning(f"Repository {repo_url} ist nicht in der Konfiguration")
                return False
            
            # Entferne das Repository aus der Konfiguration
            self.config["repositories"].remove(repo_url)
            
            # Speichere die Konfiguration
            self._save_config()
            
            # Aktualisiere die Registry
            self.registry.remove_repository(repo_url)
            
            return True
        except Exception as e:
            logger.exception(f"Fehler beim Entfernen des Repositories {repo_url}: {e}")
            return False

    def add_docker_hub_user(self, username: str) -> bool:
        """
        Füge einen Docker Hub Benutzer zur Konfiguration hinzu.

        Args:
            username: Der Benutzername

        Returns:
            True, wenn der Benutzer hinzugefügt wurde, sonst False
        """
        try:
            # Prüfe, ob der Benutzer bereits in der Konfiguration ist
            if username in self.config.get("docker_hub_users", []):
                logger.warning(f"Docker Hub Benutzer {username} ist bereits in der Konfiguration")
                return False
            
            # Füge den Benutzer zur Konfiguration hinzu
            if "docker_hub_users" not in self.config:
                self.config["docker_hub_users"] = []
            self.config["docker_hub_users"].append(username)
            
            # Speichere die Konfiguration
            self._save_config()
            
            # Aktualisiere die Registry
            self.registry.add_docker_hub_user(username)
            
            return True
        except Exception as e:
            logger.exception(f"Fehler beim Hinzufügen des Docker Hub Benutzers {username}: {e}")
            return False

    def remove_docker_hub_user(self, username: str) -> bool:
        """
        Entferne einen Docker Hub Benutzer aus der Konfiguration.

        Args:
            username: Der Benutzername

        Returns:
            True, wenn der Benutzer entfernt wurde, sonst False
        """
        try:
            # Prüfe, ob der Benutzer in der Konfiguration ist
            if username not in self.config.get("docker_hub_users", []):
                logger.warning(f"Docker Hub Benutzer {username} ist nicht in der Konfiguration")
                return False
            
            # Entferne den Benutzer aus der Konfiguration
            self.config["docker_hub_users"].remove(username)
            
            # Speichere die Konfiguration
            self._save_config()
            
            # Aktualisiere die Registry
            self.registry.remove_docker_hub_user(username)
            
            return True
        except Exception as e:
            logger.exception(f"Fehler beim Entfernen des Docker Hub Benutzers {username}: {e}")
            return False