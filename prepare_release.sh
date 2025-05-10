#!/bin/bash

# Script to prepare a release
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Function to prompt for confirmation
confirm() {
    local prompt=$1
    local default=$2
    
    if [ "$default" = "Y" ]; then
        prompt="$prompt [Y/n]"
    else
        prompt="$prompt [y/N]"
    fi
    
    read -p "$prompt " response
    
    if [ -z "$response" ]; then
        response=$default
    fi
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Display welcome message
section "Release Preparation"
echo "This script will prepare a release of the Dev-Server-Workflow application."
echo ""

# Get release version
section "Release Version"
echo "Please enter the release version (e.g., 1.0.0):"
read VERSION

if [ -z "$VERSION" ]; then
    echo "❌ Release version cannot be empty"
    exit 1
fi

echo "Release version: $VERSION"
echo ""

# Create release directory
section "Creating Release Directory"
echo "Creating release directory..."

RELEASE_DIR="releases/v$VERSION"
mkdir -p "$RELEASE_DIR"

echo "Release directory created at $RELEASE_DIR."
echo ""

# Run tests
section "Running Tests"
echo "Running tests..."

if confirm "Do you want to run tests before preparing the release?" "Y"; then
    ./run_tests.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Tests failed"
        if ! confirm "Tests failed. Do you want to continue anyway?" "N"; then
            exit 1
        fi
    else
        echo "✅ Tests passed"
    fi
else
    echo "Skipping tests."
fi

echo ""

# Build Docker images
section "Building Docker Images"
echo "Building Docker images..."

if confirm "Do you want to build Docker images?" "Y"; then
    docker-compose -f docker-compose.production.yml build
    
    if [ $? -ne 0 ]; then
        echo "❌ Docker image build failed"
        if ! confirm "Docker image build failed. Do you want to continue anyway?" "N"; then
            exit 1
        fi
    else
        echo "✅ Docker images built successfully"
        
        # Tag Docker images
        echo "Tagging Docker images..."
        docker tag dev-server-workflow/mcp-hub:latest dev-server-workflow/mcp-hub:v$VERSION
        docker tag dev-server-workflow/docker-mcp:latest dev-server-workflow/docker-mcp:v$VERSION
        docker tag dev-server-workflow/n8n-mcp:latest dev-server-workflow/n8n-mcp:v$VERSION
        docker tag dev-server-workflow/prompt-mcp:latest dev-server-workflow/prompt-mcp:v$VERSION
        docker tag dev-server-workflow/llm-cost-analyzer-mcp:latest dev-server-workflow/llm-cost-analyzer-mcp:v$VERSION
        docker tag dev-server-workflow/openhands-mcp:latest dev-server-workflow/openhands-mcp:v$VERSION
        docker tag dev-server-workflow/nginx:latest dev-server-workflow/nginx:v$VERSION
        
        echo "Docker images tagged with version v$VERSION."
    fi
else
    echo "Skipping Docker image build."
fi

echo ""

# Build Web AppImage
section "Building Web AppImage"
echo "Building Web AppImage..."

if confirm "Do you want to build the Web AppImage?" "Y"; then
    ./build-web-appimage.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Web AppImage build failed"
        if ! confirm "Web AppImage build failed. Do you want to continue anyway?" "N"; then
            exit 1
        fi
    else
        echo "✅ Web AppImage built successfully"
        
        # Copy Web AppImage to release directory
        echo "Copying Web AppImage to release directory..."
        cp Dev-Server-Workflow-Web-x86_64.AppImage "$RELEASE_DIR/"
        
        echo "Web AppImage copied to release directory."
    fi
else
    echo "Skipping Web AppImage build."
fi

echo ""

# Build Electron AppImage
section "Building Electron AppImage"
echo "Building Electron AppImage..."

if confirm "Do you want to build the Electron AppImage?" "Y"; then
    cd frontend && npm run electron:build && cd ..
    
    if [ $? -ne 0 ]; then
        echo "❌ Electron AppImage build failed"
        if ! confirm "Electron AppImage build failed. Do you want to continue anyway?" "N"; then
            exit 1
        fi
    else
        echo "✅ Electron AppImage built successfully"
        
        # Copy Electron AppImage to release directory
        echo "Copying Electron AppImage to release directory..."
        cp frontend/dist/Dev-Server-Workflow-*.AppImage "$RELEASE_DIR/"
        
        echo "Electron AppImage copied to release directory."
    fi
else
    echo "Skipping Electron AppImage build."
fi

echo ""

# Copy configuration files
section "Copying Configuration Files"
echo "Copying configuration files..."

# Copy Docker Compose file
cp docker-compose.production.yml "$RELEASE_DIR/docker-compose.yml"

# Copy environment file template
cp .env.production "$RELEASE_DIR/.env.template"

# Copy README
cp README.md "$RELEASE_DIR/"

echo "Configuration files copied to release directory."
echo ""

# Create release notes
section "Creating Release Notes"
echo "Creating release notes..."

# Create release notes file
cat > "$RELEASE_DIR/RELEASE_NOTES.md" << EOF
# Dev-Server-Workflow v$VERSION Release Notes

## Overview
This release includes improvements to the Dev-Server-Workflow application, focusing on production readiness, stability, and performance.

## New Features
- Comprehensive error handling
- Structured logging
- Health monitoring
- Production Docker configuration
- Web and Electron AppImage packages

## Improvements
- Consolidated MCP server implementations
- Consolidated Docker configurations
- Consolidated workflow files
- Enhanced test coverage
- Improved documentation

## Known Issues
- None

## Installation Instructions
Please refer to the README.md file for installation instructions.

## Upgrade Instructions
If you are upgrading from a previous version, please follow these steps:
1. Back up your data
2. Stop the running application
3. Replace the application files with the new version
4. Update the configuration files
5. Start the application

## Support
For support, please contact the development team.
EOF

echo "Release notes created at $RELEASE_DIR/RELEASE_NOTES.md."
echo ""

# Create checksums
section "Creating Checksums"
echo "Creating checksums..."

cd "$RELEASE_DIR"
sha256sum * > checksums.sha256
cd ../..

echo "Checksums created at $RELEASE_DIR/checksums.sha256."
echo ""

# Final message
section "Release Preparation Complete"
echo "The release preparation is now complete."
echo "Release artifacts are available in the $RELEASE_DIR directory."
echo ""
echo "Next steps:"
echo "1. Review the release artifacts"
echo "2. Test the release artifacts"
echo "3. Publish the release"
echo ""
echo "Thank you for using the Release Preparation script."