"""
MCP-Schnittstelle für den Docker MCP Server.

Dieses Modul bietet eine MCP-konforme Schnittstelle für den Docker MCP Server.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from src.mcp_servers.base.base_mcp_server import BaseMCPServer
from src.mcp_servers.base.mcp_tool import MCPTool

from .core.docker_executor import DockerExecutor
from .core.auth import AuthManager
from .core.audit import AuditLogger
from .core.metrics import MetricsCollector
from .utils.logger import logger


class DockerMCPServer(BaseMCPServer):
    """MCP-Server für Docker-Operationen."""
    
    def __init__(self, **kwargs):
        """Initialisiere den MCP-Server."""
        super().__init__(
            name="docker-mcp-server",
            description="MCP-Server für Docker-Operationen",
            version="0.1.0",
            **kwargs
        )
        
        # Erstelle Docker-Executor
        self.docker_executor = DockerExecutor()
        
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
                name="list_containers",
                description="Liste alle Docker-Container auf",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "all": {
                            "type": "boolean",
                            "description": "Ob alle Container aufgelistet werden sollen"
                        }
                    }
                }
            ),
            MCPTool(
                name="get_container",
                description="Erhalte einen Docker-Container",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID oder Name des Containers"
                        }
                    },
                    "required": ["container_id"]
                }
            ),
            MCPTool(
                name="start_container",
                description="Starte einen Docker-Container",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID oder Name des Containers"
                        }
                    },
                    "required": ["container_id"]
                }
            ),
            MCPTool(
                name="stop_container",
                description="Stoppe einen Docker-Container",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID oder Name des Containers"
                        }
                    },
                    "required": ["container_id"]
                }
            ),
            MCPTool(
                name="restart_container",
                description="Starte einen Docker-Container neu",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID oder Name des Containers"
                        }
                    },
                    "required": ["container_id"]
                }
            ),
            MCPTool(
                name="remove_container",
                description="Entferne einen Docker-Container",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "ID oder Name des Containers"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Ob der Container gewaltsam entfernt werden soll"
                        }
                    },
                    "required": ["container_id"]
                }
            ),
            MCPTool(
                name="list_images",
                description="Liste alle Docker-Images auf",
                parameter_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="get_image",
                description="Erhalte ein Docker-Image",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID oder Name des Images"
                        }
                    },
                    "required": ["image_id"]
                }
            ),
            MCPTool(
                name="pull_image",
                description="Ziehe ein Docker-Image",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "image_name": {
                            "type": "string",
                            "description": "Name des Images"
                        }
                    },
                    "required": ["image_name"]
                }
            ),
            MCPTool(
                name="remove_image",
                description="Entferne ein Docker-Image",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID oder Name des Images"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Ob das Image gewaltsam entfernt werden soll"
                        }
                    },
                    "required": ["image_id"]
                }
            ),
            MCPTool(
                name="list_networks",
                description="Liste alle Docker-Netzwerke auf",
                parameter_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="get_network",
                description="Erhalte ein Docker-Netzwerk",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "network_id": {
                            "type": "string",
                            "description": "ID oder Name des Netzwerks"
                        }
                    },
                    "required": ["network_id"]
                }
            ),
            MCPTool(
                name="list_volumes",
                description="Liste alle Docker-Volumes auf",
                parameter_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPTool(
                name="get_volume",
                description="Erhalte ein Docker-Volume",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "volume_id": {
                            "type": "string",
                            "description": "ID oder Name des Volumes"
                        }
                    },
                    "required": ["volume_id"]
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
            if tool_name == "list_containers":
                result = await self._handle_list_containers(arguments)
            elif tool_name == "get_container":
                result = await self._handle_get_container(arguments)
            elif tool_name == "start_container":
                result = await self._handle_start_container(arguments)
            elif tool_name == "stop_container":
                result = await self._handle_stop_container(arguments)
            elif tool_name == "restart_container":
                result = await self._handle_restart_container(arguments)
            elif tool_name == "remove_container":
                result = await self._handle_remove_container(arguments)
            elif tool_name == "list_images":
                result = await self._handle_list_images(arguments)
            elif tool_name == "get_image":
                result = await self._handle_get_image(arguments)
            elif tool_name == "pull_image":
                result = await self._handle_pull_image(arguments)
            elif tool_name == "remove_image":
                result = await self._handle_remove_image(arguments)
            elif tool_name == "list_networks":
                result = await self._handle_list_networks(arguments)
            elif tool_name == "get_network":
                result = await self._handle_get_network(arguments)
            elif tool_name == "list_volumes":
                result = await self._handle_list_volumes(arguments)
            elif tool_name == "get_volume":
                result = await self._handle_get_volume(arguments)
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
    
    async def _handle_list_containers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das list_containers-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Liste der Container
        """
        all = arguments.get("all", False)
        
        containers = self.docker_executor.list_containers(all=all)
        
        return {"containers": containers}
    
    async def _handle_get_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das get_container-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Der Container
        """
        container_id = arguments.get("container_id")
        if not container_id:
            raise ValueError("container_id is required")
        
        container = self.docker_executor.get_container(container_id)
        
        return {"container": container}
    
    async def _handle_start_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das start_container-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Erfolgsmeldung
        """
        container_id = arguments.get("container_id")
        if not container_id:
            raise ValueError("container_id is required")
        
        success = self.docker_executor.start_container(container_id)
        
        return {"success": success}
    
    async def _handle_stop_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das stop_container-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Erfolgsmeldung
        """
        container_id = arguments.get("container_id")
        if not container_id:
            raise ValueError("container_id is required")
        
        success = self.docker_executor.stop_container(container_id)
        
        return {"success": success}
    
    async def _handle_restart_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das restart_container-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Erfolgsmeldung
        """
        container_id = arguments.get("container_id")
        if not container_id:
            raise ValueError("container_id is required")
        
        success = self.docker_executor.restart_container(container_id)
        
        return {"success": success}
    
    async def _handle_remove_container(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das remove_container-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Erfolgsmeldung
        """
        container_id = arguments.get("container_id")
        if not container_id:
            raise ValueError("container_id is required")
        
        force = arguments.get("force", False)
        
        success = self.docker_executor.remove_container(container_id, force=force)
        
        return {"success": success}
    
    async def _handle_list_images(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das list_images-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Liste der Images
        """
        images = self.docker_executor.list_images()
        
        return {"images": images}
    
    async def _handle_get_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das get_image-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Das Image
        """
        image_id = arguments.get("image_id")
        if not image_id:
            raise ValueError("image_id is required")
        
        image = self.docker_executor.get_image(image_id)
        
        return {"image": image}
    
    async def _handle_pull_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das pull_image-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Erfolgsmeldung
        """
        image_name = arguments.get("image_name")
        if not image_name:
            raise ValueError("image_name is required")
        
        success = self.docker_executor.pull_image(image_name)
        
        return {"success": success}
    
    async def _handle_remove_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das remove_image-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Erfolgsmeldung
        """
        image_id = arguments.get("image_id")
        if not image_id:
            raise ValueError("image_id is required")
        
        force = arguments.get("force", False)
        
        success = self.docker_executor.remove_image(image_id, force=force)
        
        return {"success": success}
    
    async def _handle_list_networks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das list_networks-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Liste der Netzwerke
        """
        networks = self.docker_executor.list_networks()
        
        return {"networks": networks}
    
    async def _handle_get_network(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das get_network-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Das Netzwerk
        """
        network_id = arguments.get("network_id")
        if not network_id:
            raise ValueError("network_id is required")
        
        network = self.docker_executor.get_network(network_id)
        
        return {"network": network}
    
    async def _handle_list_volumes(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das list_volumes-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Liste der Volumes
        """
        volumes = self.docker_executor.list_volumes()
        
        return {"volumes": volumes}
    
    async def _handle_get_volume(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Behandle das get_volume-Tool.
        
        Args:
            arguments: Argumente für das Tool
            
        Returns:
            Das Volume
        """
        volume_id = arguments.get("volume_id")
        if not volume_id:
            raise ValueError("volume_id is required")
        
        volume = self.docker_executor.get_volume(volume_id)
        
        return {"volume": volume}


async def main():
    """Haupteinstiegspunkt."""
    parser = argparse.ArgumentParser(description="Docker MCP Server")
    parser = BaseMCPServer.add_common_arguments(parser)
    
    args = parser.parse_args()
    
    # Starte den Server
    await DockerMCPServer.run_server(args)


if __name__ == "__main__":
    asyncio.run(main())