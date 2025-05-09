"""
MCP server interface for the Dev-Server-Workflow project.

This module defines the interface for MCP servers, which provide tools to clients
via the Model Context Protocol.
"""

import abc
from typing import Dict, List, Any, Optional, Union

from .mcp_tool import MCPTool

class MCPServerInterface(abc.ABC):
    """
    Interface for MCP servers.
    
    This class defines the interface for MCP servers, which provide tools to clients
    via the Model Context Protocol.
    """
    
    @abc.abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the MCP server.
        
        This method should be called before using the server.
        """
        pass
    
    @abc.abstractmethod
    async def shutdown(self) -> None:
        """
        Shut down the MCP server.
        
        This method should be called when the server is no longer needed.
        """
        pass
    
    @abc.abstractmethod
    async def list_tools(self) -> List[MCPTool]:
        """
        List the tools provided by the MCP server.
        
        Returns:
            List[MCPTool]: List of tools
        """
        pass
    
    @abc.abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool provided by the MCP server.
        
        Args:
            tool_name: Name of the tool
            arguments: Arguments for the tool
            
        Returns:
            Dict[str, Any]: Result of the tool call
            
        Raises:
            ValueError: If the tool is not found
            Exception: If an error occurs during the tool call
        """
        pass
    
    @abc.abstractmethod
    async def get_server_info(self) -> Dict[str, Any]:
        """
        Get information about the MCP server.
        
        Returns:
            Dict[str, Any]: Server information
        """
        pass
    
    @abc.abstractmethod
    async def handle_jsonrpc_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a JSON-RPC request.
        
        Args:
            request: JSON-RPC request
            
        Returns:
            Dict[str, Any]: JSON-RPC response
        """
        pass
    
    @abc.abstractmethod
    async def start_http_server(self, host: Optional[str] = None, port: Optional[int] = None) -> Any:
        """
        Start an HTTP server for the MCP server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            
        Returns:
            Any: Server instance
        """
        pass
    
    @abc.abstractmethod
    async def process_stdin(self) -> None:
        """
        Process input from stdin.
        
        This method should read JSON-RPC requests from stdin and write responses to stdout.
        """
        pass