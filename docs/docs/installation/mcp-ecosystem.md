# MCP Ecosystem Installation

This guide provides detailed instructions for installing and configuring the MCP Ecosystem, which includes all MCP servers, n8n, monitoring tools, and OpenHands integration.

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- 4GB RAM and 2 CPU cores minimum
- GitHub token with appropriate permissions

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Configure Environment Variables

```bash
cd docker-mcp-ecosystem
cp .env.example .env
```

Edit the `.env` file with your configuration:

```bash
# Required settings
GITHUB_TOKEN=your_github_token
WORKSPACE_PATH=/path/to/your/workspace

# Optional settings
REDIS_PASSWORD=your_secure_password
DISPLAY=:0  # For desktop-commander MCP
OLLAMA_MODEL=qwen2.5-coder:7b-instruct
```

### 3. Start the MCP Ecosystem

```bash
./start-mcp-ecosystem.sh
```

This script will:
- Pull all required Docker images
- Start all MCP servers
- Start Redis for communication
- Start the MCP Inspector UI
- Start n8n for workflow automation

### 4. Verify Installation

Check if all components are running:

```bash
docker ps | grep mcp
```

Monitor the MCP servers:

```bash
# One-time status check
./monitor-mcp-servers.py

# Continuous monitoring (every 30 seconds)
./monitor-mcp-servers.py -c

# Continuous monitoring with tools display
./monitor-mcp-servers.py -c -t
```

You can also access the MCP Inspector UI at http://localhost:8080

### 5. Integrate with OpenHands (Optional)

If you want to integrate the MCP servers with OpenHands:

```bash
./integrate-with-openhands.sh
```

Follow the on-screen instructions to complete the integration.

## Configuration Options

### MCP Server Ports

| Server | Port | Description |
|--------|------|-------------|
| Filesystem MCP | 3001 | File system operations |
| Desktop Commander MCP | 3002 | Terminal command execution |
| Sequential Thinking MCP | 3003 | Structured problem-solving |
| GitHub Chat MCP | 3004 | GitHub discussions interaction |
| GitHub MCP | 3005 | GitHub repository management |
| Puppeteer MCP | 3006 | Web browsing and interaction |
| Basic Memory MCP | 3007 | Simple key-value storage |
| Wikipedia MCP | 3008 | Wikipedia search |
| MCP Inspector | 8080 | UI for monitoring MCP servers |
| n8n | 5678 | Workflow automation |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| GITHUB_TOKEN | GitHub personal access token | - |
| WORKSPACE_PATH | Path to your workspace directory | /workspace |
| REDIS_PASSWORD | Password for Redis | redis_password |
| DISPLAY | Display for Desktop Commander | :0 |
| OLLAMA_MODEL | Default model for Ollama | qwen2.5-coder:7b-instruct |
| BRAVE_API_KEY | API key for Brave Search (optional) | - |

## Stopping the Ecosystem

To stop all components:

```bash
./stop-mcp-ecosystem.sh
```

## Troubleshooting

### MCP Servers Not Starting

Check the Docker logs:

```bash
docker logs mcp-filesystem
```

Ensure the `.env` file has the correct configuration.

### n8n Not Connecting to MCP Servers

Check if the MCP servers are running and accessible:

```bash
curl http://localhost:3001/health
```

Verify the n8n environment variables in the Docker Compose file.

### OpenHands Integration Issues

Ensure OpenHands is running in the same Docker network:

```bash
docker network inspect mcp-network
```

Check the OpenHands configuration:

```bash
cat ~/.config/openhands/config.toml
```