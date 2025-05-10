#!/bin/bash

# Script to verify the OpenHands Issue Resolver configuration
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Function to check if a file exists
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo "✅ $description exists at $file"
        return 0
    else
        echo "❌ $description does not exist at $file"
        return 1
    fi
}

# Function to check if a directory exists
check_directory() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo "✅ $description exists at $dir"
        return 0
    else
        echo "❌ $description does not exist at $dir"
        return 1
    fi
}

# Display welcome message
section "OpenHands Issue Resolver Configuration Verification"
echo "This script will verify the OpenHands Issue Resolver configuration."
echo ""

# Check GitHub workflow file
section "Checking GitHub Workflow Configuration"
check_file ".github/workflows/openhands-resolver.yml" "GitHub workflow file"

# Check GitLab CI/CD configuration
section "Checking GitLab CI/CD Configuration"
check_file ".gitlab-ci.yml" "GitLab CI/CD configuration file"

# Check OpenHands microagent directory
section "Checking OpenHands Microagent Configuration"
check_directory ".openhands/microagents" "OpenHands microagent directory"
check_file ".openhands/microagents/repo.md" "Repository microagent file"

# Check documentation
section "Checking Documentation"
check_file "OPENHANDS_RESOLVER.md" "OpenHands Resolver documentation"

# Check README reference
section "Checking README Reference"
if grep -q "OpenHands Issue Resolver" README.md; then
    echo "✅ README contains reference to OpenHands Issue Resolver"
else
    echo "❌ README does not contain reference to OpenHands Issue Resolver"
fi

# Final message
section "Configuration Verification Complete"
echo "The OpenHands Issue Resolver configuration verification is now complete."
echo "Please review the results above to ensure the configuration is correct."
echo ""
echo "Next steps:"
echo "1. Set up the required secrets in GitHub or GitLab"
echo "2. Configure repository permissions for GitHub Actions"
echo "3. Test the configuration by creating an issue with the 'fix-me' label"
echo ""
echo "Thank you for using the OpenHands Issue Resolver Configuration Verification script."