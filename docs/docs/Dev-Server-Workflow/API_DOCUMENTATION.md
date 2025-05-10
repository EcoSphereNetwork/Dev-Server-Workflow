# API Documentation

This document provides comprehensive documentation for all API endpoints in the Dev-Server-Workflow system.

## Table of Contents

- [Authentication](#authentication)
- [MCP Hub API](#mcp-hub-api)
- [Docker MCP API](#docker-mcp-api)
- [n8n MCP API](#n8n-mcp-api)
- [Prometheus Exporter API](#prometheus-exporter-api)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

## Authentication

All API endpoints require authentication using one of the following methods:

### API Key Authentication

Most endpoints accept an API key in the request header:

```
X-API-Key: your-api-key-here
```

API keys can be generated in the admin dashboard or using the CLI tool:

```bash
./dev-server-cli.sh generate-api-key --name "My API Key" --permissions "read,write"
```

### JWT Authentication

For user-specific operations, JWT authentication is supported:

```
Authorization: Bearer your-jwt-token-here
```

JWT tokens can be obtained by authenticating with the `/auth/login` endpoint.

## MCP Hub API

The MCP Hub API provides endpoints for managing MCP servers and their configurations.

### Base URL

```
http://localhost:3000/api/v1
```

### Endpoints

#### GET /servers

Lists all registered MCP servers.

**Request:**
```bash
curl -X GET "http://localhost:3000/api/v1/servers" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "servers": [
    {
      "id": "docker-mcp",
      "name": "Docker MCP",
      "url": "http://docker-mcp:3334",
      "status": "online",
      "version": "0.1.0",
      "capabilities": ["container-management", "image-management"]
    },
    {
      "id": "n8n-mcp",
      "name": "n8n MCP",
      "url": "http://n8n-mcp:3335",
      "status": "online",
      "version": "0.1.0",
      "capabilities": ["workflow-management", "execution-management"]
    }
  ]
}
```

#### GET /servers/{server-id}

Get details for a specific MCP server.

**Request:**
```bash
curl -X GET "http://localhost:3000/api/v1/servers/docker-mcp" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "id": "docker-mcp",
  "name": "Docker MCP",
  "url": "http://docker-mcp:3334",
  "status": "online",
  "version": "0.1.0",
  "capabilities": ["container-management", "image-management"],
  "metrics": {
    "requests": 1245,
    "errors": 12,
    "uptime": "3d 4h 12m"
  }
}
```

#### POST /servers/{server-id}/restart

Restart a specific MCP server.

**Request:**
```bash
curl -X POST "http://localhost:3000/api/v1/servers/docker-mcp/restart" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "success": true,
  "message": "Server restart initiated",
  "requestId": "req-123456"
}
```

#### GET /tools

List all available tools across all MCP servers.

**Request:**
```bash
curl -X GET "http://localhost:3000/api/v1/tools" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "tools": [
    {
      "id": "create-container",
      "name": "Create Container",
      "description": "Create a new Docker container",
      "server": "docker-mcp",
      "parameters": {
        "image": "string",
        "name": "string",
        "ports": "string",
        "environment": "object",
        "volumes": "string"
      }
    },
    {
      "id": "execute-workflow",
      "name": "Execute Workflow",
      "description": "Execute an n8n workflow",
      "server": "n8n-mcp",
      "parameters": {
        "workflowId": "string",
        "data": "object"
      }
    }
  ]
}
```

#### POST /execute

Execute a tool on a specific MCP server.

**Request:**
```bash
curl -X POST "http://localhost:3000/api/v1/execute" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "create-container",
    "server": "docker-mcp",
    "parameters": {
      "image": "nginx:latest",
      "name": "web-server",
      "ports": "80:80"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "containerId": "abc123def456",
    "name": "web-server",
    "status": "running",
    "ports": {
      "80/tcp": [
        {
          "HostIp": "0.0.0.0",
          "HostPort": "80"
        }
      ]
    }
  },
  "executionId": "exec-789012"
}
```

## Docker MCP API

The Docker MCP API provides endpoints for managing Docker containers and images.

### Base URL

```
http://localhost:3334/api/v1
```

### Endpoints

#### GET /containers

List all Docker containers.

**Request:**
```bash
curl -X GET "http://localhost:3334/api/v1/containers" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "containers": [
    {
      "id": "abc123def456",
      "name": "web-server",
      "image": "nginx:latest",
      "status": "running",
      "created": "2025-05-01T12:34:56Z",
      "ports": {
        "80/tcp": [
          {
            "HostIp": "0.0.0.0",
            "HostPort": "80"
          }
        ]
      }
    }
  ]
}
```

#### POST /containers

Create a new Docker container.

**Request:**
```bash
curl -X POST "http://localhost:3334/api/v1/containers" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "nginx:latest",
    "name": "web-server",
    "ports": {
      "80/tcp": [
        {
          "HostIp": "0.0.0.0",
          "HostPort": "80"
        }
      ]
    },
    "environment": {
      "NGINX_HOST": "example.com"
    }
  }'
```

**Response:**
```json
{
  "id": "abc123def456",
  "name": "web-server",
  "status": "running"
}
```

#### GET /containers/{container-id}

Get details for a specific container.

**Request:**
```bash
curl -X GET "http://localhost:3334/api/v1/containers/abc123def456" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "id": "abc123def456",
  "name": "web-server",
  "image": "nginx:latest",
  "status": "running",
  "created": "2025-05-01T12:34:56Z",
  "ports": {
    "80/tcp": [
      {
        "HostIp": "0.0.0.0",
        "HostPort": "80"
      }
    ]
  },
  "environment": {
    "NGINX_HOST": "example.com"
  },
  "volumes": [],
  "networks": ["bridge"],
  "stats": {
    "cpu": "0.5%",
    "memory": "24.5MB",
    "network": {
      "rx": "1.2MB",
      "tx": "567KB"
    }
  }
}
```

#### POST /containers/{container-id}/start

Start a container.

**Request:**
```bash
curl -X POST "http://localhost:3334/api/v1/containers/abc123def456/start" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "success": true,
  "status": "running"
}
```

#### POST /containers/{container-id}/stop

Stop a container.

**Request:**
```bash
curl -X POST "http://localhost:3334/api/v1/containers/abc123def456/stop" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "success": true,
  "status": "stopped"
}
```

#### DELETE /containers/{container-id}

Remove a container.

**Request:**
```bash
curl -X DELETE "http://localhost:3334/api/v1/containers/abc123def456" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "success": true,
  "message": "Container removed"
}
```

## n8n MCP API

The n8n MCP API provides endpoints for managing n8n workflows and executions.

### Base URL

```
http://localhost:3335/api/v1
```

### Endpoints

#### GET /workflows

List all n8n workflows.

**Request:**
```bash
curl -X GET "http://localhost:3335/api/v1/workflows" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "workflows": [
    {
      "id": "1",
      "name": "GitHub to OpenProject",
      "active": true,
      "createdAt": "2025-05-01T12:34:56Z",
      "updatedAt": "2025-05-02T10:11:12Z"
    },
    {
      "id": "2",
      "name": "Document Synchronization",
      "active": false,
      "createdAt": "2025-05-01T13:14:15Z",
      "updatedAt": "2025-05-02T11:12:13Z"
    }
  ]
}
```

#### POST /workflows/{workflow-id}/execute

Execute a specific workflow.

**Request:**
```bash
curl -X POST "http://localhost:3335/api/v1/workflows/1/execute" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "issueId": "123",
      "title": "New Issue",
      "description": "This is a new issue"
    }
  }'
```

**Response:**
```json
{
  "executionId": "exec-123456",
  "status": "running"
}
```

#### GET /executions

List workflow executions.

**Request:**
```bash
curl -X GET "http://localhost:3335/api/v1/executions" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "executions": [
    {
      "id": "exec-123456",
      "workflowId": "1",
      "workflowName": "GitHub to OpenProject",
      "status": "success",
      "startedAt": "2025-05-03T14:15:16Z",
      "finishedAt": "2025-05-03T14:15:18Z",
      "data": {
        "input": {
          "issueId": "123",
          "title": "New Issue",
          "description": "This is a new issue"
        },
        "output": {
          "workPackageId": "456",
          "status": "created"
        }
      }
    }
  ]
}
```

## Prometheus Exporter API

The Prometheus Exporter API provides endpoints for monitoring and metrics.

### Base URL

```
http://localhost:9091/api/v1
```

### Endpoints

#### GET /metrics

Get Prometheus metrics in plain text format.

**Request:**
```bash
curl -X GET "http://localhost:9091/api/v1/metrics" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```
# HELP system_cpu_usage System CPU usage percentage
# TYPE system_cpu_usage gauge
system_cpu_usage 23.5
# HELP system_memory_usage System memory usage percentage
# TYPE system_memory_usage gauge
system_memory_usage 45.2
# HELP docker_container_count Number of running Docker containers
# TYPE docker_container_count gauge
docker_container_count 5
...
```

#### GET /health

Check the health of the Prometheus exporter.

**Request:**
```bash
curl -X GET "http://localhost:9091/api/v1/health" \
  -H "X-API-Key: your-api-key-here"
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime": "2d 5h 30m 15s"
}
```

## Error Handling

All API endpoints use standard HTTP status codes to indicate success or failure:

- `200 OK`: The request was successful
- `201 Created`: A resource was successfully created
- `400 Bad Request`: The request was malformed or invalid
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: The authenticated user does not have permission
- `404 Not Found`: The requested resource was not found
- `409 Conflict`: The request conflicts with the current state
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: An unexpected error occurred

Error responses include a JSON body with details:

```json
{
  "error": true,
  "code": "RESOURCE_NOT_FOUND",
  "message": "The requested resource was not found",
  "details": {
    "resourceType": "container",
    "resourceId": "abc123def456"
  },
  "requestId": "req-789012"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Rate limits are specified in the response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1620000000
```

If you exceed the rate limit, you'll receive a `429 Too Many Requests` response with a JSON body:

```json
{
  "error": true,
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Try again in 60 seconds.",
  "details": {
    "limit": 100,
    "reset": 1620000000
  }
}
```

## OpenAPI Specification

The complete OpenAPI (Swagger) specification is available at:

```
http://localhost:3000/api/docs
```

You can use this interactive documentation to explore and test all API endpoints.

## API Versioning

All API endpoints are versioned to ensure backward compatibility. The current version is `v1`.

When a new version is released, the old version will be maintained for a deprecation period of at least 6 months.

## Environment-Specific Configuration

API endpoints may behave differently depending on the environment:

- **Development**: More verbose error messages, no rate limiting
- **Staging**: Production-like behavior with higher rate limits
- **Production**: Full rate limiting and security measures

The environment can be determined from the response header:

```
X-Environment: production
```