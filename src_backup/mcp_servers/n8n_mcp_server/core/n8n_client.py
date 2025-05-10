"""
n8n-Client-Modul für den n8n MCP Server.

Dieses Modul bietet Funktionen zur Interaktion mit n8n.
"""

import os
import json
import logging
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from ..utils.logger import logger
from ..core.config import settings


class N8nClient:
    """n8n-Client-Klasse."""
    
    def __init__(self):
        """Initialisiere den n8n-Client."""
        self.base_url = settings.N8N_URL
        self.api_key = settings.N8N_API_KEY
        self.workflow_cache = {}
        self.workflow_cache_enabled = settings.WORKFLOW_CACHE_ENABLED
        self.workflow_cache_ttl = settings.WORKFLOW_CACHE_TTL
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Führe eine Anfrage an die n8n-API aus.
        
        Args:
            method: HTTP-Methode
            endpoint: API-Endpunkt
            data: Anfragedaten
            params: Anfrageparameter
            
        Returns:
            Antwort der API
            
        Raises:
            Exception: Wenn ein Fehler während der Anfrage auftritt
        """
        url = f"{self.base_url}/api/v1/{endpoint}"
        
        headers = {}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, json=data, params=params, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(f"n8n API error: {response.status} - {error_text}")
                    
                    return await response.json()
        except Exception as e:
            logger.error(f"Error making request to n8n API: {e}")
            raise
    
    async def list_workflows(self, tags: Optional[List[str]] = None, active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Liste alle Workflows auf.
        
        Args:
            tags: Filter nach Tags
            active: Filter nach aktiven Workflows
            
        Returns:
            Liste der Workflows
        """
        params = {}
        if tags:
            params["tags"] = ",".join(tags)
        if active is not None:
            params["active"] = "true" if active else "false"
        
        try:
            response = await self._make_request("GET", "workflows", params=params)
            return response["data"]
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise
    
    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Erhalte einen Workflow.
        
        Args:
            workflow_id: ID des Workflows
            
        Returns:
            Der Workflow
        """
        # Überprüfe, ob der Workflow im Cache ist
        if self.workflow_cache_enabled and workflow_id in self.workflow_cache:
            cache_entry = self.workflow_cache[workflow_id]
            
            # Überprüfe, ob der Cache noch gültig ist
            if datetime.now().timestamp() - cache_entry["timestamp"] < self.workflow_cache_ttl:
                return cache_entry["workflow"]
        
        try:
            workflow = await self._make_request("GET", f"workflows/{workflow_id}")
            
            # Speichere den Workflow im Cache
            if self.workflow_cache_enabled:
                self.workflow_cache[workflow_id] = {
                    "workflow": workflow,
                    "timestamp": datetime.now().timestamp(),
                }
            
            return workflow
        except Exception as e:
            logger.error(f"Error getting workflow {workflow_id}: {e}")
            raise
    
    async def run_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Führe einen Workflow aus.
        
        Args:
            workflow_id: ID des Workflows
            parameters: Parameter für den Workflow
            
        Returns:
            Das Ergebnis der Workflow-Ausführung
        """
        try:
            data = {
                "workflowData": {
                    "id": workflow_id,
                },
            }
            
            if parameters:
                data["data"] = parameters
            
            return await self._make_request("POST", "workflows/run", data=data)
        except Exception as e:
            logger.error(f"Error running workflow {workflow_id}: {e}")
            raise
    
    async def create_workflow(self, name: str, nodes: List[Dict[str, Any]], connections: List[Dict[str, Any]], active: bool = False, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Erstelle einen Workflow.
        
        Args:
            name: Name des Workflows
            nodes: Knoten des Workflows
            connections: Verbindungen des Workflows
            active: Ob der Workflow aktiv sein soll
            tags: Tags für den Workflow
            
        Returns:
            Der erstellte Workflow
        """
        try:
            data = {
                "name": name,
                "nodes": nodes,
                "connections": connections,
                "active": active,
            }
            
            if tags:
                data["tags"] = tags
            
            return await self._make_request("POST", "workflows", data=data)
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    async def update_workflow(self, workflow_id: str, name: Optional[str] = None, nodes: Optional[List[Dict[str, Any]]] = None, connections: Optional[List[Dict[str, Any]]] = None, active: Optional[bool] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Aktualisiere einen Workflow.
        
        Args:
            workflow_id: ID des Workflows
            name: Neuer Name des Workflows
            nodes: Neue Knoten des Workflows
            connections: Neue Verbindungen des Workflows
            active: Ob der Workflow aktiv sein soll
            tags: Neue Tags für den Workflow
            
        Returns:
            Der aktualisierte Workflow
        """
        try:
            # Erhalte den aktuellen Workflow
            workflow = await self.get_workflow(workflow_id)
            
            # Aktualisiere die Felder
            data = {
                "name": name or workflow["name"],
                "nodes": nodes or workflow["nodes"],
                "connections": connections or workflow["connections"],
                "active": active if active is not None else workflow["active"],
            }
            
            if tags:
                data["tags"] = tags
            
            # Aktualisiere den Workflow
            updated_workflow = await self._make_request("PUT", f"workflows/{workflow_id}", data=data)
            
            # Aktualisiere den Cache
            if self.workflow_cache_enabled and workflow_id in self.workflow_cache:
                self.workflow_cache[workflow_id] = {
                    "workflow": updated_workflow,
                    "timestamp": datetime.now().timestamp(),
                }
            
            return updated_workflow
        except Exception as e:
            logger.error(f"Error updating workflow {workflow_id}: {e}")
            raise
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Lösche einen Workflow.
        
        Args:
            workflow_id: ID des Workflows
            
        Returns:
            True, wenn der Workflow erfolgreich gelöscht wurde, sonst False
        """
        try:
            await self._make_request("DELETE", f"workflows/{workflow_id}")
            
            # Entferne den Workflow aus dem Cache
            if self.workflow_cache_enabled and workflow_id in self.workflow_cache:
                del self.workflow_cache[workflow_id]
            
            return True
        except Exception as e:
            logger.error(f"Error deleting workflow {workflow_id}: {e}")
            return False
    
    async def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Aktiviere einen Workflow.
        
        Args:
            workflow_id: ID des Workflows
            
        Returns:
            Der aktivierte Workflow
        """
        try:
            return await self.update_workflow(workflow_id, active=True)
        except Exception as e:
            logger.error(f"Error activating workflow {workflow_id}: {e}")
            raise
    
    async def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Deaktiviere einen Workflow.
        
        Args:
            workflow_id: ID des Workflows
            
        Returns:
            Der deaktivierte Workflow
        """
        try:
            return await self.update_workflow(workflow_id, active=False)
        except Exception as e:
            logger.error(f"Error deactivating workflow {workflow_id}: {e}")
            raise