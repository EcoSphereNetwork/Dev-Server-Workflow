#!/bin/bash

# Script to help users migrate to the new directory structure

set -e

echo "Migrating to the new directory structure..."

# Create symlinks for backward compatibility
echo "Creating symlinks for backward compatibility..."

# MCP server symlinks
ln -sf /workspace/Dev-Server-Workflow/src/mcp/base/base_mcp_server.py /workspace/Dev-Server-Workflow/src/mcp/base_mcp_server.py
ln -sf /workspace/Dev-Server-Workflow/src/mcp/servers/docker/docker_mcp_server.py /workspace/Dev-Server-Workflow/src/mcp/docker_mcp_server.py
ln -sf /workspace/Dev-Server-Workflow/src/mcp/servers/n8n/n8n_mcp_server.py /workspace/Dev-Server-Workflow/src/mcp/n8n_mcp_server.py
ln -sf /workspace/Dev-Server-Workflow/src/mcp/servers/openhands/openhands_mcp_server.py /workspace/Dev-Server-Workflow/src/mcp/openhands_server.py

# Script symlinks
ln -sf /workspace/Dev-Server-Workflow/scripts/start-all-mcp-servers.sh /workspace/Dev-Server-Workflow/start-mcp-servers.sh
ln -sf /workspace/Dev-Server-Workflow/scripts/stop-all-mcp-servers.sh /workspace/Dev-Server-Workflow/stop-mcp-servers.sh
ln -sf /workspace/Dev-Server-Workflow/scripts/start-web-ui.sh /workspace/Dev-Server-Workflow/start-web-ui.sh
ln -sf /workspace/Dev-Server-Workflow/scripts/stop-web-ui.sh /workspace/Dev-Server-Workflow/stop-web-ui.sh

echo "Migration complete!"
echo "Please update your imports to use the new structure."
echo "For example, change:"
echo "  from src.mcp.base_mcp_server import BaseMCPServer"
echo "to:"
echo "  from src.mcp.base.base_mcp_server import BaseMCPServer"
echo ""
echo "See the documentation for more details."