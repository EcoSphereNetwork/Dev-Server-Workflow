# OpenHands MCP-Server

Der OpenHands MCP-Server ermöglicht die parallele Ausführung von OpenHands-Aufgaben. Er stellt eine MCP-konforme Schnittstelle bereit, über die mehrere OpenHands-Agenten erstellt und verwaltet werden können.

## Überblick

Der OpenHands MCP-Server bietet folgende Funktionen:

- Erstellen und Verwalten von OpenHands-Agenten
- Parallele Ausführung von Aufgaben mit verschiedenen Agenten
- Überwachung des Status von Aufgaben
- Abrufen von Ergebnissen abgeschlossener Aufgaben
- Abbrechen laufender Aufgaben

Der Server verwendet einen Thread-Pool, um Aufgaben parallel auszuführen. Die maximale Anzahl von Worker-Threads kann beim Starten des Servers angegeben werden.

## Installation

Der OpenHands MCP-Server ist Teil des Dev-Server-Workflow-Projekts und wird mit diesem installiert. Stellen Sie sicher, dass Sie die folgenden Abhängigkeiten installiert haben:

```bash
pip install requests aiohttp pydantic
```

## Starten des Servers

Der OpenHands MCP-Server kann wie folgt gestartet werden:

```bash
./start-mcp-servers.sh --openhands
```

Oder mit zusätzlichen Optionen:

```bash
./start-mcp-servers.sh --openhands --max-workers 10 --verbose
```

Alternativ kann der Server auch direkt gestartet werden:

```bash
python src/mcp/openhands_server.py --max-workers 10 --verbose
```

## Konfiguration

Der OpenHands MCP-Server kann über Kommandozeilenargumente konfiguriert werden:

- `--host`: Host für den MCP-Server (Standard: 0.0.0.0)
- `--port`: Port für den MCP-Server (Standard: 3006)
- `--max-workers`: Maximale Anzahl von Worker-Threads (Standard: 5)
- `--verbose`: Ausführliche Ausgabe

## Verfügbare Funktionen

Der OpenHands MCP-Server stellt folgende Funktionen bereit:

### create_agent

Erstellt einen neuen OpenHands-Agenten.

**Parameter:**
- `config_file` (optional): Pfad zur Konfigurationsdatei

**Rückgabe:**
```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "config_file": "/path/to/config.json",
  "api_available": true
}
```

### get_agent

Ruft Informationen über einen OpenHands-Agenten ab.

**Parameter:**
- `agent_id`: ID des Agenten

**Rückgabe:**
```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "api_available": true,
  "config": {
    "openhands": {
      "api_url": "http://localhost:8000",
      "api_key": "...",
      "model": "gpt-4o",
      "temperature": 0.7,
      "max_tokens": 4000,
      "timeout": 60,
      "mcp_servers": [
        ...
      ],
      "default_system_prompt": "..."
    }
  }
}
```

### delete_agent

Löscht einen OpenHands-Agenten.

**Parameter:**
- `agent_id`: ID des Agenten

**Rückgabe:**
```json
{
  "success": true,
  "message": "Agent 550e8400-e29b-41d4-a716-446655440000 erfolgreich gelöscht"
}
```

### execute_task

Führt eine Aufgabe mit einem OpenHands-Agenten aus.

**Parameter:**
- `agent_id`: ID des Agenten
- `task`: Beschreibung der Aufgabe
- `context` (optional): Kontext für die Aufgabe

**Rückgabe:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running"
}
```

### execute_mcp_task

Führt eine MCP-Aufgabe mit einem OpenHands-Agenten aus.

**Parameter:**
- `agent_id`: ID des Agenten
- `task`: Beschreibung der Aufgabe
- `server_name`: Name des MCP-Servers
- `function_name`: Name der Funktion
- `parameters`: Parameter für die Funktion

**Rückgabe:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running"
}
```

### get_task_status

Ruft den Status einer Aufgabe ab.

**Parameter:**
- `task_id`: ID der Aufgabe

**Rückgabe:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running"
}
```

### get_task_result

Ruft das Ergebnis einer Aufgabe ab.

**Parameter:**
- `task_id`: ID der Aufgabe

**Rückgabe:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    ...
  }
}
```

### cancel_task

Bricht eine Aufgabe ab.

**Parameter:**
- `task_id`: ID der Aufgabe

**Rückgabe:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "Aufgabe erfolgreich abgebrochen"
}
```

### execute_parallel_tasks

Führt mehrere Aufgaben parallel aus.

**Parameter:**
- `tasks`: Liste von Aufgaben

**Rückgabe:**
```json
{
  "task_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ],
  "status": "running"
}
```

## Beispiele

### Erstellen eines Agenten und Ausführen einer Aufgabe

```python
from src.mcp.client import MCPClient

# Verbinde mit dem OpenHands MCP-Server
client = MCPClient("http://localhost:3006")

# Erstelle einen Agenten
result = client.call_function("create_agent", {})
agent_id = result["agent_id"]

# Führe eine Aufgabe aus
result = client.call_function("execute_task", {
    "agent_id": agent_id,
    "task": "Erstelle eine Liste der 5 wichtigsten Python-Bibliotheken für Datenanalyse."
})
task_id = result["task_id"]

# Warte auf das Ergebnis
while True:
    result = client.call_function("get_task_status", {
        "task_id": task_id
    })
    
    if result["status"] == "completed":
        result = client.call_function("get_task_result", {
            "task_id": task_id
        })
        print(result["result"])
        break
    
    time.sleep(1)

# Lösche den Agenten
client.call_function("delete_agent", {
    "agent_id": agent_id
})
```

### Parallele Ausführung von Aufgaben

```python
from src.mcp.client import MCPClient

# Verbinde mit dem OpenHands MCP-Server
client = MCPClient("http://localhost:3006")

# Erstelle Agenten
agent_ids = []
for i in range(3):
    result = client.call_function("create_agent", {})
    agent_ids.append(result["agent_id"])

# Definiere Aufgaben
tasks = [
    {
        "type": "execute_task",
        "agent_id": agent_ids[0],
        "task": "Aufgabe 1"
    },
    {
        "type": "execute_task",
        "agent_id": agent_ids[1],
        "task": "Aufgabe 2"
    },
    {
        "type": "execute_task",
        "agent_id": agent_ids[2],
        "task": "Aufgabe 3"
    }
]

# Führe Aufgaben parallel aus
result = client.call_function("execute_parallel_tasks", {
    "tasks": tasks
})
task_ids = result["task_ids"]

# Warte auf die Ergebnisse
results = {}
for task_id in task_ids:
    while True:
        result = client.call_function("get_task_status", {
            "task_id": task_id
        })
        
        if result["status"] == "completed":
            result = client.call_function("get_task_result", {
                "task_id": task_id
            })
            results[task_id] = result
            break
        
        time.sleep(1)

# Lösche die Agenten
for agent_id in agent_ids:
    client.call_function("delete_agent", {
        "agent_id": agent_id
    })
```

## Fehlerbehebung

### Server startet nicht

Wenn der Server nicht startet, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Port nicht bereits verwendet wird.
2. Überprüfen Sie, ob alle Abhängigkeiten installiert sind.
3. Überprüfen Sie die Logs auf Fehler.

### Aufgaben werden nicht ausgeführt

Wenn Aufgaben nicht ausgeführt werden, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der OpenHands-Agent korrekt erstellt wurde.
2. Überprüfen Sie, ob die OpenHands API erreichbar ist.
3. Überprüfen Sie die Logs auf Fehler.

### Aufgaben bleiben hängen

Wenn Aufgaben hängen bleiben, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Thread-Pool nicht überlastet ist.
2. Überprüfen Sie, ob die OpenHands API erreichbar ist.
3. Überprüfen Sie die Logs auf Fehler.
4. Versuchen Sie, die Aufgabe abzubrechen und neu zu starten.

## Fazit

Der OpenHands MCP-Server bietet eine leistungsstarke Möglichkeit, mehrere OpenHands-Agenten parallel zu laden und Aufgaben parallel auszuführen. Dies ermöglicht eine effiziente Nutzung der Ressourcen und eine schnellere Bearbeitung von Aufgaben.