# OpenHands Integration

This guide provides detailed instructions for integrating OpenHands AI agent with the Dev-Server-Workflow ecosystem, including MCP servers and n8n workflows.

## Prerequisites

- OpenHands installed (version 0.5.0 or higher)
- Dev-Server-Workflow installed and configured
- MCP servers running
- n8n running with appropriate workflows

## Installation Steps

### 1. Install OpenHands

If you haven't installed OpenHands yet:

```bash
pip install openhands-cli
```

Or using the provided script:

```bash
./cli/dev-server.sh install openhands
```

### 2. Configure OpenHands for MCP Integration

#### Automatic Configuration

Use the provided script to automatically configure OpenHands:

```bash
./cli/dev-server.sh config openhands-mcp
```

This script will:
- Generate MCP configuration for all available MCP servers
- Add the configuration to your OpenHands config file
- Set up appropriate permissions

#### Manual Configuration

1. Generate the OpenHands MCP configuration:

```bash
python src/generate_openhands_mcp_config.py > openhands-mcp-config.json
```

2. Add the configuration to your OpenHands config:

```bash
# Linux/macOS
cat openhands-mcp-config.json >> ~/.config/openhands/config.toml

# Windows
type openhands-mcp-config.json >> %USERPROFILE%\.config\openhands\config.toml
```

### 3. Configure OpenHands for n8n Integration

#### Automatic Configuration

```bash
./cli/dev-server.sh config openhands-n8n
```

#### Manual Configuration

1. Get the n8n webhook URL:

```bash
python src/get_n8n_webhook_url.py
```

2. Configure OpenHands to use the webhook:

```bash
openhands config set webhooks.n8n.url "http://localhost:5678/webhook/openhands"
openhands config set webhooks.n8n.events "['command_executed', 'file_changed', 'agent_started', 'agent_stopped']"
```

### 4. Test the Integration

Test if OpenHands can access the MCP servers:

```bash
openhands test-mcp github
openhands test-mcp filesystem
openhands test-mcp n8n
```

Test if OpenHands can trigger n8n workflows:

```bash
openhands trigger-webhook n8n --event command_executed --data '{"command": "ls", "output": "test output"}'
```

## Using OpenHands with MCP Servers

### GitHub Operations

You can use OpenHands to interact with GitHub repositories:

```bash
openhands "Create a new issue in the EcoSphereNetwork/Dev-Server-Workflow repository titled 'Update documentation' with the description 'The installation guide needs updating.'"
```

OpenHands will use the GitHub MCP server to create the issue.

### File Operations

You can use OpenHands to interact with the file system:

```bash
openhands "Create a new Python script that monitors the status of all MCP servers and sends an alert if any of them are down."
```

OpenHands will use the Filesystem MCP server to create the script.

### n8n Workflow Operations

You can use OpenHands to trigger n8n workflows:

```bash
openhands "Sync the documentation between GitHub and AFFiNE."
```

OpenHands will use the n8n MCP server to trigger the document sync workflow.

## Advanced Configuration

### Custom MCP Server Configuration

You can customize the MCP server configuration for OpenHands:

```bash
openhands config set mcpServers.github.command "python"
openhands config set mcpServers.github.args "['/path/to/github_mcp.py']"
openhands config set mcpServers.github.env.GITHUB_TOKEN "your_github_token"
openhands config set mcpServers.github.autoApprove "['create_issue', 'create_pull_request']"
```

### Custom n8n Webhook Configuration

You can customize the n8n webhook configuration for OpenHands:

```bash
openhands config set webhooks.n8n.headers.Authorization "Bearer your_auth_token"
openhands config set webhooks.n8n.events "['command_executed', 'file_changed', 'agent_started', 'agent_stopped', 'custom_event']"
```

## Troubleshooting

### MCP Server Connection Issues

If OpenHands cannot connect to MCP servers:

1. Check if the MCP servers are running:

```bash
./cli/dev-server.sh status
```

2. Check if the MCP servers are accessible:

```bash
curl -X POST http://localhost:3005 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

3. Check the OpenHands MCP configuration:

```bash
openhands config get mcpServers
```

### n8n Webhook Issues

If OpenHands cannot trigger n8n workflows:

1. Check if n8n is running:

```bash
./cli/dev-server.sh status
```

2. Check if the webhook is accessible:

```bash
curl -X POST http://localhost:5678/webhook/openhands \
  -H "Content-Type: application/json" \
  -d '{"event": "command_executed", "data": {"command": "ls", "output": "test output"}}'
```

3. Check the n8n execution logs in the web interface.

### Permission Issues

If OpenHands encounters permission issues:

1. Check if the MCP servers have the necessary permissions:

```bash
ls -la ~/.config/openhands/
```

2. Check if the environment variables are set correctly:

```bash
env | grep GITHUB_TOKEN
env | grep N8N_API_KEY
```