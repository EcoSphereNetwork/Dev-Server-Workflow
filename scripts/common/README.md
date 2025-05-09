# Gemeinsame MCP-Bibliothek

Diese Bibliothek enthält gemeinsame Funktionen und Konfigurationen für die MCP-Server-Skripte.

## Übersicht

Die `mcp_common.sh`-Bibliothek bietet folgende Funktionalitäten:

1. **Standardisierte Konfiguration**: Laden von Umgebungsvariablen aus der `.env`-Datei und Bereitstellen von Standardwerten
2. **Logging-Funktionen**: Einheitliche Funktionen für Logging und Fehlerbehandlung
3. **Abhängigkeitsprüfung**: Funktionen zur Überprüfung und Installation von Abhängigkeiten
4. **Server-Verwaltung**: Funktionen zum Starten und Stoppen von MCP-Servern
5. **Konfigurationserstellung**: Funktionen zum Erstellen von Konfigurationsdateien für OpenHands und Claude

## Verwendung

Um die Bibliothek in einem Skript zu verwenden, fügen Sie folgende Zeilen am Anfang des Skripts ein:

```bash
# Basisverzeichnis
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$SCRIPT_DIR/../common/mcp_common.sh"
```

## Verfügbare Funktionen

### Logging-Funktionen

```bash
log "Informationsnachricht"
warn "Warnungsnachricht"
error "Fehlermeldung"
info "Hervorgehobene Informationsnachricht"
```

### Abhängigkeitsprüfung

```bash
check_docker
check_docker_compose
start_docker_daemon
check_python_dependencies
```

### Server-Verwaltung

```bash
start_mcp_server "server-name" "command" "args"
stop_mcp_server "server-name"
stop_all_servers
start_docker_mcp_servers
start_n8n_mcp_server
start_openhands_mcp_server
```

### Konfigurationserstellung

```bash
create_openhands_config
create_claude_config
create_start_scripts
```

### Installation

```bash
install_mcp_servers
install_ollama_bridge
```

## Umgebungsvariablen

Die Bibliothek verwendet folgende Umgebungsvariablen, die in der `.env`-Datei definiert werden können:

| Variable | Beschreibung | Standardwert |
|----------|--------------|--------------|
| `N8N_URL` | URL der n8n-Instanz | `http://localhost:5678` |
| `N8N_API_KEY` | API-Schlüssel für n8n | - |
| `MCP_HTTP_PORT` | Port für den MCP-HTTP-Server | `3333` |
| `OPENHANDS_PORT` | Port für OpenHands | `3000` |
| `OLLAMA_PORT` | Port für Ollama | `8000` |
| `OLLAMA_MODEL` | Zu verwendendes Ollama-Modell | `qwen2.5-coder:7b-instruct` |
| `OLLAMA_BASE_URL` | URL der Ollama-API | `http://localhost:11434` |
| `OPENHANDS_STATE_DIR` | Verzeichnis für OpenHands-Zustandsdaten | `$HOME/.openhands-state` |
| `OPENHANDS_WORKSPACE_DIR` | Verzeichnis für OpenHands-Workspace | `$HOME/openhands-workspace` |
| `OPENHANDS_CONFIG_DIR` | Verzeichnis für OpenHands-Konfiguration | `$HOME/.config/openhands` |
| `OPENHANDS_MAX_WORKERS` | Maximale Anzahl von Worker-Threads für OpenHands | `5` |
| `LOG_DIR` | Verzeichnis für Log-Dateien | `/tmp/mcp-logs` |
| `BRAVE_API_KEY` | API-Schlüssel für Brave Search | - |
| `GITHUB_TOKEN` | GitHub-Token für API-Zugriff | - |

## Beispiel

```bash
#!/bin/bash

# Basisverzeichnis
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$SCRIPT_DIR/../common/mcp_common.sh"

# Erstelle Log-Verzeichnis
create_log_directories

# Starte MCP-Server
start_mcp_server "filesystem-mcp" "npx" "-y @modelcontextprotocol/server-filesystem --port 3457"
start_mcp_server "github-mcp" "npx" "-y @modelcontextprotocol/server-github --port 3458"

# Warte auf Benutzerunterbrechung
trap stop_all_servers EXIT

# Halte das Skript am Laufen
while true; do
    sleep 1
done
```