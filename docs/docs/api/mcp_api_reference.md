# MCP API-Referenz

Diese Dokumentation bietet eine umfassende Referenz für die MCP-API im Dev-Server-Workflow-Projekt.

## Übersicht

Die MCP (Model Context Protocol) API ist eine JSON-RPC 2.0-basierte API, die von MCP-Servern implementiert wird. Sie ermöglicht Clients, Tools aufzulisten und aufzurufen, die von MCP-Servern bereitgestellt werden.

## Endpunkte

Alle MCP-Server stellen einen einzigen Endpunkt bereit:

```
POST /mcp
```

## Methoden

### `mcp.listTools`

Listet alle verfügbaren Tools auf, die vom MCP-Server bereitgestellt werden.

**Parameter**: Keine

**Beispielanfrage**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.listTools",
  "params": {}
}
```

**Beispielantwort**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "name": "list_workflows",
      "description": "Listet alle verfügbaren n8n-Workflows auf",
      "parameter_schema": {
        "type": "object",
        "properties": {
          "tags": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Filter nach Tags"
          },
          "active": {
            "type": "boolean",
            "description": "Filter nach aktiven Workflows"
          }
        }
      }
    },
    {
      "name": "run_workflow",
      "description": "Führt einen n8n-Workflow aus",
      "parameter_schema": {
        "type": "object",
        "properties": {
          "workflow_id": {
            "type": "string",
            "description": "ID des Workflows"
          },
          "parameters": {
            "type": "object",
            "description": "Parameter für den Workflow"
          }
        },
        "required": ["workflow_id"]
      }
    }
  ]
}
```

### `mcp.callTool`

Ruft ein Tool auf, das vom MCP-Server bereitgestellt wird.

**Parameter**:

- `name` (string, erforderlich): Name des Tools
- `arguments` (object): Argumente für das Tool

**Beispielanfrage**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "run_workflow",
    "arguments": {
      "workflow_id": "1",
      "parameters": {
        "input": "Hello, World!"
      }
    }
  }
}
```

**Beispielantwort**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "execution_id": "abc123",
    "status": "completed",
    "output": {
      "result": "Hello, World!"
    }
  }
}
```

### `mcp.getServerInfo`

Ruft Informationen über den MCP-Server ab.

**Parameter**: Keine

**Beispielanfrage**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.getServerInfo",
  "params": {}
}
```

**Beispielantwort**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "name": "n8n-mcp-server",
    "version": "1.0.0",
    "description": "MCP-Server für n8n-Workflow-Automatisierung",
    "status": "online",
    "uptime": 3600,
    "request_count": 42,
    "tools_count": 5,
    "health_metrics": {
      "total_requests": 42,
      "successful_requests": 40,
      "failed_requests": 2,
      "average_response_time": 0.1234
    }
  }
}
```

## Fehlerbehandlung

Die MCP-API verwendet die JSON-RPC 2.0-Fehlerbehandlung. Fehler werden im folgenden Format zurückgegeben:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error: Tool not found: invalid_tool"
  }
}
```

### Fehlercodes

- `-32700`: Parse error (ungültiges JSON)
- `-32600`: Invalid Request (ungültige JSON-RPC-Anfrage)
- `-32601`: Method not found (Methode nicht gefunden)
- `-32602`: Invalid params (ungültige Parameter)
- `-32603`: Internal error (interner Fehler)
- `-32000` bis `-32099`: Serverspezifische Fehler

## Authentifizierung

Die MCP-API unterstützt die Authentifizierung über HTTP-Header:

```
Authorization: Bearer <token>
```

## Beispiele

### Beispiel 1: Auflisten von Tools

**Anfrage**:

```bash
curl -X POST http://localhost:3456/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.listTools",
    "params": {}
  }'
```

**Antwort**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "name": "list_workflows",
      "description": "Listet alle verfügbaren n8n-Workflows auf",
      "parameter_schema": {
        "type": "object",
        "properties": {
          "tags": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Filter nach Tags"
          },
          "active": {
            "type": "boolean",
            "description": "Filter nach aktiven Workflows"
          }
        }
      }
    },
    {
      "name": "run_workflow",
      "description": "Führt einen n8n-Workflow aus",
      "parameter_schema": {
        "type": "object",
        "properties": {
          "workflow_id": {
            "type": "string",
            "description": "ID des Workflows"
          },
          "parameters": {
            "type": "object",
            "description": "Parameter für den Workflow"
          }
        },
        "required": ["workflow_id"]
      }
    }
  ]
}
```

### Beispiel 2: Aufrufen eines Tools

**Anfrage**:

```bash
curl -X POST http://localhost:3456/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "run_workflow",
      "arguments": {
        "workflow_id": "1",
        "parameters": {
          "input": "Hello, World!"
        }
      }
    }
  }'
```

**Antwort**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "execution_id": "abc123",
    "status": "completed",
    "output": {
      "result": "Hello, World!"
    }
  }
}
```

### Beispiel 3: Abrufen von Serverinformationen

**Anfrage**:

```bash
curl -X POST http://localhost:3456/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.getServerInfo",
    "params": {}
  }'
```

**Antwort**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "name": "n8n-mcp-server",
    "version": "1.0.0",
    "description": "MCP-Server für n8n-Workflow-Automatisierung",
    "status": "online",
    "uptime": 3600,
    "request_count": 42,
    "tools_count": 5,
    "health_metrics": {
      "total_requests": 42,
      "successful_requests": 40,
      "failed_requests": 2,
      "average_response_time": 0.1234
    }
  }
}
```

## Spezifische MCP-Server-APIs

### n8n MCP-Server

#### `list_workflows`

Listet alle verfügbaren n8n-Workflows auf.

**Parameter**:

- `tags` (array, optional): Filter nach Tags
- `active` (boolean, optional): Filter nach aktiven Workflows

**Beispielanfrage**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "list_workflows",
    "arguments": {
      "tags": ["automation", "github"],
      "active": true
    }
  }
}
```

#### `run_workflow`

Führt einen n8n-Workflow aus.

**Parameter**:

- `workflow_id` (string, erforderlich): ID des Workflows
- `parameters` (object, optional): Parameter für den Workflow

**Beispielanfrage**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "run_workflow",
    "arguments": {
      "workflow_id": "1",
      "parameters": {
        "input": "Hello, World!"
      }
    }
  }
}
```

### OpenHands MCP-Server

#### `run_task`

Führt eine OpenHands-Aufgabe aus.

**Parameter**:

- `task` (string, erforderlich): Aufgabenbeschreibung
- `context` (object, optional): Kontext für die Aufgabe

**Beispielanfrage**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "run_task",
    "arguments": {
      "task": "Analysiere den Code in der Datei example.py",
      "context": {
        "file": "example.py",
        "content": "def hello_world():\n    print(\"Hello, World!\")"
      }
    }
  }
}
```

### Docker MCP-Server

#### `list_containers`

Listet alle Docker-Container auf.

**Parameter**:

- `all` (boolean, optional): Alle Container anzeigen, auch gestoppte

**Beispielanfrage**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "list_containers",
    "arguments": {
      "all": true
    }
  }
}
```

## Weitere Ressourcen

- [JSON-RPC 2.0-Spezifikation](https://www.jsonrpc.org/specification)
- [MCP-Spezifikation](https://modelcontextprotocol.ai/)