#!/bin/bash

# Script to verify the cleanup process
# Created as part of the Dev-Server-Workflow repository cleanup project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Function to check if a directory exists
check_directory() {
    if [ -d "$1" ]; then
        echo "✅ Directory $1 exists"
    else
        echo "❌ Directory $1 does not exist"
    fi
}

# Function to check if a file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✅ File $1 exists"
    else
        echo "❌ File $1 does not exist"
    fi
}

# Function to count files with a specific pattern
count_files() {
    count=$(find . -name "$1" | wc -l)
    echo "Found $count files matching pattern $1"
    if [ "$count" -eq 0 ]; then
        echo "✅ No files found with pattern $1"
    else
        echo "❌ $count files found with pattern $1"
    fi
}

# Display welcome message
section "Dev-Server-Workflow Repository Cleanup Verification"
echo "This script will verify the cleanup process for the Dev-Server-Workflow repository."
echo ""

# Verify backup file cleanup
section "Verifying Backup File Cleanup"
count_files "*.bak.20250509124941"
echo ""

# Verify MCP server consolidation
section "Verifying MCP Server Consolidation"
check_directory "src/mcp_servers/base"
check_directory "src/mcp_servers/docker"
check_directory "src/mcp_servers/n8n"
check_directory "src/mcp_servers/openhands"
check_directory "src/mcp_servers/prompt"
check_directory "src/mcp_servers/llm_cost"
check_directory "legacy/archive/mcp"
echo ""

# Verify Docker configuration consolidation
section "Verifying Docker Configuration Consolidation"
check_directory "docker/base"
check_directory "docker/monitoring"
check_directory "docker/ecosystem"
check_directory "docker/servers"
check_directory "legacy/archive/docker"
echo ""

# Verify workflow file consolidation
section "Verifying Workflow File Consolidation"
check_directory "src/workflows/n8n/integrations"
check_directory "src/workflows/n8n/triggers"
check_directory "src/workflows/n8n/mcp"
check_directory "src/workflows/n8n/openhands"
check_directory "src/workflows/n8n/utilities"
check_directory "src/workflows/n8n/llm"
check_directory "legacy/archive/workflows"
echo ""

# Verify CLI script consolidation
section "Verifying CLI Script Consolidation"
check_directory "cli/core"
check_directory "cli/config"
check_directory "cli/install"
check_directory "cli/service"
check_directory "cli/monitoring"
check_directory "cli/ai"
check_directory "legacy/archive/cli"
echo ""

# Verify documentation consolidation
section "Verifying Documentation Consolidation"
check_file "docs/architecture/README.md"
check_file "docs/development/README.md"
check_file "docs/deployment/README.md"
check_file "docs/api/README.md"
check_file "docs/user/README.md"
echo ""

# Final message
section "Cleanup Verification Complete"
echo "The cleanup verification is now complete."
echo "Please review the results above to ensure the cleanup process was successful."
echo ""
echo "Thank you for using the Dev-Server-Workflow Repository Cleanup Verification script."