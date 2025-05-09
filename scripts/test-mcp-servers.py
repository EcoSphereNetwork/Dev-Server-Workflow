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

Dieses Skript testet die MCP-Server, indem es Anfragen an jeden Server sendet und die Antworten überprüft.
Es unterstützt auch das Testen der einzelnen Tools der MCP-Server.
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    # Installiere requests, wenn es nicht verfügbar ist
    import subprocess
    logger.info("Installiere erforderliche Pakete...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp-server-tests.log')
    ]
)
logger = logging.getLogger('mcp-server-tests')

# Farbdefinitionen für die Ausgabe
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Standard-MCP-Server-Konfiguration
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

def colorize(text, color):
    """Färbt den Text in der angegebenen Farbe ein.
    
    Args:
        text: Der zu färbende Text
        color: Die zu verwendende Farbe
        
    Returns:
        Der eingefärbte Text
    """
    return f"{color}{text}{Colors.NC}"

def load_config(config_path):
    """Lädt die MCP-Server-Konfiguration aus einer JSON-Datei.
    
    Args:
        config_path: Pfad zur Konfigurationsdatei
        
    Returns:
        Liste der MCP-Server-Konfigurationen
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                if "mcp" in config and "servers" in config["mcp"]:
                    return config["mcp"]["servers"]
                elif "mcp" in config and "servers" in config["mcp"]:
                    return config["mcp"]["servers"]
        
        logger.warning(f"Konfigurationsdatei nicht gefunden oder ungültig: {config_path}")
        logger.warning("Verwende Standard-MCP-Server-Konfiguration.")
        return DEFAULT_MCP_SERVERS
    
    except Exception as e:
        logger.warning(f"Fehler beim Laden der Konfiguration: {e}")
        logger.warning("Verwende Standard-MCP-Server-Konfiguration.")
        return DEFAULT_MCP_SERVERS

def find_mcp_config_file():
    """Sucht nach der MCP-Konfigurationsdatei im Projektverzeichnis.
    
    Returns:
        Pfad zur Konfigurationsdatei oder None, wenn nicht gefunden
    """
    # Mögliche Konfigurationsdateien
    config_files = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docker-mcp-servers", "openhands-mcp-config.json"),
        os.path.expanduser("~/Dev-Server-Workflow/docker-mcp-servers/openhands-mcp-config.json"),
        "/workspace/Dev-Server-Workflow/docker-mcp-servers/openhands-mcp-config.json",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "openhands-mcp-config.json"),
        os.path.expanduser("~/Dev-Server-Workflow/config/openhands-mcp-config.json"),
        "/workspace/Dev-Server-Workflow/config/openhands-mcp-config.json",
        os.path.expanduser("~/.config/openhands/mcp-config.json"),
        "/workspace/openhands-config/mcp-config.json"
    ]
    
    for config_file in config_files:
        if os.path.isfile(config_file):
            logger.info(f"Gefundene MCP-Konfigurationsdatei: {config_file}")
            return config_file
    
    logger.warning("Keine MCP-Konfigurationsdatei gefunden.")
    return None

def test_server_health(server):
    """Testet die Gesundheit eines MCP-Servers.
    
    Args:
        server: Ein Dictionary mit den Server-Informationen
        
    Returns:
        (success, response_data): Ein Tupel mit einem Bool, der angibt, ob der Test erfolgreich war,
        und den Antwortdaten vom Server
    """
    server_name = server.get("name", "Unbekannter Server")
    server_url = server.get("url", "")
    
    if not server_url:
        logger.error(f"❌ {server_name} hat keine URL.")
        return False, None
    
    logger.info(f"Teste Gesundheit von {server_name} ({server_url})...")
    
    try:
        # Versuche zunächst den /health-Endpunkt
        response = requests.get(f"{inspector_url}/health", timeout=5)
        
        if response.status_code == 200:
            logger.info(colorize(f"✅ MCP Inspector ist gesund!", Colors.GREEN))
            return True
        else:
            logger.error(colorize(f"❌ MCP Inspector ist nicht gesund. Status-Code: {response.status_code}", Colors.RED))
            return False
    
    except requests.exceptions.RequestException as e:
        logger.error(colorize(f"❌ MCP Inspector ist nicht erreichbar: {e}", Colors.RED))
        return False
    except Exception as e:
        logger.error(colorize(f"❌ Unerwarteter Fehler beim Testen des MCP Inspectors: {e}", Colors.RED))
        return False

def test_all_servers(servers, test_tools=False, test_tool_execution=False, verbose=False):
    """Testet alle MCP-Server.
    
    Args:
        servers: Eine Liste von Dictionaries mit den Server-Informationen
        test_tools: Ob die Tools der Server getestet werden sollen
        test_tool_execution: Ob die Ausführung der Tools getestet werden soll
        verbose: Ob detaillierte Ausgaben angezeigt werden sollen
        
    Returns:
        True, wenn alle Tests erfolgreich waren, sonst False
    """
    if not servers:
        logger.error("Keine MCP-Server zum Testen gefunden.")
        return False
    
    logger.info(colorize(f"Teste {len(servers)} MCP-Server...", Colors.BLUE))
    
    healthy_servers = 0
    servers_with_tools = 0
    total_servers = len(servers)
    all_tests_passed = True
    
    for server in servers:
        # Teste die Gesundheit des Servers
        server_healthy, _ = test_server_health(server)
        if server_healthy:
            healthy_servers += 1
            
            # Teste die Tools des Servers, wenn gewünscht
            if test_tools:
                tools_success, tools = test_server_tools(server, verbose)
                
                if tools_success and tools:
                    servers_with_tools += 1
                    
                    # Teste die Ausführung der Tools, wenn gewünscht
                    if test_tool_execution and tools:
                        # Wähle ein Tool zum Testen aus (das erste)
                        test_tool(server, tools[0], verbose)
                
                all_tests_passed = all_tests_passed and tools_success
        
        all_tests_passed = all_tests_passed and server_healthy
        
        # Füge eine leere Zeile zwischen den Server-Tests ein
        logger.info("")
    
    # Teste auch den MCP Inspector
    inspector_healthy = test_inspector()
    all_tests_passed = all_tests_passed and inspector_healthy
    
    # Gib eine Zusammenfassung aus
    logger.info(colorize(f"=== Testergebnisse ===", Colors.BLUE))
    logger.info(f"Gesunde Server: {healthy_servers}/{total_servers}")
    
    if test_tools:
        logger.info(f"Server mit Tools: {servers_with_tools}/{total_servers}")
    
    if all_tests_passed:
        logger.info(colorize("✅ Alle Tests wurden erfolgreich abgeschlossen!", Colors.GREEN))
    else:
        logger.error(colorize("❌ Einige Tests sind fehlgeschlagen.", Colors.RED))
    
    return all_tests_passed

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="Test MCP Servers")
    parser.add_argument("--config", help="Pfad zur MCP-Konfigurationsdatei")
    parser.add_argument("--test-tools", action="store_true", help="Teste die Tools jedes Servers")
    parser.add_argument("--test-execution", action="store_true", help="Teste die Ausführung der Tools")
    parser.add_argument("--server", help="Teste nur den angegebenen Server")
    parser.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    # Finde die MCP-Konfigurationsdatei, wenn nicht angegeben
    config_path = args.config
    if not config_path:
        config_path = find_mcp_config_file()
        if not config_path:
            logger.warning("Keine MCP-Konfigurationsdatei gefunden. Verwende Standard-Konfiguration.")
            config_path = None
    
    # Lade die Server-Konfiguration
    servers = load_config(config_path) if config_path else DEFAULT_MCP_SERVERS
    
    # Filtere die Server, wenn ein bestimmter Server angegeben wurde
    if args.server:
        filtered_servers = []
        for server in servers:
            if server.get("name") == args.server or args.server in server.get("name", ""):
                filtered_servers.append(server)
        
        if not filtered_servers:
            logger.error(f"Server {args.server} nicht in der Konfiguration gefunden.")
            return 1
        
        servers = filtered_servers
    
    # Teste die Server
    success = test_all_servers(
        servers,
        test_tools=args.test_tools,
        test_tool_execution=args.test_execution,
        verbose=args.verbose
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()).get(f"{server_url}/health", timeout=5)
        
        if response.status_code == 200:
            logger.info(colorize(f"✅ {server_name} ist gesund!", Colors.GREEN))
            return True, response.json() if response.headers.get("content-type", "").startswith("application/json") else {"status": "ok"}
        else:
            # Wenn der /health-Endpunkt nicht verfügbar ist, versuche eine mcp.listTools-Anfrage
            logger.warning(f"⚠️ {server_name} hat keinen /health-Endpunkt oder antwortet nicht. Versuche mcp.listTools...")
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "mcp.listTools",
                "params": {}
            }
            
            response = requests.post(f"{server_url}/mcp", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    logger.info(colorize(f"✅ {server_name} ist gesund! (mcp.listTools erfolgreich)", Colors.GREEN))
                    return True, result
                elif "error" in result:
                    logger.error(colorize(f"❌ {server_name} hat einen Fehler zurückgegeben: {result['error'].get('message', 'Unbekannter Fehler')}", Colors.RED))
                    return False, result
            
            logger.error(colorize(f"❌ {server_name} ist nicht gesund. Status-Code: {response.status_code}", Colors.RED))
            return False, None
    
    except requests.exceptions.RequestException as e:
        logger.error(colorize(f"❌ {server_name} ist nicht erreichbar: {e}", Colors.RED))
        return False, None
    except Exception as e:
        logger.error(colorize(f"❌ Unerwarteter Fehler beim Testen von {server_name}: {e}", Colors.RED))
        return False, None

def test_server_tools(server, verbose=False):
    """Testet die Tools eines MCP-Servers.
    
    Args:
        server: Ein Dictionary mit den Server-Informationen
        verbose: Ob detaillierte Ausgaben angezeigt werden sollen
        
    Returns:
        (success, tools): Ein Tupel mit einem Bool, der angibt, ob der Test erfolgreich war,
        und der Liste der verfügbaren Tools
    """
    server_name = server.get("name", "Unbekannter Server")
    server_url = server.get("url", "")
    
    if not server_url:
        logger.error(f"❌ {server_name} hat keine URL.")
        return False, None
    
    logger.info(f"Teste Tools von {server_name} ({server_url})...")
    
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools",
            "params": {}
        }
        
        response = requests.post(f"{server_url}/mcp", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                tools = result["result"]
                tool_count = len(tools)
                
                if tool_count > 0:
                    logger.info(colorize(f"✅ {server_name} hat {tool_count} Tools:", Colors.GREEN))
                    
                    if verbose:
                        for i, tool in enumerate(tools):
                            logger.info(f"  {i+1}. {tool.get('name', 'Unbekanntes Tool')}: {tool.get('description', 'Keine Beschreibung')}")
                    else:
                        # Zeige nur die ersten 5 Tools an
                        for i, tool in enumerate(tools[:5]):
                            logger.info(f"  {i+1}. {tool.get('name', 'Unbekanntes Tool')}")
                        
                        if tool_count > 5:
                            logger.info(f"  ... und {tool_count - 5} weitere Tools")
                    
                    return True, tools
                else:
                    logger.warning(colorize(f"⚠️ {server_name} hat keine Tools.", Colors.YELLOW))
                    return True, []
            elif "error" in result:
                logger.error(colorize(f"❌ {server_name} hat einen Fehler zurückgegeben: {result['error'].get('message', 'Unbekannter Fehler')}", Colors.RED))
                return False, None
        else:
            logger.error(colorize(f"❌ {server_name} hat den Status-Code {response.status_code} zurückgegeben.", Colors.RED))
            return False, None
    
    except requests.exceptions.RequestException as e:
        logger.error(colorize(f"❌ {server_name} ist nicht erreichbar: {e}", Colors.RED))
        return False, None
    except Exception as e:
        logger.error(colorize(f"❌ Unerwarteter Fehler beim Testen der Tools von {server_name}: {e}", Colors.RED))
        return False, None

def test_tool(server, tool, verbose=False):
    """Testet ein bestimmtes Tool eines MCP-Servers.
    
    Args:
        server: Ein Dictionary mit den Server-Informationen
        tool: Ein Dictionary mit den Tool-Informationen
        verbose: Ob detaillierte Ausgaben angezeigt werden sollen
        
    Returns:
        (success, response_data): Ein Tupel mit einem Bool, der angibt, ob der Test erfolgreich war,
        und den Antwortdaten vom Server
    """
    server_name = server.get("name", "Unbekannter Server")
    server_url = server.get("url", "")
    tool_name = tool.get("name", "Unbekanntes Tool")
    
    if not server_url:
        logger.error(f"❌ {server_name} hat keine URL.")
        return False, None
    
    logger.info(f"Teste Tool {tool_name} auf {server_name} ({server_url})...")
    
    try:
        # Erstelle Test-Argumente basierend auf dem Parameter-Schema
        args = {}
        if "parameter_schema" in tool:
            schema = tool["parameter_schema"]
            if "properties" in schema:
                for prop_name, prop_info in schema["properties"].items():
                    if "default" in prop_info:
                        args[prop_name] = prop_info["default"]
                    elif prop_info.get("type") == "string":
                        args[prop_name] = "test_value"
                    elif prop_info.get("type") == "number" or prop_info.get("type") == "integer":
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
                "name": tool_name,
                "arguments": args
            }
        }
        
        if verbose:
            logger.info(f"Anfrage an {server_name} für Tool {tool_name}:")
            logger.info(json.dumps(payload, indent=2))
        
        response = requests.post(f"{server_url}/mcp", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                if verbose:
                    logger.info(f"Antwort von {server_name} für Tool {tool_name}:")
                    logger.info(json.dumps(result["result"], indent=2))
                
                logger.info(colorize(f"✅ Tool {tool_name} wurde erfolgreich ausgeführt auf {server_name}!", Colors.GREEN))
                return True, result["result"]
            elif "error" in result:
                logger.error(colorize(f"❌ Fehler beim Ausführen von Tool {tool_name} auf {server_name}: {result['error'].get('message', 'Unbekannter Fehler')}", Colors.RED))
                return False, result
        else:
            logger.error(colorize(f"❌ {server_name} hat den Status-Code {response.status_code} zurückgegeben.", Colors.RED))
            return False, None
    
    except requests.exceptions.RequestException as e:
        logger.error(colorize(f"❌ {server_name} ist nicht erreichbar: {e}", Colors.RED))
        return False, None
    except Exception as e:
        logger.error(colorize(f"❌ Unerwarteter Fehler beim Testen von Tool {tool_name} auf {server_name}: {e}", Colors.RED))
        return False, None

def test_inspector(inspector_url="http://localhost:8080"):
    """Testet den MCP Inspector.
    
    Args:
        inspector_url: Die URL des MCP Inspectors
        
    Returns:
        True, wenn der Test erfolgreich war, sonst False
    """
    logger.info(f"Teste MCP Inspector ({inspector_url})...")
    
    try:
        response = requests
