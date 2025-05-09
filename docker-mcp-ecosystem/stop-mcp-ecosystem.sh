#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Stop MCP Ecosystem
# This script stops all MCP servers and n8n

# Set script to exit on error
set -e

log_info "Stopping MCP ecosystem..."

# Check if docker compose is available
if ! command -v docker compose &> /dev/null; then
  log_info "ERROR: docker compose is not installed or not in PATH."
  exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  log_info "ERROR: Docker is not running or not accessible."
  exit 1
fi

# Stop the containers
docker compose down

log_info "MCP ecosystem stopped successfully!"