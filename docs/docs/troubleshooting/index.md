# Troubleshooting Guide

This guide provides solutions for common issues you might encounter when using the Dev-Server-Workflow ecosystem.

## Docker Issues

### Docker Not Starting

**Symptoms:**
- `Cannot connect to the Docker daemon` error
- Components show as stopped in status check

**Solutions:**

1. Check if Docker daemon is running:
   ```bash
   sudo systemctl status docker
   ```

2. Start Docker daemon:
   ```bash
   sudo systemctl start docker
   ```

3. If in a container environment without systemd:
   ```bash
   sudo dockerd > /tmp/docker.log 2>&1 &
   ```

4. Check Docker logs:
   ```bash
   sudo journalctl -u docker
   ```

### Docker Permission Issues

**Symptoms:**
- `Permission denied` when running Docker commands

**Solutions:**

1. Add your user to the Docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```

2. Log out and log back in, or run:
   ```bash
   newgrp docker
   ```

### Docker Compose Not Found

**Symptoms:**
- `docker compose: command not found` error

**Solutions:**

1. Install Docker Compose:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker compose
   ```

2. Install Docker Compose using pip:
   ```bash
   pip install docker compose
   ```

## n8n Issues

### n8n Not Starting

**Symptoms:**
- n8n shows as stopped in status check
- Cannot access n8n web interface

**Solutions:**

1. Check n8n Docker logs:
   ```bash
   docker logs n8n
   ```

2. Check if ports are already in use:
   ```bash
   netstat -tuln | grep 5678
   ```

3. Restart n8n:
   ```bash
   ./cli/dev-server.sh restart n8n
   ```

4. Check n8n data directory permissions:
   ```bash
   ls -la n8n_data
   sudo chown -R 1000:1000 n8n_data
   ```

### n8n Workflow Execution Failures

**Symptoms:**
- Workflows fail to execute
- Error messages in n8n execution logs

**Solutions:**

1. Check n8n execution logs in the web interface:
   - Go to Executions
   - Find the failed execution
   - Click on it to see the error details

2. Check if credentials are valid:
   - Go to Credentials
   - Test the credentials

3. Check if the workflow is activated:
   - Go to Workflows
   - Make sure the toggle is set to "Active"

4. Check if webhook URLs are accessible:
   - Test the webhook URL with curl:
     ```bash
     curl -X POST http://localhost:5678/webhook/github
     ```

### n8n API Key Issues

**Symptoms:**
- `Unauthorized` errors when accessing n8n API
- Workflows cannot be created or updated

**Solutions:**

1. Regenerate the API key in the n8n web interface:
   - Go to Settings > API
   - Create a new API key

2. Update your `.env` file with the new API key:
   ```bash
   N8N_API_KEY=your_new_api_key
   ```

3. Restart the setup:
   ```bash
   python setup.py install --env-file .env --no-install
   ```

## MCP Server Issues

### MCP Server Not Starting

**Symptoms:**
- MCP server shows as stopped in status check
- Cannot connect to MCP server

**Solutions:**

1. Check MCP server logs:
   ```bash
   docker logs mcp-github
   ```

2. Check if ports are already in use:
   ```bash
   netstat -tuln | grep 3005
   ```

3. Check if required environment variables are set:
   ```bash
   docker exec mcp-github env | grep GITHUB_TOKEN
   ```

4. Restart the MCP server:
   ```bash
   ./cli/dev-server.sh restart mcp
   ```

### MCP Server Connection Issues

**Symptoms:**
- `Connection refused` errors when connecting to MCP server
- OpenHands cannot connect to MCP server

**Solutions:**

1. Check if MCP server is running:
   ```bash
   ./cli/dev-server.sh status
   ```

2. Check if MCP server is accessible:
   ```bash
   curl -X POST http://localhost:3005 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
   ```

3. Check if MCP server is listening on the correct interface:
   ```bash
   docker exec mcp-github netstat -tuln
   ```

4. Check if firewall is blocking the connection:
   ```bash
   sudo ufw status
   ```

### MCP Server Authentication Issues

**Symptoms:**
- `Unauthorized` errors when using MCP server
- GitHub API rate limit exceeded

**Solutions:**

1. Check if GitHub token is valid:
   ```bash
   curl -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/user
   ```

2. Update GitHub token in `.env` file:
   ```bash
   GITHUB_TOKEN=your_new_github_token
   ```

3. Restart the MCP server:
   ```bash
   ./cli/dev-server.sh restart mcp
   ```

## OpenHands Integration Issues

### OpenHands Cannot Connect to MCP Servers

**Symptoms:**
- OpenHands reports "Failed to connect to MCP server"
- MCP tools not available in OpenHands

**Solutions:**

1. Check if MCP servers are running:
   ```bash
   ./cli/dev-server.sh status
   ```

2. Check OpenHands MCP configuration:
   ```bash
   openhands config get mcpServers
   ```

3. Regenerate OpenHands MCP configuration:
   ```bash
   ./cli/dev-server.sh config openhands-mcp
   ```

4. Check if OpenHands has the necessary permissions:
   ```bash
   ls -la ~/.config/openhands/
   ```

### OpenHands Cannot Trigger n8n Workflows

**Symptoms:**
- OpenHands reports "Failed to trigger webhook"
- n8n workflows not triggered by OpenHands

**Solutions:**

1. Check if n8n is running:
   ```bash
   ./cli/dev-server.sh status
   ```

2. Check OpenHands webhook configuration:
   ```bash
   openhands config get webhooks.n8n
   ```

3. Test the webhook manually:
   ```bash
   curl -X POST http://localhost:5678/webhook/openhands \
     -H "Content-Type: application/json" \
     -d '{"event": "command_executed", "data": {"command": "ls", "output": "test output"}}'
   ```

4. Check n8n execution logs in the web interface.

## CLI Issues

### CLI Command Not Found

**Symptoms:**
- `dev-server.sh: command not found` error

**Solutions:**

1. Make sure the script is executable:
   ```bash
   chmod +x cli/dev-server.sh
   ```

2. Make sure the CLI directory is in your PATH:
   ```bash
   echo $PATH | grep cli
   ```

3. Run the script with its full path:
   ```bash
   ./cli/dev-server.sh help
   ```

### CLI Cannot Connect to Components

**Symptoms:**
- CLI reports components as stopped
- CLI cannot start or stop components

**Solutions:**

1. Check if Docker is running:
   ```bash
   docker info
   ```

2. Check if components are running outside of CLI:
   ```bash
   docker ps
   ```

3. Check CLI configuration:
   ```bash
   cat cli/config.sh
   ```

## Environment Issues

### Missing Environment Variables

**Symptoms:**
- Components fail to start
- Authentication errors

**Solutions:**

1. Check if `.env` file exists:
   ```bash
   ls -la .env
   ```

2. Check if `.env` file has the required variables:
   ```bash
   cat .env | grep GITHUB_TOKEN
   cat .env | grep N8N_API_KEY
   ```

3. Copy the environment template and fill in the values:
   ```bash
   cp src/env-template .env
   ```

### Port Conflicts

**Symptoms:**
- Components fail to start
- `port is already allocated` errors

**Solutions:**

1. Check if ports are already in use:
   ```bash
   netstat -tuln
   ```

2. Stop the process using the port:
   ```bash
   sudo fuser -k 5678/tcp
   ```

3. Change the port in the configuration:
   ```bash
   # For n8n
   sed -i 's/5678/5679/g' docker compose.yml
   ```

## Getting Help

If you're still experiencing issues:

1. Check the logs:
   ```bash
   ./cli/dev-server.sh logs all
   ```

2. Run the diagnostic tool:
   ```bash
   python src/diagnostic.py
   ```

3. Open an issue on GitHub:
   [https://github.com/EcoSphereNetwork/Dev-Server-Workflow/issues](https://github.com/EcoSphereNetwork/Dev-Server-Workflow/issues)

4. Ask for help in the community Discord:
   [https://discord.gg/ecosphere](https://discord.gg/ecosphere)