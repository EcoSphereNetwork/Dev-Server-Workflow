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
MCP Server Monitor
This script monitors the health of all MCP servers and reports their status.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from tabulate import tabulate
import argparse
import signal

# Define MCP servers
MCP_SERVERS = [
    {"name": "filesystem", "url": "http://localhost:3001", "type": "filesystem"},
    {"name": "desktop-commander", "url": "http://localhost:3002", "type": "desktop"},
    {"name": "sequential-thinking", "url": "http://localhost:3003", "type": "thinking"},
    {"name": "github-chat", "url": "http://localhost:3004", "type": "github"},
    {"name": "github", "url": "http://localhost:3005", "type": "github"},
    {"name": "puppeteer", "url": "http://localhost:3006", "type": "browser"},
    {"name": "basic-memory", "url": "http://localhost:3007", "type": "memory"},
    {"name": "wikipedia", "url": "http://localhost:3008", "type": "knowledge"}
]

# Define colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def check_server_health(server):
    """Check the health of a MCP server"""
    try:
        start_time = time.time()
        response = requests.get(f"{server['url']}/health", timeout=5)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            status = "Healthy"
            color = Colors.GREEN
        else:
            status = f"Unhealthy ({response.status_code})"
            color = Colors.RED
            
        return {
            "name": server["name"],
            "url": server["url"],
            "type": server["type"],
            "status": status,
            "color": color,
            "response_time": f"{response_time:.2f}ms",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except requests.RequestException as e:
        return {
            "name": server["name"],
            "url": server["url"],
            "type": server["type"],
            "status": f"Error: {str(e)[:50]}...",
            "color": Colors.RED,
            "response_time": "N/A",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def check_server_tools(server):
    """Check the available tools on a MCP server"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools",
            "params": {}
        }
        response = requests.post(f"{server['url']}/mcp", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and isinstance(data["result"], list):
                tools = data["result"]
                return {
                    "name": server["name"],
                    "tools_count": len(tools),
                    "tools": [t.get("name", t.get("id", "unknown")) for t in tools]
                }
        
        return {
            "name": server["name"],
            "tools_count": 0,
            "tools": []
        }
    except requests.RequestException:
        return {
            "name": server["name"],
            "tools_count": 0,
            "tools": []
        }

def monitor_servers(servers, continuous=False, interval=30, show_tools=False):
    """Monitor all MCP servers and display their status"""
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Colors.HEADER}{Colors.BOLD}MCP Server Status Monitor{Colors.ENDC}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Monitoring {len(servers)} MCP servers...\n")
            
            # Check health of all servers
            results = []
            for server in servers:
                health = check_server_health(server)
                results.append([
                    f"{health['color']}{health['name']}{Colors.ENDC}",
                    health["type"],
                    f"{health['color']}{health['status']}{Colors.ENDC}",
                    health["response_time"],
                    health["timestamp"]
                ])
            
            # Display results in a table
            headers = ["Server", "Type", "Status", "Response Time", "Timestamp"]
            print(tabulate(results, headers=headers, tablefmt="grid"))
            
            # Check tools if requested
            if show_tools:
                print(f"\n{Colors.HEADER}{Colors.BOLD}MCP Server Tools{Colors.ENDC}")
                tool_results = []
                for server in servers:
                    tools_info = check_server_tools(server)
                    tool_results.append([
                        server["name"],
                        tools_info["tools_count"],
                        ", ".join(tools_info["tools"][:5]) + ("..." if len(tools_info["tools"]) > 5 else "")
                    ])
                
                tool_headers = ["Server", "Tools Count", "Available Tools"]
                print(tabulate(tool_results, headers=tool_headers, tablefmt="grid"))
            
            if not continuous:
                break
                
            print(f"\nRefreshing in {interval} seconds... (Press Ctrl+C to exit)")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped.")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Monitor MCP servers")
    parser.add_argument("-c", "--continuous", action="store_true", help="Run in continuous mode")
    parser.add_argument("-i", "--interval", type=int, default=30, help="Refresh interval in seconds (default: 30)")
    parser.add_argument("-t", "--tools", action="store_true", help="Show available tools")
    args = parser.parse_args()
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    
    monitor_servers(MCP_SERVERS, args.continuous, args.interval, args.tools)

if __name__ == "__main__":
    main()