"""
MCP-Schnittstelle für den n8n MCP Server.

Dieses Modul bietet eine MCP-konforme Schnittstelle für den n8n MCP Server.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from src.mcp.base.base_mcp_server import BaseMCPServer
from src.mcp.interfaces.mcp_tool import MCPTool

from .core.n8n_client import N8nClient
from .core.auth import AuthManager
from .core.audit import AuditLogger
from .core.metrics import MetricsCollector
from .utils.logger import logger


class N8nMCPServer(BaseMCPServer):
    """MCP-Server für n8n-Workflow-Automatisierung."""
    
    def __init__(self, **kwargs):
        """Initialisiere den MCP-Server."""
        super().__init__(
            name="n8n-mcp-server",
            description="MCP-Server für n8n-Workflow-Automatisierung",
            version="0.1.0",
            **kwargs
        )
        
        # Erstelle n8n-Client
        self.n8n_client = N8nClient()
        
        # Erstelle Auth-Manager
        self.auth_manager = AuthManager()
        
        # Erstelle Audit-Logger
        self.audit_logger = AuditLogger()
        
        # Erstelle Metriken-Sammler
        self.metrics_collector = MetricsCollector()
    
    async def _load_tools(self) -> None:
        """Lade die verfügbaren Tools."""
        self.tools = [
            MCPTool(
                name="list_workflows",
                description="Liste alle n8n-Workflows auf",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Filter nach Tags"
                        },
                        "active": {
                            "type": "boolean",
                            "description": "Filter nach aktiven Workflows"
                        }
                    }
                }
            ),
            MCPTool(
                name="get_workflow",
                description="Erhalte einen n8n-Workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID des Workflows"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="run_workflow",
                description="Führe einen n8n-Workflow aus",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID des Workflows"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Parameter für den Workflow"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="create_workflow",
                description="Erstelle einen n8n-Workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name des Workflows"
                        },
                        "nodes": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Knoten des Workflows"
                        },
                        "connections": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Verbindungen des Workflows"
                        },
                        "active": {
                            "type": "boolean",
                            "description": "Ob der Workflow aktiv sein soll"
                        },
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Tags für den Workflow"
                        }
                    },
                    "required": ["name", "nodes", "connections"]
                }
            ),
            MCPTool(
                name="update_workflow",
                description="Aktualisiere einen n8n-Workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID des Workflows"
                        },
                        "name": {
                            "type": "string",
                            "description": "Neuer Name des Workflows"
                        },
                        "nodes": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Neue Knoten des Workflows"
                        },
                        "connections": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Neue Verbindungen des Workflows"
                        },
                        "active": {
                            "type": "boolean",
                            "description": "Ob der Workflow aktiv sein soll"
                        },
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Neue Tags für den Workflow"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="delete_workflow",
                description="Lösche einen n8n-Workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID des Workflows"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="activate_workflow",
                description="Aktiviere einen n8n-Workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID des Workflows"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="deactivate_workflow",
                description="Deaktiviere einen n8n-Workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID des Workflows"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
        ]
        
        self.logger.info(f"Loaded {len(self.tools)} tools")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe ein Tool auf.
        
        Args:
            tool_name: Name des Tools
            arguments: Argumente für das Tool
            
        Returns:
            Ergebnis des Tool-Aufrufs
            
        Raises:
            ValueError: Wenn das Tool nicht gefunden wird
            Exception: Wenn ein Fehler während des Tool-Aufrufs auftritt
        """
        self.logger.info(f"Calling tool {tool_name} with arguments: {json.dumps(arguments)}")
        
        # Protokolliere das Audit-Ereignis
        self.audit_logger.log(
            event=f"call_tool:{tool_name}",
            user=None,
            details={"arguments": arguments},
        )
        
        # Finde das Tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Erfasse die Startzeit
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Implementiere die Tool-Logik
            if tool_name == "list_workflows":
                result = await self._handle_list_workflows(arguments)
            elif tool_name == "get_workflow":
                result = await self._handle_get_workflow(arguments)
            elif tool_name == "run_workflow":
                result = await self._handle_run_workflow(arguments)
            elif tool_name == "create_workflow":
                result = await self._handle_create_workflow(arguments)
            elif tool_name == "update_workflow":
                result = await self._handle_update_workflow(arguments)
            elif tool_name == "delete_workflow":
                result = await self._handle_delete_workflow(arguments)
            elif tool_name == "activate_workflow":
                result = await self._handle_activate_workflow(arguments)
            elif tool_name == "deactivate_workflow":
                result = await self._handle_deactivate_workflow(arguments)
            else:
                raise ValueError(f"Tool not implemented: {tool_name}")
            
            # Erfasse die Endzeit
            end_time = asyncio.get_event_loop().time()
            
            # Erfasse die Metriken
            self.metrics_collector.record_request(
                method=tool_name,
                success=True,
                response_time=end_time - start_time,
            )
            
            return result
        except Exception as e:
            # Erfasse die Endzeit
            end_time = asyncio.get_event_loop().time()
            
            # Erfasse die Metriken
            self.metrics_collector.record_request(
                method=tool_name,
                success=False,
                response_time=end_time - start_time,
            )
            
            # Protokolliere den Fehler
            self.logger.error(f"Error calling tool {tool_name}: {e}")
            
            # Protokolliere das Audit-Ereignis
            self.audit_logger.log(
                event=f"call_tool_error:{tool_name}",
                user=None,
                details={"arguments": arguments, "error": str(e)},
            )
            
            raise
    
    async def _handle_list_workflows(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das list_workflows-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Liste der Workflows
        """
        tags = arguments.get("tags")
        active = arguments.get("active")
        
        workflows = await self.n8n_client.list_workflows(tags=tags, active=active)
        
        return {"workflows": workflows}
    
    async def _handle_get_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das get_workflow-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Der Workflow
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        workflow = await self.n8n_client.get_workflow(workflow_id)
        
        return {"workflow": workflow}
    
    async def _handle_run_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das run_workflow-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Das Ergebnis der Workflow-Ausführung
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        parameters = arguments.get("parameters")
        
        result = await self.n8n_client.run_workflow(workflow_id, parameters)
        
        # Erfasse die Metriken
        self.metrics_collector.record_workflow_execution(success=True)
        
        return {"result": result}
    
    async def _handle_create_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das create_workflow-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Der erstellte Workflow
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("name is required")
        
        nodes = arguments.get("nodes")
        if not nodes:
            raise ValueError("nodes is required")
        
        connections = arguments.get("connections")
        if not connections:
            raise ValueError("connections is required")
        
        active = arguments.get("active", False)
        tags = arguments.get("tags")
        
        workflow = await self.n8n_client.create_workflow(name, nodes, connections, active, tags)
        
        return {"workflow": workflow}
    
    async def _handle_update_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das update_workflow-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Der aktualisierte Workflow
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        name = arguments.get("name")
        nodes = arguments.get("nodes")
        connections = arguments.get("connections")
        active = arguments.get("active")
        tags = arguments.get("tags")
        
        workflow = await self.n8n_client.update_workflow(workflow_id, name, nodes, connections, active, tags)
        
        return {"workflow": workflow}
    
    async def _handle_delete_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das delete_workflow-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Erfolgsmeldung
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        success = await self.n8n_client.delete_workflow(workflow_id)
        
        return {"success": success}
    
    async def _handle_activate_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das activate_workflow-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Der aktivierte Workflow
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        workflow = await self.n8n_client.activate_workflow(workflow_id)
        
        return {"workflow": workflow}
    
    async def _handle_deactivate_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das deactivate_workflow-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Der deaktivierte Workflow
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        workflow = await self.n8n_client.deactivate_workflow(workflow_id)
        
        return {"workflow": workflow}


async def main():
    """Haupteinstiegspunkt."""
    parser = argparse.ArgumentParser(description="n8n MCP Server")
    parser = BaseMCPServer.add_common_arguments(parser)
    
    args = parser.parse_args()
    
    # Starte den Server
    await N8nMCPServer.run_server(args)


if __name__ == "__main__":
    asyncio.run(main())