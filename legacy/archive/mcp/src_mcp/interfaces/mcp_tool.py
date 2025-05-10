"""
MCP tool interface for the Dev-Server-Workflow project.

This module defines the interface for MCP tools, which are used by MCP servers
to provide functionality to clients.
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field

@dataclass
class MCPTool:
    """
    Interface for MCP tools.
    
    This class defines the interface for MCP tools, which are used by MCP servers
    to provide functionality to clients.
    """
    
    name: str
    """Name of the tool."""
    
    description: str
    """Description of the tool."""
    
    parameter_schema: Dict[str, Any] = field(default_factory=dict)
    """JSON Schema for the tool parameters."""
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the tool
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameter_schema": self.parameter_schema
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPTool':
        """
        Create a tool from a dictionary.
        
        Args:
            data: Dictionary representation of the tool
            
        Returns:
            MCPTool: Tool instance
        """
        return cls(
            name=data["name"],
            description=data["description"],
            parameter_schema=data.get("parameter_schema", {})
        )