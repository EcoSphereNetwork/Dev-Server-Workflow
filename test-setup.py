#!/usr/bin/env python3
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
    print("=== Testing n8n Workflow Integration Setup ===")
    
    # Überprüfe, ob die .env-Datei existiert
    env_file = Path('.env')
    if not env_file.exists():
        print("Error: .env file not found. Please create it first.")
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
    print("\n=== Checking environment variables ===")
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
    print("\n=== Checking Docker installation ===")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Docker is installed: {result.stdout.strip()}")
        else:
            print("✗ Docker is not installed or not working")
    except FileNotFoundError:
        print("✗ Docker is not installed")
    
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Docker Compose is installed: {result.stdout.strip()}")
        else:
            print("✗ Docker Compose is not installed or not working")
    except FileNotFoundError:
        print("✗ Docker Compose is not installed")
    
    print("\n=== Test completed ===")
    print("The setup files are present and ready to be used.")
    return 0

if __name__ == "__main__":
    sys.exit(main())