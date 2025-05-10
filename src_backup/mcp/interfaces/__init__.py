"""
MCP server interfaces for the Dev-Server-Workflow project.

This package contains interfaces for MCP servers, including the base MCP server interface
and specific interfaces for different types of MCP servers.
"""

from .mcp_server_interface import MCPServerInterface
from .mcp_tool import MCPTool

__all__ = [
    'MCPServerInterface',
    'MCPTool',
]