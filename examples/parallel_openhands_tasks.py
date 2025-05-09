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
Beispiel für die parallele Ausführung von OpenHands-Aufgaben.

Dieses Skript demonstriert, wie man mehrere OpenHands-Agenten parallel verwenden kann,
um Aufgaben parallel auszuführen.
"""

import os
import sys
import json
import time
import argparse
import logging
from typing import Dict, List, Any, Optional

# Füge das Stammverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mcp.client import MCPClient

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('parallel-openhands-tasks')


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Parallele OpenHands-Aufgaben')
    parser.add_argument('--server-url', default='http://localhost:3006', help='URL des OpenHands MCP-Servers')
    parser.add_argument('--num-agents', type=int, default=3, help='Anzahl der OpenHands-Agenten')
    parser.add_argument('--config-file', help='Pfad zur Konfigurationsdatei')
    parser.add_argument('--verbose', '-v', action='store_true', help='Ausführliche Ausgabe')
    return parser.parse_args()


def main():
    """
    Main function.
    """
    args = parse_args()
    
    # Setze Log-Level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verbinde mit dem OpenHands MCP-Server
    client = MCPClient(args.server_url)
    
    # Überprüfe die Verbindung
    server_info = client.get_server_info()
    logger.info(f"Verbunden mit {server_info['name']} v{server_info['version']}")
    logger.info(f"Status: {server_info['status']}")
    logger.info(f"Aktive Agenten: {server_info['active_agents']}")
    logger.info(f"Aktive Aufgaben: {server_info['active_tasks']}")
    
    # Erstelle OpenHands-Agenten
    agent_ids = []
    for i in range(args.num_agents):
        result = client.call_function("create_agent", {
            "config_file": args.config_file
        })
        agent_id = result["agent_id"]
        agent_ids.append(agent_id)
        logger.info(f"Agent {i+1} erstellt (ID: {agent_id})")
    
    # Definiere Aufgaben
    tasks = [
        {
            "agent_id": agent_ids[0],
            "task": "Erstelle eine Liste der 5 wichtigsten Python-Bibliotheken für Datenanalyse und erkläre kurz, wofür sie verwendet werden."
        },
        {
            "agent_id": agent_ids[1],
            "task": "Erkläre die Unterschiede zwischen REST API und GraphQL. Welche Vor- und Nachteile haben sie?"
        },
        {
            "agent_id": agent_ids[2 % len(agent_ids)],
            "task": "Beschreibe die Architektur einer modernen Microservices-Anwendung und welche Technologien dabei zum Einsatz kommen."
        }
    ]
    
    # Führe Aufgaben parallel aus
    task_ids = []
    for i, task in enumerate(tasks):
        result = client.call_function("execute_task", task)
        task_id = result["task_id"]
        task_ids.append(task_id)
        logger.info(f"Aufgabe {i+1} gestartet (ID: {task_id})")
    
    # Warte auf die Ergebnisse
    results = {}
    all_completed = False
    
    while not all_completed:
        all_completed = True
        
        for task_id in task_ids:
            if task_id in results:
                continue
            
            result = client.call_function("get_task_status", {
                "task_id": task_id
            })
            
            status = result["status"]
            logger.debug(f"Aufgabe {task_id}: {status}")
            
            if status != "completed" and status != "failed" and status != "cancelled":
                all_completed = False
            elif status == "completed" and task_id not in results:
                result = client.call_function("get_task_result", {
                    "task_id": task_id
                })
                results[task_id] = result
                logger.info(f"Aufgabe {task_id} abgeschlossen")
            elif status == "failed" and task_id not in results:
                result = client.call_function("get_task_result", {
                    "task_id": task_id
                })
                results[task_id] = result
                logger.error(f"Aufgabe {task_id} fehlgeschlagen: {result.get('result', {}).get('error')}")
        
        if not all_completed:
            time.sleep(1)
    
    # Zeige die Ergebnisse
    for i, task_id in enumerate(task_ids):
        result = results[task_id]
        logger.info(f"Ergebnis für Aufgabe {i+1} (ID: {task_id}):")
        
        if result["status"] == "completed":
            # Extrahiere die Antwort aus dem OpenHands-Ergebnis
            try:
                response = result["result"]["choices"][0]["message"]["content"]
                print(f"\n--- Aufgabe {i+1} ---\n")
                print(response)
                logger.info("\n")
            except (KeyError, IndexError):
                logger.error(f"Ungültiges Ergebnis-Format: {result}")
        else:
            logger.error(f"Aufgabe {task_id} nicht erfolgreich: {result}")
    
    # Lösche die Agenten
    for i, agent_id in enumerate(agent_ids):
        result = client.call_function("delete_agent", {
            "agent_id": agent_id
        })
        logger.info(f"Agent {i+1} gelöscht (ID: {agent_id})")


if __name__ == "__main__":
    main()