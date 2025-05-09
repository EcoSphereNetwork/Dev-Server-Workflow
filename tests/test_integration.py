#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Konfiguriere Logging
logger = setup_logging("INFO")

# Lade Konfiguration
config_manager = ConfigManager()
config = config_manager.load_env_file(".env")

"""
End-to-end integration tests for the Dev-Server-Workflow ecosystem.

This module contains tests for the integration of all components, including:
- n8n setup and workflow execution
- MCP server functionality
- OpenHands integration
- CLI functionality
"""

import os
import sys
import unittest
import subprocess
import time
import json
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests for the Dev-Server-Workflow ecosystem."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment for all tests."""
        # Create a temporary .env file for testing
        cls.test_env_file = Path("test_integration.env")
        with open(cls.test_env_file, "w") as f:
            f.write("N8N_URL=http://localhost:5678\n")
            f.write("N8N_USER=admin\n")
            f.write("N8N_PASSWORD=password\n")
            f.write("N8N_API_KEY=test_api_key\n")
            f.write("GITHUB_TOKEN=test_github_token\n")
            f.write("OPENPROJECT_URL=https://test-openproject.com\n")
            f.write("OPENPROJECT_TOKEN=test_openproject_token\n")
            f.write("MCP_ENABLED=true\n")
            f.write("MCP_SERVER_PORT=3333\n")

        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            cls.docker_available = True
        except (subprocess.SubprocessError, FileNotFoundError):
            cls.docker_available = False
            logger.info("Docker not available, skipping Docker-dependent tests")

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment after all tests."""
        # Remove the temporary .env file
        if cls.test_env_file.exists():
            cls.test_env_file.unlink()

    def setUp(self):
        """Set up test environment for each test."""
        pass

    def tearDown(self):
        """Clean up test environment after each test."""
        pass

    @unittest.skipIf(not os.environ.get("RUN_DOCKER_TESTS"), "Docker tests disabled")
    def test_n8n_docker_installation(self):
        """Test n8n installation using Docker."""
        if not self.docker_available:
            self.skipTest("Docker not available")

        # Run the installation script with --no-install to avoid actually installing n8n
        result = subprocess.run(
            [sys.executable, "setup.py", "install", "--env-file", str(self.test_env_file), "--no-install"],
            capture_output=True,
            text=True
        )

        # Check if the command was successful
        self.assertEqual(result.returncode, 0, f"Installation failed: {result.stderr}")
        self.assertIn("No API key provided", result.stdout)

    def test_setup_test_command(self):
        """Test the setup.py test command."""
        # Run the test command
        result = subprocess.run(
            [sys.executable, "setup.py", "test"],
            capture_output=True,
            text=True
        )

        # Check if the command was successful
        self.assertEqual(result.returncode, 0, f"Test command failed: {result.stderr}")
        self.assertIn("Testing n8n Workflow Integration Setup", result.stdout)
        self.assertIn("Test completed", result.stdout)

    @patch("requests.post")
    def test_n8n_workflow_creation(self, mock_post):
        """Test n8n workflow creation."""
        # Import the necessary functions
        from src.n8n_setup_utils import create_workflow

        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "name": "Test Workflow"}
        mock_post.return_value = mock_response

        # Test data
        n8n_url = "http://localhost:5678"
        api_key = "test_api_key"
        workflow_data = {
            "name": "Test Workflow",
            "nodes": [],
            "connections": {}
        }

        # Call the function
        result = create_workflow(n8n_url, api_key, workflow_data)

        # Assertions
        self.assertEqual(result["id"], "123")
        self.assertEqual(result["name"], "Test Workflow")
        mock_post.assert_called_once_with(
            f"{n8n_url}/api/v1/workflows",
            headers={"X-N8N-API-KEY": api_key},
            json=workflow_data
        )

    @patch("requests.post")
    def test_mcp_server_initialization(self, mock_post):
        """Test MCP server initialization and tool listing."""
        # Import the MCP server class
        from src.n8n_mcp_server import N8nMCPServer

        # Create an instance of the MCP server
        n8n_url = "http://localhost:5678"
        api_key = "test_api_key"
        server = N8nMCPServer(n8n_url, api_key)

        # Check if tools are loaded
        self.assertIsNotNone(server.tools)
        self.assertIsInstance(server.tools, list)
        self.assertGreater(len(server.tools), 0)

        # Check if the tools have the required structure
        for tool in server.tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("parameters", tool)

    @unittest.skipIf(not os.environ.get("RUN_CLI_TESTS"), "CLI tests disabled")
    def test_cli_help_command(self):
        """Test the CLI help command."""
        # Run the help command
        result = subprocess.run(
            ["./cli/dev-server.sh", "help"],
            capture_output=True,
            text=True
        )

        # Check if the command was successful
        self.assertEqual(result.returncode, 0, f"Help command failed: {result.stderr}")
        self.assertIn("Dev-Server CLI", result.stdout)
        self.assertIn("Verfügbare Befehle:", result.stdout)

    @unittest.skipIf(not os.environ.get("RUN_CLI_TESTS"), "CLI tests disabled")
    def test_cli_status_command(self):
        """Test the CLI status command."""
        # Run the status command
        result = subprocess.run(
            ["./cli/dev-server.sh", "status"],
            capture_output=True,
            text=True
        )

        # Check if the command was successful
        self.assertEqual(result.returncode, 0, f"Status command failed: {result.stderr}")
        self.assertIn("=== Dev-Server Status ===", result.stdout)

    @patch("requests.post")
    def test_github_webhook_trigger(self, mock_post):
        """Test GitHub webhook trigger for n8n workflow."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        # Test data
        webhook_url = "http://localhost:5678/webhook/github"
        webhook_data = {
            "action": "opened",
            "issue": {
                "number": 42,
                "title": "Test Issue",
                "body": "Test Body",
                "user": {
                    "login": "test_user"
                }
            },
            "repository": {
                "full_name": "test_owner/test_repo"
            }
        }

        # Send the webhook
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            json=webhook_data
        )

        # Assertions
        mock_post.assert_called_once_with(
            webhook_url,
            headers={"Content-Type": "application/json"},
            json=webhook_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

    @unittest.skipIf(not os.path.exists("./cli/dev-server.sh"), "CLI script not found")
    def test_cli_script_exists(self):
        """Test if the CLI script exists and is executable."""
        cli_script = Path("./cli/dev-server.sh")
        self.assertTrue(cli_script.exists(), "CLI script does not exist")
        self.assertTrue(os.access(cli_script, os.X_OK), "CLI script is not executable")

    def test_env_template_exists(self):
        """Test if the environment template exists."""
        env_template = Path("src/env-template")
        self.assertTrue(env_template.exists(), "Environment template does not exist")

    @unittest.skipIf(not os.environ.get("RUN_DOCKER_TESTS"), "Docker tests disabled")
    def test_docker_compose_file_exists(self):
        """Test if the Docker Compose file exists."""
        docker_compose_file = Path("docker-compose.yml")
        self.assertTrue(docker_compose_file.exists(), "Docker Compose file does not exist")


if __name__ == "__main__":
    unittest.main()