"""
Pytest configuration file for Dev-Server-Workflow tests.

This file contains fixtures and configuration for pytest.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def test_env_file():
    """Create a temporary .env file for testing."""
    env_file = Path("test_fixture.env")
    with open(env_file, "w") as f:
        f.write("N8N_URL=http://localhost:5678\n")
        f.write("N8N_USER=admin\n")
        f.write("N8N_PASSWORD=password\n")
        f.write("N8N_API_KEY=test_api_key\n")
        f.write("GITHUB_TOKEN=test_github_token\n")
        f.write("OPENPROJECT_URL=https://test-openproject.com\n")
        f.write("OPENPROJECT_TOKEN=test_openproject_token\n")
        f.write("MCP_ENABLED=true\n")
        f.write("MCP_SERVER_PORT=3333\n")
    
    yield env_file
    
    # Clean up
    if env_file.exists():
        env_file.unlink()


@pytest.fixture
def mock_n8n_api():
    """Mock the n8n API responses."""
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self.json_data = json_data
        
        def json(self):
            return self.json_data
    
    return MockResponse


@pytest.fixture
def mock_github_api():
    """Mock the GitHub API responses."""
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self.json_data = json_data
        
        def json(self):
            return self.json_data
    
    return MockResponse


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing."""
    return {
        "name": "Test Workflow",
        "nodes": [
            {
                "parameters": {
                    "path": "/webhook",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [
                    250,
                    300
                ]
            }
        ],
        "connections": {}
    }


@pytest.fixture
def sample_credential_data():
    """Sample credential data for testing."""
    return {
        "name": "GitHub API",
        "type": "githubApi",
        "data": {
            "token": "test_github_token"
        }
    }


def pytest_configure(config):
    """Configure pytest."""
    # Register custom markers
    config.addinivalue_line("markers", "docker: mark test as requiring Docker")
    config.addinivalue_line("markers", "cli: mark test as requiring CLI")
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_runtest_setup(item):
    """Set up tests."""
    # Skip Docker tests if Docker is not available
    if "docker" in item.keywords and not os.environ.get("RUN_DOCKER_TESTS"):
        pytest.skip("Docker tests disabled")
    
    # Skip CLI tests if CLI tests are disabled
    if "cli" in item.keywords and not os.environ.get("RUN_CLI_TESTS"):
        pytest.skip("CLI tests disabled")
    
    # Skip integration tests if integration tests are disabled
    if "integration" in item.keywords and not os.environ.get("RUN_INTEGRATION_TESTS"):
        pytest.skip("Integration tests disabled")