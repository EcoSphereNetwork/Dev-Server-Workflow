# Dev-Server CLI

Eine umfassende Kommandozeilen-Schnittstelle (CLI) zur Verwaltung des Dev-Server-Workflows.

## Funktionen

- **Komponentenverwaltung**: Starten, Stoppen, Neustarten und Überwachen von Komponenten
- **Dienste-Integration**: Integration mit n8n, AppFlowy, OpenProject, GitLab und Affine
- **KI-Assistent**: KI-gestützter Assistent für die Automatisierung von Entwicklungsprozessen
- **Paketmanagement**: Installation, Deinstallation, Aktualisierung und Überprüfung von Paketen
- **Konfigurationsmanagement**: Verwaltung von Konfigurationsdateien in verschiedenen Formaten
- **Monitoring**: Überwachung von Diensten, Ressourcen und Containern
- **Backup und Wiederherstellung**: Sicherung und Wiederherstellung von Komponenten

## Installation

```bash
sudo ./install_improved.sh
```

## Verwendung

```bash
dev-server [Befehl] [Optionen]
```

### Verfügbare Befehle

- `help`: Zeigt die Hilfe an
- `status`: Zeigt den Status aller Komponenten an
- `start [Komponente]`: Startet eine Komponente
- `stop [Komponente]`: Stoppt eine Komponente
- `restart [Komponente]`: Startet eine Komponente neu
- `logs [Komponente]`: Zeigt die Logs einer Komponente an
- `config [Option] [Wert]`: Konfiguriert eine Option
- `web-ui [Aktion]`: Verwaltet die Web-UI
- `list [Ressourcentyp]`: Listet verfügbare Ressourcen auf
- `install [Komponente]`: Installiert eine Komponente
- `switch-llm [LLM]`: Wechselt zwischen LLMs (llamafile, claude)
- `update [Komponente]`: Aktualisiert eine Komponente
- `backup [Komponente]`: Erstellt ein Backup einer Komponente
- `restore [Backup]`: Stellt ein Backup wieder her
- `package [Aktion] [Paket] [Manager] [Optionen]`: Paketmanagement
- `configure [Aktion] [Datei] [Schlüssel] [Wert] [Extra]`: Konfigurationsmanagement
- `monitor [Aktion] [Argumente...]`: Monitoring-Funktionen
- `ai [Prompt]`: Führt einen KI-Befehl aus
- `menu`: Öffnet das interaktive Menü

### Komponenten

- `all`: Alle Komponenten
- `mcp`: MCP-Server (Docker Container)
- `n8n-mcp`: n8n MCP-Server
- `docker-mcp`: Docker MCP-Server
- `monitoring`: Monitoring Stack (Prometheus, Grafana, Alertmanager)
- `n8n`: n8n-Workflow-Engine
- `ollama`: Ollama LLM-Server
- `openhands`: OpenHands KI-Agent
- `appflowy`: AppFlowy Notizen-App
- `llamafile`: Llamafile LLM
- `web-ui`: Web-UI für die Verwaltung aller Komponenten

## Beispiele

```bash
# Status aller Komponenten anzeigen
dev-server status

# MCP-Server starten
dev-server start mcp

# n8n-Logs anzeigen
dev-server logs n8n

# KI-Assistent verwenden
dev-server ai "Wie starte ich den MCP-Server?"

# AppFlowy installieren
dev-server install appflowy

# Interaktives Menü öffnen
dev-server menu
```

## Konfiguration

Die Konfigurationsdatei befindet sich unter `cli/config/dev-server.conf`. Sie können die Konfiguration mit dem Befehl `dev-server config` ändern.

## Verzeichnisstruktur

- `cli/`: CLI-Skripte und -Funktionen
- `cli/config/`: Konfigurationsdateien
- `cli/models/`: LLM-Modelle
- `logs/`: Logdateien
- `data/`: Datenverzeichnisse für Komponenten
- `backups/`: Backup-Verzeichnisse

## Abhängigkeiten

- Bash 4.0+
- Docker
- Docker Compose
- Python 3.6+
- Node.js 14+ (für Web-UI)

## Lizenz

MIT
