#!/bin/bash

# Script to build an AppImage for the web app
# Created as part of the Dev-Server-Workflow repository cleanup project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Display welcome message
section "Web App AppImage Builder"
echo "This script will build an AppImage for the Dev-Server-Workflow web app."
echo ""

# Check if required tools are installed
section "Checking Required Tools"

# Check for appimagetool
if ! command -v appimagetool &> /dev/null; then
    echo "appimagetool is not installed. Installing..."
    
    # Create a temporary directory
    temp_dir=$(mktemp -d)
    
    # Download appimagetool
    wget -O "$temp_dir/appimagetool" "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    
    # Make it executable
    chmod +x "$temp_dir/appimagetool"
    
    # Move it to a directory in PATH
    sudo mv "$temp_dir/appimagetool" /usr/local/bin/
    
    # Remove the temporary directory
    rm -rf "$temp_dir"
    
    echo "appimagetool installed."
else
    echo "appimagetool is already installed."
fi

echo ""

# Build the web app
section "Building Web App"
echo "Building the web app..."

# Navigate to the frontend directory
cd frontend

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the app
echo "Building the app..."
npm run build

# Navigate back to the root directory
cd ..

echo "Web app built successfully."
echo ""

# Create AppDir structure
section "Creating AppDir Structure"
echo "Creating AppDir structure..."

# Create AppDir directory
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p AppDir/usr/share/metainfo

# Copy the built web app
echo "Copying web app files..."
cp -r frontend/build/* AppDir/usr/bin/

# Create desktop file
echo "Creating desktop file..."
cat > AppDir/usr/share/applications/dev-server-workflow.desktop << EOF
[Desktop Entry]
Name=Dev-Server-Workflow
Comment=Eine umfassende Loesung zur Integration von n8n-Workflows, MCP-Servern und OpenHands
Exec=dev-server-workflow
Icon=dev-server-workflow
Type=Application
Categories=Development;Utility;
EOF

# Copy icon
echo "Copying icon..."
cp frontend/assets/icon.png AppDir/usr/share/icons/hicolor/256x256/apps/dev-server-workflow.png

# Create AppStream metadata
echo "Creating AppStream metadata..."
cat > AppDir/usr/share/metainfo/dev-server-workflow.appdata.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>dev-server-workflow</id>
  <name>Dev-Server-Workflow</name>
  <summary>Eine umfassende Loesung zur Integration von n8n-Workflows, MCP-Servern und OpenHands</summary>
  <description>
    <p>
      Eine umfassende Loesung zur Integration von n8n-Workflows, MCP-Servern und OpenHands fuer die KI-gestuetzte Automatisierung von Entwicklungsprozessen.
    </p>
  </description>
  <categories>
    <category>Development</category>
    <category>Utility</category>
  </categories>
  <url type="homepage">https://github.com/EcoSphereNetwork/Dev-Server-Workflow</url>
  <provides>
    <binary>dev-server-workflow</binary>
  </provides>
  <releases>
    <release version="1.0.0" date="2025-05-10" />
  </releases>
</component>
EOF

# Create AppRun script
echo "Creating AppRun script..."
cat > AppDir/AppRun << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
exec usr/bin/index.html
EOF

# Make AppRun executable
chmod +x AppDir/AppRun

echo "AppDir structure created successfully."
echo ""

# Build AppImage
section "Building AppImage"
echo "Building AppImage..."

# Build the AppImage
ARCH=x86_64 appimagetool AppDir

# Rename the AppImage
mv Dev-Server-Workflow-x86_64.AppImage Dev-Server-Workflow-Web-x86_64.AppImage

echo "AppImage built successfully: Dev-Server-Workflow-Web-x86_64.AppImage"
echo ""

# Clean up
section "Cleaning Up"
echo "Cleaning up temporary files..."

# Remove AppDir
rm -rf AppDir

echo "Cleanup complete."
echo ""

section "Web App AppImage Build Complete"
echo "The Web App AppImage build is now complete."
echo "The AppImage is available at: Dev-Server-Workflow-Web-x86_64.AppImage"
echo ""
echo "Thank you for using the Web App AppImage Builder script."