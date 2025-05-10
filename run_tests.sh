#!/bin/bash

# Script to run tests
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Display welcome message
section "Test Runner"
echo "This script will run tests for the Dev-Server-Workflow repository."
echo ""

# Parse command line arguments
BACKEND=false
FRONTEND=false
COVERAGE=false
UNIT=false
INTEGRATION=false
E2E=false

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --backend)
            BACKEND=true
            shift
            ;;
        --frontend)
            FRONTEND=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --unit)
            UNIT=true
            shift
            ;;
        --integration)
            INTEGRATION=true
            shift
            ;;
        --e2e)
            E2E=true
            shift
            ;;
        *)
            echo "Unknown option: $key"
            exit 1
            ;;
    esac
done

# If no specific test type is specified, run all
if [ "$BACKEND" = false ] && [ "$FRONTEND" = false ]; then
    BACKEND=true
    FRONTEND=true
fi

if [ "$UNIT" = false ] && [ "$INTEGRATION" = false ] && [ "$E2E" = false ]; then
    UNIT=true
    INTEGRATION=true
    E2E=true
fi

# Run backend tests
if [ "$BACKEND" = true ]; then
    section "Running Backend Tests"
    
    # Set up environment
    export NODE_ENV=test LOG_LEVEL=debug MCP_HUB_PORT=3100 MCP_HUB_HOST=localhost DOCKER_MCP_PORT=3101 DOCKER_MCP_HOST=localhost DOCKER_MCP_SOCKET=/var/run/docker.sock N8N_MCP_PORT=3102 N8N_MCP_HOST=localhost N8N_URL=http://localhost:5778 N8N_API_KEY=test-n8n-api-key PROMPT_MCP_PORT=3103 PROMPT_MCP_HOST=localhost OPENAI_API_KEY=test-openai-api-key ANTHROPIC_API_KEY=test-anthropic-api-key LLM_COST_ANALYZER_MCP_PORT=3104 LLM_COST_ANALYZER_MCP_HOST=localhost OPENHANDS_MCP_PORT=3105 OPENHANDS_MCP_HOST=localhost OPENHANDS_URL=http://localhost:8100 OPENHANDS_API_KEY=test-openhands-api-key N8N_PORT=5778 N8N_PROTOCOL=http N8N_HOST=localhost N8N_EDITOR_BASE_URL=http://localhost:5778 N8N_ENCRYPTION_KEY=test-n8n-encryption-key WEBHOOK_URL=http://localhost:5778/ OPENHANDS_PORT=8100 OPENHANDS_HOST=localhost JWT_SECRET=test-jwt-secret SESSION_SECRET=test-session-secret COOKIE_SECRET=test-cookie-secret DB_HOST=localhost DB_PORT=5432 DB_NAME=dev_server_workflow_test DB_USER=postgres DB_PASSWORD=postgres REDIS_HOST=localhost REDIS_PORT=6379 REDIS_PASSWORD=redis
    
    # Run unit tests
    if [ "$UNIT" = true ]; then
        echo "Running backend unit tests..."
        if [ "$COVERAGE" = true ]; then
            pytest tests/unit -v --cov=src --cov-report=term-missing --cov-report=html
        else
            pytest tests/unit -v
        fi
    fi
    
    # Run integration tests
    if [ "$INTEGRATION" = true ]; then
        echo "Running backend integration tests..."
        if [ "$COVERAGE" = true ]; then
            pytest tests/integration -v --cov=src --cov-report=term-missing --cov-report=html
        else
            pytest tests/integration -v
        fi
    fi
    
    # Run end-to-end tests
    if [ "$E2E" = true ]; then
        echo "Running backend end-to-end tests..."
        if [ "$COVERAGE" = true ]; then
            pytest tests/e2e -v --cov=src --cov-report=term-missing --cov-report=html
        else
            pytest tests/e2e -v
        fi
    fi
fi

# Run frontend tests
if [ "$FRONTEND" = true ]; then
    section "Running Frontend Tests"
    
    cd frontend
    
    # Run unit tests
    if [ "$UNIT" = true ]; then
        echo "Running frontend unit tests..."
        if [ "$COVERAGE" = true ]; then
            npm test -- --coverage
        else
            npm test
        fi
    fi
    
    # Run end-to-end tests
    if [ "$E2E" = true ]; then
        echo "Running frontend end-to-end tests..."
        if [ -f "cypress.json" ]; then
            npm run cypress:run
        else
            echo "Cypress not configured, skipping frontend end-to-end tests."
        fi
    fi
    
    cd ..
fi

section "Test Run Complete"
echo "All tests have been run."
echo ""
echo "Thank you for using the Test Runner script."
