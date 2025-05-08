#!/usr/bin/env python3
"""
Import n8n Workflows

Dieses Skript importiert n8n-Workflows in eine laufende n8n-Instanz.
"""

import argparse
import json
import logging
import os
import sys
import time
import requests

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('import-workflows.log')
    ]
)
logger = logging.getLogger('import-workflows')

# Liste der Workflows
WORKFLOWS = [
    "integration-hub.json",
    "github-to-openproject.json",
    "mcp-server-to-openproject.json",
    "error-handler.json"
]

def load_workflow(workflow_path):
    """Lädt einen n8n-Workflow aus einer JSON-Datei."""
    try:
        with open(workflow_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden des Workflows {workflow_path}: {e}")
        return None

def import_workflow(n8n_url, n8n_api_key, workflow):
    """Importiert einen Workflow in n8n."""
    try:
        headers = {
            "X-N8N-API-KEY": n8n_api_key,
            "Content-Type": "application/json"
        }
        
        # Überprüfe, ob der Workflow bereits existiert
        workflow_name = workflow["name"]
        response = requests.get(
            f"{n8n_url}/api/v1/workflows",
            headers=headers
        )
        
        if response.status_code == 200:
            existing_workflows = response.json()
            for existing_workflow in existing_workflows["data"]:
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

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="Import Improved n8n Workflows")
    parser.add_argument("--n8n-url", default="http://localhost:5678", help="URL der n8n-Instanz")
    parser.add_argument("--n8n-api-key", required=True, help="API-Key der n8n-Instanz")
    parser.add_argument("--workflows-dir", default="/workspace/Dev-Server-Workflow/src/ESN_Initial-Szenario/n8n-workflows", help="Verzeichnis mit den Workflow-Dateien")
    
    args = parser.parse_args()
    
    # Importiere die Workflows
    success_count = 0
    total_count = len(WORKFLOWS)
    
    for workflow_file in WORKFLOWS:
        workflow_path = os.path.join(args.workflows_dir, workflow_file)
        logger.info(f"Importiere Workflow aus {workflow_path}...")
        
        workflow = load_workflow(workflow_path)
        if not workflow:
            continue
        
        if import_workflow(args.n8n_url, args.n8n_api_key, workflow):
            success_count += 1
        
        # Kurze Pause zwischen den Imports
        time.sleep(1)
    
    # Ausgabe der Zusammenfassung
    logger.info(f"Import abgeschlossen: {success_count}/{total_count} Workflows wurden erfolgreich importiert.")
    
    if success_count == total_count:
        logger.info("Alle Workflows wurden erfolgreich importiert! 🎉")
        return 0
    else:
        logger.warning("Einige Workflows konnten nicht importiert werden. Bitte überprüfen Sie die Logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())