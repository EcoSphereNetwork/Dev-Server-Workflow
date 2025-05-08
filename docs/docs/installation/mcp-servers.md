# MCP Servers Installation

This guide provides detailed instructions for installing and configuring individual MCP (Model Context Protocol) servers for use with OpenHands and other AI agents.

## What are MCP Servers?

MCP (Model Context Protocol) servers provide standardized interfaces for AI agents to interact with various tools and services. Each MCP server specializes in a specific domain, such as file system operations, GitHub interactions, or web browsing.

## Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)
- Git installed
- Appropriate API tokens for the services you want to integrate

## Installation Methods

You can install MCP servers using one of the following methods:

1. **Docker Compose** (recommended for production)
2. **Python Virtual Environment** (recommended for development)
3. **Direct Installation** (not recommended for production)

## Docker Compose Installation

### 1. Clone the Repository

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Configure Environment Variables

```bash
cd docker-mcp-servers
cp .env.example .env
```

Edit the `.env` file with your configuration.

### 3. Start the MCP Servers

```bash
docker compose up -d
```

This will start all MCP servers in detached mode.

To start a specific MCP server:

```bash
docker compose up -d mcp-github
```

## Python Virtual Environment Installation

### 1. Clone the Repository

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp src/env-template .env
```

Edit the `.env` file with your configuration.

### 5. Start Individual MCP Servers

```bash
# Start GitHub MCP Server
python src/mcp_servers/github_mcp.py

# Start Filesystem MCP Server
python src/mcp_servers/filesystem_mcp.py

# Start n8n MCP Server
python src/n8n_mcp_server.py
```

## Available MCP Servers

| Server | Description | Configuration |
|--------|-------------|---------------|
| n8n MCP Server | Provides n8n workflow functionality as MCP tools | Requires n8n API key |
| GitHub MCP | Provides GitHub repository management tools | Requires GitHub token |
| Filesystem MCP | Provides file system operations | No additional configuration required |
| Desktop Commander MCP | Provides terminal command execution | Requires X11 for GUI applications |
| Sequential Thinking MCP | Provides structured problem-solving tools | No additional configuration required |
| Puppeteer MCP | Provides web browsing and interaction | Requires Chrome/Chromium |
| Basic Memory MCP | Provides simple key-value storage | Optional Redis configuration |
| Wikipedia MCP | Provides Wikipedia search | No additional configuration required |

## Configuration Options

### n8n MCP Server

```env
N8N_URL=http://localhost:5678
N8N_API_KEY=your_api_key
MCP_SERVER_PORT=3333
```

### GitHub MCP Server

```env
GITHUB_TOKEN=your_github_token
GITHUB_MCP_PORT=3005
```

### Filesystem MCP Server

```env
FILESYSTEM_MCP_PORT=3001
WORKSPACE_PATH=/path/to/workspace
```

### Desktop Commander MCP Server

```env
DESKTOP_MCP_PORT=3002
DISPLAY=:0
```

## Integrating with OpenHands

To integrate MCP servers with OpenHands:

1. Create an OpenHands MCP configuration file:

```bash
python src/generate_openhands_mcp_config.py
```

2. Add the generated configuration to your OpenHands config:

```bash
cat ~/.openhands/mcp-config.json >> ~/.config/openhands/config.toml
```

## Testing MCP Servers

To test if an MCP server is working correctly:

```bash
# Test n8n MCP Server
curl -X POST http://localhost:3333 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'

# Test GitHub MCP Server
curl -X POST http://localhost:3005 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

## Monitoring MCP Servers

To monitor the status of all MCP servers:

```bash
python src/monitor_mcp_servers.py
```

## Troubleshooting

### MCP Server Not Starting

Check the logs:

```bash
# For Docker installations
docker logs mcp-github

# For Python installations
cat logs/mcp-github.log
```

### Connection Issues

Ensure the ports are not in use:

```bash
netstat -tuln | grep 3005
```

### Authentication Issues

Verify your API tokens:

```bash
# For GitHub
curl -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/user

# For n8n
curl -H "X-N8N-API-KEY: YOUR_N8N_API_KEY" http://localhost:5678/api/v1/workflows
```