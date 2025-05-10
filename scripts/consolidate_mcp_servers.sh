#!/bin/bash

# Script to assist with MCP server consolidation
# Created as part of the Dev-Server-Workflow repository cleanup project

# Create archive directory
echo "Creating archive directory..."
mkdir -p legacy/archive/mcp

# Archive original MCP implementations
echo "Archiving original MCP implementations..."

# Archive src/mcp implementations
echo "Archiving src/mcp implementations..."
mkdir -p legacy/archive/mcp/src_mcp
cp -r src/mcp/* legacy/archive/mcp/src_mcp/

# Archive legacy/src implementations
echo "Archiving legacy/src implementations..."
mkdir -p legacy/archive/mcp/legacy_src
cp -r legacy/src/mcp* legacy/archive/mcp/legacy_src/
cp -r legacy/src/*/mcp* legacy/archive/mcp/legacy_src/ 2>/dev/null || true

# Create standard MCP server interface directory
echo "Creating standard MCP server interface directory..."
mkdir -p src/mcp_servers/base

# Create directories for consolidated MCP servers
echo "Creating directories for consolidated MCP servers..."
mkdir -p src/mcp_servers/docker
mkdir -p src/mcp_servers/n8n
mkdir -p src/mcp_servers/openhands
mkdir -p src/mcp_servers/prompt
mkdir -p src/mcp_servers/llm_cost

echo "MCP server consolidation preparation complete."
echo "Next steps:"
echo "1. Move src/mcp/base/base_mcp_server.py to src/mcp_servers/base/"
echo "2. Consolidate Docker MCP server implementations"
echo "3. Consolidate n8n MCP server implementations"
echo "4. Consolidate OpenHands MCP server implementations"
echo "5. Consolidate Prompt MCP server implementations"
echo "6. Consolidate LLM Cost Analyzer MCP server implementations"
echo "7. Update MCP Hub references"