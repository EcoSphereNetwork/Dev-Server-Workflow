# MCP-Server-Implementierung

Dieses Dokument beschreibt die Implementierung der Model Context Protocol (MCP) Server im Dev-Server-Workflow-Projekt.

## Übersicht

Die MCP-Server-Implementierung umfasst die folgenden Komponenten:

1. **Docker-Container**: Alle MCP-Server werden als Docker-Container bereitgestellt.
2. **n8n-Integration**: Die MCP-Server werden mit n8n integriert, um Workflows als MCP-Tools bereitzustellen.
3. **OpenHands-Integration**: Die MCP-Server werden mit OpenHands integriert, um KI-Agenten die Verwendung der Tools zu ermöglichen.

## Implementierte MCP-Server

Die folgenden MCP-Server wurden implementiert:

1. **Filesystem MCP Server** (`mcp/filesystem`): Ermöglicht Dateisystem-Operationen wie Lesen, Schreiben und Suchen von Dateien.
2. **Desktop Commander MCP Server** (`mcp/desktop-commander`): Ermöglicht die Ausführung von Terminal-Befehlen und Desktop-Operationen.
3. **Sequential Thinking MCP Server** (`mcp/sequentialthinking`): Bietet strukturierte Problemlösungsfähigkeiten.
4. **GitHub Chat MCP Server** (`mcp/github-chat`): Ermöglicht die Interaktion mit GitHub-Diskussionen und -Kommentaren.
5. **GitHub MCP Server** (`mcp/github`): Bietet GitHub-Repository-Management-Funktionen.
6. **Puppeteer MCP Server** (`mcp/puppeteer`): Ermöglicht Web-Browsing und Interaktion mit Webseiten.
7. **Basic Memory MCP Server** (`mcp/basic-memory`): Bietet einfache Schlüssel-Wert-Speicherung für KI-Agenten.
8. **Wikipedia MCP Server** (`mcp/wikipedia-mcp`): Ermöglicht die Suche und das Abrufen von Informationen aus Wikipedia.

## Installation

### Automatische Installation

Die einfachste Methode zur Installation der MCP-Server ist die Verwendung des Installationsskripts:

```bash
cd /workspace/Dev-Server-Workflow
./install-mcp-servers.sh
```

### Manuelle Installation

Wenn Sie die MCP-Server manuell installieren möchten, folgen Sie diesen Schritten:

1. Wechseln Sie in das MCP-Servers-Verzeichnis:

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-servers
```

2. Erstellen Sie eine `.env`-Datei basierend auf der `.env.example`-Vorlage:

```bash
cp .env.example .env
# Bearbeiten Sie die .env-Datei mit Ihren Konfigurationen
```

3. Pullen Sie die Docker-Images:

```bash
./pull-images.sh
```

4. Starten Sie die Docker-Container:

```bash
docker compose up -d
```

## Verwendung

### Starten der MCP-Server

```bash
cd /workspace/Dev-Server-Workflow
./scripts/start-mcp-servers.sh
```

### Stoppen der MCP-Server

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-servers
./stop-mcp-servers.sh
```

### Testen der MCP-Server

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-servers
./test-mcp-servers.py
```

### Überwachen der MCP-Server

```bash
cd /workspace/Dev-Server-Workflow
./scripts/monitor-mcp-servers.py
```

### Integration mit n8n

```bash
cd /workspace/Dev-Server-Workflow
./scripts/integrate-mcp-with-n8n.py --n8n-api-key YOUR_N8N_API_KEY
```

### Integration mit OpenHands

```bash
cd /workspace/Dev-Server-Workflow
./scripts/integrate-mcp-with-openhands.py --openhands-config-dir /path/to/openhands/config --github-token YOUR_GITHUB_TOKEN
```

## Konfiguration

Die MCP-Server können über die `.env`-Datei im Verzeichnis `docker-mcp-servers` konfiguriert werden. Die wichtigsten Konfigurationsoptionen sind:

- `REDIS_PASSWORD`: Passwort für den Redis-Server
- `GITHUB_TOKEN`: GitHub-Personal-Access-Token
- `WORKSPACE_PATH`: Pfad zum Workspace-Verzeichnis
- `DISPLAY`: Display für Desktop Commander

## Dokumentation

Weitere Informationen zur MCP-Server-Implementierung finden Sie in der folgenden Dokumentation:

- [MCP-Server-Implementierungsanleitung](docs/docs/Dev-Server-Workflow/MCP-Server-Implementation-Guide.md)
- [MCP-OpenHands-Integration](docs/docs/Dev-Server-Workflow/MCP-OpenHands.md)
- [MCP-Integration](docs/docs/Dev-Server-Workflow/MCP-Integration.md)

## Fehlerbehebung

Wenn Sie Probleme mit den MCP-Servern haben, überprüfen Sie die folgenden Punkte:

1. Überprüfen Sie die Docker-Container-Logs:
   ```bash
   docker compose logs <container-name>
   ```

2. Überprüfen Sie, ob die MCP-Server laufen:
   ```bash
   docker compose ps
   ```

3. Überprüfen Sie den Gesundheitszustand der MCP-Server:
   ```bash
   docker compose exec <container-name> curl -f http://localhost:<port>/health
   ```

4. Verwenden Sie das Monitoring-Skript, um die MCP-Server zu überwachen:
   ```bash
   cd /workspace/Dev-Server-Workflow
   ./scripts/monitor-mcp-servers.py
   ```

## Sicherheitshinweise

- Die MCP-Server sollten nur in vertrauenswürdigen Umgebungen ausgeführt werden
- Verwenden Sie ein dediziertes GitHub-Token mit eingeschränkten Berechtigungen
- Konfigurieren Sie die erlaubten Verzeichnisse für Filesystem und Desktop Commander MCP Server
- Blockieren Sie gefährliche Befehle im Desktop Commander MCP Server