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
Beispiel für die Verwendung des MCP-Server-Generators.

Dieses Skript demonstriert, wie man den MCP-Server-Generator verwenden kann,
um dynamisch MCP-Server zu erstellen und zu verwalten.
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
logger = logging.getLogger('generator-example')


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='MCP-Server-Generator Beispiel')
    parser.add_argument('--generator-url', default='http://localhost:3007', help='URL des MCP-Server-Generators')
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
    
    # Verbinde mit dem MCP-Server-Generator
    client = MCPClient(args.generator_url)
    
    # Überprüfe die Verbindung
    server_info = client.get_server_info()
    logger.info(f"Verbunden mit {server_info['name']} v{server_info['version']}")
    logger.info(f"Status: {server_info['status']}")
    logger.info(f"Verfügbare Vorlagen: {server_info['templates']}")
    
    # Erstelle einen einfachen MCP-Server aus der Vorlage
    logger.info("Erstelle einen einfachen MCP-Server aus der Vorlage...")
    result = client.call_function("create_server_from_template", {
        "name": "Simple Server",
        "template": "simple",
        "parameters": {
            "port": 3100
        }
    })
    
    simple_server_id = result["server_id"]
    logger.info(f"Einfacher MCP-Server erstellt (ID: {simple_server_id})")
    
    # Starte den einfachen MCP-Server
    logger.info("Starte den einfachen MCP-Server...")
    result = client.call_function("start_server", {
        "server_id": simple_server_id
    })
    
    if result["success"]:
        logger.info(f"Einfacher MCP-Server gestartet (PID: {result['pid']})")
    else:
        logger.error(f"Fehler beim Starten des einfachen MCP-Servers: {result['message']}")
        sys.exit(1)
    
    # Erstelle einen Taschenrechner-MCP-Server aus der Vorlage
    logger.info("Erstelle einen Taschenrechner-MCP-Server aus der Vorlage...")
    result = client.call_function("create_server_from_template", {
        "name": "Calculator Server",
        "template": "calculator",
        "parameters": {
            "port": 3101
        }
    })
    
    calculator_server_id = result["server_id"]
    logger.info(f"Taschenrechner-MCP-Server erstellt (ID: {calculator_server_id})")
    
    # Starte den Taschenrechner-MCP-Server
    logger.info("Starte den Taschenrechner-MCP-Server...")
    result = client.call_function("start_server", {
        "server_id": calculator_server_id
    })
    
    if result["success"]:
        logger.info(f"Taschenrechner-MCP-Server gestartet (PID: {result['pid']})")
    else:
        logger.error(f"Fehler beim Starten des Taschenrechner-MCP-Servers: {result['message']}")
        sys.exit(1)
    
    # Erstelle einen benutzerdefinierten MCP-Server
    logger.info("Erstelle einen benutzerdefinierten MCP-Server...")
    result = client.call_function("create_server", {
        "name": "Custom Server",
        "description": "Ein benutzerdefinierter MCP-Server",
        "functions": [
            {
                "name": "greet",
                "description": "Begrüßt einen Benutzer",
                "parameters": {
                    "name": {
                        "type": "string",
                        "description": "Name des Benutzers"
                    }
                }
            },
            {
                "name": "calculate_age",
                "description": "Berechnet das Alter basierend auf dem Geburtsjahr",
                "parameters": {
                    "birth_year": {
                        "type": "integer",
                        "description": "Geburtsjahr"
                    }
                }
            }
        ],
        "port": 3102,
        "implementation": """
def _greet(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Begrüßt einen Benutzer.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    name = parameters.get("name", "Welt")
    return {
        "message": f"Hallo, {name}!"
    }

def _calculate_age(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Berechnet das Alter basierend auf dem Geburtsjahr.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    import datetime
    
    birth_year = parameters.get("birth_year", 0)
    current_year = datetime.datetime.now().year
    
    age = current_year - birth_year
    
    return {
        "age": age
    }
"""
    })
    
    custom_server_id = result["server_id"]
    logger.info(f"Benutzerdefinierter MCP-Server erstellt (ID: {custom_server_id})")
    
    # Starte den benutzerdefinierten MCP-Server
    logger.info("Starte den benutzerdefinierten MCP-Server...")
    result = client.call_function("start_server", {
        "server_id": custom_server_id
    })
    
    if result["success"]:
        logger.info(f"Benutzerdefinierter MCP-Server gestartet (PID: {result['pid']})")
    else:
        logger.error(f"Fehler beim Starten des benutzerdefinierten MCP-Servers: {result['message']}")
        sys.exit(1)
    
    # Liste alle Server auf
    logger.info("Liste alle Server auf...")
    result = client.call_function("list_servers", {})
    
    logger.info("Verfügbare Server:")
    for server in result["servers"]:
        logger.info(f"  - {server['name']} (ID: {server['server_id']}, Port: {server['port']}, Status: {server['status']})")
    
    # Teste die Server
    logger.info("Teste den einfachen MCP-Server...")
    simple_client = MCPClient(f"http://localhost:3100")
    
    # Hole die verfügbaren Funktionen
    functions = simple_client.get_functions()
    logger.info(f"Verfügbare Funktionen des einfachen MCP-Servers: {[f['name'] for f in functions]}")
    
    # Rufe die hello_world-Funktion auf
    result = simple_client.call_function("hello_world", {})
    logger.info(f"Ergebnis von hello_world: {result}")
    
    # Rufe die echo-Funktion auf
    result = simple_client.call_function("echo", {
        "text": "Hallo, Welt!"
    })
    logger.info(f"Ergebnis von echo: {result}")
    
    # Teste den Taschenrechner-MCP-Server
    logger.info("Teste den Taschenrechner-MCP-Server...")
    calculator_client = MCPClient(f"http://localhost:3101")
    
    # Hole die verfügbaren Funktionen
    functions = calculator_client.get_functions()
    logger.info(f"Verfügbare Funktionen des Taschenrechner-MCP-Servers: {[f['name'] for f in functions]}")
    
    # Rufe die add-Funktion auf
    result = calculator_client.call_function("add", {
        "a": 5,
        "b": 3
    })
    logger.info(f"Ergebnis von add: {result}")
    
    # Rufe die subtract-Funktion auf
    result = calculator_client.call_function("subtract", {
        "a": 10,
        "b": 4
    })
    logger.info(f"Ergebnis von subtract: {result}")
    
    # Rufe die multiply-Funktion auf
    result = calculator_client.call_function("multiply", {
        "a": 6,
        "b": 7
    })
    logger.info(f"Ergebnis von multiply: {result}")
    
    # Rufe die divide-Funktion auf
    result = calculator_client.call_function("divide", {
        "a": 20,
        "b": 4
    })
    logger.info(f"Ergebnis von divide: {result}")
    
    # Teste den benutzerdefinierten MCP-Server
    logger.info("Teste den benutzerdefinierten MCP-Server...")
    custom_client = MCPClient(f"http://localhost:3102")
    
    # Hole die verfügbaren Funktionen
    functions = custom_client.get_functions()
    logger.info(f"Verfügbare Funktionen des benutzerdefinierten MCP-Servers: {[f['name'] for f in functions]}")
    
    # Rufe die greet-Funktion auf
    result = custom_client.call_function("greet", {
        "name": "Max"
    })
    logger.info(f"Ergebnis von greet: {result}")
    
    # Rufe die calculate_age-Funktion auf
    result = custom_client.call_function("calculate_age", {
        "birth_year": 1990
    })
    logger.info(f"Ergebnis von calculate_age: {result}")
    
    # Warte auf Benutzereingabe
    input("Drücke Enter, um die Server zu stoppen...")
    
    # Stoppe die Server
    logger.info("Stoppe den einfachen MCP-Server...")
    result = client.call_function("stop_server", {
        "server_id": simple_server_id
    })
    
    if result["success"]:
        logger.info(f"Einfacher MCP-Server gestoppt")
    else:
        logger.error(f"Fehler beim Stoppen des einfachen MCP-Servers: {result['message']}")
    
    logger.info("Stoppe den Taschenrechner-MCP-Server...")
    result = client.call_function("stop_server", {
        "server_id": calculator_server_id
    })
    
    if result["success"]:
        logger.info(f"Taschenrechner-MCP-Server gestoppt")
    else:
        logger.error(f"Fehler beim Stoppen des Taschenrechner-MCP-Servers: {result['message']}")
    
    logger.info("Stoppe den benutzerdefinierten MCP-Server...")
    result = client.call_function("stop_server", {
        "server_id": custom_server_id
    })
    
    if result["success"]:
        logger.info(f"Benutzerdefinierter MCP-Server gestoppt")
    else:
        logger.error(f"Fehler beim Stoppen des benutzerdefinierten MCP-Servers: {result['message']}")
    
    # Lösche die Server
    logger.info("Lösche den einfachen MCP-Server...")
    result = client.call_function("delete_server", {
        "server_id": simple_server_id
    })
    
    if result["success"]:
        logger.info(f"Einfacher MCP-Server gelöscht")
    else:
        logger.error(f"Fehler beim Löschen des einfachen MCP-Servers: {result['message']}")
    
    logger.info("Lösche den Taschenrechner-MCP-Server...")
    result = client.call_function("delete_server", {
        "server_id": calculator_server_id
    })
    
    if result["success"]:
        logger.info(f"Taschenrechner-MCP-Server gelöscht")
    else:
        logger.error(f"Fehler beim Löschen des Taschenrechner-MCP-Servers: {result['message']}")
    
    logger.info("Lösche den benutzerdefinierten MCP-Server...")
    result = client.call_function("delete_server", {
        "server_id": custom_server_id
    })
    
    if result["success"]:
        logger.info(f"Benutzerdefinierter MCP-Server gelöscht")
    else:
        logger.error(f"Fehler beim Löschen des benutzerdefinierten MCP-Servers: {result['message']}")
    
    logger.info("Beispiel abgeschlossen.")


if __name__ == "__main__":
    main()