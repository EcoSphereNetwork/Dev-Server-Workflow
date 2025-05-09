# Benutzerhandbuch

Willkommen zum Benutzerhandbuch für das Dev-Server-Workflow-Projekt. Diese Dokumentation führt Sie durch die Installation, Konfiguration und Verwendung des Systems.

## Übersicht

Das Dev-Server-Workflow-Projekt ist eine umfassende Lösung zur Integration von n8n-Workflows, MCP-Servern (Model Context Protocol) und OpenHands für die KI-gestützte Automatisierung von Entwicklungsprozessen.

Mit diesem System können Sie:

- **Workflows automatisieren**: Erstellen und ausführen Sie Workflows mit n8n
- **KI-Agenten einsetzen**: Nutzen Sie OpenHands für KI-gestützte Automatisierung
- **MCP-Server verwalten**: Verwalten Sie MCP-Server für verschiedene Dienste
- **Entwicklungsprozesse optimieren**: Automatisieren Sie wiederkehrende Aufgaben

## Schnellstart

### Installation

1. Klonen Sie das Repository:

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

2. Führen Sie das Installationsskript aus:

```bash
./install.sh
```

3. Starten Sie die Dienste:

```bash
./start-mcp-servers.sh
```

### Erste Schritte

1. Öffnen Sie die Web-UI:

```bash
./dev-server-cli.sh web-ui open
```

2. Führen Sie einen Workflow aus:

```bash
./dev-server-cli.sh workflow run github-to-openproject
```

3. Verwenden Sie den KI-Assistenten:

```bash
./dev-server-cli.sh ai "Wie kann ich einen neuen Workflow erstellen?"
```

## Komponenten

Das System besteht aus mehreren Hauptkomponenten:

### MCP-Server

MCP-Server (Model Context Protocol) ermöglichen es KI-Agenten, mit verschiedenen Diensten zu interagieren. Das System umfasst folgende MCP-Server:

- **n8n MCP-Server**: Stellt n8n-Workflows als MCP-Tools bereit
- **OpenHands MCP-Server**: Ermöglicht die parallele Ausführung von OpenHands-Aufgaben
- **Docker MCP-Server**: Verwaltet Docker-Container über MCP
- **Generator MCP-Server**: Generiert dynamische MCP-Server

### n8n

n8n ist eine Workflow-Automatisierungsplattform, die es Ihnen ermöglicht, Workflows zu erstellen und auszuführen. Das System umfasst vordefinierte Workflows für:

- **GitHub-Integration**: Automatisierung von GitHub-Aufgaben
- **OpenProject-Integration**: Automatisierung von OpenProject-Aufgaben
- **Dokumentenverwaltung**: Automatisierung von Dokumentenverwaltungsaufgaben
- **MCP-Integration**: Automatisierung von MCP-bezogenen Aufgaben

### OpenHands

OpenHands ist eine Plattform für KI-gestützte Automatisierung. Das System integriert OpenHands für:

- **KI-gestützte Problemlösung**: Automatisierung von Problemlösungsaufgaben
- **Parallele Aufgabenausführung**: Ausführung mehrerer Aufgaben gleichzeitig
- **MCP-Integration**: Verwendung von MCP-Tools in OpenHands

### CLI-Tools

Das System bietet eine umfassende Befehlszeilenschnittstelle für die Verwaltung aller Komponenten:

- **Hauptschnittstelle**: `dev-server-cli.sh`
- **Interaktive Benutzeroberfläche**: `cli/interactive_ui.sh`
- **KI-Assistent**: `cli/ai_assistant_improved.sh`

## Verwendung

### MCP-Server verwalten

```bash
# Status aller MCP-Server anzeigen
./dev-server-cli.sh status

# Einen bestimmten MCP-Server starten
./dev-server-cli.sh start n8n-mcp

# Einen bestimmten MCP-Server stoppen
./dev-server-cli.sh stop docker-mcp

# Logs eines MCP-Servers anzeigen
./dev-server-cli.sh logs openhands-mcp
```

### n8n-Workflows verwalten

```bash
# Alle Workflows anzeigen
./dev-server-cli.sh workflow list

# Einen Workflow ausführen
./dev-server-cli.sh workflow run github-to-openproject

# Einen Workflow aktivieren
./dev-server-cli.sh workflow activate document-sync

# Einen Workflow deaktivieren
./dev-server-cli.sh workflow deactivate github-to-openproject
```

### OpenHands verwenden

```bash
# OpenHands starten
./dev-server-cli.sh start openhands

# Eine Aufgabe mit OpenHands ausführen
./dev-server-cli.sh openhands execute "Erstelle ein neues GitHub-Repository"

# OpenHands-Konfiguration anzeigen
./dev-server-cli.sh openhands config
```

### KI-Assistent verwenden

```bash
# Eine Frage stellen
./dev-server-cli.sh ai "Wie kann ich einen neuen Workflow erstellen?"

# Einen Befehl ausführen
./dev-server-cli.sh ai "Starte alle MCP-Server"
```

## Konfiguration

### Umgebungsvariablen

Die wichtigsten Konfigurationsoptionen können über Umgebungsvariablen in der `.env`-Datei gesetzt werden:

```bash
# n8n-Konfiguration
N8N_URL=http://localhost:5678
N8N_API_KEY=your-api-key

# OpenHands-Konfiguration
OPENHANDS_PORT=3000
OPENHANDS_API_KEY=your-api-key

# MCP-Server-Konfiguration
MCP_HTTP_PORT=3333
MCP_AUTH_TOKEN=your-auth-token

# LLM-Konfiguration
LLM_API_KEY=your-api-key
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
```

### Konfigurationsdateien

Detaillierte Konfigurationen können in den folgenden Dateien vorgenommen werden:

- **n8n**: `config/n8n-config.json`
- **OpenHands**: `config/openhands-config.json`
- **MCP-Server**: `config/mcp-config.json`
- **CLI-Tools**: `cli/config/dev-server.conf`

## Fehlerbehebung

### Häufige Probleme

#### MCP-Server starten nicht

```bash
# Überprüfen Sie den Status der Docker-Container
docker ps -a

# Überprüfen Sie die Logs
./dev-server-cli.sh logs mcp

# Starten Sie die Server neu
./stop-mcp-servers.sh
./start-mcp-servers.sh
```

#### n8n-Workflows funktionieren nicht

```bash
# Überprüfen Sie den Status von n8n
./dev-server-cli.sh status n8n

# Überprüfen Sie die Logs
./dev-server-cli.sh logs n8n

# Überprüfen Sie die Workflow-Konfiguration
./dev-server-cli.sh workflow check github-to-openproject
```

#### OpenHands-Integration funktioniert nicht

```bash
# Überprüfen Sie den Status von OpenHands
./dev-server-cli.sh status openhands

# Überprüfen Sie die Logs
./dev-server-cli.sh logs openhands

# Überprüfen Sie die OpenHands-Konfiguration
./dev-server-cli.sh openhands config
```

### Diagnose-Tools

```bash
# Systemdiagnose ausführen
./dev-server-cli.sh diagnose

# Netzwerkdiagnose ausführen
./dev-server-cli.sh diagnose network

# Komponentendiagnose ausführen
./dev-server-cli.sh diagnose component mcp
```

## Weitere Ressourcen

- [FAQ](faq.md)
- [Glossar](glossary.md)
- [Tutorials](tutorials/index.md)
- [Referenz](reference/index.md)