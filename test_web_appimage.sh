#!/bin/bash

# Script to test the Web AppImage
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

# Function to test a URL
test_url() {
    local url=$1
    local expected_status=$2
    local max_attempts=$3
    local attempt=1
    
    echo "Testing URL $url..."
    
    while [ $attempt -le $max_attempts ]; do
        status_code=$(curl -s -o /dev/null -w "%{http_code}" $url)
        
        if [ "$status_code" -eq "$expected_status" ]; then
            echo "✅ URL $url returned expected status code $expected_status"
            return 0
        else
            echo "⏳ URL $url returned status code $status_code, expected $expected_status (attempt $attempt/$max_attempts)..."
            sleep 2
            attempt=$((attempt + 1))
        fi
    done
    
    echo "❌ URL $url failed to return expected status code $expected_status after $max_attempts attempts"
    return 1
}

# Display welcome message
section "Web AppImage Test"
echo "This script will test the Web AppImage of the Dev-Server-Workflow application."
echo ""

# Check if the AppImage exists
section "Checking AppImage"
if [ ! -f "Dev-Server-Workflow-Web-x86_64.AppImage" ]; then
    echo "❌ Web AppImage does not exist"
    echo "Please build the Web AppImage and try again."
    exit 1
else
    echo "✅ Web AppImage exists"
fi

# Make the AppImage executable
chmod +x Dev-Server-Workflow-Web-x86_64.AppImage

# Start the AppImage
section "Starting AppImage"
echo "Starting Web AppImage..."

# Run the AppImage in the background
./Dev-Server-Workflow-Web-x86_64.AppImage &
APP_PID=$!

# Wait for the AppImage to start
sleep 5

# Check if the AppImage process is running
if ! check_process "Dev-Server-Workflow-Web"; then
    echo "❌ Web AppImage failed to start"
    exit 1
fi

echo "Web AppImage started with PID $APP_PID."
echo ""

# Test the web server
section "Testing Web Server"
echo "Testing web server..."

# Test the home page
test_url "http://localhost:8080" 200 10

# Test the API endpoint
test_url "http://localhost:8080/api/health" 200 10

echo ""

# Test functionality
section "Testing Functionality"
echo "Testing functionality..."

# Test the login page
test_url "http://localhost:8080/login" 200 5

# Test the dashboard page
test_url "http://localhost:8080/dashboard" 200 5

# Test the services page
test_url "http://localhost:8080/services" 200 5

echo ""

# Stop the AppImage
section "Stopping AppImage"
echo "Stopping Web AppImage..."

# Kill the AppImage process
kill $APP_PID

# Wait for the process to terminate
sleep 2

# Check if the process is still running
if check_process "Dev-Server-Workflow-Web"; then
    echo "⚠️ Web AppImage process is still running, forcing termination..."
    kill -9 $APP_PID
    sleep 1
    
    if check_process "Dev-Server-Workflow-Web"; then
        echo "❌ Failed to terminate Web AppImage process"
    else
        echo "✅ Web AppImage process terminated"
    fi
else
    echo "✅ Web AppImage process terminated"
fi

echo ""

# Final message
section "Web AppImage Test Complete"
echo "The Web AppImage test is now complete."
echo "Please review the results above to ensure the Web AppImage is working correctly."
echo ""
echo "Thank you for using the Web AppImage Test script."