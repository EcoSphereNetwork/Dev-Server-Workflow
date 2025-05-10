#!/bin/bash

# Script to set up the test environment
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Display welcome message
section "Test Environment Setup"
echo "This script will set up the test environment for the Dev-Server-Workflow repository."
echo ""

# Install test dependencies
section "Installing Test Dependencies"
echo "Installing test dependencies..."

# Install pytest and related packages
pip install pytest pytest-cov pytest-mock pytest-asyncio

# Install frontend test dependencies
cd frontend && npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event && cd ..

echo "Test dependencies installed."
echo ""

# Create test directories
section "Creating Test Directories"
echo "Creating test directories..."

# Create test directories for Python tests
mkdir -p tests/unit/mcp_hub
mkdir -p tests/unit/mcp_servers/docker_mcp
mkdir -p tests/unit/mcp_servers/n8n_mcp_server
mkdir -p tests/unit/mcp_servers/prompt_mcp_server
mkdir -p tests/unit/mcp_servers/llm_cost_analyzer_mcp
mkdir -p tests/unit/mcp_servers/openhands
mkdir -p tests/integration
mkdir -p tests/e2e

# Create test directories for frontend tests
mkdir -p frontend/src/__tests__/components
mkdir -p frontend/src/__tests__/pages
mkdir -p frontend/src/__tests__/services
mkdir -p frontend/src/__tests__/utils

echo "Test directories created."
echo ""

# Create test configuration files
section "Creating Test Configuration Files"
echo "Creating test configuration files..."

# Create pytest configuration file
cat > pytest.ini << EOF
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=src --cov-report=term-missing --cov-report=html
EOF

# Create test environment file
cat > .env.test << EOF
# Test Environment Configuration
NODE_ENV=test
LOG_LEVEL=debug

# MCP Hub Configuration
MCP_HUB_PORT=3100
MCP_HUB_HOST=localhost

# Docker MCP Configuration
DOCKER_MCP_PORT=3101
DOCKER_MCP_HOST=localhost
DOCKER_MCP_SOCKET=/var/run/docker.sock

# n8n MCP Configuration
N8N_MCP_PORT=3102
N8N_MCP_HOST=localhost
N8N_URL=http://localhost:5778
N8N_API_KEY=test-n8n-api-key

# Prompt MCP Configuration
PROMPT_MCP_PORT=3103
PROMPT_MCP_HOST=localhost
OPENAI_API_KEY=test-openai-api-key
ANTHROPIC_API_KEY=test-anthropic-api-key

# LLM Cost Analyzer MCP Configuration
LLM_COST_ANALYZER_MCP_PORT=3104
LLM_COST_ANALYZER_MCP_HOST=localhost

# OpenHands MCP Configuration
OPENHANDS_MCP_PORT=3105
OPENHANDS_MCP_HOST=localhost
OPENHANDS_URL=http://localhost:8100
OPENHANDS_API_KEY=test-openhands-api-key

# n8n Configuration
N8N_PORT=5778
N8N_PROTOCOL=http
N8N_HOST=localhost
N8N_EDITOR_BASE_URL=http://localhost:5778
N8N_ENCRYPTION_KEY=test-n8n-encryption-key
WEBHOOK_URL=http://localhost:5778/

# OpenHands Configuration
OPENHANDS_PORT=8100
OPENHANDS_HOST=localhost

# Security Configuration
JWT_SECRET=test-jwt-secret
SESSION_SECRET=test-session-secret
COOKIE_SECRET=test-cookie-secret

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dev_server_workflow_test
DB_USER=postgres
DB_PASSWORD=postgres

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis
EOF

# Create frontend test configuration
cat > frontend/jest.config.js << EOF
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': '<rootDir>/src/__mocks__/fileMock.js'
  },
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.(js|jsx)$': 'babel-jest'
  },
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/src/smolitux-ui/'
  ],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/smolitux-ui/**/*'
  ]
};
EOF

# Create frontend test setup file
mkdir -p frontend/src/__mocks__
cat > frontend/src/__mocks__/fileMock.js << EOF
module.exports = 'test-file-stub';
EOF

# Create frontend test setup file
cat > frontend/src/setupTests.ts << EOF
// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
EOF

echo "Test configuration files created."
echo ""

# Create sample tests
section "Creating Sample Tests"
echo "Creating sample tests..."

# Create sample Python test
cat > tests/unit/mcp_hub/test_hub_manager.py << EOF
import pytest
from unittest.mock import MagicMock, patch
from src.mcp_hub.hub_manager import HubManager

class TestHubManager:
    @pytest.fixture
    def hub_manager(self):
        return HubManager()
    
    def test_hub_manager_initialization(self, hub_manager):
        assert hub_manager is not None
        assert hasattr(hub_manager, 'servers')
        assert isinstance(hub_manager.servers, dict)
    
    @patch('src.mcp_hub.hub_manager.HubManager.register_server')
    def test_register_server(self, mock_register, hub_manager):
        server = MagicMock()
        server.id = 'test-server'
        server.name = 'Test Server'
        server.type = 'test'
        
        hub_manager.register_server(server)
        
        mock_register.assert_called_once_with(server)
EOF

# Create sample frontend test
cat > frontend/src/__tests__/components/test_button.tsx << EOF
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '../../components/common/Button';

describe('Button Component', () => {
  test('renders button with correct text', () => {
    render(<Button>Click Me</Button>);
    const buttonElement = screen.getByText(/Click Me/i);
    expect(buttonElement).toBeInTheDocument();
  });

  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    const buttonElement = screen.getByText(/Click Me/i);
    fireEvent.click(buttonElement);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies disabled state correctly', () => {
    render(<Button disabled>Click Me</Button>);
    const buttonElement = screen.getByText(/Click Me/i);
    expect(buttonElement).toBeDisabled();
  });
});
EOF

echo "Sample tests created."
echo ""

# Create test runner script
section "Creating Test Runner Script"
echo "Creating test runner script..."

cat > run_tests.sh << EOF
#!/bin/bash

# Script to run tests
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  \$1"
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

while [[ \$# -gt 0 ]]; do
    key="\$1"
    case \$key in
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
            echo "Unknown option: \$key"
            exit 1
            ;;
    esac
done

# If no specific test type is specified, run all
if [ "\$BACKEND" = false ] && [ "\$FRONTEND" = false ]; then
    BACKEND=true
    FRONTEND=true
fi

if [ "\$UNIT" = false ] && [ "\$INTEGRATION" = false ] && [ "\$E2E" = false ]; then
    UNIT=true
    INTEGRATION=true
    E2E=true
fi

# Run backend tests
if [ "\$BACKEND" = true ]; then
    section "Running Backend Tests"
    
    # Set up environment
    export $(grep -v '^#' .env.test | xargs)
    
    # Run unit tests
    if [ "\$UNIT" = true ]; then
        echo "Running backend unit tests..."
        if [ "\$COVERAGE" = true ]; then
            pytest tests/unit -v --cov=src --cov-report=term-missing --cov-report=html
        else
            pytest tests/unit -v
        fi
    fi
    
    # Run integration tests
    if [ "\$INTEGRATION" = true ]; then
        echo "Running backend integration tests..."
        if [ "\$COVERAGE" = true ]; then
            pytest tests/integration -v --cov=src --cov-report=term-missing --cov-report=html
        else
            pytest tests/integration -v
        fi
    fi
    
    # Run end-to-end tests
    if [ "\$E2E" = true ]; then
        echo "Running backend end-to-end tests..."
        if [ "\$COVERAGE" = true ]; then
            pytest tests/e2e -v --cov=src --cov-report=term-missing --cov-report=html
        else
            pytest tests/e2e -v
        fi
    fi
fi

# Run frontend tests
if [ "\$FRONTEND" = true ]; then
    section "Running Frontend Tests"
    
    cd frontend
    
    # Run unit tests
    if [ "\$UNIT" = true ]; then
        echo "Running frontend unit tests..."
        if [ "\$COVERAGE" = true ]; then
            npm test -- --coverage
        else
            npm test
        fi
    fi
    
    # Run end-to-end tests
    if [ "\$E2E" = true ]; then
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
EOF

chmod +x run_tests.sh

echo "Test runner script created."
echo ""

# Final message
section "Test Environment Setup Complete"
echo "The test environment setup is now complete."
echo "You can now run tests using the run_tests.sh script."
echo ""
echo "Examples:"
echo "  ./run_tests.sh --backend --unit                # Run backend unit tests"
echo "  ./run_tests.sh --frontend --unit --coverage    # Run frontend unit tests with coverage"
echo "  ./run_tests.sh --backend --integration         # Run backend integration tests"
echo "  ./run_tests.sh --backend --frontend --unit     # Run all unit tests"
echo "  ./run_tests.sh                                 # Run all tests"
echo ""
echo "Thank you for using the Test Environment Setup script."