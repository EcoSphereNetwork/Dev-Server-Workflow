#!/bin/bash

# Script to move duplicate MCP server implementations to the legacy directory

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Repository root: $REPO_ROOT"

echo "Moving duplicate MCP server implementations to the legacy directory..."

# Create the legacy directory structure
mkdir -p "$REPO_ROOT/legacy/src/mcp"
mkdir -p "$REPO_ROOT/legacy/src/mcp_servers"

# Move duplicate MCP server implementations
echo "Moving duplicate MCP server implementations..."
for file in "$REPO_ROOT/src/docker_mcp_server.py" \
            "$REPO_ROOT/src/n8n_mcp_server.py" \
            "$REPO_ROOT/src/simple_mcp_server.py" \
            "$REPO_ROOT/src/mcp_server_enhanced.py"; do
    if [ -f "$file" ]; then
        mv "$file" "$REPO_ROOT/legacy/src/"
        echo "Moved $file to $REPO_ROOT/legacy/src/"
    else
        echo "File $file not found, skipping"
    fi
done

# Move old MCP server implementations
echo "Moving old MCP server implementations..."
for file in "$REPO_ROOT/src/mcp/base_mcp_server.py" \
            "$REPO_ROOT/src/mcp/n8n_server.py" \
            "$REPO_ROOT/src/mcp/openhands_server.py"; do
    if [ -f "$file" ]; then
        mv "$file" "$REPO_ROOT/legacy/src/mcp/"
        echo "Moved $file to $REPO_ROOT/legacy/src/mcp/"
    else
        echo "File $file not found, skipping"
    fi
done

echo "Move complete!"
