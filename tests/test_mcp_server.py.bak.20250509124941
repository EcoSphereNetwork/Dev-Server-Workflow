#!/usr/bin/env python3
"""
Tests for MCP server functionality.

This module contains tests for the MCP server functionality, including:
- Server initialization
- Message handling
- Tool execution
"""

import os
import sys
import unittest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from io import StringIO

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the MCP server class from the template in n8n_setup_main.py
from src.n8n_mcp_server import N8nMCPServer


class TestMCPServer(unittest.TestCase):
    """Tests for MCP server functionality."""

    def setUp(self):
        """Set up test environment."""
        self.n8n_url = "http://localhost:5678"
        self.api_key = "test_api_key"
        self.server = N8nMCPServer(self.n8n_url, self.api_key)

    def test_initialization(self):
        """Test server initialization."""
        self.assertEqual(self.server.n8n_url, self.n8n_url)
        self.assertEqual(self.server.n8n_api_key, self.api_key)
        self.assertEqual(self.server.request_id, 0)
        self.assertIsNotNone(self.server.tools)
        self.assertIsInstance(self.server.tools, list)

    def test_load_available_tools(self):
        """Test loading available tools."""
        tools = self.server._load_available_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)

        # Check if tools have the required structure
        for tool in tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("parameters", tool)
            self.assertIn("type", tool["parameters"])
            self.assertIn("properties", tool["parameters"])

    @patch("asyncio.StreamWriter")
    async def test_send_response(self, mock_writer):
        """Test sending a response."""
        # Mock the writer
        mock_writer.write = AsyncMock()
        mock_writer.drain = AsyncMock()
        self.server.writer = mock_writer

        # Test data
        request_id = 1
        result = {"status": "success"}

        # Call the function
        await self.server._send_response(request_id, result)

        # Assertions
        expected_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        mock_writer.write.assert_called_once_with(f"{json.dumps(expected_response)}\n".encode())
        mock_writer.drain.assert_called_once()

    @patch("asyncio.StreamWriter")
    async def test_send_error(self, mock_writer):
        """Test sending an error."""
        # Mock the writer
        mock_writer.write = AsyncMock()
        mock_writer.drain = AsyncMock()
        self.server.writer = mock_writer

        # Test data
        request_id = 2
        error_message = "Test error"
        code = -32603

        # Call the function
        await self.server._send_error(request_id, error_message, code)

        # Assertions
        expected_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": error_message
            }
        }
        mock_writer.write.assert_called_once_with(f"{json.dumps(expected_response)}\n".encode())
        mock_writer.drain.assert_called_once()

    @patch.object(N8nMCPServer, "_send_response")
    async def test_handle_initialize(self, mock_send_response):
        """Test handling initialize method."""
        # Mock the send_response method
        mock_send_response.return_value = None

        # Test data
        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "initialize",
            "params": {}
        }

        # Call the function
        await self.server._handle_message(message)

        # Assertions
        mock_send_response.assert_called_once_with(3, {"capabilities": {"tools": True}})

    @patch.object(N8nMCPServer, "_send_response")
    async def test_handle_list_tools(self, mock_send_response):
        """Test handling mcp.listTools method."""
        # Mock the send_response method
        mock_send_response.return_value = None

        # Test data
        message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "mcp.listTools",
            "params": {}
        }

        # Call the function
        await self.server._handle_message(message)

        # Assertions
        mock_send_response.assert_called_once_with(4, self.server.tools)

    @patch.object(N8nMCPServer, "_execute_tool")
    @patch.object(N8nMCPServer, "_send_response")
    async def test_handle_call_tool(self, mock_send_response, mock_execute_tool):
        """Test handling mcp.callTool method."""
        # Mock the methods
        mock_execute_tool.return_value = {"status": "success", "result": "test_result"}
        mock_send_response.return_value = None

        # Test data
        message = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "mcp.callTool",
            "params": {
                "name": "create_github_issue",
                "arguments": {
                    "title": "Test Issue",
                    "body": "Test Body",
                    "owner": "test_owner",
                    "repo": "test_repo"
                }
            }
        }

        # Call the function
        await self.server._handle_message(message)

        # Assertions
        mock_execute_tool.assert_called_once_with(
            "create_github_issue",
            {
                "title": "Test Issue",
                "body": "Test Body",
                "owner": "test_owner",
                "repo": "test_repo"
            }
        )
        mock_send_response.assert_called_once_with(5, {"status": "success", "result": "test_result"})

    @patch.object(N8nMCPServer, "_send_error")
    async def test_handle_unknown_method(self, mock_send_error):
        """Test handling unknown method."""
        # Mock the send_error method
        mock_send_error.return_value = None

        # Test data
        message = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "unknown_method",
            "params": {}
        }

        # Call the function
        await self.server._handle_message(message)

        # Assertions
        mock_send_error.assert_called_once_with(6, "Unsupported method: unknown_method")

    async def test_execute_tool_create_github_issue(self):
        """Test executing create_github_issue tool."""
        # Test data
        tool_name = "create_github_issue"
        arguments = {
            "title": "Test Issue",
            "body": "Test Body",
            "owner": "test_owner",
            "repo": "test_repo"
        }

        # Call the function
        result = await self.server._execute_tool(tool_name, arguments)

        # Assertions
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["issue_number"], 42)
        self.assertEqual(result["issue_url"], "https://github.com/test_owner/test_repo/issues/42")

    async def test_execute_tool_update_work_package(self):
        """Test executing update_work_package tool."""
        # Test data
        tool_name = "update_work_package"
        arguments = {
            "id": "123",
            "status": "in_progress",
            "description": "Updated description"
        }

        # Call the function
        result = await self.server._execute_tool(tool_name, arguments)

        # Assertions
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["work_package_id"], "123")
        self.assertIn("status", result["updated_fields"])
        self.assertIn("description", result["updated_fields"])

    async def test_execute_tool_sync_documentation(self):
        """Test executing sync_documentation tool."""
        # Test data
        tool_name = "sync_documentation"
        arguments = {
            "doc_id": "doc123",
            "github_path": "docs/README.md",
            "owner": "test_owner",
            "repo": "test_repo"
        }

        # Call the function
        result = await self.server._execute_tool(tool_name, arguments)

        # Assertions
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["doc_id"], "doc123")
        self.assertEqual(result["github_path"], "docs/README.md")
        self.assertEqual(result["commit_sha"], "abc123")

    async def test_execute_tool_unknown(self):
        """Test executing unknown tool."""
        # Test data
        tool_name = "unknown_tool"
        arguments = {}

        # Call the function and check for exception
        with self.assertRaises(ValueError) as context:
            await self.server._execute_tool(tool_name, arguments)

        self.assertEqual(str(context.exception), f"Unknown tool: {tool_name}")


if __name__ == "__main__":
    # Run the async tests
    loop = asyncio.get_event_loop()
    unittest.main()