#!/bin/bash

# Script to start the Docker MCP Server

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create logs directory if it doesn't exist
mkdir -p "$REPO_ROOT/logs"

# Start the Docker MCP Server
echo "Starting Docker MCP Server..."
cd "$REPO_ROOT"
python -m src.mcp_servers.docker_mcp.main "$@"