# MCP-Server-Generator

Der MCP-Server-Generator ermöglicht die dynamische Erstellung und Verwaltung von MCP-Servern basierend auf benutzerdefinierten Konfigurationen. Mit diesem Tool können Sie schnell und einfach neue MCP-Server erstellen, starten, stoppen und löschen, ohne Code schreiben zu müssen.

## Überblick

Der MCP-Server-Generator bietet folgende Funktionen:

- Erstellen von MCP-Servern aus Vorlagen oder mit benutzerdefinierter Implementierung
- Starten, Stoppen und Neustarten von MCP-Servern
- Abrufen von Informationen über MCP-Server
- Abrufen von Logs von MCP-Servern
- Löschen von MCP-Servern

Der Generator verwendet ein Verzeichnis für generierte Server, in dem für jeden Server ein eigenes Unterverzeichnis erstellt wird. In diesem Unterverzeichnis werden die Konfiguration, die Implementierung und die Logs des Servers gespeichert.

## Installation

Der MCP-Server-Generator ist Teil des Dev-Server-Workflow-Projekts und wird mit diesem installiert. Stellen Sie sicher, dass Sie die folgenden Abhängigkeiten installiert haben:

```bash
pip install requests aiohttp
```

## Starten des Generators

Der MCP-Server-Generator kann wie folgt gestartet werden:

```bash
./start-mcp-servers.sh --generator
```

Oder mit zusätzlichen Optionen:

```bash
./start-mcp-servers.sh --generator --servers-dir my_servers --verbose
```

Alternativ kann der Generator auch direkt gestartet werden:

```bash
python src/mcp/generator_server.py --servers-dir my_servers --verbose
```

## Konfiguration

Der MCP-Server-Generator kann über Kommandozeilenargumente konfiguriert werden:

- `--host`: Host für den MCP-Server-Generator (Standard: 0.0.0.0)
- `--port`: Port für den MCP-Server-Generator (Standard: 3007)
- `--servers-dir`: Verzeichnis für generierte Server (Standard: generated_servers)
- `--verbose`: Ausführliche Ausgabe

## Verfügbare Funktionen

Der MCP-Server-Generator stellt folgende Funktionen bereit:

### create_server

Erstellt einen neuen MCP-Server.

**Parameter:**
- `name`: Name des Servers
- `description`: Beschreibung des Servers
- `functions`: Funktionen des Servers
- `port`: Port für den Server
- `implementation`: Python-Code für die Implementierung der Funktionen

**Rückgabe:**
```json
{
  "server_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Server",
  "description": "Ein benutzerdefinierter MCP-Server",
  "functions": [...],
  "port": 3100,
  "status": "stopped"
}
```

### get_server

Ruft Informationen über einen MCP-Server ab.

**Parameter:**
- `server_id`: ID des Servers

**Rückgabe:**
```json
{
  "server_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Server",
  "description": "Ein benutzerdefinierter MCP-Server",
  "functions": [...],
  "port": 3100,
  "status": "running"
}
```

### list_servers

Listet alle verfügbaren MCP-Server auf.

**Parameter:**
Keine

**Rückgabe:**
```json
{
  "servers": [
    {
      "server_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "My Server",
      "description": "Ein benutzerdefinierter MCP-Server",
      "port": 3100,
      "status": "running"
    },
    {
      "server_id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Another Server",
      "description": "Ein weiterer MCP-Server",
      "port": 3101,
      "status": "stopped"
    }
  ]
}
```

### update_server

Aktualisiert einen MCP-Server.

**Parameter:**
- `server_id`: ID des Servers
- `name`: Name des Servers
- `description`: Beschreibung des Servers
- `functions`: Funktionen des Servers
- `implementation`: Python-Code für die Implementierung der Funktionen

**Rückgabe:**
```json
{
  "server_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Server",
  "description": "Ein aktualisierter MCP-Server",
  "functions": [...],
  "port": 3100,
  "status": "stopped"
}
```

### delete_server

Löscht einen MCP-Server.

**Parameter:**
- `server_id`: ID des Servers

**Rückgabe:**
```json
{
  "success": true,
  "message": "Server 550e8400-e29b-41d4-a716-446655440000 erfolgreich gelöscht"
}
```

### start_server

Startet einen MCP-Server.

**Parameter:**
- `server_id`: ID des Servers

**Rückgabe:**
```json
{
  "success": true,
  "message": "Server 550e8400-e29b-41d4-a716-446655440000 erfolgreich gestartet",
  "pid": 1234
}
```

### stop_server

Stoppt einen MCP-Server.

**Parameter:**
- `server_id`: ID des Servers

**Rückgabe:**
```json
{
  "success": true,
  "message": "Server 550e8400-e29b-41d4-a716-446655440000 erfolgreich gestoppt"
}
```

### restart_server

Startet einen MCP-Server neu.

**Parameter:**
- `server_id`: ID des Servers

**Rückgabe:**
```json
{
  "success": true,
  "message": "Server 550e8400-e29b-41d4-a716-446655440000 erfolgreich neu gestartet",
  "pid": 1234
}
```

### get_server_status

Ruft den Status eines MCP-Servers ab.

**Parameter:**
- `server_id`: ID des Servers

**Rückgabe:**
```json
{
  "server_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running"
}
```

### get_server_logs

Ruft die Logs eines MCP-Servers ab.

**Parameter:**
- `server_id`: ID des Servers
- `lines`: Anzahl der Zeilen (Standard: 100)

**Rückgabe:**
```json
{
  "logs": "2023-05-08 12:34:56 - INFO - MCP-Server gestartet auf ('0.0.0.0', 3100)\n..."
}
```

### create_server_from_template

Erstellt einen neuen MCP-Server aus einer Vorlage.

**Parameter:**
- `name`: Name des Servers
- `template`: Name der Vorlage
- `parameters`: Parameter für die Vorlage

**Rückgabe:**
```json
{
  "server_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Server",
  "description": "Ein MCP-Server aus einer Vorlage",
  "functions": [...],
  "port": 3100,
  "status": "stopped"
}
```

## Verfügbare Vorlagen

Der MCP-Server-Generator bietet folgende Vorlagen:

### simple

Ein einfacher MCP-Server mit grundlegenden Funktionen.

**Funktionen:**
- `hello_world`: Gibt "Hello, World!" zurück
- `echo`: Gibt den übergebenen Text zurück

### calculator

Ein MCP-Server für mathematische Berechnungen.

**Funktionen:**
- `add`: Addiert zwei Zahlen
- `subtract`: Subtrahiert zwei Zahlen
- `multiply`: Multipliziert zwei Zahlen
- `divide`: Dividiert zwei Zahlen

### file_manager

Ein MCP-Server für Dateiverwaltung.

**Funktionen:**
- `read_file`: Liest eine Datei
- `write_file`: Schreibt in eine Datei
- `delete_file`: Löscht eine Datei
- `list_directory`: Listet den Inhalt eines Verzeichnisses auf

### database

Ein MCP-Server für einfache Datenbankverwaltung.

**Funktionen:**
- `create_table`: Erstellt eine Tabelle
- `insert_data`: Fügt Daten in eine Tabelle ein
- `query_data`: Fragt Daten aus einer Tabelle ab
- `delete_data`: Löscht Daten aus einer Tabelle

## Beispiele

### Erstellen eines Servers aus einer Vorlage

```python
from src.mcp.client import MCPClient

# Verbinde mit dem MCP-Server-Generator
client = MCPClient("http://localhost:3007")

# Erstelle einen Server aus der Vorlage
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

if result["success"]:
    print(f"Server gestartet (PID: {result['pid']})")
else:
    print(f"Fehler beim Starten des Servers: {result['message']}")
```

### Erstellen eines benutzerdefinierten Servers

```python
from src.mcp.client import MCPClient

# Verbinde mit dem MCP-Server-Generator
client = MCPClient("http://localhost:3007")

# Erstelle einen benutzerdefinierten Server
result = client.call_function("create_server", {
    "name": "Custom Server",
    "description": "Ein benutzerdefinierter MCP-Server",
    "functions": [
        {
            "name": "greet",
            "description": "Begrüßt einen Benutzer",
            "parameters": {
                "name": {
                    "type": "string",
                    "description": "Name des Benutzers"
                }
            }
        }
    ],
    "port": 3101,
    "implementation": """
def _greet(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Begrüßt einen Benutzer.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    name = parameters.get("name", "Welt")
    return {
        "message": f"Hallo, {name}!"
    }
"""
})

server_id = result["server_id"]
print(f"Server erstellt (ID: {server_id})")

# Starte den Server
result = client.call_function("start_server", {
    "server_id": server_id
})

if result["success"]:
    print(f"Server gestartet (PID: {result['pid']})")
else:
    print(f"Fehler beim Starten des Servers: {result['message']}")
```

### Verwenden eines generierten Servers

```python
from src.mcp.client import MCPClient

# Verbinde mit dem generierten Server
client = MCPClient("http://localhost:3100")

# Hole die verfügbaren Funktionen
functions = client.get_functions()
print(f"Verfügbare Funktionen: {[f['name'] for f in functions]}")

# Rufe eine Funktion auf
result = client.call_function("add", {
    "a": 5,
    "b": 3
})
print(f"Ergebnis: {result}")
```

## Fehlerbehebung

### Generator startet nicht

Wenn der Generator nicht startet, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Port nicht bereits verwendet wird.
2. Überprüfen Sie, ob alle Abhängigkeiten installiert sind.
3. Überprüfen Sie die Logs auf Fehler.

### Server startet nicht

Wenn ein generierter Server nicht startet, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Port nicht bereits verwendet wird.
2. Überprüfen Sie, ob die Implementierung korrekt ist.
3. Überprüfen Sie die Logs des Servers auf Fehler.

### Server ist nicht erreichbar

Wenn ein generierter Server nicht erreichbar ist, überprüfen Sie Folgendes:

1. Stellen Sie sicher, dass der Server gestartet wurde.
2. Überprüfen Sie, ob der Port korrekt ist.
3. Überprüfen Sie die Logs des Servers auf Fehler.

## Fazit

Der MCP-Server-Generator bietet eine leistungsstarke Möglichkeit, dynamisch MCP-Server zu erstellen und zu verwalten. Durch die Verwendung von Vorlagen oder benutzerdefinierten Implementierungen können Sie schnell und einfach neue Server erstellen, die genau Ihren Anforderungen entsprechen.