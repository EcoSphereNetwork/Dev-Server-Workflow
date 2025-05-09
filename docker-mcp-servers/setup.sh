#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Main setup script for MCP servers

# Set up environment variables
export WORKSPACE_PATH=${WORKSPACE_PATH:-/workspace}
export N8N_URL=${N8N_URL:-http://localhost:5678}
export OPENHANDS_CONFIG_DIR=${OPENHANDS_CONFIG_DIR:-/workspace/openhands-config}

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    log_info "Creating .env file..."
    cp .env.example .env
    log_info "Please edit the .env file with your configuration."
    log_info "Press Enter to continue..."
    read
fi

# Pull Docker images
log_info "Pulling Docker images..."
./pull-images.sh

# Start MCP servers
log_info "Starting MCP servers..."
./start-mcp-servers.sh

# Wait for servers to start
log_info "Waiting for servers to start..."
sleep 10

# Test MCP servers
log_info "Testing MCP servers..."
./test-mcp-servers.py
if [ $? -ne 0 ]; then
    log_info "Some MCP servers failed the test. Please check the logs."
    log_info "Do you want to continue with the setup? (y/n)"
    read continue_setup
    if [ "$continue_setup" != "y" ]; then
        log_info "Setup aborted."
        exit 1
    fi
fi

# Integrate with n8n if N8N_API_KEY is set
if [ -n "$N8N_API_KEY" ]; then
    log_info "Integrating with n8n..."
    ./n8n-mcp-integration.py --n8n-url "$N8N_URL" --n8n-api-key "$N8N_API_KEY"
else
    log_info "N8N_API_KEY is not set. Skipping n8n integration."
fi

# Integrate with OpenHands
log_info "Integrating with OpenHands..."
./openhands-mcp-integration.py --openhands-config-dir "$OPENHANDS_CONFIG_DIR"

log_info "Setup completed successfully! 🎉"
log_info "The MCP servers are now running and integrated with n8n and OpenHands."
log_info "To stop the MCP servers, run: ./stop-mcp-servers.sh"