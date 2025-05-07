# MCP-Server-Ökosystem mit OpenHands-Integration

Dieses Projekt implementiert ein umfassendes MCP-Server-Ökosystem mit Integration von OpenHands als zentralem Verwaltungstool. Es umfasst verschiedene MCP-Server-Container, die Integration des Ollama-MCP-Bridge und die Konfiguration von OpenHands für die Verwaltung des gesamten Systems.

## Architektur

Das System besteht aus folgenden Komponenten:

1. **MCP-Server**: Eine Sammlung von Docker-Containern, die das Model Context Protocol (MCP) implementieren:
   - GitHub MCP Server
   - GitHub Chat MCP Server
   - GitLab MCP Server
   - Memory MCP Server
   - Basic Memory MCP Server
   - Time MCP Server
   - Wolfram Alpha MCP Server
   - Discord MCP Server
   - Fetch MCP Server
   - Inspector MCP Server
   - Sequential Thinking MCP Server
   - Puppeteer MCP Server
   - 3D Printer MCP Server
   - Desktop Commander MCP Server
   - PostgreSQL MCP Server
   - Elasticsearch MCP Server
   - SQLite MCP Server

2. **Ollama MCP Bridge**: Eine Brücke zwischen Ollama und dem MCP-Protokoll, die es ermöglicht, Ollama-Modelle über das MCP-Protokoll zu verwenden.

3. **OpenHands**: Ein zentrales Verwaltungstool, das Zugriff auf alle MCP-Server, das lokale Dateisystem und Docker-Container hat.

4. **n8n**: Eine Workflow-Automatisierungsplattform mit benutzerdefinierten MCP-Nodes.

5. **GitLab, OpenProject, AppFlowy**: Integrierte Dienste für Versionskontrolle, Projektmanagement und Dokumentation.

## Voraussetzungen

- Docker und Docker Compose
- Mindestens 8 GB RAM
- Mindestens 50 GB freier Festplattenspeicher
- Linux-Betriebssystem (empfohlen)

## Installation

1. Repository klonen:
   ```bash
   git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
   cd Dev-Server-Workflow/docker-mcp-ecosystem
   ```

2. Umgebungsvariablen konfigurieren:
   ```bash
   cp .env.example .env
   # Bearbeite die .env-Datei mit deinen API-Zugangsdaten
   ```

3. Docker-Container starten:
   ```bash
   docker-compose up -d
   ```

4. Auf die Dienste zugreifen:
   - OpenHands: http://openhands.ecospherenet.work
   - n8n: http://n8n.ecospherenet.work
   - GitLab: http://gitlab.ecospherenet.work
   - OpenProject: http://openproject.eocspherenet.work
   - AppFlowy: http://appflowy.ecospherenet.work

## Verwendung

### OpenHands

OpenHands ist das zentrale Verwaltungstool für das MCP-Server-Ökosystem. Es bietet eine Benutzeroberfläche für die Interaktion mit allen MCP-Servern, dem lokalen Dateisystem und Docker-Containern.

### MCP-Server

Jeder MCP-Server implementiert das Model Context Protocol und bietet spezifische Funktionen an. Die Server können über OpenHands oder direkt über ihre jeweiligen Endpunkte angesprochen werden.

### n8n-Workflows

n8n ist mit benutzerdefinierten MCP-Nodes konfiguriert, die die Interaktion mit den MCP-Servern ermöglichen. Es können Workflows erstellt werden, die verschiedene MCP-Server und andere Dienste integrieren.

## Konfiguration

### OpenHands

Die OpenHands-Konfiguration befindet sich in der Datei `openhands/openhands-config.json`. Hier können die MCP-Server, der Zugriff auf das Dateisystem und Docker konfiguriert werden.

### Nginx

Die Nginx-Konfiguration befindet sich im Verzeichnis `nginx/conf.d/`. Hier können die Reverse-Proxy-Einstellungen für die verschiedenen Dienste angepasst werden.

### MCP-Server

Die Konfiguration der MCP-Server erfolgt über Umgebungsvariablen in der `docker-compose.yml`-Datei.

## Entwicklung

### Hinzufügen eines neuen MCP-Servers

1. Füge einen neuen Service zur `docker-compose.yml` hinzu
2. Aktualisiere die OpenHands-Konfiguration in `openhands/openhands-config.json`
3. Aktualisiere die Nginx-Konfiguration in `nginx/conf.d/default.conf`
4. Starte die Container neu: `docker-compose up -d`

### Anpassen von n8n-Workflows

n8n-Workflows können über die n8n-Benutzeroberfläche erstellt und angepasst werden. Die benutzerdefinierten MCP-Nodes ermöglichen die Interaktion mit den MCP-Servern.

## Fehlerbehebung

### Container startet nicht

Überprüfe die Logs:
```bash
docker-compose logs [service-name]
```

### MCP-Server nicht erreichbar

Überprüfe die Netzwerkkonfiguration:
```bash
docker-compose exec nginx nginx -t
```

### OpenHands kann nicht auf MCP-Server zugreifen

Überprüfe die OpenHands-Konfiguration:
```bash
docker-compose exec openhands cat /app/data/config.json
```

## Lizenz

MIT