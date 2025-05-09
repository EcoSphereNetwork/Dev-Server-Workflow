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
import subprocess
from pathlib import Path

try:
    import requests
except ImportError:
    # Installiere requests, wenn es nicht verfügbar ist
    logger.info("Installiere erforderliche Pakete...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

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
    """Lädt die MCP-Server-Konfiguration aus einer JSON-Datei.
    
    Args:
        config_path: Pfad zur Konfigurationsdatei
        
    Returns:
        Liste der MCP-Server-Konfigurationen oder DEFAULT_MCP_SERVERS, wenn die Datei nicht existiert
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                if "mcp" in config and "servers" in config["mcp"]:
                    return config["mcp"]["servers"]
        
        logger.warning(f"Konfigurationsdatei nicht gefunden: {config_path}")
        logger.warning("Verwende Standard-MCP-Server-Konfiguration.")
        return DEFAULT_MCP_SERVERS
    
    except Exception as e:
        logger.warning(f"Fehler beim Laden der Konfiguration: {e}")
        logger.warning("Verwende Standard-MCP-Server-Konfiguration.")
        return DEFAULT_MCP_SERVERS

def create_n8n_environment_variables(n8n_url, n8n_api_key, mcp_servers):
    """Erstellt Umgebungsvariablen in n8n für die MCP-Server.
    
    Args:
        n8n_url: URL der n8n-Instanz
        n8n_api_key: API-Key der n8n-Instanz
        mcp_servers: Liste der MCP-Server-Konfigurationen
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
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
            for variable in variables.get("data", []):
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

def find_workflow_files():
    """Sucht nach n8n-Workflow-Dateien im Projektverzeichnis.
    
    Returns:
        Liste der Pfade zu den Workflow-Dateien
    """
    # Mögliche Workflow-Verzeichnisse
    workflow_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "n8n-workflows"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflows"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "ESN_Initial-Szenario", "n8n-workflows"),
        os.path.expanduser("~/Dev-Server-Workflow/src/n8n-workflows"),
        os.path.expanduser("~/Dev-Server-Workflow/workflows"),
        os.path.expanduser("~/Dev-Server-Workflow/src/ESN_Initial-Szenario/n8n-workflows"),
        "/workspace/Dev-Server-Workflow/src/n8n-workflows",
        "/workspace/Dev-Server-Workflow/workflows",
        "/workspace/Dev-Server-Workflow/src/ESN_Initial-Szenario/n8n-workflows"
    ]
    
    workflow_files = []
    
    for workflow_dir in workflow_dirs:
        if os.path.isdir(workflow_dir):
            for file in os.listdir(workflow_dir):
                if file.endswith(".json"):
                    workflow_files.append(os.path.join(workflow_dir, file))
    
    if not workflow_files:
        logger.warning("Keine Workflow-Dateien gefunden.")
    else:
        logger.info(f"Gefundene Workflow-Dateien: {len(workflow_files)}")
        for file in workflow_files:
            logger.info(f"  - {file}")
    
    return workflow_files

def load_workflow(workflow_path):
    """Lädt einen n8n-Workflow aus einer JSON-Datei.
    
    Args:
        workflow_path: Pfad zur Workflow-Datei
        
    Returns:
        Der Workflow als Dictionary oder None, wenn ein Fehler auftritt
    """
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
            return workflow
    except Exception as e:
        logger.error(f"Fehler beim Laden des Workflows {workflow_path}: {e}")
        return None

def import_workflow(n8n_url, n8n_api_key, workflow):
    """Importiert einen Workflow in n8n.
    
    Args:
        n8n_url: URL der n8n-Instanz
        n8n_api_key: API-Key der n8n-Instanz
        workflow: Der zu importierende Workflow
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        headers = {
            "X-N8N-API-KEY": n8n_api_key,
            "Content-Type": "application/json"
        }
        
        # Überprüfe, ob der Workflow bereits existiert
        workflow_name = workflow.get("name", "Unbekannter Workflow")
        response = requests.get(
            f"{n8n_url}/api/v1/workflows",
            headers=headers
        )
        
        if response.status_code == 200:
            existing_workflows = response.json()
            for existing_workflow in existing_workflows.get("data", []):
                if existing_workflow["name"] == workflow_name:
                    # Workflow existiert bereits, aktualisiere ihn
                    logger.info(f"Workflow '{workflow_name}' existiert bereits, aktualisiere ihn...")
                    response = requests.put(
                        f"{n8n_url}/api/v1/workflows/{existing_workflow['id']}",
                        headers=headers,
                        json=workflow
                    )
                    
                    if response.status_code in (200, 201):
                        result = response.json()
                        logger.info(f"✅ Workflow '{workflow_name}' wurde erfolgreich aktualisiert mit ID: {result['id']}")
                        return True
                    else:
                        logger.error(f"❌ Fehler beim Aktualisieren des Workflows '{workflow_name}': {response.status_code} - {response.text}")
                        return False
        
        # Workflow existiert nicht, erstelle ihn
        response = requests.post(
            f"{n8n_url}/api/v1/workflows",
            headers=headers,
            json=workflow
        )
        
        if response.status_code in (200, 201):
            result = response.json()
            logger.info(f"✅ Workflow '{workflow_name}' wurde erfolgreich importiert mit ID: {result['id']}")
            return True
        else:
            logger.error(f"❌ Fehler beim Importieren des Workflows '{workflow_name}': {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler beim Importieren des Workflows: {e}")
        return False

def import_all_workflows(n8n_url, n8n_api_key):
    """Importiert alle gefundenen Workflows in n8n.
    
    Args:
        n8n_url: URL der n8n-Instanz
        n8n_api_key: API-Key der n8n-Instanz
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Finde die Workflow-Dateien
        workflow_files = find_workflow_files()
        
        if not workflow_files:
            logger.warning("Keine Workflow-Dateien gefunden. Überspringe Import.")
            return False
        
        # Importiere jeden Workflow
        success_count = 0
        total_count = len(workflow_files)
        
        for workflow_file in workflow_files:
            logger.info(f"Importiere Workflow aus {workflow_file}...")
            
            workflow = load_workflow(workflow_file)
            if not workflow:
                continue
            
            if import_workflow(n8n_url, n8n_api_key, workflow):
                success_count += 1
            
            # Kurze Pause zwischen den Imports
            time.sleep(1)
        
        # Ausgabe der Zusammenfassung
        logger.info(f"Import abgeschlossen: {success_count}/{total_count} Workflows wurden erfolgreich importiert.")
        
        if success_count == total_count:
            logger.info("Alle Workflows wurden erfolgreich importiert! 🎉")
            return True
        else:
            logger.warning("Einige Workflows konnten nicht importiert werden. Bitte überprüfen Sie die Logs.")
            return False
    
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler beim Importieren der Workflows: {e}")
        return False

def test_mcp_integration(n8n_url):
    """Testet die Integration der MCP-Server mit n8n.
    
    Args:
        n8n_url: URL der n8n-Instanz
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
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
            logger.info(f"Antwort: {response.json() if response.headers.get('content-type') == 'application/json' else response.text}")
            return True
        else:
            logger.error(f"❌ Fehler beim Testen der MCP-Integration: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler beim Testen der MCP-Integration: {e}")
        return False

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
        "/workspace/Dev-Server-Workflow/config/openhands-mcp-config.json"
    ]
    
    for config_file in config_files:
        if os.path.isfile(config_file):
            logger.info(f"Gefundene MCP-Konfigurationsdatei: {config_file}")
            return config_file
    
    logger.warning("Keine MCP-Konfigurationsdatei gefunden.")
    return None

def detect_n8n_url():
    """Versucht, die URL der n8n-Instanz automatisch zu erkennen.
    
    Returns:
        URL der n8n-Instanz oder None, wenn nicht gefunden
    """
    # Mögliche URLs
    urls = [
        "http://localhost:5678",
        "http://n8n:5678",
        "http://n8n.ecospherenet.work",
        "https://n8n.ecospherenet.work"
    ]
    
    # Prüfe auch Umgebungsvariablen
    if "N8N_URL" in os.environ:
        urls.insert(0, os.environ["N8N_URL"])
    
    # Prüfe alle URLs
    for url in urls:
        try:
            response = requests.get(f"{url}/healthz", timeout=3)
            if response.status_code == 200:
                logger.info(f"Gefundene n8n-Instanz: {url}")
                return url
        except:
            continue
    
    logger.warning("Konnte die n8n-Instanz nicht automatisch erkennen.")
    return None

def check_n8n_api_key(n8n_url, n8n_api_key):
    """Überprüft, ob der n8n-API-Key gültig ist.
    
    Args:
        n8n_url: URL der n8n-Instanz
        n8n_api_key: API-Key der n8n-Instanz
        
    Returns:
        True, wenn der API-Key gültig ist, sonst False
    """
    try:
        headers = {
            "X-N8N-API-KEY": n8n_api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{n8n_url}/api/v1/workflows",
            headers=headers
        )
        
        if response.status_code == 200:
            logger.info("✅ n8n-API-Key ist gültig.")
            return True
        else:
            logger.error(f"❌ n8n-API-Key ist ungültig: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Überprüfen des n8n-API-Keys: {e}")
        return False

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="MCP-Server n8n Integration mit verbesserten Workflows")
    parser.add_argument("--config", help="Pfad zur MCP-Konfigurationsdatei")
    parser.add_argument("--n8n-url", help="URL der n8n-Instanz")
    parser.add_argument("--n8n-api-key", help="API-Key der n8n-Instanz")
    parser.add_argument("--test", action="store_true", help="Teste die Integration nach der Konfiguration")
    parser.add_argument("--skip-import", action="store_true", help="Überspringe den Import der Workflows")
    
    args = parser.parse_args()
    
    # Erkenne die n8n-URL automatisch, wenn nicht angegeben
    n8n_url = args.n8n_url
    if not n8n_url:
        n8n_url = detect_n8n_url()
        if not n8n_url:
            logger.error("n8n-URL konnte nicht automatisch erkannt werden und wurde nicht angegeben.")
            logger.error("Bitte geben Sie die URL mit --n8n-url an.")
            return 1
    
    # Überprüfe den n8n-API-Key
    n8n_api_key = args.n8n_api_key
    if not n8n_api_key:
        # Suche nach API-Key in Umgebungsvariablen
        if "N8N_API_KEY" in os.environ:
            n8n_api_key = os.environ["N8N_API_KEY"]
            logger.info("n8n-API-Key aus Umgebungsvariable geladen.")
        else:
            logger.error("n8n-API-Key wurde nicht angegeben.")
            logger.error("Bitte geben Sie den API-Key mit --n8n-api-key an oder setzen Sie die Umgebungsvariable N8N_API_KEY.")
            return 1
    
    # Überprüfe, ob der API-Key gültig ist
    if not check_n8n_api_key(n8n_url, n8n_api_key):
        logger.error("n8n-API-Key ist ungültig. Bitte überprüfen Sie den API-Key.")
        return 1
    
    # Finde die MCP-Konfigurationsdatei, wenn nicht angegeben
    config_path = args.config
    if not config_path:
        config_path = find_mcp_config_file()
    
    # Lade die Server-Konfiguration
    servers = load_config(config_path if config_path else None)
    
    if not servers:
        logger.error("Keine MCP-Server in der Konfiguration gefunden.")
        return 1
    
    # Erstelle Umgebungsvariablen in n8n
    if not create_n8n_environment_variables(n8n_url, n8n_api_key, servers):
        logger.error("Umgebungsvariablen konnten nicht erstellt werden.")
        return 1
    
    # Importiere die Workflows, wenn nicht übersprungen
    if not args.skip_import:
        if not import_all_workflows(n8n_url, n8n_api_key):
            logger.warning("Einige Workflows konnten nicht importiert werden.")
            # Wir fahren trotzdem fort, da dies kein kritischer Fehler ist
    
    # Teste die Integration, wenn gewünscht
    if args.test:
        if not test_mcp_integration(n8n_url):
            logger.error("Integration konnte nicht getestet werden.")
            return 1
    
    logger.info("✅ MCP-Server wurden erfolgreich mit n8n integriert!")
    logger.info(f"Die n8n-Instanz ist erreichbar unter: {n8n_url}")
    logger.info("Die MCP-Server-Konfiguration wurde als Umgebungsvariable in n8n hinzugefügt.")
    
    if not args.skip_import:
        logger.info("Die Workflows wurden in n8n importiert.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
