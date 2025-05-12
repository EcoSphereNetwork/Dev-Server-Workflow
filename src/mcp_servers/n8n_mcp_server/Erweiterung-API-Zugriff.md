# Erweiterung des n8n MCP Servers für vollständigen n8n API-Zugriff

Um LLMs/Agents (MCP-Clients) vollständigen Zugriff auf die n8n-API zu ermöglichen, ist eine umfassende Erweiterung des aktuellen Servers notwendig. Hier ist mein Plan, wie du den n8n MCP Server zu einem vollständigen n8n API-Proxy ausbauen kannst:

## 1. Kartierung der vollständigen n8n-API

Zunächst müssen wir alle verfügbaren n8n-API-Endpunkte kartieren und als MCP-Tools abbilden:

### Hauptbereiche der n8n-API:

- **Workflows**: CRUD-Operationen, Ausführung, Export/Import, Sharing
- **Credentials**: Verwaltung von API-Schlüsseln und Zugangsdaten
- **Executions**: Verlauf, Status, Abbruch, Wiederholung
- **Tags**: Verwaltung von Tags/Labels
- **Users**: Benutzerverwaltung (in n8n Enterprise)
- **Variables**: Umgebungsvariablen und Secrets
- **Nodes**: Node-Typen, benutzerdefinierte Nodes
- **Community-Nodes**: Installation, Aktualisierung, Entfernung
- **Settings**: Systemkonfiguration und Einstellungen
- **Queue**: Workflow-Warteschlangen (Enterprise-Feature)
- **Audit**: Audit-Logs (Enterprise-Feature)

## 2. Architekturvorschlag für die Implementierung

### 2.1 Dynamischer Tool-Registry-Ansatz

```python
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
```

### 2.2 Generischer API-Client mit Pfad-Mapping

```python
class N8nAPIClient:
    """Generischer Client für den Zugriff auf die n8n-API."""
    
    def __init__(self, base_url, api_key=None, session=None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = session or aiohttp.ClientSession(headers={
            "X-N8N-API-KEY": api_key,
            "Content-Type": "application/json"
        })
        
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
```

## 3. Implementierung der vollständigen API-Abdeckung

Hier ist eine strukturierte Implementierung zur Erweiterung des existierenden Codes:

### 3.1 Modul für API-Ressourcen mit Auto-Discovery

```python
# n8n_api_resources.py
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
}
```

### 3.2 Automatische Tool-Generierung

```python
# n8n_tool_generator.py
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
```

### 3.3 Generischer Handler für dynamische API-Anfragen

```python
# n8n_mcp_handler.py
import re
from urllib.parse import quote

class N8nMCPHandler:
    """Handler für MCP-Anfragen an die n8n-API."""
    
    def __init__(self, api_client, registry):
        self.api_client = api_client
        self.registry = registry
        # Erstelle Event (Registry gefüllt)
        self.initialized = asyncio.Event()
        # Fülle die Registry mit allen Tools
        asyncio.create_task(self._initialize_registry())
    
    async def _initialize_registry(self):
        """Initialisiere die Tool-Registry mit allen n8n-API-Tools."""
        from .n8n_tool_generator import generate_all_tools
        from .n8n_api_resources import API_RESOURCES, ResourceType
        
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
```

### 3.4 Integration in den n8n MCP Server

```python
# Erweitere die N8nMCPServer-Klasse
async def initialize(self):
    """Initialisiere den Server und lade alle verfügbaren API-Tools."""
    self.session = aiohttp.ClientSession(headers={
        "X-N8N-API-KEY": self.api_key,
        "Content-Type": "application/json"
    })
    
    # API-Client erstellen
    self.api_client = N8nAPIClient(self.n8n_url, self.api_key, self.session)
    
    # Tool-Registry erstellen
    self.tool_registry = N8nToolRegistry()
    
    # MCP-Handler erstellen
    self.mcp_handler = N8nMCPHandler(self.api_client, self.tool_registry)
    
    # Warten, bis die Registry initialisiert ist
    await self.mcp_handler.initialized.wait()
    
    # Tools aus der Registry in die Server-Tools übernehmen
    self.tools = [
        MCPTool(
            name=tool["name"],
            description=tool["description"],
            parameter_schema=tool["parameter_schema"]
        )
        for tool in self.tool_registry.list_tools()
    ]
    
    logger.info(f"MCP Server initialized with {len(self.tools)} tools")

async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call a tool.
    
    Args:
        tool_name: Name of the tool
        arguments: Arguments for the tool
        
    Returns:
        Result of the tool call
    """
    logger.info(f"Calling tool {tool_name} with arguments: {json.dumps(arguments)}")
    
    # Log the audit event
    self.audit_logger.log(
        event=f"call_tool:{tool_name}",
        user=None,
        details={"arguments": arguments},
    )
    
    # Find the tool in the registry
    tool = self.tool_registry.get_tool(tool_name)
    if not tool:
        raise ValueError(f"Tool not found: {tool_name}")
    
    # Record start time
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Call the handler
        result = await tool["handler"](arguments)
        
        # Record end time and metrics
        end_time = asyncio.get_event_loop().time()
        self.metrics_collector.record_request(
            method=tool_name,
            success=True,
            response_time=end_time - start_time,
        )
        
        return result
    except Exception as e:
        # Record end time and metrics for failures
        end_time = asyncio.get_event_loop().time()
        self.metrics_collector.record_request(
            method=tool_name,
            success=False,
            response_time=end_time - start_time,
        )
        
        # Log the error
        logger.error(f"Error calling tool {tool_name}: {e}")
        
        # Log the audit event
        self.audit_logger.log(
            event=f"call_tool_error:{tool_name}",
            user=None,
            details={"arguments": arguments, "error": str(e)},
        )
        
        raise
```

## 4. Sicherheitsaspekte bei vollständigem API-Zugriff

Da der Server nun vollständigen Zugriff auf die n8n-API bietet, sind folgende Sicherheitsmaßnahmen besonders wichtig:

1. **Detaillierte Berechtigungskontrolle**: 
   ```python
   # Erweitere die Authentifizierungsklasse
   class AuthManager:
       # ...
       
       def authorize_api_access(self, token: str, resource: str, action: str) -> bool:
           """Prüfe, ob ein Token Zugriff auf eine bestimmte API-Ressource und -Aktion hat."""
           if not self.authenticate(token):
               return False
               
           permissions = self.tokens[token].get("permissions", [])
           
           # Wildcard-Berechtigung (alle Ressourcen/Aktionen)
           if "*" in permissions:
               return True
               
           # Ressourcen-Wildcard (alle Aktionen für diese Ressource)
           if f"{resource}:*" in permissions:
               return True
               
           # Spezifische Berechtigung
           if f"{resource}:{action}" in permissions:
               return True
               
           return False
   ```

2. **Rate-Limiting pro Token**:
   ```python
   class RateLimiter:
       """Rate-Limiter für API-Zugriffe."""
       
       def __init__(self):
           self.limits = {}  # Token -> {count, last_reset}
           
       async def check_limit(self, token: str, limit: int, window: int) -> bool:
           """Prüfe, ob ein Token sein Limit überschritten hat."""
           now = time.time()
           
           if token not in self.limits:
               self.limits[token] = {"count": 1, "last_reset": now}
               return True
               
           # Reset, wenn Zeitfenster abgelaufen
           if now - self.limits[token]["last_reset"] > window:
               self.limits[token] = {"count": 1, "last_reset": now}
               return True
               
           # Prüfe Limit
           if self.limits[token]["count"] >= limit:
               return False
               
           # Inkrementiere Zähler
           self.limits[token]["count"] += 1
           return True
   ```

3. **Umfassendes Audit-Logging**:
   ```python
   # Erweitere den Audit-Logger
   class AuditLogger:
       # ...
       
       def log_api_access(self, event: str, user: Optional[str], resource: str, 
                         action: str, resource_id: Optional[str], data: Optional[Dict] = None):
           """
           Protokolliere einen API-Zugriff detailliert.
           """
           audit_entry = {
               "timestamp": datetime.datetime.now().isoformat(),
               "event": event,
               "user": user or "anonymous",
               "resource": resource,
               "action": action,
               "resource_id": resource_id,
               "data": self._sanitize_sensitive_data(data) if data else {},
           }
           
           with open(self.audit_file, "a") as f:
               f.write(json.dumps(audit_entry) + "\n")
               
       def _sanitize_sensitive_data(self, data: Dict) -> Dict:
           """Entferne sensible Daten vor dem Logging."""
           if not data:
               return {}
               
           sanitized = copy.deepcopy(data)
           
           # Liste sensibler Felder
           sensitive_fields = [
               "password", "token", "secret", "key", "credential"
           ]
           
           # Rekursive Funktion zum Durchsuchen des Dictionaries
           def redact_sensitive(obj, path=""):
               if isinstance(obj, dict):
                   for k, v in list(obj.items()):
                       if any(sensitive in k.lower() for sensitive in sensitive_fields):
                           obj[k] = "***REDACTED***"
                       else:
                           redact_sensitive(v, f"{path}.{k}")
               elif isinstance(obj, list):
                   for i, item in enumerate(obj):
                       redact_sensitive(item, f"{path}[{i}]")
                       
           redact_sensitive(sanitized)
           return sanitized
   ```

## 5. Beispiele für die Nutzung der erweiterten API

### 5.1 Workflow-Verwaltung

```json
// Alle Workflows auflisten
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "list_workflows",
    "arguments": {
      "filter": {
        "active": true
      },
      "take": 10,
      "skip": 0
    }
  }
}

// Einzelnen Workflow abrufen
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "mcp.callTool",
  "params": {
    "name": "get_workflows",
    "arguments": {
      "id": "123abc"
    }
  }
}

// Workflow ausführen
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "mcp.callTool",
  "params": {
    "name": "workflows_run",
    "arguments": {
      "id": "123abc",
      "data": {
        "inputs": {
          "myParam1": "value1",
          "myParam2": "value2"
        }
      }
    }
  }
}
```

### 5.2 Credentials-Verwaltung

```json
// Alle Credentials auflisten
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "mcp.callTool",
  "params": {
    "name": "list_credentials",
    "arguments": {}
  }
}

// Neue Credential erstellen
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "mcp.callTool",
  "params": {
    "name": "create_credentials",
    "arguments": {
      "data": {
        "name": "My API Key",
        "type": "githubApi",
        "data": {
          "accessToken": "SECURE-TOKEN-HERE"
        }
      }
    }
  }
}
```

### 5.3 System-Informationen

```json
// Systemgesundheit prüfen
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "mcp.callTool",
  "params": {
    "name": "system_health",
    "arguments": {}
  }
}

// Systemmetriken abrufen
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "mcp.callTool",
  "params": {
    "name": "system_metrics",
    "arguments": {}
  }
}
```

## 6. Zusammenfassung und nächste Schritte

Diese Architektur ermöglicht es LLMs/Agents, die vollständige n8n-API über das Model Context Protocol zu nutzen. Die modulare Struktur mit automatischer Tool-Generierung macht die Implementierung wartbar und erweiterbar.

### Vorteile dieser Lösung:

1. **Dynamische Erfassung der API**: Wenn n8n neue API-Endpunkte hinzufügt, müssen nur die API_RESOURCES erweitert werden
2. **Einheitliche Handhabung**: Konsistente Struktur für alle API-Aufrufe
3. **Sicherheit**: Detaillierte Berechtigungskontrolle und Audit-Logging
4. **Performance**: Effizienter durch Wiederverwendung von Code und Verbindungen

### Nächste Schritte:

1. **API-Dokumentation erstellen**: Automatisch generierte Dokumentation für alle Tools
2. **Tests implementieren**: Unit- und Integrationstests für die neue Funktionalität
3. **Caching-Strategie verbessern**: Intelligentes Caching für häufig verwendete Ressourcen
4. **Observability einbauen**: Detailliertes Tracing für API-Aufrufe
5. **Vorlagen für komplexere Workflows**: Parametervorlagen für häufige Operationen bereitstellen

Diese Architektur ermöglicht es, die vollständige n8n-API über MCP zugänglich zu machen und dabei die Sicherheit, Wartbarkeit und Leistungsfähigkeit des Systems zu wahren.
