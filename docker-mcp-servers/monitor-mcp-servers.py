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
Monitor MCP Servers

This script monitors the MCP servers by periodically checking their health and reporting any issues.
"""

import argparse
import json
import logging
import os
import sys
import time
import requests
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp-server-monitor.log')
    ]
)
logger = logging.getLogger('mcp-server-monitor')

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

def check_server_health(server):
    """Check the health of an MCP server."""
    try:
        url = f"{server['url']}/health"
        
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

def check_server_tools(server):
    """Check the tools of an MCP server."""
    try:
        url = f"{server['url']}/mcp"
        
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
                logger.info(f"✅ {server['name']} has {len(tools)} tools available")
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

def monitor_servers(servers, interval=60, notify_url=None):
    """Monitor the MCP servers by periodically checking their health."""
    try:
        logger.info(f"Starting MCP server monitor with interval {interval} seconds")
        
        # Initialize server status
        server_status = {}
        for server in servers:
            server_status[server['name']] = {
                'healthy': False,
                'last_check': None,
                'last_healthy': None,
                'consecutive_failures': 0
            }
        
        while True:
            logger.info(f"=== Monitoring cycle started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            
            healthy_servers = 0
            total_servers = len(servers)
            
            for server in servers:
                server_name = server['name']
                logger.info(f"Checking {server_name} ({server['url']})...")
                
                # Check server health
                is_healthy = check_server_health(server)
                
                # Update server status
                server_status[server_name]['last_check'] = datetime.datetime.now()
                
                if is_healthy:
                    healthy_servers += 1
                    server_status[server_name]['healthy'] = True
                    server_status[server_name]['last_healthy'] = datetime.datetime.now()
                    server_status[server_name]['consecutive_failures'] = 0
                    
                    # Check server tools
                    check_server_tools(server)
                else:
                    server_status[server_name]['healthy'] = False
                    server_status[server_name]['consecutive_failures'] += 1
                    
                    # Send notification if server is down for too long
                    if server_status[server_name]['consecutive_failures'] >= 3 and notify_url:
                        try:
                            notification = {
                                'server_name': server_name,
                                'url': server['url'],
                                'status': 'down',
                                'consecutive_failures': server_status[server_name]['consecutive_failures'],
                                'last_healthy': server_status[server_name]['last_healthy'].isoformat() if server_status[server_name]['last_healthy'] else None,
                                'timestamp': datetime.datetime.now().isoformat()
                            }
                            
                            requests.post(notify_url, json=notification, timeout=5)
                            logger.info(f"Sent notification for {server_name} being down")
                        except Exception as e:
                            logger.error(f"Failed to send notification: {e}")
                
                # Add a small delay between server checks
                time.sleep(1)
            
            # Print summary
            logger.info(f"=== Monitoring cycle completed: {healthy_servers}/{total_servers} servers are healthy ===")
            
            # Wait for the next cycle
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error in monitoring loop: {e}")
        return False
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Monitor MCP Servers")
    parser.add_argument("--config", default="openhands-mcp-config.json", help="Path to the MCP configuration file")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds")
    parser.add_argument("--notify-url", help="URL to send notifications to when a server goes down")
    
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
    
    # Start monitoring
    monitor_servers(servers, args.interval, args.notify_url)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
