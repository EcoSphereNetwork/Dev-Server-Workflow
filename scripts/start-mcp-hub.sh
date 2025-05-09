#!/bin/bash

# Script to start the MCP Hub

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create logs directory if it doesn't exist
mkdir -p "$REPO_ROOT/logs"

# Start the MCP Hub
echo "Starting MCP Hub..."
cd "$REPO_ROOT"
python -m src.mcp_hub.main "$@"