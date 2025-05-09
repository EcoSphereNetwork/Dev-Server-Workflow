#!/bin/bash

# Main setup script for MCP servers

# Set up environment variables
export WORKSPACE_PATH=${WORKSPACE_PATH:-/workspace}
export N8N_URL=${N8N_URL:-http://localhost:5678}
export OPENHANDS_CONFIG_DIR=${OPENHANDS_CONFIG_DIR:-/workspace/openhands-config}

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit the .env file with your configuration."
    echo "Press Enter to continue..."
    read
fi

# Pull Docker images
echo "Pulling Docker images..."
./pull-images.sh

# Start MCP servers
echo "Starting MCP servers..."
./start-mcp-servers.sh

# Wait for servers to start
echo "Waiting for servers to start..."
sleep 10

# Test MCP servers
echo "Testing MCP servers..."
./test-mcp-servers.py
if [ $? -ne 0 ]; then
    echo "Some MCP servers failed the test. Please check the logs."
    echo "Do you want to continue with the setup? (y/n)"
    read continue_setup
    if [ "$continue_setup" != "y" ]; then
        echo "Setup aborted."
        exit 1
    fi
fi

# Integrate with n8n if N8N_API_KEY is set
if [ -n "$N8N_API_KEY" ]; then
    echo "Integrating with n8n..."
    ./n8n-mcp-integration.py --n8n-url "$N8N_URL" --n8n-api-key "$N8N_API_KEY"
else
    echo "N8N_API_KEY is not set. Skipping n8n integration."
fi

# Integrate with OpenHands
echo "Integrating with OpenHands..."
./openhands-mcp-integration.py --openhands-config-dir "$OPENHANDS_CONFIG_DIR"

echo "Setup completed successfully! 🎉"
echo "The MCP servers are now running and integrated with n8n and OpenHands."
echo "To stop the MCP servers, run: ./stop-mcp-servers.sh"