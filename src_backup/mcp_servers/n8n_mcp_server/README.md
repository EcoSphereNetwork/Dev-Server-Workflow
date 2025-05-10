# n8n MCP Server

Ein MCP-Server für n8n-Workflow-Automatisierung.

## Übersicht

Der n8n MCP Server bietet eine MCP-konforme Schnittstelle für n8n-Workflow-Automatisierung. Er ermöglicht es, n8n-Workflows über das Model Context Protocol (MCP) zu verwalten und auszuführen.

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- n8n-Instanz
- FastAPI
- Pydantic
- aiohttp

### Installation der Abhängigkeiten

```bash
pip install fastapi uvicorn pydantic aiohttp
```

### Konfiguration

Die Konfiguration erfolgt über Umgebungsvariablen oder eine `.env`-Datei. Die folgenden Umgebungsvariablen werden unterstützt:

- `N8N_MCP_HOST`: Host, auf dem der Server läuft (Standard: `0.0.0.0`)
- `N8N_MCP_PORT`: Port, auf dem der Server läuft (Standard: `3456`)
- `N8N_MCP_DEBUG`: Debug-Modus (Standard: `False`)
- `N8N_MCP_LOG_LEVEL`: Log-Level (Standard: `INFO`)
- `N8N_MCP_LOG_FILE`: Pfad zur Log-Datei (Standard: `logs/n8n_mcp.log`)
- `N8N_MCP_N8N_URL`: URL der n8n-Instanz (Standard: `http://localhost:5678`)
- `N8N_MCP_N8N_API_KEY`: API-Schlüssel für die n8n-Instanz (Standard: `None`)
- `N8N_MCP_N8N_WEBHOOK_URL`: URL für Webhooks (Standard: `http://localhost:3456/webhook`)
- `N8N_MCP_N8N_WEBHOOK_PATH`: Pfad für Webhooks (Standard: `/webhook`)
- `N8N_MCP_AUTH_ENABLED`: Ob die Authentifizierung aktiviert ist (Standard: `False`)
- `N8N_MCP_AUTH_TOKEN`: Authentifizierungstoken (Standard: `None`)
- `N8N_MCP_AUDIT_ENABLED`: Ob die Audit-Protokollierung aktiviert ist (Standard: `True`)
- `N8N_MCP_AUDIT_LOG_FILE`: Pfad zur Audit-Log-Datei (Standard: `logs/n8n_mcp_audit.log`)
- `N8N_MCP_METRICS_ENABLED`: Ob die Metriken-Erfassung aktiviert ist (Standard: `True`)
- `N8N_MCP_METRICS_ENDPOINT`: Endpunkt für Metriken (Standard: `/metrics`)
- `N8N_MCP_WORKFLOW_CACHE_ENABLED`: Ob der Workflow-Cache aktiviert ist (Standard: `True`)
- `N8N_MCP_WORKFLOW_CACHE_TTL`: TTL für den Workflow-Cache in Sekunden (Standard: `300`)

## Verwendung

### Starten des Servers

#### Als HTTP-Server

```bash
./scripts/start-n8n-mcp-server.sh
```

#### Als MCP-Server

```bash
./scripts/start-n8n-mcp-server-mcp.sh
```

### API-Endpunkte

#### Gesundheitscheck

```
GET /health
```

#### Metriken

```
GET /metrics
```

#### Workflows

```
GET /workflows
GET /workflows/{workflow_id}
POST /workflows/{workflow_id}/run
POST /workflows
PUT /workflows/{workflow_id}
DELETE /workflows/{workflow_id}
POST /workflows/{workflow_id}/activate
POST /workflows/{workflow_id}/deactivate
```

### MCP-Tools

- `list_workflows`: Liste alle n8n-Workflows auf
- `get_workflow`: Erhalte einen n8n-Workflow
- `run_workflow`: Führe einen n8n-Workflow aus
- `create_workflow`: Erstelle einen n8n-Workflow
- `update_workflow`: Aktualisiere einen n8n-Workflow
- `delete_workflow`: Lösche einen n8n-Workflow
- `activate_workflow`: Aktiviere einen n8n-Workflow
- `deactivate_workflow`: Deaktiviere einen n8n-Workflow

## Beispiele

### Auflisten aller Workflows

```bash
curl -X GET http://localhost:3456/workflows
```

### Ausführen eines Workflows

```bash
curl -X POST http://localhost:3456/workflows/1/run \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "input": "Hello, World!"
    }
  }'
```

### Auflisten aller Workflows über MCP

```bash
curl -X POST http://localhost:3456/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "list_workflows",
      "arguments": {
        "active": true
      }
    }
  }'
```

### Ausführen eines Workflows über MCP

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

## Entwicklung

### Projektstruktur

```
n8n_mcp_server/
├── api/
│   ├── __init__.py
│   └── router.py
├── core/
│   ├── __init__.py
│   ├── auth.py
│   ├── audit.py
│   ├── config.py
│   ├── metrics.py
│   └── n8n_client.py
├── models/
│   ├── __init__.py
│   └── workflow.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── __init__.py
├── main.py
└── mcp_interface.py
```

### Tests

```bash
pytest tests/mcp_servers/n8n_mcp_server/
```

## Lizenz

MIT