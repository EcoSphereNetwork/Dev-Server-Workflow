#!/bin/bash

# Script to start the MCP servers

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it based on .env.example."
    exit 1
fi

# Start the MCP servers
echo "Starting MCP servers..."
docker-compose up -d

# Check if all containers are running
echo "Checking container status..."
docker-compose ps

echo "MCP servers have been started. Use 'docker-compose logs' to view the logs."