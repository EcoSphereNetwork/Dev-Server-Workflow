#!/usr/bin/env python3

"""
Test script for MCP servers.

This script tests the functionality of MCP servers by sending requests to them
and verifying the responses.
"""

import os
import sys
import json
import asyncio
import argparse
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Add the directory of the common library to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Import the common library
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Configure logging
logger = setup_logging("INFO")

# Initialize configuration manager
config_manager = ConfigManager()

# Load environment variables
env_config = config_manager.load_env_config()

# Default MCP server configuration
DEFAULT_MCP_SERVERS = {
    "n8n-mcp": {
        "url": f"http://localhost:{env_config.get('N8N_MCP_PORT', '3456')}",
        "description": "n8n Workflow Automation"
    },
    "openhands-mcp": {
        "url": f"http://localhost:{env_config.get('OPENHANDS_MCP_PORT', '3457')}",
        "description": "OpenHands AI Agent"
    },
    "docker-mcp": {
        "url": f"http://localhost:{env_config.get('DOCKER_MCP_PORT', '3458')}",
        "description": "Docker Container Management"
    }
}

async def test_server_health(session: aiohttp.ClientSession, server_name: str, server_url: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Test the health of an MCP server.
    
    Args:
        session: aiohttp ClientSession
        server_name: Name of the server
        server_url: URL of the server
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: (Success, Health data)
    """
    try:
        # Try the health endpoint
        async with session.get(f"{server_url}/health", timeout=5) as response:
            if response.status == 200:
                health_data = await response.json()
                logger.info(f"✅ {server_name} health check successful")
                return True, health_data
            else:
                logger.warning(f"⚠️ {server_name} health check failed with status {response.status}")
                return False, None
    except Exception as e:
        logger.error(f"❌ {server_name} health check error: {e}")
        return False, None

async def test_server_info(session: aiohttp.ClientSession, server_name: str, server_url: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Test getting server information from an MCP server.
    
    Args:
        session: aiohttp ClientSession
        server_name: Name of the server
        server_url: URL of the server
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: (Success, Server info)
    """
    try:
        # Send a getServerInfo request
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.getServerInfo"
        }
        
        async with session.post(f"{server_url}/mcp", json=payload, timeout=5) as response:
            if response.status == 200:
                result = await response.json()
                if "result" in result:
                    logger.info(f"✅ {server_name} getServerInfo successful")
                    return True, result["result"]
                elif "error" in result:
                    logger.error(f"❌ {server_name} getServerInfo error: {result['error']['message']}")
                    return False, None
            else:
                logger.error(f"❌ {server_name} getServerInfo failed with status {response.status}")
                return False, None
    except Exception as e:
        logger.error(f"❌ {server_name} getServerInfo error: {e}")
        return False, None

async def test_list_tools(session: aiohttp.ClientSession, server_name: str, server_url: str) -> Tuple[bool, Optional[List[Dict[str, Any]]]]:
    """
    Test listing tools from an MCP server.
    
    Args:
        session: aiohttp ClientSession
        server_name: Name of the server
        server_url: URL of the server
        
    Returns:
        Tuple[bool, Optional[List[Dict[str, Any]]]]: (Success, Tools)
    """
    try:
        # Send a listTools request
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools"
        }
        
        async with session.post(f"{server_url}/mcp", json=payload, timeout=5) as response:
            if response.status == 200:
                result = await response.json()
                if "result" in result:
                    tools = result["result"]
                    logger.info(f"✅ {server_name} listTools successful: {len(tools)} tools available")
                    return True, tools
                elif "error" in result:
                    logger.error(f"❌ {server_name} listTools error: {result['error']['message']}")
                    return False, None
            else:
                logger.error(f"❌ {server_name} listTools failed with status {response.status}")
                return False, None
    except Exception as e:
        logger.error(f"❌ {server_name} listTools error: {e}")
        return False, None

async def test_call_tool(session: aiohttp.ClientSession, server_name: str, server_url: str, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Test calling a tool from an MCP server.
    
    Args:
        session: aiohttp ClientSession
        server_name: Name of the server
        server_url: URL of the server
        tool_name: Name of the tool
        arguments: Arguments for the tool
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: (Success, Result)
    """
    try:
        # Send a callTool request
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.callTool",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        logger.info(f"Testing tool {tool_name} on {server_name} with arguments: {json.dumps(arguments)}")
        
        async with session.post(f"{server_url}/mcp", json=payload, timeout=10) as response:
            if response.status == 200:
                result = await response.json()
                if "result" in result:
                    logger.info(f"✅ Tool {tool_name} executed successfully")
                    return True, result["result"]
                elif "error" in result:
                    logger.error(f"❌ Tool {tool_name} error: {result['error']['message']}")
                    return False, None
            else:
                logger.error(f"❌ Tool {tool_name} failed with status {response.status}")
                return False, None
    except Exception as e:
        logger.error(f"❌ Tool {tool_name} error: {e}")
        return False, None

async def test_server(session: aiohttp.ClientSession, server_name: str, server_url: str, test_tools: bool = False) -> Dict[str, Any]:
    """
    Test an MCP server.
    
    Args:
        session: aiohttp ClientSession
        server_name: Name of the server
        server_url: URL of the server
        test_tools: Whether to test tools
        
    Returns:
        Dict[str, Any]: Test results
    """
    results = {
        "name": server_name,
        "url": server_url,
        "health": False,
        "info": False,
        "tools": False,
        "tool_tests": []
    }
    
    # Test health
    health_success, health_data = await test_server_health(session, server_name, server_url)
    results["health"] = health_success
    results["health_data"] = health_data
    
    # Test server info
    info_success, server_info = await test_server_info(session, server_name, server_url)
    results["info"] = info_success
    results["server_info"] = server_info
    
    # Test list tools
    tools_success, tools = await test_list_tools(session, server_name, server_url)
    results["tools"] = tools_success
    results["tools_data"] = tools
    
    # Test tools if requested and available
    if test_tools and tools_success and tools:
        for tool in tools:
            tool_name = tool["name"]
            
            # Create example arguments based on the parameter schema
            args = {}
            if "parameter_schema" in tool:
                schema = tool["parameter_schema"]
                if "properties" in schema:
                    for prop_name, prop_info in schema["properties"].items():
                        if "default" in prop_info:
                            args[prop_name] = prop_info["default"]
                        elif prop_info.get("type") == "string":
                            args[prop_name] = "test"
                        elif prop_info.get("type") == "number" or prop_info.get("type") == "integer":
                            args[prop_name] = 1
                        elif prop_info.get("type") == "boolean":
                            args[prop_name] = True
                        elif prop_info.get("type") == "array":
                            args[prop_name] = []
                        elif prop_info.get("type") == "object":
                            args[prop_name] = {}
            
            # Test the tool
            tool_success, tool_result = await test_call_tool(session, server_name, server_url, tool_name, args)
            
            results["tool_tests"].append({
                "name": tool_name,
                "success": tool_success,
                "arguments": args,
                "result": tool_result
            })
    
    return results

async def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="Test MCP servers")
    parser.add_argument("--config", default=None, help="Path to the MCP configuration file")
    parser.add_argument("--server", help="Name of the server to test")
    parser.add_argument("--test-tools", action="store_true", help="Test tools")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", help="Output file for test results (JSON format)")
    parser.add_argument("--retry", type=int, default=3, help="Number of retries for failed tests")
    parser.add_argument("--retry-delay", type=int, default=1, help="Delay between retries in seconds")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for requests in seconds")
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logger.setLevel("DEBUG")
    
    # Load server configuration
    servers = DEFAULT_MCP_SERVERS
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
                if "mcp" in config and "servers" in config["mcp"]:
                    servers = config["mcp"]["servers"]
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    # Filter servers if specified
    if args.server:
        if args.server in servers:
            servers = {args.server: servers[args.server]}
        else:
            logger.error(f"Server {args.server} not found in configuration")
            return 1
    
    # Test servers
    async with aiohttp.ClientSession() as session:
        results = []
        
        for server_name, server_config in servers.items():
            server_url = server_config["url"]
            logger.info(f"Testing server {server_name} at {server_url}")
            
            # Try multiple times if requested
            for attempt in range(args.retry):
                try:
                    result = await test_server(session, server_name, server_url, args.test_tools)
                    results.append(result)
                    break
                except Exception as e:
                    if attempt < args.retry - 1:
                        logger.warning(f"Error testing server {server_name}, retrying in {args.retry_delay} seconds: {e}")
                        await asyncio.sleep(args.retry_delay)
                    else:
                        logger.error(f"Error testing server {server_name}: {e}")
                        results.append({
                            "name": server_name,
                            "url": server_url,
                            "health": False,
                            "info": False,
                            "tools": False,
                            "error": str(e)
                        })
        
        # Print summary
        print("\nTest Results:")
        print("=============")
        
        for result in results:
            print(f"\nServer: {result['name']} ({result['url']})")
            print(f"  Health: {'✅' if result.get('health', False) else '❌'}")
            print(f"  Info: {'✅' if result.get('info', False) else '❌'}")
            print(f"  Tools: {'✅' if result.get('tools', False) else '❌'}")
            
            if "error" in result:
                print(f"  Error: {result['error']}")
            
            if "tools_data" in result and result["tools_data"]:
                print(f"  Available Tools: {len(result['tools_data'])}")
                for tool in result["tools_data"]:
                    print(f"    - {tool['name']}: {tool['description']}")
            
            if "tool_tests" in result and result["tool_tests"]:
                print(f"  Tool Tests:")
                for tool_test in result["tool_tests"]:
                    print(f"    - {tool_test['name']}: {'✅' if tool_test['success'] else '❌'}")
        
        # Determine overall success
        success = all(result.get("health", False) and result.get("info", False) and result.get("tools", False) for result in results)
        
        print(f"\nOverall: {'✅ All tests passed' if success else '❌ Some tests failed'}")
        
        # Save results to file if requested
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    json.dump({
                        "timestamp": asyncio.get_event_loop().time(),
                        "servers": results,
                        "success": success
                    }, f, indent=2)
                logger.info(f"Test results saved to {args.output}")
            except Exception as e:
                logger.error(f"Error saving test results: {e}")
        
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))