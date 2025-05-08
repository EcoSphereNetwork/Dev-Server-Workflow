# MCP-Server Integration

Diese Dokumentation beschreibt die Integration der verschiedenen MCP-Server im Dev-Server-Workflow-Projekt. Das Projekt umfasst mehrere MCP-Server, die unterschiedliche Funktionen bereitstellen und miteinander interagieren können.

## Überblick

Das Dev-Server-Workflow-Projekt umfasst folgende MCP-Server:

1. **n8n MCP-Server**: Ermöglicht die Integration mit n8n-Workflows
2. **OpenHands MCP-Server**: Ermöglicht die parallele Ausführung von OpenHands-Aufgaben
3. **MCP-Server-Generator**: Ermöglicht die dynamische Erstellung und Verwaltung von MCP-Servern
4. **Dynamisch generierte MCP-Server**: Benutzerdefinierte MCP-Server, die vom Generator erstellt wurden

Diese Server können unabhängig voneinander oder zusammen gestartet werden und bieten eine flexible und erweiterbare Architektur für verschiedene Anwendungsfälle.

## Architektur

Die MCP-Server-Architektur basiert auf dem Model Context Protocol (MCP), das eine einheitliche Schnittstelle für die Kommunikation zwischen verschiedenen Komponenten bietet. Jeder MCP-Server implementiert diese Schnittstelle und kann von anderen Komponenten über einen MCP-Client angesprochen werden.

Die Architektur ermöglicht eine lose Kopplung zwischen den Komponenten und eine einfache Erweiterbarkeit durch neue MCP-Server. Die Kommunikation erfolgt über TCP/IP, wobei jeder Server auf einem eigenen Port lauscht.

### Kommunikationsfluss

1. Ein Client sendet eine Anfrage an einen MCP-Server
2. Der MCP-Server verarbeitet die Anfrage und führt die entsprechende Funktion aus
3. Der MCP-Server sendet eine Antwort an den Client
4. Der Client verarbeitet die Antwort

### Ports

Die MCP-Server verwenden standardmäßig folgende Ports:

- **n8n MCP-Server**: 3000
- **OpenHands MCP-Server**: 3006
- **MCP-Server-Generator**: 3007
- **Dynamisch generierte MCP-Server**: 3100 und höher

## Start und Stopp der MCP-Server

Die MCP-Server können über die Start- und Stopp-Skripte gestartet und gestoppt werden.

### Starten der MCP-Server

```bash
./start-mcp-servers.sh [Optionen]
```

Optionen:
- `--n8n`: Startet den n8n MCP-Server
- `--openhands`: Startet den OpenHands MCP-Server
- `--generator`: Startet den MCP-Server-Generator
- `--all`: Startet alle MCP-Server
- `--api-key KEY`: API-Schlüssel für n8n
- `--max-workers N`: Maximale Anzahl von Worker-Threads für OpenHands
- `--servers-dir DIR`: Verzeichnis für generierte Server
- `--verbose`: Ausführliche Ausgabe

Beispiel:
```bash
./start-mcp-servers.sh --all --api-key my-api-key --max-workers 10 --verbose
```

### Stoppen der MCP-Server

```bash
./stop-mcp-servers.sh [Optionen]
```

Optionen:
- `--n8n`: Stoppt den n8n MCP-Server
- `--openhands`: Stoppt den OpenHands MCP-Server
- `--generator`: Stoppt den MCP-Server-Generator und alle generierten Server
- `--all`: Stoppt alle MCP-Server

Beispiel:
```bash
./stop-mcp-servers.sh --all
```

## Integration der MCP-Server

Die MCP-Server können auf verschiedene Weise integriert werden, um komplexe Anwendungsfälle zu unterstützen.

### Integration mit n8n

Der n8n MCP-Server ermöglicht die Integration mit n8n-Workflows. n8n ist eine Workflow-Automatisierungsplattform, die es ermöglicht, verschiedene Dienste und Anwendungen zu verbinden und zu automatisieren.

Mit dem n8n MCP-Server können Sie:
- n8n-Workflows erstellen, aktualisieren und löschen
- n8n-Workflows ausführen
- n8n-Workflows aktivieren und deaktivieren
- Informationen über n8n-Workflows abrufen

Beispiel für die Integration mit n8n:
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
```

### Integration mit OpenHands

Der OpenHands MCP-Server ermöglicht die parallele Ausführung von OpenHands-Aufgaben. OpenHands ist ein KI-Agent, der verschiedene Aufgaben übernehmen und als zentraler Manager für alle Prozesse dienen kann.

Mit dem OpenHands MCP-Server können Sie:
- OpenHands-Agenten erstellen und verwalten
- Aufgaben parallel ausführen
- Den Status von Aufgaben überwachen
- Ergebnisse von Aufgaben abrufen

Beispiel für die Integration mit OpenHands:
```python
from src.mcp.client import MCPClient

# Verbinde mit dem OpenHands MCP-Server
client = MCPClient("http://localhost:3006")

# Erstelle einen OpenHands-Agenten
result = client.call_function("create_agent", {})
agent_id = result["agent_id"]

# Führe eine Aufgabe aus
result = client.call_function("execute_task", {
    "agent_id": agent_id,
    "task": "Erstelle eine Liste der 5 wichtigsten Python-Bibliotheken für Datenanalyse."
})
task_id = result["task_id"]

# Hole das Ergebnis der Aufgabe
result = client.call_function("get_task_result", {
    "task_id": task_id
})
```

### Integration mit dem MCP-Server-Generator

Der MCP-Server-Generator ermöglicht die dynamische Erstellung und Verwaltung von MCP-Servern. Mit diesem Tool können Sie schnell und einfach neue MCP-Server erstellen, starten, stoppen und löschen, ohne Code schreiben zu müssen.

Mit dem MCP-Server-Generator können Sie:
- MCP-Server aus Vorlagen erstellen
- Benutzerdefinierte MCP-Server erstellen
- MCP-Server starten, stoppen und neustarten
- Informationen über MCP-Server abrufen
- Logs von MCP-Servern abrufen

Beispiel für die Integration mit dem MCP-Server-Generator:
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

# Starte den MCP-Server
result = client.call_function("start_server", {
    "server_id": server_id
})
```

### Integration mit dynamisch generierten MCP-Servern

Dynamisch generierte MCP-Server sind benutzerdefinierte MCP-Server, die vom MCP-Server-Generator erstellt wurden. Diese Server können verschiedene Funktionen bereitstellen und mit anderen Komponenten des Systems interagieren.

Beispiel für die Integration mit einem dynamisch generierten MCP-Server:
```python
from src.mcp.client import MCPClient

# Verbinde mit einem dynamisch generierten MCP-Server
client = MCPClient("http://localhost:3100")

# Hole die verfügbaren Funktionen
functions = client.get_functions()

# Rufe eine Funktion auf
result = client.call_function("add", {
    "a": 5,
    "b": 3
})
```

## Komplexe Integrationsszenarien

Die MCP-Server können in komplexen Szenarien kombiniert werden, um leistungsstarke Anwendungen zu erstellen.

### Szenario 1: KI-gestützte Workflow-Automatisierung

In diesem Szenario wird OpenHands verwendet, um n8n-Workflows zu erstellen und auszuführen, die wiederum mit dynamisch generierten MCP-Servern interagieren.

1. OpenHands analysiert eine Aufgabe und entscheidet, welche Workflows erstellt werden müssen
2. OpenHands verwendet den n8n MCP-Server, um die Workflows zu erstellen
3. OpenHands verwendet den MCP-Server-Generator, um benutzerdefinierte MCP-Server zu erstellen
4. OpenHands startet die Workflows, die mit den generierten MCP-Servern interagieren
5. OpenHands überwacht die Ausführung und sammelt die Ergebnisse

### Szenario 2: Dynamische Microservices-Architektur

In diesem Szenario werden dynamisch generierte MCP-Server verwendet, um eine flexible Microservices-Architektur zu erstellen.

1. Der MCP-Server-Generator erstellt verschiedene MCP-Server für unterschiedliche Funktionen
2. Die MCP-Server kommunizieren miteinander über ihre MCP-Schnittstellen
3. Ein zentraler Orchestrator (z.B. OpenHands) verwaltet die MCP-Server und koordiniert ihre Aktionen
4. Neue Funktionen können durch das Erstellen neuer MCP-Server hinzugefügt werden, ohne bestehende Komponenten zu ändern

### Szenario 3: Parallele Datenverarbeitung

In diesem Szenario werden mehrere OpenHands-Agenten verwendet, um Daten parallel zu verarbeiten.

1. Ein Hauptprozess teilt die Daten in Teilmengen auf
2. Für jede Teilmenge wird ein OpenHands-Agent erstellt
3. Die Agenten verarbeiten die Daten parallel
4. Die Ergebnisse werden gesammelt und zusammengeführt

## Fehlerbehebung

### MCP-Server startet nicht

Wenn ein MCP-Server nicht startet, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Port nicht bereits verwendet wird.
2. Überprüfen Sie, ob alle Abhängigkeiten installiert sind.
3. Überprüfen Sie die Logs auf Fehler.

### MCP-Server ist nicht erreichbar

Wenn ein MCP-Server nicht erreichbar ist, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Server gestartet wurde.
2. Überprüfen Sie, ob der Port korrekt ist.
3. Überprüfen Sie die Logs des Servers auf Fehler.

### Fehler bei der Ausführung von Funktionen

Wenn bei der Ausführung von Funktionen Fehler auftreten, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass die Funktion existiert und korrekt implementiert ist.
2. Überprüfen Sie, ob die Parameter korrekt sind.
3. Überprüfen Sie die Logs des Servers auf Fehler.

## Fazit

Die Integration der verschiedenen MCP-Server im Dev-Server-Workflow-Projekt bietet eine flexible und erweiterbare Architektur für verschiedene Anwendungsfälle. Durch die Kombination von n8n, OpenHands und dem MCP-Server-Generator können komplexe Anwendungen erstellt werden, die verschiedene Funktionen bereitstellen und miteinander interagieren können.