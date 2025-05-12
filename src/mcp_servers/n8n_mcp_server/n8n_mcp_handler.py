"""
MCP-Handler für n8n-API-Anfragen.

Dieses Modul bietet Funktionen zur Verarbeitung von MCP-Anfragen an die n8n-API.
"""

import re
import json
import asyncio
from urllib.parse import quote
from typing import Dict, List, Any, Optional

from .n8n_api_resources import API_RESOURCES, ResourceType
from ..utils.logger import logger

class N8nToolRegistry:
    """Registry für n8n API-Tools."""
    
    def __init__(self):
        self.tools = {}
        
    def register_tool(self, tool_name, handler_func, schema, description=None):
        """Registriere ein neues MCP-Tool."""
        self.tools[tool_name] = {
            "handler": handler_func,
            "schema": schema,
            "description": description or f"Access to n8n {tool_name} API"
        }
        
    def get_tool(self, tool_name):
        """Hole ein registriertes Tool."""
        return self.tools.get(tool_name)
        
    def list_tools(self):
        """Liste alle verfügbaren Tools auf."""
        return [
            {
                "name": name,
                "description": info["description"],
                "parameter_schema": info["schema"]
            }
            for name, info in self.tools.items()
        ]

class N8nAPIClient:
    """Generischer Client für den Zugriff auf die n8n-API."""
    
    def __init__(self, base_url, api_key=None, session=None):
        """Initialisiere den API-Client."""
        self.base_url = base_url
        self.api_key = api_key
        self.session = session
        
    async def request(self, method, path, data=None, params=None):
        """Führe eine generische API-Anfrage aus."""
        url = f"{self.base_url}/api/v1/{path}"
        
        try:
            async with self.session.request(method, url, json=data, params=params) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"n8n API error: {response.status} - {error_text}")
                
                return await response.json()
        except Exception as e:
            logger.error(f"Error making request to n8n API: {e}")
            raise

class N8nMCPHandler:
    """Handler für MCP-Anfragen an die n8n-API."""
    
    def __init__(self, api_client, registry):
        """Initialisiere den MCP-Handler."""
        self.api_client = api_client
        self.registry = registry
        # Erstelle Event (Registry gefüllt)
        self.initialized = asyncio.Event()
        # Fülle die Registry mit allen Tools
        asyncio.create_task(self._initialize_registry())
    
    async def _initialize_registry(self):
        """Initialisiere die Tool-Registry mit allen n8n-API-Tools."""
        from .n8n_tool_generator import generate_all_tools
        
        tools = generate_all_tools()
        
        for tool in tools:
            # Extrahiere Ressourcenname und ggf. Aktion aus dem Tool-Namen
            tool_parts = tool["name"].split("_", 1)
            action = tool_parts[0]  # list, get, create, update, delete
            resource_parts = tool_parts[1].split("_", 1)
            resource_name = resource_parts[0]
            
            resource_action = None
            if len(resource_parts) > 1:
                resource_action = resource_parts[1]
            
            # Erstelle Handler-Funktion für dieses Tool
            handler = self._create_handler_for_tool(
                action, resource_name, resource_action,
                API_RESOURCES[resource_name]
            )
            
            # Registriere das Tool
            self.registry.register_tool(
                tool["name"],
                handler,
                tool["parameter_schema"],
                tool["description"]
            )
        
        # Markiere die Registry als initialisiert
        self.initialized.set()
        logger.info(f"Initialized {len(self.registry.tools)} API tools")
    
    def _create_handler_for_tool(self, action, resource_name, resource_action, resource_info):
        """Erstelle einen Handler für ein spezifisches Tool."""
        
        # Mapping von action zu HTTP-Methode
        method_map = {
            "list": "GET",
            "get": "GET",
            "create": "POST",
            "update": "PUT",
            "delete": "DELETE"
        }
        
        # Standardmethode festlegen
        method = method_map.get(action, "GET")
        
        # Pfad basierend auf Aktion festlegen
        if resource_action and resource_action in resource_info.get("actions", {}):
            # Spezielle Aktion
            action_info = resource_info["actions"][resource_action]
            path_template = action_info["path"]
            method = action_info["method"]
        elif action == "list":
            # Liste abrufen
            path_template = resource_info["path"]
        elif action == "create":
            # Neue Ressource erstellen
            path_template = resource_info["path"]
        else:
            # Einzelne Ressource (get, update, delete)
            path_template = f"{resource_info['path']}/{{id}}"
        
        # Handler-Funktion erstellen
        async def handler(arguments):
            await self.initialized.wait()  # Warten, bis die Registry initialisiert ist
            
            # Parameter vorbereiten
            params = {}
            data = None
            
            # ID in der Pfad-URL ersetzen, falls vorhanden
            path = path_template
            if "{id}" in path and "id" in arguments:
                path = path.replace("{id}", quote(str(arguments["id"])))
            
            # Filter-Parameter für Listenabfragen
            if action == "list" and "filter" in arguments:
                params.update(arguments["filter"])
                
                # Pagination
                if "skip" in arguments:
                    params["skip"] = arguments["skip"]
                if "take" in arguments:
                    params["take"] = arguments["take"]
                    
                # Sortierung
                if "sort" in arguments:
                    params["orderBy"] = arguments["sort"]
            
            # Daten für Create/Update/Action
            if "data" in arguments:
                data = arguments["data"]
            
            # API-Anfrage ausführen
            result = await self.api_client.request(method, path, data=data, params=params)
            
            return result
        
        return handler
