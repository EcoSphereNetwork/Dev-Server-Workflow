#!/usr/bin/env python3
"""
Test-Skript für den n8n MCP Server

Dieses Skript testet die Funktionalität des MCP-Servers durch Simulation von MCP-Protokoll-Anfragen.
"""

import json
import subprocess
import sys
import os
import time
from pathlib import Path

def main():
    """Hauptfunktion zum Testen des MCP-Servers."""
    # Finde den Pfad zum MCP-Server
    script_dir = Path(__file__).parent
    mcp_server_path = script_dir / 'n8n-mcp-server.py'
    
    if not mcp_server_path.exists():
        print(f"Error: MCP server script not found at {mcp_server_path}")
        return 1
    
    # Setze Umgebungsvariablen für den Test
    env = os.environ.copy()
    env["N8N_URL"] = os.environ.get("N8N_URL", "http://localhost:5678")
    env["N8N_API_KEY"] = os.environ.get("N8N_API_KEY", "test-api-key")
    
    print(f"Starting MCP server from {mcp_server_path}...")
    
    # Starte den MCP-Server als Subprocess
    process = subprocess.Popen(
        [sys.executable, str(mcp_server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    try:
        # Warte kurz, damit der Server starten kann
        time.sleep(1)
        
        # Sende initialize-Anfrage
        print("Sending initialize request...")
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize"
        }
        process.stdin.write(json.dumps(initialize_request) + "\n")
        process.stdin.flush()
        
        # Lese Antwort
        initialize_response = json.loads(process.stdout.readline())
        print(f"Initialize response: {json.dumps(initialize_response, indent=2)}")
        
        if "result" not in initialize_response or "capabilities" not in initialize_response["result"]:
            print("Error: Failed to initialize MCP server")
            return 1
        
        # Sende listTools-Anfrage
        print("\nSending listTools request...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "mcp.listTools"
        }
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        
        # Lese Antwort
        list_tools_response = json.loads(process.stdout.readline())
        print(f"Available tools: {len(list_tools_response.get('result', []))}")
        for tool in list_tools_response.get("result", []):
            print(f" - {tool.get('name')}: {tool.get('description')}")
        
        # Teste ein Tool
        print("\nTesting tool execution...")
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "mcp.callTool",
            "params": {
                "name": "create_github_issue",
                "arguments": {
                    "title": "Test Issue",
                    "body": "This is a test issue created via MCP",
                    "owner": "EcoSphereNetwork",
                    "repo": "Dev-Server-Workflow"
                }
            }
        }
        process.stdin.write(json.dumps(call_tool_request) + "\n")
        process.stdin.flush()
        
        # Lese Antwort
        call_tool_response = json.loads(process.stdout.readline())
        print(f"Tool execution response: {json.dumps(call_tool_response, indent=2)}")
        
        print("\nMCP server test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error during MCP server test: {str(e)}")
        return 1
    finally:
        # Beende den MCP-Server
        print("Terminating MCP server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    sys.exit(main())