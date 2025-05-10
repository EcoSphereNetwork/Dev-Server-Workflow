#!/bin/bash

# Script to fix Python imports after repository reorganization
# Created as part of the Dev-Server-Workflow repository cleanup project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Display welcome message
section "Python Import Fixer"
echo "This script will fix Python imports after the repository reorganization."
echo ""

# Create a mapping of old to new import paths
section "Creating Import Mapping"
echo "Creating a mapping of old to new import paths..."

# Create a temporary file to store the mapping
mapping_file=$(mktemp)

# Add mappings for MCP server imports
echo "Adding mappings for MCP server imports..."
echo "src.mcp.base.base_mcp_server -> src.mcp_servers.base.base_mcp_server" >> $mapping_file
echo "src.mcp.interfaces.mcp_server_interface -> src.mcp_servers.base.mcp_server_interface" >> $mapping_file
echo "src.mcp.interfaces.mcp_tool -> src.mcp_servers.base.mcp_tool" >> $mapping_file
echo "src.mcp.servers.docker.docker_mcp_server -> src.mcp_servers.docker.docker_mcp_server" >> $mapping_file
echo "src.mcp.servers.n8n.n8n_mcp_server -> src.mcp_servers.n8n.n8n_mcp_server" >> $mapping_file
echo "src.mcp.servers.openhands.openhands_mcp_server -> src.mcp_servers.openhands.openhands_mcp_server" >> $mapping_file
echo "src.mcp.base_mcp_server_improved -> src.mcp_servers.base.base_mcp_server_improved" >> $mapping_file
echo "src.mcp.docker_mcp_server_improved -> src.mcp_servers.docker.docker_mcp_server_improved" >> $mapping_file
echo "src.mcp.n8n_mcp_server_improved -> src.mcp_servers.n8n.n8n_mcp_server_improved" >> $mapping_file
echo "src.mcp.openhands_server_improved -> src.mcp_servers.openhands.openhands_mcp_server_improved" >> $mapping_file

# Add mappings for workflow imports
echo "Adding mappings for workflow imports..."
echo "src.n8n-workflows -> src.workflows.n8n" >> $mapping_file

# Add mappings for CLI imports
echo "Adding mappings for CLI imports..."
echo "cli.config -> cli.config.config" >> $mapping_file
echo "cli.functions -> cli.core.functions" >> $mapping_file
echo "cli.menu -> cli.core.menu" >> $mapping_file
echo "cli.interactive_ui -> cli.core.interactive_ui" >> $mapping_file
echo "cli.ai_assistant -> cli.ai.ai_assistant" >> $mapping_file
echo "cli.ai_command -> cli.ai.ai_command" >> $mapping_file
echo "cli.error_handler -> cli.core.error_handler" >> $mapping_file
echo "cli.install -> cli.install.install" >> $mapping_file
echo "cli.install_components -> cli.install.install_components" >> $mapping_file
echo "cli.monitoring -> cli.monitoring.monitoring" >> $mapping_file
echo "cli.monitoring_management -> cli.monitoring.monitoring_management" >> $mapping_file
echo "cli.package_management -> cli.install.package_management" >> $mapping_file
echo "cli.start-web-ui -> cli.service.start_web_ui" >> $mapping_file
echo "cli.stop-web-ui -> cli.service.stop_web_ui" >> $mapping_file

echo "Mapping file created with $(wc -l < $mapping_file) entries."
echo ""

# Find all Python files
section "Finding Python Files"
echo "Finding all Python files in the repository..."
python_files=$(find . -name "*.py" -not -path "*/\.*" -not -path "*/legacy/*" -not -path "*/node_modules/*")
echo "Found $(echo "$python_files" | wc -l) Python files."
echo ""

# Process each Python file
section "Processing Python Files"
echo "Processing Python files to fix imports..."

for file in $python_files; do
    echo "Processing $file..."
    
    # Create a temporary file
    temp_file=$(mktemp)
    
    # Copy the original file to the temporary file
    cp "$file" "$temp_file"
    
    # Process each mapping
    while IFS= read -r mapping; do
        old_import=$(echo "$mapping" | cut -d' ' -f1)
        new_import=$(echo "$mapping" | cut -d' ' -f3)
        
        # Replace imports
        sed -i "s/from $old_import/from $new_import/g" "$temp_file"
        sed -i "s/import $old_import/import $new_import/g" "$temp_file"
    done < "$mapping_file"
    
    # Check if the file has changed
    if ! cmp -s "$file" "$temp_file"; then
        echo "  Imports updated in $file"
        cp "$temp_file" "$file"
    else
        echo "  No changes needed in $file"
    fi
    
    # Remove the temporary file
    rm "$temp_file"
done

# Remove the mapping file
rm "$mapping_file"

echo ""
section "Import Fixing Complete"
echo "The import fixing process is now complete."
echo "Please review the changes and test the code to ensure everything works correctly."
echo ""
echo "Thank you for using the Python Import Fixer script."
