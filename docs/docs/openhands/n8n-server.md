# n8n MCP-Server

Der n8n MCP-Server ermöglicht die Integration von n8n in das Dev-Server-Workflow-Projekt. Er stellt eine MCP-konforme Schnittstelle bereit, über die n8n-Workflows verwaltet und ausgeführt werden können.

## Überblick

Der n8n MCP-Server bietet folgende Funktionen:

- Abrufen von Informationen über n8n-Workflows
- Erstellen, Aktualisieren und Löschen von n8n-Workflows
- Ausführen von n8n-Workflows
- Aktivieren und Deaktivieren von n8n-Workflows
- Abrufen von Informationen über Workflow-Ausführungen
- Verwalten von n8n-Workflows über eine einheitliche Schnittstelle

Der Server kommuniziert mit einer n8n-Instanz über die n8n REST API und stellt diese Funktionen über eine MCP-konforme Schnittstelle bereit.

## Installation

Der n8n MCP-Server ist Teil des Dev-Server-Workflow-Projekts und wird mit diesem installiert. Stellen Sie sicher, dass Sie die folgenden Abhängigkeiten installiert haben:

```bash
pip install requests aiohttp
```

## Starten des Servers

Der n8n MCP-Server kann wie folgt gestartet werden:

```bash
./start-mcp-servers.sh --n8n --api-key YOUR_API_KEY
```

Oder mit zusätzlichen Optionen:

```bash
./start-mcp-servers.sh --n8n --api-key YOUR_API_KEY --n8n-url http://localhost:5678 --verbose
```

Alternativ kann der Server auch direkt gestartet werden:

```bash
python src/mcp/n8n_server.py --n8n-url http://localhost:5678 --api-key YOUR_API_KEY --verbose
```

## Konfiguration

Der n8n MCP-Server kann über Kommandozeilenargumente konfiguriert werden:

- `--n8n-url`: URL der n8n-Instanz (Standard: http://localhost:5678)
- `--api-key`: API-Schlüssel für n8n
- `--host`: Host für den MCP-Server (Standard: 0.0.0.0)
- `--port`: Port für den MCP-Server (Standard: 3000)
- `--verbose`: Ausführliche Ausgabe

## Verfügbare Funktionen

Der n8n MCP-Server stellt folgende Funktionen bereit:

### get_workflows

Ruft alle Workflows ab.

**Parameter:**
Keine

**Rückgabe:**
```json
{
  "workflows": [
    {
      "id": "1",
      "name": "Workflow 1",
      "active": true,
      ...
    },
    {
      "id": "2",
      "name": "Workflow 2",
      "active": false,
      ...
    }
  ]
}
```

### get_workflow

Ruft einen Workflow ab.

**Parameter:**
- `workflow_id`: ID des Workflows

**Rückgabe:**
```json
{
  "workflow": {
    "id": "1",
    "name": "Workflow 1",
    "active": true,
    "nodes": [...],
    "connections": {...},
    ...
  }
}
```

### execute_workflow

Führt einen Workflow aus.

**Parameter:**
- `workflow_id`: ID des Workflows
- `data` (optional): Daten für den Workflow

**Rückgabe:**
```json
{
  "execution": {
    "id": "1",
    "finished": true,
    "status": "success",
    "data": {...},
    ...
  }
}
```

### activate_workflow

Aktiviert einen Workflow.

**Parameter:**
- `workflow_id`: ID des Workflows

**Rückgabe:**
```json
{
  "success": true,
  "message": "Workflow erfolgreich aktiviert"
}
```

### deactivate_workflow

Deaktiviert einen Workflow.

**Parameter:**
- `workflow_id`: ID des Workflows

**Rückgabe:**
```json
{
  "success": true,
  "message": "Workflow erfolgreich deaktiviert"
}
```

### create_workflow

Erstellt einen neuen Workflow.

**Parameter:**
- `name`: Name des Workflows
- `nodes`: Knoten des Workflows
- `connections`: Verbindungen des Workflows
- `active` (optional): Ob der Workflow aktiv sein soll

**Rückgabe:**
```json
{
  "workflow": {
    "id": "1",
    "name": "Workflow 1",
    "active": true,
    "nodes": [...],
    "connections": {...},
    ...
  }
}
```

### update_workflow

Aktualisiert einen Workflow.

**Parameter:**
- `workflow_id`: ID des Workflows
- `name` (optional): Name des Workflows
- `nodes` (optional): Knoten des Workflows
- `connections` (optional): Verbindungen des Workflows
- `active` (optional): Ob der Workflow aktiv sein soll

**Rückgabe:**
```json
{
  "workflow": {
    "id": "1",
    "name": "Workflow 1",
    "active": true,
    "nodes": [...],
    "connections": {...},
    ...
  }
}
```

### delete_workflow

Löscht einen Workflow.

**Parameter:**
- `workflow_id`: ID des Workflows

**Rückgabe:**
```json
{
  "success": true,
  "message": "Workflow erfolgreich gelöscht"
}
```

### get_executions

Ruft alle Ausführungen eines Workflows ab.

**Parameter:**
- `workflow_id`: ID des Workflows
- `limit` (optional): Maximale Anzahl von Ausführungen

**Rückgabe:**
```json
{
  "executions": [
    {
      "id": "1",
      "finished": true,
      "status": "success",
      "data": {...},
      ...
    },
    {
      "id": "2",
      "finished": true,
      "status": "error",
      "data": {...},
      ...
    }
  ]
}
```

### get_execution

Ruft eine Ausführung ab.

**Parameter:**
- `execution_id`: ID der Ausführung

**Rückgabe:**
```json
{
  "execution": {
    "id": "1",
    "finished": true,
    "status": "success",
    "data": {...},
    ...
  }
}
```

### manage_workflow

Verwaltet einen Workflow.

**Parameter:**
- `workflow_name`: Name des Workflows
- `action`: Aktion, die ausgeführt werden soll (start, stop, execute, update, delete, get, get_executions)
- `parameters` (optional): Parameter für die Aktion

**Rückgabe:**
Abhängig von der Aktion.

## Beispiele

### Abrufen aller Workflows

```python
from src.mcp.client import MCPClient

# Verbinde mit dem n8n MCP-Server
client = MCPClient("http://localhost:3000")

# Hole alle Workflows
workflows = client.call_function("get_workflows", {})
print(workflows)
```

### Ausführen eines Workflows

```python
from src.mcp.client import MCPClient

# Verbinde mit dem n8n MCP-Server
client = MCPClient("http://localhost:3000")

# Führe einen Workflow aus
result = client.call_function("execute_workflow", {
    "workflow_id": "1",
    "data": {
        "input": "Beispieldaten"
    }
})
print(result)
```

### Verwalten eines Workflows

```python
from src.mcp.client import MCPClient

# Verbinde mit dem n8n MCP-Server
client = MCPClient("http://localhost:3000")

# Starte einen Workflow
result = client.call_function("manage_workflow", {
    "workflow_name": "OpenHands Integration",
    "action": "start"
})
print(result)

# Führe einen Workflow aus
result = client.call_function("manage_workflow", {
    "workflow_name": "OpenHands Integration",
    "action": "execute",
    "parameters": {
        "data": {
            "input": "Beispieldaten"
        }
    }
})
print(result)

# Stoppe einen Workflow
result = client.call_function("manage_workflow", {
    "workflow_name": "OpenHands Integration",
    "action": "stop"
})
print(result)
```

## Integration mit OpenHands

Der n8n MCP-Server kann mit OpenHands integriert werden, um n8n-Workflows zu verwalten und auszuführen. Hier ist ein Beispiel für die Integration:

```python
from src.openhands.agent import get_openhands_agent

# Hole den OpenHands Agent
agent = get_openhands_agent()

# Verwalte einen n8n-Workflow
result = agent.manage_workflow(
    "OpenHands Integration",
    "start"
)
print(result)

# Führe einen n8n-Workflow aus
result = agent.manage_workflow(
    "OpenHands Integration",
    "execute",
    {
        "data": {
            "input": "Beispieldaten"
        }
    }
)
print(result)
```

## Fehlerbehebung

### Server startet nicht

Wenn der Server nicht startet, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Port nicht bereits verwendet wird.
2. Überprüfen Sie, ob alle Abhängigkeiten installiert sind.
3. Überprüfen Sie die Logs auf Fehler.

### n8n nicht erreichbar

Wenn n8n nicht erreichbar ist, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass n8n läuft und unter der angegebenen URL erreichbar ist.
2. Überprüfen Sie, ob der API-Schlüssel korrekt ist.
3. Überprüfen Sie, ob die Netzwerkverbindung funktioniert.

### Workflow nicht gefunden

Wenn ein Workflow nicht gefunden wird, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Workflow existiert und der Name oder die ID korrekt ist.
2. Überprüfen Sie, ob Sie die richtigen Berechtigungen haben, um auf den Workflow zuzugreifen.

## Fazit

Der n8n MCP-Server bietet eine leistungsstarke Möglichkeit, n8n in das Dev-Server-Workflow-Projekt zu integrieren. Durch die MCP-konforme Schnittstelle können n8n-Workflows einfach verwaltet und ausgeführt werden, was die Integration mit anderen Komponenten des Projekts erleichtert.