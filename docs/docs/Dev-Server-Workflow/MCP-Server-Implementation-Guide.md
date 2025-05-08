# MCP-Server-Implementierungsanleitung

Diese Anleitung beschreibt die Implementierung der Model Context Protocol (MCP) Server als Docker-Container im Dev-Server-Workflow-Projekt.

## Übersicht

Das Model Context Protocol (MCP) ist ein standardisiertes Protokoll, das es KI-Agenten ermöglicht, mit verschiedenen Tools und Diensten zu interagieren. Jeder MCP-Server implementiert das Protokoll und stellt spezifische Funktionalitäten bereit.

In dieser Implementierung werden die folgenden MCP-Server als Docker-Container bereitgestellt:

1. **Filesystem MCP Server** (`mcp/filesystem`): Ermöglicht Dateisystem-Operationen wie Lesen, Schreiben und Suchen von Dateien.
2. **Desktop Commander MCP Server** (`mcp/desktop-commander`): Ermöglicht die Ausführung von Terminal-Befehlen und Desktop-Operationen.
3. **Sequential Thinking MCP Server** (`mcp/sequentialthinking`): Bietet strukturierte Problemlösungsfähigkeiten.
4. **GitHub Chat MCP Server** (`mcp/github-chat`): Ermöglicht die Interaktion mit GitHub-Diskussionen und -Kommentaren.
5. **GitHub MCP Server** (`mcp/github`): Bietet GitHub-Repository-Management-Funktionen.
6. **Puppeteer MCP Server** (`mcp/puppeteer`): Ermöglicht Web-Browsing und Interaktion mit Webseiten.
7. **Basic Memory MCP Server** (`mcp/basic-memory`): Bietet einfache Schlüssel-Wert-Speicherung für KI-Agenten.
8. **Wikipedia MCP Server** (`mcp/wikipedia-mcp`): Ermöglicht die Suche und das Abrufen von Informationen aus Wikipedia.

## Voraussetzungen

- Docker und Docker Compose
- Zugriff auf die MCP-Server-Docker-Images
- GitHub-Token (für GitHub-bezogene MCP-Server)
- Mindestens 4 GB RAM und 20 GB freier Festplattenspeicher

## Installation

### Automatische Installation

Die einfachste Methode zur Installation der MCP-Server ist die Verwendung des Installationsskripts:

```bash
cd /workspace/Dev-Server-Workflow
./install-mcp-servers.sh
```

Das Skript führt die folgenden Schritte aus:

1. Überprüft, ob Docker und Docker Compose installiert sind, und installiert sie bei Bedarf
2. Startet den Docker-Daemon, falls er nicht läuft
3. Kopiert die Docker-Compose-Datei
4. Startet die MCP-Server
5. Integriert die MCP-Server mit OpenHands

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
docker-compose up -d
```

## Konfiguration

### Umgebungsvariablen

Die folgenden Umgebungsvariablen können in der `.env`-Datei konfiguriert werden:

- `REDIS_PASSWORD`: Passwort für den Redis-Server
- `GITHUB_TOKEN`: GitHub-Personal-Access-Token
- `WORKSPACE_PATH`: Pfad zum Workspace-Verzeichnis
- `DISPLAY`: Display für Desktop Commander

### Port-Konfiguration

Jeder MCP-Server ist so konfiguriert, dass er auf einem bestimmten Port läuft:

- Filesystem MCP: 3001
- Desktop Commander MCP: 3002
- Sequential Thinking MCP: 3003
- GitHub Chat MCP: 3004
- GitHub MCP: 3005
- Puppeteer MCP: 3006
- Basic Memory MCP: 3007
- Wikipedia MCP: 3008

## Integration mit n8n

Die MCP-Server können mit n8n-Workflows integriert werden, indem Sie das Integrationsskript verwenden:

```bash
cd /workspace/Dev-Server-Workflow
./scripts/integrate-mcp-with-n8n.py --n8n-api-key YOUR_N8N_API_KEY
```

Alternativ können Sie die Integration manuell durchführen:

1. Importieren Sie den Workflow aus `src/ESN_Initial-Szenario/n8n-workflows/enhanced-mcp-trigger.json` in n8n
2. Konfigurieren Sie die MCP-Server-URLs in den n8n-Umgebungsvariablen

## Integration mit OpenHands

Um die MCP-Server mit OpenHands zu integrieren, verwenden Sie das Integrationsskript:

```bash
cd /workspace/Dev-Server-Workflow
./scripts/integrate-mcp-with-openhands.py --openhands-config-dir /path/to/openhands/config --github-token YOUR_GITHUB_TOKEN
```

Alternativ können Sie die Integration manuell durchführen:

1. Kopieren Sie die Datei `docker-mcp-servers/openhands-mcp-config.json` in Ihr OpenHands-Konfigurationsverzeichnis
2. Starten Sie OpenHands neu, um die MCP-Integration zu aktivieren

## Verwendung der MCP-Server

### Direkte Verwendung

Sie können die MCP-Server direkt über ihre HTTP-Endpunkte verwenden. Jeder Server implementiert das JSON-RPC-basierte Model Context Protocol.

Beispiel für eine Anfrage an den Filesystem MCP Server:

```bash
curl -X POST http://localhost:3001/mcp -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.listTools",
  "params": {}
}'
```

### Verwendung mit OpenHands

Wenn Sie die MCP-Server mit OpenHands integriert haben, können Sie die Tools direkt in OpenHands verwenden. OpenHands wird die verfügbaren Tools automatisch erkennen und anzeigen.

### Verwendung mit n8n

Wenn Sie die MCP-Server mit n8n integriert haben, können Sie die MCP-Tools in Ihren n8n-Workflows verwenden. Der MCP-Trigger-Workflow wird die verfügbaren Tools automatisch erkennen und als n8n-Nodes bereitstellen.

## Fehlerbehebung

Wenn Sie Probleme mit den MCP-Servern haben:

1. Überprüfen Sie die Docker-Container-Logs:
   ```bash
   docker-compose logs <container-name>
   ```

2. Überprüfen Sie, ob die MCP-Server laufen:
   ```bash
   docker-compose ps
   ```

3. Überprüfen Sie den Gesundheitszustand der MCP-Server:
   ```bash
   docker-compose exec <container-name> curl -f http://localhost:<port>/health
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

## Referenzen

- [Model Context Protocol Dokumentation](https://github.com/modelcontextprotocol/protocol)
- [MCP-Server-Implementierungsanleitung](../docs/Dev-Server-Workflow/MCP-Server-Implementation.md)
- [MCP-OpenHands-Integration](../docs/Dev-Server-Workflow/MCP-OpenHands.md)