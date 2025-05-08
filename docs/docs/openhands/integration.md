# OpenHands Integration

Diese Dokumentation beschreibt die Integration von OpenHands in das Dev-Server-Workflow-Projekt. OpenHands fungiert als allgemeiner KI-Agent, der verschiedene Aufgaben übernehmen und als zentraler Manager für alle Prozesse dienen kann.

## Überblick

Die OpenHands-Integration besteht aus mehreren Komponenten:

1. **OpenHands Agent**: Eine Klasse, die die Interaktion mit OpenHands ermöglicht und verschiedene Methoden für die Ausführung von Aufgaben bereitstellt.
2. **OpenHands MCP-Server**: Ein MCP-Server, der es ermöglicht, mehrere OpenHands-Agenten parallel zu laden und Aufgaben parallel auszuführen.
3. **n8n MCP-Server**: Ein MCP-Server, der die Integration mit n8n ermöglicht und es OpenHands erlaubt, n8n-Workflows zu verwalten und auszuführen.
4. **Kommandozeilentool**: Ein Tool, das die Interaktion mit dem OpenHands-Agenten über die Kommandozeile ermöglicht.
5. **Beispiele**: Verschiedene Beispiele, die die Verwendung der OpenHands-Integration demonstrieren.

## Installation

Die OpenHands-Integration ist Teil des Dev-Server-Workflow-Projekts und wird mit diesem installiert. Stellen Sie sicher, dass Sie die folgenden Abhängigkeiten installiert haben:

```bash
pip install requests aiohttp pydantic
```

## Konfiguration

Die OpenHands-Integration kann über eine Konfigurationsdatei konfiguriert werden. Die Standardkonfiguration sieht wie folgt aus:

```json
{
  "openhands": {
    "api_url": "http://localhost:8000",
    "api_key": "",
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 4000,
    "timeout": 60,
    "mcp_servers": [
      {
        "name": "filesystem",
        "url": "http://localhost:3001",
        "description": "File system operations"
      },
      {
        "name": "desktop-commander",
        "url": "http://localhost:3002",
        "description": "Terminal command execution"
      },
      {
        "name": "sequential-thinking",
        "url": "http://localhost:3003",
        "description": "Sequential thinking for complex tasks"
      },
      {
        "name": "github-chat",
        "url": "http://localhost:3004",
        "description": "GitHub discussions and comments"
      },
      {
        "name": "github",
        "url": "http://localhost:3005",
        "description": "GitHub repository operations"
      },
      {
        "name": "n8n",
        "url": "http://localhost:3000",
        "description": "n8n workflow operations"
      }
    ],
    "default_system_prompt": "You are OpenHands, a helpful AI assistant that can interact with various systems through MCP servers. You can help with file operations, terminal commands, GitHub operations, and more."
  }
}
```

Sie können die Konfiguration anpassen, indem Sie eine eigene Konfigurationsdatei erstellen und diese beim Starten des OpenHands-Agenten angeben.

## Verwendung

### OpenHands Agent

Der OpenHands Agent kann wie folgt verwendet werden:

```python
from src.openhands.agent import get_openhands_agent

# Hole den OpenHands Agent
agent = get_openhands_agent()

# Führe eine Aufgabe aus
result = agent.execute_task("Erstelle eine Liste der 5 wichtigsten Python-Bibliotheken für Datenanalyse.")

# Führe eine MCP-Aufgabe aus
result = agent.execute_mcp_task(
    "Führe den Befehl 'ls -la' aus und analysiere das Ergebnis.",
    "desktop-commander",
    "execute_command",
    {"command": "ls -la"}
)

# Verwalte einen n8n-Workflow
result = agent.manage_workflow(
    "OpenHands Integration",
    "start"
)

# Verwalte ein GitHub-Repository
result = agent.manage_github_repository(
    "EcoSphereNetwork/Dev-Server-Workflow",
    "clone"
)

# Führe einen Befehl aus
result = agent.execute_command("ls -la")

# Verwalte Dateien
result = agent.manage_files(
    "read",
    "/path/to/file.txt"
)

# Löse eine komplexe Aufgabe
result = agent.solve_complex_task(
    "Erstelle ein Python-Skript, das eine REST API mit FastAPI implementiert."
)
```

### OpenHands MCP-Server

Der OpenHands MCP-Server kann wie folgt gestartet werden:

```bash
./start-mcp-servers.sh --openhands
```

Oder mit zusätzlichen Optionen:

```bash
./start-mcp-servers.sh --openhands --max-workers 10 --verbose
```

### n8n MCP-Server

Der n8n MCP-Server kann wie folgt gestartet werden:

```bash
./start-mcp-servers.sh --n8n --api-key YOUR_API_KEY
```

Oder mit zusätzlichen Optionen:

```bash
./start-mcp-servers.sh --n8n --api-key YOUR_API_KEY --n8n-url http://localhost:5678 --verbose
```

### Kommandozeilentool

Das Kommandozeilentool kann wie folgt verwendet werden:

```bash
python src/openhands/cli.py task "Erstelle eine Liste der 5 wichtigsten Python-Bibliotheken für Datenanalyse."
```

Oder mit zusätzlichen Optionen:

```bash
python src/openhands/cli.py --config config.json --verbose task "Erstelle eine Liste der 5 wichtigsten Python-Bibliotheken für Datenanalyse."
```

### Beispiele

Das Projekt enthält verschiedene Beispiele, die die Verwendung der OpenHands-Integration demonstrieren:

- **Parallele OpenHands-Aufgaben**: Demonstriert, wie man mehrere OpenHands-Agenten parallel verwenden kann, um Aufgaben parallel auszuführen.
- **OpenHands n8n Integration**: Demonstriert, wie man OpenHands mit n8n-Workflows integrieren kann, um komplexe Automatisierungsaufgaben zu lösen.

Die Beispiele können wie folgt ausgeführt werden:

```bash
python examples/parallel_openhands_tasks.py
python examples/openhands_n8n_integration.py --n8n-api-key YOUR_API_KEY
```

## Parallele Ausführung von Aufgaben

Eine der Hauptfunktionen der OpenHands-Integration ist die Möglichkeit, mehrere OpenHands-Agenten parallel zu laden und Aufgaben parallel auszuführen. Dies ermöglicht eine effiziente Nutzung der Ressourcen und eine schnellere Bearbeitung von Aufgaben.

Der OpenHands MCP-Server verwendet einen Thread-Pool, um Aufgaben parallel auszuführen. Die maximale Anzahl von Worker-Threads kann beim Starten des Servers angegeben werden.

Hier ist ein Beispiel für die parallele Ausführung von Aufgaben:

```python
from src.mcp.client import MCPClient

# Verbinde mit dem OpenHands MCP-Server
client = MCPClient("http://localhost:3006")

# Erstelle OpenHands-Agenten
agent_ids = []
for i in range(3):
    result = client.call_function("create_agent", {})
    agent_ids.append(result["agent_id"])

# Definiere Aufgaben
tasks = [
    {
        "agent_id": agent_ids[0],
        "task": "Aufgabe 1"
    },
    {
        "agent_id": agent_ids[1],
        "task": "Aufgabe 2"
    },
    {
        "agent_id": agent_ids[2],
        "task": "Aufgabe 3"
    }
]

# Führe Aufgaben parallel aus
task_ids = []
for task in tasks:
    result = client.call_function("execute_task", task)
    task_ids.append(result["task_id"])

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

## Integration mit n8n

Die OpenHands-Integration ermöglicht die nahtlose Integration mit n8n-Workflows. Dies ermöglicht die Automatisierung komplexer Prozesse, bei denen OpenHands als KI-Agent fungiert und n8n die Workflow-Orchestrierung übernimmt.

Der n8n MCP-Server stellt verschiedene Funktionen bereit, um n8n-Workflows zu verwalten und auszuführen. Diese Funktionen können von OpenHands oder anderen Clients aufgerufen werden.

Hier ist ein Beispiel für die Integration mit n8n:

```python
from src.mcp.client import MCPClient

# Verbinde mit dem n8n MCP-Server
client = MCPClient("http://localhost:3000")

# Hole alle Workflows
workflows = client.call_function("get_workflows", {})

# Führe einen Workflow aus
result = client.call_function("execute_workflow", {
    "workflow_id": workflows["workflows"][0]["id"],
    "data": {
        "input": "Beispieldaten"
    }
})

# Verwalte einen Workflow
result = client.call_function("manage_workflow", {
    "workflow_name": "OpenHands Integration",
    "action": "start"
})
```

## Fehlerbehebung

### OpenHands API nicht erreichbar

Wenn die OpenHands API nicht erreichbar ist, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass die OpenHands API läuft und unter der angegebenen URL erreichbar ist.
2. Überprüfen Sie, ob der API-Schlüssel korrekt ist.
3. Überprüfen Sie, ob die Netzwerkverbindung funktioniert.

### MCP-Server nicht erreichbar

Wenn ein MCP-Server nicht erreichbar ist, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der MCP-Server läuft und unter der angegebenen URL erreichbar ist.
2. Überprüfen Sie, ob die Netzwerkverbindung funktioniert.
3. Überprüfen Sie die Logs des MCP-Servers auf Fehler.

### n8n nicht erreichbar

Wenn n8n nicht erreichbar ist, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass n8n läuft und unter der angegebenen URL erreichbar ist.
2. Überprüfen Sie, ob der API-Schlüssel korrekt ist.
3. Überprüfen Sie, ob die Netzwerkverbindung funktioniert.

## Fazit

Die OpenHands-Integration bietet eine leistungsstarke Möglichkeit, OpenHands als allgemeinen KI-Agenten in das Dev-Server-Workflow-Projekt zu integrieren. Durch die Möglichkeit, mehrere OpenHands-Agenten parallel zu laden und Aufgaben parallel auszuführen, sowie die nahtlose Integration mit n8n-Workflows, können komplexe Automatisierungsaufgaben effizient gelöst werden.