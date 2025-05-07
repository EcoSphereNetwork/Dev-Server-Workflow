# MCP Server Implementation

This directory contains the Docker Compose configuration for implementing the Model Context Protocol (MCP) servers as part of the Dev-Server-Workflow project.

## Overview

The MCP servers provide a standardized way for AI agents like OpenHands to interact with various tools and services. Each MCP server implements the Model Context Protocol and provides specific functionality.

## Included MCP Servers

The following MCP servers are included in this implementation:

1. **Filesystem MCP Server** (`mcp/filesystem`): Provides file system operations like reading, writing, and searching files.
2. **Desktop Commander MCP Server** (`mcp/desktop-commander`): Allows execution of terminal commands and desktop operations.
3. **Sequential Thinking MCP Server** (`mcp/sequentialthinking`): Provides structured problem-solving capabilities.
4. **GitHub Chat MCP Server** (`mcp/github-chat`): Enables interaction with GitHub discussions and comments.
5. **GitHub MCP Server** (`mcp/github`): Provides GitHub repository management capabilities.
6. **Puppeteer MCP Server** (`mcp/puppeteer`): Enables web browsing and interaction with web pages.
7. **Basic Memory MCP Server** (`mcp/basic-memory`): Provides simple key-value storage for AI agents.
8. **Wikipedia MCP Server** (`mcp/wikipedia-mcp`): Enables searching and retrieving information from Wikipedia.

## Prerequisites

- Docker and Docker Compose
- Access to the MCP server Docker images
- GitHub token (for GitHub-related MCP servers)

## Installation

1. Clone this repository
2. Create a `.env` file based on the `.env.example` template
3. Run the Docker Compose configuration:

```bash
cd docker-mcp-servers
cp .env.example .env
# Edit the .env file with your configuration
docker-compose up -d
```

## Configuration

### Environment Variables

The following environment variables can be configured in the `.env` file:

- `REDIS_PASSWORD`: Password for the Redis server
- `GITHUB_TOKEN`: GitHub personal access token
- `WORKSPACE_PATH`: Path to the workspace directory
- `DISPLAY`: Display for Desktop Commander

### Port Configuration

Each MCP server is configured to run on a specific port:

- Filesystem MCP: 3001
- Desktop Commander MCP: 3002
- Sequential Thinking MCP: 3003
- GitHub Chat MCP: 3004
- GitHub MCP: 3005
- Puppeteer MCP: 3006
- Basic Memory MCP: 3007
- Wikipedia MCP: 3008

## Integration with n8n

The MCP servers can be integrated with n8n workflows using the MCP integration workflow. See the [MCP-Server-Implementation.md](../docs/docs/Dev-Server-Workflow/MCP-Server-Implementation.md) documentation for details.

## Integration with OpenHands

To integrate the MCP servers with OpenHands, configure the OpenHands instance to connect to the MCP servers. See the [MCP-OpenHands.md](../docs/docs/Dev-Server-Workflow/MCP-OpenHands.md) documentation for details.

## Troubleshooting

If you encounter issues with the MCP servers:

1. Check the Docker container logs:
   ```bash
   docker-compose logs <container-name>
   ```

2. Verify that the MCP servers are running:
   ```bash
   docker-compose ps
   ```

3. Check the health status of the MCP servers:
   ```bash
   docker-compose exec <container-name> curl -f http://localhost:<port>/health
   ```

## Security Considerations

- The MCP servers should only be run in trusted environments
- Use a dedicated GitHub token with limited permissions
- Configure the allowed directories for filesystem and desktop commander MCP servers
- Block dangerous commands in the desktop commander MCP server

## References

- [Model Context Protocol Documentation](https://github.com/modelcontextprotocol/protocol)
- [MCP Server Implementation Guide](../docs/docs/Dev-Server-Workflow/MCP-Server-Implementation.md)
- [MCP OpenHands Integration](../docs/docs/Dev-Server-Workflow/MCP-OpenHands.md)