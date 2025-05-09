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
Kommandozeilentool für den OpenHands-Agenten.

Dieses Tool ermöglicht die Interaktion mit dem OpenHands-Agenten über die Kommandozeile.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from .agent import get_openhands_agent

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('openhands-cli')


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='OpenHands Agent CLI')
    
    # Allgemeine Argumente
    parser.add_argument('--config', help='Pfad zur Konfigurationsdatei')
    parser.add_argument('--verbose', '-v', action='store_true', help='Ausführliche Ausgabe')
    
    # Subparser für Befehle
    subparsers = parser.add_subparsers(dest='command', help='Befehl')
    
    # Befehl: task
    task_parser = subparsers.add_parser('task', help='Führe eine Aufgabe aus')
    task_parser.add_argument('task', help='Beschreibung der Aufgabe')
    task_parser.add_argument('--context', help='Kontext für die Aufgabe (JSON)')
    
    # Befehl: mcp
    mcp_parser = subparsers.add_parser('mcp', help='Führe eine MCP-Aufgabe aus')
    mcp_parser.add_argument('task', help='Beschreibung der Aufgabe')
    mcp_parser.add_argument('server', help='Name des MCP-Servers')
    mcp_parser.add_argument('function', help='Name der Funktion')
    mcp_parser.add_argument('--parameters', help='Parameter für die Funktion (JSON)')
    
    # Befehl: workflow
    workflow_parser = subparsers.add_parser('workflow', help='Verwalte einen n8n-Workflow')
    workflow_parser.add_argument('workflow', help='Name des Workflows')
    workflow_parser.add_argument('action', help='Aktion (start, stop, update, etc.)')
    workflow_parser.add_argument('--parameters', help='Parameter für die Aktion (JSON)')
    
    # Befehl: github
    github_parser = subparsers.add_parser('github', help='Verwalte ein GitHub-Repository')
    github_parser.add_argument('repository', help='Name des Repositories')
    github_parser.add_argument('action', help='Aktion (clone, pull, push, etc.)')
    github_parser.add_argument('--parameters', help='Parameter für die Aktion (JSON)')
    
    # Befehl: command
    command_parser = subparsers.add_parser('command', help='Führe einen Befehl aus')
    command_parser.add_argument('command', help='Befehl, der ausgeführt werden soll')
    command_parser.add_argument('--working-directory', help='Arbeitsverzeichnis für den Befehl')
    
    # Befehl: files
    files_parser = subparsers.add_parser('files', help='Verwalte Dateien')
    files_parser.add_argument('action', help='Aktion (read, write, delete, etc.)')
    files_parser.add_argument('path', help='Pfad zur Datei')
    files_parser.add_argument('--content', help='Inhalt für die Datei (bei write)')
    
    # Befehl: complex
    complex_parser = subparsers.add_parser('complex', help='Löse eine komplexe Aufgabe')
    complex_parser.add_argument('task', help='Beschreibung der Aufgabe')
    complex_parser.add_argument('--steps', help='Schritte für die Lösung der Aufgabe (JSON)')
    
    # Befehl: config
    config_parser = subparsers.add_parser('config', help='Verwalte die Konfiguration')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Konfigurationsbefehl')
    
    # Befehl: config show
    config_show_parser = config_subparsers.add_parser('show', help='Zeige die Konfiguration')
    
    # Befehl: config update
    config_update_parser = config_subparsers.add_parser('update', help='Aktualisiere die Konfiguration')
    config_update_parser.add_argument('updates', help='Aktualisierungen für die Konfiguration (JSON)')
    
    # Befehl: config save
    config_save_parser = config_subparsers.add_parser('save', help='Speichere die Konfiguration')
    
    return parser.parse_args()


def main():
    """
    Main function.
    """
    args = parse_args()
    
    # Setze Log-Level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Hole OpenHands Agent
    agent = get_openhands_agent(args.config)
    
    # Führe Befehl aus
    if args.command == 'task':
        # Parse Kontext
        context = None
        if args.context:
            try:
                context = json.loads(args.context)
            except json.JSONDecodeError:
                logger.error("Ungültiger JSON-Kontext")
                sys.exit(1)
        
        # Führe Aufgabe aus
        try:
            result = agent.execute_task(args.task, context)
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung der Aufgabe: {e}")
            sys.exit(1)
    
    elif args.command == 'mcp':
        # Parse Parameter
        parameters = {}
        if args.parameters:
            try:
                parameters = json.loads(args.parameters)
            except json.JSONDecodeError:
                logger.error("Ungültige JSON-Parameter")
                sys.exit(1)
        
        # Führe MCP-Aufgabe aus
        try:
            result = agent.execute_mcp_task(args.task, args.server, args.function, parameters)
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung der MCP-Aufgabe: {e}")
            sys.exit(1)
    
    elif args.command == 'workflow':
        # Parse Parameter
        parameters = None
        if args.parameters:
            try:
                parameters = json.loads(args.parameters)
            except json.JSONDecodeError:
                logger.error("Ungültige JSON-Parameter")
                sys.exit(1)
        
        # Verwalte Workflow
        try:
            result = agent.manage_workflow(args.workflow, args.action, parameters)
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Fehler bei der Verwaltung des Workflows: {e}")
            sys.exit(1)
    
    elif args.command == 'github':
        # Parse Parameter
        parameters = None
        if args.parameters:
            try:
                parameters = json.loads(args.parameters)
            except json.JSONDecodeError:
                logger.error("Ungültige JSON-Parameter")
                sys.exit(1)
        
        # Verwalte GitHub-Repository
        try:
            result = agent.manage_github_repository(args.repository, args.action, parameters)
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Fehler bei der Verwaltung des Repositories: {e}")
            sys.exit(1)
    
    elif args.command == 'command':
        # Führe Befehl aus
        try:
            result = agent.execute_command(args.command, args.working_directory)
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung des Befehls: {e}")
            sys.exit(1)
    
    elif args.command == 'files':
        # Verwalte Dateien
        try:
            result = agent.manage_files(args.action, args.path, args.content)
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Fehler bei der Verwaltung der Datei: {e}")
            sys.exit(1)
    
    elif args.command == 'complex':
        # Parse Schritte
        steps = None
        if args.steps:
            try:
                steps = json.loads(args.steps)
            except json.JSONDecodeError:
                logger.error("Ungültige JSON-Schritte")
                sys.exit(1)
        
        # Löse komplexe Aufgabe
        try:
            result = agent.solve_complex_task(args.task, steps)
            print(json.dumps(result, indent=2))
        except Exception as e:
            logger.error(f"Fehler bei der Lösung der komplexen Aufgabe: {e}")
            sys.exit(1)
    
    elif args.command == 'config':
        if args.config_command == 'show':
            # Zeige Konfiguration
            print(json.dumps(agent.config, indent=2))
        
        elif args.config_command == 'update':
            # Parse Aktualisierungen
            try:
                updates = json.loads(args.updates)
            except json.JSONDecodeError:
                logger.error("Ungültige JSON-Aktualisierungen")
                sys.exit(1)
            
            # Aktualisiere Konfiguration
            try:
                agent.update_config(updates)
                logger.info("Konfiguration erfolgreich aktualisiert")
            except Exception as e:
                logger.error(f"Fehler bei der Aktualisierung der Konfiguration: {e}")
                sys.exit(1)
        
        elif args.config_command == 'save':
            # Speichere Konfiguration
            try:
                agent.save_config()
                logger.info("Konfiguration erfolgreich gespeichert")
            except Exception as e:
                logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
                sys.exit(1)
        
        else:
            logger.error("Unbekannter Konfigurationsbefehl")
            sys.exit(1)
    
    else:
        logger.error("Unbekannter Befehl")
        sys.exit(1)


if __name__ == "__main__":
    main()