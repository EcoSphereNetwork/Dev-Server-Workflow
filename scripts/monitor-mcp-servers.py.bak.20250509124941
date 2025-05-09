#!/usr/bin/env python3
"""
MCP Server Monitor

Dieses Skript überwacht die MCP-Server und stellt sicher, dass sie ordnungsgemäß funktionieren.
Es sendet regelmäßig Anfragen an die Server und protokolliert die Ergebnisse.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
import requests

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp-monitor.log')
    ]
)
logger = logging.getLogger('mcp-monitor')

# Standard-MCP-Server-Konfiguration
DEFAULT_MCP_SERVERS = {
    "filesystem-mcp": {"url": "http://localhost:3001", "description": "File system operations"},
    "desktop-commander-mcp": {"url": "http://localhost:3002", "description": "Terminal command execution"},
    "sequential-thinking-mcp": {"url": "http://localhost:3003", "description": "Structured problem-solving"},
    "github-chat-mcp": {"url": "http://localhost:3004", "description": "GitHub discussions interaction"},
    "github-mcp": {"url": "http://localhost:3005", "description": "GitHub repository management"},
    "puppeteer-mcp": {"url": "http://localhost:3006", "description": "Web browsing and interaction"},
    "basic-memory-mcp": {"url": "http://localhost:3007", "description": "Simple key-value storage"},
    "wikipedia-mcp": {"url": "http://localhost:3008", "description": "Wikipedia search"}
}

def load_config(config_path):
    """Lädt die MCP-Server-Konfiguration aus einer JSON-Datei."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('mcp', {}).get('servers', DEFAULT_MCP_SERVERS)
    except Exception as e:
        logger.warning(f"Fehler beim Laden der Konfiguration: {e}")
        return DEFAULT_MCP_SERVERS

def check_server_health(server_name, server_url):
    """Überprüft den Gesundheitszustand eines MCP-Servers."""
    try:
        # Sende eine listTools-Anfrage an den Server
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools",
            "params": {}
        }
        
        response = requests.post(f"{server_url}/mcp", json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                tools = result["result"]
                logger.info(f"✅ {server_name} ist gesund! {len(tools)} Tools verfügbar.")
                return True, tools
            elif "error" in result:
                logger.error(f"❌ {server_name} hat einen Fehler zurückgegeben: {result['error']['message']}")
                return False, None
        else:
            logger.error(f"❌ {server_name} hat den Status-Code {response.status_code} zurückgegeben.")
            return False, None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ {server_name} Verbindungsfehler: {e}")
        return False, None
    except Exception as e:
        logger.error(f"❌ {server_name} unerwarteter Fehler: {e}")
        return False, None

def test_tool(server_name, server_url, tool_name, args):
    """Testet ein bestimmtes Tool auf einem MCP-Server."""
    try:
        # Sende eine callTool-Anfrage an den Server
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.callTool",
            "params": {
                "name": tool_name,
                "arguments": args
            }
        }
        
        logger.info(f"Teste Tool {tool_name} auf {server_name} mit Argumenten: {args}")
        response = requests.post(f"{server_url}/mcp", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                logger.info(f"✅ Tool {tool_name} erfolgreich ausgeführt!")
                return True, result["result"]
            elif "error" in result:
                logger.error(f"❌ Tool {tool_name} hat einen Fehler zurückgegeben: {result['error']['message']}")
                return False, None
        else:
            logger.error(f"❌ Tool {tool_name} hat den Status-Code {response.status_code} zurückgegeben.")
            return False, None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Tool {tool_name} Verbindungsfehler: {e}")
        return False, None
    except Exception as e:
        logger.error(f"❌ Tool {tool_name} unerwarteter Fehler: {e}")
        return False, None

def monitor_servers(servers, interval=60, test_tools=False):
    """Überwacht die MCP-Server in regelmäßigen Abständen."""
    logger.info(f"Starte Überwachung von {len(servers)} MCP-Servern mit Intervall {interval} Sekunden.")
    
    try:
        while True:
            logger.info(f"=== Überwachungszyklus gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            
            healthy_servers = 0
            for server_name, server_config in servers.items():
                server_url = server_config["url"]
                logger.info(f"Überprüfe {server_name} ({server_url})...")
                
                healthy, tools = check_server_health(server_name, server_url)
                if healthy:
                    healthy_servers += 1
                    
                    # Teste ein Tool, wenn gewünscht und Tools verfügbar sind
                    if test_tools and tools and len(tools) > 0:
                        # Wähle das erste Tool für den Test
                        tool = tools[0]
                        tool_name = tool["name"]
                        
                        # Erstelle leere Argumente oder Beispielargumente basierend auf dem Schema
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
                        
                        # Teste das Tool
                        test_tool(server_name, server_url, tool_name, args)
                
                # Kurze Pause zwischen den Server-Checks
                time.sleep(1)
            
            logger.info(f"=== Überwachungszyklus abgeschlossen: {healthy_servers}/{len(servers)} Server sind gesund ===")
            
            # Warte bis zum nächsten Zyklus
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logger.info("Überwachung wurde durch Benutzer beendet.")
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei der Überwachung: {e}")
        return False
    
    return True

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="MCP Server Monitor")
    parser.add_argument("--config", default="/workspace/Dev-Server-Workflow/docker-mcp-servers/openhands-mcp-config.json", help="Pfad zur MCP-Konfigurationsdatei")
    parser.add_argument("--interval", type=int, default=60, help="Überwachungsintervall in Sekunden")
    parser.add_argument("--test-tools", action="store_true", help="Teste auch die Tools der Server")
    
    args = parser.parse_args()
    
    # Lade die Server-Konfiguration
    servers = load_config(args.config)
    
    if not servers:
        logger.error("Keine MCP-Server in der Konfiguration gefunden.")
        return 1
    
    # Starte die Überwachung
    success = monitor_servers(servers, args.interval, args.test_tools)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())