#!/usr/bin/env python3

"""
MCP Server Monitor

Dieses Skript überwacht die MCP-Server und stellt sicher, dass sie ordnungsgemäß funktionieren.
Es sendet regelmäßig Anfragen an die Server und protokolliert die Ergebnisse.
"""

import os
import sys
import json
import time
import argparse
import logging
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Konfiguriere Logging
logger = setup_logging("INFO", "mcp-monitor.log")

# Lade Konfiguration
config_manager = ConfigManager()
config = config_manager.load_env_file(".env")

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

async def check_server_health(session, server_name, server_url):
    """Überprüft den Gesundheitszustand eines MCP-Servers."""
    try:
        # Versuche zuerst den Gesundheitsendpunkt
        try:
            async with session.get(f"{server_url}/health", timeout=5) as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"✅ {server_name} Gesundheitscheck erfolgreich!")
                else:
                    logger.warning(f"⚠️ {server_name} Gesundheitscheck fehlgeschlagen, versuche listTools...")
        except Exception:
            logger.warning(f"⚠️ {server_name} Gesundheitsendpunkt nicht verfügbar, versuche listTools...")
        
        # Sende eine listTools-Anfrage an den Server
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools",
            "params": {}
        }
        
        async with session.post(f"{server_url}/mcp", json=payload, timeout=5) as response:
            if response.status == 200:
                result = await response.json()
                if "result" in result:
                    tools = result["result"]
                    logger.info(f"✅ {server_name} ist gesund! {len(tools)} Tools verfügbar.")
                    return True, tools
                elif "error" in result:
                    logger.error(f"❌ {server_name} hat einen Fehler zurückgegeben: {result['error']['message']}")
                    return False, None
            else:
                logger.error(f"❌ {server_name} hat den Status-Code {response.status} zurückgegeben.")
                return False, None
    
    except asyncio.TimeoutError:
        logger.error(f"❌ {server_name} Timeout bei der Verbindung.")
        return False, None
    except Exception as e:
        logger.error(f"❌ {server_name} unerwarteter Fehler: {e}")
        return False, None

async def test_tool(session, server_name, server_url, tool_name, args):
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
        
        async with session.post(f"{server_url}/mcp", json=payload, timeout=10) as response:
            if response.status == 200:
                result = await response.json()
                if "result" in result:
                    logger.info(f"✅ Tool {tool_name} erfolgreich ausgeführt!")
                    return True, result["result"]
                elif "error" in result:
                    logger.error(f"❌ Tool {tool_name} hat einen Fehler zurückgegeben: {result['error']['message']}")
                    return False, None
            else:
                logger.error(f"❌ Tool {tool_name} hat den Status-Code {response.status} zurückgegeben.")
                return False, None
    
    except asyncio.TimeoutError:
        logger.error(f"❌ Tool {tool_name} Timeout bei der Verbindung.")
        return False, None
    except Exception as e:
        logger.error(f"❌ Tool {tool_name} unerwarteter Fehler: {e}")
        return False, None

async def monitor_servers(servers, interval=60, test_tools=False):
    """Überwacht die MCP-Server in regelmäßigen Abständen."""
    logger.info(f"Starte Überwachung von {len(servers)} MCP-Servern mit Intervall {interval} Sekunden.")
    
    # Erstelle eine Session für alle HTTP-Anfragen
    async with aiohttp.ClientSession() as session:
        try:
            while True:
                logger.info(f"=== Überwachungszyklus gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
                
                healthy_servers = 0
                for server_name, server_config in servers.items():
                    server_url = server_config["url"]
                    logger.info(f"Überprüfe {server_name} ({server_url})...")
                    
                    healthy, tools = await check_server_health(session, server_name, server_url)
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
                            await test_tool(session, server_name, server_url, tool_name, args)
                    
                    # Kurze Pause zwischen den Server-Checks
                    await asyncio.sleep(1)
                
                logger.info(f"=== Überwachungszyklus abgeschlossen: {healthy_servers}/{len(servers)} Server sind gesund ===")
                
                # Warte bis zum nächsten Zyklus
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("Überwachung wurde durch Benutzer beendet.")
        except Exception as e:
            logger.error(f"Unerwarteter Fehler bei der Überwachung: {e}")
            return False
    
    return True

async def restart_server(server_name):
    """Startet einen MCP-Server neu."""
    logger.info(f"Starte Server {server_name} neu...")
    
    # Stoppe den Server
    stop_script = BASE_DIR / "scripts" / "stop-all-mcp-servers.sh"
    if not stop_script.exists():
        logger.error(f"Stopp-Skript nicht gefunden: {stop_script}")
        return False
    
    process = await asyncio.create_subprocess_exec(
        str(stop_script), f"--{server_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        logger.error(f"Fehler beim Stoppen des Servers: {stderr.decode()}")
        return False
    
    # Warte einen Moment
    await asyncio.sleep(2)
    
    # Starte den Server
    start_script = BASE_DIR / "scripts" / "start-all-mcp-servers.sh"
    if not start_script.exists():
        logger.error(f"Start-Skript nicht gefunden: {start_script}")
        return False
    
    process = await asyncio.create_subprocess_exec(
        str(start_script), f"--{server_name}", "--http",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        logger.error(f"Fehler beim Starten des Servers: {stderr.decode()}")
        return False
    
    logger.info(f"Server {server_name} erfolgreich neu gestartet")
    return True

async def check_server_status(server_name, server_url):
    """Überprüft den Status eines MCP-Servers und gibt detaillierte Informationen zurück."""
    async with aiohttp.ClientSession() as session:
        try:
            # Versuche den Gesundheitsendpunkt
            try:
                async with session.get(f"{server_url}/health", timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        logger.info(f"Server {server_name} ist online")
                        return {
                            "status": "online",
                            "uptime": health_data.get("uptime", "unbekannt"),
                            "version": health_data.get("version", "unbekannt"),
                            "name": health_data.get("name", server_name)
                        }
            except Exception:
                pass
            
            # Versuche die Server-Informationen abzurufen
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "mcp.getServerInfo",
                "params": {}
            }
            
            async with session.post(f"{server_url}/mcp", json=payload, timeout=5) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        server_info = result["result"]
                        logger.info(f"Server {server_name} ist online")
                        return {
                            "status": "online",
                            "uptime": server_info.get("uptime", "unbekannt"),
                            "version": server_info.get("version", "unbekannt"),
                            "name": server_info.get("name", server_name),
                            "tools_count": server_info.get("tools_count", "unbekannt"),
                            "request_count": server_info.get("request_count", "unbekannt")
                        }
            
            # Wenn wir hier ankommen, ist der Server nicht erreichbar
            logger.warning(f"Server {server_name} ist nicht erreichbar")
            return {
                "status": "offline",
                "error": "Server nicht erreichbar"
            }
        
        except Exception as e:
            logger.error(f"Fehler bei der Überprüfung des Servers {server_name}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

async def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="MCP Server Monitor")
    parser.add_argument("--config", default="/workspace/Dev-Server-Workflow/docker-mcp-servers/openhands-mcp-config.json", help="Pfad zur MCP-Konfigurationsdatei")
    parser.add_argument("--interval", type=int, default=60, help="Überwachungsintervall in Sekunden")
    parser.add_argument("--test-tools", action="store_true", help="Teste auch die Tools der Server")
    parser.add_argument("--restart", help="Starte einen bestimmten Server neu")
    parser.add_argument("--status", help="Zeige den Status eines bestimmten Servers an")
    parser.add_argument("--all-status", action="store_true", help="Zeige den Status aller Server an")
    parser.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    # Setze Log-Level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Lade die Server-Konfiguration
    servers = load_config(args.config)
    
    if not servers:
        logger.error("Keine MCP-Server in der Konfiguration gefunden.")
        return 1
    
    # Verarbeite Kommandozeilenargumente
    if args.restart:
        server_name = args.restart
        if server_name not in servers:
            logger.error(f"Server {server_name} nicht gefunden.")
            return 1
        
        success = await restart_server(server_name)
        return 0 if success else 1
    
    if args.status:
        server_name = args.status
        if server_name not in servers:
            logger.error(f"Server {server_name} nicht gefunden.")
            return 1
        
        server_url = servers[server_name]["url"]
        status = await check_server_status(server_name, server_url)
        
        print(f"Status des Servers {server_name}:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        return 0
    
    if args.all_status:
        print("Status aller MCP-Server:")
        for server_name, server_config in servers.items():
            server_url = server_config["url"]
            status = await check_server_status(server_name, server_url)
            
            print(f"\nServer {server_name} ({server_url}):")
            for key, value in status.items():
                print(f"  {key}: {value}")
        
        return 0
    
    # Starte die Überwachung
    success = await monitor_servers(servers, args.interval, args.test_tools)
    
    return 0 if success else 1

if __name__ == "__main__":
    asyncio.run(main())