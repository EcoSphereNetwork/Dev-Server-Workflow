#!/usr/bin/env python3

import requests
import json
import sys
import time

def test_mcp_server(server_name, url):
    """Test an MCP server by sending a listTools request."""
    print(f"Testing {server_name} at {url}...")
    
    try:
        # Prepare the JSON-RPC request
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools",
            "params": {}
        }
        
        # Send the request
        response = requests.post(f"{url}/mcp", json=payload, timeout=5)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                tools = result["result"]
                print(f"✅ {server_name} is working! Available tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
                return True
            elif "error" in result:
                print(f"❌ {server_name} returned an error: {result['error']['message']}")
                return False
        else:
            print(f"❌ {server_name} returned status code {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ {server_name} connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ {server_name} unexpected error: {e}")
        return False

def main():
    # Load the OpenHands MCP configuration
    try:
        with open("openhands-mcp-config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Get the MCP servers from the configuration
    servers = config.get("mcp", {}).get("servers", {})
    if not servers:
        print("No MCP servers found in the configuration.")
        sys.exit(1)
    
    # Test each MCP server
    success_count = 0
    total_count = len(servers)
    
    for server_name, server_config in servers.items():
        url = server_config.get("url")
        if url:
            if test_mcp_server(server_name, url):
                success_count += 1
            print()  # Add a blank line between server tests
            time.sleep(1)  # Add a small delay between tests
        else:
            print(f"❌ {server_name} has no URL configured.")
    
    # Print summary
    print(f"Summary: {success_count}/{total_count} MCP servers are working.")
    
    if success_count == total_count:
        print("All MCP servers are working correctly! 🎉")
        sys.exit(0)
    else:
        print("Some MCP servers are not working. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()