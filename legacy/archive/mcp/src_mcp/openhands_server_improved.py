#!/usr/bin/env python3

import os
import sys
import json
import uuid
import logging
import asyncio
import argparse
import threading
import concurrent.futures
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

# Füge das Stammverzeichnis zum Pfad hinzu für OpenHands-Import
sys.path.insert(0, str(BASE_DIR))

try:
    from src.openhands.agent import OpenHandsAgent
except ImportError:
    # Mock-Klasse für den Fall, dass OpenHands nicht installiert ist
    class OpenHandsAgent:
        def __init__(self, config_file):
            self.config_file = config_file
            self.config = {}
            self.api_available = False
            
        def execute_task(self, task, context=None):
            raise NotImplementedError("OpenHands ist nicht installiert")
            
        def execute_mcp_task(self, task, server_name, function_name, parameters=None):
            raise NotImplementedError("OpenHands ist nicht installiert")


class OpenHandsMCPServer(BaseMCPServer):
    """
    MCP-Server für die parallele Ausführung von OpenHands-Aufgaben.
    
    Diese Klasse implementiert einen MCP-Server, der die parallele Ausführung
    von OpenHands-Aufgaben ermöglicht.
    """
    
    def __init__(self, max_workers: int = 5, **kwargs):
        """
        Initialisiert den OpenHands MCP-Server.
        
        Args:
            max_workers: Maximale Anzahl von Worker-Threads
            **kwargs: Weitere Argumente für die Basisklasse
        """
        super().__init__(
            name="openhands-mcp-server",
            description="MCP-Server für die parallele Ausführung von OpenHands-Aufgaben",
            version="1.1.0",
            **kwargs
        )
        
        # OpenHands-spezifische Konfiguration
        self.max_workers = max_workers
        
        # Initialisiere den Thread-Pool
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        # Initialisiere die Agenten
        self.agents = {}
        
        # Initialisiere die Aufgaben
        self.tasks = {}
    
    async def _load_tools(self):
        """
        Definiert die verfügbaren Tools für den OpenHands MCP-Server.
        """
        self.tools = [
            {
                "name": "create_agent",
                "description": "Erstellt einen neuen OpenHands-Agenten",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "config_file": {
                            "type": "string",
                            "description": "Pfad zur Konfigurationsdatei"
                        }
                    },
                    "required": ["config_file"]
                }
            },
            {
                "name": "get_agent",
                "description": "Ruft einen OpenHands-Agenten ab",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID des Agenten"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "delete_agent",
                "description": "Löscht einen OpenHands-Agenten",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID des Agenten"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "execute_task",
                "description": "Führt eine Aufgabe mit einem OpenHands-Agenten aus",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
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
                    },
                    "required": ["agent_id", "task"]
                }
            },
            {
                "name": "execute_mcp_task",
                "description": "Führt eine MCP-Aufgabe mit einem OpenHands-Agenten aus",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
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
                    },
                    "required": ["agent_id", "task", "server_name", "function_name"]
                }
            },
            {
                "name": "get_task_status",
                "description": "Ruft den Status einer Aufgabe ab",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID der Aufgabe"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "get_task_result",
                "description": "Ruft das Ergebnis einer Aufgabe ab",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID der Aufgabe"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "cancel_task",
                "description": "Bricht eine Aufgabe ab",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID der Aufgabe"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "execute_parallel_tasks",
                "description": "Führt mehrere Aufgaben parallel aus",
                "parameter_schema": {
                    "type": "object",
                    "properties": {
                        "tasks": {
                            "type": "array",
                            "description": "Liste von Aufgaben",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "description": "Typ der Aufgabe (execute_task oder execute_mcp_task)"
                                    },
                                    "agent_id": {
                                        "type": "string",
                                        "description": "ID des Agenten"
                                    },
                                    "task": {
                                        "type": "string",
                                        "description": "Beschreibung der Aufgabe"
                                    }
                                },
                                "required": ["type", "agent_id", "task"]
                            }
                        }
                    },
                    "required": ["tasks"]
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
    
    async def _handle_create_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt einen neuen OpenHands-Agenten.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        config_file = arguments.get("config_file")
        if not config_file:
            raise ValueError("Parameter config_file fehlt")
        
        try:
            # Erstelle einen neuen Agenten
            loop = asyncio.get_event_loop()
            agent = await loop.run_in_executor(self.executor, OpenHandsAgent, config_file)
            
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
            self.logger.error(f"Fehler bei der Erstellung des Agenten: {e}")
            raise
    
    async def _handle_get_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft einen OpenHands-Agenten ab.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        agent_id = arguments.get("agent_id")
        if not agent_id:
            raise ValueError("Parameter agent_id fehlt")
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} nicht gefunden")
        
        agent = self.agents[agent_id]
        
        return {
            "agent_id": agent_id,
            "api_available": agent.api_available,
            "config": agent.config
        }
    
    async def _handle_delete_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Löscht einen OpenHands-Agenten.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        agent_id = arguments.get("agent_id")
        if not agent_id:
            raise ValueError("Parameter agent_id fehlt")
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} nicht gefunden")
        
        # Lösche den Agenten
        del self.agents[agent_id]
        
        return {
            "success": True,
            "message": f"Agent {agent_id} erfolgreich gelöscht"
        }
    
    async def _handle_execute_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt eine Aufgabe mit einem OpenHands-Agenten aus.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        agent_id = arguments.get("agent_id")
        if not agent_id:
            raise ValueError("Parameter agent_id fehlt")
        
        task = arguments.get("task")
        if not task:
            raise ValueError("Parameter task fehlt")
        
        context = arguments.get("context", {})
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} nicht gefunden")
        
        agent = self.agents[agent_id]
        
        # Generiere eine ID für die Aufgabe
        task_id = str(uuid.uuid4())
        
        # Erstelle einen Future für die Aufgabe
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(self.executor, agent.execute_task, task, context)
        
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
                self.logger.info(f"Aufgabe {task_id} erfolgreich abgeschlossen")
            except Exception as e:
                self.tasks[task_id]["status"] = "failed"
                self.tasks[task_id]["result"] = {"error": str(e)}
                self.logger.error(f"Fehler bei der Ausführung der Aufgabe {task_id}: {e}")
        
        future.add_done_callback(update_status)
        
        return {
            "task_id": task_id,
            "status": "running"
        }
    
    async def _handle_execute_mcp_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt eine MCP-Aufgabe mit einem OpenHands-Agenten aus.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        agent_id = arguments.get("agent_id")
        if not agent_id:
            raise ValueError("Parameter agent_id fehlt")
        
        task = arguments.get("task")
        if not task:
            raise ValueError("Parameter task fehlt")
        
        server_name = arguments.get("server_name")
        if not server_name:
            raise ValueError("Parameter server_name fehlt")
        
        function_name = arguments.get("function_name")
        if not function_name:
            raise ValueError("Parameter function_name fehlt")
        
        parameters = arguments.get("parameters", {})
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} nicht gefunden")
        
        agent = self.agents[agent_id]
        
        # Generiere eine ID für die Aufgabe
        task_id = str(uuid.uuid4())
        
        # Erstelle einen Future für die Aufgabe
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            self.executor,
            agent.execute_mcp_task,
            task,
            server_name,
            function_name,
            parameters
        )
        
        # Speichere die Aufgabe
        self.tasks[task_id] = {
            "future": future,
            "agent_id": agent_id,
            "task": task,
            "server_name": server_name,
            "function_name": function_name,
            "parameters": parameters,
            "status": "running",
            "result": None
        }
        
        # Füge einen Callback hinzu, um den Status zu aktualisieren
        def update_status(future):
            try:
                result = future.result()
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["result"] = result
                self.logger.info(f"MCP-Aufgabe {task_id} erfolgreich abgeschlossen")
            except Exception as e:
                self.tasks[task_id]["status"] = "failed"
                self.tasks[task_id]["result"] = {"error": str(e)}
                self.logger.error(f"Fehler bei der Ausführung der MCP-Aufgabe {task_id}: {e}")
        
        future.add_done_callback(update_status)
        
        return {
            "task_id": task_id,
            "status": "running"
        }
    
    async def _handle_get_task_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft den Status einer Aufgabe ab.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        task_id = arguments.get("task_id")
        if not task_id:
            raise ValueError("Parameter task_id fehlt")
        
        if task_id not in self.tasks:
            raise ValueError(f"Aufgabe {task_id} nicht gefunden")
        
        task = self.tasks[task_id]
        
        return {
            "task_id": task_id,
            "status": task["status"],
            "agent_id": task["agent_id"],
            "task": task["task"]
        }
    
    async def _handle_get_task_result(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft das Ergebnis einer Aufgabe ab.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        task_id = arguments.get("task_id")
        if not task_id:
            raise ValueError("Parameter task_id fehlt")
        
        if task_id not in self.tasks:
            raise ValueError(f"Aufgabe {task_id} nicht gefunden")
        
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
    
    async def _handle_cancel_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bricht eine Aufgabe ab.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        task_id = arguments.get("task_id")
        if not task_id:
            raise ValueError("Parameter task_id fehlt")
        
        if task_id not in self.tasks:
            raise ValueError(f"Aufgabe {task_id} nicht gefunden")
        
        task = self.tasks[task_id]
        
        if task["status"] != "running":
            return {
                "task_id": task_id,
                "status": task["status"],
                "message": f"Aufgabe ist bereits {task['status']}"
            }
        
        # Breche die Aufgabe ab
        task["future"].cancel()
        task["status"] = "cancelled"
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Aufgabe erfolgreich abgebrochen"
        }
    
    async def _handle_execute_parallel_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt mehrere Aufgaben parallel aus.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
        """
        tasks = arguments.get("tasks")
        if not tasks:
            raise ValueError("Parameter tasks fehlt")
        
        if not isinstance(tasks, list):
            raise ValueError("Parameter tasks muss eine Liste sein")
        
        # Führe die Aufgaben aus
        task_ids = []
        for task_params in tasks:
            task_type = task_params.get("type")
            if not task_type:
                raise ValueError("Parameter type fehlt in einer Aufgabe")
            
            if task_type == "execute_task":
                result = await self._handle_execute_task(task_params)
            elif task_type == "execute_mcp_task":
                result = await self._handle_execute_mcp_task(task_params)
            else:
                raise ValueError(f"Unbekannter Aufgabentyp: {task_type}")
            
            task_ids.append(result["task_id"])
        
        return {
            "task_ids": task_ids,
            "status": "running"
        }
    
    async def shutdown(self):
        """
        Beendet den MCP-Server ordnungsgemäß.
        """
        await super().shutdown()
        
        # Beende alle laufenden Aufgaben
        for task_id, task in self.tasks.items():
            if task["status"] == "running":
                task["future"].cancel()
                task["status"] = "cancelled"
        
        # Beende den Thread-Pool
        self.executor.shutdown(wait=False)


async def main():
    """
    Hauptfunktion zum Starten des OpenHands MCP-Servers.
    """
    parser = argparse.ArgumentParser(description='OpenHands MCP Server')
    parser = BaseMCPServer.add_common_arguments(parser)
    
    parser.add_argument('--max-workers', type=int, default=5,
                        help='Maximale Anzahl von Worker-Threads (Standard: 5)')
    
    args = parser.parse_args()
    
    await OpenHandsMCPServer.run_server(
        args,
        max_workers=args.max_workers
    )


if __name__ == "__main__":
    asyncio.run(main())