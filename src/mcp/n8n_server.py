#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Konfiguriere Logging
logger = setup_logging("INFO")

# Lade Konfiguration
config_manager = ConfigManager()
config = config_manager.load_env_file(".env")

"""
n8n MCP-Server für die Integration mit OpenHands.

Dieser MCP-Server ermöglicht es OpenHands, n8n-Workflows zu verwalten und auszuführen.
"""

import os
import sys
import json
import logging
import asyncio
import argparse
import requests
from typing import Dict, List, Any, Optional, Union, Tuple

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('n8n-mcp-server')


class N8nMCPServer:
    """
    MCP-Server für die Integration mit n8n.
    
    Diese Klasse bietet Methoden zur Verwaltung und Ausführung von n8n-Workflows.
    """
    
    def __init__(self, n8n_url: str, api_key: str, host: str = "0.0.0.0", port: int = 3000):
        """
        Initialisiere den n8n MCP-Server.
        
        Args:
            n8n_url: URL der n8n-Instanz
            api_key: API-Schlüssel für n8n
            host: Host für den MCP-Server
            port: Port für den MCP-Server
        """
        self.n8n_url = n8n_url
        self.api_key = api_key
        self.host = host
        self.port = port
        
        # Überprüfe, ob n8n erreichbar ist
        self.n8n_available = self._check_n8n_availability()
        
        # Definiere die verfügbaren Funktionen
        self.functions = [
            {
                "name": "get_workflows",
                "description": "Ruft alle Workflows ab",
                "parameters": {}
            },
            {
                "name": "get_workflow",
                "description": "Ruft einen Workflow ab",
                "parameters": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID des Workflows"
                    }
                }
            },
            {
                "name": "execute_workflow",
                "description": "Führt einen Workflow aus",
                "parameters": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID des Workflows"
                    },
                    "data": {
                        "type": "object",
                        "description": "Daten für den Workflow"
                    }
                }
            },
            {
                "name": "activate_workflow",
                "description": "Aktiviert einen Workflow",
                "parameters": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID des Workflows"
                    }
                }
            },
            {
                "name": "deactivate_workflow",
                "description": "Deaktiviert einen Workflow",
                "parameters": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID des Workflows"
                    }
                }
            },
            {
                "name": "create_workflow",
                "description": "Erstellt einen neuen Workflow",
                "parameters": {
                    "name": {
                        "type": "string",
                        "description": "Name des Workflows"
                    },
                    "nodes": {
                        "type": "array",
                        "description": "Knoten des Workflows"
                    },
                    "connections": {
                        "type": "object",
                        "description": "Verbindungen des Workflows"
                    },
                    "active": {
                        "type": "boolean",
                        "description": "Ob der Workflow aktiv sein soll"
                    }
                }
            },
            {
                "name": "update_workflow",
                "description": "Aktualisiert einen Workflow",
                "parameters": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID des Workflows"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name des Workflows"
                    },
                    "nodes": {
                        "type": "array",
                        "description": "Knoten des Workflows"
                    },
                    "connections": {
                        "type": "object",
                        "description": "Verbindungen des Workflows"
                    },
                    "active": {
                        "type": "boolean",
                        "description": "Ob der Workflow aktiv sein soll"
                    }
                }
            },
            {
                "name": "delete_workflow",
                "description": "Löscht einen Workflow",
                "parameters": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID des Workflows"
                    }
                }
            },
            {
                "name": "get_executions",
                "description": "Ruft alle Ausführungen ab",
                "parameters": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID des Workflows"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximale Anzahl von Ausführungen"
                    }
                }
            },
            {
                "name": "get_execution",
                "description": "Ruft eine Ausführung ab",
                "parameters": {
                    "execution_id": {
                        "type": "string",
                        "description": "ID der Ausführung"
                    }
                }
            },
            {
                "name": "manage_workflow",
                "description": "Verwaltet einen Workflow",
                "parameters": {
                    "workflow_name": {
                        "type": "string",
                        "description": "Name des Workflows"
                    },
                    "action": {
                        "type": "string",
                        "description": "Aktion, die ausgeführt werden soll (start, stop, update, etc.)"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameter für die Aktion"
                    }
                }
            }
        ]
    
    def _check_n8n_availability(self) -> bool:
        """
        Überprüfe, ob n8n erreichbar ist.
        
        Returns:
            True, wenn n8n erreichbar ist, sonst False
        """
        try:
            response = requests.get(
                f"{self.n8n_url}/healthz",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"n8n nicht erreichbar: {e}")
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Rufe Informationen über den MCP-Server ab.
        
        Returns:
            Dict mit Serverinformationen
        """
        return {
            "name": "n8n-mcp-server",
            "version": "1.0.0",
            "description": "MCP-Server für die Integration mit n8n",
            "status": "online" if self.n8n_available else "offline",
            "n8n_url": self.n8n_url,
            "n8n_available": self.n8n_available
        }
    
    def get_functions(self) -> List[Dict[str, Any]]:
        """
        Rufe die verfügbaren Funktionen ab.
        
        Returns:
            Liste mit Funktionsinformationen
        """
        return self.functions
    
    def call_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe eine Funktion auf.
        
        Args:
            function_name: Name der Funktion
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Funktion
            
        Raises:
            Exception: Wenn die Funktion nicht gefunden wurde oder ein Fehler auftrat
        """
        if not self.n8n_available:
            raise Exception("n8n nicht erreichbar")
        
        # Überprüfe, ob die Funktion existiert
        function = next((f for f in self.functions if f["name"] == function_name), None)
        if not function:
            raise Exception(f"Funktion {function_name} nicht gefunden")
        
        # Rufe die entsprechende Methode auf
        method_name = f"_{function_name}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(parameters)
        else:
            raise Exception(f"Methode {method_name} nicht implementiert")
    
    def _get_workflows(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe alle Workflows ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit den Workflows
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        try:
            response = requests.get(
                f"{self.n8n_url}/rest/workflows",
                headers={
                    "X-N8N-API-KEY": self.api_key
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler beim Abrufen der Workflows: {response.text}")
            
            return {
                "workflows": response.json()["data"]
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Workflows: {e}")
            raise
    
    def _get_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe einen Workflow ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Workflow
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        workflow_id = parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("Parameter workflow_id fehlt")
        
        try:
            response = requests.get(
                f"{self.n8n_url}/rest/workflows/{workflow_id}",
                headers={
                    "X-N8N-API-KEY": self.api_key
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler beim Abrufen des Workflows: {response.text}")
            
            return {
                "workflow": response.json()["data"]
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Workflows: {e}")
            raise
    
    def _execute_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führe einen Workflow aus.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Ausführung
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        workflow_id = parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("Parameter workflow_id fehlt")
        
        data = parameters.get("data", {})
        
        try:
            response = requests.post(
                f"{self.n8n_url}/rest/workflows/{workflow_id}/execute",
                headers={
                    "X-N8N-API-KEY": self.api_key
                },
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler bei der Ausführung des Workflows: {response.text}")
            
            return {
                "execution": response.json()["data"]
            }
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung des Workflows: {e}")
            raise
    
    def _activate_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktiviere einen Workflow.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Aktivierung
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        workflow_id = parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("Parameter workflow_id fehlt")
        
        try:
            response = requests.post(
                f"{self.n8n_url}/rest/workflows/{workflow_id}/activate",
                headers={
                    "X-N8N-API-KEY": self.api_key
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler bei der Aktivierung des Workflows: {response.text}")
            
            return {
                "success": True,
                "message": "Workflow erfolgreich aktiviert"
            }
        except Exception as e:
            logger.error(f"Fehler bei der Aktivierung des Workflows: {e}")
            raise
    
    def _deactivate_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deaktiviere einen Workflow.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Deaktivierung
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        workflow_id = parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("Parameter workflow_id fehlt")
        
        try:
            response = requests.post(
                f"{self.n8n_url}/rest/workflows/{workflow_id}/deactivate",
                headers={
                    "X-N8N-API-KEY": self.api_key
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler bei der Deaktivierung des Workflows: {response.text}")
            
            return {
                "success": True,
                "message": "Workflow erfolgreich deaktiviert"
            }
        except Exception as e:
            logger.error(f"Fehler bei der Deaktivierung des Workflows: {e}")
            raise
    
    def _create_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstelle einen neuen Workflow.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem erstellten Workflow
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        name = parameters.get("name")
        if not name:
            raise Exception("Parameter name fehlt")
        
        nodes = parameters.get("nodes", [])
        connections = parameters.get("connections", {})
        active = parameters.get("active", False)
        
        try:
            response = requests.post(
                f"{self.n8n_url}/rest/workflows",
                headers={
                    "X-N8N-API-KEY": self.api_key
                },
                json={
                    "name": name,
                    "nodes": nodes,
                    "connections": connections,
                    "active": active
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler bei der Erstellung des Workflows: {response.text}")
            
            return {
                "workflow": response.json()["data"]
            }
        except Exception as e:
            logger.error(f"Fehler bei der Erstellung des Workflows: {e}")
            raise
    
    def _update_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktualisiere einen Workflow.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem aktualisierten Workflow
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        workflow_id = parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("Parameter workflow_id fehlt")
        
        name = parameters.get("name")
        nodes = parameters.get("nodes")
        connections = parameters.get("connections")
        active = parameters.get("active")
        
        # Hole den aktuellen Workflow
        try:
            response = requests.get(
                f"{self.n8n_url}/rest/workflows/{workflow_id}",
                headers={
                    "X-N8N-API-KEY": self.api_key
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler beim Abrufen des Workflows: {response.text}")
            
            workflow = response.json()["data"]
            
            # Aktualisiere die Felder
            if name:
                workflow["name"] = name
            if nodes:
                workflow["nodes"] = nodes
            if connections:
                workflow["connections"] = connections
            if active is not None:
                workflow["active"] = active
            
            # Aktualisiere den Workflow
            response = requests.put(
                f"{self.n8n_url}/rest/workflows/{workflow_id}",
                headers={
                    "X-N8N-API-KEY": self.api_key
                },
                json=workflow
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler bei der Aktualisierung des Workflows: {response.text}")
            
            return {
                "workflow": response.json()["data"]
            }
        except Exception as e:
            logger.error(f"Fehler bei der Aktualisierung des Workflows: {e}")
            raise
    
    def _delete_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lösche einen Workflow.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Löschung
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        workflow_id = parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("Parameter workflow_id fehlt")
        
        try:
            response = requests.delete(
                f"{self.n8n_url}/rest/workflows/{workflow_id}",
                headers={
                    "X-N8N-API-KEY": self.api_key
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler bei der Löschung des Workflows: {response.text}")
            
            return {
                "success": True,
                "message": "Workflow erfolgreich gelöscht"
            }
        except Exception as e:
            logger.error(f"Fehler bei der Löschung des Workflows: {e}")
            raise
    
    def _get_executions(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe alle Ausführungen ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit den Ausführungen
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        workflow_id = parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("Parameter workflow_id fehlt")
        
        limit = parameters.get("limit", 20)
        
        try:
            response = requests.get(
                f"{self.n8n_url}/rest/executions",
                headers={
                    "X-N8N-API-KEY": self.api_key
                },
                params={
                    "workflowId": workflow_id,
                    "limit": limit
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler beim Abrufen der Ausführungen: {response.text}")
            
            return {
                "executions": response.json()["data"]
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Ausführungen: {e}")
            raise
    
    def _get_execution(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe eine Ausführung ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit der Ausführung
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        execution_id = parameters.get("execution_id")
        if not execution_id:
            raise Exception("Parameter execution_id fehlt")
        
        try:
            response = requests.get(
                f"{self.n8n_url}/rest/executions/{execution_id}",
                headers={
                    "X-N8N-API-KEY": self.api_key
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler beim Abrufen der Ausführung: {response.text}")
            
            return {
                "execution": response.json()["data"]
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Ausführung: {e}")
            raise
    
    def _manage_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verwalte einen Workflow.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Verwaltung
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        workflow_name = parameters.get("workflow_name")
        if not workflow_name:
            raise Exception("Parameter workflow_name fehlt")
        
        action = parameters.get("action")
        if not action:
            raise Exception("Parameter action fehlt")
        
        action_parameters = parameters.get("parameters", {})
        
        # Hole alle Workflows
        try:
            response = requests.get(
                f"{self.n8n_url}/rest/workflows",
                headers={
                    "X-N8N-API-KEY": self.api_key
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Fehler beim Abrufen der Workflows: {response.text}")
            
            workflows = response.json()["data"]
            
            # Suche den Workflow mit dem angegebenen Namen
            workflow = next((w for w in workflows if w["name"] == workflow_name), None)
            if not workflow:
                raise Exception(f"Workflow {workflow_name} nicht gefunden")
            
            workflow_id = workflow["id"]
            
            # Führe die entsprechende Aktion aus
            if action == "start":
                return self._activate_workflow({"workflow_id": workflow_id})
            elif action == "stop":
                return self._deactivate_workflow({"workflow_id": workflow_id})
            elif action == "execute":
                return self._execute_workflow({
                    "workflow_id": workflow_id,
                    "data": action_parameters.get("data", {})
                })
            elif action == "update":
                return self._update_workflow({
                    "workflow_id": workflow_id,
                    "name": action_parameters.get("name"),
                    "nodes": action_parameters.get("nodes"),
                    "connections": action_parameters.get("connections"),
                    "active": action_parameters.get("active")
                })
            elif action == "delete":
                return self._delete_workflow({"workflow_id": workflow_id})
            elif action == "get":
                return self._get_workflow({"workflow_id": workflow_id})
            elif action == "get_executions":
                return self._get_executions({
                    "workflow_id": workflow_id,
                    "limit": action_parameters.get("limit", 20)
                })
            else:
                raise Exception(f"Unbekannte Aktion: {action}")
        except Exception as e:
            logger.error(f"Fehler bei der Verwaltung des Workflows: {e}")
            raise
    
    async def start(self):
        """
        Starte den MCP-Server.
        """
        server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"MCP-Server gestartet auf {addr}")
        
        async with server:
            await server.serve_forever()
    
    async def _handle_client(self, reader, writer):
        """
        Behandle eine Client-Verbindung.
        
        Args:
            reader: StreamReader für die Verbindung
            writer: StreamWriter für die Verbindung
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"Verbindung von {addr}")
        
        while True:
            try:
                # Lese eine Zeile vom Client
                data = await reader.readline()
                if not data:
                    break
                
                # Parse die Anfrage
                try:
                    request = json.loads(data.decode())
                except json.JSONDecodeError:
                    logger.error(f"Ungültige JSON-Anfrage: {data.decode()}")
                    response = {
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    writer.write(f"{json.dumps(response)}\n".encode())
                    await writer.drain()
                    continue
                
                # Verarbeite die Anfrage
                response = self._process_request(request)
                
                # Sende die Antwort
                writer.write(f"{json.dumps(response)}\n".encode())
                await writer.drain()
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung der Anfrage: {e}")
                response = {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                writer.write(f"{json.dumps(response)}\n".encode())
                await writer.drain()
                break
        
        # Schließe die Verbindung
        writer.close()
        await writer.wait_closed()
        logger.info(f"Verbindung zu {addr} geschlossen")
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeite eine Anfrage.
        
        Args:
            request: Anfrage
            
        Returns:
            Dict mit der Antwort
        """
        # Überprüfe, ob die Anfrage gültig ist
        if "method" not in request:
            return {
                "error": {
                    "code": -32600,
                    "message": "Invalid request"
                }
            }
        
        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Verarbeite die Methode
        if method == "mcp.get_server_info":
            result = self.get_server_info()
        elif method == "mcp.get_functions":
            result = self.get_functions()
        elif method == "mcp.call_function":
            function_name = params.get("function_name")
            function_params = params.get("parameters", {})
            
            if not function_name:
                return {
                    "error": {
                        "code": -32602,
                        "message": "Invalid params: function_name is required"
                    },
                    "id": request_id
                }
            
            try:
                result = self.call_function(function_name, function_params)
            except Exception as e:
                return {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    },
                    "id": request_id
                }
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": request_id
            }
        
        # Erstelle die Antwort
        response = {
            "result": result
        }
        
        if request_id is not None:
            response["id"] = request_id
        
        return response


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='n8n MCP-Server')
    parser.add_argument('--n8n-url', default='http://localhost:5678', help='URL der n8n-Instanz')
    parser.add_argument('--api-key', help='API-Schlüssel für n8n')
    parser.add_argument('--host', default='0.0.0.0', help='Host für den MCP-Server')
    parser.add_argument('--port', type=int, default=3000, help='Port für den MCP-Server')
    parser.add_argument('--verbose', '-v', action='store_true', help='Ausführliche Ausgabe')
    return parser.parse_args()


async def main():
    """
    Main function.
    """
    args = parse_args()
    
    # Setze Log-Level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Hole API-Schlüssel aus Umgebungsvariablen, falls nicht angegeben
    api_key = args.api_key or os.environ.get('N8N_API_KEY')
    if not api_key:
        logger.error("API-Schlüssel für n8n nicht angegeben")
        sys.exit(1)
    
    # Starte den MCP-Server
    server = N8nMCPServer(args.n8n_url, api_key, args.host, args.port)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())