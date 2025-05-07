Analysiere /workspace/Dev-Server-Workflow/docs/docs/Dev-Server-Workflow
und 
/workspace/Dev-Server-Workflow/docs/docs/Dev-Server-Workflow
und
/workspace/Dev-Server-Workflow/tools

Verstehe den Kontext.

Erstelle einen detaillierten verbessereungsplan aller n8n-workflows und der mcp server. 

Implementiere alle docker container (MCP Server) in das MCP-Server-Ökosystem:

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/brave.md
https://hub.docker.com/r/mcp/brave-search

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/filesystem.md
https://hub.docker.com/r/mcp/filesystem

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/grafana.md
https://hub.docker.com/r/mcp/grafana

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/hyperbrowser.md

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/wolfram-alpha.md

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/oxylabs.md

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/e2b.md

https://github.com/wonderwhy-er/DesktopCommanderMCP https://github.com/wonderwhy-er/DesktopCommanderMCP/blob/main/Dockerfile

https://github.com/modelcontextprotocol/servers https://github.com/modelcontextprotocol/servers/blob/2025.4.6/src/sequentialthinking/Dockerfile

https://hub.docker.com/r/mcp/memory

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/basic-memory.md

https://github.com/docker/labs-ai-tools-for-devs

https://raw.githubusercontent.com/docker/labs-ai-tools-for-devs/refs/heads/main/prompts/chrome.md

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/github-chat.md
https://hub.docker.com/r/mcp/github-chat

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/gitlab.md
https://hub.docker.com/r/mcp/gitlab

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/github-official.md
https://hub.docker.com/r/mcp/github-mcp-server

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/github.md
https://hub.docker.com/r/mcp/github

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/duckduckgo.md
https://hub.docker.com/r/mcp/duckduckgo

https://github.com/docker/labs-ai-tools-for-devs/blob/main/prompts/mcp/readmes/wikipedia-mcp.md
https://hub.docker.com/r/mcp/wikipedia-mcp# Verbessertes MCP-Server-Ökosystem mit OpenHands-Integration

Dieses Projekt implementiert ein umfassendes MCP-Server-Ökosystem mit Integration von OpenHands als zentralem Verwaltungstool. Es umfasst verschiedene MCP-Server-Container, die Integration des Ollama-MCP-Bridge und die Konfiguration von OpenHands für die Verwaltung des gesamten Systems.

## Verbesserungen gegenüber der vorherigen Version

### 1. Sicherheit und Berechtigungen

- **Docker Socket Proxy**: Statt direktem Zugriff auf die Docker-Socket verwendet OpenHands nun einen Docker-Socket-Proxy, der nur bestimmte API-Endpunkte freigibt.
- **Eingeschränkte Dateisystem-Berechtigungen**: Container haben nur Zugriff auf spezifische Verzeichnisse statt auf das gesamte Dateisystem.
- **Container-Härtung**: Sicherheitsoptionen wie `no-new-privileges` und `cap_drop` wurden hinzugefügt, um die Container-Sicherheit zu erhöhen.
- **Gesundheitschecks**: Alle Container verfügen über Gesundheitschecks, um die Verfügbarkeit zu überwachen.

### 2. Desktop Commander Integration

- **Desktop Commander MCP-Server**: Integration des offiziellen Docker-Images `mcp/desktop-commander` mit eingeschränkten Berechtigungen.
- **Sichere Konfiguration**: Beschränkung der erlaubten Verzeichnisse und Befehle für den Desktop Commander.
- **OpenHands-Integration**: Konfiguration von OpenHands für die Nutzung des Desktop Commander.

### 3. Ollama-MCP-Bridge

- **Verbesserte Konfiguration**: Erweiterte Konfigurationsmöglichkeiten für verschiedene Modelle und Parameter.
- **Tool-Erkennung**: Aktivierung der automatischen Tool-Erkennung für bessere Nutzererfahrung.
- **Fehlerbehandlung**: Robustere Fehlerbehandlung und Wiederherstellungsmechanismen.

### 4. Nginx-Konfiguration

- **Verbesserte Sicherheit**: Implementierung von Best Practices für Nginx-Sicherheit.
- **Gesundheitschecks**: Endpunkte für Gesundheitschecks für alle Dienste.
- **Verbesserte Proxy-Einstellungen**: Optimierte Proxy-Einstellungen für bessere Leistung und Zuverlässigkeit.

### 5. OpenHands-Integration

- **Verbesserte Konfiguration**: Detailliertere Konfiguration für MCP-Server und Berechtigungen.
- **Sicherheitseinstellungen**: Zusätzliche Sicherheitseinstellungen für OpenHands.
- **Benutzeroberfläche**: Konfigurationsoptionen für die Benutzeroberfläche.

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

6. **Docker Socket Proxy**: Ein Proxy für die Docker-Socket, der nur bestimmte API-Endpunkte freigibt.

## Voraussetzungen

- Docker und Docker Compose
- Mindestens 8 GB RAM
- Mindestens 50 GB freier Festplattenspeicher
- Linux-Betriebssystem (empfohlen)

## Installation

1. Repository klonen:
   ```bash
   git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
   cd Dev-Server-Workflow/docker-mcp-ecosystem-improved
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
   - MCP Inspector UI: http://inspector.ecospherenet.work

## Verwendung

### OpenHands

OpenHands ist das zentrale Verwaltungstool für das MCP-Server-Ökosystem. Es bietet eine Benutzeroberfläche für die Interaktion mit allen MCP-Servern, dem lokalen Dateisystem und Docker-Containern.

### Desktop Commander

Der Desktop Commander MCP-Server ermöglicht die Interaktion mit dem Dateisystem und die Ausführung von Terminalbefehlen. Er bietet folgende Funktionen:

- Dateisystem-Operationen (Lesen, Schreiben, Suchen)
- Terminalbefehle ausführen
- Prozessverwaltung
- Textbearbeitung

Der Desktop Commander ist mit einer detaillierten Konfiguration ausgestattet, die in der Datei `desktop-commander/config.json` definiert ist. Diese Konfiguration umfasst:

- Erlaubte Verzeichnisse: Nur `/workspace` ist standardmäßig erlaubt
- Blockierte Befehle: Potenziell gefährliche Befehle wie `rm -rf /` sind blockiert
- Sicherheitseinstellungen: Einschränkungen für Netzwerkzugriff und Ausführung von Binärdateien

### MCP Inspector

Der MCP Inspector ist ein leistungsstarkes Entwicklungswerkzeug für das Testen und Debuggen von MCP-Servern. Er bietet folgende Funktionen:

- Visuelle Benutzeroberfläche für die Interaktion mit MCP-Servern
- Anzeige und Test von verfügbaren Tools, Ressourcen und Prompts
- Detaillierte Fehlerinformationen und Logs
- CLI-Modus für Automatisierung und Scripting

Der MCP Inspector ist unter http://inspector.ecospherenet.work erreichbar und kann für die Entwicklung und das Debugging von MCP-Servern verwendet werden.

Für die Verwendung des MCP Inspectors im CLI-Modus steht das Skript `scripts/mcp-inspector-cli.sh` zur Verfügung:

```bash
./scripts/mcp-inspector-cli.sh --server github --method tools/list
```

### Ollama-MCP-Bridge

Die Ollama-MCP-Bridge ermöglicht die Verwendung lokaler LLMs über das MCP-Protokoll. Sie unterstützt verschiedene Modelle wie Qwen2.5, Llama3 und Mistral.

### Verwaltungsskripte

Das MCP-Server-Ökosystem enthält verschiedene Skripte zur Verwaltung und Automatisierung:

- `scripts/setup.sh`: Automatisiert die Einrichtung des MCP-Server-Ökosystems
- `scripts/manage-mcp-ecosystem.sh`: Ermöglicht die Verwaltung des gesamten Ökosystems
- `scripts/mcp-server-manager.sh`: Ermöglicht die Verwaltung der MCP-Server
- `scripts/mcp-inspector-cli.sh`: Ermöglicht die Verwendung des MCP Inspectors im CLI-Modus

Beispiele für die Verwendung der Skripte:

```bash
# Einrichtung des Ökosystems
./scripts/setup.sh

# Starten des gesamten Ökosystems
./scripts/manage-mcp-ecosystem.sh start

# Anzeigen der Logs eines bestimmten Dienstes
./scripts/manage-mcp-ecosystem.sh logs --service github-mcp

# Auflisten der verfügbaren Tools eines MCP-Servers
./scripts/mcp-server-manager.sh list-tools --server desktop-commander-mcp

# Aufrufen eines Tools eines MCP-Servers
./scripts/mcp-server-manager.sh call-tool --server desktop-commander-mcp --tool read_file --args '{"path":"/workspace/README.md"}'
```

### n8n-Workflows

n8n ist mit benutzerdefinierten MCP-Nodes konfiguriert, die die Interaktion mit den MCP-Servern ermöglichen. Es können Workflows erstellt werden, die verschiedene MCP-Server und andere Dienste integrieren.

## Konfiguration

### OpenHands

Die OpenHands-Konfiguration befindet sich in der Datei `openhands/openhands-config.json`. Hier können die MCP-Server, der Zugriff auf das Dateisystem und Docker konfiguriert werden.

### Ollama-MCP-Bridge

Die Ollama-MCP-Bridge-Konfiguration befindet sich in der Datei `ollama-mcp-bridge/bridge_config.json`. Hier können die LLM-Einstellungen und die MCP-Server-Verbindungen konfiguriert werden.

### Nginx

Die Nginx-Konfiguration befindet sich im Verzeichnis `nginx/conf.d/`. Hier können die Reverse-Proxy-Einstellungen für die verschiedenen Dienste angepasst werden.

## Sicherheitshinweise

- **API-Schlüssel**: Alle API-Schlüssel sollten sicher in der `.env`-Datei gespeichert werden.
- **Docker-Socket-Proxy**: Der Docker-Socket-Proxy beschränkt den Zugriff auf die Docker-API auf bestimmte Endpunkte.
- **Dateisystem-Berechtigungen**: Container haben nur Zugriff auf spezifische Verzeichnisse.
- **Container-Härtung**: Sicherheitsoptionen wie `no-new-privileges` und `cap_drop` erhöhen die Container-Sicherheit.

## Fehlerbehebung

### Container startet nicht

Überprüfe die Logs:
```bash
docker-compose logs [service-name]
```

### Gesundheitschecks schlagen fehl

Überprüfe den Status der Gesundheitschecks:
```bash
docker-compose ps
```

### OpenHands kann nicht auf MCP-Server zugreifen

Überprüfe die OpenHands-Konfiguration:
```bash
docker-compose exec openhands cat /app/data/config.json
```

## Lizenz

MIT