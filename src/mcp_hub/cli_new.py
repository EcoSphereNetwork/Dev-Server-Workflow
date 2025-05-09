"""
CLI-Modul für den MCP Hub.

Dieses Modul bietet eine Kommandozeilenschnittstelle für den MCP Hub.
"""

import os
import sys
import asyncio
import typer
from typing import List, Optional
from enum import Enum
from pathlib import Path

from .core.manager import HubManager
from .models.server import ServerConfig, ServerInfo, ServerStatus, ServerType, ServerProtocol
from .utils.logger import setup_logging

# Konfiguriere Logging
logger = setup_logging()

# Erstelle Typer-App
app = typer.Typer(
    name="mcp-hub",
    help="Ein Hub für MCP-Server",
    add_completion=False,
)

# Erstelle Hub-Manager
hub_manager = HubManager()


class ServerTypeChoice(str, Enum):
    """Enum für Servertypen."""
    
    N8N = "n8n"
    OPENHANDS = "openhands"
    DOCKER = "docker"
    GENERATOR = "generator"
    LLM_COST_ANALYZER = "llm_cost_analyzer"
    PROMPT = "prompt"
    CUSTOM = "custom"


class ServerProtocolChoice(str, Enum):
    """Enum für Serverprotokolle."""
    
    HTTP = "http"
    WEBSOCKET = "websocket"
    STDIO = "stdio"


@app.command("list")
def list_servers():
    """Liste alle MCP-Server auf."""
    servers = hub_manager.list_servers()
    
    if not servers:
        typer.echo("Keine MCP-Server gefunden.")
        return
    
    # Erstelle eine Tabelle
    typer.echo("MCP-Server:")
    typer.echo("Name\tTyp\tProtokoll\tURL\tStatus")
    typer.echo("-" * 80)
    
    # Fülle die Tabelle
    for server in servers:
        # Erhalte den Status des Servers
        status = asyncio.run(hub_manager.get_server_status(server.name))
        
        typer.echo(f"{server.name}\t{server.type}\t{server.protocol}\t{server.url or '-'}\t{status}")


@app.command("info")
def get_server_info(server_name: str):
    """Erhalte Informationen über einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        typer.echo(f"Server nicht gefunden: {server_name}")
        return
    
    # Erhalte Informationen über den Server
    server_info = asyncio.run(hub_manager.get_server_info(server_name))
    if not server_info:
        typer.echo(f"Fehler beim Abrufen der Serverinformationen: {server_name}")
        return
    
    # Zeige die Serverinformationen an
    typer.echo(f"Name: {server_info.name}")
    typer.echo(f"Beschreibung: {server_info.description}")
    typer.echo(f"Version: {server_info.version}")
    typer.echo(f"Typ: {server_info.type}")
    typer.echo(f"Protokoll: {server_info.protocol}")
    typer.echo(f"URL: {server_info.url or '-'}")
    typer.echo(f"Status: {server_info.status}")
    typer.echo(f"Zuletzt gesehen: {server_info.last_seen or '-'}")
    
    # Zeige die Tools an
    if server_info.tools:
        typer.echo("\nTools:")
        for tool in server_info.tools:
            typer.echo(f"- {tool.name}: {tool.description}")


@app.command("add")
def add_server(
    name: str = typer.Option(..., "--name", "-n", help="Name des Servers"),
    description: str = typer.Option(..., "--description", "-d", help="Beschreibung des Servers"),
    type: ServerTypeChoice = typer.Option(..., "--type", "-t", help="Typ des Servers"),
    protocol: ServerProtocolChoice = typer.Option(..., "--protocol", "-p", help="Protokoll des Servers"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="URL des Servers"),
    auth_token: Optional[str] = typer.Option(None, "--auth-token", "-a", help="Authentifizierungstoken des Servers"),
    enabled: bool = typer.Option(True, "--enabled/--disabled", help="Ob der Server aktiviert ist"),
    auto_start: bool = typer.Option(False, "--auto-start/--no-auto-start", help="Ob der Server automatisch gestartet werden soll"),
    auto_restart: bool = typer.Option(False, "--auto-restart/--no-auto-restart", help="Ob der Server automatisch neu gestartet werden soll"),
):
    """Füge einen MCP-Server hinzu."""
    # Erstelle die Serverkonfiguration
    server_config = ServerConfig(
        name=name,
        description=description,
        type=ServerType(type.value),
        protocol=ServerProtocol(protocol.value),
        url=url,
        auth_token=auth_token,
        enabled=enabled,
        auto_start=auto_start,
        auto_restart=auto_restart,
    )
    
    # Überprüfe, ob der Server bereits existiert
    if hub_manager.registry_manager.get_server(name):
        typer.echo(f"Server existiert bereits: {name}")
        return
    
    # Installiere den Server
    if not asyncio.run(hub_manager.install_server(server_config)):
        typer.echo(f"Fehler beim Installieren des Servers: {name}")
        return
    
    typer.echo(f"Server hinzugefügt: {name}")


@app.command("remove")
def remove_server(
    server_name: str = typer.Argument(..., help="Name des Servers"),
    force: bool = typer.Option(False, "--force", "-f", help="Erzwinge das Entfernen des Servers"),
):
    """Entferne einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        typer.echo(f"Server nicht gefunden: {server_name}")
        return
    
    # Bestätige das Entfernen
    if not force and not typer.confirm(f"Möchten Sie den Server {server_name} wirklich entfernen?"):
        typer.echo("Abgebrochen.")
        return
    
    # Deinstalliere den Server
    if not asyncio.run(hub_manager.uninstall_server(server_name)):
        typer.echo(f"Fehler beim Deinstallieren des Servers: {server_name}")
        return
    
    typer.echo(f"Server entfernt: {server_name}")


@app.command("start")
def start_server(
    server_name: str = typer.Argument(..., help="Name des Servers"),
):
    """Starte einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        typer.echo(f"Server nicht gefunden: {server_name}")
        return
    
    # Starte den Server
    if not asyncio.run(hub_manager.start_server(server_name)):
        typer.echo(f"Fehler beim Starten des Servers: {server_name}")
        return
    
    typer.echo(f"Server gestartet: {server_name}")


@app.command("stop")
def stop_server(
    server_name: str = typer.Argument(..., help="Name des Servers"),
):
    """Stoppe einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        typer.echo(f"Server nicht gefunden: {server_name}")
        return
    
    # Stoppe den Server
    if not asyncio.run(hub_manager.stop_server(server_name)):
        typer.echo(f"Fehler beim Stoppen des Servers: {server_name}")
        return
    
    typer.echo(f"Server gestoppt: {server_name}")


@app.command("restart")
def restart_server(
    server_name: str = typer.Argument(..., help="Name des Servers"),
):
    """Starte einen MCP-Server neu."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        typer.echo(f"Server nicht gefunden: {server_name}")
        return
    
    # Starte den Server neu
    if not asyncio.run(hub_manager.restart_server(server_name)):
        typer.echo(f"Fehler beim Neustarten des Servers: {server_name}")
        return
    
    typer.echo(f"Server neu gestartet: {server_name}")


@app.command("update")
def update_server(
    server_name: str = typer.Argument(..., help="Name des Servers"),
):
    """Aktualisiere einen MCP-Server."""
    # Überprüfe, ob der Server existiert
    server = hub_manager.registry_manager.get_server(server_name)
    if not server:
        typer.echo(f"Server nicht gefunden: {server_name}")
        return
    
    # Aktualisiere den Server
    if not asyncio.run(hub_manager.update_server(server_name)):
        typer.echo(f"Fehler beim Aktualisieren des Servers: {server_name}")
        return
    
    typer.echo(f"Server aktualisiert: {server_name}")


@app.command("discover")
def discover_servers():
    """Entdecke MCP-Server im Netzwerk."""
    # Entdecke Server
    servers = asyncio.run(hub_manager.discover_servers())
    
    if not servers:
        typer.echo("Keine MCP-Server gefunden.")
        return
    
    # Erstelle eine Tabelle
    typer.echo("Gefundene MCP-Server:")
    typer.echo("Name\tTyp\tProtokoll\tURL\tStatus")
    typer.echo("-" * 80)
    
    # Fülle die Tabelle
    for server in servers:
        typer.echo(f"{server.name}\t{server.type}\t{server.protocol}\t{server.url or '-'}\t{server.status}")
    
    # Frage, ob die Server hinzugefügt werden sollen
    if typer.confirm("Möchten Sie die gefundenen Server zur Registry hinzufügen?"):
        for server in servers:
            # Überprüfe, ob der Server bereits existiert
            if hub_manager.registry_manager.get_server(server.name):
                typer.echo(f"Server existiert bereits: {server.name}")
                continue
            
            # Erstelle die Serverkonfiguration
            server_config = ServerConfig(
                name=server.name,
                description=server.description,
                type=server.type,
                protocol=server.protocol,
                url=server.url,
                enabled=True,
                auto_start=False,
                auto_restart=False,
            )
            
            # Füge den Server zur Registry hinzu
            hub_manager.registry_manager.add_server(server_config)
            typer.echo(f"Server hinzugefügt: {server.name}")


@app.command("repositories")
def list_repositories():
    """Liste alle Repositories auf."""
    repositories = hub_manager.list_repositories()
    
    if not repositories:
        typer.echo("Keine Repositories gefunden.")
        return
    
    # Zeige die Repositories an
    typer.echo("Repositories:")
    for repo in repositories:
        typer.echo(f"- {repo}")


@app.command("add-repository")
def add_repository(
    repo_url: str = typer.Argument(..., help="URL des Repositories"),
):
    """Füge ein Repository hinzu."""
    hub_manager.add_repository(repo_url)
    typer.echo(f"Repository hinzugefügt: {repo_url}")


@app.command("remove-repository")
def remove_repository(
    repo_url: str = typer.Argument(..., help="URL des Repositories"),
    force: bool = typer.Option(False, "--force", "-f", help="Erzwinge das Entfernen des Repositories"),
):
    """Entferne ein Repository."""
    # Überprüfe, ob das Repository existiert
    if repo_url not in hub_manager.list_repositories():
        typer.echo(f"Repository nicht gefunden: {repo_url}")
        return
    
    # Bestätige das Entfernen
    if not force and not typer.confirm(f"Möchten Sie das Repository {repo_url} wirklich entfernen?"):
        typer.echo("Abgebrochen.")
        return
    
    hub_manager.remove_repository(repo_url)
    typer.echo(f"Repository entfernt: {repo_url}")


@app.command("docker-hub-users")
def list_docker_hub_users():
    """Liste alle Docker Hub-Benutzer auf."""
    users = hub_manager.list_docker_hub_users()
    
    if not users:
        typer.echo("Keine Docker Hub-Benutzer gefunden.")
        return
    
    # Zeige die Benutzer an
    typer.echo("Docker Hub-Benutzer:")
    for user in users:
        typer.echo(f"- {user}")


@app.command("add-docker-hub-user")
def add_docker_hub_user(
    username: str = typer.Argument(..., help="Benutzername"),
):
    """Füge einen Docker Hub-Benutzer hinzu."""
    hub_manager.add_docker_hub_user(username)
    typer.echo(f"Docker Hub-Benutzer hinzugefügt: {username}")


@app.command("remove-docker-hub-user")
def remove_docker_hub_user(
    username: str = typer.Argument(..., help="Benutzername"),
    force: bool = typer.Option(False, "--force", "-f", help="Erzwinge das Entfernen des Benutzers"),
):
    """Entferne einen Docker Hub-Benutzer."""
    # Überprüfe, ob der Benutzer existiert
    if username not in hub_manager.list_docker_hub_users():
        typer.echo(f"Docker Hub-Benutzer nicht gefunden: {username}")
        return
    
    # Bestätige das Entfernen
    if not force and not typer.confirm(f"Möchten Sie den Docker Hub-Benutzer {username} wirklich entfernen?"):
        typer.echo("Abgebrochen.")
        return
    
    hub_manager.remove_docker_hub_user(username)
    typer.echo(f"Docker Hub-Benutzer entfernt: {username}")


def main():
    """Haupteinstiegspunkt."""
    app()


if __name__ == "__main__":
    main()