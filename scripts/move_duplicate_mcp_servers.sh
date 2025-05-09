#!/bin/bash

# Script to move duplicate MCP server implementations to the legacy directory

set -e

echo "Moving duplicate MCP server implementations to the legacy directory..."

# Create the legacy directory structure
mkdir -p /workspace/Dev-Server-Workflow/legacy/src/mcp
mkdir -p /workspace/Dev-Server-Workflow/legacy/src/mcp_servers

# Move duplicate MCP server implementations
echo "Moving duplicate MCP server implementations..."
mv /workspace/Dev-Server-Workflow/src/docker_mcp_server.py /workspace/Dev-Server-Workflow/legacy/src/
mv /workspace/Dev-Server-Workflow/src/n8n_mcp_server.py /workspace/Dev-Server-Workflow/legacy/src/
mv /workspace/Dev-Server-Workflow/src/simple_mcp_server.py /workspace/Dev-Server-Workflow/legacy/src/
mv /workspace/Dev-Server-Workflow/src/mcp_server_enhanced.py /workspace/Dev-Server-Workflow/legacy/src/

# Move old MCP server implementations
echo "Moving old MCP server implementations..."
mv /workspace/Dev-Server-Workflow/src/mcp/base_mcp_server.py /workspace/Dev-Server-Workflow/legacy/src/mcp/
mv /workspace/Dev-Server-Workflow/src/mcp/n8n_server.py /workspace/Dev-Server-Workflow/legacy/src/mcp/
mv /workspace/Dev-Server-Workflow/src/mcp/openhands_server.py /workspace/Dev-Server-Workflow/legacy/src/mcp/

echo "Move complete!"