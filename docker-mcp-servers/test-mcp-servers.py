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
Test MCP Servers

This script tests the MCP servers by sending requests to each server and checking the response.
"""

import argparse
import json
import logging
import os
import sys
import time
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp-server-tests.log')
    ]
)
logger = logging.getLogger('mcp-server-tests')

# Default MCP server configuration
DEFAULT_MCP_SERVERS = [
    {
        "name": "filesystem-mcp",
        "url": "http://localhost:3001",
        "description": "File system operations"
    },
    {
        "name": "desktop-commander-mcp",
        "url": "http://localhost:3002",
        "description": "Terminal command execution"
    },
    {
        "name": "sequential-thinking-mcp",
        "url": "http://localhost:3003",
        "description": "Structured problem-solving"
    },
    {
        "name": "github-chat-mcp",
        "url": "http://localhost:3004",
        "description": "GitHub discussions interaction"
    },
    {
        "name": "github-mcp",
        "url": "http://localhost:3005",
        "description": "GitHub repository management"
    },
    {
        "name": "puppeteer-mcp",
        "url": "http://localhost:3006",
        "description": "Web browsing and interaction"
    },
    {
        "name": "basic-memory-mcp",
        "url": "http://localhost:3007",
        "description": "Simple key-value storage"
    },
    {
        "name": "wikipedia-mcp",
        "url": "http://localhost:3008",
        "description": "Wikipedia search"
    }
]

def test_server_health(server):
    """Test the health of an MCP server."""
    try:
        url = f"{server['url']}/health"
        logger.info(f"Testing health of {server['name']} at {url}...")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"✅ {server['name']} is healthy!")
            return True
        else:
            logger.error(f"❌ {server['name']} returned status code {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ {server['name']} connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ {server['name']} unexpected error: {e}")
        return False

def test_server_tools(server):
    """Test the tools of an MCP server."""
    try:
        url = f"{server['url']}/mcp"
        logger.info(f"Testing tools of {server['name']} at {url}...")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools",
            "params": {}
        }
        
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                tools = result["result"]
                logger.info(f"✅ {server['name']} has {len(tools)} tools:")
                for tool in tools:
                    logger.info(f"  - {tool.get('name', 'unnamed')}: {tool.get('description', 'no description')}")
                return True, tools
            elif "error" in result:
                logger.error(f"❌ {server['name']} returned an error: {result['error'].get('message', 'unknown error')}")
                return False, None
            else:
                logger.error(f"❌ {server['name']} returned an unexpected response: {result}")
                return False, None
        else:
            logger.error(f"❌ {server['name']} returned status code {response.status_code}")
            return False, None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ {server['name']} connection error: {e}")
        return False, None
    except Exception as e:
        logger.error(f"❌ {server['name']} unexpected error: {e}")
        return False, None

def test_tool(server, tool):
    """Test a specific tool on an MCP server."""
    try:
        url = f"{server['url']}/mcp"
        logger.info(f"Testing tool {tool['name']} on {server['name']}...")
        
        # Create test arguments based on the parameter schema
        args = {}
        if "parameter_schema" in tool:
            schema = tool["parameter_schema"]
            if "properties" in schema:
                for prop_name, prop_info in schema["properties"].items():
                    if "default" in prop_info:
                        args[prop_name] = prop_info["default"]
                    elif prop_info.get("type") == "string":
                        args[prop_name] = "test"
                    elif prop_info.get("type") == "number":
                        args[prop_name] = 1
                    elif prop_info.get("type") == "boolean":
                        args[prop_name] = True
                    elif prop_info.get("type") == "array":
                        args[prop_name] = []
                    elif prop_info.get("type") == "object":
                        args[prop_name] = {}
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.callTool",
            "params": {
                "name": tool["name"],
                "arguments": args
            }
        }
        
        logger.info(f"Calling tool with arguments: {args}")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                logger.info(f"✅ Tool {tool['name']} executed successfully!")
                return True, result["result"]
            elif "error" in result:
                logger.error(f"❌ Tool {tool['name']} returned an error: {result['error'].get('message', 'unknown error')}")
                return False, None
            else:
                logger.error(f"❌ Tool {tool['name']} returned an unexpected response: {result}")
                return False, None
        else:
            logger.error(f"❌ Tool {tool['name']} returned status code {response.status_code}")
            return False, None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Tool {tool['name']} connection error: {e}")
        return False, None
    except Exception as e:
        logger.error(f"❌ Tool {tool['name']} unexpected error: {e}")
        return False, None

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test MCP Servers")
    parser.add_argument("--config", default="openhands-mcp-config.json", help="Path to the MCP configuration file")
    parser.add_argument("--test-tools", action="store_true", help="Test the tools of each server")
    parser.add_argument("--server", help="Test only the specified server")
    
    args = parser.parse_args()
    
    # Load the MCP server configuration
    servers = DEFAULT_MCP_SERVERS
    if os.path.exists(args.config):
        try:
            with open(args.config, "r") as f:
                config = json.load(f)
                if "mcp" in config and "servers" in config["mcp"]:
                    servers = config["mcp"]["servers"]
        except Exception as e:
            logger.warning(f"Failed to load configuration from {args.config}: {e}")
    
    # Filter servers if a specific server was specified
    if args.server:
        servers = [s for s in servers if s["name"] == args.server]
        if not servers:
            logger.error(f"Server {args.server} not found in configuration")
            return 1
    
    # Test each server
    healthy_servers = 0
    total_servers = len(servers)
    
    for server in servers:
        logger.info(f"Testing server: {server['name']} ({server['url']})")
        
        # Test server health
        if test_server_health(server):
            healthy_servers += 1
            
            # Test server tools
            if args.test_tools:
                success, tools = test_server_tools(server)
                if success and tools:
                    # Test the first tool
                    if tools:
                        test_tool(server, tools[0])
        
        logger.info("")  # Add a blank line between server tests
    
    # Print summary
    logger.info(f"Summary: {healthy_servers}/{total_servers} MCP servers are healthy")
    
    if healthy_servers == total_servers:
        logger.info("All MCP servers are healthy! 🎉")
        return 0
    else:
        logger.warning("Some MCP servers are not healthy. Please check the logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
