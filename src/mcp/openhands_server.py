#!/usr/bin/env python3
"""
OpenHands MCP-Server für die parallele Ausführung von Aufgaben.

Dieser MCP-Server ermöglicht es, mehrere OpenHands-Agenten parallel zu laden und
Aufgaben parallel auszuführen.
"""

import os
import sys
import json
import uuid
import logging
import asyncio
import argparse
import threading
import concurrent.futures
from typing import Dict, List, Any, Optional, Union, Tuple

# Füge das Stammverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.openhands.agent import OpenHandsAgent

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('openhands-mcp-server')


class OpenHandsMCPServer:
    """
    MCP-Server für die parallele Ausführung von OpenHands-Aufgaben.
    
    Diese Klasse bietet Methoden zur Verwaltung von OpenHands-Agenten und zur
    parallelen Ausführung von Aufgaben.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 3006, max_workers: int = 5):
        """
        Initialisiere den OpenHands MCP-Server.
        
        Args:
            host: Host für den MCP-Server
            port: Port für den MCP-Server
            max_workers: Maximale Anzahl von Worker-Threads
        """
        self.host = host
        self.port = port
        self.max_workers = max_workers
        
        # Initialisiere den Thread-Pool
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        # Initialisiere die Agenten
        self.agents = {}
        
        # Initialisiere die Aufgaben
        self.tasks = {}
        
        # Definiere die verfügbaren Funktionen
        self.functions = [
            {
                "name": "create_agent",
                "description": "Erstellt einen neuen OpenHands-Agenten",
                "parameters": {
                    "config_file": {
                        "type": "string",
                        "description": "Pfad zur Konfigurationsdatei"
                    }
                }
            },
            {
                "name": "get_agent",
                "description": "Ruft einen OpenHands-Agenten ab",
                "parameters": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID des Agenten"
                    }
                }
            },
            {
                "name": "delete_agent",
                "description": "Löscht einen OpenHands-Agenten",
                "parameters": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID des Agenten"
                    }
                }
            },
            {
                "name": "execute_task",
                "description": "Führt eine Aufgabe mit einem OpenHands-Agenten aus",
                "parameters": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID des Agenten"
                    },
                    "task": {
                        "type": "string",
                        "description": "Beschreibung der Aufgabe"
                    },
                    "context": {
                        "type": "object",
                        "description": "Kontext für die Aufgabe"
                    }
                }
            },
            {
                "name": "execute_mcp_task",
                "description": "Führt eine MCP-Aufgabe mit einem OpenHands-Agenten aus",
                "parameters": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID des Agenten"
                    },
                    "task": {
                        "type": "string",
                        "description": "Beschreibung der Aufgabe"
                    },
                    "server_name": {
                        "type": "string",
                        "description": "Name des MCP-Servers"
                    },
                    "function_name": {
                        "type": "string",
                        "description": "Name der Funktion"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameter für die Funktion"
                    }
                }
            },
            {
                "name": "get_task_status",
                "description": "Ruft den Status einer Aufgabe ab",
                "parameters": {
                    "task_id": {
                        "type": "string",
                        "description": "ID der Aufgabe"
                    }
                }
            },
            {
                "name": "get_task_result",
                "description": "Ruft das Ergebnis einer Aufgabe ab",
                "parameters": {
                    "task_id": {
                        "type": "string",
                        "description": "ID der Aufgabe"
                    }
                }
            },
            {
                "name": "cancel_task",
                "description": "Bricht eine Aufgabe ab",
                "parameters": {
                    "task_id": {
                        "type": "string",
                        "description": "ID der Aufgabe"
                    }
                }
            },
            {
                "name": "execute_parallel_tasks",
                "description": "Führt mehrere Aufgaben parallel aus",
                "parameters": {
                    "tasks": {
                        "type": "array",
                        "description": "Liste von Aufgaben"
                    }
                }
            }
        ]
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Rufe Informationen über den MCP-Server ab.
        
        Returns:
            Dict mit Serverinformationen
        """
        return {
            "name": "openhands-mcp-server",
            "version": "1.0.0",
            "description": "MCP-Server für die parallele Ausführung von OpenHands-Aufgaben",
            "status": "online",
            "max_workers": self.max_workers,
            "active_agents": len(self.agents),
            "active_tasks": len(self.tasks)
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
    
    def _create_agent(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstelle einen neuen OpenHands-Agenten.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem erstellten Agenten
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        config_file = parameters.get("config_file")
        
        try:
            # Erstelle einen neuen Agenten
            agent = OpenHandsAgent(config_file)
            
            # Generiere eine ID für den Agenten
            agent_id = str(uuid.uuid4())
            
            # Speichere den Agenten
            self.agents[agent_id] = agent
            
            return {
                "agent_id": agent_id,
                "config_file": config_file,
                "api_available": agent.api_available
            }
        except Exception as e:
            logger.error(f"Fehler bei der Erstellung des Agenten: {e}")
            raise
    
    def _get_agent(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe einen OpenHands-Agenten ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Agenten
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        agent_id = parameters.get("agent_id")
        if not agent_id:
            raise Exception("Parameter agent_id fehlt")
        
        if agent_id not in self.agents:
            raise Exception(f"Agent {agent_id} nicht gefunden")
        
        agent = self.agents[agent_id]
        
        return {
            "agent_id": agent_id,
            "api_available": agent.api_available,
            "config": agent.config
        }
    
    def _delete_agent(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lösche einen OpenHands-Agenten.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Löschung
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        agent_id = parameters.get("agent_id")
        if not agent_id:
            raise Exception("Parameter agent_id fehlt")
        
        if agent_id not in self.agents:
            raise Exception(f"Agent {agent_id} nicht gefunden")
        
        # Lösche den Agenten
        del self.agents[agent_id]
        
        return {
            "success": True,
            "message": f"Agent {agent_id} erfolgreich gelöscht"
        }
    
    def _execute_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führe eine Aufgabe mit einem OpenHands-Agenten aus.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Aufgabe
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        agent_id = parameters.get("agent_id")
        if not agent_id:
            raise Exception("Parameter agent_id fehlt")
        
        task = parameters.get("task")
        if not task:
            raise Exception("Parameter task fehlt")
        
        context = parameters.get("context")
        
        if agent_id not in self.agents:
            raise Exception(f"Agent {agent_id} nicht gefunden")
        
        agent = self.agents[agent_id]
        
        # Generiere eine ID für die Aufgabe
        task_id = str(uuid.uuid4())
        
        # Erstelle einen Future für die Aufgabe
        future = self.executor.submit(agent.execute_task, task, context)
        
        # Speichere die Aufgabe
        self.tasks[task_id] = {
            "future": future,
            "agent_id": agent_id,
            "task": task,
            "context": context,
            "status": "running",
            "result": None
        }
        
        # Füge einen Callback hinzu, um den Status zu aktualisieren
        def update_status(future):
            try:
                result = future.result()
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["result"] = result
            except Exception as e:
                self.tasks[task_id]["status"] = "failed"
                self.tasks[task_id]["result"] = {"error": str(e)}
        
        future.add_done_callback(update_status)
        
        return {
            "task_id": task_id,
            "status": "running"
        }
    
    def _execute_mcp_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führe eine MCP-Aufgabe mit einem OpenHands-Agenten aus.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Aufgabe
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        agent_id = parameters.get("agent_id")
        if not agent_id:
            raise Exception("Parameter agent_id fehlt")
        
        task = parameters.get("task")
        if not task:
            raise Exception("Parameter task fehlt")
        
        server_name = parameters.get("server_name")
        if not server_name:
            raise Exception("Parameter server_name fehlt")
        
        function_name = parameters.get("function_name")
        if not function_name:
            raise Exception("Parameter function_name fehlt")
        
        function_parameters = parameters.get("parameters", {})
        
        if agent_id not in self.agents:
            raise Exception(f"Agent {agent_id} nicht gefunden")
        
        agent = self.agents[agent_id]
        
        # Generiere eine ID für die Aufgabe
        task_id = str(uuid.uuid4())
        
        # Erstelle einen Future für die Aufgabe
        future = self.executor.submit(
            agent.execute_mcp_task,
            task,
            server_name,
            function_name,
            function_parameters
        )
        
        # Speichere die Aufgabe
        self.tasks[task_id] = {
            "future": future,
            "agent_id": agent_id,
            "task": task,
            "server_name": server_name,
            "function_name": function_name,
            "parameters": function_parameters,
            "status": "running",
            "result": None
        }
        
        # Füge einen Callback hinzu, um den Status zu aktualisieren
        def update_status(future):
            try:
                result = future.result()
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["result"] = result
            except Exception as e:
                self.tasks[task_id]["status"] = "failed"
                self.tasks[task_id]["result"] = {"error": str(e)}
        
        future.add_done_callback(update_status)
        
        return {
            "task_id": task_id,
            "status": "running"
        }
    
    def _get_task_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe den Status einer Aufgabe ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Status der Aufgabe
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        task_id = parameters.get("task_id")
        if not task_id:
            raise Exception("Parameter task_id fehlt")
        
        if task_id not in self.tasks:
            raise Exception(f"Aufgabe {task_id} nicht gefunden")
        
        task = self.tasks[task_id]
        
        return {
            "task_id": task_id,
            "status": task["status"]
        }
    
    def _get_task_result(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe das Ergebnis einer Aufgabe ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Aufgabe
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        task_id = parameters.get("task_id")
        if not task_id:
            raise Exception("Parameter task_id fehlt")
        
        if task_id not in self.tasks:
            raise Exception(f"Aufgabe {task_id} nicht gefunden")
        
        task = self.tasks[task_id]
        
        if task["status"] == "running":
            return {
                "task_id": task_id,
                "status": "running",
                "message": "Aufgabe wird noch ausgeführt"
            }
        
        return {
            "task_id": task_id,
            "status": task["status"],
            "result": task["result"]
        }
    
    def _cancel_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bricht eine Aufgabe ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis des Abbruchs
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        task_id = parameters.get("task_id")
        if not task_id:
            raise Exception("Parameter task_id fehlt")
        
        if task_id not in self.tasks:
            raise Exception(f"Aufgabe {task_id} nicht gefunden")
        
        task = self.tasks[task_id]
        
        if task["status"] != "running":
            return {
                "task_id": task_id,
                "status": task["status"],
                "message": "Aufgabe ist bereits abgeschlossen oder fehlgeschlagen"
            }
        
        # Brich die Aufgabe ab
        task["future"].cancel()
        task["status"] = "cancelled"
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Aufgabe erfolgreich abgebrochen"
        }
    
    def _execute_parallel_tasks(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führe mehrere Aufgaben parallel aus.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit den Ergebnissen der Aufgaben
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        tasks = parameters.get("tasks")
        if not tasks:
            raise Exception("Parameter tasks fehlt")
        
        if not isinstance(tasks, list):
            raise Exception("Parameter tasks muss eine Liste sein")
        
        # Führe die Aufgaben aus
        task_ids = []
        for task_params in tasks:
            task_type = task_params.get("type")
            if not task_type:
                raise Exception("Parameter type fehlt in einer Aufgabe")
            
            if task_type == "execute_task":
                result = self._execute_task(task_params)
            elif task_type == "execute_mcp_task":
                result = self._execute_mcp_task(task_params)
            else:
                raise Exception(f"Unbekannter Aufgabentyp: {task_type}")
            
            task_ids.append(result["task_id"])
        
        return {
            "task_ids": task_ids,
            "status": "running"
        }
    
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
    parser = argparse.ArgumentParser(description='OpenHands MCP-Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host für den MCP-Server')
    parser.add_argument('--port', type=int, default=3006, help='Port für den MCP-Server')
    parser.add_argument('--max-workers', type=int, default=5, help='Maximale Anzahl von Worker-Threads')
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
    
    # Starte den MCP-Server
    server = OpenHandsMCPServer(args.host, args.port, args.max_workers)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())