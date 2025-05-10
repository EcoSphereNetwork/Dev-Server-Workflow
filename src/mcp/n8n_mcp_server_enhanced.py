#!/usr/bin/env python3
"""
Enhanced n8n MCP Server with Integration Layer.

This module provides an enhanced MCP server for n8n with a comprehensive
integration layer for bidirectional communication, workflow management,
and monitoring.
"""

import os
import sys
import json
import asyncio
import logging
import aiohttp
import uuid
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Add the parent directory to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import the base MCP server
from mcp.base_mcp_server_improved import BaseMCPServer

# Import the n8n integration
from mcp.n8n_integration import N8nIntegration, N8nIntegrationError

# Import core utilities
from core.logging import get_logger
from core.error_handling import ErrorHandler
from core.performance import async_cached, async_profiled, async_timed

# Set up logging
logger = get_logger(__name__)


class EnhancedN8nMCPServer(BaseMCPServer):
    """
    Enhanced MCP server for n8n with integration layer.
    
    This class extends the base MCP server with a comprehensive integration
    layer for n8n, enabling bidirectional communication, workflow management,
    and monitoring.
    """
    
    def __init__(
        self,
        n8n_url: str = None,
        api_key: str = None,
        webhook_secret: str = None,
        cache_ttl: int = 300,
        server_name: str = "n8n-mcp-server",
        server_version: str = "2.0.0",
        **kwargs
    ):
        """
        Initialize the enhanced n8n MCP server.
        
        Args:
            n8n_url: URL of the n8n instance
            api_key: API key for n8n
            webhook_secret: Secret for webhook validation
            cache_ttl: Cache time-to-live in seconds
            server_name: Name of the MCP server
            server_version: Version of the MCP server
            **kwargs: Additional arguments for the base class
        """
        super().__init__(
            server_name=server_name,
            server_version=server_version,
            **kwargs
        )
        
        # Initialize the n8n integration
        self.n8n_integration = N8nIntegration(
            n8n_url=n8n_url,
            api_key=api_key,
            webhook_secret=webhook_secret,
            cache_ttl=cache_ttl
        )
        
        # Initialize tool cache
        self.tools = []
        self.last_tools_update = None
        self.tools_cache_ttl = cache_ttl
        
        # Initialize execution tracking
        self.executions = {}
        
        # Register signal handlers
        self._register_signal_handlers()
    
    async def initialize(self):
        """Initialize the server."""
        logger.info("Initializing enhanced n8n MCP server...")
        
        # Initialize the base server
        await super().initialize()
        
        # Connect to n8n
        try:
            await self.n8n_integration.connect()
            logger.info("Connected to n8n")
        except N8nIntegrationError as e:
            logger.error(f"Failed to connect to n8n: {e}")
            raise
        
        # Generate tools
        await self._generate_tools()
        
        # Set up webhook handlers
        await self._setup_webhook_handlers()
        
        logger.info("Enhanced n8n MCP server initialized")
    
    @async_cached(ttl=300)
    async def _generate_tools(self):
        """Generate MCP tools from n8n workflows."""
        logger.info("Generating tools from n8n workflows...")
        
        try:
            # Get all workflows
            workflows = await self.n8n_integration.get_workflows()
            
            # Filter workflows with MCP tag
            mcp_workflows = [w for w in workflows if "mcp" in w.get("tags", [])]
            
            # Generate tools
            self.tools = []
            for workflow in mcp_workflows:
                # Extract parameter schema
                parameter_schema = await self._extract_parameter_schema(workflow)
                
                # Create tool definition
                tool = {
                    "name": f"workflow_{workflow['name'].lower().replace(' ', '_')}",
                    "description": workflow.get("description", f"Execute n8n workflow: {workflow['name']}"),
                    "parameter_schema": parameter_schema,
                    "metadata": {
                        "workflow_id": workflow["id"],
                        "tags": workflow.get("tags", []),
                        "active": workflow.get("active", False),
                    }
                }
                
                self.tools.append(tool)
            
            # Update timestamp
            self.last_tools_update = datetime.now()
            
            logger.info(f"Generated {len(self.tools)} tools from n8n workflows")
        except Exception as e:
            logger.error(f"Error generating tools: {e}")
            # Keep existing tools if available
            if not self.tools:
                self.tools = []
    
    async def _extract_parameter_schema(self, workflow):
        """Extract parameter schema from a workflow.
        
        Args:
            workflow: Workflow data
            
        Returns:
            Parameter schema
        """
        # Default schema
        default_schema = {
            "type": "object",
            "properties": {
                "input": {
                    "type": "object",
                    "description": "Input data for the workflow"
                }
            }
        }
        
        try:
            # Try to get detailed workflow information
            workflow_id = workflow["id"]
            workflow_details = await self.n8n_integration.get_workflow(workflow_id)
            
            # Check for schema in metadata
            if "meta" in workflow_details and "parameterSchema" in workflow_details["meta"]:
                return workflow_details["meta"]["parameterSchema"]
            
            # Check for schema in notes (markdown)
            notes = workflow_details.get("notes", "")
            if notes and "```json" in notes:
                try:
                    # Extract JSON from markdown code block
                    start = notes.find("```json") + 7
                    end = notes.find("```", start)
                    if start > 7 and end > start:
                        json_str = notes[start:end].strip()
                        metadata = json.loads(json_str)
                        if "parameter_schema" in metadata:
                            return metadata["parameter_schema"]
                except json.JSONDecodeError:
                    pass
            
            # Try to infer schema from workflow nodes
            if "nodes" in workflow_details:
                for node in workflow_details["nodes"]:
                    if node.get("type") == "n8n-nodes-base.httpRequest" and node.get("position", {}).get("x", 0) < 300:
                        # Likely a trigger node at the beginning
                        params = node.get("parameters", {})
                        if "options" in params and "bodyParametersUi" in params["options"]:
                            body_params = params["options"]["bodyParametersUi"]
                            if body_params and "parameter" in body_params:
                                # Create schema from defined parameters
                                properties = {}
                                for param in body_params["parameter"]:
                                    properties[param["name"]] = {
                                        "type": "string",  # Default type
                                        "description": param.get("description", f"Parameter {param['name']}")
                                    }
                                
                                if properties:
                                    return {
                                        "type": "object",
                                        "properties": properties
                                    }
        except Exception as e:
            logger.warning(f"Error extracting parameter schema: {e}")
        
        return default_schema
    
    async def _setup_webhook_handlers(self):
        """Set up webhook handlers for n8n."""
        logger.info("Setting up webhook handlers...")
        
        # Register a handler for workflow completions
        await self.n8n_integration.register_webhook(
            "*",  # All workflows
            "workflow.completed",
            self._handle_workflow_completion
        )
        
        # Register a handler for workflow failures
        await self.n8n_integration.register_webhook(
            "*",  # All workflows
            "workflow.failed",
            self._handle_workflow_failure
        )
        
        logger.info("Webhook handlers set up")
    
    async def _handle_workflow_completion(self, data):
        """Handle workflow completion webhook.
        
        Args:
            data: Webhook data
            
        Returns:
            Response data
        """
        logger.info(f"Workflow completed: {data.get('workflowId')}")
        
        # Update execution status
        execution_id = data.get("executionId")
        if execution_id in self.executions:
            self.executions[execution_id]["status"] = "completed"
            self.executions[execution_id]["result"] = data.get("result")
            self.executions[execution_id]["completed_at"] = datetime.now()
        
        return {"status": "success"}
    
    async def _handle_workflow_failure(self, data):
        """Handle workflow failure webhook.
        
        Args:
            data: Webhook data
            
        Returns:
            Response data
        """
        logger.warning(f"Workflow failed: {data.get('workflowId')}")
        
        # Update execution status
        execution_id = data.get("executionId")
        if execution_id in self.executions:
            self.executions[execution_id]["status"] = "failed"
            self.executions[execution_id]["error"] = data.get("error")
            self.executions[execution_id]["completed_at"] = datetime.now()
        
        return {"status": "success"}
    
    async def handle_mcp_list_tools(self, params=None):
        """Handle mcp.listTools request.
        
        Args:
            params: Request parameters
            
        Returns:
            List of tools
        """
        # Check if tools need to be refreshed
        if self.last_tools_update is None or \
           (datetime.now() - self.last_tools_update).total_seconds() > self.tools_cache_ttl:
            await self._generate_tools()
        
        return self.tools
    
    async def handle_mcp_call_tool(self, params):
        """Handle mcp.callTool request.
        
        Args:
            params: Request parameters
            
        Returns:
            Tool execution result
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {tool_name} with arguments: {json.dumps(arguments)}")
        
        # Find the workflow for this tool
        workflow_id = None
        for tool in self.tools:
            if tool["name"] == tool_name:
                workflow_id = tool["metadata"]["workflow_id"]
                break
        
        if not workflow_id:
            return {
                "error": f"Tool not found: {tool_name}",
                "status": "error"
            }
        
        try:
            # Execute the workflow
            execution_result = await self.n8n_integration.execute_workflow(
                workflow_id,
                arguments,
                wait_for_completion=True
            )
            
            # Track the execution
            execution_id = execution_result.get("execution_id")
            self.executions[execution_id] = {
                "tool_name": tool_name,
                "workflow_id": workflow_id,
                "arguments": arguments,
                "status": "completed" if execution_result.get("status") == "success" else "failed",
                "result": execution_result,
                "started_at": datetime.now(),
                "completed_at": datetime.now(),
            }
            
            return {
                "status": "success",
                "execution_id": execution_id,
                "result": execution_result
            }
        except Exception as e:
            error_dict = ErrorHandler.handle_error(e, log_error=True, raise_error=False)
            return {
                "status": "error",
                "error": error_dict
            }
    
    async def handle_mcp_get_execution(self, params):
        """Handle mcp.getExecution request.
        
        Args:
            params: Request parameters
            
        Returns:
            Execution details
        """
        execution_id = params.get("execution_id")
        
        # Check local tracking first
        if execution_id in self.executions:
            return self.executions[execution_id]
        
        # Try to get from n8n
        try:
            execution = await self.n8n_integration.get_execution(execution_id)
            return execution
        except Exception as e:
            error_dict = ErrorHandler.handle_error(e, log_error=True, raise_error=False)
            return {
                "status": "error",
                "error": error_dict
            }
    
    async def handle_mcp_get_status(self, params=None):
        """Handle mcp.getStatus request.
        
        Args:
            params: Request parameters
            
        Returns:
            Server status
        """
        # Get n8n integration status
        n8n_status = await self.n8n_integration.get_status()
        
        # Get server status
        server_status = {
            "server_name": self.server_name,
            "server_version": self.server_version,
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "tools_count": len(self.tools),
            "executions_count": len(self.executions),
            "n8n_integration": n8n_status,
        }
        
        return server_status
    
    async def handle_jsonrpc_request(self, request_data):
        """Handle a JSON-RPC request.
        
        Args:
            request_data: JSON-RPC request data
            
        Returns:
            JSON-RPC response
        """
        request_id = request_data.get("id")
        method = request_data.get("method", "")
        params = request_data.get("params", {})
        
        logger.info(f"JSON-RPC request: {method} (ID: {request_id})")
        
        try:
            # Handle MCP methods
            if method == "mcp.listTools":
                result = await self.handle_mcp_list_tools(params)
            elif method == "mcp.callTool":
                result = await self.handle_mcp_call_tool(params)
            elif method == "mcp.getExecution":
                result = await self.handle_mcp_get_execution(params)
            elif method == "mcp.getStatus":
                result = await self.handle_mcp_get_status(params)
            else:
                # Try to handle with base class
                return await super().handle_jsonrpc_request(request_data)
            
            # Return successful response
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            # Handle error
            error_dict = ErrorHandler.handle_error(e, log_error=True, raise_error=False)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": error_dict
                }
            }
    
    async def setup_http_server(self, app):
        """Set up HTTP server routes.
        
        Args:
            app: aiohttp web application
        """
        # Set up base routes
        await super().setup_http_server(app)
        
        # Set up n8n integration routes
        await self.n8n_integration.setup_http_handlers(app)
    
    def _register_signal_handlers(self):
        """Register signal handlers."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
    
    async def shutdown(self):
        """Shut down the server."""
        logger.info("Shutting down enhanced n8n MCP server...")
        
        # Perform cleanup
        try:
            # Close n8n connection
            if hasattr(self.n8n_integration, "connector") and self.n8n_integration.connector:
                await self.n8n_integration.connector.disconnect()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        # Call base shutdown
        await super().shutdown()
        
        logger.info("Enhanced n8n MCP server shut down")


async def main():
    """Main entry point."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Enhanced n8n MCP Server")
    parser.add_argument("--n8n-url", help="URL of the n8n instance", default=os.environ.get("N8N_URL", "http://localhost:5678"))
    parser.add_argument("--api-key", help="API key for n8n", default=os.environ.get("N8N_API_KEY", ""))
    parser.add_argument("--webhook-secret", help="Secret for webhook validation", default=os.environ.get("N8N_WEBHOOK_SECRET", ""))
    parser.add_argument("--host", help="Host to bind to", default="0.0.0.0")
    parser.add_argument("--port", help="Port to listen on", type=int, default=3456)
    parser.add_argument("--log-level", help="Logging level", default="INFO")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Create and initialize the server
    server = EnhancedN8nMCPServer(
        n8n_url=args.n8n_url,
        api_key=args.api_key,
        webhook_secret=args.webhook_secret,
    )
    
    try:
        # Initialize the server
        await server.initialize()
        
        # Start the HTTP server
        from aiohttp import web
        app = web.Application()
        await server.setup_http_server(app)
        
        # Run the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, args.host, args.port)
        await site.start()
        
        logger.info(f"Enhanced n8n MCP server running at http://{args.host}:{args.port}")
        
        # Keep the server running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        # Shut down the server
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())