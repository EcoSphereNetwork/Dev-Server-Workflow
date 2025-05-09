#!/bin/bash

# Script to clean up backup files

set -e

echo "Cleaning up backup files..."

# Move backup files to the legacy directory
echo "Moving backup files to the legacy directory..."
find /workspace/Dev-Server-Workflow -type f -name "*.bak*" -o -name "*.old" -o -name "*.tmp" | grep -v "node_modules" | while read file; do
    # Create the directory structure in the legacy directory
    legacy_dir="/workspace/Dev-Server-Workflow/legacy$(dirname "$file" | sed 's|/workspace/Dev-Server-Workflow||')"
    mkdir -p "$legacy_dir"
    
    # Move the file
    mv "$file" "$legacy_dir/"
    
    echo "Moved $file to $legacy_dir/"
done

echo "Cleanup complete!"