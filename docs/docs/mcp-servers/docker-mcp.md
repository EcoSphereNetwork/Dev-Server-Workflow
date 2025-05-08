# Docker MCP Server

The Docker MCP Server provides a Model Context Protocol (MCP) interface for Docker operations, enabling AI agents to manage Docker containers and Docker Compose stacks.

## Overview

The Docker MCP Server allows AI agents to:

- Create and manage Docker containers
- Deploy and manage Docker Compose stacks
- Retrieve container logs
- List running containers
- Start, stop, and restart containers and services

## Installation

The Docker MCP Server is included in the Dev-Server-Workflow project. To install it, follow these steps:

1. Ensure you have the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Docker MCP Server using the CLI:
   ```bash
   ./cli/dev-server.sh start docker-mcp
   ```

## Configuration

The Docker MCP Server uses the following configuration options:

| Option | Description | Default |
|--------|-------------|---------|
| `DOCKER_MCP_PORT` | Port for the Docker MCP Server | 3334 |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |

You can configure these options in the `.env` file or by setting environment variables.

## Usage

### Starting the Server

```bash
# Using the CLI
./cli/dev-server.sh start docker-mcp

# Directly
python src/docker_mcp_server.py
```

### Stopping the Server

```bash
# Using the CLI
./cli/dev-server.sh stop docker-mcp
```

### Checking Status

```bash
# Using the CLI
./cli/dev-server.sh status
```

## Available Tools

The Docker MCP Server provides the following tools:

### Container Management

- **create-container**: Create a new standalone Docker container
  ```json
  {
      "image": "nginx:latest",
      "name": "my-nginx",
      "ports": {"80": "8080"},
      "environment": {"ENV_VAR": "value"},
      "volumes": {"/host/path": "/container/path"}
  }
  ```

- **list-containers**: List all Docker containers
  ```json
  {
      "all": true
  }
  ```

- **get-logs**: Retrieve the latest logs for a specified Docker container
  ```json
  {
      "container_name": "my-nginx",
      "tail": 100
  }
  ```

- **start-container**: Start a stopped Docker container
  ```json
  {
      "container_name": "my-nginx"
  }
  ```

- **stop-container**: Stop a running Docker container
  ```json
  {
      "container_name": "my-nginx"
  }
  ```

- **restart-container**: Restart a Docker container
  ```json
  {
      "container_name": "my-nginx"
  }
  ```

- **remove-container**: Remove a Docker container
  ```json
  {
      "container_name": "my-nginx",
      "force": true
  }
  ```

### Docker Compose Management

- **deploy-compose**: Deploy a Docker Compose stack
  ```json
  {
      "project_name": "my-stack",
      "compose_yaml": "version: '3.8'\nservices:\n  web:\n    image: nginx:latest\n    ports:\n      - '8080:80'"
  }
  ```

- **compose-logs**: Retrieve logs from a Docker Compose stack
  ```json
  {
      "project_name": "my-stack",
      "compose_file": "docker compose.yml",
      "service": "web"
  }
  ```

- **compose-ps**: List services in a Docker Compose stack
  ```json
  {
      "project_name": "my-stack",
      "compose_file": "docker compose.yml"
  }
  ```

- **compose-start**: Start services in a Docker Compose stack
  ```json
  {
      "project_name": "my-stack",
      "compose_file": "docker compose.yml",
      "service": "web"
  }
  ```

- **compose-stop**: Stop services in a Docker Compose stack
  ```json
  {
      "project_name": "my-stack",
      "compose_file": "docker compose.yml",
      "service": "web"
  }
  ```

- **compose-restart**: Restart services in a Docker Compose stack
  ```json
  {
      "project_name": "my-stack",
      "compose_file": "docker compose.yml",
      "service": "web"
  }
  ```

## Available Prompts

The Docker MCP Server provides the following prompts:

- **deploy-stack**: Generate and deploy a Docker stack based on requirements
  ```json
  {
      "requirements": "I need a web server with a database",
      "project_name": "web-db-stack"
  }
  ```

- **manage-containers**: Manage Docker containers (list, start, stop, restart, remove)
  ```json
  {
      "action": "list",
      "container_name": "my-nginx"
  }
  ```

- **manage-compose**: Manage Docker Compose stacks (deploy, start, stop, restart, logs)
  ```json
  {
      "action": "deploy",
      "project_name": "my-stack",
      "compose_yaml": "version: '3.8'\nservices:\n  web:\n    image: nginx:latest\n    ports:\n      - '8080:80'"
  }
  ```

## Integration with OpenHands

To integrate the Docker MCP Server with OpenHands, add the following configuration to your OpenHands config file:

```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "python3",
      "args": [
        "/path/to/Dev-Server-Workflow/src/docker_mcp_server.py"
      ]
    }
  }
}
```

## Troubleshooting

### Server Not Starting

- Check if the port is already in use:
  ```bash
  netstat -tuln | grep 3334
  ```

- Check the logs:
  ```bash
  cat logs/docker_mcp.log
  ```

### Docker Command Errors

- Ensure Docker is running:
  ```bash
  docker info
  ```

- Check Docker permissions:
  ```bash
  docker ps
  ```

### Compose File Errors

- Validate your Docker Compose file:
  ```bash
  docker compose -f your-compose-file.yml config
  ```