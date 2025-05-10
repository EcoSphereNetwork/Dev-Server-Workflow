#!/bin/bash

# Script to verify the repository structure
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Function to check if a directory exists and has expected content
check_directory() {
    local dir=$1
    local expected_files=$2
    
    if [ ! -d "$dir" ]; then
        echo "❌ Directory $dir does not exist"
        return 1
    fi
    
    local file_count=$(find "$dir" -type f | wc -l)
    if [ "$file_count" -lt "$expected_files" ]; then
        echo "⚠️ Directory $dir exists but has fewer files than expected ($file_count < $expected_files)"
        return 2
    else
        echo "✅ Directory $dir exists with $file_count files"
        return 0
    fi
}

# Function to check for import errors in files
check_imports() {
    local pattern=$1
    local file_types=$2
    
    echo "Checking for import errors in $file_types files..."
    
    # Exclude lines with "except ImportError" as these are handling import errors properly
    local errors=$(grep -r "$pattern" --include="$file_types" . | grep -v "except ImportError" | wc -l)
    if [ "$errors" -gt 0 ]; then
        echo "❌ Found $errors import errors in $file_types files"
        grep -r "$pattern" --include="$file_types" . | grep -v "except ImportError" | head -n 10
        if [ "$errors" -gt 10 ]; then
            echo "... and $(($errors - 10)) more errors"
        fi
        return 1
    else
        echo "✅ No import errors found in $file_types files"
        return 0
    fi
}

# Display welcome message
section "Repository Structure Verification"
echo "This script will verify the structure of the Dev-Server-Workflow repository."
echo ""

# Check MCP server consolidation
section "Verifying MCP Server Consolidation"
check_directory "src/mcp_servers/base" 1
check_directory "src/mcp_servers/docker_mcp" 5
check_directory "src/mcp_servers/n8n_mcp_server" 5
check_directory "src/mcp_servers/prompt_mcp_server" 5
check_directory "src/mcp_servers/llm_cost_analyzer_mcp" 5
check_directory "src/mcp_servers/openhands" 1

# Check Docker configuration consolidation
section "Verifying Docker Configuration Consolidation"
check_directory "docker/base" 1
check_directory "docker/monitoring" 1
check_directory "docker/ecosystem" 1
check_directory "docker/servers" 1

# Check workflow file consolidation
section "Verifying Workflow File Consolidation"
check_directory "src/workflows/n8n/integrations" 1
check_directory "src/workflows/n8n/triggers" 1
check_directory "src/workflows/n8n/mcp" 1
check_directory "src/workflows/n8n/openhands" 1
check_directory "src/workflows/n8n/utilities" 1
check_directory "src/workflows/n8n/llm" 1

# Check CLI script consolidation
section "Verifying CLI Script Consolidation"
check_directory "cli/core" 1
check_directory "cli/config" 1
check_directory "cli/install" 1
check_directory "cli/service" 1
check_directory "cli/monitoring" 1
check_directory "cli/ai" 1

# Check for import errors
section "Checking for Import Errors"
check_imports "ImportError\|ModuleNotFoundError" "*.py"
check_imports "Cannot find module" "*.js"
check_imports "Cannot find module" "*.tsx"

# Check for production configuration
section "Checking Production Configuration"
if [ -f "docker-compose.production.yml" ]; then
    echo "✅ Production Docker Compose file exists"
else
    echo "❌ Production Docker Compose file does not exist"
fi

if [ -f ".env.production" ]; then
    echo "✅ Production environment file exists"
else
    echo "❌ Production environment file does not exist"
fi

# Final message
section "Structure Verification Complete"
echo "The structure verification is now complete."
echo "Please review the results above to ensure the repository structure is correct."
echo ""
echo "Thank you for using the Repository Structure Verification script."