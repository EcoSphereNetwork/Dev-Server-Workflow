"""
MCP Hub CLI - Kommandozeilenschnittstelle für den MCP Hub.

Diese Datei bietet eine Kommandozeilenschnittstelle für den MCP Hub.
"""

import os
import sys
import argparse
import logging
from typing import List, Optional

from .hub_manager import MCPHubManager

# Erstelle Logger
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """
    Konfiguriere das Logging.

    Args:
        verbose: Ob ausführliche Logs aktiviert werden sollen
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse die Kommandozeilenargumente.

    Args:
        args: Die zu parsenden Argumente

    Returns:
        Die geparsten Argumente
    """
    parser = argparse.ArgumentParser(description="MCP Hub - Ein Hub für MCP Server")
    
    # Globale Optionen
    parser.add_argument("--verbose", "-v", action="store_true", help="Aktiviere ausführliche Logs")
    parser.add_argument("--config", "-c", help="Pfad zur Konfigurationsdatei")
    
    # Subparser für Befehle
    subparsers = parser.add_subparsers(dest="command", help="Befehl")
    
    # Befehl: search
    search_parser = subparsers.add_parser("search", help="Suche nach MCP Servern")
    search_parser.add_argument("query", help="Die Suchanfrage")
    
    # Befehl: install
    install_parser = subparsers.add_parser("install", help="Installiere einen MCP Server")
    install_parser.add_argument("server_id", help="Die ID des zu installierenden MCP Servers")
    
    # Befehl: uninstall
    uninstall_parser = subparsers.add_parser("uninstall", help="Deinstalliere einen MCP Server")
    uninstall_parser.add_argument("server_id", help="Die ID des zu deinstallierenden MCP Servers")
    
    # Befehl: list
    list_parser = subparsers.add_parser("list", help="Liste alle installierten MCP Server auf")
    
    # Befehl: start
    start_parser = subparsers.add_parser("start", help="Starte einen MCP Server")
    start_parser.add_argument("server_id", help="Die ID des zu startenden MCP Servers")
    
    # Befehl: stop
    stop_parser = subparsers.add_parser("stop", help="Stoppe einen MCP Server")
    stop_parser.add_argument("server_id", help="Die ID des zu stoppenden MCP Servers")
    
    # Befehl: status
    status_parser = subparsers.add_parser("status", help="Zeige den Status eines MCP Servers an")
    status_parser.add_argument("server_id", help="Die ID des MCP Servers")
    
    # Befehl: update
    update_parser = subparsers.add_parser("update", help="Aktualisiere die Registry")
    
    # Befehl: add-repo
    add_repo_parser = subparsers.add_parser("add-repo", help="Füge ein Repository hinzu")
    add_repo_parser.add_argument("repo_url", help="Die URL des Repositories")
    
    # Befehl: remove-repo
    remove_repo_parser = subparsers.add_parser("remove-repo", help="Entferne ein Repository")
    remove_repo_parser.add_argument("repo_url", help="Die URL des Repositories")
    
    # Befehl: add-docker-user
    add_docker_user_parser = subparsers.add_parser("add-docker-user", help="Füge einen Docker Hub Benutzer hinzu")
    add_docker_user_parser.add_argument("username", help="Der Benutzername")
    
    # Befehl: remove-docker-user
    remove_docker_user_parser = subparsers.add_parser("remove-docker-user", help="Entferne einen Docker Hub Benutzer")
    remove_docker_user_parser.add_argument("username", help="Der Benutzername")
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Hauptfunktion für die Kommandozeilenschnittstelle.

    Args:
        args: Die Kommandozeilenargumente

    Returns:
        Der Exit-Code
    """
    # Parse die Argumente
    parsed_args = parse_args(args)
    
    # Konfiguriere das Logging
    setup_logging(parsed_args.verbose)
    
    # Erstelle den Hub Manager
    hub_manager = MCPHubManager(config_path=parsed_args.config)
    
    # Führe den Befehl aus
    if parsed_args.command == "search":
        # Aktualisiere die Registry
        hub_manager.update_registry()
        
        # Suche nach MCP Servern
        results = hub_manager.search_servers(parsed_args.query)
        
        # Zeige die Ergebnisse an
        if results:
            print(f"Gefundene MCP Server für '{parsed_args.query}':")
            for i, server in enumerate(results, 1):
                print(f"{i}. {server['name']} ({server['id']})")
                print(f"   Beschreibung: {server['description']}")
                print(f"   URL: {server['url']}")
                print(f"   Quelle: {server['source']}")
                print()
        else:
            print(f"Keine MCP Server für '{parsed_args.query}' gefunden.")
    
    elif parsed_args.command == "install":
        # Aktualisiere die Registry
        hub_manager.update_registry()
        
        # Installiere den MCP Server
        success = hub_manager.install_server(parsed_args.server_id)
        
        if success:
            print(f"MCP Server {parsed_args.server_id} erfolgreich installiert.")
        else:
            print(f"Fehler bei der Installation von MCP Server {parsed_args.server_id}.")
            return 1
    
    elif parsed_args.command == "uninstall":
        # Deinstalliere den MCP Server
        success = hub_manager.uninstall_server(parsed_args.server_id)
        
        if success:
            print(f"MCP Server {parsed_args.server_id} erfolgreich deinstalliert.")
        else:
            print(f"Fehler bei der Deinstallation von MCP Server {parsed_args.server_id}.")
            return 1
    
    elif parsed_args.command == "list":
        # Liste alle installierten MCP Server auf
        servers = hub_manager.list_installed_servers()
        
        if servers:
            print("Installierte MCP Server:")
            for i, server in enumerate(servers, 1):
                print(f"{i}. {server['name']} ({server.get('type', 'unknown')})")
                print(f"   Beschreibung: {server.get('description', '')}")
                print(f"   Pfad: {server.get('path', '')}")
                print()
        else:
            print("Keine MCP Server installiert.")
    
    elif parsed_args.command == "start":
        # Starte den MCP Server
        success = hub_manager.start_server(parsed_args.server_id)
        
        if success:
            print(f"MCP Server {parsed_args.server_id} erfolgreich gestartet.")
        else:
            print(f"Fehler beim Starten von MCP Server {parsed_args.server_id}.")
            return 1
    
    elif parsed_args.command == "stop":
        # Stoppe den MCP Server
        success = hub_manager.stop_server(parsed_args.server_id)
        
        if success:
            print(f"MCP Server {parsed_args.server_id} erfolgreich gestoppt.")
        else:
            print(f"Fehler beim Stoppen von MCP Server {parsed_args.server_id}.")
            return 1
    
    elif parsed_args.command == "status":
        # Zeige den Status des MCP Servers an
        status = hub_manager.get_server_status(parsed_args.server_id)
        
        print(f"Status von MCP Server {parsed_args.server_id}:")
        print(f"Status: {status.get('status', 'unbekannt')}")
        print(f"Typ: {status.get('type', 'unbekannt')}")
        
        if "error" in status:
            print(f"Fehler: {status['error']}")
    
    elif parsed_args.command == "update":
        # Aktualisiere die Registry
        hub_manager.update_registry()
        print("Registry erfolgreich aktualisiert.")
    
    elif parsed_args.command == "add-repo":
        # Füge ein Repository hinzu
        success = hub_manager.add_repository(parsed_args.repo_url)
        
        if success:
            print(f"Repository {parsed_args.repo_url} erfolgreich hinzugefügt.")
        else:
            print(f"Fehler beim Hinzufügen des Repositories {parsed_args.repo_url}.")
            return 1
    
    elif parsed_args.command == "remove-repo":
        # Entferne ein Repository
        success = hub_manager.remove_repository(parsed_args.repo_url)
        
        if success:
            print(f"Repository {parsed_args.repo_url} erfolgreich entfernt.")
        else:
            print(f"Fehler beim Entfernen des Repositories {parsed_args.repo_url}.")
            return 1
    
    elif parsed_args.command == "add-docker-user":
        # Füge einen Docker Hub Benutzer hinzu
        success = hub_manager.add_docker_hub_user(parsed_args.username)
        
        if success:
            print(f"Docker Hub Benutzer {parsed_args.username} erfolgreich hinzugefügt.")
        else:
            print(f"Fehler beim Hinzufügen des Docker Hub Benutzers {parsed_args.username}.")
            return 1
    
    elif parsed_args.command == "remove-docker-user":
        # Entferne einen Docker Hub Benutzer
        success = hub_manager.remove_docker_hub_user(parsed_args.username)
        
        if success:
            print(f"Docker Hub Benutzer {parsed_args.username} erfolgreich entfernt.")
        else:
            print(f"Fehler beim Entfernen des Docker Hub Benutzers {parsed_args.username}.")
            return 1
    
    else:
        # Kein Befehl angegeben
        print("Kein Befehl angegeben. Verwende --help für Hilfe.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())