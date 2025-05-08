"""
Docker MCP server module.

This module implements a Model Context Protocol (MCP) server for Docker operations,
enabling AI agents to manage Docker containers and Docker Compose stacks.
"""

import asyncio
import signal
import sys
import os
import logging
import json
import time
from typing import List, Dict, Any, Optional
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from .handlers import DockerHandlers
from .auth import AuthManager
from .audit import AuditLogger
from .metrics import MetricsCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '../../../logs/docker_mcp.log'))
    ]
)
logger = logging.getLogger("docker-mcp")

# Initialize auth manager, audit logger, and metrics collector
auth_config_path = os.path.join(os.path.dirname(__file__), '../../../config/docker_mcp_auth.json')
auth_manager = AuthManager(auth_config_path)
audit_logger = AuditLogger()
metrics_collector = MetricsCollector()

# Create the server
server = Server("docker-mcp")


@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """Handle list_prompts request.
    
    Returns:
        List of available prompts
    """
    return [
        types.Prompt(
            name="deploy-stack",
            description="Generate and deploy a Docker stack based on requirements",
            arguments=[
                types.PromptArgument(
                    name="requirements",
                    description="Description of the desired Docker stack",
                    required=True
                ),
                types.PromptArgument(
                    name="project_name",
                    description="Name for the Docker Compose project",
                    required=True
                )
            ]
        ),
        types.Prompt(
            name="manage-containers",
            description="Manage Docker containers (list, start, stop, restart, remove)",
            arguments=[
                types.PromptArgument(
                    name="action",
                    description="Action to perform (list, start, stop, restart, remove)",
                    required=True
                ),
                types.PromptArgument(
                    name="container_name",
                    description="Name of the container to manage",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="manage-compose",
            description="Manage Docker Compose stacks (deploy, start, stop, restart, logs)",
            arguments=[
                types.PromptArgument(
                    name="action",
                    description="Action to perform (deploy, start, stop, restart, logs)",
                    required=True
                ),
                types.PromptArgument(
                    name="project_name",
                    description="Name of the Docker Compose project",
                    required=True
                ),
                types.PromptArgument(
                    name="compose_yaml",
                    description="Docker Compose YAML content (for deploy action)",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="authenticate",
            description="Authenticate with the Docker MCP server",
            arguments=[
                types.PromptArgument(
                    name="username",
                    description="Username",
                    required=True
                ),
                types.PromptArgument(
                    name="api_key",
                    description="API key",
                    required=True
                )
            ]
        ),
        types.Prompt(
            name="audit-logs",
            description="View audit logs for Docker operations",
            arguments=[
                types.PromptArgument(
                    name="username",
                    description="Filter by username",
                    required=False
                ),
                types.PromptArgument(
                    name="tool_name",
                    description="Filter by tool name",
                    required=False
                ),
                types.PromptArgument(
                    name="status",
                    description="Filter by status (success, error)",
                    required=False
                ),
                types.PromptArgument(
                    name="limit",
                    description="Maximum number of logs to return",
                    required=False
                )
            ]
        )
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: Dict[str, str] | None) -> types.GetPromptResult:
    """Handle get_prompt request.
    
    Args:
        name: Name of the prompt
        arguments: Prompt arguments
        
    Returns:
        Prompt result
    """
    if name == "deploy-stack":
        if not arguments or "requirements" not in arguments or "project_name" not in arguments:
            raise ValueError("Missing required arguments")

        system_message = (
            "You are a Docker deployment specialist. Generate appropriate Docker Compose YAML or "
            "container configurations based on user requirements. For simple single-container "
            "deployments, use the create-container tool. For multi-container deployments, generate "
            "a docker-compose.yml and use the deploy-compose tool. To access logs, first use the "
            "list-containers tool to discover running containers, then use the get-logs tool to "
            "retrieve logs for a specific container."
        )

        user_message = f"""Please help me deploy the following stack:
Requirements: {arguments['requirements']}
Project name: {arguments['project_name']}

Analyze if this needs a single container or multiple containers. Then:
1. For single container: Use the create-container tool with format:
{{
    "image": "image-name",
    "name": "container-name",
    "ports": {{"80": "80"}},
    "environment": {{"ENV_VAR": "value"}},
    "volumes": {{"/host/path": "/container/path"}}
}}

2. For multiple containers: Use the deploy-compose tool with format:
{{
    "project_name": "example-stack",
    "compose_yaml": "version: '3.8'\\nservices:\\n  service1:\\n    image: image1:latest\\n    ports:\\n      - '8080:80'"
}}"""

        return types.GetPromptResult(
            description="Generate and deploy a Docker stack",
            messages=[
                types.PromptMessage(
                    role="system",
                    content=types.TextContent(
                        type="text",
                        text=system_message
                    )
                ),
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=user_message
                    )
                )
            ]
        )
    elif name == "manage-containers":
        if not arguments or "action" not in arguments:
            raise ValueError("Missing required arguments")
            
        action = arguments["action"].lower()
        container_name = arguments.get("container_name", "")
        
        system_message = (
            "You are a Docker container management specialist. Help the user manage their Docker containers "
            "by using the appropriate tools based on their request."
        )
        
        user_message = f"""I need to {action} {'a' if action != 'list' else ''} Docker container{f' named {container_name}' if container_name and action != 'list' else ''}.

Available tools:
1. list-containers: List all Docker containers
2. get-logs: Get logs from a specific container
3. start-container: Start a stopped container
4. stop-container: Stop a running container
5. restart-container: Restart a container
6. remove-container: Remove a container

Please help me perform this action using the appropriate tool."""

        return types.GetPromptResult(
            description=f"Manage Docker containers - {action}",
            messages=[
                types.PromptMessage(
                    role="system",
                    content=types.TextContent(
                        type="text",
                        text=system_message
                    )
                ),
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=user_message
                    )
                )
            ]
        )
    elif name == "manage-compose":
        if not arguments or "action" not in arguments or "project_name" not in arguments:
            raise ValueError("Missing required arguments")
            
        action = arguments["action"].lower()
        project_name = arguments["project_name"]
        compose_yaml = arguments.get("compose_yaml", "")
        
        system_message = (
            "You are a Docker Compose specialist. Help the user manage their Docker Compose stacks "
            "by using the appropriate tools based on their request."
        )
        
        user_message = f"""I need to {action} a Docker Compose stack for project '{project_name}'.
{f'Here is the Docker Compose YAML:\\n```yaml\\n{compose_yaml}\\n```' if compose_yaml and action == 'deploy' else ''}

Available tools:
1. deploy-compose: Deploy a Docker Compose stack
2. compose-ps: List services in a Docker Compose stack
3. compose-logs: Get logs from a Docker Compose stack
4. compose-start: Start services in a Docker Compose stack
5. compose-stop: Stop services in a Docker Compose stack
6. compose-restart: Restart services in a Docker Compose stack

Please help me perform this action using the appropriate tool."""

        return types.GetPromptResult(
            description=f"Manage Docker Compose - {action}",
            messages=[
                types.PromptMessage(
                    role="system",
                    content=types.TextContent(
                        type="text",
                        text=system_message
                    )
                ),
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=user_message
                    )
                )
            ]
        )
    elif name == "authenticate":
        if not arguments or "username" not in arguments or "api_key" not in arguments:
            raise ValueError("Missing required arguments")
            
        username = arguments["username"]
        api_key = arguments["api_key"]
        
        system_message = (
            "You are a Docker MCP authentication assistant. Help the user authenticate with the Docker MCP server."
        )
        
        # Attempt to authenticate
        token = auth_manager.authenticate(username, api_key)
        
        # Record authentication metrics
        metrics_collector.record_authentication_attempt("success" if token else "error")
        
        if token:
            user_message = f"""Authentication successful!

Your authentication token is:
{token}

This token will be valid for 1 hour. You can use it to authenticate requests to the Docker MCP server.

To use this token, include it in the authorization header of your requests:
Authorization: {token}

For security reasons, do not share this token with anyone."""
        else:
            user_message = f"""Authentication failed.

Please check your username and API key and try again.

If you don't have an account, please contact the administrator to create one for you."""

        # Log the authentication attempt
        audit_logger.log_event(
            event_type="authentication",
            username=username,
            tool_name="authenticate",
            arguments={"username": username},
            result="",
            status="success" if token else "error",
            error=None if token else "Authentication failed"
        )

        return types.GetPromptResult(
            description="Authenticate with the Docker MCP server",
            messages=[
                types.PromptMessage(
                    role="system",
                    content=types.TextContent(
                        type="text",
                        text=system_message
                    )
                ),
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=user_message
                    )
                )
            ]
        )
    elif name == "audit-logs":
        # Default values
        username = arguments.get("username") if arguments else None
        tool_name = arguments.get("tool_name") if arguments else None
        status = arguments.get("status") if arguments else None
        limit = int(arguments.get("limit", "10")) if arguments else 10
        
        system_message = (
            "You are a Docker MCP audit log assistant. Help the user view audit logs for Docker operations."
        )
        
        # Get audit logs
        logs = audit_logger.get_logs(
            username=username,
            tool_name=tool_name,
            status=status,
            limit=limit
        )
        
        if logs:
            logs_text = "\n\n".join([
                f"Timestamp: {log.get('timestamp')}\n"
                f"User: {log.get('username')}\n"
                f"Tool: {log.get('tool_name')}\n"
                f"Status: {log.get('status')}\n"
                f"Arguments: {json.dumps(log.get('arguments', {}), indent=2)}"
                + (f"\nError: {log.get('error')}" if log.get('error') else "")
                for log in logs
            ])
            
            user_message = f"""Here are the audit logs for Docker operations:

{logs_text}

Total logs: {len(logs)}"""
        else:
            user_message = "No audit logs found matching the specified criteria."

        return types.GetPromptResult(
            description="View audit logs for Docker operations",
            messages=[
                types.PromptMessage(
                    role="system",
                    content=types.TextContent(
                        type="text",
                        text=system_message
                    )
                ),
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=user_message
                    )
                )
            ]
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """Handle list_tools request.
    
    Returns:
        List of available tools
    """
    return [
        # Container management tools
        types.Tool(
            name="create-container",
            description="Create a new standalone Docker container with advanced options",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Docker image name"},
                    "name": {"type": "string", "description": "Container name"},
                    "ports": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Port mappings (host:container)"
                    },
                    "environment": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Environment variables"
                    },
                    "volumes": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Volume mappings (host:container)"
                    },
                    "networks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Networks to connect to"
                    },
                    "health_check": {
                        "type": "object",
                        "properties": {
                            "cmd": {"type": "string", "description": "Command to check container health"},
                            "interval": {"type": "string", "description": "Interval between health checks (e.g., '30s')"},
                            "retries": {"type": "integer", "description": "Number of retries before considering unhealthy"},
                            "timeout": {"type": "string", "description": "Timeout for health check (e.g., '10s')"},
                            "start_period": {"type": "string", "description": "Start period for health check (e.g., '30s')"}
                        },
                        "description": "Health check configuration"
                    },
                    "resources": {
                        "type": "object",
                        "properties": {
                            "cpu": {"type": "string", "description": "CPU limit (e.g., '0.5')"},
                            "memory": {"type": "string", "description": "Memory limit (e.g., '512m')"}
                        },
                        "description": "Resource limits"
                    },
                    "restart_policy": {"type": "string", "description": "Restart policy (e.g., 'always', 'unless-stopped')"}
                },
                "required": ["image"]
            }
        ),
        types.Tool(
            name="list-containers",
            description="List all Docker containers",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {"type": "boolean", "description": "Show all containers (default: true)"}
                }
            }
        ),
        types.Tool(
            name="get-logs",
            description="Retrieve the latest logs for a specified Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {"type": "string", "description": "Container name or ID"},
                    "tail": {"type": "integer", "description": "Number of lines to show from the end of the logs"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="start-container",
            description="Start a stopped Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {"type": "string", "description": "Container name or ID"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="stop-container",
            description="Stop a running Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {"type": "string", "description": "Container name or ID"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="restart-container",
            description="Restart a Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {"type": "string", "description": "Container name or ID"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="remove-container",
            description="Remove a Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {"type": "string", "description": "Container name or ID"},
                    "force": {"type": "boolean", "description": "Force removal of running container"}
                },
                "required": ["container_name"]
            }
        ),
        
        # Network management tools
        types.Tool(
            name="network-create",
            description="Create a Docker network",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Network name"},
                    "driver": {"type": "string", "description": "Network driver (e.g., 'bridge', 'overlay')"}
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="network-remove",
            description="Remove a Docker network",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Network name"}
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="network-list",
            description="List Docker networks",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="network-connect",
            description="Connect a container to a network",
            inputSchema={
                "type": "object",
                "properties": {
                    "network": {"type": "string", "description": "Network name"},
                    "container": {"type": "string", "description": "Container name or ID"}
                },
                "required": ["network", "container"]
            }
        ),
        types.Tool(
            name="network-disconnect",
            description="Disconnect a container from a network",
            inputSchema={
                "type": "object",
                "properties": {
                    "network": {"type": "string", "description": "Network name"},
                    "container": {"type": "string", "description": "Container name or ID"}
                },
                "required": ["network", "container"]
            }
        ),
        types.Tool(
            name="network-inspect",
            description="Inspect a Docker network",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Network name"}
                },
                "required": ["name"]
            }
        ),
        
        # Docker Compose tools
        types.Tool(
            name="deploy-compose",
            description="Deploy a Docker Compose stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "compose_yaml": {"type": "string", "description": "Docker Compose YAML content"},
                    "project_name": {"type": "string", "description": "Project name"}
                },
                "required": ["compose_yaml", "project_name"]
            }
        ),
        types.Tool(
            name="compose-logs",
            description="Retrieve logs from a Docker Compose stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Project name"},
                    "compose_file": {"type": "string", "description": "Path to compose file or YAML content"},
                    "service": {"type": "string", "description": "Service name (optional)"}
                },
                "required": ["project_name", "compose_file"]
            }
        ),
        types.Tool(
            name="compose-ps",
            description="List services in a Docker Compose stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Project name"},
                    "compose_file": {"type": "string", "description": "Path to compose file or YAML content"}
                },
                "required": ["project_name", "compose_file"]
            }
        ),
        types.Tool(
            name="compose-start",
            description="Start services in a Docker Compose stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Project name"},
                    "compose_file": {"type": "string", "description": "Path to compose file or YAML content"},
                    "service": {"type": "string", "description": "Service name (optional)"}
                },
                "required": ["project_name", "compose_file"]
            }
        ),
        types.Tool(
            name="compose-stop",
            description="Stop services in a Docker Compose stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Project name"},
                    "compose_file": {"type": "string", "description": "Path to compose file or YAML content"},
                    "service": {"type": "string", "description": "Service name (optional)"}
                },
                "required": ["project_name", "compose_file"]
            }
        ),
        types.Tool(
            name="compose-restart",
            description="Restart services in a Docker Compose stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Project name"},
                    "compose_file": {"type": "string", "description": "Path to compose file or YAML content"},
                    "service": {"type": "string", "description": "Service name (optional)"}
                },
                "required": ["project_name", "compose_file"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None, metadata: Optional[Dict[str, Any]] = None) -> List[types.TextContent]:
    """Handle call_tool request.
    
    Args:
        name: Name of the tool
        arguments: Tool arguments
        metadata: Request metadata
        
    Returns:
        List of TextContent with the result
    """
    if not arguments and name not in ["list-containers", "network-list"]:
        arguments = {}
        
    # Get authentication token from metadata
    token = None
    username = "anonymous"
    if metadata and "authorization" in metadata:
        token = metadata["authorization"]
        token_info = auth_manager.validate_token(token)
        if token_info:
            username = token_info.get("username", "anonymous")
    
    # Check if tool is auto-approved or user is authorized
    is_auto_approved = name in auth_manager.get_auto_approve_tools()
    is_authorized = is_auto_approved or (token and auth_manager.is_authorized(token, name))
    
    if not is_authorized:
        error_message = f"Unauthorized access to tool {name}"
        logger.warning(error_message)
        audit_logger.log_event(
            event_type="tool_execution",
            username=username,
            tool_name=name,
            arguments=arguments or {},
            result="",
            status="error",
            error=error_message
        )
        return [types.TextContent(type="text", text=f"Error: {error_message}")]

    try:
        # Log the tool execution start
        logger.info(f"Executing tool {name} for user {username}")
        
        # Record start time for metrics
        start_time = time.time()
        
        result = None
        
        # Container management tools
        if name == "create-container":
            result = await DockerHandlers.handle_create_container(arguments)
        elif name == "list-containers":
            result = await DockerHandlers.handle_list_containers(arguments)
            
            # Update container metrics if list-containers was successful
            if result:
                # Parse container counts from result
                text = result[0].text
                running_count = text.count("Up ")
                total_count = text.count("\n")
                stopped_count = total_count - running_count
                
                # Update metrics
                metrics_collector.update_container_counts(
                    running=running_count,
                    stopped=stopped_count,
                    total=total_count
                )
                
        elif name == "get-logs":
            result = await DockerHandlers.handle_get_logs(arguments)
        elif name == "start-container":
            result = await DockerHandlers.handle_start_container(arguments)
        elif name == "stop-container":
            result = await DockerHandlers.handle_stop_container(arguments)
        elif name == "restart-container":
            result = await DockerHandlers.handle_restart_container(arguments)
        elif name == "remove-container":
            result = await DockerHandlers.handle_remove_container(arguments)
            
        # Network management tools
        elif name == "network-create":
            result = await DockerHandlers.handle_network_create(arguments)
        elif name == "network-remove":
            result = await DockerHandlers.handle_network_remove(arguments)
        elif name == "network-list":
            result = await DockerHandlers.handle_network_list(arguments)
            
            # Update network metrics if network-list was successful
            if result:
                # Parse network count from result
                text = result[0].text
                network_count = text.count("\n")
                
                # Update metrics
                metrics_collector.update_network_count(network_count)
                
        elif name == "network-connect":
            result = await DockerHandlers.handle_network_connect(arguments)
        elif name == "network-disconnect":
            result = await DockerHandlers.handle_network_disconnect(arguments)
        elif name == "network-inspect":
            result = await DockerHandlers.handle_network_inspect(arguments)
            
        # Docker Compose tools
        elif name == "deploy-compose":
            result = await DockerHandlers.handle_deploy_compose(arguments)
        elif name == "compose-logs":
            result = await DockerHandlers.handle_compose_logs(arguments)
        elif name == "compose-ps":
            result = await DockerHandlers.handle_compose_ps(arguments)
            
            # Update compose stack metrics if compose-ps was successful
            if result:
                # Parse compose stack count from result
                text = result[0].text
                stack_count = 1  # At least one stack if compose-ps was successful
                
                # Update metrics
                metrics_collector.update_compose_stack_count(stack_count)
                
        elif name == "compose-start":
            result = await DockerHandlers.handle_compose_start(arguments)
        elif name == "compose-stop":
            result = await DockerHandlers.handle_compose_stop(arguments)
        elif name == "compose-restart":
            result = await DockerHandlers.handle_compose_restart(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
        # Calculate execution duration
        duration = time.time() - start_time
        
        # Record metrics
        metrics_collector.record_tool_execution(name, duration, "success")
            
        # Log the successful tool execution
        audit_logger.log_event(
            event_type="tool_execution",
            username=username,
            tool_name=name,
            arguments=arguments or {},
            result=result[0].text if result else "",
            status="success"
        )
        
        return result
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error executing tool {name}: {error_message}")
        
        # Calculate execution duration
        duration = time.time() - start_time
        
        # Record metrics
        metrics_collector.record_tool_execution(name, duration, "error")
        
        # Log the failed tool execution
        audit_logger.log_event(
            event_type="tool_execution",
            username=username,
            tool_name=name,
            arguments=arguments or {},
            result="",
            status="error",
            error=error_message
        )
        
        return [types.TextContent(type="text", text=f"Error: {error_message} | Arguments: {arguments}")]


from .http_server import HttpServer

# Global HTTP server instance
http_server = None


def handle_shutdown(signum, frame):
    """Handle shutdown signals."""
    logger.info("Shutting down gracefully...")
    
    # Stop HTTP server if it's running
    if http_server:
        asyncio.create_task(http_server.stop())
        
    sys.exit(0)


async def run_server():
    """Run the MCP server."""
    global http_server
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Start HTTP server
    http_port = int(os.environ.get("DOCKER_MCP_PORT", "3334"))
    http_server = HttpServer(
        port=http_port,
        metrics_collector=metrics_collector,
        auth_manager=auth_manager,
        audit_logger=audit_logger
    )
    await http_server.start()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="docker-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Main entry point."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), '../../../logs'), exist_ok=True)
    
    # Create config directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), '../../../config'), exist_ok=True)
    
    logger.info("Starting Docker MCP server")
    asyncio.run(run_server())


if __name__ == "__main__":
    main()