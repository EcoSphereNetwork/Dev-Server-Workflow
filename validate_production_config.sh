#!/bin/bash

# Script to validate the production configuration
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Function to check if a variable is defined in a file
check_variable() {
    local file=$1
    local variable=$2
    local description=$3
    
    if grep -q "^$variable=" "$file" || grep -q "^$variable:" "$file"; then
        echo "✅ $description ($variable) is defined in $file"
        return 0
    else
        echo "❌ $description ($variable) is not defined in $file"
        return 1
    fi
}

# Display welcome message
section "Production Configuration Validation"
echo "This script will validate the production configuration of the Dev-Server-Workflow repository."
echo ""

# Check if production environment file exists
section "Checking Production Environment File"
if [ -f ".env.production" ]; then
    echo "✅ Production environment file exists"
    
    # Check required variables
    check_variable ".env.production" "NODE_ENV" "Node environment"
    check_variable ".env.production" "LOG_LEVEL" "Log level"
    check_variable ".env.production" "MCP_HUB_PORT" "MCP Hub port"
    check_variable ".env.production" "MCP_HUB_HOST" "MCP Hub host"
    check_variable ".env.production" "DOCKER_MCP_PORT" "Docker MCP port"
    check_variable ".env.production" "N8N_MCP_PORT" "n8n MCP port"
    check_variable ".env.production" "PROMPT_MCP_PORT" "Prompt MCP port"
    check_variable ".env.production" "LLM_COST_ANALYZER_MCP_PORT" "LLM Cost Analyzer MCP port"
    check_variable ".env.production" "OPENHANDS_MCP_PORT" "OpenHands MCP port"
    check_variable ".env.production" "N8N_PORT" "n8n port"
    check_variable ".env.production" "NGINX_PORT" "Nginx port"
    check_variable ".env.production" "PROMETHEUS_PORT" "Prometheus port"
    check_variable ".env.production" "GRAFANA_PORT" "Grafana port"
    check_variable ".env.production" "ALERTMANAGER_PORT" "Alertmanager port"
    check_variable ".env.production" "JWT_SECRET" "JWT secret"
    check_variable ".env.production" "SESSION_SECRET" "Session secret"
    check_variable ".env.production" "COOKIE_SECRET" "Cookie secret"
else
    echo "❌ Production environment file does not exist"
fi

echo ""

# Check if production Docker Compose file exists
section "Checking Production Docker Compose File"
if [ -f "docker-compose.production.yml" ]; then
    echo "✅ Production Docker Compose file exists"
    
    # Check required services
    if grep -q "mcp-hub:" "docker-compose.production.yml"; then
        echo "✅ MCP Hub service is defined in docker-compose.production.yml"
    else
        echo "❌ MCP Hub service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "docker-mcp:" "docker-compose.production.yml"; then
        echo "✅ Docker MCP service is defined in docker-compose.production.yml"
    else
        echo "❌ Docker MCP service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "n8n-mcp:" "docker-compose.production.yml"; then
        echo "✅ n8n MCP service is defined in docker-compose.production.yml"
    else
        echo "❌ n8n MCP service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "prompt-mcp:" "docker-compose.production.yml"; then
        echo "✅ Prompt MCP service is defined in docker-compose.production.yml"
    else
        echo "❌ Prompt MCP service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "llm-cost-analyzer-mcp:" "docker-compose.production.yml"; then
        echo "✅ LLM Cost Analyzer MCP service is defined in docker-compose.production.yml"
    else
        echo "❌ LLM Cost Analyzer MCP service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "openhands-mcp:" "docker-compose.production.yml"; then
        echo "✅ OpenHands MCP service is defined in docker-compose.production.yml"
    else
        echo "❌ OpenHands MCP service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "n8n:" "docker-compose.production.yml"; then
        echo "✅ n8n service is defined in docker-compose.production.yml"
    else
        echo "❌ n8n service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "nginx:" "docker-compose.production.yml"; then
        echo "✅ Nginx service is defined in docker-compose.production.yml"
    else
        echo "❌ Nginx service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "prometheus:" "docker-compose.production.yml"; then
        echo "✅ Prometheus service is defined in docker-compose.production.yml"
    else
        echo "❌ Prometheus service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "grafana:" "docker-compose.production.yml"; then
        echo "✅ Grafana service is defined in docker-compose.production.yml"
    else
        echo "❌ Grafana service is not defined in docker-compose.production.yml"
    fi
    
    if grep -q "alertmanager:" "docker-compose.production.yml"; then
        echo "✅ Alertmanager service is defined in docker-compose.production.yml"
    else
        echo "❌ Alertmanager service is not defined in docker-compose.production.yml"
    fi
else
    echo "❌ Production Docker Compose file does not exist"
fi

echo ""

# Check if production Dockerfile exists
section "Checking Production Dockerfile"
if [ -f "Dockerfile.production" ]; then
    echo "✅ Production Dockerfile exists"
else
    echo "⚠️ Production Dockerfile does not exist, using default Dockerfile"
    
    if [ -f "Dockerfile" ]; then
        echo "✅ Default Dockerfile exists"
    else
        echo "❌ Default Dockerfile does not exist"
    fi
fi

echo ""

# Final message
section "Production Configuration Validation Complete"
echo "The production configuration validation is now complete."
echo "Please review the results above to ensure the production configuration is correct."
echo ""
echo "Thank you for using the Production Configuration Validation script."