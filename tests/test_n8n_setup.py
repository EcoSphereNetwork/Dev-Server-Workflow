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
Tests for n8n setup functionality.

This module contains tests for the n8n setup functionality, including:
- Environment variable loading
- Credential creation
- Workflow creation
- API key generation
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.n8n_setup_utils import load_env_file, create_workflow, create_credential, activate_workflow
from src.n8n_setup_install import get_n8n_api_key
from src.n8n_setup_credentials import setup_github_credential, setup_openproject_credential


class TestN8nSetupUtils(unittest.TestCase):
    """Tests for n8n setup utility functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary .env file for testing
        self.test_env_file = Path("test.env")
        with open(self.test_env_file, "w") as f:
            f.write("TEST_VAR=test_value\n")
            f.write("GITHUB_TOKEN=test_github_token\n")
            f.write("OPENPROJECT_TOKEN=test_openproject_token\n")
            f.write("N8N_API_KEY=test_api_key\n")

    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary .env file
        if self.test_env_file.exists():
            self.test_env_file.unlink()

    def test_load_env_file(self):
        """Test loading environment variables from a file."""
        env_vars = load_env_file(self.test_env_file)
        self.assertEqual(env_vars.get("TEST_VAR"), "test_value")
        self.assertEqual(env_vars.get("GITHUB_TOKEN"), "test_github_token")
        self.assertEqual(env_vars.get("OPENPROJECT_TOKEN"), "test_openproject_token")
        self.assertEqual(env_vars.get("N8N_API_KEY"), "test_api_key")

    @patch("requests.post")
    def test_create_workflow(self, mock_post):
        """Test creating a workflow."""
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
    def test_create_credential(self, mock_post):
        """Test creating a credential."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "456", "name": "Test Credential"}
        mock_post.return_value = mock_response

        # Test data
        n8n_url = "http://localhost:5678"
        api_key = "test_api_key"
        credential_data = {
            "name": "Test Credential",
            "type": "githubApi",
            "data": {"token": "test_token"}
        }

        # Call the function
        result = create_credential(n8n_url, api_key, credential_data)

        # Assertions
        self.assertEqual(result["id"], "456")
        self.assertEqual(result["name"], "Test Credential")
        mock_post.assert_called_once_with(
            f"{n8n_url}/api/v1/credentials",
            headers={"X-N8N-API-KEY": api_key},
            json=credential_data
        )

    @patch("requests.patch")
    def test_activate_workflow(self, mock_patch):
        """Test activating a workflow."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "active": True}
        mock_patch.return_value = mock_response

        # Test data
        n8n_url = "http://localhost:5678"
        api_key = "test_api_key"
        workflow_id = "123"

        # Call the function
        result = activate_workflow(n8n_url, api_key, workflow_id)

        # Assertions
        self.assertTrue(result)
        mock_patch.assert_called_once_with(
            f"{n8n_url}/api/v1/workflows/{workflow_id}/activate",
            headers={"X-N8N-API-KEY": api_key}
        )

    @patch("requests.post")
    def test_get_n8n_api_key(self, mock_post):
        """Test getting an n8n API key."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"apiKey": "generated_api_key"}}
        mock_post.return_value = mock_response

        # Test data
        n8n_url = "http://localhost:5678"
        username = "admin"
        password = "password"

        # Call the function
        result = get_n8n_api_key(n8n_url, username, password)

        # Assertions
        self.assertEqual(result, "generated_api_key")
        mock_post.assert_called_once_with(
            f"{n8n_url}/api/v1/me/api-key",
            auth=(username, password)
        )

    @patch("src.n8n_setup_credentials.create_credential")
    def test_setup_github_credential(self, mock_create_credential):
        """Test setting up a GitHub credential."""
        # Mock the response
        mock_create_credential.return_value = {"id": "789", "name": "GitHub"}

        # Test data
        n8n_url = "http://localhost:5678"
        api_key = "test_api_key"
        github_token = "test_github_token"

        # Call the function
        result = setup_github_credential(n8n_url, api_key, github_token)

        # Assertions
        self.assertEqual(result["id"], "789")
        self.assertEqual(result["name"], "GitHub")
        mock_create_credential.assert_called_once()
        args, kwargs = mock_create_credential.call_args
        self.assertEqual(args[0], n8n_url)
        self.assertEqual(args[1], api_key)
        self.assertEqual(args[2]["type"], "githubApi")
        self.assertEqual(args[2]["data"]["token"], github_token)

    @patch("src.n8n_setup_credentials.create_credential")
    def test_setup_openproject_credential(self, mock_create_credential):
        """Test setting up an OpenProject credential."""
        # Mock the response
        mock_create_credential.return_value = {"id": "101", "name": "OpenProject"}

        # Test data
        n8n_url = "http://localhost:5678"
        api_key = "test_api_key"
        openproject_token = "test_openproject_token"

        # Call the function
        result = setup_openproject_credential(n8n_url, api_key, openproject_token)

        # Assertions
        self.assertEqual(result["id"], "101")
        self.assertEqual(result["name"], "OpenProject")
        mock_create_credential.assert_called_once()
        args, kwargs = mock_create_credential.call_args
        self.assertEqual(args[0], n8n_url)
        self.assertEqual(args[1], api_key)
        self.assertEqual(args[2]["type"], "httpHeaderAuth")
        self.assertEqual(args[2]["data"]["name"], "Authorization")
        self.assertEqual(args[2]["data"]["value"], f"Bearer {openproject_token}")


if __name__ == "__main__":
    unittest.main()