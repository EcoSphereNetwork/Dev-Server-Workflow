#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Fix Python Import Issues for n8n Workflow Integration
#
# This script:
# 1. Creates backup of original files
# 2. Creates consistent module names (underscores instead of hyphens)
# 3. Updates import references in all files

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directory to work in
SRC_DIR="./src"

# Create backup of original files
BACKUP_DIR="./src_backup"
if [ ! -d "$BACKUP_DIR" ]; then
  log_info "${YELLOW}Creating backup of original files in $BACKUP_DIR${NC}"
  cp -r "$SRC_DIR" "$BACKUP_DIR"
  log_info "${GREEN}Backup created${NC}"
else
  log_info "${YELLOW}Backup directory already exists. Using existing backup.${NC}"
fi

# Map of file renames and create renamed files
log_info "${YELLOW}Creating files with underscores instead of hyphens...${NC}"
for file in "$SRC_DIR"/n8n-*.py; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    new_name="${filename//-/_}"
    new_path="$SRC_DIR/$new_name"
    
    # Create the new file if it doesn't already exist
    if [ ! -f "$new_path" ]; then
      cp "$file" "$new_path"
      log_info "${GREEN}Created $new_name from $filename${NC}"
    else
      log_info "${YELLOW}$new_name already exists, skipping${NC}"
    fi
  fi
done

# Update imports in all Python files
log_info "${YELLOW}Updating import statements in Python files...${NC}"
for file in "$SRC_DIR"/*.py; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    # Skip __init__.py and similar files
    if [[ "$filename" == __* ]]; then
      continue
    fi
    
    # Create temporary file
    temp_file=$(mktemp)
    
    # Process the file
    while IFS= read -r line; do
      # Check if line contains an import statement with n8n-* pattern
      if [[ "$line" =~ (from|import)\ +n8n[-_]([a-zA-Z0-9_]+[-_][a-zA-Z0-9_]+) ]]; then
        # Get the module name and replace hyphens with underscores
        import_type="${BASH_REMATCH[1]}"
        module="${BASH_REMATCH[2]}"
        new_module="${module//-/_}"
        
        # Replace the module name
        new_line="${line//$module/$new_module}"
        log_info "$new_line" >> "$temp_file"
      else
        # Keep the line as is
        log_info "$line" >> "$temp_file"
      fi
    done < "$file"
    
    # Replace the original file with the modified one
    mv "$temp_file" "$file"
    log_info "${GREEN}Updated imports in $filename${NC}"
  fi
done

# Update setup.py if it exists
SETUP_PY="./setup.py"
if [ -f "$SETUP_PY" ]; then
  log_info "${YELLOW}Updating module references in setup.py...${NC}"
  temp_file=$(mktemp)
  
  while IFS= read -r line; do
    # Replace any references to n8n-setup-*.py with n8n_setup_*.py
    new_line="${line//n8n-setup/n8n_setup}"
    log_info "$new_line" >> "$temp_file"
  done < "$SETUP_PY"
  
  # Replace the original file with the modified one
  mv "$temp_file" "$SETUP_PY"
  log_info "${GREEN}Updated module references in setup.py${NC}"
fi

# Update docker-start.sh if it exists
DOCKER_START="./docker-start.sh"
if [ -f "$DOCKER_START" ]; then
  log_info "${YELLOW}Updating references in docker-start.sh...${NC}"
  temp_file=$(mktemp)
  
  while IFS= read -r line; do
    # Replace references to Python script names
    new_line="${line//n8n-setup/n8n_setup}"
    new_line="${new_line//n8n-mcp/n8n_mcp}"
    log_info "$new_line" >> "$temp_file"
  done < "$DOCKER_START"
  
  # Replace the original file with the modified one
  mv "$temp_file" "$DOCKER_START"
  chmod +x "$DOCKER_START"
  log_info "${GREEN}Updated references in docker-start.sh${NC}"
fi

# Update docker compose.yml if it exists
DOCKER_COMPOSE="./docker-compose.yml"
if [ -f "$DOCKER_COMPOSE" ]; then
  log_info "${YELLOW}Updating references in docker compose.yml...${NC}"
  temp_file=$(mktemp)
  
  while IFS= read -r line; do
    # Replace references to Python script names
    new_line="${line//n8n-setup/n8n_setup}"
    new_line="${new_line//n8n-mcp/n8n_mcp}"
    log_info "$new_line" >> "$temp_file"
  done < "$DOCKER_COMPOSE"
  
  # Replace the original file with the modified one
  mv "$temp_file" "$DOCKER_COMPOSE"
  log_info "${GREEN}Updated references in docker compose.yml${NC}"
fi

log_info "\n${GREEN}Fix complete. Please try running the setup again:${NC}"
log_info "${YELLOW}./docker-start.sh setup${NC}"
