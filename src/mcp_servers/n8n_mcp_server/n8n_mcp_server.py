# unified_mcp_server.py - Vervollständigte Version

"""
Unified MCP Server for n8n Workflow Automation.

This module provides a MCP-compliant interface for n8n workflow automation,
combining the features of both previous implementations.
"""

import os
import sys
import json
import asyncio
import logging
import aiohttp
import argparse
import signal
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from aiohttp import web

from src.mcp_servers.base.base_mcp_server import BaseMCPServer
from src.mcp_servers.base.mcp_tool import MCPTool

from .utils.logger import setup_logging
from .core.config import settings
from .core.auth import AuthManager
from .core.audit import AuditLogger
from .core.metrics import MetricsCollector

# Configure logging
logger = setup_logging()

class N8nMCPServer(BaseMCPServer):
    """MCP Server for n8n workflow automation."""
    
    def __init__(self, **kwargs):
        """Initialize the MCP server."""
        super().__init__(
            name="n8n-mcp-server",
            description="MCP Server for n8n workflow automation",
            version=settings.APP_VERSION,
            **kwargs
        )
        
        # Create n8n client
        self.n8n_url = kwargs.get('n8n_url', settings.N8N_URL)
        self.api_key = kwargs.get('api_key', settings.N8N_API_KEY)
        self.session = None
        
        # Create auth manager
        self.auth_manager = AuthManager()
        
        # Create audit logger
        self.audit_logger = AuditLogger()
        
        # Create metrics collector
        self.metrics_collector = MetricsCollector()
        
        # Workflow cache
        self.workflows = {}
        self.last_cache_update = None
        self.workflow_cache_enabled = settings.WORKFLOW_CACHE_ENABLED
        self.workflow_cache_ttl = settings.WORKFLOW_CACHE_TTL
        
        # Server stats
        self.running = True
        self.request_counter = 0

    async def initialize(self):
        """Initialize the server and load workflow information."""
        self.session = aiohttp.ClientSession(headers={
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        })
        
        # Load workflows and generate tools
        await self._fetch_workflows()
        await self._load_tools()
        
        logger.info(f"MCP Server initialized with {len(self.tools)} tools")

    async def _fetch_workflows(self):
        """Fetch all workflows from n8n with MCP tag."""
        try:
            async with self.session.get(f"{self.n8n_url}/api/v1/workflows") as response:
                if response.status == 200:
                    workflows_data = await response.json()
                    
                    # Process workflows and filter by MCP tags
                    for workflow in workflows_data.get('data', []):
                        if 'tags' in workflow and 'mcp' in workflow.get('tags', []):
                            workflow_id = workflow['id']
                            self.workflows[workflow_id] = {
                                'id': workflow_id,
                                'name': workflow['name'],
                                'description': workflow.get('description', ''),
                                'tags': workflow.get('tags', []),
                                'active': workflow.get('active', False)
                            }
                    
                    self.last_cache_update = datetime.now()
                    logger.info(f"Fetched {len(self.workflows)} workflows with MCP tag")
                else:
                    logger.error(f"Error fetching workflows: {response.status}")
        except Exception as e:
            logger.error(f"Error connecting to n8n: {e}")
            raise

    async def _load_tools(self):
        """Load available tools based on workflows."""
        self.tools = []
        
        # Standard tools for workflow management
        standard_tools = [
            MCPTool(
                name="list_workflows",
                description="List all n8n workflows",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags"
                        },
                        "active": {
                            "type": "boolean",
                            "description": "Filter by active workflows"
                        }
                    }
                }
            ),
            MCPTool(
                name="get_workflow",
                description="Get a specific n8n workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="run_workflow",
                description="Execute an n8n workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Parameters for the workflow"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="create_workflow",
                description="Create an n8n workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the workflow"
                        },
                        "nodes": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Nodes of the workflow"
                        },
                        "connections": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Connections of the workflow"
                        },
                        "active": {
                            "type": "boolean",
                            "description": "Whether the workflow should be active"
                        },
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Tags for the workflow"
                        }
                    },
                    "required": ["name", "nodes", "connections"]
                }
            ),
            MCPTool(
                name="update_workflow",
                description="Update an n8n workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow"
                        },
                        "name": {
                            "type": "string",
                            "description": "New name of the workflow"
                        },
                        "nodes": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "New nodes of the workflow"
                        },
                        "connections": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "New connections of the workflow"
                        },
                        "active": {
                            "type": "boolean",
                            "description": "Whether the workflow should be active"
                        },
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "New tags for the workflow"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="delete_workflow",
                description="Delete an n8n workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="activate_workflow",
                description="Activate an n8n workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="deactivate_workflow",
                description="Deactivate an n8n workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            MCPTool(
                name="list_nodes",
                description="List all available n8n nodes",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Filter by node type"
                        },
                        "include_custom": {
                            "type": "boolean",
                            "description": "Include custom nodes"
                        }
                    }
                }
            ),
            MCPTool(
                name="configure_node",
                description="Configure an n8n node in a workflow",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow containing the node"
                        },
                        "node_id": {
                            "type": "string",
                            "description": "ID of the node to configure"
                        },
                        "name": {
                            "type": "string",
                            "description": "New name for the node"
                        },
                        "type": {
                            "type": "string",
                            "description": "Type of the node"
                        },
                        "position": {
                            "type": "object",
                            "description": "Position of the node in the workflow editor"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Parameters for the node configuration"
                        },
                        "credentials": {
                            "type": "object",
                            "description": "Credentials for the node"
                        }
                    },
                    "required": ["workflow_id", "node_id"]
                }
            ),
            MCPTool(
                name="create_custom_node",
                description="Create a new custom n8n node",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the custom node"
                        },
                        "display_name": {
                            "type": "string",
                            "description": "Display name of the custom node"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the custom node"
                        },
                        "icon": {
                            "type": "string",
                            "description": "Icon for the custom node"
                        },
                        "properties": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Properties/parameters of the custom node"
                        },
                        "inputs": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Input definitions of the custom node"
                        },
                        "outputs": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Output definitions of the custom node"
                        },
                        "code": {
                            "type": "string",
                            "description": "JavaScript code for the custom node"
                        }
                    },
                    "required": ["name", "display_name", "properties", "code"]
                }
            ),
            MCPTool(
                name="update_custom_node",
                description="Update an existing custom n8n node",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "node_id": {
                            "type": "string",
                            "description": "ID of the custom node to update"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the custom node"
                        },
                        "display_name": {
                            "type": "string",
                            "description": "Display name of the custom node"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the custom node"
                        },
                        "icon": {
                            "type": "string",
                            "description": "Icon for the custom node"
                        },
                        "properties": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Properties/parameters of the custom node"
                        },
                        "inputs": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Input definitions of the custom node"
                        },
                        "outputs": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Output definitions of the custom node"
                        },
                        "code": {
                            "type": "string",
                            "description": "JavaScript code for the custom node"
                        }
                    },
                    "required": ["node_id"]
                }
            ),
            MCPTool(
                name="delete_custom_node",
                description="Delete a custom n8n node",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "node_id": {
                            "type": "string",
                            "description": "ID of the custom node to delete"
                        }
                    },
                    "required": ["node_id"]
                }
            )
        ]
        
        self.tools.extend(standard_tools)
        
        # Add workflow-specific tools
        for workflow_id, workflow in self.workflows.items():
            tool_name = f"workflow_{workflow['name'].lower().replace(' ', '_')}"
            parameter_schema = await self._extract_parameter_schema(workflow_id)
            
            self.tools.append(MCPTool(
                name=tool_name,
                description=workflow.get('description', f"Execute the n8n workflow '{workflow['name']}'"),
                parameter_schema=parameter_schema
            ))
        
        logger.info(f"Loaded {len(self.tools)} tools")

    async def _extract_parameter_schema(self, workflow_id):
        """Extract parameter schema from a workflow."""
        # Default schema if no specific schema is defined
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
            # Try to load detailed workflow information
            async with self.session.get(f"{self.n8n_url}/api/v1/workflows/{workflow_id}") as response:
                if response.status == 200:
                    workflow_data = await response.json()
                    
                    # Look for MCP metadata in workflow notes or description
                    notes = workflow_data.get('notes', '')
                    if notes and '```json' in notes:
                        # Extract JSON from markdown code block
                        try:
                            start = notes.find('```json') + 7
                            end = notes.find('```', start)
                            if start > 7 and end > start:
                                json_str = notes[start:end].strip()
                                metadata = json.loads(json_str)
                                if 'parameter_schema' in metadata:
                                    return metadata['parameter_schema']
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            logger.warning(f"Error extracting parameter schema for workflow {workflow_id}: {e}")
        
        return default_schema

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool.
        
        Args:
            tool_name: Name of the tool
            arguments: Arguments for the tool
            
        Returns:
            Result of the tool call
        """
        logger.info(f"Calling tool {tool_name} with arguments: {json.dumps(arguments)}")
        
        # Log the audit event
        self.audit_logger.log(
            event=f"call_tool:{tool_name}",
            user=None,
            details={"arguments": arguments},
        )
        
        # Find the tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Record start time
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Handle standard tools
            if tool_name == "list_workflows":
                result = await self._handle_list_workflows(arguments)
            elif tool_name == "get_workflow":
                result = await self._handle_get_workflow(arguments)
            elif tool_name == "run_workflow":
                result = await self._handle_run_workflow(arguments)
            elif tool_name == "create_workflow":
                result = await self._handle_create_workflow(arguments)
            elif tool_name == "update_workflow":
                result = await self._handle_update_workflow(arguments)
            elif tool_name == "delete_workflow":
                result = await self._handle_delete_workflow(arguments)
            elif tool_name == "activate_workflow":
                result = await self._handle_activate_workflow(arguments)
            elif tool_name == "deactivate_workflow":
                result = await self._handle_deactivate_workflow(arguments)
            # Handle workflow execution tools
            elif tool_name.startswith("workflow_"):
                workflow_id = self._get_workflow_id_by_tool_name(tool_name)
                if workflow_id:
                    result = await self._execute_workflow(workflow_id, arguments)
                else:
                    raise ValueError(f"No matching workflow for tool: {tool_name}")
            else:
                raise ValueError(f"Tool not implemented: {tool_name}")
            
            # Record end time and metrics
            end_time = asyncio.get_event_loop().time()
            self.metrics_collector.record_request(
                method=tool_name,
                success=True,
                response_time=end_time - start_time,
            )
            
            return result
        except Exception as e:
            # Record end time and metrics for failures
            end_time = asyncio.get_event_loop().time()
            self.metrics_collector.record_request(
                method=tool_name,
                success=False,
                response_time=end_time - start_time,
            )
            
            # Log the error
            logger.error(f"Error calling tool {tool_name}: {e}")
            
            # Log the audit event
            self.audit_logger.log(
                event=f"call_tool_error:{tool_name}",
                user=None,
                details={"arguments": arguments, "error": str(e)},
            )
            
            raise

    async def _handle_list_workflows(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the list_workflows tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            List of workflows
        """
        tags = arguments.get("tags")
        active = arguments.get("active")
        
        try:
            # Check if cache needs refresh
            if self.workflow_cache_enabled and self.last_cache_update:
                now = datetime.now()
                if (now - self.last_cache_update).total_seconds() > self.workflow_cache_ttl:
                    logger.info("Cache expired, fetching workflows")
                    await self._fetch_workflows()
            
            # Filter workflows
            filtered_workflows = []
            for workflow_id, workflow in self.workflows.items():
                # Filter by tags
                if tags and not any(tag in workflow.get('tags', []) for tag in tags):
                    continue
                
                # Filter by active status
                if active is not None and workflow.get('active', False) != active:
                    continue
                
                filtered_workflows.append(workflow)
            
            return {"workflows": filtered_workflows, "total": len(filtered_workflows)}
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise

    async def _handle_get_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the get_workflow tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            The workflow
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        try:
            # Check if workflow is in cache
            if self.workflow_cache_enabled and workflow_id in self.workflows:
                # Check if cache needs refresh
                now = datetime.now()
                if not self.last_cache_update or (now - self.last_cache_update).total_seconds() > self.workflow_cache_ttl:
                    logger.info("Cache expired, fetching workflow")
                    await self._fetch_workflow(workflow_id)
                
                return {"workflow": self.workflows.get(workflow_id)}
            else:
                # Fetch workflow from n8n
                workflow = await self._fetch_workflow(workflow_id)
                return {"workflow": workflow}
        except Exception as e:
            logger.error(f"Error getting workflow {workflow_id}: {e}")
            raise

    async def _fetch_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Fetch a workflow from n8n.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            The workflow
        """
        try:
            async with self.session.get(f"{self.n8n_url}/api/v1/workflows/{workflow_id}") as response:
                if response.status == 200:
                    workflow = await response.json()
                    
                    # Cache workflow
                    if self.workflow_cache_enabled:
                        self.workflows[workflow_id] = {
                            'id': workflow['id'],
                            'name': workflow['name'],
                            'description': workflow.get('description', ''),
                            'tags': workflow.get('tags', []),
                            'active': workflow.get('active', False),
                            'nodes': workflow.get('nodes', []),
                            'connections': workflow.get('connections', {})
                        }
                        self.last_cache_update = datetime.now()
                    
                    return workflow
                else:
                    error_text = await response.text()
                    logger.error(f"Error fetching workflow {workflow_id}: {response.status} - {error_text}")
                    raise Exception(f"Error fetching workflow: {error_text}")
        except Exception as e:
            logger.error(f"Error connecting to n8n: {e}")
            raise

    async def _handle_run_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the run_workflow tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            Result of the workflow execution
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        parameters = arguments.get("parameters", {})
        
        try:
            return await self._execute_workflow(workflow_id, parameters)
        except Exception as e:
            logger.error(f"Error running workflow {workflow_id}: {e}")
            raise

    async def _handle_create_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the create_workflow tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            The created workflow
        """
        name = arguments.get("name")
        if not name:
            raise ValueError("name is required")
        
        nodes = arguments.get("nodes")
        if not nodes:
            raise ValueError("nodes is required")
        
        connections = arguments.get("connections")
        if not connections:
            raise ValueError("connections is required")
        
        active = arguments.get("active", False)
        tags = arguments.get("tags", [])
        
        try:
            # Add 'mcp' tag if not present
            if 'mcp' not in tags:
                tags.append('mcp')
            
            # Create workflow
            payload = {
                'name': name,
                'nodes': nodes,
                'connections': connections,
                'active': active,
                'tags': tags
            }
            
            async with self.session.post(
                f"{self.n8n_url}/api/v1/workflows",
                json=payload
            ) as response:
                if response.status in (200, 201):
                    workflow = await response.json()
                    
                    # Update cache
                    if self.workflow_cache_enabled:
                        workflow_id = workflow['id']
                        self.workflows[workflow_id] = {
                            'id': workflow_id,
                            'name': workflow['name'],
                            'description': workflow.get('description', ''),
                            'tags': workflow.get('tags', []),
                            'active': workflow.get('active', False),
                            'nodes': workflow.get('nodes', []),
                            'connections': workflow.get('connections', {})
                        }
                        self.last_cache_update = datetime.now()
                    
                    # Add tool for the new workflow
                    tool_name = f"workflow_{workflow['name'].lower().replace(' ', '_')}"
                    parameter_schema = await self._extract_parameter_schema(workflow['id'])
                    
                    self.tools.append(MCPTool(
                        name=tool_name,
                        description=workflow.get('description', f"Execute the n8n workflow '{workflow['name']}'"),
                        parameter_schema=parameter_schema
                    ))
                    
                    return {"workflow": workflow}
                else:
                    error_text = await response.text()
                    logger.error(f"Error creating workflow: {response.status} - {error_text}")
                    raise Exception(f"Error creating workflow: {error_text}")
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise

    async def _handle_update_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the update_workflow tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            The updated workflow
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        try:
            # Get current workflow
            current_workflow = await self._fetch_workflow(workflow_id)
            
            # Update workflow fields
            name = arguments.get("name", current_workflow.get('name'))
            nodes = arguments.get("nodes", current_workflow.get('nodes', []))
            connections = arguments.get("connections", current_workflow.get('connections', {}))
            active = arguments.get("active", current_workflow.get('active', False))
            tags = arguments.get("tags", current_workflow.get('tags', []))
            
            # Add 'mcp' tag if not present
            if 'mcp' not in tags:
                tags.append('mcp')
            
            # Update workflow
            payload = {
                'name': name,
                'nodes': nodes,
                'connections': connections,
                'active': active,
                'tags': tags
            }
            
            async with self.session.put(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}",
                json=payload
            ) as response:
                if response.status == 200:
                    workflow = await response.json()
                    
                    # Update cache
                    if self.workflow_cache_enabled:
                        self.workflows[workflow_id] = {
                            'id': workflow['id'],
                            'name': workflow['name'],
                            'description': workflow.get('description', ''),
                            'tags': workflow.get('tags', []),
                            'active': workflow.get('active', False),
                            'nodes': workflow.get('nodes', []),
                            'connections': workflow.get('connections', {})
                        }
                        self.last_cache_update = datetime.now()
                    
                    return {"workflow": workflow}
                else:
                    error_text = await response.text()
                    logger.error(f"Error updating workflow {workflow_id}: {response.status} - {error_text}")
                    raise Exception(f"Error updating workflow: {error_text}")
        except Exception as e:
            logger.error(f"Error updating workflow {workflow_id}: {e}")
            raise

    async def _handle_delete_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the delete_workflow tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            Success message
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        try:
            async with self.session.delete(f"{self.n8n_url}/api/v1/workflows/{workflow_id}") as response:
                if response.status in (200, 204):
                    # Update cache
                    if self.workflow_cache_enabled and workflow_id in self.workflows:
                        del self.workflows[workflow_id]
                        
                        # Remove tool for the deleted workflow
                        workflow_name = None
                        for tool in self.tools:
                            if tool.name.startswith("workflow_") and self._get_workflow_id_by_tool_name(tool.name) == workflow_id:
                                workflow_name = tool.name
                                self.tools.remove(tool)
                                break
                    
                    return {"success": True, "message": f"Workflow {workflow_id} deleted"}
                else:
                    error_text = await response.text()
                    logger.error(f"Error deleting workflow {workflow_id}: {response.status} - {error_text}")
                    raise Exception(f"Error deleting workflow: {error_text}")
        except Exception as e:
            logger.error(f"Error deleting workflow {workflow_id}: {e}")
            raise

    async def _handle_activate_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the activate_workflow tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            The activated workflow
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        try:
            # Update workflow with active=true
            arguments["active"] = True
            return await self._handle_update_workflow(arguments)
        except Exception as e:
            logger.error(f"Error activating workflow {workflow_id}: {e}")
            raise

    async def _handle_deactivate_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the deactivate_workflow tool.
        
        Args:
            arguments: Arguments for the tool
            
        Returns:
            The deactivated workflow
        """
        workflow_id = arguments.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required")
        
        try:
            # Update workflow with active=false
            arguments["active"] = False
            return await self._handle_update_workflow(arguments)
        except Exception as e:
            logger.error(f"Error deactivating workflow {workflow_id}: {e}")
            raise

    def _get_workflow_id_by_tool_name(self, tool_name: str) -> Optional[str]:
        """Get workflow ID based on tool name."""
        for workflow_id, workflow in self.workflows.items():
            if tool_name == f"workflow_{workflow['name'].lower().replace(' ', '_')}":
                return workflow_id
        return None

    async def _execute_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        try:
            execution_id = str(uuid.uuid4())
            payload = {
                'workflowData': {
                    'id': workflow_id
                },
                'executionId': execution_id,
                'runData': data
            }
            
            async with self.session.post(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute",
                json=payload
            ) as response:
                if response.status in (200, 201):
                    result = await response.json()
                    
                    # Record successful workflow execution
                    self.metrics_collector.record_workflow_execution(success=True)
                    
                    return {
                        'success': True,
                        'execution_id': execution_id,
                        'data': result.get('data', result)
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Error executing workflow: {response.status} - {error_text}")
                    
                    # Record failed workflow execution
                    self.metrics_collector.record_workflow_execution(success=False)
                    
                    return {
                        'success': False,
                        'error': f"HTTP {response.status}: {error_text}"
                    }
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            
            # Record failed workflow execution
            self.metrics_collector.record_workflow_execution(success=False)
            
            return {
                'success': False,
                'error': str(e)
            }

    async def handle_jsonrpc_request(self, request_data):
        """
        Handle a JSON-RPC request.
        
        Args:
            request_data: The JSON-RPC request
            
        Returns:
            The JSON-RPC response
        """
        self.request_counter += 1
        request_id = request_data.get('id', None)
        method = request_data.get('method', '')
        params = request_data.get('params', {})
        
        logger.info(f"Request #{self.request_counter}: Method={method}, ID={request_id}")
        
        try:
            if method == 'mcp.listTools':
                result = await self.handle_list_tools()
            elif method == 'mcp.callTool':
                result = await self.handle_call_tool(params)
            else:
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {
                        'code': -32601,
                        'message': f'Method not found: {method}'
                    }
                }
            
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            }
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32603,
                    'message': f'Internal error: {str(e)}'
                }
            }

    async def handle_list_tools(self):
        """
        Handle the mcp.listTools request.
        
        Returns:
            List of available tools
        """
        # Check if workflows need refresh
        if self.last_cache_update:
            now = datetime.now()
            if (now - self.last_cache_update).total_seconds() > self.workflow_cache_ttl:
                logger.info("Cache expired, fetching workflows")
                await self._fetch_workflows()
                await self._load_tools()
        
        # Return tools in MCP format
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameter_schema": tool.parameter_schema
            }
            for tool in self.tools
        ]

    async def handle_call_tool(self, params):
        """
        Handle the mcp.callTool request.
        
        Args:
            params: Parameters of the request
            
        Returns:
            Result of the tool call
        """
        tool_name = params.get('name', '')
        arguments = params.get('arguments', {})
        
        logger.info(f"Tool call: {tool_name} with arguments: {json.dumps(arguments)}")
        
        # Call the tool
        return await self.call_tool(tool_name, arguments)

    async def process_stdin(self):
        """Process input from stdin in JSON-RPC format."""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Read a line from stdin (non-blocking)
                line = await loop.run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    logger.info("No more input available, shutting down server")
                    self.running = False
                    break
                
                # Process the JSON-RPC request
                try:
                    request = json.loads(line)
                    response = await self.handle_jsonrpc_request(request)
                    
                    # Send response to stdout
                    print(json.dumps(response))
                    sys.stdout.flush()
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON request: {line}")
                    error_response = {
                        'jsonrpc': '2.0',
                        'id': None,
                        'error': {
                            'code': -32700,
                            'message': 'Invalid JSON request'
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error processing input: {e}")

    async def start_http_server(self, host='0.0.0.0', port=3456):
        """
        Start an HTTP server for MCP requests.
        
        Args:
            host: Host address for the server
            port: Port for the server
        """
        app = web.Application()
        
        async def handle_mcp_request(request):
            try:
                request_data = await request.json()
                response = await self.handle_jsonrpc_request(request_data)
                return web.json_response(response)
            except Exception as e:
                logger.error(f"Error processing HTTP request: {e}")
                return web.json_response({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32603,
                        'message': f'Internal error: {str(e)}'
                    }
                }, status=500)
        
        # Add CORS middleware
        app.add_middleware = lambda middleware: None
        app.middlewares.append(
            web.middleware(
                lambda handler: lambda request: handler(request),
                origins=settings.ALLOWED_ORIGINS,
                allow_credentials=True,
                allow_methods=["GET", "POST"],
                allow_headers=["*"],
            )
        )
        
        # Add rate limiting middleware
        @web.middleware
        async def rate_limit_middleware(request, handler):
            client_ip = request.remote
            # Simple in-memory rate limiting
            # In production, use Redis or similar for distributed rate limiting
            rate_limit_key = f"rate_limit:{client_ip}"
            # Implement rate limiting logic here
            return await handler(request)
        
        app.middlewares.append(rate_limit_middleware)
        
        # Add security headers middleware
        @web.middleware
        async def security_headers_middleware(request, handler):
            response = await handler(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["X-Frame-Options"] = "DENY"
            return response
        
        app.middlewares.append(security_headers_middleware)
        
        # Add authentication middleware
        @web.middleware
        async def auth_middleware(request, handler):
            if request.path == "/health" or request.path == "/metrics":
                # Skip authentication for health check and metrics
                return await handler(request)
            
            # Check for authentication header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return web.json_response({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32401,
                        'message': 'Unauthorized'
                    }
                }, status=401)
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            if not self.auth_manager.authenticate(token):
                return web.json_response({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32401,
                        'message': 'Unauthorized'
                    }
                }, status=401)
            
            return await handler(request)
        
        if settings.AUTH_ENABLED:
            app.middlewares.append(auth_middleware)
        
        # Add routes
        app.router.add_post('/mcp', handle_mcp_request)
        
        # Add status page
        async def handle_status(request):
            return web.Response(text=f"""
            <html>
                <head><title>n8n MCP Server</title></head>
                <body>
                    <h1>n8n MCP Server</h1>
                    <p>Status: Active</p>
                    <p>Available tools: {len(self.tools)}</p>
                    <p>Processed requests: {self.request_counter}</p>
                    <p>Last cache update: {self.last_cache_update}</p>
                </body>
            </html>
            """, content_type='text/html')
        
        app.router.add_get('/', handle_status)
        
        # Add health check endpoint
        async def health_check(request):
            # Check n8n connection
            try:
                async with self.session.get(f"{self.n8n_url}/api/v1/health") as response:
                    n8n_status = "ok" if response.status == 200 else "error"
            except Exception:
                n8n_status = "error"
            
            status = "ok" if n8n_status == "ok" else "degraded"
            
            return web.json_response({
                "status": status,
                "services": {
                    "n8n": n8n_status
                }
            })
        
        app.router.add_get('/health', health_check)
        
        # Add metrics endpoint
        async def get_metrics(request):
            # Update workflow metrics
            try:
                total_workflows = len(self.workflows)
                active_workflows = sum(1 for w in self.workflows.values() if w.get("active", False))
                
                self.metrics_collector.update_workflow_metrics(
                    total=total_workflows,
                    active=active_workflows,
                )
            except Exception as e:
                logger.error(f"Error updating workflow metrics: {e}")
            
            # Get metrics in Prometheus format
            prometheus_metrics = self.metrics_collector.get_prometheus_metrics()
            
            return web.Response(text=prometheus_metrics, content_type="text/plain")
        
        app.router.add_get('/metrics', get_metrics)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"HTTP server started on http://{host}:{port}")
        
        return runner

    async def shutdown(self):
        """Shutdown the server gracefully."""
        logger.info("Shutting down server...")
        self.running = False
        
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")

async def main():
    """Main function to start the MCP server."""
    parser = argparse.ArgumentParser(description='n8n MCP Server')
    parser.add_argument('--n8n-url', default=os.environ.get('N8N_MCP_N8N_URL', 'http://localhost:5678'),
                        help='URL of the n8n instance (default: http://localhost:5678)')
    parser.add_argument('--api-key', default=os.environ.get('N8N_MCP_N8N_API_KEY', ''),
                        help='API key for n8n')
    parser.add_argument('--mode', choices=['stdio', 'http'], default='stdio',
                        help='Operating mode (stdio or http)')
    parser.add_argument('--http-host', default=os.environ.get('N8N_MCP_HOST', '0.0.0.0'),
                        help='Host for the HTTP server (only in HTTP mode)')
    parser.add_argument('--http-port', type=int, default=int(os.environ.get('N8N_MCP_PORT', 3456)),
                        help='Port for the HTTP server (only in HTTP mode)')
    
    args = parser.parse_args()
    
    if not args.api_key and args.mode != 'stdio':
        logger.error("No API key provided. Please provide an API key with --api-key or the N8N_MCP_N8N_API_KEY environment variable.")
        sys.exit(1)
    
    # Create and initialize the server
    server = N8nMCPServer(n8n_url=args.n8n_url, api_key=args.api_key)
    await server.initialize()
    
    # Register signal handlers for clean shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("Signal received, shutting down server...")
        asyncio.create_task(server.shutdown())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        if args.mode == 'stdio':
            logger.info("Starting MCP server in STDIO mode")
            await server.process_stdin()
        else:
            logger.info(f"Starting MCP server in HTTP mode on {args.http_host}:{args.http_port}")
            runner = await server.start_http_server(args.http_host, args.http_port)
            
            # Keep the server running
            while server.running:
                await asyncio.sleep(1)
                
            await runner.cleanup()
    finally:
        await server.shutdown()

if __name__ == "__main__":
    asyncio.run(main())


noch zu implementieren:
async def _handle_list_nodes(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the list_nodes tool.
    
    Args:
        arguments: Arguments for the tool
        
    Returns:
        List of available nodes
    """
    node_type = arguments.get("type")
    include_custom = arguments.get("include_custom", True)
    
    try:
        async with self.session.get(f"{self.n8n_url}/api/v1/nodes") as response:
            if response.status == 200:
                nodes_data = await response.json()
                
                # Filter nodes
                filtered_nodes = []
                for node in nodes_data.get('data', []):
                    # Filter by type
                    if node_type and node.get('type') != node_type:
                        continue
                    
                    # Filter custom nodes
                    if not include_custom and node.get('custom', False):
                        continue
                    
                    filtered_nodes.append(node)
                
                return {"nodes": filtered_nodes, "total": len(filtered_nodes)}
            else:
                error_text = await response.text()
                logger.error(f"Error listing nodes: {response.status} - {error_text}")
                raise Exception(f"Error listing nodes: {error_text}")
    except Exception as e:
        logger.error(f"Error listing nodes: {e}")
        raise

async def _handle_configure_node(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the configure_node tool.
    
    Args:
        arguments: Arguments for the tool
        
    Returns:
        The updated workflow with the configured node
    """
    workflow_id = arguments.get("workflow_id")
    if not workflow_id:
        raise ValueError("workflow_id is required")
    
    node_id = arguments.get("node_id")
    if not node_id:
        raise ValueError("node_id is required")
    
    try:
        # Get current workflow
        current_workflow = await self._fetch_workflow(workflow_id)
        
        # Find the node to configure
        nodes = current_workflow.get('nodes', [])
        node_index = None
        for i, node in enumerate(nodes):
            if node.get('id') == node_id:
                node_index = i
                break
        
        if node_index is None:
            raise ValueError(f"Node with ID {node_id} not found in workflow {workflow_id}")
        
        # Update node configuration
        updated_node = nodes[node_index].copy()
        
        # Update node fields
        if "name" in arguments:
            updated_node['name'] = arguments["name"]
        
        if "type" in arguments:
            updated_node['type'] = arguments["type"]
        
        if "position" in arguments:
            updated_node['position'] = arguments["position"]
        
        if "parameters" in arguments:
            updated_node['parameters'] = arguments["parameters"]
        
        if "credentials" in arguments:
            updated_node['credentials'] = arguments["credentials"]
        
        # Update node in workflow
        nodes[node_index] = updated_node
        
        # Update workflow
        update_args = {
            "workflow_id": workflow_id,
            "nodes": nodes,
            "connections": current_workflow.get('connections', {})
        }
        
        result = await self._handle_update_workflow(update_args)
        
        return {
            "success": True,
            "node": updated_node,
            "workflow": result.get("workflow", {})
        }
    except Exception as e:
        logger.error(f"Error configuring node {node_id} in workflow {workflow_id}: {e}")
        raise

async def _handle_create_custom_node(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the create_custom_node tool.
    
    Args:
        arguments: Arguments for the tool
        
    Returns:
        The created custom node
    """
    name = arguments.get("name")
    if not name:
        raise ValueError("name is required")
    
    display_name = arguments.get("display_name")
    if not display_name:
        raise ValueError("display_name is required")
    
    properties = arguments.get("properties")
    if not properties:
        raise ValueError("properties is required")
    
    code = arguments.get("code")
    if not code:
        raise ValueError("code is required")
    
    try:
        # Check if n8n supports custom nodes via API
        try:
            # Try to use n8n's custom nodes API if available
            payload = {
                "name": name,
                "displayName": display_name,
                "description": arguments.get("description", ""),
                "icon": arguments.get("icon", "file:node.svg"),
                "properties": properties,
                "inputs": arguments.get("inputs", [{"name": "main", "type": "main"}]),
                "outputs": arguments.get("outputs", [{"name": "main", "type": "main"}]),
                "code": code
            }
            
            async with self.session.post(
                f"{self.n8n_url}/api/v1/custom-nodes",
                json=payload
            ) as response:
                if response.status in (200, 201):
                    custom_node = await response.json()
                    return {"success": True, "node": custom_node}
                else:
                    # If API not available, fall back to file-based approach
                    raise Exception("API not available")
                
        except Exception:
            # Fall back to creating a custom node via file system
            # Note: This requires n8n to be configured to load custom nodes from a specific directory
            # and the MCP server needs access to this directory

            # Generate a unique ID for the node
            node_id = str(uuid.uuid4())
            
            # Create a node package structure
            node_directory = f"/tmp/n8n-custom-nodes/{name}"
            os.makedirs(node_directory, exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": f"n8n-nodes-{name}",
                "version": "1.0.0",
                "description": arguments.get("description", "Custom node created via MCP"),
                "main": "dist/nodes/index.js",
                "scripts": {
                    "build": "tsc",
                    "dev": "tsc --watch"
                },
                "keywords": ["n8n", "node", "custom"],
                "author": "MCP Server",
                "license": "MIT",
                "dependencies": {
                    "n8n-core": "^0.125.0",
                    "n8n-workflow": "^0.107.0"
                },
                "devDependencies": {
                    "typescript": "^4.7.2"
                },
                "n8n": {
                    "nodes": [
                        f"{name}"
                    ]
                }
            }
            
            with open(f"{node_directory}/package.json", "w") as f:
                json.dump(package_json, f, indent=2)
            
            # Create TypeScript definition
            typescript_code = f"""
import {{ IExecuteFunctions }} from 'n8n-core';
import {{
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
}} from 'n8n-workflow';

export class {display_name.replace(' ', '')} implements INodeType {{
    description: INodeTypeDescription = {{
        displayName: '{display_name}',
        name: '{name}',
        icon: '{arguments.get("icon", "file:node.svg")}',
        group: ['transform'],
        version: 1,
        description: '{arguments.get("description", "Custom node created via MCP")}',
        defaults: {{
            name: '{display_name}',
        }},
        inputs: {json.dumps(arguments.get("inputs", [{"name": "main", "type": "main"}]))},
        outputs: {json.dumps(arguments.get("outputs", [{"name": "main", "type": "main"}]))},
        properties: {json.dumps(properties)},
    }};
    
    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {{
        // User-provided code begins here
        {code}
        // User-provided code ends here
    }}
}}
"""
            
            # Create node.ts file
            os.makedirs(f"{node_directory}/nodes", exist_ok=True)
            with open(f"{node_directory}/nodes/{name}.node.ts", "w") as f:
                f.write(typescript_code)
            
            # Create index.ts
            with open(f"{node_directory}/nodes/index.ts", "w") as f:
                f.write(f"import {{ {display_name.replace(' ', '')} }} from './{name}.node';\n\nexport {{ {display_name.replace(' ', '')} }};")
            
            # Create tsconfig.json
            tsconfig = {
                "compilerOptions": {
                    "target": "es2019",
                    "module": "commonjs",
                    "outDir": "./dist",
                    "rootDir": "./",
                    "strict": true,
                    "esModuleInterop": true,
                    "skipLibCheck": true
                }
            }
            
            with open(f"{node_directory}/tsconfig.json", "w") as f:
                json.dump(tsconfig, f, indent=2)
            
            # Compile the TypeScript code
            import subprocess
            try:
                subprocess.run(["npm", "install"], cwd=node_directory, check=True)
                subprocess.run(["npm", "run", "build"], cwd=node_directory, check=True)
            except subprocess.CalledProcessError as e:
                raise Exception(f"Error building custom node: {e}")
            
            # Return information about the created node
            return {
                "success": True,
                "node": {
                    "id": node_id,
                    "name": name,
                    "displayName": display_name,
                    "description": arguments.get("description", ""),
                    "directory": node_directory
                },
                "message": "Custom node created. Restart n8n to load the new node."
            }
    except Exception as e:
        logger.error(f"Error creating custom node: {e}")
        raise

async def _handle_update_custom_node(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the update_custom_node tool.
    
    Args:
        arguments: Arguments for the tool
        
    Returns:
        The updated custom node
    """
    node_id = arguments.get("node_id")
    if not node_id:
        raise ValueError("node_id is required")
    
    try:
        # Similar to create_custom_node but updating an existing node
        # This will depend on how the n8n instance is configured
        # For file-based custom nodes, we would need to find the node directory and update files
        
        # Try API approach first
        try:
            payload = {k: v for k, v in arguments.items() if k != "node_id"}
            
            async with self.session.put(
                f"{self.n8n_url}/api/v1/custom-nodes/{node_id}",
                json=payload
            ) as response:
                if response.status == 200:
                    custom_node = await response.json()
                    return {"success": True, "node": custom_node}
                else:
                    # If API not available, fall back to file-based approach
                    raise Exception("API not available")
        
        except Exception:
            # Here we would need to implement file-based update
            # This is just a placeholder that would need to be customized
            # based on how n8n is configured
            return {
                "success": False,
                "message": "Updating custom nodes via file system is not implemented. Please use the n8n API or update the files manually."
            }
    except Exception as e:
        logger.error(f"Error updating custom node {node_id}: {e}")
        raise

async def _handle_delete_custom_node(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the delete_custom_node tool.
    
    Args:
        arguments: Arguments for the tool
        
    Returns:
        Success message
    """
    node_id = arguments.get("node_id")
    if not node_id:
        raise ValueError("node_id is required")
    
    try:
        # Try API approach first
        try:
            async with self.session.delete(
                f"{self.n8n_url}/api/v1/custom-nodes/{node_id}"
            ) as response:
                if response.status in (200, 204):
                    return {"success": True, "message": f"Custom node {node_id} deleted"}
                else:
                    # If API not available, fall back to file-based approach
                    raise Exception("API not available")
        
        except Exception:
            # Here we would need to implement file-based deletion
            # This is just a placeholder that would need to be customized
            return {
                "success": False,
                "message": "Deleting custom nodes via file system is not implemented. Please use the n8n API or delete the files manually."
            }
    except Exception as e:
        logger.error(f"Error deleting custom node {node_id}: {e}")
        raise



async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call a tool.
    
    Args:
        tool_name: Name of the tool
        arguments: Arguments for the tool
        
    Returns:
        Result of the tool call
    """
    logger.info(f"Calling tool {tool_name} with arguments: {json.dumps(arguments)}")
    
    # Log the audit event
    self.audit_logger.log(
        event=f"call_tool:{tool_name}",
        user=None,
        details={"arguments": arguments},
    )
    
    # Find the tool
    tool = next((t for t in self.tools if t.name == tool_name), None)
    if not tool:
        raise ValueError(f"Tool not found: {tool_name}")
    
    # Record start time
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Handle standard workflow tools
        if tool_name == "list_workflows":
            result = await self._handle_list_workflows(arguments)
        elif tool_name == "get_workflow":
            result = await self._handle_get_workflow(arguments)
        elif tool_name == "run_workflow":
            result = await self._handle_run_workflow(arguments)
        elif tool_name == "create_workflow":
            result = await self._handle_create_workflow(arguments)
        elif tool_name == "update_workflow":
            result = await self._handle_update_workflow(arguments)
        elif tool_name == "delete_workflow":
            result = await self._handle_delete_workflow(arguments)
        elif tool_name == "activate_workflow":
            result = await self._handle_activate_workflow(arguments)
        elif tool_name == "deactivate_workflow":
            result = await self._handle_deactivate_workflow(arguments)
        # Handle node-related tools
        elif tool_name == "list_nodes":
            result = await self._handle_list_nodes(arguments)
        elif tool_name == "configure_node":
            result = await self._handle_configure_node(arguments)
        elif tool_name == "create_custom_node":
            result = await self._handle_create_custom_node(arguments)
        elif tool_name == "update_custom_node":
            result = await self._handle_update_custom_node(arguments)
        elif tool_name == "delete_custom_node":
            result = await self._handle_delete_custom_node(arguments)
        # Handle workflow execution tools
        elif tool_name.startswith("workflow_"):
            workflow_id = self._get_workflow_id_by_tool_name(tool_name)
            if workflow_id:
                result = await self._execute_workflow(workflow_id, arguments)
            else:
                raise ValueError(f"No matching workflow for tool: {tool_name}")
        else:
            raise ValueError(f"Tool not implemented: {tool_name}")
        
        # Record end time and metrics
        end_time = asyncio.get_event_loop().time()
        self.metrics_collector.record_request(
            method=tool_name,
            success=True,
            response_time=end_time - start_time,
        )
        
        return result
    except Exception as e:
        # Record end time and metrics for failures
        end_time = asyncio.get_event_loop().time()
        self.metrics_collector.record_request(
            method=tool_name,
            success=False,
            response_time=end_time - start_time,
        )
        
        # Log the error
        logger.error(f"Error calling tool {tool_name}: {e}")
        
        # Log the audit event
        self.audit_logger.log(
            event=f"call_tool_error:{tool_name}",
            user=None,
            details={"arguments": arguments, "error": str(e)},
        )
        
        raise


4. Demonstration: Beispiele für die Nutzung der neuen Node-Funktionen
Liste aller verfügbaren Nodes anzeigen
json{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "list_nodes",
    "arguments": {
      "include_custom": true
    }
  }
}
Konfiguration eines bestehenden Nodes in einem Workflow
json{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "mcp.callTool",
  "params": {
    "name": "configure_node",
    "arguments": {
      "workflow_id": "123",
      "node_id": "456",
      "name": "HTTP Request",
      "parameters": {
        "url": "https://api.example.com/data",
        "method": "GET",
        "authentication": "basicAuth",
        "options": {
          "timeout": 5000
        }
      }
    }
  }
}
Erstellen eines benutzerdefinierten Nodes
json{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "mcp.callTool",
  "params": {
    "name": "create_custom_node",
    "arguments": {
      "name": "my-data-processor",
      "display_name": "Data Processor",
      "description": "A custom node for processing data",
      "icon": "file:processor.svg",
      "properties": [
        {
          "displayName": "Operation",
          "name": "operation",
          "type": "options",
          "options": [
            {
              "name": "Transform",
              "value": "transform"
            },
            {
              "name": "Filter",
              "value": "filter"
            },
            {
              "name": "Aggregate",
              "value": "aggregate"
            }
          ],
          "default": "transform",
          "description": "The operation to perform on the data"
        },
        {
          "displayName": "Fields",
          "name": "fields",
          "type": "string",
          "default": "",
          "description": "Comma-separated list of fields to process"
        }
      ],
      "code": "const items = this.getInputData();\nconst operation = this.getNodeParameter('operation', 0) as string;\nconst fields = this.getNodeParameter('fields', 0) as string;\n\nconst fieldList = fields.split(',').map(f => f.trim());\n\nconst returnData: INodeExecutionData[] = [];\n\nfor (let i = 0; i < items.length; i++) {\n  const item = items[i];\n  const newItem: INodeExecutionData = { json: {} };\n  \n  if (operation === 'transform') {\n    // Transform operation\n    for (const field of fieldList) {\n      if (item.json[field] !== undefined) {\n        newItem.json[field] = item.json[field].toString().toUpperCase();\n      }\n    }\n  } else if (operation === 'filter') {\n    // Filter operation\n    let include = true;\n    for (const field of fieldList) {\n      if (item.json[field] === undefined || item.json[field] === '') {\n        include = false;\n        break;\n      }\n    }\n    if (include) {\n      newItem.json = { ...item.json };\n    } else {\n      continue;\n    }\n  } else if (operation === 'aggregate') {\n    // Aggregate operation\n    let sum = 0;\n    for (const field of fieldList) {\n      if (typeof item.json[field] === 'number') {\n        sum += item.json[field];\n      }\n    }\n    newItem.json = { sum };\n  }\n  \n  returnData.push(newItem);\n}\n\nreturn [returnData];"
    }
  }
}
5. Hinweise zur Implementierung

API vs. Dateisystem: Die Implementierung bietet zwei Ansätze:

API-basiert: Wenn die n8n-Instanz eine API für benutzerdefinierte Nodes anbietet
Dateisystem-basiert: Erstellen von Node-Dateien in einem Verzeichnis, das n8n überwacht


Berechtigungen: Für die dateisystembasierte Methode benötigt der MCP-Server Schreibzugriff auf das n8n-Custom-Nodes-Verzeichnis. Dies erfordert möglicherweise zusätzliche Konfiguration.
Node-Entwicklung: Die Erstellung benutzerdefinierter Nodes erfordert Kenntnisse des n8n-Node-Entwicklungsframeworks. Der bereitgestellte Code generiert TypeScript-Dateien, die den n8n-Standards entsprechen.
Neustarts: Nach dem Erstellen oder Aktualisieren benutzerdefinierter Nodes muss n8n möglicherweise neu gestartet werden, damit die Änderungen wirksam werden.

6. Sicherheitsüberlegungen
Bei der Implementierung dieser Funktionen sollten folgende Sicherheitsaspekte berücksichtigt werden:

Code-Ausführung: Das Erstellen benutzerdefinierter Nodes ermöglicht die Ausführung von benutzerdefiniertem Code auf dem n8n-Server. Dies sollte nur autorisierten Benutzern mit entsprechenden Berechtigungen erlaubt sein.
Eingabevalidierung: Alle Eingaben, insbesondere der benutzerdefinierte Code, sollten auf potenziell schädliche Inhalte überprüft werden.
Ressourcenbeschränkungen: Implementieren Sie Limits für die Anzahl und Größe der benutzerdefinierten Nodes, um Denial-of-Service-Angriffe zu verhindern.
Isolierung: Idealerweise sollten benutzerdefinierte Nodes in einer isolierten Umgebung ausgeführt werden, um mögliche Schäden durch schädlichen Code zu begrenzen.

Diese Erweiterungen ermöglichen es dem n8n MCP Server, n8n-Nodes zu konfigurieren und neue benutzerdefinierte Nodes zu erstellen, was die Flexibilität und den Nutzen des Systems erheblich steigert.
