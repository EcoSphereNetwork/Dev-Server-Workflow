"""
Tests für das Docker-Executor-Modul des Docker MCP Servers.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from src.mcp_servers.docker_mcp.core.docker_executor import DockerExecutor


@pytest.fixture
def docker_client_mock():
    """Fixture für einen gemockten Docker-Client."""
    with patch("docker.DockerClient") as mock:
        yield mock


@pytest.fixture
def docker_executor(docker_client_mock):
    """Fixture für einen Docker-Executor."""
    with patch("src.mcp_servers.docker_mcp.core.docker_executor.DockerExecutor._create_docker_client") as mock_create:
        # Erstelle einen Mock-Client
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        # Erstelle den Docker-Executor
        executor = DockerExecutor()
        
        # Setze den Mock-Client
        executor.client = mock_client
        
        yield executor


def test_list_containers(docker_executor):
    """Teste das Auflisten von Containern."""
    # Erstelle Mock-Container
    container1 = MagicMock()
    container1.id = "container1"
    container1.name = "container1"
    container1.status = "running"
    container1.attrs = {"Created": "2021-01-01T00:00:00Z"}
    container1.ports = {}
    container1.labels = {}
    container1.image.tags = ["image1"]
    
    container2 = MagicMock()
    container2.id = "container2"
    container2.name = "container2"
    container2.status = "exited"
    container2.attrs = {"Created": "2021-01-01T00:00:00Z"}
    container2.ports = {}
    container2.labels = {}
    container2.image.tags = []
    container2.image.id = "image2"
    
    # Setze den Rückgabewert für containers.list
    docker_executor.client.containers.list.return_value = [container1, container2]
    
    # Rufe die list_containers-Methode auf
    containers = docker_executor.list_containers()
    
    # Überprüfe, ob die containers.list-Methode aufgerufen wurde
    docker_executor.client.containers.list.assert_called_once_with(all=False)
    
    # Überprüfe, ob die Rückgabe korrekt ist
    assert len(containers) == 2
    assert containers[0]["id"] == "container1"
    assert containers[0]["name"] == "container1"
    assert containers[0]["status"] == "running"
    assert containers[0]["image"] == "image1"
    assert containers[1]["id"] == "container2"
    assert containers[1]["name"] == "container2"
    assert containers[1]["status"] == "exited"
    assert containers[1]["image"] == "image2"


def test_get_container(docker_executor):
    """Teste das Abrufen eines Containers."""
    # Erstelle einen Mock-Container
    container = MagicMock()
    container.id = "container1"
    container.name = "container1"
    container.status = "running"
    container.attrs = {
        "Created": "2021-01-01T00:00:00Z",
        "Config": {
            "Cmd": ["cmd"],
            "Entrypoint": ["entrypoint"],
            "Env": ["env"],
            "Volumes": {},
        },
        "HostConfig": {
            "NetworkMode": "bridge",
            "RestartPolicy": {"Name": "always"},
        },
        "Mounts": [],
    }
    container.ports = {}
    container.labels = {}
    container.image.tags = ["image1"]
    
    # Setze den Rückgabewert für containers.get
    docker_executor.client.containers.get.return_value = container
    
    # Rufe die get_container-Methode auf
    container_dict = docker_executor.get_container("container1")
    
    # Überprüfe, ob die containers.get-Methode aufgerufen wurde
    docker_executor.client.containers.get.assert_called_once_with("container1")
    
    # Überprüfe, ob die Rückgabe korrekt ist
    assert container_dict["id"] == "container1"
    assert container_dict["name"] == "container1"
    assert container_dict["status"] == "running"
    assert container_dict["image"] == "image1"
    assert container_dict["command"] == ["cmd"]
    assert container_dict["entrypoint"] == ["entrypoint"]
    assert container_dict["env"] == ["env"]
    assert container_dict["volumes"] == {}
    assert container_dict["network_mode"] == "bridge"
    assert container_dict["restart_policy"] == {"Name": "always"}
    assert container_dict["mounts"] == []


def test_start_container(docker_executor):
    """Teste das Starten eines Containers."""
    # Erstelle einen Mock-Container
    container = MagicMock()
    
    # Setze den Rückgabewert für containers.get
    docker_executor.client.containers.get.return_value = container
    
    # Rufe die start_container-Methode auf
    result = docker_executor.start_container("container1")
    
    # Überprüfe, ob die containers.get-Methode aufgerufen wurde
    docker_executor.client.containers.get.assert_called_once_with("container1")
    
    # Überprüfe, ob die start-Methode aufgerufen wurde
    container.start.assert_called_once()
    
    # Überprüfe, ob die Rückgabe korrekt ist
    assert result == True


def test_stop_container(docker_executor):
    """Teste das Stoppen eines Containers."""
    # Erstelle einen Mock-Container
    container = MagicMock()
    
    # Setze den Rückgabewert für containers.get
    docker_executor.client.containers.get.return_value = container
    
    # Rufe die stop_container-Methode auf
    result = docker_executor.stop_container("container1")
    
    # Überprüfe, ob die containers.get-Methode aufgerufen wurde
    docker_executor.client.containers.get.assert_called_once_with("container1")
    
    # Überprüfe, ob die stop-Methode aufgerufen wurde
    container.stop.assert_called_once()
    
    # Überprüfe, ob die Rückgabe korrekt ist
    assert result == True


def test_restart_container(docker_executor):
    """Teste das Neustarten eines Containers."""
    # Erstelle einen Mock-Container
    container = MagicMock()
    
    # Setze den Rückgabewert für containers.get
    docker_executor.client.containers.get.return_value = container
    
    # Rufe die restart_container-Methode auf
    result = docker_executor.restart_container("container1")
    
    # Überprüfe, ob die containers.get-Methode aufgerufen wurde
    docker_executor.client.containers.get.assert_called_once_with("container1")
    
    # Überprüfe, ob die restart-Methode aufgerufen wurde
    container.restart.assert_called_once()
    
    # Überprüfe, ob die Rückgabe korrekt ist
    assert result == True


def test_remove_container(docker_executor):
    """Teste das Entfernen eines Containers."""
    # Erstelle einen Mock-Container
    container = MagicMock()
    
    # Setze den Rückgabewert für containers.get
    docker_executor.client.containers.get.return_value = container
    
    # Rufe die remove_container-Methode auf
    result = docker_executor.remove_container("container1")
    
    # Überprüfe, ob die containers.get-Methode aufgerufen wurde
    docker_executor.client.containers.get.assert_called_once_with("container1")
    
    # Überprüfe, ob die remove-Methode aufgerufen wurde
    container.remove.assert_called_once_with(force=False)
    
    # Überprüfe, ob die Rückgabe korrekt ist
    assert result == True