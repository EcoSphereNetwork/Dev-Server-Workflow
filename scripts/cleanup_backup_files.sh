#!/bin/bash

# Script to clean up backup files

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Cleaning up backup files..."

# Move backup files to the legacy directory
echo "Moving backup files to the legacy directory..."
find "$REPO_ROOT" -type f -name "*.bak*" -o -name "*.old" -o -name "*.tmp" | grep -v "node_modules" | while read file; do
    # Create the directory structure in the legacy directory
    legacy_dir="$REPO_ROOT/legacy$(dirname "$file" | sed "s|$REPO_ROOT||")"
    mkdir -p "$legacy_dir"
    
    # Move the file
    mv "$file" "$legacy_dir/"
    
    echo "Moved $file to $legacy_dir/"
done

echo "Cleanup complete!"