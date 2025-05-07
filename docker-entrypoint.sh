#!/bin/bash

# Docker entrypoint script to prepare Python module environment
# This creates symlinks for all Python modules and adds the src directory to PYTHONPATH

echo "Setting up Python environment for n8n workflow integration..."

# Go to the source directory
cd /app/src

# Create symlinks for all Python modules (both directions to be safe)
for file in n8n-*.py; do
  if [ -f "$file" ]; then
    module_name="${file//-/_}"
    # Create symlink if it doesn't exist
    if [ ! -L "$module_name" ]; then
      ln -sf "$file" "$module_name"
      echo "Created symlink: $file -> $module_name"
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
      echo "Created symlink: $file -> $module_name"
    fi
  fi
done

# Add the current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/app/src
echo "Added /app/src to PYTHONPATH"

# Create an __init__.py file if it doesn't exist
if [ ! -f "__init__.py" ]; then
  echo '"""n8n Workflow Integration package"""' > __init__.py
  echo "Created __init__.py file"
fi

echo "Python environment setup complete"

# Display Python path for debugging
echo "Python path:"
python -c "import sys; print(sys.path)"

# Run the original command
echo "Running original command: $@"
exec "$@"
