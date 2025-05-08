# Dev-Server CLI

Eine umfassende Befehlszeilenschnittstelle (CLI) zur Verwaltung des Dev-Server-Workflows, einschließlich MCP-Server, n8n-Workflows, Docker-Container und KI-Integration.

## Übersicht

Die Dev-Server CLI bietet eine einheitliche Schnittstelle zur Verwaltung aller Komponenten des Dev-Server-Workflows. Sie ermöglicht das Starten, Stoppen, Konfigurieren und Überwachen der verschiedenen Dienste sowie die Integration mit KI-Modellen für die Unterstützung bei der Administration.

## Funktionen

- **Komponentenverwaltung**: Starten, Stoppen und Neustarten von MCP-Servern, n8n, Ollama, OpenHands und mehr
- **Logverwaltung**: Anzeigen von Logs für alle Komponenten
- **Ressourcenlisten**: Auflisten von verfügbaren MCP-Servern, Workflows, Modellen und Containern
- **Konfiguration**: Anpassen von Einstellungen für alle Komponenten
- **KI-Integration**: Verwendung von ShellGPT mit Llamafile oder Claude für KI-gestützte Administration
- **Interaktives Menü**: Benutzerfreundliche Menüoberfläche für alle Funktionen

## Installation

```bash
# Klonen des Repositories (falls noch nicht geschehen)
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow

# Installation der CLI
sudo ./cli/install.sh
```

Das Installationsskript erstellt einen symbolischen Link in `/usr/local/bin`, sodass die CLI systemweit verfügbar ist.

## Verwendung

### Grundlegende Befehle

```bash
# Hilfe anzeigen
dev-server help

# Status aller Komponenten anzeigen
dev-server status

# Interaktives Menü öffnen
dev-server menu

# Komponente starten
dev-server start mcp

# Komponente stoppen
dev-server stop n8n

# Logs anzeigen
dev-server logs ollama
```

### KI-Integration

Die CLI unterstützt zwei LLM-Backends für die KI-Integration:

1. **Llamafile** (lokal): Ein lokales LLM, das keine Internetverbindung benötigt
2. **Claude** (Anthropic API): Ein leistungsstarkes Cloud-LLM mit API-Zugriff

#### Konfiguration der KI-Integration

```bash
# Llamafile installieren
dev-server install llamafile

# ShellGPT installieren
dev-server install shellgpt

# Anthropic API-Schlüssel konfigurieren
dev-server config anthropic-key YOUR_API_KEY

# Claude-Modell ändern
dev-server config claude-model claude-3-opus-20240229

# Zwischen LLMs wechseln
dev-server switch-llm llamafile
dev-server switch-llm claude
```

#### Verwendung der KI-Integration

```bash
# KI-Befehl ausführen
dev-server ai "Wie starte ich den MCP-Server?"

# Interaktiven KI-Modus starten
dev-server menu
# Dann Option 6 (KI-Assistent) wählen
```

## Komponenten

Die CLI kann folgende Komponenten verwalten:

- **MCP-Server**: Model Context Protocol Server für KI-Agenten
- **n8n**: Workflow-Automatisierungsplattform
- **Ollama**: Lokaler LLM-Server
- **OpenHands**: KI-Agent für Entwicklungsaufgaben
- **Llamafile**: Lokales LLM für die KI-Integration

## Konfiguration

Die Konfiguration der CLI wird in `~/.config/dev-server/dev-server.conf` gespeichert und kann über das Menü oder direkt mit dem `config`-Befehl angepasst werden:

```bash
# Konfiguration anzeigen
dev-server config show

# Llamafile-Pfad ändern
dev-server config llamafile-path /pfad/zu/llamafile

# Llamafile-Port ändern
dev-server config llamafile-port 8080

# Verbose-Modus umschalten
dev-server config verbose
```

## Fehlerbehebung

Bei Problemen mit der CLI können folgende Schritte helfen:

1. **Logs anzeigen**: `dev-server logs cli`
2. **Status prüfen**: `dev-server status`
3. **KI-Hilfe nutzen**: `dev-server ai "Ich habe folgendes Problem: ..."`

## Entwicklung

Die CLI ist in Bash geschrieben und kann leicht erweitert werden. Die Hauptdatei ist `cli/dev-server.sh`, die alle Funktionen und Befehle enthält.

Um neue Funktionen hinzuzufügen:

1. Fügen Sie eine neue Funktion in `dev-server.sh` hinzu
2. Aktualisieren Sie die `main`-Funktion, um den neuen Befehl zu verarbeiten
3. Aktualisieren Sie die `show_help`-Funktion, um den neuen Befehl zu dokumentieren

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen finden Sie in der [LICENSE](../LICENSE)-Datei.