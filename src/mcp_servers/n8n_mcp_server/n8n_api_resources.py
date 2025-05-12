"""
Kartierung der n8n-API-Ressourcen.

Dieses Modul definiert alle verfügbaren n8n-API-Endpunkte und ihre Eigenschaften.
"""

from enum import Enum

class ResourceType(Enum):
    """Typen von n8n-API-Ressourcen."""
    COLLECTION = "collection"  # Liste von Ressourcen abrufbar (GET /resource)
    SINGLETON = "singleton"    # Einzelne Ressource (GET /resource/{id})
    ACTION = "action"          # Aktion auf Ressource (POST /resource/{id}/action)
    SYSTEM = "system"          # Systemweite Operation (POST /system/action)

# Definiere alle n8n-API-Ressourcen und ihre Pfade/Methoden
API_RESOURCES = {
    # Workflows
    "workflows": {
        "type": ResourceType.COLLECTION,
        "path": "workflows",
        "methods": ["GET", "POST"],
        "singleton_methods": ["GET", "PUT", "DELETE"],
        "actions": {
            "run": {"method": "POST", "path": "workflows/{id}/run"},
            "activate": {"method": "POST", "path": "workflows/{id}/activate"},
            "deactivate": {"method": "POST", "path": "workflows/{id}/deactivate"},
            "execute": {"method": "POST", "path": "workflows/{id}/execute"},
            "share": {"method": "POST", "path": "workflows/{id}/share"},
            "export": {"method": "GET", "path": "workflows/{id}/export"},
            "import": {"method": "POST", "path": "workflows/import"},
        }
    },
    
    # Credentials
    "credentials": {
        "type": ResourceType.COLLECTION,
        "path": "credentials",
        "methods": ["GET", "POST"],
        "singleton_methods": ["GET", "PUT", "DELETE"],
        "actions": {
            "test": {"method": "POST", "path": "credentials/{id}/test"},
            "share": {"method": "POST", "path": "credentials/{id}/share"},
            "types": {"method": "GET", "path": "credentials/types"},
        }
    },
    
    # Executions
    "executions": {
        "type": ResourceType.COLLECTION,
        "path": "executions",
        "methods": ["GET"],
        "singleton_methods": ["GET", "DELETE"],
        "actions": {
            "retry": {"method": "POST", "path": "executions/{id}/retry"},
            "stop": {"method": "POST", "path": "executions/{id}/stop"},
        }
    },
    
    # Nodes
    "nodes": {
        "type": ResourceType.COLLECTION,
        "path": "nodes",
        "methods": ["GET"],
        "actions": {
            "types": {"method": "GET", "path": "nodes/types"},
        }
    },
    
    # Variables
    "variables": {
        "type": ResourceType.COLLECTION,
        "path": "variables",
        "methods": ["GET", "POST"],
        "singleton_methods": ["GET", "PUT", "DELETE"],
    },
    
    # Tags
    "tags": {
        "type": ResourceType.COLLECTION,
        "path": "tags",
        "methods": ["GET", "POST"],
        "singleton_methods": ["GET", "PUT", "DELETE"],
    },
    
    # Users (Enterprise)
    "users": {
        "type": ResourceType.COLLECTION,
        "path": "users",
        "methods": ["GET", "POST"],
        "singleton_methods": ["GET", "PUT", "DELETE"],
        "actions": {
            "invite": {"method": "POST", "path": "users/invite"},
            "reinvite": {"method": "POST", "path": "users/{id}/reinvite"},
        }
    },
    
    # Community Nodes
    "community-nodes": {
        "type": ResourceType.COLLECTION,
        "path": "community-nodes",
        "methods": ["GET", "POST"],
        "singleton_methods": ["GET", "DELETE"],
        "actions": {
            "install": {"method": "POST", "path": "community-nodes/install"},
            "update": {"method": "POST", "path": "community-nodes/{id}/update"},
        }
    },
    
    # Settings
    "settings": {
        "type": ResourceType.COLLECTION,
        "path": "settings",
        "methods": ["GET", "POST"],
        "singleton_methods": ["GET", "PUT", "DELETE"],
    },
    
    # System
    "system": {
        "type": ResourceType.SYSTEM,
        "path": "system",
        "actions": {
            "health": {"method": "GET", "path": "health"},
            "metrics": {"method": "GET", "path": "metrics"},
            "restart": {"method": "POST", "path": "system/restart"},
            "worker-queue": {"method": "GET", "path": "system/worker-queue"},
            "version": {"method": "GET", "path": "system/version"},
        }
    },
    
    # Audit Logs (Enterprise)
    "audit": {
        "type": ResourceType.COLLECTION,
        "path": "audit",
        "methods": ["GET"],
    },
    
    # Queue (Enterprise)
    "queue": {
        "type": ResourceType.COLLECTION,
        "path": "queue",
        "methods": ["GET"],
        "actions": {
            "clean": {"method": "POST", "path": "queue/clean"},
            "pause": {"method": "POST", "path": "queue/pause"},
            "resume": {"method": "POST", "path": "queue/resume"},
        }
    },
}
