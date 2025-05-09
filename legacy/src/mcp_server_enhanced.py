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
Enhanced MCP Server for n8n

This module implements an enhanced Model Context Protocol (MCP) server for n8n,
which allows AI agents to use n8n workflows as tools.

Features:
- Improved error handling
- Detailed logging
- Authentication and authorization
- Health check endpoint
- Metrics collection
- Tool discovery from n8n workflows
"""

import os
import json
import asyncio
import logging
import sys
import time
import traceback
import argparse
import signal
import uuid
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
import aiohttp
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'mcp_server.log'))
    ]
)
logger = logging.getLogger("n8n-mcp-server")


class MCPError(Exception):
    """Base class for MCP server errors."""
    
    def __init__(self, message: str, code: int = -32603):
        """Initialize the error.
        
        Args:
            message: Error message
            code: JSON-RPC error code
        """
        self.message = message
        self.code = code
        super().__init__(message)


class AuthenticationError(MCPError):
    """Authentication error."""
    
    def __init__(self, message: str = "Authentication failed"):
        """Initialize the error."""
        super().__init__(message, -32001)


class AuthorizationError(MCPError):
    """Authorization error."""
    
    def __init__(self, message: str = "Not authorized to perform this action"):
        """Initialize the error."""
        super().__init__(message, -32002)


class ToolNotFoundError(MCPError):
    """Tool not found error."""
    
    def __init__(self, tool_name: str):
        """Initialize the error."""
        super().__init__(f"Tool not found: {tool_name}", -32003)


class ToolExecutionError(MCPError):
    """Tool execution error."""
    
    def __init__(self, tool_name: str, message: str):
        """Initialize the error."""
        super().__init__(f"Error executing tool {tool_name}: {message}", -32004)


class N8nMCPServer:
    """Enhanced MCP server that provides n8n workflow functionality as tools."""
    
    def __init__(self, n8n_url: str, api_key: str, auth_token: Optional[str] = None):
        """Initialize the MCP server with n8n API credentials.
        
        Args:
            n8n_url: URL of the n8n instance
            api_key: API key for n8n
            auth_token: Optional authentication token for clients
        """
        self.n8n_url = n8n_url
        self.n8n_api_key = api_key
        self.auth_token = auth_token
        self.request_id = 0
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.tool_executions = {}
        self.session = None
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Load available tools
        self.tools = self._load_available_tools()
        logger.info(f"Initialized MCP server with {len(self.tools)} tools")
    
    async def _create_session(self):
        """Create an aiohttp session for API requests."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"X-N8N-API-KEY": self.n8n_api_key}
            )
    
    async def _close_session(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _load_available_tools(self) -> List[Dict[str, Any]]:
        """Load available n8n workflows as tools.
        
        In a real implementation, this would query the n8n API to get workflows.
        For this example, we'll use hardcoded tools.
        
        Returns:
            List of tools in MCP format
        """
        logger.info("Loading available tools from n8n")
        
        # In a real implementation, we would query the n8n API:
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(
        #         f"{self.n8n_url}/api/v1/workflows",
        #         headers={"X-N8N-API-KEY": self.n8n_api_key}
        #     ) as response:
        #         workflows = await response.json()
        
        # For this example, we'll use hardcoded tools
        return [
            {
                "name": "create_github_issue",
                "description": "Creates a new issue in GitHub",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the issue"},
                        "body": {"type": "string", "description": "Description of the issue"},
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "labels": {"type": "array", "items": {"type": "string"}, "description": "Labels to apply to the issue"}
                    },
                    "required": ["title", "body", "owner", "repo"]
                }
            },
            {
                "name": "update_work_package",
                "description": "Updates a work package in OpenProject",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "ID of the work package"},
                        "status": {"type": "string", "description": "New status"},
                        "description": {"type": "string", "description": "New description"},
                        "assignee": {"type": "string", "description": "User ID to assign the work package to"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "sync_documentation",
                "description": "Synchronizes documentation between AFFiNE and GitHub",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "doc_id": {"type": "string", "description": "ID of the document in AFFiNE"},
                        "github_path": {"type": "string", "description": "Path of the file in GitHub"},
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "branch": {"type": "string", "description": "Branch to commit to"}
                    },
                    "required": ["doc_id", "github_path", "owner", "repo"]
                }
            },
            {
                "name": "trigger_workflow",
                "description": "Triggers an n8n workflow by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "ID of the workflow to trigger"},
                        "data": {"type": "object", "description": "Data to pass to the workflow"}
                    },
                    "required": ["workflow_id"]
                }
            }
        ]
    
    async def start(self):
        """Start the MCP server and process standard input/output according to the MCP protocol."""
        logger.info("Starting MCP Server for n8n")
        
        # Create aiohttp session
        await self._create_session()
        
        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self._shutdown()))
        
        try:
            # Read from stdin, write to stdout
            self.reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(self.reader)
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
            
            self.writer_transport, self.writer_protocol = await loop.connect_write_pipe(
                asyncio.streams.FlowControlMixin, sys.stdout)
            self.writer = asyncio.StreamWriter(
                self.writer_transport, self.writer_protocol, None, loop)
            
            # Process incoming messages
            while True:
                try:
                    line = await self.reader.readline()
                    if not line:
                        break
                    
                    message = json.loads(line.decode())
                    self.request_count += 1
                    logger.debug(f"Received message: {message}")
                    
                    await self._handle_message(message)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON: {e}")
                    await self._send_error(None, f"Invalid JSON: {e}", -32700)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    logger.error(traceback.format_exc())
                    self.error_count += 1
                    await self._send_error(None, str(e))
        finally:
            await self._close_session()
    
    async def _shutdown(self):
        """Shut down the server gracefully."""
        logger.info("Shutting down MCP server")
        await self._close_session()
        self.writer_transport.close()
        sys.exit(0)
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Process incoming JSON-RPC messages.
        
        Args:
            message: The received JSON-RPC message
        """
        message_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})
        
        # Check authentication if required
        if self.auth_token and method != "initialize":
            auth_header = params.get("auth")
            if not auth_header or auth_header != self.auth_token:
                await self._send_error(message_id, "Authentication required", -32001)
                return
        
        # Process different RPC methods
        try:
            if method == "initialize":
                await self._send_response(message_id, {"capabilities": {"tools": True}})
            elif method == "mcp.listTools":
                await self._send_response(message_id, self.tools)
            elif method == "mcp.callTool":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    raise MCPError("Tool name is required", -32602)
                
                result = await self._execute_tool(tool_name, arguments)
                await self._send_response(message_id, result)
            elif method == "mcp.health":
                health_info = self._get_health_info()
                await self._send_response(message_id, health_info)
            elif method == "mcp.metrics":
                metrics = self._get_metrics()
                await self._send_response(message_id, metrics)
            else:
                raise MCPError(f"Unsupported method: {method}", -32601)
        except MCPError as e:
            await self._send_error(message_id, e.message, e.code)
        except Exception as e:
            logger.error(f"Error handling method {method}: {e}")
            logger.error(traceback.format_exc())
            self.error_count += 1
            await self._send_error(message_id, str(e))
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by calling the corresponding n8n workflow.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Parameters for the tool call
            
        Returns:
            The result of the workflow execution
            
        Raises:
            ToolNotFoundError: If the tool is not found
            ToolExecutionError: If the tool execution fails
        """
        logger.info(f"Executing tool {tool_name} with arguments {json.dumps(arguments)}")
        
        # Check if the tool exists
        tool = next((t for t in self.tools if t["name"] == tool_name), None)
        if not tool:
            raise ToolNotFoundError(tool_name)
        
        # Validate arguments against the tool's parameter schema
        self._validate_arguments(tool, arguments)
        
        # Record the tool execution
        execution_id = str(uuid.uuid4())
        self.tool_executions[execution_id] = {
            "tool": tool_name,
            "arguments": arguments,
            "start_time": time.time(),
            "status": "running"
        }
        
        try:
            # In a real implementation, we would call the n8n API to execute the workflow
            # For this example, we'll simulate the response based on the tool name
            
            if tool_name == "create_github_issue":
                # Simulate a delay
                await asyncio.sleep(0.5)
                
                result = {
                    "status": "success",
                    "issue_number": 42,
                    "issue_url": f"https://github.com/{arguments['owner']}/{arguments['repo']}/issues/42",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            elif tool_name == "update_work_package":
                # Simulate a delay
                await asyncio.sleep(0.3)
                
                result = {
                    "status": "success",
                    "work_package_id": arguments["id"],
                    "updated_fields": list(arguments.keys()),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            elif tool_name == "sync_documentation":
                # Simulate a delay
                await asyncio.sleep(0.7)
                
                result = {
                    "status": "success",
                    "doc_id": arguments["doc_id"],
                    "github_path": arguments["github_path"],
                    "commit_sha": "abc123",
                    "commit_url": f"https://github.com/{arguments['owner']}/{arguments['repo']}/commit/abc123",
                    "synced_at": datetime.now(timezone.utc).isoformat()
                }
            elif tool_name == "trigger_workflow":
                # Simulate a delay
                await asyncio.sleep(0.2)
                
                result = {
                    "status": "success",
                    "workflow_id": arguments["workflow_id"],
                    "execution_id": str(uuid.uuid4()),
                    "triggered_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                raise ToolNotFoundError(tool_name)
            
            # Update the tool execution record
            self.tool_executions[execution_id].update({
                "status": "success",
                "end_time": time.time(),
                "result": result
            })
            
            return result
        except Exception as e:
            # Update the tool execution record
            self.tool_executions[execution_id].update({
                "status": "error",
                "end_time": time.time(),
                "error": str(e)
            })
            
            logger.error(f"Error executing tool {tool_name}: {e}")
            logger.error(traceback.format_exc())
            raise ToolExecutionError(tool_name, str(e))
    
    def _validate_arguments(self, tool: Dict[str, Any], arguments: Dict[str, Any]):
        """Validate arguments against the tool's parameter schema.
        
        Args:
            tool: Tool definition
            arguments: Arguments to validate
            
        Raises:
            MCPError: If the arguments are invalid
        """
        # Check required parameters
        required = tool["parameters"].get("required", [])
        for param in required:
            if param not in arguments:
                raise MCPError(f"Missing required parameter: {param}", -32602)
        
        # Check parameter types (simplified validation)
        properties = tool["parameters"].get("properties", {})
        for param, value in arguments.items():
            if param in properties:
                param_type = properties[param].get("type")
                if param_type == "string" and not isinstance(value, str):
                    raise MCPError(f"Parameter {param} must be a string", -32602)
                elif param_type == "number" and not isinstance(value, (int, float)):
                    raise MCPError(f"Parameter {param} must be a number", -32602)
                elif param_type == "integer" and not isinstance(value, int):
                    raise MCPError(f"Parameter {param} must be an integer", -32602)
                elif param_type == "boolean" and not isinstance(value, bool):
                    raise MCPError(f"Parameter {param} must be a boolean", -32602)
                elif param_type == "array" and not isinstance(value, list):
                    raise MCPError(f"Parameter {param} must be an array", -32602)
                elif param_type == "object" and not isinstance(value, dict):
                    raise MCPError(f"Parameter {param} must be an object", -32602)
    
    def _get_health_info(self) -> Dict[str, Any]:
        """Get health information about the server.
        
        Returns:
            Health information
        """
        return {
            "status": "healthy",
            "uptime": time.time() - self.start_time,
            "n8n_url": self.n8n_url,
            "tool_count": len(self.tools),
            "request_count": self.request_count,
            "error_count": self.error_count
        }
    
    def _get_metrics(self) -> Dict[str, Any]:
        """Get metrics about the server.
        
        Returns:
            Metrics information
        """
        # Calculate tool execution statistics
        tool_stats = {}
        for execution in self.tool_executions.values():
            tool_name = execution["tool"]
            if tool_name not in tool_stats:
                tool_stats[tool_name] = {
                    "count": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "total_duration": 0
                }
            
            tool_stats[tool_name]["count"] += 1
            
            if execution["status"] == "success":
                tool_stats[tool_name]["success_count"] += 1
            elif execution["status"] == "error":
                tool_stats[tool_name]["error_count"] += 1
            
            if "end_time" in execution and "start_time" in execution:
                duration = execution["end_time"] - execution["start_time"]
                tool_stats[tool_name]["total_duration"] += duration
        
        # Calculate average duration for each tool
        for tool_name, stats in tool_stats.items():
            if stats["count"] > 0:
                stats["average_duration"] = stats["total_duration"] / stats["count"]
            else:
                stats["average_duration"] = 0
        
        return {
            "uptime": time.time() - self.start_time,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "tool_executions": len(self.tool_executions),
            "tool_stats": tool_stats
        }
    
    async def _send_response(self, request_id: Any, result: Any):
        """Send a successful JSON-RPC response.
        
        Args:
            request_id: ID of the request
            result: Result of the operation
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        await self._send_message(response)
    
    async def _send_error(self, request_id: Any, error_message: str, code: int = -32603):
        """Send a JSON-RPC error message.
        
        Args:
            request_id: ID of the request
            error_message: Error message
            code: JSON-RPC error code
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": error_message
            }
        }
        await self._send_message(response)
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send a JSON-RPC message.
        
        Args:
            message: The message to send
        """
        message_json = json.dumps(message)
        logger.debug(f"Sending message: {message_json}")
        self.writer.write(f"{message_json}\n".encode())
        await self.writer.drain()


async def main():
    """Main function to start the MCP server."""
    parser = argparse.ArgumentParser(description="n8n MCP Server")
    parser.add_argument("--n8n-url", default=os.environ.get("N8N_URL", "http://localhost:5678"),
                        help="URL of the n8n instance")
    parser.add_argument("--api-key", default=os.environ.get("N8N_API_KEY"),
                        help="API key for n8n")
    parser.add_argument("--auth-token", default=os.environ.get("MCP_AUTH_TOKEN"),
                        help="Authentication token for clients")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"),
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level")
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    if not args.api_key:
        logger.error("N8N_API_KEY environment variable or --api-key argument is required")
        sys.exit(1)
    
    # Start MCP server
    server = N8nMCPServer(args.n8n_url, args.api_key, args.auth_token)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())