"""
Integration tests for MCP workflows.
"""

import unittest
import os
import sys
import json
import time
import requests
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.error_handling import BaseError

class TestMCPWorkflows(unittest.TestCase):
    """Integration tests for MCP workflows."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Set up environment variables for testing
        os.environ['MCP_HUB_URL'] = 'http://localhost:3000'
        os.environ['N8N_URL'] = 'http://localhost:5678'
        os.environ['DOCKER_MCP_URL'] = 'http://localhost:3334'
        os.environ['N8N_MCP_URL'] = 'http://localhost:3335'
        os.environ['PROMPT_MCP_URL'] = 'http://localhost:3336'
        os.environ['LLM_COST_MCP_URL'] = 'http://localhost:3337'
        os.environ['OPENHANDS_MCP_URL'] = 'http://localhost:3338'
        
        # Check if MCP Hub is running
        try:
            response = requests.get(os.environ['MCP_HUB_URL'] + '/health', timeout=5)
            if response.status_code != 200:
                raise Exception(f"MCP Hub is not running: {response.status_code}")
        except requests.exceptions.RequestException:
            # Skip tests if MCP Hub is not running
            raise unittest.SkipTest("MCP Hub is not running")
    
    def test_mcp_hub_health(self):
        """Test that MCP Hub is healthy."""
        response = requests.get(os.environ['MCP_HUB_URL'] + '/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_docker_mcp_health(self):
        """Test that Docker MCP is healthy."""
        try:
            response = requests.get(os.environ['DOCKER_MCP_URL'] + '/health')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
        except requests.exceptions.RequestException:
            self.skipTest("Docker MCP is not running")
    
    def test_n8n_mcp_health(self):
        """Test that n8n MCP is healthy."""
        try:
            response = requests.get(os.environ['N8N_MCP_URL'] + '/health')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
        except requests.exceptions.RequestException:
            self.skipTest("n8n MCP is not running")
    
    def test_prompt_mcp_health(self):
        """Test that Prompt MCP is healthy."""
        try:
            response = requests.get(os.environ['PROMPT_MCP_URL'] + '/health')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
        except requests.exceptions.RequestException:
            self.skipTest("Prompt MCP is not running")
    
    def test_llm_cost_mcp_health(self):
        """Test that LLM Cost MCP is healthy."""
        try:
            response = requests.get(os.environ['LLM_COST_MCP_URL'] + '/health')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
        except requests.exceptions.RequestException:
            self.skipTest("LLM Cost MCP is not running")
    
    def test_openhands_mcp_health(self):
        """Test that OpenHands MCP is healthy."""
        try:
            response = requests.get(os.environ['OPENHANDS_MCP_URL'] + '/health')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
        except requests.exceptions.RequestException:
            self.skipTest("OpenHands MCP is not running")
    
    def test_mcp_hub_list_servers(self):
        """Test that MCP Hub can list servers."""
        response = requests.get(os.environ['MCP_HUB_URL'] + '/servers')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        # Check that all expected servers are in the list
        server_types = [server['type'] for server in data]
        expected_types = ['docker', 'n8n', 'prompt', 'llm-cost', 'openhands']
        for expected_type in expected_types:
            self.assertIn(expected_type, server_types)
    
    def test_docker_mcp_list_containers(self):
        """Test that Docker MCP can list containers."""
        try:
            response = requests.get(os.environ['DOCKER_MCP_URL'] + '/containers')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
        except requests.exceptions.RequestException:
            self.skipTest("Docker MCP is not running")
    
    def test_n8n_mcp_list_workflows(self):
        """Test that n8n MCP can list workflows."""
        try:
            response = requests.get(os.environ['N8N_MCP_URL'] + '/workflows')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
        except requests.exceptions.RequestException:
            self.skipTest("n8n MCP is not running")
    
    def test_prompt_mcp_list_prompts(self):
        """Test that Prompt MCP can list prompts."""
        try:
            response = requests.get(os.environ['PROMPT_MCP_URL'] + '/prompts')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
        except requests.exceptions.RequestException:
            self.skipTest("Prompt MCP is not running")
    
    def test_llm_cost_mcp_get_stats(self):
        """Test that LLM Cost MCP can get stats."""
        try:
            response = requests.get(os.environ['LLM_COST_MCP_URL'] + '/stats')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, dict)
        except requests.exceptions.RequestException:
            self.skipTest("LLM Cost MCP is not running")
    
    def test_openhands_mcp_list_tools(self):
        """Test that OpenHands MCP can list tools."""
        try:
            response = requests.get(os.environ['OPENHANDS_MCP_URL'] + '/tools')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
        except requests.exceptions.RequestException:
            self.skipTest("OpenHands MCP is not running")
    
    def test_workflow_execution(self):
        """Test that a workflow can be executed."""
        # This test requires n8n to be running with a test workflow
        try:
            # Check if n8n is running
            response = requests.get(os.environ['N8N_URL'] + '/healthz')
            if response.status_code != 200:
                self.skipTest("n8n is not running")
                
            # Get the list of workflows
            response = requests.get(os.environ['N8N_MCP_URL'] + '/workflows')
            self.assertEqual(response.status_code, 200)
            workflows = response.json()
            
            if not workflows:
                self.skipTest("No workflows found in n8n")
                
            # Execute the first workflow
            workflow_id = workflows[0]['id']
            response = requests.post(
                os.environ['N8N_MCP_URL'] + f'/workflows/{workflow_id}/execute',
                json={}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('executionId', data)
            
            # Wait for the execution to complete
            execution_id = data['executionId']
            max_retries = 10
            retry_count = 0
            
            while retry_count < max_retries:
                response = requests.get(
                    os.environ['N8N_MCP_URL'] + f'/executions/{execution_id}'
                )
                self.assertEqual(response.status_code, 200)
                execution = response.json()
                
                if execution['status'] in ['success', 'error']:
                    break
                    
                time.sleep(1)
                retry_count += 1
                
            self.assertIn(execution['status'], ['success', 'error'])
        except requests.exceptions.RequestException:
            self.skipTest("n8n MCP is not running")
    
    def test_docker_container_management(self):
        """Test that Docker containers can be managed."""
        try:
            # Check if Docker MCP is running
            response = requests.get(os.environ['DOCKER_MCP_URL'] + '/health')
            if response.status_code != 200:
                self.skipTest("Docker MCP is not running")
                
            # Get the list of containers
            response = requests.get(os.environ['DOCKER_MCP_URL'] + '/containers')
            self.assertEqual(response.status_code, 200)
            containers = response.json()
            
            if not containers:
                self.skipTest("No containers found")
                
            # Get details of the first container
            container_id = containers[0]['id']
            response = requests.get(
                os.environ['DOCKER_MCP_URL'] + f'/containers/{container_id}'
            )
            self.assertEqual(response.status_code, 200)
            container = response.json()
            self.assertEqual(container['id'], container_id)
        except requests.exceptions.RequestException:
            self.skipTest("Docker MCP is not running")
    
    def test_prompt_execution(self):
        """Test that a prompt can be executed."""
        try:
            # Check if Prompt MCP is running
            response = requests.get(os.environ['PROMPT_MCP_URL'] + '/health')
            if response.status_code != 200:
                self.skipTest("Prompt MCP is not running")
                
            # Execute a simple prompt
            response = requests.post(
                os.environ['PROMPT_MCP_URL'] + '/execute',
                json={
                    'prompt': 'Say hello',
                    'model': 'echo',  # Use a mock model that just echoes the prompt
                    'parameters': {}
                }
            )
            
            # If the API key is not set, this will return an error
            if response.status_code == 401:
                self.skipTest("API key not set for Prompt MCP")
                
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('result', data)
        except requests.exceptions.RequestException:
            self.skipTest("Prompt MCP is not running")

if __name__ == '__main__':
    unittest.main()