#!/bin/bash

# Script to assist with workflow file consolidation
# Created as part of the Dev-Server-Workflow repository cleanup project

# Create new workflow directory structure
echo "Creating new workflow directory structure..."
mkdir -p src/workflows/n8n/integrations
mkdir -p src/workflows/n8n/triggers
mkdir -p src/workflows/n8n/mcp
mkdir -p src/workflows/n8n/openhands
mkdir -p src/workflows/n8n/utilities
mkdir -p src/workflows/n8n/llm

# Create placeholder README files
echo "Creating placeholder README files..."
echo "# Integration Workflows" > src/workflows/n8n/integrations/README.md
echo "# Trigger Workflows" > src/workflows/n8n/triggers/README.md
echo "# MCP Server Workflows" > src/workflows/n8n/mcp/README.md
echo "# OpenHands Workflows" > src/workflows/n8n/openhands/README.md
echo "# Utility Workflows" > src/workflows/n8n/utilities/README.md
echo "# LLM Workflows" > src/workflows/n8n/llm/README.md

# Archive original workflow files
echo "Archiving original workflow files..."
mkdir -p legacy/archive/workflows
mkdir -p legacy/archive/workflows/n8n-workflows
mkdir -p legacy/archive/workflows/workflows-n8n

# Copy original workflows to archive
echo "Copying original workflows to archive..."
cp -r src/n8n-workflows/* legacy/archive/workflows/n8n-workflows/
cp -r src/workflows/n8n/* legacy/archive/workflows/workflows-n8n/

echo "Workflow file consolidation preparation complete."
echo "Next steps:"
echo "1. Move integration workflows to src/workflows/n8n/integrations/"
echo "2. Move trigger workflows to src/workflows/n8n/triggers/"
echo "3. Move MCP server workflows to src/workflows/n8n/mcp/"
echo "4. Move OpenHands workflows to src/workflows/n8n/openhands/"
echo "5. Move utility workflows to src/workflows/n8n/utilities/"
echo "6. Move LLM workflows to src/workflows/n8n/llm/"
echo "7. Update workflow documentation"