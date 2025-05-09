# MCP-Server-Verwendung

Diese Dokumentation bietet einen umfassenden Leitfaden für die Verwendung von MCP-Servern im Dev-Server-Workflow-Projekt.

## Übersicht

MCP (Model Context Protocol) Server stellen Tools für Clients über eine standardisierte Schnittstelle bereit. Das Dev-Server-Workflow-Projekt umfasst mehrere MCP-Server, die verschiedene Funktionalitäten bieten.

## Verfügbare MCP-Server

### n8n MCP-Server

Der n8n MCP-Server stellt n8n-Workflows als MCP-Tools bereit.

**Port**: 3456

**Tools**:
- `list_workflows`: Listet alle verfügbaren n8n-Workflows auf
- `run_workflow`: Führt einen n8n-Workflow aus
- `get_workflow`: Ruft die Details eines n8n-Workflows ab
- `create_workflow`: Erstellt einen neuen n8n-Workflow
- `update_workflow`: Aktualisiert einen vorhandenen n8n-Workflow
- `delete_workflow`: Löscht einen n8n-Workflow

### OpenHands MCP-Server

Der OpenHands MCP-Server ermöglicht die parallele Ausführung von OpenHands-Aufgaben.

**Port**: 3457

**Tools**:
- `run_task`: Führt eine OpenHands-Aufgabe aus
- `run_parallel_tasks`: Führt mehrere OpenHands-Aufgaben parallel aus
- `get_task_status`: Ruft den Status einer OpenHands-Aufgabe ab
- `cancel_task`: Bricht eine laufende OpenHands-Aufgabe ab

### Docker MCP-Server

Der Docker MCP-Server verwaltet Docker-Container über MCP.

**Port**: 3458

**Tools**:
- `list_containers`: Listet alle Docker-Container auf
- `start_container`: Startet einen Docker-Container
- `stop_container`: Stoppt einen Docker-Container
- `restart_container`: Startet einen Docker-Container neu
- `remove_container`: Entfernt einen Docker-Container
- `list_images`: Listet alle Docker-Images auf
- `pull_image`: Zieht ein Docker-Image
- `remove_image`: Entfernt ein Docker-Image

### LLM Cost Analyzer MCP-Server

Der LLM Cost Analyzer MCP-Server analysiert die Kosten von LLM-Anfragen.

**Port**: 3459

**Tools**:
- `estimate_cost`: Schätzt die Kosten einer LLM-Anfrage
- `analyze_task`: Analysiert die Komplexität einer Aufgabe
- `list_models`: Listet alle verfügbaren LLM-Modelle auf
- `get_model_info`: Ruft Informationen über ein LLM-Modell ab

### Prompt MCP-Server

Der Prompt MCP-Server verwaltet und optimiert Prompts für LLMs.

**Port**: 3460

**Tools**:
- `optimize_prompt`: Optimiert einen Prompt für ein LLM
- `list_templates`: Listet alle verfügbaren Prompt-Templates auf
- `get_template`: Ruft ein Prompt-Template ab
- `create_template`: Erstellt ein neues Prompt-Template
- `update_template`: Aktualisiert ein vorhandenes Prompt-Template
- `delete_template`: Löscht ein Prompt-Template

## Verwendung der MCP-Server

### Über die Befehlszeile

Sie können MCP-Server über die Befehlszeile mit `curl` verwenden:

```bash
curl -X POST http://localhost:<port>/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "<tool_name>",
      "arguments": {
        "<arg1>": "<value1>",
        "<arg2>": "<value2>"
      }
    }
  }'
```

### Über Python

Sie können MCP-Server über Python mit der `requests`-Bibliothek verwenden:

```python
import requests
import json

def call_mcp_tool(port, tool_name, arguments):
    url = f"http://localhost:{port}/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.callTool",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Beispiel: Führen Sie einen n8n-Workflow aus
result = call_mcp_tool(3456, "run_workflow", {
    "workflow_id": "1",
    "parameters": {}
})
print(json.dumps(result, indent=2))
```

### Über JavaScript

Sie können MCP-Server über JavaScript mit der `fetch`-API verwenden:

```javascript
async function callMcpTool(port, toolName, arguments) {
    const url = `http://localhost:${port}/mcp`;
    const payload = {
        jsonrpc: "2.0",
        id: 1,
        method: "mcp.callTool",
        params: {
            name: toolName,
            arguments: arguments
        }
    };
    
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}

// Beispiel: Führen Sie einen n8n-Workflow aus
callMcpTool(3456, "run_workflow", {
    workflow_id: "1",
    parameters: {}
}).then(result => {
    console.log(JSON.stringify(result, null, 2));
});
```

## Beispiele

### Beispiel 1: Auflisten von n8n-Workflows

```bash
curl -X POST http://localhost:3456/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "list_workflows",
      "arguments": {}
    }
  }'
```

### Beispiel 2: Ausführen einer OpenHands-Aufgabe

```bash
curl -X POST http://localhost:3457/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "run_task",
      "arguments": {
        "task": "Analysiere den Code in der Datei example.py",
        "context": {
          "file": "example.py",
          "content": "def hello_world():\\n    print(\\"Hello, World!\\")"
        }
      }
    }
  }'
```

### Beispiel 3: Auflisten von Docker-Containern

```bash
curl -X POST http://localhost:3458/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "list_containers",
      "arguments": {
        "all": true
      }
    }
  }'
```

### Beispiel 4: Schätzen der Kosten einer LLM-Anfrage

```bash
curl -X POST http://localhost:3459/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "estimate_cost",
      "arguments": {
        "model": "gpt-4",
        "prompt": "Erkläre mir die Quantenphysik",
        "max_tokens": 1000
      }
    }
  }'
```

### Beispiel 5: Optimieren eines Prompts

```bash
curl -X POST http://localhost:3460/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "optimize_prompt",
      "arguments": {
        "prompt": "Erkläre mir die Quantenphysik",
        "target_model": "gpt-4",
        "optimization_goal": "clarity"
      }
    }
  }'
```

## Fehlerbehebung

### Häufige Fehler

#### Verbindungsfehler

Wenn Sie einen Verbindungsfehler erhalten, stellen Sie sicher, dass der MCP-Server läuft:

```bash
# Überprüfen Sie, ob der MCP-Server läuft
curl http://localhost:<port>/health
```

#### Authentifizierungsfehler

Wenn Sie einen Authentifizierungsfehler erhalten, stellen Sie sicher, dass Sie das richtige Authentifizierungstoken verwenden:

```bash
# Fügen Sie das Authentifizierungstoken hinzu
curl -X POST http://localhost:<port>/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_auth_token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "<tool_name>",
      "arguments": {}
    }
  }'
```

#### Tool nicht gefunden

Wenn Sie einen "Tool nicht gefunden"-Fehler erhalten, stellen Sie sicher, dass Sie den richtigen Tool-Namen verwenden:

```bash
# Listet alle verfügbaren Tools auf
curl -X POST http://localhost:<port>/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.listTools",
    "params": {}
  }'
```

### Logs überprüfen

Wenn Sie Probleme haben, überprüfen Sie die Logs des MCP-Servers:

```bash
# Zeigt die Logs des MCP-Servers an
docker logs <container_name>
```

## Weitere Ressourcen

- [MCP-Spezifikation](https://modelcontextprotocol.ai/)
- [n8n-Dokumentation](https://docs.n8n.io/)
- [OpenHands-Dokumentation](https://openhands.ai/docs)
- [Docker-Dokumentation](https://docs.docker.com/)