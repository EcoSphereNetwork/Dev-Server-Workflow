"""
Tool-Generator für n8n-API-Ressourcen.

Dieses Modul generiert automatisch MCP-Tools für alle definierten n8n-API-Ressourcen.
"""

import json
from .n8n_api_resources import API_RESOURCES, ResourceType

def generate_list_schema(resource_name, resource_info):
    """Generiere das Schema für eine Listenoperation."""
    return {
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "description": f"Filter-Kriterien für {resource_name}"
            },
            "skip": {
                "type": "integer",
                "description": "Anzahl der zu überspringenden Einträge (Pagination)"
            },
            "take": {
                "type": "integer",
                "description": "Anzahl der abzurufenden Einträge (Pagination)"
            },
            "sort": {
                "type": "object",
                "description": "Sortierkriterien"
            }
        }
    }

def generate_get_schema(resource_name):
    """Generiere das Schema für eine Get-Operation."""
    return {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": f"ID des {resource_name}-Objekts"
            }
        },
        "required": ["id"]
    }

def generate_create_schema(resource_name):
    """Generiere das Schema für eine Create-Operation."""
    return {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "description": f"Daten für das neue {resource_name}-Objekt"
            }
        },
        "required": ["data"]
    }

def generate_update_schema(resource_name):
    """Generiere das Schema für eine Update-Operation."""
    return {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": f"ID des {resource_name}-Objekts"
            },
            "data": {
                "type": "object",
                "description": f"Aktualisierte Daten für das {resource_name}-Objekt"
            }
        },
        "required": ["id", "data"]
    }

def generate_delete_schema(resource_name):
    """Generiere das Schema für eine Delete-Operation."""
    return {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": f"ID des zu löschenden {resource_name}-Objekts"
            }
        },
        "required": ["id"]
    }

def generate_action_schema(resource_name, action_name, action_info):
    """Generiere das Schema für eine Aktion."""
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    # Wenn die Aktion einen ID-Parameter benötigt
    if "{id}" in action_info["path"]:
        schema["properties"]["id"] = {
            "type": "string",
            "description": f"ID des {resource_name}-Objekts"
        }
        schema["required"].append("id")
    
    # Für Aktionen, die Daten erfordern (z.B. POST-Anfragen)
    if action_info["method"] in ["POST", "PUT"]:
        schema["properties"]["data"] = {
            "type": "object",
            "description": f"Daten für die {action_name}-Aktion auf {resource_name}"
        }
    
    return schema

def generate_tools_for_resource(resource_name, resource_info):
    """Generiere alle Tools für eine Ressource."""
    tools = []
    
    # Liste von Ressourcen abrufen
    if "GET" in resource_info.get("methods", []):
        tools.append({
            "name": f"list_{resource_name}",
            "description": f"Liste alle {resource_name} auf",
            "parameter_schema": generate_list_schema(resource_name, resource_info)
        })
    
    # Einzelne Ressource abrufen
    if "GET" in resource_info.get("singleton_methods", []):
        tools.append({
            "name": f"get_{resource_name}",
            "description": f"Rufe ein einzelnes {resource_name}-Objekt ab",
            "parameter_schema": generate_get_schema(resource_name)
        })
    
    # Ressource erstellen
    if "POST" in resource_info.get("methods", []):
        tools.append({
            "name": f"create_{resource_name}",
            "description": f"Erstelle ein neues {resource_name}-Objekt",
            "parameter_schema": generate_create_schema(resource_name)
        })
    
    # Ressource aktualisieren
    if "PUT" in resource_info.get("singleton_methods", []):
        tools.append({
            "name": f"update_{resource_name}",
            "description": f"Aktualisiere ein {resource_name}-Objekt",
            "parameter_schema": generate_update_schema(resource_name)
        })
    
    # Ressource löschen
    if "DELETE" in resource_info.get("singleton_methods", []):
        tools.append({
            "name": f"delete_{resource_name}",
            "description": f"Lösche ein {resource_name}-Objekt",
            "parameter_schema": generate_delete_schema(resource_name)
        })
    
    # Aktionen für diese Ressource
    for action_name, action_info in resource_info.get("actions", {}).items():
        tools.append({
            "name": f"{resource_name}_{action_name}",
            "description": f"Führe die Aktion {action_name} auf {resource_name} aus",
            "parameter_schema": generate_action_schema(resource_name, action_name, action_info)
        })
    
    return tools

def generate_all_tools():
    """Generiere alle Tools für alle Ressourcen."""
    all_tools = []
    
    for resource_name, resource_info in API_RESOURCES.items():
        tools = generate_tools_for_resource(resource_name, resource_info)
        all_tools.extend(tools)
    
    return all_tools
