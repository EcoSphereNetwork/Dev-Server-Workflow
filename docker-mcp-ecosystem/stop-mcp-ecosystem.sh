#!/bin/bash

# Stop MCP Ecosystem
# This script stops all MCP servers and n8n

# Set script to exit on error
set -e

echo "Stopping MCP ecosystem..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
  echo "ERROR: docker-compose is not installed or not in PATH."
  exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "ERROR: Docker is not running or not accessible."
  exit 1
fi

# Stop the containers
docker-compose down

echo "MCP ecosystem stopped successfully!"