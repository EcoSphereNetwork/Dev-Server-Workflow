# MCP Server Ecosystem

Diese Implementierung stellt ein vollständiges MCP-Server-Ökosystem bereit, das verschiedene MCP-Server und n8n für Workflow-Automatisierung umfasst. Die MCP-Server können auch mit OpenHands integriert werden, um die Fähigkeiten des KI-Agenten zu erweitern.

## Enthaltene MCP-Server

1. **Filesystem MCP** (Port 3001) - Dateisystemoperationen
2. **Desktop Commander MCP** (Port 3002) - Ausführung von Befehlen
3. **Sequential Thinking MCP** (Port 3003) - Schrittweises Denken
4. **GitHub Chat MCP** (Port 3004) - GitHub-Konversationen
5. **GitHub MCP** (Port 3005) - GitHub-API-Interaktionen
6. **Puppeteer MCP** (Port 3006) - Browserautomatisierung
7. **Basic Memory MCP** (Port 3007) - Einfacher Speicher
8. **Wikipedia MCP** (Port 3008) - Wikipedia-Zugriff

Zusätzlich:
- **MCP Inspector** (Port 8080) - UI zur Überwachung aller MCP-Server
- **n8n** (Port 5678) - Workflow-Automatisierung
- **OpenHands Integration** - Integration mit dem OpenHands KI-Agenten (siehe [OPENHANDS_INTEGRATION.md](OPENHANDS_INTEGRATION.md))

## Voraussetzungen

- Docker und Docker Compose
- GitHub-Token für GitHub-bezogene MCP-Server
- Mindestens 4 GB RAM und 2 CPU-Kerne

## Installation und Start

1. Kopieren Sie die `.env.example` zu `.env` und passen Sie die Werte an:
   ```bash
   cp .env.example .env
   ```

2. Bearbeiten Sie die `.env`-Datei und setzen Sie mindestens:
   - `GITHUB_TOKEN` - Ihr GitHub-Token
   - `WORKSPACE_PATH` - Pfad zu Ihrem Workspace

3. Starten Sie das MCP-Ökosystem:
   ```bash
   ./start-mcp-ecosystem.sh
   ```

## Überwachung

Verwenden Sie das Python-Skript zur Überwachung der MCP-Server:

```bash
# Einmalige Statusprüfung
./monitor-mcp-servers.py

# Kontinuierliche Überwachung (alle 30 Sekunden)
./monitor-mcp-servers.py -c

# Kontinuierliche Überwachung mit Tools-Anzeige
./monitor-mcp-servers.py -c -t

# Anpassen des Aktualisierungsintervalls (z.B. 10 Sekunden)
./monitor-mcp-servers.py -c -i 10
```

Alternativ können Sie die MCP Inspector UI unter http://localhost:8080 verwenden.

## n8n-Workflows

Die folgenden n8n-Workflows werden automatisch importiert:

1. **Multi-MCP-Server-Integration** - Integriert Ereignisse von allen MCP-Servern
2. **MCP-Server-Monitor** - Überwacht den Status aller MCP-Server
3. **MCP-GitHub-Integration** - Integriert MCP-Server mit GitHub
4. **MCP-LLM-Analyzer** - Analysiert MCP-Server-Ereignisse mit LLMs

Zugriff auf n8n: http://localhost:5678

## Stoppen des Ökosystems

```bash
./stop-mcp-ecosystem.sh
```

## Fehlerbehebung

### MCP-Server sind nicht erreichbar

Überprüfen Sie den Status der Docker-Container:
```bash
docker ps | grep mcp
```

Prüfen Sie die Logs eines bestimmten MCP-Servers:
```bash
docker logs mcp-filesystem
```

### n8n-Workflows funktionieren nicht

Überprüfen Sie die n8n-Logs:
```bash
docker logs n8n
```

Stellen Sie sicher, dass die Umgebungsvariablen in der `.env`-Datei korrekt gesetzt sind.

## Architektur

```
┌─────────────────┐     ┌─────────────────┐
│  MCP Inspector  │     │       n8n       │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       │
┌────────┴───────────────────────┴────────┐
│                Redis                     │
└────────┬───────────────────────┬────────┘
         │                       │
┌────────┴────────┐     ┌────────┴────────┐
│  MCP Server 1   │     │  MCP Server N   │
└─────────────────┘     └─────────────────┘
```

## Lizenz

Siehe LICENSE-Datei im Hauptverzeichnis des Projekts.