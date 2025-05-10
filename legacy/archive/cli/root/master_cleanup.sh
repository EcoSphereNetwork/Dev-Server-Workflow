#!/bin/bash

# Master script to orchestrate the entire cleanup process
# Created as part of the Dev-Server-Workflow repository cleanup project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Function to prompt for confirmation
confirm() {
    read -p "$1 (y/n): " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Display welcome message
section "Dev-Server-Workflow Repository Cleanup"
echo "This script will guide you through the cleanup process for the Dev-Server-Workflow repository."
echo "The process is divided into several phases, and you will be prompted for confirmation before each phase."
echo ""

# Phase 1: Backup File Cleanup
section "Phase 1: Backup File Cleanup"
echo "This phase will remove all .bak.20250509124941 backup files from the repository."
echo ""

if confirm "Do you want to proceed with backup file cleanup?"; then
    echo "Executing backup file cleanup script..."
    ./cleanup_backup_files.sh
else
    echo "Skipping backup file cleanup."
fi

echo ""

# Phase 2: MCP Server Consolidation
section "Phase 2: MCP Server Consolidation"
echo "This phase will consolidate MCP server implementations."
echo ""

if confirm "Do you want to proceed with MCP server consolidation preparation?"; then
    echo "Executing MCP server consolidation preparation script..."
    ./scripts/consolidate_mcp_servers.sh
else
    echo "Skipping MCP server consolidation preparation."
fi

echo ""

# Phase 3: Docker Configuration Consolidation
section "Phase 3: Docker Configuration Consolidation"
echo "This phase will consolidate Docker configurations."
echo ""

if confirm "Do you want to proceed with Docker configuration consolidation preparation?"; then
    echo "Executing Docker configuration consolidation preparation script..."
    ./scripts/consolidate_docker_configs.sh
else
    echo "Skipping Docker configuration consolidation preparation."
fi

echo ""

# Phase 4: Workflow File Consolidation
section "Phase 4: Workflow File Consolidation"
echo "This phase will consolidate workflow files."
echo ""

if confirm "Do you want to proceed with workflow file consolidation preparation?"; then
    echo "Executing workflow file consolidation preparation script..."
    ./scripts/consolidate_workflows.sh
else
    echo "Skipping workflow file consolidation preparation."
fi

echo ""

# Phase 5: CLI Script Consolidation
section "Phase 5: CLI Script Consolidation"
echo "This phase will consolidate CLI scripts."
echo ""

if confirm "Do you want to proceed with CLI script consolidation preparation?"; then
    echo "Executing CLI script consolidation preparation script..."
    ./scripts/consolidate_cli_scripts.sh
else
    echo "Skipping CLI script consolidation preparation."
fi

echo ""

# Final message
section "Cleanup Process Preparation Complete"
echo "The cleanup process preparation is now complete."
echo "Please refer to the implementation plan for the next steps in each phase."
echo "The implementation plan can be found at: docs/implementation_plan.md"
echo ""
echo "Thank you for using the Dev-Server-Workflow Repository Cleanup script."