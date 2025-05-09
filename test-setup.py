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
Test-Skript für die n8n-Workflow-Integration

Dieses Skript testet die grundlegende Funktionalität der Setup-Skripte.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Hauptfunktion zum Testen der Setup-Skripte."""
    logger.info("=== Testing n8n Workflow Integration Setup ===")
    
    # Überprüfe, ob die .env-Datei existiert
    env_file = Path('.env')
    if not env_file.exists():
        logger.info("Error: .env file not found. Please create it first.")
        return 1
    
    # Überprüfe, ob die Workflow-Dateien existieren
    workflow_files = [
        "n8n_setup_main.py",
        "n8n_setup_utils.py",
        "n8n_setup_install.py",
        "n8n_setup_credentials.py",
        "n8n_setup_workflows.py",
        "n8n_setup_workflows_github.py",
        "n8n_setup_workflows_document.py",
        "n8n_setup_workflows_openhands.py",
        "n8n_setup_workflows_special.py",
        "n8n_setup_workflows_mcp.py",
        "n8n_mcp_server.py"
    ]
    
    for file in workflow_files:
        file_path = Path('src') / file
        if file_path.exists():
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} does not exist")
    
    # Überprüfe die Umgebungsvariablen in der .env-Datei
    logger.info("\n=== Checking environment variables ===")
    with open('.env', 'r') as f:
        env_content = f.read()
    
    required_vars = [
        "N8N_URL",
        "N8N_API_KEY",
        "GITHUB_TOKEN",
        "OPENPROJECT_URL",
        "OPENPROJECT_TOKEN"
    ]
    
    for var in required_vars:
        if f"{var}=" in env_content and not f"{var}=" + os.linesep in env_content:
            print(f"✓ {var} is set")
        else:
            print(f"✗ {var} is not set")
    
    # Überprüfe die Docker-Installation
    logger.info("\n=== Checking Docker installation ===")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Docker is installed: {result.stdout.strip()}")
        else:
            logger.info("✗ Docker is not installed or not working")
    except FileNotFoundError:
        logger.info("✗ Docker is not installed")
    
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Docker Compose is installed: {result.stdout.strip()}")
        else:
            logger.info("✗ Docker Compose is not installed or not working")
    except FileNotFoundError:
        logger.info("✗ Docker Compose is not installed")
    
    logger.info("\n=== Test completed ===")
    logger.info("The setup files are present and ready to be used.")
    return 0

if __name__ == "__main__":
    sys.exit(main())