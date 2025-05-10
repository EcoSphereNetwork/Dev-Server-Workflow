#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Docker entrypoint script to prepare Python module environment
# This creates symlinks for all Python modules and adds the src directory to PYTHONPATH

log_info "Setting up Python environment for n8n workflow integration..."

# Go to the source directory
cd /app/src

# Create symlinks for all Python modules (both directions to be safe)
for file in n8n-*.py; do
  if [ -f "$file" ]; then
    module_name="${file//-/_}"
    # Create symlink if it doesn't exist
    if [ ! -L "$module_name" ]; then
      ln -sf "$file" "$module_name"
      log_info "Created symlink: $file -> $module_name"
    fi
  fi
done

# Also try the other way around
for file in n8n_*.py; do
  if [ -f "$file" ]; then
    module_name="${file//_/-}"
    # Create symlink if it doesn't exist
    if [ ! -L "$module_name" ]; then
      ln -sf "$file" "$module_name"
      log_info "Created symlink: $file -> $module_name"
    fi
  fi
done

# Add the current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/app/src
log_info "Added /app/src to PYTHONPATH"

# Create an __init__.py file if it doesn't exist
if [ ! -f "__init__.py" ]; then
  echo '"""n8n Workflow Integration package"""' > __init__.py
  log_info "Created __init__.py file"
fi

log_info "Python environment setup complete"

# Display Python path for debugging
log_info "Python path:"
python -c "import sys; print(sys.path)"

# Run the original command
log_info "Running original command: $@"
exec "$@"
