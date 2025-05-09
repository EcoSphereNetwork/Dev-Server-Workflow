"""
Tests für das Registry-Modul des MCP Hub.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.mcp_hub.core.registry import RegistryManager
from src.mcp_hub.models.server import ServerConfig, ServerType, ServerProtocol


@pytest.fixture
def registry_file():
    """Fixture für eine temporäre Registry-Datei."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(b"{}")
    
    yield Path(f.name)
    
    # Aufräumen
    os.unlink(f.name)


@pytest.fixture
def registry_manager(registry_file):
    """Fixture für einen Registry-Manager."""
    return RegistryManager(registry_file=registry_file)


def test_add_repository(registry_manager):
    """Teste das Hinzufügen eines Repositories."""
    # Füge ein Repository hinzu
    repo_url = "https://github.com/example/repo"
    registry_manager.add_repository(repo_url)
    
    # Überprüfe, ob das Repository hinzugefügt wurde
    assert repo_url in registry_manager.registry.repositories


def test_remove_repository(registry_manager):
    """Teste das Entfernen eines Repositories."""
    # Füge ein Repository hinzu
    repo_url = "https://github.com/example/repo"
    registry_manager.add_repository(repo_url)
    
    # Entferne das Repository
    registry_manager.remove_repository(repo_url)
    
    # Überprüfe, ob das Repository entfernt wurde
    assert repo_url not in registry_manager.registry.repositories


def test_add_docker_hub_user(registry_manager):
    """Teste das Hinzufügen eines Docker Hub-Benutzers."""
    # Füge einen Docker Hub-Benutzer hinzu
    username = "example"
    registry_manager.add_docker_hub_user(username)
    
    # Überprüfe, ob der Benutzer hinzugefügt wurde
    assert username in registry_manager.registry.docker_hub_users


def test_remove_docker_hub_user(registry_manager):
    """Teste das Entfernen eines Docker Hub-Benutzers."""
    # Füge einen Docker Hub-Benutzer hinzu
    username = "example"
    registry_manager.add_docker_hub_user(username)
    
    # Entferne den Benutzer
    registry_manager.remove_docker_hub_user(username)
    
    # Überprüfe, ob der Benutzer entfernt wurde
    assert username not in registry_manager.registry.docker_hub_users


def test_add_server(registry_manager):
    """Teste das Hinzufügen eines Servers."""
    # Erstelle einen Server
    server = ServerConfig(
        name="test-server",
        description="Test Server",
        type=ServerType.DOCKER,
        protocol=ServerProtocol.HTTP,
        url="http://localhost:3458",
        enabled=True,
    )
    
    # Füge den Server hinzu
    registry_manager.add_server(server)
    
    # Überprüfe, ob der Server hinzugefügt wurde
    assert "test-server" in registry_manager.registry.servers
    assert registry_manager.registry.servers["test-server"].name == "test-server"
    assert registry_manager.registry.servers["test-server"].description == "Test Server"
    assert registry_manager.registry.servers["test-server"].type == ServerType.DOCKER
    assert registry_manager.registry.servers["test-server"].protocol == ServerProtocol.HTTP
    assert registry_manager.registry.servers["test-server"].url == "http://localhost:3458"
    assert registry_manager.registry.servers["test-server"].enabled == True


def test_remove_server(registry_manager):
    """Teste das Entfernen eines Servers."""
    # Erstelle einen Server
    server = ServerConfig(
        name="test-server",
        description="Test Server",
        type=ServerType.DOCKER,
        protocol=ServerProtocol.HTTP,
        url="http://localhost:3458",
        enabled=True,
    )
    
    # Füge den Server hinzu
    registry_manager.add_server(server)
    
    # Entferne den Server
    registry_manager.remove_server("test-server")
    
    # Überprüfe, ob der Server entfernt wurde
    assert "test-server" not in registry_manager.registry.servers


def test_get_server(registry_manager):
    """Teste das Abrufen eines Servers."""
    # Erstelle einen Server
    server = ServerConfig(
        name="test-server",
        description="Test Server",
        type=ServerType.DOCKER,
        protocol=ServerProtocol.HTTP,
        url="http://localhost:3458",
        enabled=True,
    )
    
    # Füge den Server hinzu
    registry_manager.add_server(server)
    
    # Erhalte den Server
    retrieved_server = registry_manager.get_server("test-server")
    
    # Überprüfe, ob der Server korrekt abgerufen wurde
    assert retrieved_server is not None
    assert retrieved_server.name == "test-server"
    assert retrieved_server.description == "Test Server"
    assert retrieved_server.type == ServerType.DOCKER
    assert retrieved_server.protocol == ServerProtocol.HTTP
    assert retrieved_server.url == "http://localhost:3458"
    assert retrieved_server.enabled == True


def test_list_servers(registry_manager):
    """Teste das Auflisten von Servern."""
    # Erstelle Server
    server1 = ServerConfig(
        name="test-server-1",
        description="Test Server 1",
        type=ServerType.DOCKER,
        protocol=ServerProtocol.HTTP,
        url="http://localhost:3458",
        enabled=True,
    )
    
    server2 = ServerConfig(
        name="test-server-2",
        description="Test Server 2",
        type=ServerType.N8N,
        protocol=ServerProtocol.HTTP,
        url="http://localhost:3456",
        enabled=True,
    )
    
    # Füge die Server hinzu
    registry_manager.add_server(server1)
    registry_manager.add_server(server2)
    
    # Liste die Server auf
    servers = registry_manager.list_servers()
    
    # Überprüfe, ob die Server korrekt aufgelistet wurden
    assert len(servers) == 2
    assert any(s.name == "test-server-1" for s in servers)
    assert any(s.name == "test-server-2" for s in servers)


@pytest.mark.asyncio
async def test_discover_servers(registry_manager):
    """Teste das Entdecken von Servern."""
    # Mocke die _discover_http_servers-Methode
    with patch.object(registry_manager, "_discover_http_servers") as mock_discover_http:
        # Setze den Rückgabewert
        mock_discover_http.return_value = []
        
        # Rufe die discover_servers-Methode auf
        servers = await registry_manager.discover_servers()
        
        # Überprüfe, ob die _discover_http_servers-Methode aufgerufen wurde
        mock_discover_http.assert_called_once()
        
        # Überprüfe, ob die Rückgabe korrekt ist
        assert servers == []