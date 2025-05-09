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
MCP-Server OpenHands Integration

Dieses Skript integriert die MCP-Server mit OpenHands, indem es die erforderliche
Konfigurationsdatei erstellt und in das OpenHands-Konfigurationsverzeichnis kopiert.
"""

import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp-openhands-integration.log')
    ]
)
logger = logging.getLogger('mcp-openhands-integration')

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

def create_openhands_config(output_path, mcp_servers, github_token=None):
    """Erstellt eine OpenHands-Konfigurationsdatei für die MCP-Server.
    
    Args:
        output_path: Pfad zur Ausgabedatei
        mcp_servers: Liste der MCP-Server-Konfigurationen
        github_token: GitHub-Token für die GitHub-MCP-Server (optional)
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Erstelle die Konfiguration
        config = {
            "mcp": {
                "enabled": True,
                "servers": mcp_servers,
                "autoApproveTools": True,
                "autoApproveToolsList": [
                    "read_file",
                    "write_file",
                    "list_directory",
                    "execute_command",
                    "search_wikipedia",
                    "create_github_issue",
                    "create_github_pr",
                    "update_work_package",
                    "sync_documentation",
                    "capture_screenshot",
                    "browse_website",
                    "scrape_content",
                    "remember_information",
                    "recall_information"
                ]
            }
        }
        
        # Füge GitHub-Token hinzu, wenn vorhanden
        if github_token:
            for server in config["mcp"]["servers"]:
                if "github" in server["name"]:
                    server["auth"] = {
                        "type": "token",
                        "token": github_token
                    }
        
        # Erstelle das Verzeichnis, falls es nicht existiert
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Schreibe die Konfiguration in eine Datei
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✅ OpenHands-Konfigurationsdatei wurde erfolgreich erstellt: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Erstellen der OpenHands-Konfigurationsdatei: {e}")
        return False

def copy_config_to_openhands(source_path, openhands_config_dir):
    """Kopiert die Konfigurationsdatei in das OpenHands-Konfigurationsverzeichnis.
    
    Args:
        source_path: Pfad zur Quelldatei
        openhands_config_dir: Pfad zum OpenHands-Konfigurationsverzeichnis
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Erstelle das Zielverzeichnis, falls es nicht existiert
        os.makedirs(openhands_config_dir, exist_ok=True)
        
        # Kopiere die Datei
        target_path = os.path.join(openhands_config_dir, "mcp-config.json")
        shutil.copy2(source_path, target_path)
        
        logger.info(f"✅ Konfigurationsdatei wurde erfolgreich nach {target_path} kopiert.")
        
        # Erstelle auch ein Start-Skript für OpenHands
        create_openhands_start_script(openhands_config_dir)
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Kopieren der Konfigurationsdatei: {e}")
        return False

def create_openhands_start_script(openhands_config_dir):
    """Erstellt ein Start-Skript für OpenHands.
    
    Args:
        openhands_config_dir: Pfad zum OpenHands-Konfigurationsverzeichnis
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Pfad zum Start-Skript
        start_script_path = os.path.join(openhands_config_dir, "start-mcp-servers.sh")
        
        # Inhalt des Start-Skripts
        script_content = """#!/bin/bash

# Script to start the MCP servers for OpenHands

# Change to the MCP servers directory
MCP_DIR="$HOME/Dev-Server-Workflow/docker-mcp-servers"
WORKSPACE_MCP_DIR="/workspace/Dev-Server-Workflow/docker-mcp-servers"

if [ -d "$MCP_DIR" ]; then
    cd "$MCP_DIR"
    echo "Using MCP directory: $MCP_DIR"
elif [ -d "$WORKSPACE_MCP_DIR" ]; then
    cd "$WORKSPACE_MCP_DIR"
    echo "Using MCP directory: $WORKSPACE_MCP_DIR"
else
    echo "MCP directory not found. Please provide the correct path."
    echo "Usage: $0 [path/to/mcp-servers]"
    
    if [ -n "$1" ] && [ -d "$1" ]; then
        cd "$1"
        echo "Using provided MCP directory: $1"
    else
        echo "Error: MCP directory not found."
        exit 1
    fi
fi

# Start the MCP servers
./start-mcp-servers.sh

# Wait for the servers to start
echo "Waiting for the MCP servers to start..."
sleep 5

# Test the MCP servers
if [ -f "./test-mcp-servers.py" ]; then
    echo "Testing the MCP servers..."
    python3 ./test-mcp-servers.py
else
    echo "Test script not found. Skipping tests."
fi

echo "MCP servers are ready for OpenHands!"
"""
        
        # Schreibe das Start-Skript
        with open(start_script_path, 'w') as f:
            f.write(script_content)
        
        # Mache das Skript ausführbar
        os.chmod(start_script_path, 0o755)
        
        logger.info(f"✅ Start-Skript wurde erfolgreich erstellt: {start_script_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Erstellen des Start-Skripts: {e}")
        return False

def detect_openhands_config_dir():
    """Versucht, das OpenHands-Konfigurationsverzeichnis automatisch zu erkennen.
    
    Returns:
        Pfad zum OpenHands-Konfigurationsverzeichnis oder None, wenn nicht gefunden
    """
    # Mögliche Standardpfade
    standard_paths = [
        os.path.expanduser("~/.config/openhands"),
        os.path.expanduser("~/.openhands"),
        "/workspace/openhands-config",
        os.path.expanduser("~/openhands-config")
    ]
    
    # Prüfe auch Umgebungsvariablen
    env_paths = []
    for env_var in ["OPENHANDS_CONFIG_DIR", "OPENHANDS_CONFIG", "OPENHANDS_DIR"]:
        if env_var in os.environ:
            env_paths.append(os.environ[env_var])
    
    # Prüfe alle Pfade
    for path in env_paths + standard_paths:
        if os.path.isdir(path):
            logger.info(f"Gefundenes OpenHands-Konfigurationsverzeichnis: {path}")
            return path
    
    # Versuche, nach einer OpenHands-Installation zu suchen
    for openhands_dir in ["openhands", ".openhands", "OpenHands", ".OpenHands"]:
        for root_dir in [os.path.expanduser("~"), "/workspace", "/opt", "/usr/local"]:
            path = os.path.join(root_dir, openhands_dir)
            config_path = os.path.join(path, "config")
            
            if os.path.isdir(config_path):
                logger.info(f"Gefundenes OpenHands-Konfigurationsverzeichnis: {config_path}")
                return config_path
    
    logger.warning("Konnte das OpenHands-Konfigurationsverzeichnis nicht automatisch erkennen.")
    return None

def find_docker_mcp_servers_dir():
    """Versucht, das Verzeichnis mit den MCP-Servern zu finden.
    
    Returns:
        Pfad zum MCP-Server-Verzeichnis oder None, wenn nicht gefunden
    """
    # Mögliche Standardpfade
    standard_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docker-mcp-servers"),
        os.path.expanduser("~/Dev-Server-Workflow/docker-mcp-servers"),
        "/workspace/Dev-Server-Workflow/docker-mcp-servers",
        "/opt/Dev-Server-Workflow/docker-mcp-servers"
    ]
    
    # Prüfe alle Pfade
    for path in standard_paths:
        if os.path.isdir(path):
            logger.info(f"Gefundenes MCP-Server-Verzeichnis: {path}")
            return path
    
    # Versuche, es in übergeordneten Verzeichnissen zu finden
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):  # Maximum 5 Verzeichnisebenen nach oben
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Wurzelverzeichnis erreicht
            break
        
        potential_path = os.path.join(parent_dir, "docker-mcp-servers")
        if os.path.isdir(potential_path):
            logger.info(f"Gefundenes MCP-Server-Verzeichnis: {potential_path}")
            return potential_path
        
        current_dir = parent_dir
    
    logger.warning("Konnte das MCP-Server-Verzeichnis nicht automatisch finden.")
    return None

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="MCP-Server OpenHands Integration")
    parser.add_argument("--config", help="Pfad zur Ausgabekonfigurationsdatei", 
                        default=None)
    parser.add_argument("--openhands-config-dir", help="Pfad zum OpenHands-Konfigurationsverzeichnis",
                        default=None)
    parser.add_argument("--github-token", help="GitHub-Token für die GitHub-MCP-Server")
    parser.add_argument("--docker-mcp-dir", help="Pfad zum MCP-Server-Verzeichnis",
                        default=None)
    
    args = parser.parse_args()
    
    # Finde das MCP-Server-Verzeichnis, wenn nicht angegeben
    docker_mcp_dir = args.docker_mcp_dir
    if not docker_mcp_dir:
        docker_mcp_dir = find_docker_mcp_servers_dir()
    
    # Bestimme den Pfad zur Konfigurationsdatei
    config_path = args.config
    if not config_path:
        if docker_mcp_dir:
            config_path = os.path.join(docker_mcp_dir, "openhands-mcp-config.json")
        else:
            config_path = "openhands-mcp-config.json"
    
    # Erstelle die OpenHands-Konfigurationsdatei
    if not create_openhands_config(config_path, DEFAULT_MCP_SERVERS, args.github_token):
        logger.error("OpenHands-Konfigurationsdatei konnte nicht erstellt werden.")
        return 1
    
    # Finde das OpenHands-Konfigurationsverzeichnis, wenn nicht angegeben
    openhands_config_dir = args.openhands_config_dir
    if not openhands_config_dir:
        openhands_config_dir = detect_openhands_config_dir()
    
    # Kopiere die Konfigurationsdatei in das OpenHands-Konfigurationsverzeichnis, falls angegeben
    if openhands_config_dir:
        if not copy_config_to_openhands(config_path, openhands_config_dir):
            logger.error("Konfigurationsdatei konnte nicht in das OpenHands-Konfigurationsverzeichnis kopiert werden.")
            return 1
    else:
        logger.warning("OpenHands-Konfigurationsverzeichnis nicht angegeben oder gefunden.")
        logger.warning("Die Konfigurationsdatei wurde erstellt, aber nicht in das OpenHands-Konfigurationsverzeichnis kopiert.")
        logger.warning(f"Die Konfigurationsdatei befindet sich hier: {config_path}")
        logger.warning("Um die Integration abzuschließen, kopieren Sie die Konfigurationsdatei in das OpenHands-Konfigurationsverzeichnis:")
        logger.warning(f"  cp {config_path} /path/to/openhands/config/mcp-config.json")
    
    logger.info("✅ MCP-Server wurden erfolgreich mit OpenHands integriert!")
    logger.info(f"Die Konfigurationsdatei wurde erstellt: {config_path}")
    
    if openhands_config_dir:
        logger.info(f"Die Konfigurationsdatei wurde in das OpenHands-Konfigurationsverzeichnis kopiert: {openhands_config_dir}")
        logger.info("Ein Start-Skript wurde erstellt, um die MCP-Server zu starten:")
        logger.info(f"  {os.path.join(openhands_config_dir, 'start-mcp-servers.sh')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
