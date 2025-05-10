#!/usr/bin/env python3

"""
Base MCP server for the Dev-Server-Workflow project.

This module provides a base class for MCP servers, which implement the Model Context Protocol
to provide tools to clients.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
import signal
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import aiohttp
from aiohttp import web

# Import from core modules
from src.core.logger import setup_logging, get_logger
from src.core.config_manager import ConfigManager
from src.core.utils.docker_utils import DockerUtils
from src.core.utils.process_utils import ProcessManager
from src.core.utils.network_utils import NetworkUtils
from src.core.utils.system_utils import SystemUtils

# Import the MCP server interface
from src.mcp_servers.base.mcp_server_interface import MCPServerInterface
from src.mcp_servers.base.mcp_tool import MCPTool

class BaseMCPServer(MCPServerInterface):
    """
    Base class for MCP server implementations.
    
    This class provides a common foundation for all MCP server implementations
    with standardized methods for logging, error handling, configuration, and
    communication.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 version: str = "1.0.0",
                 host: str = "0.0.0.0", 
                 port: int = 3000,
                 log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 config_file: Optional[str] = None):
        """
        Initialize the MCP server.
        
        Args:
            name: Name of the MCP server
            description: Description of the MCP server
            version: Version of the MCP server
            host: Host for the MCP server
            port: Port for the MCP server
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to the log file (optional)
            config_file: Path to the configuration file (optional)
        """
        self.name = name
        self.description = description
        self.version = version
        self.host = host
        self.port = port
        
        # Configure logging
        self.logger = setup_logging(log_level, log_file)
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Load configuration if specified
        self.config = {}
        if config_file:
            if config_file.endswith('.json'):
                self.config = self.config_manager.load_json_config(config_file, {})
            elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                self.config = self.config_manager.load_yaml_config(config_file, {})
            else:
                self.logger.warning(f"Unknown configuration format: {config_file}")
        
        # Load environment variables
        self.env_config = self.config_manager.load_env_config()
        
        # Initialize counters and status
        self.request_counter = 0
        self.running = True
        self.start_time = None
        self.tools = []
        
        # Initialize HTTP session
        self.session = None
        
        # Initialize health metrics
        self.health_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "last_error": None,
            "last_error_time": None
        }
    
    async def initialize(self) -> None:
        """
        Initialize the MCP server.
        
        This method should be called before using the server.
        """
        self.start_time = asyncio.get_event_loop().time()
        self.session = aiohttp.ClientSession()
        self.logger.info(f"MCP server {self.name} initialized")
        
        # Load tools
        await self._load_tools()
    
    async def _load_tools(self) -> None:
        """
        Load the available tools.
        
        This method must be implemented by derived classes.
        """
        raise NotImplementedError("_load_tools must be implemented by derived classes")
    
    async def get_server_info(self) -> Dict[str, Any]:
        """
        Get information about the MCP server.
        
        Returns:
            Dict[str, Any]: Server information
        """
        uptime = 0
        if self.start_time:
            uptime = asyncio.get_event_loop().time() - self.start_time
        
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": "online" if self.running else "offline",
            "uptime": uptime,
            "request_count": self.request_counter,
            "tools_count": len(self.tools),
            "health_metrics": self.health_metrics
        }
    
    async def list_tools(self) -> List[MCPTool]:
        """
        List the tools provided by the MCP server.
        
        Returns:
            List[MCPTool]: List of tools
        """
        return self.tools
    
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
        raise NotImplementedError("call_tool must be implemented by derived classes")
    
    async def handle_jsonrpc_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a JSON-RPC request.
        
        Args:
            request: JSON-RPC request
            
        Returns:
            Dict[str, Any]: JSON-RPC response
        """
        self.request_counter += 1
        self.health_metrics["total_requests"] += 1
        
        request_id = request.get('id', None)
        method = request.get('method', '')
        params = request.get('params', {})
        
        self.logger.info(f"Request #{self.request_counter}: Method={method}, ID={request_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            if method == 'mcp.listTools':
                tools = await self.list_tools()
                result = [tool.to_dict() for tool in tools]
                self.health_metrics["successful_requests"] += 1
            elif method == 'mcp.callTool':
                tool_name = params.get('name', '')
                arguments = params.get('arguments', {})
                
                if not tool_name:
                    self.health_metrics["failed_requests"] += 1
                    return {
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'error': {
                            'code': -32602,
                            'message': 'Invalid parameters: Tool name is missing'
                        }
                    }
                
                result = await self.call_tool(tool_name, arguments)
                self.health_metrics["successful_requests"] += 1
            elif method == 'mcp.getServerInfo':
                result = await self.get_server_info()
                self.health_metrics["successful_requests"] += 1
            else:
                self.health_metrics["failed_requests"] += 1
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {
                        'code': -32601,
                        'message': f'Method not found: {method}'
                    }
                }
            
            # Update average response time
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            # Calculate new average
            total_successful = self.health_metrics["successful_requests"]
            current_avg = self.health_metrics["average_response_time"]
            new_avg = ((current_avg * (total_successful - 1)) + response_time) / total_successful
            self.health_metrics["average_response_time"] = new_avg
            
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            }
        except Exception as e:
            self.logger.error(f"Error processing request: {e}", exc_info=True)
            
            # Update health metrics
            self.health_metrics["failed_requests"] += 1
            self.health_metrics["last_error"] = str(e)
            self.health_metrics["last_error_time"] = asyncio.get_event_loop().time()
            
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32603,
                    'message': f'Internal error: {str(e)}'
                }
            }
    
    async def process_stdin(self) -> None:
        """
        Process input from stdin.
        
        This method reads JSON-RPC requests from stdin and writes responses to stdout.
        """
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Read a line from stdin (non-blocking)
                line = await loop.run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    self.logger.info("No more input available, shutting down server")
                    self.running = False
                    break
                
                # Process the JSON-RPC request
                try:
                    request = json.loads(line)
                    response = await self.handle_jsonrpc_request(request)
                    
                    # Send the response to stdout
                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON request: {line}")
                    print(json.dumps({
                        'jsonrpc': '2.0',
                        'id': None,
                        'error': {
                            'code': -32700,
                            'message': 'Parse error'
                        }
                    }), flush=True)
            except Exception as e:
                self.logger.error(f"Error processing input: {e}", exc_info=True)
                print(json.dumps({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32603,
                        'message': f'Internal error: {str(e)}'
                    }
                }), flush=True)
    
    async def start_http_server(self, host: Optional[str] = None, port: Optional[int] = None) -> web.AppRunner:
        """
        Start an HTTP server for the MCP server.
        
        Args:
            host: Host to bind to (overrides the constructor value)
            port: Port to bind to (overrides the constructor value)
            
        Returns:
            web.AppRunner: The AppRunner for the HTTP server
        """
        if host:
            self.host = host
        if port:
            self.port = port
        
        app = web.Application()
        
        # Add an endpoint for MCP requests
        async def handle_mcp_request(request):
            try:
                # Parse the JSON-RPC request
                request_data = await request.json()
                
                # Process the request
                response = await self.handle_jsonrpc_request(request_data)
                
                # Send the response
                return web.json_response(response)
            except json.JSONDecodeError:
                return web.json_response({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32700,
                        'message': 'Parse error'
                    }
                }, status=400)
            except Exception as e:
                self.logger.error(f"Error processing HTTP request: {e}", exc_info=True)
                return web.json_response({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32603,
                        'message': f'Internal error: {str(e)}'
                    }
                }, status=500)
        
        app.router.add_post('/mcp', handle_mcp_request)
        
        # Add a simple status page
        async def handle_status(request):
            server_info = await self.get_server_info()
            tools = await self.list_tools()
            
            return web.Response(text=f"""
            <html>
                <head>
                    <title>{server_info['name']}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                        h1 {{ color: #333; }}
                        h2 {{ color: #666; }}
                        .info {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
                        .tools {{ margin-top: 20px; }}
                        .tool {{ background-color: #f9f9f9; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
                        .tool h3 {{ margin-top: 0; }}
                        pre {{ background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                    </style>
                </head>
                <body>
                    <h1>{server_info['name']}</h1>
                    <p>{server_info['description']}</p>
                    
                    <h2>Server Information</h2>
                    <div class="info">
                        <p><strong>Version:</strong> {server_info['version']}</p>
                        <p><strong>Status:</strong> {server_info['status']}</p>
                        <p><strong>Uptime:</strong> {server_info['uptime']:.2f} seconds</p>
                        <p><strong>Processed Requests:</strong> {server_info['request_count']}</p>
                        <p><strong>Available Tools:</strong> {server_info['tools_count']}</p>
                    </div>
                    
                    <h2>Health Metrics</h2>
                    <div class="info">
                        <p><strong>Total Requests:</strong> {server_info['health_metrics']['total_requests']}</p>
                        <p><strong>Successful Requests:</strong> {server_info['health_metrics']['successful_requests']}</p>
                        <p><strong>Failed Requests:</strong> {server_info['health_metrics']['failed_requests']}</p>
                        <p><strong>Average Response Time:</strong> {server_info['health_metrics']['average_response_time']:.4f} seconds</p>
                        <p><strong>Last Error:</strong> {server_info['health_metrics']['last_error'] or 'None'}</p>
                    </div>
                    
                    <h2>Available Tools</h2>
                    <div class="tools">
                        {''.join([f'''
                        <div class="tool">
                            <h3>{tool.name}</h3>
                            <p>{tool.description}</p>
                            <h4>Parameter Schema:</h4>
                            <pre>{json.dumps(tool.parameter_schema, indent=2)}</pre>
                        </div>
                        ''' for tool in tools])}
                    </div>
                    
                    <h2>API Endpoints</h2>
                    <div class="info">
                        <p><strong>MCP Endpoint:</strong> <code>POST /mcp</code></p>
                        <p><strong>Status Page:</strong> <code>GET /</code></p>
                        <p><strong>Health Check:</strong> <code>GET /health</code></p>
                    </div>
                </body>
            </html>
            """, content_type='text/html')
        
        app.router.add_get('/', handle_status)
        
        # Add a health check endpoint
        async def handle_health(request):
            return web.json_response({
                "status": "ok",
                "name": self.name,
                "version": self.version,
                "uptime": asyncio.get_event_loop().time() - self.start_time if self.start_time else 0
            })
        
        app.router.add_get('/health', handle_health)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"HTTP server started at http://{self.host}:{self.port}")
        
        return runner
    
    async def shutdown(self) -> None:
        """
        Shut down the MCP server.
        
        This method should be called when the server is no longer needed.
        """
        self.logger.info("Shutting down MCP server...")
        self.running = False
        
        if self.session:
            await self.session.close()
            self.logger.info("HTTP session closed")
    
    @staticmethod
    def add_common_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Add common command line arguments to an ArgumentParser.
        
        Args:
            parser: ArgumentParser instance
            
        Returns:
            ArgumentParser with added arguments
        """
        parser.add_argument('--host', default='0.0.0.0',
                            help='Host for the MCP server')
        parser.add_argument('--port', type=int, default=3000,
                            help='Port for the MCP server')
        parser.add_argument('--log-level', choices=['debug', 'info', 'warning', 'error', 'critical'],
                            default='info', help='Log level')
        parser.add_argument('--log-file',
                            help='Path to the log file')
        parser.add_argument('--config-file',
                            help='Path to the configuration file')
        parser.add_argument('--mode', choices=['stdio', 'http'], default='stdio',
                            help='Operating mode (stdio or http)')
        
        return parser
    
    @classmethod
    async def run_server(cls, args: argparse.Namespace, **kwargs):
        """
        Create and run an instance of the MCP server.
        
        Args:
            args: Command line arguments
            **kwargs: Additional arguments for the constructor
        """
        # Create and initialize the server
        server = cls(
            host=args.host,
            port=args.port,
            log_level=args.log_level.upper(),
            log_file=args.log_file,
            config_file=args.config_file,
            **kwargs
        )
        await server.initialize()
        
        # Register signal handlers for clean shutdown
        loop = asyncio.get_event_loop()
        
        def signal_handler():
            server.logger.info("Signal received, shutting down server...")
            asyncio.create_task(server.shutdown())
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
        
        try:
            if args.mode == 'stdio':
                server.logger.info(f"Starting {server.name} in STDIO mode")
                await server.process_stdin()
            else:
                server.logger.info(f"Starting {server.name} in HTTP mode on {args.host}:{args.port}")
                runner = await server.start_http_server()
                
                # Keep the server running
                while server.running:
                    await asyncio.sleep(1)
                
                await runner.cleanup()
        finally:
            await server.shutdown()