# MCP Server Template

This document provides a template and checklist for creating new MCP servers for the Dev-Server-Workflow project.

## Overview

MCP (Model Context Protocol) servers provide tools to clients via a standardized interface. Each MCP server should implement the `MCPServerInterface` and extend the `BaseMCPServer` class.

## Checklist

- [ ] Create a new Python file in `src/mcp/` or `src/mcp_servers/`
- [ ] Import the necessary modules
- [ ] Create a class that extends `BaseMCPServer`
- [ ] Implement the required methods
- [ ] Add command line arguments
- [ ] Create a main function
- [ ] Add the server to the Docker Compose configuration
- [ ] Update the documentation

## Template

```python
#!/usr/bin/env python3

"""
[Server Name] MCP server for the Dev-Server-Workflow project.

This module provides an MCP server that [brief description of what the server does].
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Add the directory of the common library to the path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Import the common library
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Import the base MCP server
from base_mcp_server_improved import BaseMCPServer
from interfaces import MCPTool

class YourMCPServer(BaseMCPServer):
    """
    MCP server for [brief description].
    
    This class implements an MCP server that [detailed description of what the server does].
    """
    
    def __init__(self, 
                 # Add your specific parameters here
                 **kwargs):
        """
        Initialize the MCP server.
        
        Args:
            # Document your specific parameters here
            **kwargs: Additional arguments for the base class
        """
        super().__init__(
            name="your-mcp-server",
            description="MCP server for [brief description]",
            version="1.0.0",
            **kwargs
        )
        
        # Initialize your specific attributes here
    
    async def _load_tools(self) -> None:
        """
        Load the available tools.
        """
        self.tools = [
            MCPTool(
                name="your_tool",
                description="Description of your tool",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Description of param1"
                        },
                        "param2": {
                            "type": "integer",
                            "description": "Description of param2"
                        }
                    },
                    "required": ["param1"]
                }
            ),
            # Add more tools here
        ]
        
        self.logger.info(f"Loaded {len(self.tools)} tools")
    
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
        self.logger.info(f"Calling tool {tool_name} with arguments: {json.dumps(arguments)}")
        
        # Find the tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Implement your tool logic here
        if tool_name == "your_tool":
            return await self._handle_your_tool(arguments)
        
        # If we get here, the tool is not implemented
        raise NotImplementedError(f"Tool not implemented: {tool_name}")
    
    async def _handle_your_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the 'your_tool' tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            Dict[str, Any]: Result of the tool call
        """
        # Validate arguments
        param1 = arguments.get("param1")
        if not param1:
            raise ValueError("param1 is required")
        
        param2 = arguments.get("param2", 0)
        
        # Implement your tool logic here
        result = {
            "param1": param1,
            "param2": param2,
            "result": "Your result here"
        }
        
        return result


async def main():
    """
    Main function to start the MCP server.
    """
    parser = argparse.ArgumentParser(description='Your MCP Server')
    parser = BaseMCPServer.add_common_arguments(parser)
    
    # Add your specific command line arguments here
    parser.add_argument('--your-param', default='default_value',
                        help='Description of your parameter')
    
    args = parser.parse_args()
    
    # Run the server
    await YourMCPServer.run_server(
        args,
        # Pass your specific parameters here
        your_param=args.your_param
    )


if __name__ == "__main__":
    asyncio.run(main())
```

## Integration with Docker Compose

Add your server to the Docker Compose configuration in `docker-mcp-servers/docker-compose.yml`:

```yaml
services:
  your-mcp-server:
    build:
      context: ..
      dockerfile: docker-mcp-servers/Dockerfile
    command: python3 src/mcp/your_mcp_server.py --mode http --port 3456
    ports:
      - "3456:3456"
    volumes:
      - ..:/workspace
    environment:
      - YOUR_ENV_VAR=value
    networks:
      - mcp-network
```

## Documentation

Update the documentation to include your new MCP server:

1. Add a section to `docs/docs/dev/index.md` describing your server
2. Add API documentation to `docs/docs/dev/api-reference.md`
3. Add user documentation to `docs/docs/user/index.md`

## Testing

Create tests for your MCP server in `tests/mcp/`:

```python
import unittest
import asyncio
from src.mcp.your_mcp_server import YourMCPServer

class TestYourMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = YourMCPServer()
        asyncio.run(self.server.initialize())
    
    def tearDown(self):
        asyncio.run(self.server.shutdown())
    
    def test_load_tools(self):
        tools = asyncio.run(self.server.list_tools())
        self.assertGreater(len(tools), 0)
    
    def test_call_tool(self):
        result = asyncio.run(self.server.call_tool("your_tool", {"param1": "test"}))
        self.assertEqual(result["param1"], "test")
```

## Best Practices

1. **Error Handling**: Use try-except blocks to catch and handle errors properly
2. **Logging**: Use the logger provided by the base class for consistent logging
3. **Configuration**: Use the configuration manager for loading and saving configuration
4. **Documentation**: Document your code with docstrings and comments
5. **Testing**: Write tests for your code to ensure it works as expected
6. **Security**: Validate and sanitize all input to prevent security issues
7. **Performance**: Use async/await for I/O-bound operations to improve performance