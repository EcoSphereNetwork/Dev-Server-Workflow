#!/bin/bash

# Master script to run all the reorganization scripts

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting repository reorganization..."

# Run the cleanup scripts
echo "Running cleanup scripts..."
"$REPO_ROOT/scripts/cleanup_backup_files.sh"
"$REPO_ROOT/scripts/move_duplicate_mcp_servers.sh"
"$REPO_ROOT/scripts/consolidate_docker_configs.sh"

# Run the migration script
echo "Running migration script..."
"$REPO_ROOT/scripts/migrate_to_new_structure.sh"

# Update the README
echo "Updating README..."
if [ -f "$REPO_ROOT/README.md.new" ]; then
    mv "$REPO_ROOT/README.md.new" "$REPO_ROOT/README.md"
    echo "README.md updated"
else
    echo "README.md.new not found, skipping"
fi

echo "Repository reorganization complete!"
echo "Please see the new README.md for details on the new structure."