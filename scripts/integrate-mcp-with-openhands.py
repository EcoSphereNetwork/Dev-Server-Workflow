#!/usr/bin/env python3
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
    """Erstellt eine OpenHands-Konfigurationsdatei für die MCP-Server."""
    try:
        # Erstelle die Konfiguration
        config = {
            "mcp": {
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
                    "sync_documentation"
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
        
        # Schreibe die Konfiguration in eine Datei
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✅ OpenHands-Konfigurationsdatei wurde erfolgreich erstellt: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Erstellen der OpenHands-Konfigurationsdatei: {e}")
        return False

def copy_config_to_openhands(source_path, openhands_config_dir):
    """Kopiert die Konfigurationsdatei in das OpenHands-Konfigurationsverzeichnis."""
    try:
        # Erstelle das Zielverzeichnis, falls es nicht existiert
        os.makedirs(openhands_config_dir, exist_ok=True)
        
        # Kopiere die Datei
        target_path = os.path.join(openhands_config_dir, "mcp-config.json")
        shutil.copy2(source_path, target_path)
        
        logger.info(f"✅ Konfigurationsdatei wurde erfolgreich nach {target_path} kopiert.")
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Kopieren der Konfigurationsdatei: {e}")
        return False

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="MCP-Server OpenHands Integration")
    parser.add_argument("--output", default="/workspace/Dev-Server-Workflow/docker-mcp-servers/openhands-mcp-config.json", help="Pfad zur Ausgabedatei")
    parser.add_argument("--openhands-config-dir", help="Pfad zum OpenHands-Konfigurationsverzeichnis")
    parser.add_argument("--github-token", help="GitHub-Token für die GitHub-MCP-Server")
    
    args = parser.parse_args()
    
    # Erstelle die OpenHands-Konfigurationsdatei
    if not create_openhands_config(args.output, DEFAULT_MCP_SERVERS, args.github_token):
        logger.error("OpenHands-Konfigurationsdatei konnte nicht erstellt werden.")
        return 1
    
    # Kopiere die Konfigurationsdatei in das OpenHands-Konfigurationsverzeichnis, falls angegeben
    if args.openhands_config_dir:
        if not copy_config_to_openhands(args.output, args.openhands_config_dir):
            logger.error("Konfigurationsdatei konnte nicht in das OpenHands-Konfigurationsverzeichnis kopiert werden.")
            return 1
    
    logger.info("✅ MCP-Server wurden erfolgreich mit OpenHands integriert!")
    logger.info(f"Die Konfigurationsdatei wurde erstellt: {args.output}")
    
    if not args.openhands_config_dir:
        logger.info("Um die Integration abzuschließen, kopieren Sie die Konfigurationsdatei in Ihr OpenHands-Konfigurationsverzeichnis:")
        logger.info(f"  cp {args.output} /path/to/openhands/config/mcp-config.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())