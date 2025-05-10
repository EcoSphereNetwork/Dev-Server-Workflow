"""
OpenHands Agent Integration für das Dev-Server-Workflow-Projekt.

Dieses Modul bietet eine Integration mit OpenHands, die es ermöglicht, OpenHands
als allgemeinen KI-Agenten zu verwenden, der verschiedene Aufgaben übernehmen kann.
"""

import os
import sys
import json
import logging
import requests
import subprocess
from typing import Dict, List, Any, Optional, Union, Tuple, Callable

from ..common.config_manager import get_config_manager, ConfigValidationError
from ..mcp.client import MCPClient, MCPClientManager

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('openhands-agent')


class OpenHandsAgent:
    """
    OpenHands Agent für die Integration mit dem Dev-Server-Workflow-Projekt.
    
    Diese Klasse bietet Methoden zur Interaktion mit OpenHands und zur Ausführung
    von Aufgaben mit OpenHands als KI-Agent.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialisiere den OpenHands Agent.
        
        Args:
            config_file: Pfad zur Konfigurationsdatei
        """
        self.config_manager = get_config_manager()
        
        # Standardkonfiguration
        default_config = {
            "openhands": {
                "api_url": "http://localhost:8000",
                "api_key": "",
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 4000,
                "timeout": 60,
                "mcp_servers": [
                    {
                        "name": "filesystem",
                        "url": "http://localhost:3001",
                        "description": "File system operations"
                    },
                    {
                        "name": "desktop-commander",
                        "url": "http://localhost:3002",
                        "description": "Terminal command execution"
                    },
                    {
                        "name": "sequential-thinking",
                        "url": "http://localhost:3003",
                        "description": "Sequential thinking for complex tasks"
                    },
                    {
                        "name": "github-chat",
                        "url": "http://localhost:3004",
                        "description": "GitHub discussions and comments"
                    },
                    {
                        "name": "github",
                        "url": "http://localhost:3005",
                        "description": "GitHub repository operations"
                    },
                    {
                        "name": "n8n",
                        "url": "http://localhost:3000",
                        "description": "n8n workflow operations"
                    }
                ],
                "default_system_prompt": "You are OpenHands, a helpful AI assistant that can interact with various systems through MCP servers. You can help with file operations, terminal commands, GitHub operations, and more."
            }
        }
        
        # Lade Konfiguration
        if config_file:
            try:
                self.config = self.config_manager.load_json_config(config_file, default_config)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Konfigurationsdatei {config_file}: {e}")
                self.config = default_config
        else:
            # Versuche, die Konfiguration aus der Standarddatei zu laden
            try:
                self.config = self.config_manager.load_json_config("openhands", default_config)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Standardkonfigurationsdatei: {e}")
                self.config = default_config
        
        # Initialisiere MCP-Client-Manager
        self.mcp_client_manager = MCPClientManager(self.config["openhands"]["mcp_servers"])
        
        # Überprüfe, ob die OpenHands API erreichbar ist
        self.api_available = self._check_api_availability()
    
    def _check_api_availability(self) -> bool:
        """
        Überprüfe, ob die OpenHands API erreichbar ist.
        
        Returns:
            True, wenn die API erreichbar ist, sonst False
        """
        try:
            response = requests.get(
                f"{self.config['openhands']['api_url']}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"OpenHands API nicht erreichbar: {e}")
            return False
    
    def execute_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Führe eine Aufgabe mit OpenHands aus.
        
        Args:
            task: Beschreibung der Aufgabe
            context: Kontext für die Aufgabe
            
        Returns:
            Dict mit dem Ergebnis der Aufgabe
            
        Raises:
            Exception: Wenn die Aufgabe nicht ausgeführt werden konnte
        """
        if not self.api_available:
            raise Exception("OpenHands API nicht erreichbar")
        
        # Bereite die Anfrage vor
        request_data = {
            "model": self.config["openhands"]["model"],
            "temperature": self.config["openhands"]["temperature"],
            "max_tokens": self.config["openhands"]["max_tokens"],
            "messages": [
                {
                    "role": "system",
                    "content": self.config["openhands"]["default_system_prompt"]
                },
                {
                    "role": "user",
                    "content": task
                }
            ]
        }
        
        # Füge Kontext hinzu, falls vorhanden
        if context:
            request_data["context"] = context
        
        # Sende die Anfrage an die OpenHands API
        try:
            response = requests.post(
                f"{self.config['openhands']['api_url']}/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.config['openhands']['api_key']}"
                },
                json=request_data,
                timeout=self.config["openhands"]["timeout"]
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler bei der Anfrage an die OpenHands API: {response.text}")
            
            return response.json()
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung der Aufgabe: {e}")
            raise
    
    def execute_mcp_task(self, task: str, server_name: str, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führe eine MCP-Aufgabe mit OpenHands aus.
        
        Args:
            task: Beschreibung der Aufgabe
            server_name: Name des MCP-Servers
            function_name: Name der Funktion
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Aufgabe
            
        Raises:
            Exception: Wenn die Aufgabe nicht ausgeführt werden konnte
        """
        # Hole den MCP-Client
        client = self.mcp_client_manager.get_client(server_name)
        if not client:
            raise Exception(f"MCP-Server {server_name} nicht gefunden")
        
        # Führe die Funktion aus
        try:
            result = client.call_function(function_name, parameters)
            
            # Bereite den Kontext für OpenHands vor
            context = {
                "mcp_result": result,
                "mcp_server": server_name,
                "mcp_function": function_name,
                "mcp_parameters": parameters
            }
            
            # Führe die Aufgabe mit OpenHands aus
            return self.execute_task(task, context)
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung der MCP-Aufgabe: {e}")
            raise
    
    def manage_workflow(self, workflow_name: str, action: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verwalte einen n8n-Workflow mit OpenHands.
        
        Args:
            workflow_name: Name des Workflows
            action: Aktion, die ausgeführt werden soll (start, stop, update, etc.)
            parameters: Parameter für die Aktion
            
        Returns:
            Dict mit dem Ergebnis der Aktion
            
        Raises:
            Exception: Wenn die Aktion nicht ausgeführt werden konnte
        """
        # Hole den MCP-Client für n8n
        client = self.mcp_client_manager.get_client("n8n")
        if not client:
            raise Exception("n8n MCP-Server nicht gefunden")
        
        # Bereite die Parameter vor
        mcp_parameters = {
            "workflow_name": workflow_name,
            "action": action
        }
        
        if parameters:
            mcp_parameters["parameters"] = parameters
        
        # Führe die Funktion aus
        try:
            result = client.call_function("manage_workflow", mcp_parameters)
            
            # Bereite den Kontext für OpenHands vor
            context = {
                "workflow_name": workflow_name,
                "action": action,
                "parameters": parameters,
                "result": result
            }
            
            # Führe die Aufgabe mit OpenHands aus
            task = f"Verwalte den n8n-Workflow '{workflow_name}' mit der Aktion '{action}'."
            return self.execute_task(task, context)
        except Exception as e:
            logger.error(f"Fehler bei der Verwaltung des Workflows: {e}")
            raise
    
    def manage_github_repository(self, repository: str, action: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verwalte ein GitHub-Repository mit OpenHands.
        
        Args:
            repository: Name des Repositories
            action: Aktion, die ausgeführt werden soll (clone, pull, push, etc.)
            parameters: Parameter für die Aktion
            
        Returns:
            Dict mit dem Ergebnis der Aktion
            
        Raises:
            Exception: Wenn die Aktion nicht ausgeführt werden konnte
        """
        # Hole den MCP-Client für GitHub
        client = self.mcp_client_manager.get_client("github")
        if not client:
            raise Exception("GitHub MCP-Server nicht gefunden")
        
        # Bereite die Parameter vor
        mcp_parameters = {
            "repository": repository,
            "action": action
        }
        
        if parameters:
            mcp_parameters["parameters"] = parameters
        
        # Führe die Funktion aus
        try:
            result = client.call_function("manage_repository", mcp_parameters)
            
            # Bereite den Kontext für OpenHands vor
            context = {
                "repository": repository,
                "action": action,
                "parameters": parameters,
                "result": result
            }
            
            # Führe die Aufgabe mit OpenHands aus
            task = f"Verwalte das GitHub-Repository '{repository}' mit der Aktion '{action}'."
            return self.execute_task(task, context)
        except Exception as e:
            logger.error(f"Fehler bei der Verwaltung des Repositories: {e}")
            raise
    
    def execute_command(self, command: str, working_directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Führe einen Befehl mit OpenHands aus.
        
        Args:
            command: Befehl, der ausgeführt werden soll
            working_directory: Arbeitsverzeichnis für den Befehl
            
        Returns:
            Dict mit dem Ergebnis des Befehls
            
        Raises:
            Exception: Wenn der Befehl nicht ausgeführt werden konnte
        """
        # Hole den MCP-Client für Desktop Commander
        client = self.mcp_client_manager.get_client("desktop-commander")
        if not client:
            raise Exception("Desktop Commander MCP-Server nicht gefunden")
        
        # Bereite die Parameter vor
        mcp_parameters = {
            "command": command
        }
        
        if working_directory:
            mcp_parameters["working_directory"] = working_directory
        
        # Führe die Funktion aus
        try:
            result = client.call_function("execute_command", mcp_parameters)
            
            # Bereite den Kontext für OpenHands vor
            context = {
                "command": command,
                "working_directory": working_directory,
                "result": result
            }
            
            # Führe die Aufgabe mit OpenHands aus
            task = f"Führe den Befehl '{command}' aus und analysiere das Ergebnis."
            return self.execute_task(task, context)
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung des Befehls: {e}")
            raise
    
    def manage_files(self, action: str, path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Verwalte Dateien mit OpenHands.
        
        Args:
            action: Aktion, die ausgeführt werden soll (read, write, delete, etc.)
            path: Pfad zur Datei
            content: Inhalt für die Datei (bei write)
            
        Returns:
            Dict mit dem Ergebnis der Aktion
            
        Raises:
            Exception: Wenn die Aktion nicht ausgeführt werden konnte
        """
        # Hole den MCP-Client für Filesystem
        client = self.mcp_client_manager.get_client("filesystem")
        if not client:
            raise Exception("Filesystem MCP-Server nicht gefunden")
        
        # Bereite die Parameter vor
        mcp_parameters = {
            "path": path
        }
        
        if content is not None:
            mcp_parameters["content"] = content
        
        # Führe die Funktion aus
        try:
            result = client.call_function(action, mcp_parameters)
            
            # Bereite den Kontext für OpenHands vor
            context = {
                "action": action,
                "path": path,
                "content": content,
                "result": result
            }
            
            # Führe die Aufgabe mit OpenHands aus
            task = f"Führe die Dateiaktion '{action}' für '{path}' aus und analysiere das Ergebnis."
            return self.execute_task(task, context)
        except Exception as e:
            logger.error(f"Fehler bei der Verwaltung der Datei: {e}")
            raise
    
    def solve_complex_task(self, task: str, steps: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Löse eine komplexe Aufgabe mit OpenHands.
        
        Args:
            task: Beschreibung der Aufgabe
            steps: Schritte für die Lösung der Aufgabe
            
        Returns:
            Dict mit dem Ergebnis der Aufgabe
            
        Raises:
            Exception: Wenn die Aufgabe nicht gelöst werden konnte
        """
        # Hole den MCP-Client für Sequential Thinking
        client = self.mcp_client_manager.get_client("sequential-thinking")
        if not client:
            raise Exception("Sequential Thinking MCP-Server nicht gefunden")
        
        # Bereite die Parameter vor
        mcp_parameters = {
            "task": task
        }
        
        if steps:
            mcp_parameters["steps"] = steps
        
        # Führe die Funktion aus
        try:
            result = client.call_function("solve_task", mcp_parameters)
            
            # Bereite den Kontext für OpenHands vor
            context = {
                "task": task,
                "steps": steps,
                "result": result
            }
            
            # Führe die Aufgabe mit OpenHands aus
            return self.execute_task(task, context)
        except Exception as e:
            logger.error(f"Fehler bei der Lösung der komplexen Aufgabe: {e}")
            raise
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Aktualisiere die Konfiguration.
        
        Args:
            updates: Aktualisierungen für die Konfiguration
        """
        self.config_manager.update_config("openhands", updates)
        self.config = self.config_manager.get_config("openhands")
        
        # Aktualisiere MCP-Client-Manager
        self.mcp_client_manager = MCPClientManager(self.config["openhands"]["mcp_servers"])
        
        # Überprüfe, ob die OpenHands API erreichbar ist
        self.api_available = self._check_api_availability()
    
    def save_config(self) -> None:
        """
        Speichere die Konfiguration.
        """
        self.config_manager.save_json_config("openhands", self.config)


# Singleton-Instanz des OpenHands Agents
_openhands_agent = None


def get_openhands_agent(config_file: Optional[str] = None) -> OpenHandsAgent:
    """
    Hole die Singleton-Instanz des OpenHands Agents.
    
    Args:
        config_file: Pfad zur Konfigurationsdatei
        
    Returns:
        Singleton-Instanz des OpenHands Agents
    """
    global _openhands_agent
    
    if _openhands_agent is None:
        _openhands_agent = OpenHandsAgent(config_file)
    
    return _openhands_agent