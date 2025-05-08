# MCP-Client

Der MCP-Client ermöglicht die Kommunikation mit MCP-Servern über das Model Context Protocol (MCP). Er bietet eine einfache und einheitliche Schnittstelle für den Zugriff auf verschiedene MCP-Server und deren Funktionen.

## Überblick

Der MCP-Client bietet folgende Funktionen:

- Verbindung zu MCP-Servern herstellen
- Informationen über MCP-Server abrufen
- Verfügbare Funktionen eines MCP-Servers abrufen
- Funktionen eines MCP-Servers aufrufen
- Verbindung zu einem MCP-Server testen

Der Client verwendet das Model Context Protocol (MCP), um mit den Servern zu kommunizieren. Dieses Protokoll definiert eine einheitliche Schnittstelle für die Kommunikation zwischen verschiedenen Komponenten und ermöglicht eine lose Kopplung zwischen Client und Server.

## Installation

Der MCP-Client ist Teil des Dev-Server-Workflow-Projekts und wird mit diesem installiert. Stellen Sie sicher, dass Sie die folgende Abhängigkeit installiert haben:

```bash
pip install requests
```

## Verwendung

### Verbindung zu einem MCP-Server herstellen

```python
from src.mcp.client import MCPClient

# Erstelle einen MCP-Client
client = MCPClient("http://localhost:3000")
```

### Informationen über einen MCP-Server abrufen

```python
# Hole Informationen über den MCP-Server
server_info = client.get_server_info()
print(f"Server: {server_info['name']} v{server_info['version']}")
print(f"Beschreibung: {server_info['description']}")
print(f"Status: {server_info['status']}")
```

### Verfügbare Funktionen eines MCP-Servers abrufen

```python
# Hole die verfügbaren Funktionen des MCP-Servers
functions = client.get_functions()
for function in functions:
    print(f"Funktion: {function['name']}")
    print(f"Beschreibung: {function['description']}")
    print(f"Parameter: {function['parameters']}")
    print()
```

### Funktion eines MCP-Servers aufrufen

```python
# Rufe eine Funktion des MCP-Servers auf
result = client.call_function("add", {
    "a": 5,
    "b": 3
})
print(f"Ergebnis: {result}")
```

### Verbindung zu einem MCP-Server testen

```python
# Teste die Verbindung zum MCP-Server
success, message = client.test_connection()
if success:
    print(f"Verbindung erfolgreich: {message}")
else:
    print(f"Verbindung fehlgeschlagen: {message}")
```

## Fehlerbehandlung

Der MCP-Client bietet eine integrierte Fehlerbehandlung für verschiedene Fehlerszenarien:

### Verbindungsfehler

Wenn der Client keine Verbindung zum MCP-Server herstellen kann, wird eine `MCPConnectionError` ausgelöst:

```python
from src.mcp.client import MCPClient, MCPConnectionError

try:
    client = MCPClient("http://localhost:9999")  # Nicht existierender Server
    client.get_server_info()
except MCPConnectionError as e:
    print(f"Verbindungsfehler: {e}")
```

### Funktionsfehler

Wenn bei der Ausführung einer Funktion ein Fehler auftritt, wird eine `MCPFunctionError` ausgelöst:

```python
from src.mcp.client import MCPClient, MCPFunctionError

try:
    client = MCPClient("http://localhost:3000")
    client.call_function("nicht_existierende_funktion", {})
except MCPFunctionError as e:
    print(f"Funktionsfehler: {e}")
```

### Allgemeine Fehler

Für allgemeine Fehler wird eine `MCPError` ausgelöst:

```python
from src.mcp.client import MCPClient, MCPError

try:
    client = MCPClient("http://localhost:3000")
    # ...
except MCPError as e:
    print(f"Fehler: {e}")
```

## Erweiterte Verwendung

### Timeout konfigurieren

Sie können den Timeout für Anfragen konfigurieren:

```python
# Erstelle einen MCP-Client mit einem Timeout von 30 Sekunden
client = MCPClient("http://localhost:3000", timeout=30)
```

### Benutzerdefinierte Header

Sie können benutzerdefinierte Header für Anfragen konfigurieren:

```python
# Erstelle einen MCP-Client mit benutzerdefinierten Headern
client = MCPClient(
    "http://localhost:3000",
    headers={
        "X-API-Key": "my-api-key",
        "User-Agent": "My-App/1.0"
    }
)
```

### Mehrere MCP-Server verwalten

Sie können den `MCPClientManager` verwenden, um mehrere MCP-Server zu verwalten:

```python
from src.mcp.client import MCPClientManager

# Definiere die MCP-Server
servers = [
    {
        "name": "n8n",
        "url": "http://localhost:3000",
        "description": "n8n workflow operations"
    },
    {
        "name": "openhands",
        "url": "http://localhost:3006",
        "description": "OpenHands operations"
    },
    {
        "name": "generator",
        "url": "http://localhost:3007",
        "description": "MCP-Server-Generator operations"
    }
]

# Erstelle einen MCP-Client-Manager
manager = MCPClientManager(servers)

# Hole einen Client für einen bestimmten Server
n8n_client = manager.get_client("n8n")
openhands_client = manager.get_client("openhands")
generator_client = manager.get_client("generator")

# Verwende die Clients
n8n_info = n8n_client.get_server_info()
openhands_info = openhands_client.get_server_info()
generator_info = generator_client.get_server_info()
```

### Asynchrone Anfragen

Für asynchrone Anfragen können Sie den `AsyncMCPClient` verwenden:

```python
import asyncio
from src.mcp.client import AsyncMCPClient

async def main():
    # Erstelle einen asynchronen MCP-Client
    client = AsyncMCPClient("http://localhost:3000")
    
    # Hole Informationen über den MCP-Server
    server_info = await client.get_server_info()
    print(f"Server: {server_info['name']} v{server_info['version']}")
    
    # Hole die verfügbaren Funktionen des MCP-Servers
    functions = await client.get_functions()
    for function in functions:
        print(f"Funktion: {function['name']}")
    
    # Rufe eine Funktion des MCP-Servers auf
    result = await client.call_function("add", {
        "a": 5,
        "b": 3
    })
    print(f"Ergebnis: {result}")

# Führe die asynchrone Funktion aus
asyncio.run(main())
```

## Beispiele

### Beispiel 1: Einfache Berechnung mit einem Taschenrechner-MCP-Server

```python
from src.mcp.client import MCPClient

# Verbinde mit dem Taschenrechner-MCP-Server
client = MCPClient("http://localhost:3100")

# Führe einige Berechnungen durch
add_result = client.call_function("add", {"a": 5, "b": 3})
subtract_result = client.call_function("subtract", {"a": 10, "b": 4})
multiply_result = client.call_function("multiply", {"a": 6, "b": 7})
divide_result = client.call_function("divide", {"a": 20, "b": 4})

print(f"5 + 3 = {add_result['result']}")
print(f"10 - 4 = {subtract_result['result']}")
print(f"6 * 7 = {multiply_result['result']}")
print(f"20 / 4 = {divide_result['result']}")
```

### Beispiel 2: Dateiverwaltung mit einem Dateiverwaltungs-MCP-Server

```python
from src.mcp.client import MCPClient

# Verbinde mit dem Dateiverwaltungs-MCP-Server
client = MCPClient("http://localhost:3101")

# Schreibe eine Datei
client.call_function("write_file", {
    "path": "example.txt",
    "content": "Dies ist ein Beispieltext."
})

# Lese die Datei
result = client.call_function("read_file", {
    "path": "example.txt"
})
print(f"Dateiinhalt: {result['content']}")

# Liste den Inhalt des Verzeichnisses auf
result = client.call_function("list_directory", {
    "path": "."
})
print(f"Verzeichnisinhalt: {result['files']}")

# Lösche die Datei
client.call_function("delete_file", {
    "path": "example.txt"
})
```

### Beispiel 3: Verwaltung von n8n-Workflows

```python
from src.mcp.client import MCPClient

# Verbinde mit dem n8n MCP-Server
client = MCPClient("http://localhost:3000")

# Hole alle Workflows
workflows = client.call_function("get_workflows", {})
for workflow in workflows["workflows"]:
    print(f"Workflow: {workflow['name']} (ID: {workflow['id']})")

# Führe einen Workflow aus
result = client.call_function("execute_workflow", {
    "workflow_id": workflows["workflows"][0]["id"],
    "data": {
        "input": "Beispieldaten"
    }
})
print(f"Ausführungsergebnis: {result}")
```

### Beispiel 4: Parallele Ausführung von OpenHands-Aufgaben

```python
from src.mcp.client import MCPClient
import time

# Verbinde mit dem OpenHands MCP-Server
client = MCPClient("http://localhost:3006")

# Erstelle OpenHands-Agenten
agent_ids = []
for i in range(3):
    result = client.call_function("create_agent", {})
    agent_ids.append(result["agent_id"])
    print(f"Agent {i+1} erstellt (ID: {result['agent_id']})")

# Definiere Aufgaben
tasks = [
    {
        "agent_id": agent_ids[0],
        "task": "Erstelle eine Liste der 5 wichtigsten Python-Bibliotheken für Datenanalyse."
    },
    {
        "agent_id": agent_ids[1],
        "task": "Erkläre die Unterschiede zwischen REST API und GraphQL."
    },
    {
        "agent_id": agent_ids[2],
        "task": "Beschreibe die Architektur einer modernen Microservices-Anwendung."
    }
]

# Führe Aufgaben parallel aus
task_ids = []
for i, task in enumerate(tasks):
    result = client.call_function("execute_task", task)
    task_ids.append(result["task_id"])
    print(f"Aufgabe {i+1} gestartet (ID: {result['task_id']})")

# Warte auf die Ergebnisse
results = {}
all_completed = False

while not all_completed:
    all_completed = True
    
    for task_id in task_ids:
        if task_id in results:
            continue
        
        result = client.call_function("get_task_status", {
            "task_id": task_id
        })
        
        status = result["status"]
        print(f"Aufgabe {task_id}: {status}")
        
        if status != "completed" and status != "failed" and status != "cancelled":
            all_completed = False
        elif status == "completed" and task_id not in results:
            result = client.call_function("get_task_result", {
                "task_id": task_id
            })
            results[task_id] = result
            print(f"Aufgabe {task_id} abgeschlossen")
    
    if not all_completed:
        time.sleep(1)

# Zeige die Ergebnisse
for i, task_id in enumerate(task_ids):
    result = results[task_id]
    print(f"Ergebnis für Aufgabe {i+1} (ID: {task_id}):")
    print(result["result"])
    print()

# Lösche die Agenten
for agent_id in agent_ids:
    client.call_function("delete_agent", {
        "agent_id": agent_id
    })
```

### Beispiel 5: Dynamische Erstellung von MCP-Servern

```python
from src.mcp.client import MCPClient

# Verbinde mit dem MCP-Server-Generator
client = MCPClient("http://localhost:3007")

# Erstelle einen MCP-Server aus einer Vorlage
result = client.call_function("create_server_from_template", {
    "name": "My Calculator",
    "template": "calculator",
    "parameters": {
        "port": 3100
    }
})
server_id = result["server_id"]
print(f"Server erstellt (ID: {server_id})")

# Starte den Server
result = client.call_function("start_server", {
    "server_id": server_id
})
print(f"Server gestartet (PID: {result['pid']})")

# Verwende den Server
calculator_client = MCPClient("http://localhost:3100")
add_result = calculator_client.call_function("add", {"a": 5, "b": 3})
print(f"5 + 3 = {add_result['result']}")

# Stoppe und lösche den Server
client.call_function("stop_server", {"server_id": server_id})
client.call_function("delete_server", {"server_id": server_id})
print("Server gestoppt und gelöscht")
```

## Fazit

Der MCP-Client bietet eine einfache und einheitliche Schnittstelle für den Zugriff auf verschiedene MCP-Server und deren Funktionen. Durch die Verwendung des Model Context Protocols (MCP) ermöglicht er eine lose Kopplung zwischen Client und Server und eine flexible Integration verschiedener Komponenten.