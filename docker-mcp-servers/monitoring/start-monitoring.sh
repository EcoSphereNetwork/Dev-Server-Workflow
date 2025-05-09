#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Script to start the monitoring stack for MCP servers

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display messages
log() {
    log_info "${GREEN}[INFO]${NC} $1"
}

warn() {
    log_info "${YELLOW}[WARN]${NC} $1"
}

error() {
    log_info "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if MCP network exists
if ! docker network inspect mcp-network > /dev/null 2>&1; then
    warn "MCP network does not exist. Creating it..."
    docker network create mcp-network
fi

# Start the monitoring stack
log "Starting monitoring stack..."
docker compose up -d

# Check if all containers are running
log "Checking if all containers are running..."
if docker compose ps | grep -q "Exit"; then
    error "Some containers failed to start. Please check the logs with 'docker compose logs'."
    exit 1
fi

log "Monitoring stack is running."
log "You can access Prometheus at http://localhost:9090"
log "You can access Grafana at http://localhost:3000 (admin/admin)"
log "You can access cAdvisor at http://localhost:8081"

# List all running monitoring containers
log "Running monitoring containers:"
docker compose ps

exit 0