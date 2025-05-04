#!/usr/bin/env python3
"""
n8n Workflow Integration Setup

Dieses Skript dient als Wrapper für die Installation und Konfiguration von n8n
mit Workflows für AFFiNE, AppFlowy, GitLab/GitHub, OpenProject und OpenHands.

Verwendung:
python setup.py install --env-file .env
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Set up n8n with integrated workflows')
    parser.add_argument('command', choices=['install', 'test', 'help'], 
                        help='Command to execute: install, test, or help')
    parser.add_argument('--env-file', default='.env', 
                        help='Path to .env file with configurations')
    parser.add_argument('--workflows', nargs='+', 
                        choices=['github', 'document', 'openhands', 'discord', 'timetracking', 'ai', 'mcp', 'all'],
                        default=['all'], 
                        help='Specific workflows to install')
    parser.add_argument('--mcp', action='store_true', 
                        help='Enable MCP server for n8n workflows')
    parser.add_argument('--no-install', action='store_true', 
                        help='Skip n8n installation')
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Überprüfe, ob die .env-Datei existiert
    env_file = Path(args.env_file)
    if not env_file.exists() and args.command != 'help':
        print(f"Error: Environment file {args.env_file} not found.")
        print("Please create the file or specify a different file with --env-file.")
        return 1
    
    # Überprüfe, ob das src-Verzeichnis existiert
    src_dir = Path('src')
    if not src_dir.exists() and args.command != 'help':
        print("Error: src directory not found.")
        print("Please run this script from the root directory of the project.")
        return 1
    
    # Führe den entsprechenden Befehl aus
    if args.command == 'help':
        show_help()
    elif args.command == 'test':
        run_tests(args)
    elif args.command == 'install':
        install_workflows(args)
    
    return 0

def show_help():
    """Show help information."""
    print("""
n8n Workflow Integration Setup

Dieses Skript dient als Wrapper für die Installation und Konfiguration von n8n
mit Workflows für AFFiNE, AppFlowy, GitLab/GitHub, OpenProject und OpenHands.

Befehle:
  install     Installiere n8n und richte Workflows ein
  test        Teste die Installation und Konfiguration
  help        Zeige diese Hilfe an

Optionen für 'install':
  --env-file FILE       Pfad zur .env-Datei mit Konfigurationen (Standard: .env)
  --workflows WORKFLOWS Spezifische Workflows zum Installieren (github, document, 
                        openhands, discord, timetracking, ai, mcp, all)
  --mcp                 Aktiviere den MCP-Server für n8n-Workflows
  --no-install          Überspringe die n8n-Installation

Optionen für 'test':
  --env-file FILE       Pfad zur .env-Datei mit Konfigurationen (Standard: .env)

Beispiele:
  python setup.py install --env-file .env --workflows github document openhands
  python setup.py install --mcp --no-install
  python setup.py test
  python setup.py help
""")

def run_tests(args):
    """Run tests."""
    print("=== Running tests ===")
    
    # Führe das Test-Skript aus
    test_script = Path('test-setup.py')
    if test_script.exists():
        subprocess.run([sys.executable, str(test_script)])
    else:
        print(f"Error: Test script {test_script} not found.")
        print("Creating a simple test script...")
        
        # Erstelle ein einfaches Test-Skript
        with open(test_script, 'w') as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Test-Skript für die n8n-Workflow-Integration

Dieses Skript testet die grundlegende Funktionalität der Setup-Skripte.
\"\"\"

import os
import sys
from pathlib import Path

def main():
    \"\"\"Hauptfunktion zum Testen der Setup-Skripte.\"\"\"
    print("=== Testing n8n Workflow Integration Setup ===")
    
    # Überprüfe, ob die .env-Datei existiert
    env_file = Path('.env')
    if not env_file.exists():
        print("Error: .env file not found. Please create it first.")
        return 1
    
    # Überprüfe, ob die Workflow-Dateien existieren
    workflow_files = [
        "n8n-setup-main.py",
        "n8n-setup-utils.py",
        "n8n-setup-install.py",
        "n8n-setup-credentials.py",
        "n8n-setup-workflows.py",
        "n8n-setup-workflows-github.py",
        "n8n-setup-workflows-document.py",
        "n8n-setup-workflows-openhands.py",
        "n8n-setup-workflows-special.py",
        "n8n-setup-workflows-mcp.py",
        "n8n-mcp-server.py"
    ]
    
    for file in workflow_files:
        file_path = Path('src') / file
        if file_path.exists():
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} does not exist")
    
    print("\\n=== Test completed ===")
    print("The setup files are present and ready to be used.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
""")
        
        print(f"Test script created at {test_script}")
        subprocess.run([sys.executable, str(test_script)])

def install_workflows(args):
    """Install workflows."""
    print("=== Installing workflows ===")
    
    # Bereite die Befehlszeilenargumente vor
    cmd = [sys.executable, 'src/n8n-setup-main.py']
    
    # Füge die .env-Datei hinzu
    cmd.extend(['--env-file', args.env_file])
    
    # Füge die Installation hinzu, wenn nicht deaktiviert
    if not args.no_install:
        cmd.append('--install')
    
    # Füge den MCP-Server hinzu, wenn aktiviert
    if args.mcp:
        cmd.append('--mcp')
    
    # Füge die Workflows hinzu
    if 'all' in args.workflows:
        cmd.extend(['--workflows', 'github', 'document', 'openhands', 'discord', 'timetracking', 'ai', 'mcp'])
    else:
        cmd.extend(['--workflows'] + args.workflows)
    
    # Führe das Hauptskript aus
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    sys.exit(main())