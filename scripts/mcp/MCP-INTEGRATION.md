# MCP-Integration für Dev-Server-Workflow

Diese Dokumentation beschreibt die Integration des Model Context Protocols (MCP) in das Dev-Server-Workflow-System.

## Überblick

Die MCP-Integration ermöglicht es KI-Agenten wie OpenHands, direkt mit n8n-Workflows und anderen Diensten zu interagieren. Die Integration besteht aus folgenden Komponenten:

1. **MCP-Server**: Stellen Funktionalität über das MCP-Protokoll bereit
   - n8n MCP-Server: Ermöglicht den Zugriff auf n8n-Workflows
   - Filesystem MCP-Server: Ermöglicht den Zugriff auf das Dateisystem
   - Weitere MCP-Server für GitHub, GitLab, etc.

2. **MCP-Client**: Ermöglicht die Kommunikation mit MCP-Servern
   - Unterstützt verschiedene Transport-Typen (stdio, http, sse)
   - Kann für Tests und Debugging verwendet werden

3. **n8n-Workflows**: Implementieren die eigentliche Funktionalität
   - Werden über den n8n MCP-Server aufgerufen
   - Können mit verschiedenen Diensten interagieren (GitHub, GitLab, OpenProject, etc.)

## Komponenten

### MCP-Server

- `src/mcp/improved_n8n_mcp_server.py`: Ein verbesserter MCP-Server für n8n
- `src/n8n_mcp_server.py`: Der ursprüngliche MCP-Server für n8n

### MCP-Client

- `src/mcp/mcp-client.py`: Ein Client für das MCP-Protokoll

### Test-Skripte

- `src/mcp/test-mcp-integration.py`: Testet die MCP-Integration
- `tools/mcp/start-mcp-servers.sh`: Startet die MCP-Server

### Konfiguration

- `src/mcp/openhands-mcp-config.json`: Konfiguration für OpenHands

### n8n-Workflows

- `src/mcp/n8n-mcp-workflow.json`: Ein Beispiel-Workflow für die MCP-Integration

## Verwendung

### MCP-Server starten

```bash
cd /workspace/Dev-Server-Workflow
tools/mcp/start-mcp-servers.sh
```

### MCP-Integration testen

```bash
cd /workspace/Dev-Server-Workflow
python src/mcp/test-mcp-integration.py
```

### OpenHands konfigurieren

1. Kopiere die Datei `src/mcp/openhands-mcp-config.json` nach `~/.config/openhands/mcp-config.json`
2. Starte OpenHands neu

## Entwicklung

### Neuen MCP-Server hinzufügen

1. Implementiere einen neuen MCP-Server
2. Füge ihn zur OpenHands-Konfiguration hinzu
3. Aktualisiere die Dokumentation

### Neuen n8n-Workflow hinzufügen

1. Erstelle einen neuen Workflow in n8n
2. Füge den Tag "mcp" hinzu
3. Exportiere den Workflow und speichere ihn im Repository

## Fehlerbehebung

### MCP-Server startet nicht

- Überprüfe die Log-Dateien in `/tmp/mcp-logs/`
- Stelle sicher, dass alle Abhängigkeiten installiert sind

### OpenHands kann nicht mit MCP-Servern kommunizieren

- Überprüfe die OpenHands-Konfiguration
- Stelle sicher, dass die MCP-Server laufen
- Überprüfe die Firewall-Einstellungen

## Architektur

Die MCP-Integration folgt einer Client-Server-Architektur:

```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
|   OpenHands    |     |   Claude AI    |     |  Andere Tools  |
|                |     |                |     |                |
+-------+--------+     +-------+--------+     +-------+--------+
        |                      |                      |
        v                      v                      v
+-------+------------------------+------------------------+-------+
|                                                                 |
|                       MCP-Client-Bibliothek                     |
|                                                                 |
+-----------------+------------------+------------------+---------+
                  |                  |                  |
                  v                  v                  v
        +---------+------+  +--------+-------+  +-------+---------+
        |                |  |                |  |                 |
        | n8n MCP-Server |  | Filesystem MCP |  | GitHub MCP etc. |
        |                |  |                |  |                 |
        +--------+-------+  +--------+-------+  +-----------------+
                 |                   |
                 v                   v
        +--------+-------+  +--------+-------+
        |                |  |                |
        |  n8n-Workflows |  |  Dateisystem   |
        |                |  |                |
        +----------------+  +----------------+
```

Diese Architektur ermöglicht eine flexible und erweiterbare Integration verschiedener Dienste über das MCP-Protokoll.
