# Docker MCP Server

The Docker MCP Server provides a Model Context Protocol (MCP) interface for Docker operations, enabling AI agents to manage Docker containers and Docker Compose stacks.

## Overview

The Docker MCP Server allows AI agents to:

- Create and manage Docker containers
- Deploy and manage Docker Compose stacks
- Retrieve container logs
- List running containers
- Start, stop, and restart containers and services
- Manage Docker networks
- Monitor Docker operations

## Features

### Container Management

- Create containers with advanced options (networks, health checks, resource limits)
- List containers
- Get container logs
- Start, stop, restart, and remove containers

### Network Management

- Create networks
- List networks
- Connect containers to networks
- Disconnect containers from networks
- Inspect networks

### Docker Compose Management

- Deploy Docker Compose stacks
- List services in a Docker Compose stack
- Get logs from a Docker Compose stack
- Start, stop, and restart services in a Docker Compose stack

### Security

- Authentication and authorization
- Audit logging
- Auto-approve safe operations

### Monitoring

- Prometheus metrics
- Grafana dashboard
- Alerting

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
| `MCP_AUTH_SECRET` | Secret key for token signing | Random value |

You can configure these options in the `.env` file or by setting environment variables.

## Authentication

The Docker MCP Server supports authentication using API keys and tokens. To authenticate:

1. Use the `authenticate` prompt with your username and API key:
   ```json
   {
       "username": "admin",
       "api_key": "admin_api_key"
   }
   ```

2. The server will return a token that you can use to authenticate requests:
   ```json
   {
       "token": "username:timestamp:signature"
   }
   ```

3. Include the token in the `authorization` header of your requests:
   ```json
   {
       "metadata": {
           "authorization": "username:timestamp:signature"
       }
   }
   ```

## Authorization

The Docker MCP Server supports role-based access control. The following roles are available:

- `admin`: Full access to all operations
- `user`: Limited access to safe operations (list, logs, inspect)

You can configure roles and permissions in the `config/docker_mcp_auth.json` file.

## Audit Logging

The Docker MCP Server logs all operations to an audit log. You can view the audit log using the `audit-logs` prompt:

```json
{
    "username": "admin",
    "tool_name": "create-container",
    "status": "success",
    "limit": 10
}
```

## Monitoring

The Docker MCP Server exposes Prometheus metrics at the `/prometheus` endpoint. You can use these metrics to monitor the server's operations.

A Grafana dashboard is available in the monitoring stack. To access it:

1. Start the monitoring stack:
   ```bash
   ./cli/dev-server.sh start monitoring
   ```

2. Access the Grafana dashboard at [http://localhost:3000](http://localhost:3000)

## API Reference

### Container Management

- **create-container**: Create a new standalone Docker container
  ```json
  {
      "image": "nginx:latest",
      "name": "my-nginx",
      "ports": {"80": "8080"},
      "environment": {"ENV_VAR": "value"},
      "volumes": {"/host/path": "/container/path"},
      "networks": ["my-network"],
      "health_check": {
          "cmd": "curl -f http://localhost/ || exit 1",
          "interval": "30s",
          "retries": 3,
          "timeout": "10s",
          "start_period": "30s"
      },
      "resources": {
          "cpu": "0.5",
          "memory": "512m"
      },
      "restart_policy": "always"
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

### Network Management

- **network-create**: Create a Docker network
  ```json
  {
      "name": "my-network",
      "driver": "bridge"
  }
  ```

- **network-remove**: Remove a Docker network
  ```json
  {
      "name": "my-network"
  }
  ```

- **network-list**: List Docker networks
  ```json
  {}
  ```

- **network-connect**: Connect a container to a network
  ```json
  {
      "network": "my-network",
      "container": "my-nginx"
  }
  ```

- **network-disconnect**: Disconnect a container from a network
  ```json
  {
      "network": "my-network",
      "container": "my-nginx"
  }
  ```

- **network-inspect**: Inspect a Docker network
  ```json
  {
      "name": "my-network"
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

## Integration with OpenHands

To integrate the Docker MCP Server with OpenHands, add the following configuration to your OpenHands config file:

```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "python3",
      "args": [
        "/path/to/Dev-Server-Workflow/src/docker_mcp_server.py"
      ],
      "env": {
        "DOCKER_MCP_PORT": "3334",
        "LOG_LEVEL": "INFO",
        "MCP_AUTH_SECRET": "your_secret_key_here"
      },
      "autoApprove": [
        "list-containers",
        "get-logs",
        "network-list",
        "compose-ps",
        "compose-logs"
      ],
      "metadata": {
        "authorization": "username:timestamp:signature"
      }
    }
  }
}
```

You can generate this configuration using the CLI:

```bash
./cli/dev-server.sh config openhands-docker-mcp /path/to/config.json
```