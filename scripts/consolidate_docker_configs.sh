#!/bin/bash

# Script to consolidate Docker configurations

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Consolidating Docker configurations..."

# Create the docker/compose directory structure
mkdir -p "$REPO_ROOT/docker/compose/mcp-ecosystem"
mkdir -p "$REPO_ROOT/docker/compose/mcp-servers"
mkdir -p "$REPO_ROOT/docker/compose/monitoring"

# Copy Docker Compose files
echo "Copying Docker Compose files..."
for src_file in "$REPO_ROOT/docker-mcp-ecosystem/docker-compose.yml" \
                "$REPO_ROOT/docker-mcp-servers/docker-compose.yml" \
                "$REPO_ROOT/docker-mcp-servers/docker-compose-full.yml" \
                "$REPO_ROOT/docker-mcp-servers/monitoring/docker-compose.yml"; do
    if [ -f "$src_file" ]; then
        # Determine the destination directory
        if [[ "$src_file" == *"docker-mcp-ecosystem"* ]]; then
            dest_dir="$REPO_ROOT/docker/compose/mcp-ecosystem"
        elif [[ "$src_file" == *"monitoring"* ]]; then
            dest_dir="$REPO_ROOT/docker/compose/monitoring"
        else
            dest_dir="$REPO_ROOT/docker/compose/mcp-servers"
        fi
        
        # Get the filename
        filename=$(basename "$src_file")
        
        # Copy the file
        cp "$src_file" "$dest_dir/$filename"
        echo "Copied $src_file to $dest_dir/$filename"
    else
        echo "File $src_file not found, skipping"
    fi
done

# Create symlinks for backward compatibility
echo "Creating symlinks for backward compatibility..."
for src_file in "$REPO_ROOT/docker/compose/mcp-ecosystem/docker-compose.yml" \
                "$REPO_ROOT/docker/compose/mcp-servers/docker-compose.yml" \
                "$REPO_ROOT/docker/compose/mcp-servers/docker-compose-full.yml" \
                "$REPO_ROOT/docker/compose/monitoring/docker-compose.yml"; do
    if [ -f "$src_file" ]; then
        # Determine the destination directory
        if [[ "$src_file" == *"mcp-ecosystem"* ]]; then
            dest_dir="$REPO_ROOT/docker-mcp-ecosystem"
        elif [[ "$src_file" == *"monitoring"* ]]; then
            dest_dir="$REPO_ROOT/docker-mcp-servers/monitoring"
        else
            dest_dir="$REPO_ROOT/docker-mcp-servers"
        fi
        
        # Get the filename
        filename=$(basename "$src_file")
        
        # Create the symlink
        ln -sf "$src_file" "$dest_dir/$filename"
        echo "Created symlink from $src_file to $dest_dir/$filename"
    else
        echo "File $src_file not found, skipping"
    fi
done

echo "Consolidation complete!"