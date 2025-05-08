"""
Docker MCP Server module.

This module provides a Model Context Protocol (MCP) server for Docker operations,
enabling AI agents to manage Docker containers and Docker Compose stacks.
"""

from .server import main

__all__ = ["main"]