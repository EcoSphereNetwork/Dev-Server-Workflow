"""
Hilfsfunktionen für MCP-Server.
"""

import os
import sys
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union

from .client import MCPClient
from .error_handling import MCPConnectionError, MCPServerError
from ..common.docker_utils import (
    check_docker_running,
    check_docker_compose_installed,
    get_docker_compose_command,
    start_docker_compose,
    stop_docker_compose,
    restart_docker_compose,
    get_docker_container_id,
    is_docker_container_running,
    start_docker_container,
    stop_docker_container,
    restart_docker_container,
    get_docker_container_logs,
    run_docker_command
)

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp-utils')


def check_mcp_servers_running() -> Tuple[bool, List[str]]:
    """
    Überprüfe, ob MCP-Server laufen.

    Returns:
        Tuple mit (Laufen MCP-Server, Liste der laufenden MCP-Server).
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return False, []
        
        running_containers = result.stdout.strip().split('\n')
        mcp_servers = [c for c in running_containers if c.startswith('mcp-')]
        
        return len(mcp_servers) > 0, mcp_servers
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen der MCP-Server: {e}")
        return False, []


def start_mcp_servers(compose_file: str, extended: bool = False) -> bool:
    """
    Starte die MCP-Server.

    Args:
        compose_file: Pfad zur Docker Compose Datei.
        extended: Ob die erweiterte Version gestartet werden soll.

    Returns:
        True, wenn erfolgreich, sonst False.
    """
    result = start_docker_compose(compose_file, extended)
    if result:
        logger.info("MCP-Server wurden erfolgreich gestartet.")
    return result


def stop_mcp_servers(compose_file: str) -> bool:
    """
    Stoppe die MCP-Server.

    Args:
        compose_file: Pfad zur Docker Compose Datei.

    Returns:
        True, wenn erfolgreich, sonst False.
    """
    result = stop_docker_compose(compose_file)
    if result:
        logger.info("MCP-Server wurden erfolgreich gestoppt.")
    return result


def restart_mcp_servers(compose_file: str) -> bool:
    """
    Starte die MCP-Server neu.

    Args:
        compose_file: Pfad zur Docker Compose Datei.

    Returns:
        True, wenn erfolgreich, sonst False.
    """
    result = restart_docker_compose(compose_file)
    if result:
        logger.info("MCP-Server wurden erfolgreich neu gestartet.")
    return result


def check_server_status(server_url: str) -> bool:
    """
    Überprüfe den Status eines MCP-Servers.

    Args:
        server_url: URL des Servers.

    Returns:
        True, wenn der Server online ist, sonst False.
    """
    try:
        client = MCPClient(server_url=server_url)
        result = client.test_connection()
        return result[0]
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen des Server-Status: {e}")
        return False


def start_server(server_name: str) -> bool:
    """
    Starte einen MCP-Server.

    Args:
        server_name: Name des Servers.

    Returns:
        True, wenn erfolgreich, sonst False.
    """
    container_name = f"mcp-{server_name}"
    result = start_docker_container(container_name)
    if result:
        logger.info(f"Server {server_name} wurde erfolgreich gestartet.")
    return result


def stop_server(server_name: str) -> bool:
    """
    Stoppe einen MCP-Server.

    Args:
        server_name: Name des Servers.

    Returns:
        True, wenn erfolgreich, sonst False.
    """
    container_name = f"mcp-{server_name}"
    result = stop_docker_container(container_name)
    if result:
        logger.info(f"Server {server_name} wurde erfolgreich gestoppt.")
    return result


def restart_server(server_name: str) -> bool:
    """
    Starte einen MCP-Server neu.

    Args:
        server_name: Name des Servers.

    Returns:
        True, wenn erfolgreich, sonst False.
    """
    container_name = f"mcp-{server_name}"
    result = restart_docker_container(container_name)
    if result:
        logger.info(f"Server {server_name} wurde erfolgreich neu gestartet.")
    return result


def get_server_logs(server_name: str, lines: int = 100) -> str:
    """
    Rufe die Logs eines MCP-Servers ab.

    Args:
        server_name: Name des Servers.
        lines: Anzahl der Zeilen, die abgerufen werden sollen.

    Returns:
        Logs des Servers.
    """
    container_name = f"mcp-{server_name}"
    return get_docker_container_logs(container_name, lines)