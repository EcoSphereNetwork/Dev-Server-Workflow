#!/bin/bash

# Master script to run all the reorganization scripts

set -e

echo "Starting repository reorganization..."

# Run the cleanup scripts
echo "Running cleanup scripts..."
./scripts/cleanup_backup_files.sh
./scripts/move_duplicate_mcp_servers.sh
./scripts/consolidate_docker_configs.sh

# Run the migration script
echo "Running migration script..."
./scripts/migrate_to_new_structure.sh

# Update the README
echo "Updating README..."
mv /workspace/Dev-Server-Workflow/README.md.new /workspace/Dev-Server-Workflow/README.md

echo "Repository reorganization complete!"
echo "Please see the new README.md for details on the new structure."