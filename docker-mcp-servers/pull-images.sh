#!/bin/bash

# Script to pull the MCP server Docker images

echo "Pulling MCP server Docker images..."

# Pull Redis image
docker pull redis:7-alpine

# Pull MCP server images
docker pull mcp/filesystem:latest
docker pull mcp/desktop-commander:latest
docker pull mcp/sequentialthinking:latest
docker pull mcp/github-chat:latest
docker pull mcp/github:latest
docker pull mcp/puppeteer:latest
docker pull mcp/basic-memory:latest
docker pull mcp/wikipedia-mcp:latest

echo "All MCP server Docker images have been pulled successfully."