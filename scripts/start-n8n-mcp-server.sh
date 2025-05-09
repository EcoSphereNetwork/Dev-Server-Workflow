#!/bin/bash

# Script to start the n8n MCP Server

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create logs directory if it doesn't exist
mkdir -p "$REPO_ROOT/logs"

# Start the n8n MCP Server
echo "Starting n8n MCP Server..."
cd "$REPO_ROOT"
python -m src.mcp_servers.n8n_mcp_server.main "$@"