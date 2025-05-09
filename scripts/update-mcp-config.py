#!/usr/bin/env python3

"""
MCP Server Configuration Updater

Dieses Skript aktualisiert die MCP-Server-Konfiguration für OpenHands und andere Komponenten.
"""

import os
import sys
import json
import argparse
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

def load_config(config_path):
    """Lädt die MCP-Server-Konfiguration aus einer JSON-Datei."""
    try:
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {"mcp": {"servers": {}}}
    except Exception as e:
        logger.error(f"Fehler beim Laden der Konfiguration: {e}")
        return {"mcp": {"servers": {}}}

def save_config(config_path, config_data):
    """Speichert die MCP-Server-Konfiguration in einer JSON-Datei."""
    try:
        # Stelle sicher, dass das Verzeichnis existiert
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Konfiguration erfolgreich gespeichert: {config_path}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
        return False

def update_openhands_config(config_path, mcp_servers):
    """Aktualisiert die OpenHands-Konfiguration mit den MCP-Servern."""
    try:
        # Lade die bestehende Konfiguration
        config_data = load_config(config_path)
        
        # Stelle sicher, dass die MCP-Konfiguration existiert
        if "mcp" not in config_data:
            config_data["mcp"] = {}
        
        # Aktualisiere die Server-Konfiguration
        config_data["mcp"]["servers"] = mcp_servers
        
        # Speichere die aktualisierte Konfiguration
        return save_config(config_path, config_data)
    except Exception as e:
        logger.error(f"Fehler bei der Aktualisierung der OpenHands-Konfiguration: {e}")
        return False

def get_default_mcp_servers():
    """Gibt die Standard-MCP-Server-Konfiguration zurück."""
    # Lade Umgebungsvariablen für die Ports
    n8n_mcp_port = config.get("N8N_MCP_PORT", "3456")
    openhands_mcp_port = config.get("OPENHANDS_MCP_PORT", "3457")
    docker_mcp_port = config.get("DOCKER_MCP_PORT", "3458")
    
    return {
        "n8n-mcp": {
            "url": f"http://localhost:{n8n_mcp_port}",
            "description": "n8n Workflow Automation"
        },
        "openhands-mcp": {
            "url": f"http://localhost:{openhands_mcp_port}",
            "description": "OpenHands AI Agent"
        },
        "docker-mcp": {
            "url": f"http://localhost:{docker_mcp_port}",
            "description": "Docker Container Management"
        }
    }

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="MCP Server Configuration Updater")
    parser.add_argument("--config", default="/workspace/Dev-Server-Workflow/docker-mcp-servers/openhands-mcp-config.json", help="Pfad zur MCP-Konfigurationsdatei")
    parser.add_argument("--openhands-config", default=None, help="Pfad zur OpenHands-Konfigurationsdatei")
    parser.add_argument("--add-server", nargs=3, metavar=("NAME", "URL", "DESCRIPTION"), action="append", help="Fügt einen MCP-Server hinzu")
    parser.add_argument("--remove-server", metavar="NAME", action="append", help="Entfernt einen MCP-Server")
    parser.add_argument("--list", action="store_true", help="Listet alle konfigurierten MCP-Server auf")
    parser.add_argument("--reset", action="store_true", help="Setzt die Konfiguration auf die Standardwerte zurück")
    
    args = parser.parse_args()
    
    # Lade die bestehende Konfiguration
    config_data = load_config(args.config)
    
    # Stelle sicher, dass die MCP-Konfiguration existiert
    if "mcp" not in config_data:
        config_data["mcp"] = {}
    if "servers" not in config_data["mcp"]:
        config_data["mcp"]["servers"] = {}
    
    # Verarbeite Kommandozeilenargumente
    if args.reset:
        logger.info("Setze Konfiguration auf Standardwerte zurück")
        config_data["mcp"]["servers"] = get_default_mcp_servers()
    
    if args.add_server:
        for server in args.add_server:
            name, url, description = server
            logger.info(f"Füge MCP-Server hinzu: {name} ({url})")
            config_data["mcp"]["servers"][name] = {
                "url": url,
                "description": description
            }
    
    if args.remove_server:
        for name in args.remove_server:
            if name in config_data["mcp"]["servers"]:
                logger.info(f"Entferne MCP-Server: {name}")
                del config_data["mcp"]["servers"][name]
            else:
                logger.warning(f"MCP-Server nicht gefunden: {name}")
    
    # Speichere die aktualisierte Konfiguration
    save_config(args.config, config_data)
    
    # Aktualisiere die OpenHands-Konfiguration, falls angegeben
    if args.openhands_config:
        update_openhands_config(args.openhands_config, config_data["mcp"]["servers"])
    
    # Liste alle konfigurierten MCP-Server auf
    if args.list or not (args.add_server or args.remove_server or args.reset):
        print("Konfigurierte MCP-Server:")
        for name, server in config_data["mcp"]["servers"].items():
            print(f"  {name}:")
            print(f"    URL: {server['url']}")
            print(f"    Beschreibung: {server['description']}")
            print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())