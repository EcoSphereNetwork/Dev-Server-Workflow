#!/usr/bin/env python3
"""
n8n Integration Layer for MCP Servers.

This module provides a comprehensive integration layer between MCP servers and n8n,
enabling bidirectional communication, workflow management, and monitoring.
"""

import os
import sys
import json
import asyncio
import logging
import aiohttp
import uuid
import hmac
import hashlib
import time
import base64
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from functools import wraps

# Add the parent directory to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import core utilities
from core.logging import get_logger
from core.error_handling import BaseError, ErrorCategory, ErrorHandler
from core.performance import async_cached, async_profiled, async_timed, Cache

# Import workflow utilities
from workflow.n8n_templates import N8nWorkflowTemplate, N8nConnector
from workflow.orchestrator import WorkflowDefinition, orchestrator
from connectors.base import ConnectorConfig, ConnectorError

# Set up logging
logger = get_logger(__name__)

# Constants
DEFAULT_CACHE_TTL = 300  # 5 minutes
DEFAULT_WEBHOOK_SECRET = "mcp-n8n-integration"
DEFAULT_WEBHOOK_PATH = "/webhook/n8n"
DEFAULT_STATUS_PATH = "/status/n8n"
DEFAULT_EXECUTION_TIMEOUT = 300  # 5 minutes


class N8nIntegrationError(BaseError):
    """Base class for n8n integration errors."""
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.INTEGRATION,
            code="ERR_N8N_INTEGRATION",
            details={
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.workflow_id = workflow_id
        self.execution_id = execution_id


class N8nAuthError(N8nIntegrationError):
    """Error raised when authentication with n8n fails."""
    def __init__(
        self,
        message: str,
        **kwargs
    ):
        super().__init__(
            message,
            code="ERR_N8N_AUTH",
            **kwargs
        )


class N8nWebhookError(N8nIntegrationError):
    """Error raised when there's an issue with n8n webhooks."""
    def __init__(
        self,
        message: str,
        webhook_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            code="ERR_N8N_WEBHOOK",
            details={
                "webhook_id": webhook_id,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.webhook_id = webhook_id


class N8nWorkflowError(N8nIntegrationError):
    """Error raised when there's an issue with n8n workflows."""
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            workflow_id=workflow_id,
            code="ERR_N8N_WORKFLOW",
            **kwargs
        )


class N8nExecutionError(N8nIntegrationError):
    """Error raised when there's an issue with n8n workflow execution."""
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            workflow_id=workflow_id,
            execution_id=execution_id,
            code="ERR_N8N_EXECUTION",
            **kwargs
        )


def require_auth(func):
    """Decorator to ensure authentication is set up."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.connector or not await self.connector.is_connected():
            await self.connect()
        return await func(self, *args, **kwargs)
    return wrapper


class N8nIntegration:
    """Integration layer between MCP servers and n8n."""

    def __init__(
        self,
        n8n_url: str = None,
        api_key: str = None,
        webhook_secret: str = None,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        webhook_path: str = DEFAULT_WEBHOOK_PATH,
        status_path: str = DEFAULT_STATUS_PATH,
        execution_timeout: int = DEFAULT_EXECUTION_TIMEOUT,
    ):
        """Initialize the n8n integration.

        Args:
            n8n_url: URL of the n8n instance
            api_key: API key for n8n
            webhook_secret: Secret for webhook validation
            cache_ttl: Cache time-to-live in seconds
            webhook_path: Path for webhook endpoint
            status_path: Path for status endpoint
            execution_timeout: Timeout for workflow executions in seconds
        """
        self.n8n_url = n8n_url or os.environ.get("N8N_URL", "http://localhost:5678")
        self.api_key = api_key or os.environ.get("N8N_API_KEY", "")
        self.webhook_secret = webhook_secret or os.environ.get("N8N_WEBHOOK_SECRET", DEFAULT_WEBHOOK_SECRET)
        self.cache_ttl = cache_ttl
        self.webhook_path = webhook_path
        self.status_path = status_path
        self.execution_timeout = execution_timeout
        
        # Initialize caches
        self.workflow_cache = Cache(default_ttl=cache_ttl)
        self.execution_cache = Cache(default_ttl=cache_ttl * 2)  # Longer TTL for executions
        
        # Initialize connector
        self.connector = None
        self.connector_config = ConnectorConfig(
            service_name="n8n",
            api_key=self.api_key,
            base_url=self.n8n_url,
            timeout=30,
            max_retries=3,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        
        # Initialize webhook handlers
        self.webhook_handlers = {}
        
        # Initialize execution tracking
        self.active_executions = {}
        self.execution_callbacks = {}
        
        # Initialize metrics
        self.metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "webhook_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    async def connect(self) -> None:
        """Connect to n8n.

        Raises:
            N8nAuthError: If authentication fails.
        """
        try:
            # Create and connect the n8n connector
            self.connector = N8nConnector(self.connector_config)
            await self.connector.connect()
            logger.info(f"Connected to n8n at {self.n8n_url}")
        except ConnectorError as e:
            raise N8nAuthError(f"Failed to connect to n8n: {e}", cause=e)

    @require_auth
    async def get_workflows(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get all workflows from n8n.

        Args:
            force_refresh: Whether to force a refresh from n8n

        Returns:
            List of workflow data

        Raises:
            N8nIntegrationError: If fetching workflows fails
        """
        cache_key = "workflows"
        
        # Check cache first
        if not force_refresh:
            cached_workflows = self.workflow_cache.get(cache_key)
            if cached_workflows:
                self.metrics["cache_hits"] += 1
                return cached_workflows
        
        self.metrics["cache_misses"] += 1
        
        try:
            # Fetch workflows from n8n
            workflows = await self.connector.list_workflows()
            
            # Cache the results
            self.workflow_cache.set(cache_key, workflows)
            
            return workflows
        except Exception as e:
            raise N8nIntegrationError(f"Failed to get workflows: {e}", cause=e)

    @require_auth
    async def get_workflow(self, workflow_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Get a specific workflow from n8n.

        Args:
            workflow_id: ID of the workflow
            force_refresh: Whether to force a refresh from n8n

        Returns:
            Workflow data

        Raises:
            N8nWorkflowError: If the workflow is not found
        """
        cache_key = f"workflow:{workflow_id}"
        
        # Check cache first
        if not force_refresh:
            cached_workflow = self.workflow_cache.get(cache_key)
            if cached_workflow:
                self.metrics["cache_hits"] += 1
                return cached_workflow
        
        self.metrics["cache_misses"] += 1
        
        try:
            # Fetch workflow from n8n
            workflow = await self.connector.get_workflow(workflow_id)
            
            # Cache the result
            self.workflow_cache.set(cache_key, workflow)
            
            return workflow
        except ConnectorError as e:
            raise N8nWorkflowError(f"Workflow not found: {workflow_id}", workflow_id=workflow_id, cause=e)

    @require_auth
    @async_timed
    async def execute_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any],
        wait_for_completion: bool = True,
        callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Execute a workflow in n8n.

        Args:
            workflow_id: ID of the workflow to execute
            data: Input data for the workflow
            wait_for_completion: Whether to wait for the workflow to complete
            callback: Optional callback function to call when the workflow completes

        Returns:
            Execution result

        Raises:
            N8nExecutionError: If the execution fails
        """
        try:
            # Generate a unique execution ID
            execution_id = str(uuid.uuid4())
            
            # Register callback if provided
            if callback:
                self.execution_callbacks[execution_id] = callback
            
            # Execute the workflow
            self.metrics["total_executions"] += 1
            execution_result = await self.connector.execute_workflow(workflow_id, data)
            
            # Store execution in active executions
            self.active_executions[execution_id] = {
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "start_time": datetime.now(),
                "status": "running",
                "data": data,
                "result": None,
            }
            
            # If not waiting for completion, return immediately
            if not wait_for_completion:
                return {
                    "execution_id": execution_id,
                    "status": "running",
                    "message": "Workflow execution started",
                }
            
            # Wait for the execution to complete
            start_time = time.time()
            while time.time() - start_time < self.execution_timeout:
                # Check if execution has completed
                execution_data = await self.get_execution(execution_id)
                if execution_data.get("finished"):
                    # Update metrics
                    if execution_data.get("status") == "success":
                        self.metrics["successful_executions"] += 1
                    else:
                        self.metrics["failed_executions"] += 1
                    
                    # Update active executions
                    self.active_executions[execution_id]["status"] = execution_data.get("status", "unknown")
                    self.active_executions[execution_id]["result"] = execution_data
                    
                    # Call callback if registered
                    if execution_id in self.execution_callbacks:
                        try:
                            await self.execution_callbacks[execution_id](execution_data)
                        except Exception as e:
                            logger.error(f"Error in execution callback: {e}")
                        finally:
                            del self.execution_callbacks[execution_id]
                    
                    return execution_data
                
                # Wait before checking again
                await asyncio.sleep(1)
            
            # Timeout reached
            self.metrics["failed_executions"] += 1
            raise N8nExecutionError(
                f"Workflow execution timed out after {self.execution_timeout} seconds",
                workflow_id=workflow_id,
                execution_id=execution_id,
            )
        except Exception as e:
            self.metrics["failed_executions"] += 1
            if isinstance(e, N8nExecutionError):
                raise
            raise N8nExecutionError(
                f"Failed to execute workflow: {e}",
                workflow_id=workflow_id,
                cause=e,
            )

    @require_auth
    async def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get execution details from n8n.

        Args:
            execution_id: ID of the execution

        Returns:
            Execution data

        Raises:
            N8nExecutionError: If the execution is not found
        """
        cache_key = f"execution:{execution_id}"
        
        # Check cache first
        cached_execution = self.execution_cache.get(cache_key)
        if cached_execution and cached_execution.get("finished"):
            self.metrics["cache_hits"] += 1
            return cached_execution
        
        self.metrics["cache_misses"] += 1
        
        try:
            # Fetch execution from n8n
            execution = await self.connector.get_execution(execution_id)
            
            # Process the execution data
            processed_execution = {
                "execution_id": execution_id,
                "workflow_id": execution.get("workflowId"),
                "status": "success" if execution.get("status") == "success" else "error",
                "started_at": execution.get("startedAt"),
                "finished_at": execution.get("stoppedAt"),
                "finished": execution.get("status") in ["success", "error", "failed", "crashed"],
                "data": execution.get("data", {}),
            }
            
            # Cache the result
            self.execution_cache.set(cache_key, processed_execution)
            
            return processed_execution
        except ConnectorError as e:
            raise N8nExecutionError(f"Execution not found: {execution_id}", execution_id=execution_id, cause=e)

    @require_auth
    async def register_webhook(
        self,
        workflow_id: str,
        event_type: str,
        handler: Callable,
    ) -> str:
        """Register a webhook handler for a workflow.

        Args:
            workflow_id: ID of the workflow
            event_type: Type of event to handle
            handler: Function to call when the webhook is triggered

        Returns:
            Webhook ID

        Raises:
            N8nWebhookError: If registering the webhook fails
        """
        webhook_id = f"{workflow_id}:{event_type}:{uuid.uuid4()}"
        
        # Register the handler
        self.webhook_handlers[webhook_id] = {
            "workflow_id": workflow_id,
            "event_type": event_type,
            "handler": handler,
            "created_at": datetime.now(),
        }
        
        logger.info(f"Registered webhook handler: {webhook_id}")
        return webhook_id

    async def unregister_webhook(self, webhook_id: str) -> None:
        """Unregister a webhook handler.

        Args:
            webhook_id: ID of the webhook to unregister
        """
        if webhook_id in self.webhook_handlers:
            del self.webhook_handlers[webhook_id]
            logger.info(f"Unregistered webhook handler: {webhook_id}")

    async def handle_webhook(self, request_data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle an incoming webhook from n8n.

        Args:
            request_data: Webhook payload
            headers: Request headers

        Returns:
            Response data

        Raises:
            N8nWebhookError: If webhook validation fails
        """
        # Validate the webhook signature if present
        signature = headers.get("x-n8n-signature")
        if signature and self.webhook_secret:
            if not self._validate_webhook_signature(signature, json.dumps(request_data)):
                raise N8nWebhookError("Invalid webhook signature")
        
        # Extract workflow information
        workflow_id = request_data.get("workflowId")
        execution_id = request_data.get("executionId")
        event_type = request_data.get("eventType", "webhook")
        
        # Update metrics
        self.metrics["webhook_calls"] += 1
        
        # Find matching handlers
        handlers = []
        for webhook_id, webhook in self.webhook_handlers.items():
            if (webhook["workflow_id"] == workflow_id or webhook["workflow_id"] == "*") and \
               (webhook["event_type"] == event_type or webhook["event_type"] == "*"):
                handlers.append(webhook["handler"])
        
        # Call handlers
        results = []
        for handler in handlers:
            try:
                result = await handler(request_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in webhook handler: {e}")
                results.append({"error": str(e)})
        
        # Return combined results
        return {
            "success": True,
            "message": f"Processed webhook with {len(handlers)} handlers",
            "results": results,
        }

    def _validate_webhook_signature(self, signature: str, payload: str) -> bool:
        """Validate the webhook signature.

        Args:
            signature: Signature from the request headers
            payload: Raw request payload

        Returns:
            True if the signature is valid, False otherwise
        """
        try:
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False

    @require_auth
    async def import_workflow_template(self, template: N8nWorkflowTemplate) -> str:
        """Import a workflow template into n8n.

        Args:
            template: Workflow template to import

        Returns:
            ID of the created workflow

        Raises:
            N8nWorkflowError: If importing the template fails
        """
        try:
            # Convert template to n8n format
            workflow_data = template.to_n8n_format()
            
            # Create the workflow in n8n
            result = await self.connector.create_workflow(workflow_data)
            
            # Invalidate cache
            self.workflow_cache.clear("workflows")
            
            return result["id"]
        except Exception as e:
            raise N8nWorkflowError(f"Failed to import workflow template: {e}", cause=e)

    @require_auth
    async def export_workflow_to_template(self, workflow_id: str) -> N8nWorkflowTemplate:
        """Export a workflow from n8n as a template.

        Args:
            workflow_id: ID of the workflow to export

        Returns:
            Workflow template

        Raises:
            N8nWorkflowError: If exporting the workflow fails
        """
        try:
            # Get the workflow from n8n
            workflow_data = await self.get_workflow(workflow_id)
            
            # Convert to template format
            template = N8nWorkflowTemplate.from_n8n_format(workflow_data)
            
            return template
        except Exception as e:
            raise N8nWorkflowError(f"Failed to export workflow: {e}", workflow_id=workflow_id, cause=e)

    @require_auth
    async def sync_workflow_to_orchestrator(self, workflow_id: str) -> str:
        """Sync a workflow from n8n to the workflow orchestrator.

        Args:
            workflow_id: ID of the workflow to sync

        Returns:
            ID of the synced workflow in the orchestrator

        Raises:
            N8nWorkflowError: If syncing the workflow fails
        """
        try:
            # Export the workflow as a template
            template = await self.export_workflow_to_template(workflow_id)
            
            # Convert to orchestrator format
            workflow_def = WorkflowDefinition(
                id=f"n8n:{workflow_id}",
                name=template.name,
                description=template.description,
                version=template.to_dict().get("version", "1.0.0"),
                metadata={
                    "source": "n8n",
                    "n8n_workflow_id": workflow_id,
                    "n8n_template_id": template.id,
                    "synced_at": datetime.now().isoformat(),
                }
            )
            
            # Register with orchestrator
            orchestrator.register_workflow(workflow_def)
            
            return workflow_def.id
        except Exception as e:
            raise N8nWorkflowError(f"Failed to sync workflow to orchestrator: {e}", workflow_id=workflow_id, cause=e)

    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the n8n integration.

        Returns:
            Status information
        """
        status = {
            "connected": self.connector is not None and await self.connector.is_connected(),
            "n8n_url": self.n8n_url,
            "metrics": self.metrics,
            "active_executions": len(self.active_executions),
            "registered_webhooks": len(self.webhook_handlers),
            "cache_size": {
                "workflows": len([k for k in self.workflow_cache._cache if k.startswith("workflow")]),
                "executions": len([k for k in self.execution_cache._cache if k.startswith("execution")]),
            },
        }
        
        # Try to get additional information if connected
        if status["connected"]:
            try:
                workflows = await self.get_workflows()
                status["workflows_count"] = len(workflows)
            except Exception as e:
                status["workflows_error"] = str(e)
        
        return status

    async def setup_http_handlers(self, app) -> None:
        """Set up HTTP handlers for the integration.

        Args:
            app: The web application to add routes to
        """
        from aiohttp import web
        
        # Webhook handler
        async def handle_webhook_request(request):
            try:
                # Parse request data
                request_data = await request.json()
                
                # Process the webhook
                result = await self.handle_webhook(request_data, dict(request.headers))
                
                return web.json_response(result)
            except Exception as e:
                error_dict = ErrorHandler.handle_error(e, log_error=True, raise_error=False)
                return web.json_response({"error": error_dict}, status=400)
        
        # Status handler
        async def handle_status_request(request):
            try:
                status = await self.get_status()
                return web.json_response(status)
            except Exception as e:
                error_dict = ErrorHandler.handle_error(e, log_error=True, raise_error=False)
                return web.json_response({"error": error_dict}, status=500)
        
        # Add routes
        app.router.add_post(self.webhook_path, handle_webhook_request)
        app.router.add_get(self.status_path, handle_status_request)
        
        logger.info(f"Set up HTTP handlers: webhook={self.webhook_path}, status={self.status_path}")


# Create a global instance
n8n_integration = N8nIntegration()


async def initialize_integration():
    """Initialize the n8n integration."""
    await n8n_integration.connect()
    logger.info("n8n integration initialized")


# Example usage in an MCP server
class N8nMCPServer:
    """MCP server with n8n integration."""
    
    def __init__(self, n8n_url=None, api_key=None):
        """Initialize the MCP server.
        
        Args:
            n8n_url: URL of the n8n instance
            api_key: API key for n8n
        """
        self.n8n_integration = N8nIntegration(n8n_url=n8n_url, api_key=api_key)
        self.tools = []
    
    async def initialize(self):
        """Initialize the server."""
        await self.n8n_integration.connect()
        await self._generate_tools()
    
    async def _generate_tools(self):
        """Generate MCP tools from n8n workflows."""
        try:
            # Get all workflows
            workflows = await self.n8n_integration.get_workflows()
            
            # Filter workflows with MCP tag
            mcp_workflows = [w for w in workflows if "mcp" in w.get("tags", [])]
            
            # Generate tools
            self.tools = []
            for workflow in mcp_workflows:
                tool = {
                    "name": f"workflow_{workflow['name'].lower().replace(' ', '_')}",
                    "description": workflow.get("description", f"Execute n8n workflow: {workflow['name']}"),
                    "parameter_schema": self._get_parameter_schema(workflow),
                }
                self.tools.append(tool)
            
            logger.info(f"Generated {len(self.tools)} tools from n8n workflows")
        except Exception as e:
            logger.error(f"Error generating tools: {e}")
    
    def _get_parameter_schema(self, workflow):
        """Get parameter schema for a workflow."""
        # Default schema
        schema = {
            "type": "object",
            "properties": {
                "input": {
                    "type": "object",
                    "description": "Input data for the workflow"
                }
            }
        }
        
        # Try to extract schema from workflow metadata
        try:
            if "meta" in workflow and "parameterSchema" in workflow["meta"]:
                return workflow["meta"]["parameterSchema"]
        except Exception:
            pass
        
        return schema
    
    async def handle_tool_call(self, tool_name, arguments):
        """Handle a tool call.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Result of the tool call
        """
        try:
            # Find the workflow for this tool
            workflows = await self.n8n_integration.get_workflows()
            workflow_id = None
            
            for workflow in workflows:
                generated_name = f"workflow_{workflow['name'].lower().replace(' ', '_')}"
                if generated_name == tool_name:
                    workflow_id = workflow["id"]
                    break
            
            if not workflow_id:
                return {"error": f"Tool not found: {tool_name}"}
            
            # Execute the workflow
            result = await self.n8n_integration.execute_workflow(workflow_id, arguments)
            return result
        except Exception as e:
            logger.error(f"Error handling tool call: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Shut down the server."""
        # Clean up resources
        pass