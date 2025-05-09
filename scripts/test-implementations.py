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
Automatisierte Tests für MCP-Server-Implementierungen

Dieses Skript testet beide MCP-Server-Implementierungen (docker-mcp-ecosystem und docker-mcp-servers)
und stellt sicher, dass sie korrekt funktionieren.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import requests
from pathlib import Path

# Konfiguration des Loggings
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test-implementations')

# Farbdefinitionen für die Ausgabe
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def run_command(command, cwd=None, env=None):
    """Führt einen Befehl aus und gibt das Ergebnis zurück."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env
        )
        return True, result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode('utf-8')

def test_docker_installation():
    """Testet, ob Docker installiert ist."""
    logger.info("Teste Docker-Installation...")
    success, output = run_command("docker --version")
    if success:
        logger.info(f"{Colors.GREEN}✅ Docker ist installiert: {output.strip()}{Colors.NC}")
        return True
    else:
        logger.error(f"{Colors.RED}❌ Docker ist nicht installiert oder nicht verfügbar{Colors.NC}")
        return False

def test_docker_compose_installation():
    """Testet, ob Docker Compose installiert ist."""
    logger.info("Teste Docker Compose-Installation...")
    success, output = run_command("docker-compose --version")
    if success:
        logger.info(f"{Colors.GREEN}✅ Docker Compose ist installiert: {output.strip()}{Colors.NC}")
        return True
    else:
        # Versuche es mit dem neuen Docker Compose-Plugin
        success, output = run_command("docker compose version")
        if success:
            logger.info(f"{Colors.GREEN}✅ Docker Compose Plugin ist installiert: {output.strip()}{Colors.NC}")
            return True
        else:
            logger.error(f"{Colors.RED}❌ Docker Compose ist nicht installiert oder nicht verfügbar{Colors.NC}")
            return False

def test_implementation(implementation_dir, start_script, stop_script):
    """Testet eine MCP-Server-Implementierung."""
    logger.info(f"{Colors.BLUE}Teste Implementierung in {implementation_dir}...{Colors.NC}")
    
    # Prüfe, ob die Verzeichnisse und Skripte existieren
    if not os.path.isdir(implementation_dir):
        logger.error(f"{Colors.RED}❌ Verzeichnis {implementation_dir} existiert nicht{Colors.NC}")
        return False
    
    start_script_path = os.path.join(implementation_dir, start_script)
    stop_script_path = os.path.join(implementation_dir, stop_script)
    
    if not os.path.isfile(start_script_path):
        logger.error(f"{Colors.RED}❌ Start-Skript {start_script_path} existiert nicht{Colors.NC}")
        return False
    
    if not os.path.isfile(stop_script_path):
        logger.error(f"{Colors.RED}❌ Stopp-Skript {stop_script_path} existiert nicht{Colors.NC}")
        return False
    
    # Stoppe die Implementierung, falls sie bereits läuft
    logger.info(f"Stoppe vorherige Instanz...")
    run_command(f"bash {stop_script_path}", cwd=implementation_dir)
    
    # Starte die Implementierung
    logger.info(f"Starte Implementierung...")
    success, output = run_command(f"bash {start_script_path}", cwd=implementation_dir)
    if not success:
        logger.error(f"{Colors.RED}❌ Implementierung konnte nicht gestartet werden: {output}{Colors.NC}")
        return False
    
    # Warte, bis die Container gestartet sind
    logger.info(f"Warte auf den Start der Container...")
    time.sleep(30)
    
    # Teste die MCP-Server
    logger.info(f"Teste MCP-Server...")
    mcp_servers = [
        {"name": "filesystem", "port": 3001},
        {"name": "desktop-commander", "port": 3002},
        {"name": "sequential-thinking", "port": 3003},
        {"name": "github-chat", "port": 3004},
        {"name": "github", "port": 3005},
        {"name": "puppeteer", "port": 3006},
        {"name": "basic-memory", "port": 3007},
        {"name": "wikipedia", "port": 3008}
    ]
    
    all_servers_healthy = True
    
    for server in mcp_servers:
        try:
            response = requests.get(f"http://localhost:{server['port']}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"{Colors.GREEN}✅ MCP-Server {server['name']} ist gesund{Colors.NC}")
            else:
                logger.error(f"{Colors.RED}❌ MCP-Server {server['name']} ist nicht gesund: {response.status_code}{Colors.NC}")
                all_servers_healthy = False
        except requests.RequestException as e:
            logger.error(f"{Colors.RED}❌ MCP-Server {server['name']} ist nicht erreichbar: {e}{Colors.NC}")
            all_servers_healthy = False
    
    # Teste den MCP Inspector
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            logger.info(f"{Colors.GREEN}✅ MCP Inspector ist gesund{Colors.NC}")
        else:
            logger.error(f"{Colors.RED}❌ MCP Inspector ist nicht gesund: {response.status_code}{Colors.NC}")
            all_servers_healthy = False
    except requests.RequestException as e:
        logger.error(f"{Colors.RED}❌ MCP Inspector ist nicht erreichbar: {e}{Colors.NC}")
        all_servers_healthy = False
    
    # Teste n8n, falls vorhanden
    try:
        response = requests.get("http://localhost:5678/healthz", timeout=5)
        if response.status_code == 200:
            logger.info(f"{Colors.GREEN}✅ n8n ist gesund{Colors.NC}")
        else:
            logger.warning(f"{Colors.YELLOW}⚠️ n8n ist nicht gesund: {response.status_code}{Colors.NC}")
    except requests.RequestException as e:
        logger.warning(f"{Colors.YELLOW}⚠️ n8n ist nicht erreichbar: {e}{Colors.NC}")
    
    # Stoppe die Implementierung
    logger.info(f"Stoppe Implementierung...")
    run_command(f"bash {stop_script_path}", cwd=implementation_dir)
    
    if all_servers_healthy:
        logger.info(f"{Colors.GREEN}✅ Implementierung in {implementation_dir} wurde erfolgreich getestet{Colors.NC}")
        return True
    else:
        logger.error(f"{Colors.RED}❌ Implementierung in {implementation_dir} hat Fehler{Colors.NC}")
        return False

def test_mcp_tools(implementation_dir, start_script, stop_script):
    """Testet die MCP-Tools einer Implementierung."""
    logger.info(f"{Colors.BLUE}Teste MCP-Tools in {implementation_dir}...{Colors.NC}")
    
    # Starte die Implementierung
    logger.info(f"Starte Implementierung...")
    success, output = run_command(f"bash {start_script_path}", cwd=implementation_dir)
    if not success:
        logger.error(f"{Colors.RED}❌ Implementierung konnte nicht gestartet werden: {output}{Colors.NC}")
        return False
    
    # Warte, bis die Container gestartet sind
    logger.info(f"Warte auf den Start der Container...")
    time.sleep(30)
    
    # Teste die MCP-Tools
    logger.info(f"Teste MCP-Tools...")
    mcp_servers = [
        {"name": "filesystem", "port": 3001},
        {"name": "desktop-commander", "port": 3002},
        {"name": "sequential-thinking", "port": 3003},
        {"name": "github-chat", "port": 3004},
        {"name": "github", "port": 3005},
        {"name": "puppeteer", "port": 3006},
        {"name": "basic-memory", "port": 3007},
        {"name": "wikipedia", "port": 3008}
    ]
    
    all_tools_working = True
    
    for server in mcp_servers:
        try:
            # Rufe die verfügbaren Tools ab
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "mcp.listTools",
                "params": {}
            }
            response = requests.post(f"http://localhost:{server['port']}/mcp", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and isinstance(data["result"], list):
                    tools = data["result"]
                    logger.info(f"{Colors.GREEN}✅ MCP-Server {server['name']} hat {len(tools)} Tools: {', '.join(t.get('name', t.get('id', 'unknown')) for t in tools)}{Colors.NC}")
                else:
                    logger.warning(f"{Colors.YELLOW}⚠️ MCP-Server {server['name']} hat keine Tools oder ungültiges Format{Colors.NC}")
            else:
                logger.error(f"{Colors.RED}❌ MCP-Server {server['name']} konnte Tools nicht auflisten: {response.status_code}{Colors.NC}")
                all_tools_working = False
        except requests.RequestException as e:
            logger.error(f"{Colors.RED}❌ MCP-Server {server['name']} ist nicht erreichbar: {e}{Colors.NC}")
            all_tools_working = False
    
    # Stoppe die Implementierung
    logger.info(f"Stoppe Implementierung...")
    run_command(f"bash {stop_script_path}", cwd=implementation_dir)
    
    if all_tools_working:
        logger.info(f"{Colors.GREEN}✅ MCP-Tools in {implementation_dir} wurden erfolgreich getestet{Colors.NC}")
        return True
    else:
        logger.error(f"{Colors.RED}❌ MCP-Tools in {implementation_dir} haben Fehler{Colors.NC}")
        return False

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="Automatisierte Tests für MCP-Server-Implementierungen")
    parser.add_argument("--ecosystem", action="store_true", help="Teste die Ecosystem-Implementierung")
    parser.add_argument("--servers", action="store_true", help="Teste die Servers-Implementierung")
    parser.add_argument("--tools", action="store_true", help="Teste die MCP-Tools")
    parser.add_argument("--ecosystem-dir", default="docker-mcp-ecosystem", help="Verzeichnis für die Ecosystem-Implementierung")
    parser.add_argument("--servers-dir", default="docker-mcp-servers", help="Verzeichnis für die Servers-Implementierung")
    
    args = parser.parse_args()
    
    # Wenn keine spezifischen Tests angegeben wurden, teste beide Implementierungen
    if not args.ecosystem and not args.servers:
        args.ecosystem = True
        args.servers = True
    
    # Teste die Voraussetzungen
    if not test_docker_installation() or not test_docker_compose_installation():
        logger.error(f"{Colors.RED}❌ Voraussetzungen nicht erfüllt{Colors.NC}")
        return 1
    
    # Teste die Implementierungen
    ecosystem_success = True
    servers_success = True
    
    if args.ecosystem:
        ecosystem_success = test_implementation(
            args.ecosystem_dir,
            "start-mcp-ecosystem.sh",
            "stop-mcp-ecosystem.sh"
        )
        
        if args.tools and ecosystem_success:
            ecosystem_success = test_mcp_tools(
                args.ecosystem_dir,
                "start-mcp-ecosystem.sh",
                "stop-mcp-ecosystem.sh"
            )
    
    if args.servers:
        servers_success = test_implementation(
            args.servers_dir,
            "start-mcp-servers.sh",
            "stop-mcp-servers.sh"
        )
        
        if args.tools and servers_success:
            servers_success = test_mcp_tools(
                args.servers_dir,
                "start-mcp-servers.sh",
                "stop-mcp-servers.sh"
            )
    
    # Zeige das Gesamtergebnis an
    if args.ecosystem and args.servers:
        if ecosystem_success and servers_success:
            logger.info(f"{Colors.GREEN}✅ Alle Tests wurden erfolgreich abgeschlossen{Colors.NC}")
            return 0
        elif ecosystem_success:
            logger.error(f"{Colors.RED}❌ Tests für die Servers-Implementierung sind fehlgeschlagen{Colors.NC}")
            return 1
        elif servers_success:
            logger.error(f"{Colors.RED}❌ Tests für die Ecosystem-Implementierung sind fehlgeschlagen{Colors.NC}")
            return 1
        else:
            logger.error(f"{Colors.RED}❌ Alle Tests sind fehlgeschlagen{Colors.NC}")
            return 1
    elif args.ecosystem:
        if ecosystem_success:
            logger.info(f"{Colors.GREEN}✅ Tests für die Ecosystem-Implementierung wurden erfolgreich abgeschlossen{Colors.NC}")
            return 0
        else:
            logger.error(f"{Colors.RED}❌ Tests für die Ecosystem-Implementierung sind fehlgeschlagen{Colors.NC}")
            return 1
    elif args.servers:
        if servers_success:
            logger.info(f"{Colors.GREEN}✅ Tests für die Servers-Implementierung wurden erfolgreich abgeschlossen{Colors.NC}")
            return 0
        else:
            logger.error(f"{Colors.RED}❌ Tests für die Servers-Implementierung sind fehlgeschlagen{Colors.NC}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())