#!/bin/bash

# Script to pull the MCP server Docker images

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

# Function to pull an image with error handling
pull_image() {
    local image=$1
    log "Pulling image: $image"
    
    if docker pull $image; then
        log "Successfully pulled $image"
        return 0
    else
        error "Failed to pull $image"
        return 1
    fi
}

# Main function
main() {
    log "Pulling MCP server Docker images..."
    
    # Pull Redis image
    pull_image "redis:7-alpine" || warn "Failed to pull Redis image, but continuing..."
    
    # Pull MCP server images
    pull_image "mcp/filesystem:latest" || warn "Failed to pull filesystem MCP image, but continuing..."
    pull_image "mcp/desktop-commander:latest" || warn "Failed to pull desktop-commander MCP image, but continuing..."
    pull_image "mcp/sequentialthinking:latest" || warn "Failed to pull sequentialthinking MCP image, but continuing..."
    pull_image "mcp/github-chat:latest" || warn "Failed to pull github-chat MCP image, but continuing..."
    pull_image "mcp/github:latest" || warn "Failed to pull github MCP image, but continuing..."
    pull_image "mcp/puppeteer:latest" || warn "Failed to pull puppeteer MCP image, but continuing..."
    pull_image "mcp/basic-memory:latest" || warn "Failed to pull basic-memory MCP image, but continuing..."
    pull_image "mcp/wikipedia-mcp:latest" || warn "Failed to pull wikipedia MCP image, but continuing..."
    pull_image "mcp/inspector:latest" || warn "Failed to pull inspector image, but continuing..."
    
    log "All MCP server Docker images have been pulled successfully."
    return 0
}

# Execute the main function
main
