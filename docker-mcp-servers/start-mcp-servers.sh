#!/bin/bash

# Script to start the MCP servers

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display messages
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    warn ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        log "Created .env file from .env.example. Please edit it with your configuration."
    else
        error ".env.example file not found. Please create a .env file manually."
        exit 1
    fi
fi

# Start the MCP servers
log "Starting MCP servers..."
docker-compose up -d

# Check if all containers are running
log "Checking if all containers are running..."
if docker-compose ps | grep -q "Exit"; then
    error "Some containers failed to start. Please check the logs with 'docker-compose logs'."
    exit 1
fi

log "All MCP servers are running."
log "You can access the MCP Inspector UI at http://localhost:8080"
log "You can stop the MCP servers with './stop-mcp-servers.sh'"

# List all running MCP servers
log "Running MCP servers:"
docker-compose ps
