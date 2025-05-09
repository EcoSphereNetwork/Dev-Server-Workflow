#!/bin/bash

# Script to consolidate Docker configurations

set -e

echo "Consolidating Docker configurations..."

# Create the docker/compose directory structure
mkdir -p /workspace/Dev-Server-Workflow/docker/compose/mcp-ecosystem
mkdir -p /workspace/Dev-Server-Workflow/docker/compose/mcp-servers
mkdir -p /workspace/Dev-Server-Workflow/docker/compose/monitoring

# Copy Docker Compose files
echo "Copying Docker Compose files..."
cp /workspace/Dev-Server-Workflow/docker-mcp-ecosystem/docker-compose.yml /workspace/Dev-Server-Workflow/docker/compose/mcp-ecosystem/
cp /workspace/Dev-Server-Workflow/docker-mcp-servers/docker-compose.yml /workspace/Dev-Server-Workflow/docker/compose/mcp-servers/
cp /workspace/Dev-Server-Workflow/docker-mcp-servers/docker-compose-full.yml /workspace/Dev-Server-Workflow/docker/compose/mcp-servers/
cp /workspace/Dev-Server-Workflow/docker-mcp-servers/monitoring/docker-compose.yml /workspace/Dev-Server-Workflow/docker/compose/monitoring/

# Create symlinks for backward compatibility
echo "Creating symlinks for backward compatibility..."
ln -sf /workspace/Dev-Server-Workflow/docker/compose/mcp-ecosystem/docker-compose.yml /workspace/Dev-Server-Workflow/docker-mcp-ecosystem/docker-compose.yml
ln -sf /workspace/Dev-Server-Workflow/docker/compose/mcp-servers/docker-compose.yml /workspace/Dev-Server-Workflow/docker-mcp-servers/docker-compose.yml
ln -sf /workspace/Dev-Server-Workflow/docker/compose/mcp-servers/docker-compose-full.yml /workspace/Dev-Server-Workflow/docker-mcp-servers/docker-compose-full.yml
ln -sf /workspace/Dev-Server-Workflow/docker/compose/monitoring/docker-compose.yml /workspace/Dev-Server-Workflow/docker-mcp-servers/monitoring/docker-compose.yml

echo "Consolidation complete!"