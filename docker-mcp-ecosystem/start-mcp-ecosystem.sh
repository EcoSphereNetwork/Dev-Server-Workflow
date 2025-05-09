#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Start MCP Ecosystem
# This script starts all MCP servers and n8n for workflow automation

# Set script to exit on error
set -e

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
  log_info "Creating .env file from .env.example..."
  cp .env.example .env
  log_info "Please edit .env file with your configuration values."
  log_info "Then run this script again."
  exit 1
fi

# Source environment variables
source .env

# Check for required environment variables
if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "your-github-token" ]; then
  log_info "ERROR: GITHUB_TOKEN is not set in .env file."
  log_info "Please set a valid GitHub token and try again."
  exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  log_info "ERROR: Docker is not running or not accessible."
  log_info "Please start Docker and try again."
  exit 1
fi

# Pull required images
log_info "Pulling required Docker images..."
docker pull redis:7-alpine
docker pull postgres:14-alpine
docker pull n8nio/n8n:latest

# Check if MCP images exist
log_info "Checking for MCP server images..."
MCP_IMAGES=("mcp/filesystem" "mcp/desktop-commander" "mcp/sequentialthinking" "mcp/github-chat" "mcp/github" "mcp/puppeteer" "mcp/basic-memory" "mcp/wikipedia-mcp" "mcp/inspector")

MISSING_IMAGES=()
for IMAGE in "${MCP_IMAGES[@]}"; do
  if ! docker image inspect "$IMAGE" > /dev/null 2>&1; then
    MISSING_IMAGES+=("$IMAGE")
  fi
done

if [ ${#MISSING_IMAGES[@]} -gt 0 ]; then
  log_info "WARNING: The following MCP images are missing:"
  for IMAGE in "${MISSING_IMAGES[@]}"; do
    log_info "  - $IMAGE"
  done
  
  log_info "Would you like to pull these images from Docker Hub? (y/n)"
  read -r PULL_IMAGES
  
  if [[ "$PULL_IMAGES" =~ ^[Yy]$ ]]; then
    for IMAGE in "${MISSING_IMAGES[@]}"; do
      log_info "Pulling $IMAGE..."
      docker pull "$IMAGE:latest" || log_info "Failed to pull $IMAGE. It may not exist on Docker Hub."
    done
  else
    log_info "Please build or pull the missing images before continuing."
    exit 1
  fi
fi

# Start the containers
log_info "Starting MCP ecosystem..."
docker compose up -d

# Wait for services to be ready
log_info "Waiting for services to be ready..."
sleep 10

# Check if n8n is running
log_info "Checking n8n status..."
if docker ps | grep -q "n8n"; then
  log_info "n8n is running."
else
  log_info "ERROR: n8n failed to start. Check logs with 'docker compose logs n8n'"
  exit 1
fi

# Import workflows
log_info "Importing n8n workflows..."
WORKFLOW_DIR="/workspace/Dev-Server-Workflow/src/ESN_Initial-Szenario/n8n-workflows"
if [ -d "$WORKFLOW_DIR" ]; then
  # Wait for n8n to be fully ready
  log_info "Waiting for n8n to be fully ready..."
  sleep 20
  
  # Import each workflow
  for WORKFLOW in "$WORKFLOW_DIR"/*.json; do
    WORKFLOW_NAME=$(basename "$WORKFLOW" .json)
    log_info "Importing workflow: $WORKFLOW_NAME"
    
    # Use n8n CLI to import workflow
    docker exec n8n n8n import:workflow --file="/workspace/Dev-Server-Workflow/src/ESN_Initial-Szenario/n8n-workflows/$WORKFLOW_NAME.json" --skipOwnershipCheck
  done
  
  log_info "Workflows imported successfully."
else
  log_info "WARNING: Workflow directory not found at $WORKFLOW_DIR"
fi

log_info "MCP ecosystem started successfully!"
log_info "Access n8n at: http://localhost:5678"
log_info "Access MCP Inspector at: http://localhost:8080"

# List running MCP servers
log_info "\nRunning MCP servers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "mcp-"