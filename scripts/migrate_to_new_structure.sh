#!/bin/bash

# Script to help users migrate to the new directory structure

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Migrating to the new directory structure..."

# Create symlinks for backward compatibility
echo "Creating symlinks for backward compatibility..."

# MCP server symlinks
for src_file in "$REPO_ROOT/src/mcp/base/base_mcp_server.py" \
                "$REPO_ROOT/src/mcp/servers/docker/docker_mcp_server.py" \
                "$REPO_ROOT/src/mcp/servers/n8n/n8n_mcp_server.py" \
                "$REPO_ROOT/src/mcp/servers/openhands/openhands_mcp_server.py"; do
    if [ -f "$src_file" ]; then
        # Determine the destination file
        if [[ "$src_file" == *"base/base_mcp_server.py"* ]]; then
            dest_file="$REPO_ROOT/src/mcp/base_mcp_server.py"
        elif [[ "$src_file" == *"docker/docker_mcp_server.py"* ]]; then
            dest_file="$REPO_ROOT/src/mcp/docker_mcp_server.py"
        elif [[ "$src_file" == *"n8n/n8n_mcp_server.py"* ]]; then
            dest_file="$REPO_ROOT/src/mcp/n8n_mcp_server.py"
        elif [[ "$src_file" == *"openhands/openhands_mcp_server.py"* ]]; then
            dest_file="$REPO_ROOT/src/mcp/openhands_server.py"
        fi
        
        # Create the symlink
        ln -sf "$src_file" "$dest_file"
        echo "Created symlink from $src_file to $dest_file"
    else
        echo "File $src_file not found, skipping"
    fi
done

# Script symlinks
for src_file in "$REPO_ROOT/scripts/start-all-mcp-servers.sh" \
                "$REPO_ROOT/scripts/stop-all-mcp-servers.sh" \
                "$REPO_ROOT/scripts/start-web-ui.sh" \
                "$REPO_ROOT/scripts/stop-web-ui.sh"; do
    if [ -f "$src_file" ]; then
        # Determine the destination file
        filename=$(basename "$src_file")
        if [[ "$filename" == "start-all-mcp-servers.sh" ]]; then
            dest_file="$REPO_ROOT/start-mcp-servers.sh"
        elif [[ "$filename" == "stop-all-mcp-servers.sh" ]]; then
            dest_file="$REPO_ROOT/stop-mcp-servers.sh"
        else
            dest_file="$REPO_ROOT/$filename"
        fi
        
        # Create the symlink
        ln -sf "$src_file" "$dest_file"
        echo "Created symlink from $src_file to $dest_file"
    else
        echo "File $src_file not found, skipping"
    fi
done

echo "Migration complete!"
echo "Please update your imports to use the new structure."
echo "For example, change:"
echo "  from src.mcp.base_mcp_server import BaseMCPServer"
echo "to:"
echo "  from src.mcp.base.base_mcp_server import BaseMCPServer"
echo ""
echo "See the documentation for more details."