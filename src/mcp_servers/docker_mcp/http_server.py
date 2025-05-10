"""
HTTP server for Docker MCP server.

This module provides an HTTP server for the Docker MCP server, exposing metrics and health endpoints.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from aiohttp import web

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("docker-mcp-http")


class HttpServer:
    """HTTP server for Docker MCP server."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 3334, 
                 metrics_collector=None, auth_manager=None, audit_logger=None):
        """Initialize the HTTP server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            metrics_collector: Metrics collector
            auth_manager: Authentication manager
            audit_logger: Audit logger
        """
        self.host = host
        self.port = port
        self.metrics_collector = metrics_collector
        self.auth_manager = auth_manager
        self.audit_logger = audit_logger
        self.app = web.Application()
        self.runner = None
        self.site = None
        
        # Set up routes
        self.app.add_routes([
            web.get('/health', self.health_handler),
            web.get('/metrics', self.metrics_handler),
            web.get('/tools', self.tools_handler),
            web.get('/executions', self.executions_handler),
            web.post('/execute', self.execute_handler),
            web.get('/prometheus', self.prometheus_handler),
        ])
        
    async def start(self) -> None:
        """Start the HTTP server."""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        logger.info(f"HTTP server started on http://{self.host}:{self.port}")
        
    async def stop(self) -> None:
        """Stop the HTTP server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("HTTP server stopped")
        
    async def health_handler(self, request: web.Request) -> web.Response:
        """Handle health check requests.
        
        Args:
            request: HTTP request
            
        Returns:
            HTTP response
        """
        # Calculate uptime
        import time
        import psutil
        
        # Get process start time
        process = psutil.Process()
        start_time = process.create_time()
        current_time = time.time()
        
        # Calculate uptime in seconds
        uptime_seconds = int(current_time - start_time)
        
        # Format uptime as days, hours, minutes, seconds
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        return web.json_response({
            "status": "healthy",
            "version": "0.1.0",
            "uptime": uptime_str
        })
        
    async def metrics_handler(self, request: web.Request) -> web.Response:
        """Handle metrics requests.
        
        Args:
            request: HTTP request
            
        Returns:
            HTTP response
        """
        if not self.metrics_collector:
            return web.json_response({
                "error": "Metrics collector not available"
            }, status=500)
            
        return web.json_response(self.metrics_collector.get_metrics_dict())
        
    async def prometheus_handler(self, request: web.Request) -> web.Response:
        """Handle Prometheus metrics requests.
        
        Args:
            request: HTTP request
            
        Returns:
            HTTP response
        """
        if not self.metrics_collector:
            return web.Response(
                text="# Metrics collector not available",
                content_type="text/plain",
                status=500
            )
            
        return web.Response(
            body=self.metrics_collector.get_metrics(),
            content_type="text/plain"
        )
        
    async def tools_handler(self, request: web.Request) -> web.Response:
        """Handle tools requests.
        
        Args:
            request: HTTP request
            
        Returns:
            HTTP response
        """
        # This is a placeholder for a real implementation
        # In a real implementation, this would return the list of available tools
        return web.json_response([
            {
                "name": "create-container",
                "description": "Create a new standalone Docker container",
                "parameters": {
                    "image": "Docker image name",
                    "name": "Container name",
                    "ports": "Port mappings (host:container)",
                    "environment": "Environment variables",
                    "volumes": "Volume mappings (host:container)"
                }
            },
            {
                "name": "list-containers",
                "description": "List all Docker containers",
                "parameters": {
                    "all": "Show all containers (default: true)"
                }
            }
        ])
        
    async def executions_handler(self, request: web.Request) -> web.Response:
        """Handle executions requests.
        
        Args:
            request: HTTP request
            
        Returns:
            HTTP response
        """
        if not self.audit_logger:
            return web.json_response({
                "error": "Audit logger not available"
            }, status=500)
            
        # Get executions from audit logger
        executions = self.audit_logger.get_logs(
            event_type="tool_execution",
            limit=10
        )
        
        return web.json_response(executions)
        
    async def execute_handler(self, request: web.Request) -> web.Response:
        """Handle execute requests.
        
        Args:
            request: HTTP request
            
        Returns:
            HTTP response
        """
        # This is a placeholder for a real implementation
        # In a real implementation, this would execute a tool
        try:
            data = await request.json()
            
            tool_name = data.get("name")
            arguments = data.get("arguments", {})
            
            if not tool_name:
                return web.json_response({
                    "error": "Missing required parameter: name"
                }, status=400)
                
            # Check authorization
            auth_header = request.headers.get("Authorization")
            if not auth_header and self.auth_manager:
                # Check if tool is auto-approved
                if tool_name not in self.auth_manager.get_auto_approve_tools():
                    return web.json_response({
                        "error": "Unauthorized"
                    }, status=401)
                    
            # Execute tool (placeholder)
            result = {
                "status": "success",
                "result": f"Executed tool {tool_name} with arguments {arguments}"
            }
            
            return web.json_response(result)
        except Exception as e:
            return web.json_response({
                "error": str(e)
            }, status=500)