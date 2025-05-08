#!/usr/bin/env python3
"""
MCP-Server n8n Integration

Dieses Skript integriert die MCP-Server mit n8n, indem es die Workflows importiert
und die Umgebungsvariablen konfiguriert.
"""

import argparse
import json
import logging
import os
import sys
import time
import requests
import subprocess

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp-n8n-integration.log')
    ]
)
logger = logging.getLogger('mcp-n8n-integration')

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

def load_config(config_path):
    """Lädt die MCP-Server-Konfiguration aus einer JSON-Datei."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('mcp', {}).get('servers', DEFAULT_MCP_SERVERS)
    except Exception as e:
        logger.warning(f"Fehler beim Laden der Konfiguration: {e}")
        return DEFAULT_MCP_SERVERS

def create_n8n_environment_variables(n8n_url, n8n_api_key, mcp_servers):
    """Erstellt Umgebungsvariablen in n8n für die MCP-Server."""
    try:
        # Erstelle die MCP_SERVERS_CONFIG-Variable
        mcp_servers_config = {
            "servers": mcp_servers
        }
        
        # Konvertiere die Konfiguration in einen JSON-String
        mcp_servers_config_json = json.dumps(mcp_servers_config)
        
        # Erstelle die Umgebungsvariable in n8n
        headers = {
            "X-N8N-API-KEY": n8n_api_key,
            "Content-Type": "application/json"
        }
        
        # Überprüfe, ob die Variable bereits existiert
        response = requests.get(
            f"{n8n_url}/api/v1/variables",
            headers=headers
        )
        
        if response.status_code == 200:
            variables = response.json()
            for variable in variables["data"]:
                if variable["key"] == "MCP_SERVERS_CONFIG":
                    # Variable existiert bereits, aktualisiere sie
                    logger.info("MCP_SERVERS_CONFIG-Variable existiert bereits, aktualisiere sie...")
                    response = requests.patch(
                        f"{n8n_url}/api/v1/variables/{variable['id']}",
                        headers=headers,
                        json={"value": mcp_servers_config_json}
                    )
                    
                    if response.status_code in (200, 201):
                        logger.info("✅ MCP_SERVERS_CONFIG-Variable wurde erfolgreich aktualisiert.")
                        return True
                    else:
                        logger.error(f"❌ Fehler beim Aktualisieren der Variable: {response.status_code} - {response.text}")
                        return False
        
        # Variable existiert nicht, erstelle sie
        payload = {
            "key": "MCP_SERVERS_CONFIG",
            "value": mcp_servers_config_json
        }
        
        response = requests.post(
            f"{n8n_url}/api/v1/variables",
            headers=headers,
            json=payload
        )
        
        if response.status_code in (200, 201):
            logger.info("✅ MCP_SERVERS_CONFIG-Umgebungsvariable wurde erfolgreich erstellt.")
            return True
        else:
            logger.error(f"❌ Fehler beim Erstellen der Umgebungsvariable: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler beim Erstellen der Umgebungsvariablen: {e}")
        return False

def import_workflows(n8n_api_key):
    """Importiert die Workflows in n8n."""
    try:
        # Führe das Import-Skript aus
        import_script = "/workspace/Dev-Server-Workflow/scripts/import-workflows.py"
        result = subprocess.run(
            [import_script, "--n8n-api-key", n8n_api_key],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Workflows wurden erfolgreich importiert.")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"❌ Fehler beim Importieren der Workflows: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler beim Importieren der Workflows: {e}")
        return False

def test_mcp_integration(n8n_url):
    """Testet die Integration der MCP-Server mit n8n."""
    try:
        # Sende eine Testanfrage an den Integration-Hub
        test_data = {
            "source_type": "mcp_server",
            "server_name": "test-mcp",
            "event_type": "test",
            "title": "MCP Integration Test",
            "description": "This is a test event to verify the MCP integration with n8n.",
            "severity": "info",
            "components": ["test", "integration"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        response = requests.post(
            f"{n8n_url}/webhook/event",
            json=test_data
        )
        
        if response.status_code in (200, 201):
            logger.info("✅ MCP-Integration wurde erfolgreich getestet.")
            logger.info(f"Antwort: {response.json()}")
            return True
        else:
            logger.error(f"❌ Fehler beim Testen der MCP-Integration: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler beim Testen der MCP-Integration: {e}")
        return False

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="MCP-Server n8n Integration mit verbesserten Workflows")
    parser.add_argument("--config", default="/workspace/Dev-Server-Workflow/docker-mcp-servers/openhands-mcp-config.json", help="Pfad zur MCP-Konfigurationsdatei")
    parser.add_argument("--n8n-url", default="http://localhost:5678", help="URL der n8n-Instanz")
    parser.add_argument("--n8n-api-key", required=True, help="API-Key der n8n-Instanz")
    parser.add_argument("--test", action="store_true", help="Teste die Integration nach der Konfiguration")
    
    args = parser.parse_args()
    
    # Lade die Server-Konfiguration
    servers = load_config(args.config)
    
    if not servers:
        logger.error("Keine MCP-Server in der Konfiguration gefunden.")
        return 1
    
    # Erstelle Umgebungsvariablen in n8n
    if not create_n8n_environment_variables(args.n8n_url, args.n8n_api_key, servers):
        logger.error("Umgebungsvariablen konnten nicht erstellt werden.")
        return 1
    
    # Importiere die Workflows
    if not import_workflows(args.n8n_api_key):
        logger.error("Workflows konnten nicht importiert werden.")
        return 1
    
    # Teste die Integration, wenn gewünscht
    if args.test:
        if not test_mcp_integration(args.n8n_url):
            logger.error("Integration konnte nicht getestet werden.")
            return 1
    
    logger.info("✅ MCP-Server wurden erfolgreich mit n8n integriert!")
    return 0

if __name__ == "__main__":
    sys.exit(main())