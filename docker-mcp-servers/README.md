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

### Automatic Installation

The easiest way to install and run the MCP servers is to use the provided scripts:

```bash
cd docker-mcp-servers
./pull-images.sh     # Pull the Docker images
./start-mcp-servers.sh  # Start the MCP servers
```

### Manual Installation

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

The MCP servers can be integrated with n8n using the provided integration script:

```bash
cd /workspace/Dev-Server-Workflow
./scripts/integrate-mcp-with-n8n.py --n8n-api-key YOUR_N8N_API_KEY
```

For more details, see the [MCP-Server-Implementation.md](../docs/docs/Dev-Server-Workflow/MCP-Server-Implementation.md) documentation.

## Integration with OpenHands

The MCP servers can be integrated with OpenHands by copying the `openhands-mcp-config.json` file to your OpenHands configuration directory:

```bash
cd /workspace/Dev-Server-Workflow
./scripts/integrate-mcp-with-openhands.py --openhands-config-dir /path/to/openhands/config --github-token YOUR_GITHUB_TOKEN
```

For more details, see the [MCP-OpenHands.md](../docs/docs/Dev-Server-Workflow/MCP-OpenHands.md) documentation.

## Usage

### Testing the MCP Servers

You can test the MCP servers using the provided test script:

```bash
./test-mcp-servers.py
```

To test a specific server:

```bash
./test-mcp-servers.py --server filesystem-mcp
```

To test the tools of each server:

```bash
./test-mcp-servers.py --test-tools
```

### Stopping the MCP Servers

To stop the MCP servers:

```bash
./stop-mcp-servers.sh
```

### MCP Inspector UI

The MCP Inspector UI is available at http://localhost:8080 and provides a web interface for interacting with the MCP servers.

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
   ./test-mcp-servers.py
   ```

4. Check the MCP Inspector UI at http://localhost:8080

## Security Considerations

- The MCP servers should only be run in trusted environments
- Use a dedicated GitHub token with limited permissions
- Configure the allowed directories for filesystem and desktop commander MCP servers
- Block dangerous commands in the desktop commander MCP server

## References

- [Model Context Protocol Documentation](https://github.com/modelcontextprotocol/protocol)
- [MCP Server Implementation Guide](../docs/docs/Dev-Server-Workflow/MCP-Server-Implementation.md)
- [MCP OpenHands Integration](../docs/docs/Dev-Server-Workflow/MCP-OpenHands.md)