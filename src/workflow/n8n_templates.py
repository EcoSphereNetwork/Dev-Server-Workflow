"""
n8n Workflow Templates.

This module provides templates and utilities for working with n8n workflows.
"""

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from src.connectors.base import ConnectorConfig, ConnectorError, HttpConnector
from src.core.logging import get_logger

# Set up logging
logger = get_logger(__name__)


@dataclass
class N8nWorkflowTemplate:
    """Template for an n8n workflow."""
    
    id: str
    name: str
    description: Optional[str] = None
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    connections: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the template to a dictionary.
        
        Returns:
            Dictionary representation of the template.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": self.nodes,
            "connections": self.connections,
            "settings": self.settings,
            "tags": self.tags,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "N8nWorkflowTemplate":
        """Create a template from a dictionary.
        
        Args:
            data: Dictionary representation of the template.
            
        Returns:
            N8n workflow template.
        """
        created_at = data.get("createdAt") or data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        elif not isinstance(created_at, datetime):
            created_at = datetime.now()
        
        updated_at = data.get("updatedAt") or data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        elif not isinstance(updated_at, datetime):
            updated_at = datetime.now()
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled Workflow"),
            description=data.get("description"),
            nodes=data.get("nodes", []),
            connections=data.get("connections", {}),
            settings=data.get("settings", {}),
            tags=data.get("tags", []),
            created_at=created_at,
            updated_at=updated_at,
        )
    
    def to_n8n_format(self) -> Dict[str, Any]:
        """Convert the template to n8n workflow format.
        
        Returns:
            n8n workflow data.
        """
        # Convert connections to n8n format
        connections = []
        for source_node_id, targets in self.connections.items():
            for target in targets:
                connections.append({
                    "node": source_node_id,
                    "type": target.get("type", "main"),
                    "index": target.get("index", 0),
                    "target_node": target.get("target_node"),
                    "target_type": target.get("target_type", "main"),
                    "target_index": target.get("target_index", 0),
                })
        
        return {
            "id": self.id,
            "name": self.name,
            "active": True,
            "nodes": self.nodes,
            "connections": {
                "main": connections
            },
            "settings": self.settings,
            "tags": self.tags,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_n8n_format(cls, data: Dict[str, Any]) -> "N8nWorkflowTemplate":
        """Create a template from n8n workflow format.
        
        Args:
            data: n8n workflow data.
            
        Returns:
            N8n workflow template.
        """
        # Convert n8n connections to our format
        connections = {}
        for connection in data.get("connections", {}).get("main", []):
            source_node_id = connection.get("node")
            if source_node_id not in connections:
                connections[source_node_id] = []
            
            connections[source_node_id].append({
                "type": connection.get("type", "main"),
                "index": connection.get("index", 0),
                "target_node": connection.get("target_node"),
                "target_type": connection.get("target_type", "main"),
                "target_index": connection.get("target_index", 0),
            })
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled Workflow"),
            description=data.get("description"),
            nodes=data.get("nodes", []),
            connections=connections,
            settings=data.get("settings", {}),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data.get("createdAt", datetime.now().isoformat()).replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data.get("updatedAt", datetime.now().isoformat()).replace("Z", "+00:00")),
        )
    
    def save_to_file(self, file_path: str) -> None:
        """Save the template to a file.
        
        Args:
            file_path: Path to save the file.
        """
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> "N8nWorkflowTemplate":
        """Load a template from a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            N8n workflow template.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        
        return cls.from_dict(data)


class N8nConnector(HttpConnector):
    """Connector for n8n API."""
    
    def __init__(self, config: ConnectorConfig):
        """Initialize the n8n connector.
        
        Args:
            config: Connector configuration.
        """
        super().__init__(config)
        
        # Set default base URL if not provided
        if not config.base_url:
            config.base_url = "http://localhost:5678/api/v1"
        
        # Set default headers
        if config.api_key:
            config.headers["X-N8N-API-KEY"] = config.api_key
    
    async def _test_connection(self) -> None:
        """Test the connection to n8n.
        
        Raises:
            ConnectorError: If the connection test fails.
        """
        try:
            # Make a simple request to test the connection
            await self.request("GET", "workflows")
        except Exception as e:
            raise ConnectorError(
                f"Failed to connect to n8n: {e}",
                connector_type=self.connector_type,
                service_name=self.service_name,
                cause=e,
            )
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows.
        
        Returns:
            List of workflows.
            
        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", "workflows")
        return response["data"]["data"]
    
    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow.
            
        Returns:
            Workflow data.
            
        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", f"workflows/{workflow_id}")
        return response["data"]
    
    async def create_workflow(self, workflow: Union[Dict[str, Any], N8nWorkflowTemplate]) -> Dict[str, Any]:
        """Create a new workflow.
        
        Args:
            workflow: Workflow data or template.
            
        Returns:
            Created workflow data.
            
        Raises:
            ConnectorError: If the request fails.
        """
        if isinstance(workflow, N8nWorkflowTemplate):
            workflow_data = workflow.to_n8n_format()
        else:
            workflow_data = workflow
        
        response = await self.request("POST", "workflows", json=workflow_data)
        return response["data"]
    
    async def update_workflow(self, workflow_id: str, workflow: Union[Dict[str, Any], N8nWorkflowTemplate]) -> Dict[str, Any]:
        """Update a workflow.
        
        Args:
            workflow_id: ID of the workflow to update.
            workflow: Updated workflow data or template.
            
        Returns:
            Updated workflow data.
            
        Raises:
            ConnectorError: If the request fails.
        """
        if isinstance(workflow, N8nWorkflowTemplate):
            workflow_data = workflow.to_n8n_format()
        else:
            workflow_data = workflow
        
        response = await self.request("PUT", f"workflows/{workflow_id}", json=workflow_data)
        return response["data"]
    
    async def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete a workflow.
        
        Args:
            workflow_id: ID of the workflow to delete.
            
        Returns:
            Response data.
            
        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("DELETE", f"workflows/{workflow_id}")
        return response["data"]
    
    async def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Activate a workflow.
        
        Args:
            workflow_id: ID of the workflow to activate.
            
        Returns:
            Response data.
            
        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("POST", f"workflows/{workflow_id}/activate")
        return response["data"]
    
    async def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Deactivate a workflow.
        
        Args:
            workflow_id: ID of the workflow to deactivate.
            
        Returns:
            Response data.
            
        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("POST", f"workflows/{workflow_id}/deactivate")
        return response["data"]
    
    async def execute_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to execute.
            data: Input data for the workflow.
            
        Returns:
            Execution result.
            
        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("POST", f"workflows/{workflow_id}/execute", json=data or {})
        return response["data"]
    
    async def list_executions(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflow executions.
        
        Args:
            workflow_id: Optional ID of the workflow to filter by.
            
        Returns:
            List of executions.
            
        Raises:
            ConnectorError: If the request fails.
        """
        params = {}
        if workflow_id:
            params["workflowId"] = workflow_id
        
        response = await self.request("GET", "executions", params=params)
        return response["data"]["data"]
    
    async def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get an execution by ID.
        
        Args:
            execution_id: ID of the execution.
            
        Returns:
            Execution data.
            
        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", f"executions/{execution_id}")
        return response["data"]
    
    async def delete_execution(self, execution_id: str) -> Dict[str, Any]:
        """Delete an execution.
        
        Args:
            execution_id: ID of the execution to delete.
            
        Returns:
            Response data.
            
        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("DELETE", f"executions/{execution_id}")
        return response["data"]


# Workflow template for data processing
data_processing_template = N8nWorkflowTemplate(
    id="data-processing-template",
    name="Data Processing Template",
    description="Template for processing data from various sources",
    nodes=[
        {
            "id": "start",
            "name": "Start",
            "type": "n8n-nodes-base.start",
            "typeVersion": 1,
            "position": [100, 300]
        },
        {
            "id": "http-request",
            "name": "HTTP Request",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 1,
            "position": [300, 300],
            "parameters": {
                "url": "https://api.example.com/data",
                "method": "GET",
                "authentication": "none",
                "options": {}
            }
        },
        {
            "id": "function",
            "name": "Transform Data",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [500, 300],
            "parameters": {
                "functionCode": "// Transform the data\nconst data = $input.all()[0].json;\n\n// Example transformation\nconst transformed = data.map(item => ({\n  id: item.id,\n  name: item.name,\n  value: item.value * 2,\n  category: item.type || 'unknown'\n}));\n\nreturn [{json: transformed}];"
            }
        },
        {
            "id": "if",
            "name": "Filter Data",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [700, 300],
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json[\"value\"]}}",
                            "operation": "larger",
                            "value2": 100
                        }
                    ]
                }
            }
        },
        {
            "id": "write-file",
            "name": "Write to File",
            "type": "n8n-nodes-base.writeFile",
            "typeVersion": 1,
            "position": [900, 200],
            "parameters": {
                "fileName": "={{$json[\"id\"]}}.json",
                "fileContent": "={{JSON.stringify($json, null, 2)}}",
                "directory": "/data/processed"
            }
        },
        {
            "id": "no-op",
            "name": "Skip",
            "type": "n8n-nodes-base.noOp",
            "typeVersion": 1,
            "position": [900, 400]
        }
    ],
    connections={
        "start": [
            {
                "target_node": "http-request"
            }
        ],
        "http-request": [
            {
                "target_node": "function"
            }
        ],
        "function": [
            {
                "target_node": "if"
            }
        ],
        "if": [
            {
                "index": 0,  # true
                "target_node": "write-file"
            },
            {
                "index": 1,  # false
                "target_node": "no-op"
            }
        ]
    },
    settings={
        "saveExecutionProgress": true,
        "saveManualExecutions": true,
        "callerPolicy": "workflowsFromSameOwner"
    },
    tags=["template", "data-processing"]
)

# Workflow template for API integration
api_integration_template = N8nWorkflowTemplate(
    id="api-integration-template",
    name="API Integration Template",
    description="Template for integrating with external APIs",
    nodes=[
        {
            "id": "webhook",
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [100, 300],
            "webhookId": "api-integration-webhook",
            "parameters": {
                "path": "api-integration",
                "responseMode": "responseNode",
                "options": {}
            }
        },
        {
            "id": "set-variables",
            "name": "Set Variables",
            "type": "n8n-nodes-base.set",
            "typeVersion": 1,
            "position": [300, 300],
            "parameters": {
                "values": {
                    "string": [
                        {
                            "name": "apiKey",
                            "value": "YOUR_API_KEY"
                        },
                        {
                            "name": "baseUrl",
                            "value": "https://api.example.com"
                        }
                    ]
                }
            }
        },
        {
            "id": "http-request",
            "name": "API Request",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 1,
            "position": [500, 300],
            "parameters": {
                "url": "={{$node[\"set-variables\"].json[\"baseUrl\"]}}/data",
                "method": "POST",
                "authentication": "headerAuth",
                "headerAuthKey": "X-API-Key",
                "headerAuthValue": "={{$node[\"set-variables\"].json[\"apiKey\"]}}",
                "options": {},
                "bodyParametersUi": {
                    "parameter": [
                        {
                            "name": "data",
                            "value": "={{$json[\"data\"]}}"
                        }
                    ]
                }
            }
        },
        {
            "id": "function",
            "name": "Process Response",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [700, 300],
            "parameters": {
                "functionCode": "// Process the API response\nconst response = $input.all()[0].json;\n\n// Check for errors\nif (response.error) {\n  return [\n    {\n      json: {\n        success: false,\n        error: response.error,\n        message: response.message || 'API request failed'\n      }\n    }\n  ];\n}\n\n// Process successful response\nreturn [\n  {\n    json: {\n      success: true,\n      data: response.data,\n      timestamp: new Date().toISOString()\n    }\n  }\n];"
            }
        },
        {
            "id": "respond-to-webhook",
            "name": "Respond to Webhook",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [900, 300],
            "parameters": {}
        }
    ],
    connections={
        "webhook": [
            {
                "target_node": "set-variables"
            }
        ],
        "set-variables": [
            {
                "target_node": "http-request"
            }
        ],
        "http-request": [
            {
                "target_node": "function"
            }
        ],
        "function": [
            {
                "target_node": "respond-to-webhook"
            }
        ]
    },
    settings={
        "saveExecutionProgress": true,
        "saveManualExecutions": true,
        "callerPolicy": "workflowsFromSameOwner"
    },
    tags=["template", "api-integration"]
)

# Workflow template for scheduled tasks
scheduled_tasks_template = N8nWorkflowTemplate(
    id="scheduled-tasks-template",
    name="Scheduled Tasks Template",
    description="Template for running scheduled tasks",
    nodes=[
        {
            "id": "schedule",
            "name": "Schedule",
            "type": "n8n-nodes-base.cron",
            "typeVersion": 1,
            "position": [100, 300],
            "parameters": {
                "triggerTimes": {
                    "item": [
                        {
                            "mode": "everyDay"
                        }
                    ]
                }
            }
        },
        {
            "id": "function",
            "name": "Prepare Tasks",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [300, 300],
            "parameters": {
                "functionCode": "// Define tasks to run\nconst tasks = [\n  { id: 1, name: 'Backup Database', command: 'backup-db' },\n  { id: 2, name: 'Clean Temp Files', command: 'clean-temp' },\n  { id: 3, name: 'Update Indexes', command: 'update-indexes' }\n];\n\n// Return tasks as separate items\nreturn tasks.map(task => ({ json: task }));"
            }
        },
        {
            "id": "split-in-batches",
            "name": "Split in Batches",
            "type": "n8n-nodes-base.splitInBatches",
            "typeVersion": 1,
            "position": [500, 300],
            "parameters": {
                "batchSize": 1
            }
        },
        {
            "id": "execute-command",
            "name": "Execute Command",
            "type": "n8n-nodes-base.executeCommand",
            "typeVersion": 1,
            "position": [700, 300],
            "parameters": {
                "command": "={{$json[\"command\"]}}",
                "executeInShell": true
            }
        },
        {
            "id": "merge",
            "name": "Merge Results",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 2,
            "position": [900, 300],
            "parameters": {
                "mode": "mergeByPosition"
            }
        },
        {
            "id": "send-email",
            "name": "Send Email Report",
            "type": "n8n-nodes-base.emailSend",
            "typeVersion": 1,
            "position": [1100, 300],
            "parameters": {
                "fromEmail": "reports@example.com",
                "toEmail": "admin@example.com",
                "subject": "Daily Task Report - {{$now.format(\"YYYY-MM-DD\")}}",
                "text": "=Task execution report:\n\n{{$json[\"results\"].map(item => `${item.name}: ${item.exitCode === 0 ? 'Success' : 'Failed'}`).join('\\n')}}",
                "options": {}
            }
        }
    ],
    connections={
        "schedule": [
            {
                "target_node": "function"
            }
        ],
        "function": [
            {
                "target_node": "split-in-batches"
            }
        ],
        "split-in-batches": [
            {
                "target_node": "execute-command"
            }
        ],
        "execute-command": [
            {
                "target_node": "split-in-batches"
            },
            {
                "index": 1,
                "target_node": "merge"
            }
        ],
        "merge": [
            {
                "target_node": "send-email"
            }
        ]
    },
    settings={
        "saveExecutionProgress": true,
        "saveManualExecutions": false,
        "callerPolicy": "workflowsFromSameOwner",
        "timezone": "UTC"
    },
    tags=["template", "scheduled-tasks"]
)

# Workflow template for data synchronization
data_sync_template = N8nWorkflowTemplate(
    id="data-sync-template",
    name="Data Synchronization Template",
    description="Template for synchronizing data between systems",
    nodes=[
        {
            "id": "schedule",
            "name": "Schedule",
            "type": "n8n-nodes-base.cron",
            "typeVersion": 1,
            "position": [100, 300],
            "parameters": {
                "triggerTimes": {
                    "item": [
                        {
                            "mode": "everyX",
                            "unit": "hours",
                            "value": 1
                        }
                    ]
                }
            }
        },
        {
            "id": "source-db",
            "name": "Source Database",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 1,
            "position": [300, 300],
            "credentials": {
                "postgres": "source-db-credentials"
            },
            "parameters": {
                "operation": "executeQuery",
                "query": "SELECT * FROM users WHERE updated_at > NOW() - INTERVAL '1 hour'"
            }
        },
        {
            "id": "transform",
            "name": "Transform Data",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [500, 300],
            "parameters": {
                "functionCode": "// Transform data for target system\nconst items = $input.all();\n\nreturn items.map(item => {\n  const user = item.json;\n  \n  return {\n    json: {\n      external_id: user.id,\n      username: user.username,\n      email: user.email,\n      first_name: user.first_name,\n      last_name: user.last_name,\n      status: user.active ? 'active' : 'inactive',\n      metadata: {\n        source: 'postgres',\n        last_sync: new Date().toISOString()\n      }\n    }\n  };\n});"
            }
        },
        {
            "id": "target-api",
            "name": "Target API",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 1,
            "position": [700, 300],
            "parameters": {
                "url": "https://api.target-system.com/users",
                "method": "POST",
                "authentication": "headerAuth",
                "headerAuthKey": "X-API-Key",
                "headerAuthValue": "YOUR_API_KEY",
                "options": {},
                "bodyParametersUi": {
                    "parameter": [
                        {
                            "name": "user",
                            "value": "={{$json}}"
                        }
                    ]
                }
            }
        },
        {
            "id": "if",
            "name": "Check Success",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [900, 300],
            "parameters": {
                "conditions": {
                    "number": [
                        {
                            "value1": "={{$json[\"statusCode\"]}}",
                            "operation": "equal",
                            "value2": 200
                        }
                    ]
                }
            }
        },
        {
            "id": "success-log",
            "name": "Log Success",
            "type": "n8n-nodes-base.functionItem",
            "typeVersion": 1,
            "position": [1100, 200],
            "parameters": {
                "functionCode": "// Log successful sync\nconsole.log(`Successfully synced user ${$json.external_id}`);\nreturn $input.item;"
            }
        },
        {
            "id": "error-log",
            "name": "Log Error",
            "type": "n8n-nodes-base.functionItem",
            "typeVersion": 1,
            "position": [1100, 400],
            "parameters": {
                "functionCode": "// Log sync error\nconsole.error(`Failed to sync user ${$json.external_id}: ${$json.error || 'Unknown error'}`);\nreturn $input.item;"
            }
        }
    ],
    connections={
        "schedule": [
            {
                "target_node": "source-db"
            }
        ],
        "source-db": [
            {
                "target_node": "transform"
            }
        ],
        "transform": [
            {
                "target_node": "target-api"
            }
        ],
        "target-api": [
            {
                "target_node": "if"
            }
        ],
        "if": [
            {
                "index": 0,  # true
                "target_node": "success-log"
            },
            {
                "index": 1,  # false
                "target_node": "error-log"
            }
        ]
    },
    settings={
        "saveExecutionProgress": true,
        "saveManualExecutions": true,
        "callerPolicy": "workflowsFromSameOwner",
        "timezone": "UTC"
    },
    tags=["template", "data-sync"]
)

# Workflow template for notification system
notification_template = N8nWorkflowTemplate(
    id="notification-template",
    name="Notification System Template",
    description="Template for sending notifications through multiple channels",
    nodes=[
        {
            "id": "webhook",
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [100, 300],
            "webhookId": "notification-webhook",
            "parameters": {
                "path": "send-notification",
                "responseMode": "responseNode",
                "options": {}
            }
        },
        {
            "id": "validate",
            "name": "Validate Input",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [300, 300],
            "parameters": {
                "functionCode": "// Validate notification input\nconst input = $input.all()[0].json;\n\n// Check required fields\nconst errors = [];\nif (!input.message) errors.push('Message is required');\nif (!input.channels || !Array.isArray(input.channels) || input.channels.length === 0) {\n  errors.push('At least one channel is required');\n}\n\nif (errors.length > 0) {\n  return [\n    {\n      json: {\n        success: false,\n        errors\n      }\n    }\n  ];\n}\n\n// Prepare notification for each channel\nconst channels = input.channels.map(channel => ({\n  json: {\n    ...input,\n    channel,\n    timestamp: new Date().toISOString()\n  }\n}));\n\nreturn channels;"
            }
        },
        {
            "id": "router",
            "name": "Route by Channel",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 1,
            "position": [500, 300],
            "parameters": {
                "rules": {
                    "rules": [
                        {
                            "value": "email",
                            "conditions": [
                                {
                                    "value1": "={{$json[\"channel\"]}}",
                                    "operation": "equal",
                                    "value2": "email"
                                }
                            ]
                        },
                        {
                            "value": "slack",
                            "conditions": [
                                {
                                    "value1": "={{$json[\"channel\"]}}",
                                    "operation": "equal",
                                    "value2": "slack"
                                }
                            ]
                        },
                        {
                            "value": "sms",
                            "conditions": [
                                {
                                    "value1": "={{$json[\"channel\"]}}",
                                    "operation": "equal",
                                    "value2": "sms"
                                }
                            ]
                        }
                    ]
                }
            }
        },
        {
            "id": "email",
            "name": "Send Email",
            "type": "n8n-nodes-base.emailSend",
            "typeVersion": 1,
            "position": [700, 100],
            "parameters": {
                "fromEmail": "={{$json[\"from\"] || \"notifications@example.com\"}}",
                "toEmail": "={{$json[\"to\"]}}",
                "subject": "={{$json[\"subject\"] || \"Notification\"}}",
                "text": "={{$json[\"message\"]}}",
                "options": {}
            }
        },
        {
            "id": "slack",
            "name": "Send Slack",
            "type": "n8n-nodes-base.slack",
            "typeVersion": 1,
            "position": [700, 300],
            "parameters": {
                "channel": "={{$json[\"to\"]}}",
                "text": "={{$json[\"message\"]}}",
                "otherOptions": {
                    "attachments": "={{$json[\"attachments\"]}}"
                }
            }
        },
        {
            "id": "sms",
            "name": "Send SMS",
            "type": "n8n-nodes-base.twilio",
            "typeVersion": 1,
            "position": [700, 500],
            "parameters": {
                "from": "={{$json[\"from\"]}}",
                "to": "={{$json[\"to\"]}}",
                "message": "={{$json[\"message\"]}}"
            }
        },
        {
            "id": "merge",
            "name": "Merge Results",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 2,
            "position": [900, 300],
            "parameters": {
                "mode": "mergeByPosition"
            }
        },
        {
            "id": "respond",
            "name": "HTTP Response",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [1100, 300],
            "parameters": {}
        }
    ],
    connections={
        "webhook": [
            {
                "target_node": "validate"
            }
        ],
        "validate": [
            {
                "target_node": "router"
            }
        ],
        "router": [
            {
                "index": 0,  # email
                "target_node": "email"
            },
            {
                "index": 1,  # slack
                "target_node": "slack"
            },
            {
                "index": 2,  # sms
                "target_node": "sms"
            }
        ],
        "email": [
            {
                "target_node": "merge"
            }
        ],
        "slack": [
            {
                "target_node": "merge"
            }
        ],
        "sms": [
            {
                "target_node": "merge"
            }
        ],
        "merge": [
            {
                "target_node": "respond"
            }
        ]
    },
    settings={
        "saveExecutionProgress": true,
        "saveManualExecutions": true,
        "callerPolicy": "workflowsFromSameOwner"
    },
    tags=["template", "notification"]
)

# List of all templates
templates = [
    data_processing_template,
    api_integration_template,
    scheduled_tasks_template,
    data_sync_template,
    notification_template
]

def get_template_by_id(template_id: str) -> Optional[N8nWorkflowTemplate]:
    """Get a template by ID.
    
    Args:
        template_id: ID of the template.
        
    Returns:
        Template if found, None otherwise.
    """
    for template in templates:
        if template.id == template_id:
            return template
    return None

def get_templates_by_tag(tag: str) -> List[N8nWorkflowTemplate]:
    """Get templates by tag.
    
    Args:
        tag: Tag to filter by.
        
    Returns:
        List of matching templates.
    """
    return [template for template in templates if tag in template.tags]

def save_templates_to_directory(directory: str) -> None:
    """Save all templates to a directory.
    
    Args:
        directory: Directory to save templates to.
    """
    os.makedirs(directory, exist_ok=True)
    
    for template in templates:
        file_path = os.path.join(directory, f"{template.id}.json")
        template.save_to_file(file_path)
        logger.info(f"Saved template to {file_path}")

def load_templates_from_directory(directory: str) -> List[N8nWorkflowTemplate]:
    """Load templates from a directory.
    
    Args:
        directory: Directory to load templates from.
        
    Returns:
        List of loaded templates.
    """
    loaded_templates = []
    
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return loaded_templates
    
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            try:
                template = N8nWorkflowTemplate.load_from_file(file_path)
                loaded_templates.append(template)
                logger.info(f"Loaded template from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load template from {file_path}: {e}")
    
    return loaded_templates