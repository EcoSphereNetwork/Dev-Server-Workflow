#!/usr/bin/env python3
"""
MCP-Server OpenHands Konfigurationsgenerator

Dieses Skript generiert eine OpenHands-Konfigurationsdatei für die MCP-Server
basierend auf der aktuellen Docker-Compose-Konfiguration.
"""

import argparse
import json
import os
import re
import sys
import yaml
import toml
from pathlib import Path

# Konfiguration des Loggings
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('generate-openhands-config')

def load_docker_compose(compose_file):
    """Lädt die Docker-Compose-Konfiguration."""
    try:
        with open(compose_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden der Docker-Compose-Datei: {e}")
        return None

def extract_mcp_servers(compose_config):
    """Extrahiert die MCP-Server aus der Docker-Compose-Konfiguration."""
    mcp_servers = []
    
    if not compose_config or 'services' not in compose_config:
        return mcp_servers
    
    for service_name, service_config in compose_config['services'].items():
        # Prüfe, ob es sich um einen MCP-Server handelt
        if service_name.startswith('mcp-') or 'mcp' in service_name.lower():
            # Extrahiere Port aus der Konfiguration
            port = None
            if 'ports' in service_config:
                for port_mapping in service_config['ports']:
                    match = re.search(r'(\d+):(\d+)', str(port_mapping))
                    if match:
                        port = match.group(2)
                        break
            
            if port:
                mcp_servers.append({
                    'name': service_name,
                    'url': f"http://{service_name}:{port}/mcp",
                    'description': service_config.get('environment', {}).get('DESCRIPTION', f"{service_name} MCP server")
                })
    
    return mcp_servers

def generate_openhands_config(mcp_servers, template_file, output_file, github_token=None):
    """Generiert die OpenHands-Konfigurationsdatei."""
    try:
        # Lade die Vorlage
        with open(template_file, 'r') as f:
            config = toml.load(f)
        
        # Aktualisiere die MCP-Server-Konfiguration
        if 'mcp' not in config:
            config['mcp'] = {}
        
        # Setze die SSE-Server
        config['mcp']['sse_servers'] = [server['url'] for server in mcp_servers]
        
        # Aktualisiere die GitHub-Token in den stdio_servers
        if github_token and 'stdio_servers' in config['mcp']:
            for server in config['mcp']['stdio_servers']:
                if 'env' in server and 'GITHUB_TOKEN' in server['env']:
                    server['env']['GITHUB_TOKEN'] = github_token
        
        # Schreibe die Konfiguration in eine Datei
        with open(output_file, 'w') as f:
            toml.dump(config, f)
        
        logger.info(f"✅ OpenHands-Konfigurationsdatei wurde erfolgreich erstellt: {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Erstellen der OpenHands-Konfigurationsdatei: {e}")
        return False

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="MCP-Server OpenHands Konfigurationsgenerator")
    parser.add_argument("--compose", default="docker-compose.yml", help="Pfad zur Docker-Compose-Datei")
    parser.add_argument("--template", default="openhands-config.toml", help="Pfad zur OpenHands-Konfigurationsvorlage")
    parser.add_argument("--output", default="openhands-config-generated.toml", help="Pfad zur Ausgabedatei")
    parser.add_argument("--github-token", help="GitHub-Token für die GitHub-MCP-Server")
    
    args = parser.parse_args()
    
    # Lade die Docker-Compose-Konfiguration
    compose_config = load_docker_compose(args.compose)
    if not compose_config:
        logger.error("Docker-Compose-Konfiguration konnte nicht geladen werden.")
        return 1
    
    # Extrahiere die MCP-Server
    mcp_servers = extract_mcp_servers(compose_config)
    if not mcp_servers:
        logger.warning("Keine MCP-Server in der Docker-Compose-Konfiguration gefunden.")
    else:
        logger.info(f"Gefundene MCP-Server: {', '.join(server['name'] for server in mcp_servers)}")
    
    # Generiere die OpenHands-Konfigurationsdatei
    if not generate_openhands_config(mcp_servers, args.template, args.output, args.github_token):
        logger.error("OpenHands-Konfigurationsdatei konnte nicht erstellt werden.")
        return 1
    
    logger.info(f"✅ MCP-Server wurden erfolgreich für OpenHands konfiguriert!")
    logger.info(f"Die Konfigurationsdatei wurde erstellt: {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())