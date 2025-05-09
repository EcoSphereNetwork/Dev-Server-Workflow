"""
Tests für das n8n-Client-Modul des n8n MCP Servers.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.mcp_servers.n8n_mcp_server.core.n8n_client import N8nClient


@pytest.fixture
def n8n_client():
    """Fixture für einen n8n-Client."""
    client = N8nClient()
    client.base_url = "http://localhost:5678"
    client.api_key = "test-api-key"
    return client


@pytest.mark.asyncio
async def test_list_workflows(n8n_client):
    """Teste das Auflisten von Workflows."""
    # Erstelle Mock-Workflows
    workflows = [
        {
            "id": "1",
            "name": "Workflow 1",
            "active": True,
            "nodes": [],
            "connections": {},
            "settings": {},
            "tags": [],
            "created_at": "2021-01-01T00:00:00Z",
            "updated_at": "2021-01-01T00:00:00Z",
        },
        {
            "id": "2",
            "name": "Workflow 2",
            "active": False,
            "nodes": [],
            "connections": {},
            "settings": {},
            "tags": [],
            "created_at": "2021-01-01T00:00:00Z",
            "updated_at": "2021-01-01T00:00:00Z",
        },
    ]
    
    # Mocke die _make_request-Methode
    with patch.object(n8n_client, "_make_request", new_callable=AsyncMock) as mock_request:
        # Setze den Rückgabewert
        mock_request.return_value = {"data": workflows}
        
        # Rufe die list_workflows-Methode auf
        result = await n8n_client.list_workflows()
        
        # Überprüfe, ob die _make_request-Methode aufgerufen wurde
        mock_request.assert_called_once_with("GET", "workflows", params={})
        
        # Überprüfe, ob die Rückgabe korrekt ist
        assert result == workflows


@pytest.mark.asyncio
async def test_get_workflow(n8n_client):
    """Teste das Abrufen eines Workflows."""
    # Erstelle einen Mock-Workflow
    workflow = {
        "id": "1",
        "name": "Workflow 1",
        "active": True,
        "nodes": [],
        "connections": {},
        "settings": {},
        "tags": [],
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2021-01-01T00:00:00Z",
    }
    
    # Mocke die _make_request-Methode
    with patch.object(n8n_client, "_make_request", new_callable=AsyncMock) as mock_request:
        # Setze den Rückgabewert
        mock_request.return_value = workflow
        
        # Rufe die get_workflow-Methode auf
        result = await n8n_client.get_workflow("1")
        
        # Überprüfe, ob die _make_request-Methode aufgerufen wurde
        mock_request.assert_called_once_with("GET", "workflows/1")
        
        # Überprüfe, ob die Rückgabe korrekt ist
        assert result == workflow


@pytest.mark.asyncio
async def test_run_workflow(n8n_client):
    """Teste das Ausführen eines Workflows."""
    # Erstelle ein Mock-Ergebnis
    result = {
        "data": {
            "result": "success",
        },
    }
    
    # Mocke die _make_request-Methode
    with patch.object(n8n_client, "_make_request", new_callable=AsyncMock) as mock_request:
        # Setze den Rückgabewert
        mock_request.return_value = result
        
        # Rufe die run_workflow-Methode auf
        response = await n8n_client.run_workflow("1", {"input": "test"})
        
        # Überprüfe, ob die _make_request-Methode aufgerufen wurde
        mock_request.assert_called_once_with(
            "POST",
            "workflows/run",
            data={
                "workflowData": {
                    "id": "1",
                },
                "data": {"input": "test"},
            },
        )
        
        # Überprüfe, ob die Rückgabe korrekt ist
        assert response == result


@pytest.mark.asyncio
async def test_create_workflow(n8n_client):
    """Teste das Erstellen eines Workflows."""
    # Erstelle einen Mock-Workflow
    workflow = {
        "id": "1",
        "name": "Workflow 1",
        "active": True,
        "nodes": [],
        "connections": {},
        "settings": {},
        "tags": [],
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2021-01-01T00:00:00Z",
    }
    
    # Mocke die _make_request-Methode
    with patch.object(n8n_client, "_make_request", new_callable=AsyncMock) as mock_request:
        # Setze den Rückgabewert
        mock_request.return_value = workflow
        
        # Rufe die create_workflow-Methode auf
        result = await n8n_client.create_workflow("Workflow 1", [], [], True, ["tag1"])
        
        # Überprüfe, ob die _make_request-Methode aufgerufen wurde
        mock_request.assert_called_once_with(
            "POST",
            "workflows",
            data={
                "name": "Workflow 1",
                "nodes": [],
                "connections": [],
                "active": True,
                "tags": ["tag1"],
            },
        )
        
        # Überprüfe, ob die Rückgabe korrekt ist
        assert result == workflow


@pytest.mark.asyncio
async def test_update_workflow(n8n_client):
    """Teste das Aktualisieren eines Workflows."""
    # Erstelle einen Mock-Workflow
    workflow = {
        "id": "1",
        "name": "Workflow 1",
        "active": True,
        "nodes": [],
        "connections": {},
        "settings": {},
        "tags": [],
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2021-01-01T00:00:00Z",
    }
    
    # Mocke die get_workflow-Methode
    with patch.object(n8n_client, "get_workflow", new_callable=AsyncMock) as mock_get:
        # Setze den Rückgabewert
        mock_get.return_value = workflow
        
        # Mocke die _make_request-Methode
        with patch.object(n8n_client, "_make_request", new_callable=AsyncMock) as mock_request:
            # Setze den Rückgabewert
            mock_request.return_value = workflow
            
            # Rufe die update_workflow-Methode auf
            result = await n8n_client.update_workflow("1", "New Name", [], [], True, ["tag1"])
            
            # Überprüfe, ob die get_workflow-Methode aufgerufen wurde
            mock_get.assert_called_once_with("1")
            
            # Überprüfe, ob die _make_request-Methode aufgerufen wurde
            mock_request.assert_called_once_with(
                "PUT",
                "workflows/1",
                data={
                    "name": "New Name",
                    "nodes": [],
                    "connections": {},
                    "active": True,
                    "tags": ["tag1"],
                },
            )
            
            # Überprüfe, ob die Rückgabe korrekt ist
            assert result == workflow


@pytest.mark.asyncio
async def test_delete_workflow(n8n_client):
    """Teste das Löschen eines Workflows."""
    # Mocke die _make_request-Methode
    with patch.object(n8n_client, "_make_request", new_callable=AsyncMock) as mock_request:
        # Setze den Rückgabewert
        mock_request.return_value = {}
        
        # Rufe die delete_workflow-Methode auf
        result = await n8n_client.delete_workflow("1")
        
        # Überprüfe, ob die _make_request-Methode aufgerufen wurde
        mock_request.assert_called_once_with("DELETE", "workflows/1")
        
        # Überprüfe, ob die Rückgabe korrekt ist
        assert result == True