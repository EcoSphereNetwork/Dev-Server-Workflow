#!/bin/bash

# Script to test the Electron AppImage
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Function to check if a process is running
check_process() {
    local process_name=$1
    
    if pgrep -f "$process_name" > /dev/null; then
        echo "✅ Process $process_name is running"
        return 0
    else
        echo "❌ Process $process_name is not running"
        return 1
    fi
}

# Display welcome message
section "Electron AppImage Test"
echo "This script will test the Electron AppImage of the Dev-Server-Workflow application."
echo ""

# Check if the AppImage exists
section "Checking AppImage"
if [ ! -f "frontend/dist/Dev-Server-Workflow-*.AppImage" ]; then
    echo "❌ Electron AppImage does not exist"
    echo "Please build the Electron AppImage and try again."
    exit 1
else
    APPIMAGE_PATH=$(find frontend/dist -name "Dev-Server-Workflow-*.AppImage" | head -n 1)
    echo "✅ Electron AppImage exists at $APPIMAGE_PATH"
fi

# Make the AppImage executable
chmod +x "$APPIMAGE_PATH"

# Start the AppImage
section "Starting AppImage"
echo "Starting Electron AppImage..."

# Run the AppImage in the background with a virtual display
if command -v xvfb-run > /dev/null 2>&1; then
    echo "Using Xvfb for virtual display..."
    xvfb-run "$APPIMAGE_PATH" &
    APP_PID=$!
else
    echo "Xvfb not found, attempting to run directly..."
    "$APPIMAGE_PATH" &
    APP_PID=$!
fi

# Wait for the AppImage to start
sleep 5

# Check if the AppImage process is running
if ! check_process "Dev-Server-Workflow"; then
    echo "❌ Electron AppImage failed to start"
    exit 1
fi

echo "Electron AppImage started with PID $APP_PID."
echo ""

# Test functionality
section "Testing Functionality"
echo "Testing functionality..."

# Since we can't directly interact with the Electron app in a headless environment,
# we'll check if it's still running after a few seconds
sleep 5

if check_process "Dev-Server-Workflow"; then
    echo "✅ Electron AppImage is still running after 5 seconds"
else
    echo "❌ Electron AppImage crashed or exited prematurely"
    exit 1
fi

# Check if the app created any log files
if [ -d "$HOME/.config/Dev-Server-Workflow/logs" ]; then
    echo "✅ Log directory exists"
    
    # Check for error logs
    if grep -r "error\|exception\|fail" "$HOME/.config/Dev-Server-Workflow/logs"; then
        echo "⚠️ Found errors in logs"
    else
        echo "✅ No errors found in logs"
    fi
else
    echo "⚠️ Log directory not found"
fi

echo ""

# Stop the AppImage
section "Stopping AppImage"
echo "Stopping Electron AppImage..."

# Kill the AppImage process
kill $APP_PID

# Wait for the process to terminate
sleep 2

# Check if the process is still running
if check_process "Dev-Server-Workflow"; then
    echo "⚠️ Electron AppImage process is still running, forcing termination..."
    kill -9 $APP_PID
    sleep 1
    
    if check_process "Dev-Server-Workflow"; then
        echo "❌ Failed to terminate Electron AppImage process"
    else
        echo "✅ Electron AppImage process terminated"
    fi
else
    echo "✅ Electron AppImage process terminated"
fi

echo ""

# Final message
section "Electron AppImage Test Complete"
echo "The Electron AppImage test is now complete."
echo "Please review the results above to ensure the Electron AppImage is working correctly."
echo ""
echo "Thank you for using the Electron AppImage Test script."