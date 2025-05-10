#!/bin/bash

# Script to test the Docker deployment
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Function to check if a service is healthy
check_service() {
    local service=$1
    local max_attempts=$2
    local attempt=1
    
    echo "Checking health of $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.production.yml ps $service | grep -q "Up"; then
            echo "✅ Service $service is up"
            
            # Check health status if available
            if docker-compose -f docker-compose.production.yml ps $service | grep -q "(healthy)"; then
                echo "✅ Service $service is healthy"
                return 0
            elif docker-compose -f docker-compose.production.yml ps $service | grep -q "(unhealthy)"; then
                echo "❌ Service $service is unhealthy"
                return 1
            else
                echo "⚠️ Service $service health status is unknown"
                return 0
            fi
        else
            echo "⏳ Waiting for service $service to start (attempt $attempt/$max_attempts)..."
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    echo "❌ Service $service failed to start after $max_attempts attempts"
    return 1
}

# Function to test a service endpoint
test_endpoint() {
    local service=$1
    local endpoint=$2
    local expected_status=$3
    local max_attempts=$4
    local attempt=1
    
    echo "Testing endpoint $endpoint for service $service..."
    
    while [ $attempt -le $max_attempts ]; do
        status_code=$(curl -s -o /dev/null -w "%{http_code}" $endpoint)
        
        if [ "$status_code" -eq "$expected_status" ]; then
            echo "✅ Endpoint $endpoint returned expected status code $expected_status"
            return 0
        else
            echo "⏳ Endpoint $endpoint returned status code $status_code, expected $expected_status (attempt $attempt/$max_attempts)..."
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    echo "❌ Endpoint $endpoint failed to return expected status code $expected_status after $max_attempts attempts"
    return 1
}

# Display welcome message
section "Docker Deployment Test"
echo "This script will test the Docker deployment of the Dev-Server-Workflow application."
echo ""

# Check if Docker is running
section "Checking Docker"
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    echo "Please start Docker and try again."
    exit 1
else
    echo "✅ Docker is running"
fi

# Check if docker-compose is installed
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose is not installed"
    echo "Please install docker-compose and try again."
    exit 1
else
    echo "✅ docker-compose is installed"
fi

# Check if production Docker Compose file exists
if [ ! -f "docker-compose.production.yml" ]; then
    echo "❌ Production Docker Compose file does not exist"
    echo "Please create docker-compose.production.yml and try again."
    exit 1
else
    echo "✅ Production Docker Compose file exists"
fi

# Start the Docker deployment
section "Starting Docker Deployment"
echo "Starting Docker deployment..."

docker-compose -f docker-compose.production.yml up -d

echo "Docker deployment started."
echo ""

# Wait for services to start
section "Waiting for Services"
echo "Waiting for services to start..."

# Check core services
check_service "mcp-hub" 12
check_service "docker-mcp" 12
check_service "n8n-mcp" 12
check_service "prompt-mcp" 12
check_service "llm-cost-analyzer-mcp" 12
check_service "openhands-mcp" 12
check_service "n8n" 12
check_service "nginx" 12

echo ""

# Test service endpoints
section "Testing Service Endpoints"
echo "Testing service endpoints..."

# Test MCP Hub endpoint
test_endpoint "mcp-hub" "http://localhost:3000/health" 200 12

# Test Docker MCP endpoint
test_endpoint "docker-mcp" "http://localhost:3001/health" 200 12

# Test n8n MCP endpoint
test_endpoint "n8n-mcp" "http://localhost:3002/health" 200 12

# Test Prompt MCP endpoint
test_endpoint "prompt-mcp" "http://localhost:3003/health" 200 12

# Test LLM Cost Analyzer MCP endpoint
test_endpoint "llm-cost-analyzer-mcp" "http://localhost:3004/health" 200 12

# Test OpenHands MCP endpoint
test_endpoint "openhands-mcp" "http://localhost:3005/health" 200 12

# Test n8n endpoint
test_endpoint "n8n" "http://localhost:5678/healthz" 200 12

# Test Nginx endpoint
test_endpoint "nginx" "http://localhost:80/health" 200 12

echo ""

# Test integration
section "Testing Integration"
echo "Testing integration between services..."

# Test MCP Hub to Docker MCP integration
echo "Testing MCP Hub to Docker MCP integration..."
response=$(curl -s -X POST "http://localhost:3000/api/v1/execute" -H "Content-Type: application/json" -d '{"server":"docker-mcp","command":"list-containers"}')
if echo "$response" | grep -q "containers"; then
    echo "✅ MCP Hub to Docker MCP integration is working"
else
    echo "❌ MCP Hub to Docker MCP integration is not working"
    echo "Response: $response"
fi

# Test MCP Hub to n8n MCP integration
echo "Testing MCP Hub to n8n MCP integration..."
response=$(curl -s -X POST "http://localhost:3000/api/v1/execute" -H "Content-Type: application/json" -d '{"server":"n8n-mcp","command":"list-workflows"}')
if echo "$response" | grep -q "workflows"; then
    echo "✅ MCP Hub to n8n MCP integration is working"
else
    echo "❌ MCP Hub to n8n MCP integration is not working"
    echo "Response: $response"
fi

echo ""

# Check logs for errors
section "Checking Logs for Errors"
echo "Checking logs for errors..."

# Check MCP Hub logs
echo "Checking MCP Hub logs..."
if docker-compose -f docker-compose.production.yml logs --tail=100 mcp-hub | grep -i "error\|exception\|fail"; then
    echo "⚠️ Found errors in MCP Hub logs"
else
    echo "✅ No errors found in MCP Hub logs"
fi

# Check Docker MCP logs
echo "Checking Docker MCP logs..."
if docker-compose -f docker-compose.production.yml logs --tail=100 docker-mcp | grep -i "error\|exception\|fail"; then
    echo "⚠️ Found errors in Docker MCP logs"
else
    echo "✅ No errors found in Docker MCP logs"
fi

# Check n8n MCP logs
echo "Checking n8n MCP logs..."
if docker-compose -f docker-compose.production.yml logs --tail=100 n8n-mcp | grep -i "error\|exception\|fail"; then
    echo "⚠️ Found errors in n8n MCP logs"
else
    echo "✅ No errors found in n8n MCP logs"
fi

echo ""

# Stop the Docker deployment
section "Stopping Docker Deployment"
echo "Stopping Docker deployment..."

docker-compose -f docker-compose.production.yml down

echo "Docker deployment stopped."
echo ""

# Final message
section "Docker Deployment Test Complete"
echo "The Docker deployment test is now complete."
echo "Please review the results above to ensure the Docker deployment is working correctly."
echo ""
echo "Thank you for using the Docker Deployment Test script."