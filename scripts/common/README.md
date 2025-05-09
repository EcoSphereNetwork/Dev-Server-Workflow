# Gemeinsame Bibliotheken für Dev-Server-Workflow

Dieses Verzeichnis enthält gemeinsame Bibliotheken für das Dev-Server-Workflow-Projekt. Diese Bibliotheken bieten standardisierte Funktionen und Klassen, die in allen Skripten des Projekts verwendet werden können.

## Struktur

- `shell/`: Gemeinsame Shell-Bibliotheken
  - `common.sh`: Hauptbibliothek für Shell-Skripte
- `python/`: Gemeinsame Python-Bibliotheken
  - `common.py`: Hauptbibliothek für Python-Skripte
- `mcp_common.sh`: Gemeinsame Bibliothek für MCP-Server-Skripte (Legacy)

## Übersicht

Die gemeinsamen Bibliotheken bieten folgende Funktionalitäten:

1. **Standardisierte Konfiguration**: Laden von Umgebungsvariablen aus der `.env`-Datei und Bereitstellen von Standardwerten
2. **Logging-Funktionen**: Einheitliche Funktionen für Logging und Fehlerbehandlung
3. **Abhängigkeitsprüfung**: Funktionen zur Überprüfung und Installation von Abhängigkeiten
4. **Docker-Funktionen**: Funktionen zur Verwaltung von Docker-Containern und Docker Compose
5. **Server-Verwaltung**: Funktionen zum Starten und Stoppen von MCP-Servern
6. **Konfigurationserstellung**: Funktionen zum Erstellen von Konfigurationsdateien
7. **Prozessverwaltung**: Funktionen zum Starten, Stoppen und Überwachen von Prozessen
8. **Netzwerkfunktionen**: Funktionen zur Überprüfung von Ports und Netzwerkverbindungen

## Shell-Bibliothek

Die Shell-Bibliothek `shell/common.sh` bietet eine umfassende Sammlung von Funktionen für Shell-Skripte.

### Verwendung

Um die Shell-Bibliothek in einem Skript zu verwenden, fügen Sie folgende Zeilen am Anfang des Skripts ein:

```bash
# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"
```

Für Legacy-Skripte, die noch die alte MCP-Bibliothek verwenden:

```bash
# Basisverzeichnis
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$SCRIPT_DIR/../common/mcp_common.sh"
```

### Shell-Bibliothek: Verfügbare Funktionen

#### Logging-Funktionen

```bash
log_debug "Debug-Nachricht"
log_info "Informationsnachricht"
log_warn "Warnungsnachricht"
log_error "Fehlermeldung"

# Legacy-Aliase
log "Informationsnachricht"
warn "Warnungsnachricht"
error "Fehlermeldung"
info "Hervorgehobene Informationsnachricht"
```

#### Fehlerbehandlung

```bash
set_operation "operation_name"
set_container "container_name"
set_component "component_name"
handle_error $? $LINENO "$BASH_COMMAND"
```

#### Abhängigkeitsprüfung

```bash
check_command "command_name" "installation_hint"
check_file "file_path" "create_if_not_exists"
check_directory "directory_path" "create_if_not_exists"
check_docker
check_docker_compose
start_docker_daemon
check_python_dependencies
```

#### Docker-Funktionen

```bash
start_docker_mcp_servers
stop_docker_mcp_servers
check_container_running "container_name"
check_container_exists "container_name"
start_container "container_name" "image_name" "port_mapping" "environment" "volume_mapping" "network"
stop_container "container_name"
```

#### Server-Verwaltung

```bash
start_mcp_server "server_name" "command" "args"
stop_mcp_server "server_name"
stop_all_mcp_processes
start_n8n_mcp_server
start_openhands_mcp_server
```

#### Konfigurationsverwaltung

```bash
load_env_file "env_file_path"
save_env_file "env_file_path" "var1" "var2" "var3"
create_openhands_config "config_file_path"
create_claude_config "config_file_path"
create_start_scripts
```

## Python-Bibliothek

Die Python-Bibliothek `python/common.py` bietet eine umfassende Sammlung von Klassen und Funktionen für Python-Skripte.

### Verwendung

Um die Python-Bibliothek in einem Skript zu verwenden, fügen Sie folgende Zeilen am Anfang des Skripts ein:

```python
#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Konfiguriere Logging
logger = setup_logging("INFO")

# Lade Konfiguration
config_manager = ConfigManager()
config = config_manager.load_env_file(".env")
```

### Python-Bibliothek: Verfügbare Klassen und Funktionen

#### Logging

```python
logger = setup_logging(level="INFO", log_file="app.log")
logger.debug("Debug-Nachricht")
logger.info("Informationsnachricht")
logger.warning("Warnungsnachricht")
logger.error("Fehlermeldung")
```

#### Konfigurationsmanagement

```python
config_manager = ConfigManager()
config = config_manager.load_json_config("config_name", default={})
config = config_manager.load_yaml_config("config_name", default={})
config_manager.save_json_config("config_name", config)
config_manager.save_yaml_config("config_name", config)
config = config_manager.load_env_file(".env")
config = config_manager.load_env_config(prefix="APP_")
```

#### Docker-Hilfsfunktionen

```python
if DockerUtils.check_docker_installed():
    if DockerUtils.check_docker_running():
        DockerUtils.start_docker_compose("docker-compose.yml")
        DockerUtils.stop_docker_compose("docker-compose.yml")
        if DockerUtils.is_docker_container_running("container_name"):
            logs = DockerUtils.get_docker_container_logs("container_name")
```

#### Prozessverwaltung

```python
if ProcessManager.is_process_running(pid):
    ProcessManager.kill_process(pid)
if ProcessManager.is_process_running_by_name("process_name"):
    ProcessManager.kill_process_by_name("process_name")
success, pid = ProcessManager.start_process(["command", "arg1", "arg2"], log_file="app.log", pid_file="app.pid")
```

#### Netzwerkfunktionen

```python
if NetworkUtils.is_port_in_use(8080):
    print("Port 8080 ist bereits in Verwendung")
free_port = NetworkUtils.find_free_port(8000, 9000)
if NetworkUtils.wait_for_port(8080, timeout=30):
    print("Port 8080 ist verfügbar")
```

#### Systemfunktionen

```python
system_info = SystemUtils.get_system_info()
if SystemUtils.check_command("docker"):
    print("Docker ist installiert")
if SystemUtils.check_python_package("requests"):
    print("requests ist installiert")
else:
    SystemUtils.install_python_package("requests")
```

## Umgebungsvariablen

Die Bibliotheken verwenden folgende Umgebungsvariablen, die in der `.env`-Datei definiert werden können:

| Variable | Beschreibung | Standardwert |
|----------|--------------|--------------|
| `N8N_URL` | URL der n8n-Instanz | `http://localhost:5678` |
| `N8N_API_KEY` | API-Schlüssel für n8n | - |
| `N8N_USER` | Benutzername für n8n | `admin` |
| `N8N_PASSWORD` | Passwort für n8n | `password` |
| `MCP_HTTP_PORT` | Port für den MCP-HTTP-Server | `3333` |
| `MCP_AUTH_TOKEN` | Authentifizierungstoken für MCP-Server | - |
| `OPENHANDS_PORT` | Port für OpenHands | `3000` |
| `OPENHANDS_API_KEY` | API-Schlüssel für OpenHands | - |
| `OPENHANDS_STATE_DIR` | Verzeichnis für OpenHands-Zustandsdaten | `$HOME/.openhands-state` |
| `OPENHANDS_WORKSPACE_DIR` | Verzeichnis für OpenHands-Workspace | `$HOME/openhands-workspace` |
| `OPENHANDS_CONFIG_DIR` | Verzeichnis für OpenHands-Konfiguration | `$HOME/.config/openhands` |
| `OPENHANDS_MAX_WORKERS` | Maximale Anzahl von Worker-Threads für OpenHands | `5` |
| `OLLAMA_PORT` | Port für Ollama | `11434` |
| `OLLAMA_MODEL` | Zu verwendendes Ollama-Modell | `qwen2.5-coder:7b-instruct` |
| `OLLAMA_BASE_URL` | URL der Ollama-API | `http://localhost:11434` |
| `LLM_API_KEY` | API-Schlüssel für LLM | - |
| `LLM_MODEL` | Zu verwendendes LLM-Modell | `anthropic/claude-3-5-sonnet-20240620` |
| `LOG_LEVEL` | Log-Level (debug, info, warn, error) | `info` |
| `LOG_DIR` | Verzeichnis für Log-Dateien | `/tmp/mcp-logs` |
| `GITHUB_TOKEN` | GitHub-Token für API-Zugriff | - |
| `DOCKER_NETWORK` | Docker-Netzwerk für Container | `dev-server-network` |

## Beispiele

### Shell-Skript-Beispiel

```bash
#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

# Erstelle Log-Verzeichnis
create_log_directories

# Überprüfe Abhängigkeiten
check_docker || exit 1
check_docker_compose || exit 1
check_python_dependencies || exit 1

# Starte MCP-Server
log_info "Starte MCP-Server..."
start_mcp_server "filesystem-mcp" "npx" "-y @modelcontextprotocol/server-filesystem --port 3457"
start_mcp_server "github-mcp" "npx" "-y @modelcontextprotocol/server-github --port 3458"

# Warte auf Benutzerunterbrechung
trap 'log_info "Stoppe MCP-Server..."; stop_mcp_server "filesystem-mcp"; stop_mcp_server "github-mcp"' EXIT

# Halte das Skript am Laufen
log_info "MCP-Server gestartet. Drücke Ctrl+C zum Beenden."
while true; do
    sleep 1
done
```

### Python-Skript-Beispiel

```python
#!/usr/bin/env python3

import os
import sys
import time
from pathlib import Path

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

def main():
    # Parse Argumente
    parser = parse_arguments("MCP-Server-Monitor")
    parser.add_argument("--port", type=int, default=8080, help="Port für den Monitor-Server")
    args = parser.parse_args()
    
    # Konfiguriere Logging
    logger = setup_logging(args.log_level, args.log_file)
    
    # Lade Konfiguration
    config_manager = ConfigManager()
    config = config_manager.load_env_file(".env")
    
    # Überprüfe Docker
    if not DockerUtils.check_docker_installed():
        logger.error("Docker ist nicht installiert.")
        return 1
    
    if not DockerUtils.check_docker_running():
        logger.error("Docker läuft nicht.")
        return 1
    
    # Starte Docker Compose
    logger.info("Starte MCP-Server mit Docker Compose...")
    if not DockerUtils.start_docker_compose(BASE_DIR / "docker-mcp-servers" / "docker-compose.yml"):
        logger.error("Fehler beim Starten der MCP-Server.")
        return 1
    
    # Warte auf Verfügbarkeit der Server
    logger.info("Warte auf Verfügbarkeit der MCP-Server...")
    if not NetworkUtils.wait_for_port(8080, timeout=30):
        logger.error("MCP-Server sind nicht verfügbar.")
        return 1
    
    logger.info("MCP-Server erfolgreich gestartet.")
    
    try:
        # Halte das Skript am Laufen
        logger.info("Drücke Ctrl+C zum Beenden.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Beende MCP-Server...")
        DockerUtils.stop_docker_compose(BASE_DIR / "docker-mcp-servers" / "docker-compose.yml")
        logger.info("MCP-Server gestoppt.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Migrationsanleitung

Wenn Sie bestehende Skripte auf die neuen gemeinsamen Bibliotheken umstellen möchten, folgen Sie diesen Schritten:

### Shell-Skripte

1. Ersetzen Sie individuelle Logging-Funktionen durch die standardisierten Funktionen
2. Ersetzen Sie individuelle Fehlerbehandlung durch die standardisierte Fehlerbehandlung
3. Ersetzen Sie individuelle Docker-Funktionen durch die standardisierten Funktionen
4. Ersetzen Sie individuelle Konfigurationsverwaltung durch die standardisierten Funktionen

Beispiel:

```bash
# Altes Skript
#!/bin/bash
echo "Starte Server..."
docker-compose up -d
echo "Server gestartet."

# Neues Skript
#!/bin/bash
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$BASE_DIR/scripts/common/shell/common.sh"
log_info "Starte Server..."
start_docker_mcp_servers
log_info "Server gestartet."
```

### Python-Skripte

1. Importieren Sie die gemeinsame Bibliothek
2. Ersetzen Sie individuelle Logging-Funktionen durch die standardisierten Funktionen
3. Ersetzen Sie individuelle Konfigurationsverwaltung durch die standardisierten Funktionen
4. Ersetzen Sie individuelle Docker-Funktionen durch die standardisierten Funktionen

Beispiel:

```python
# Altes Skript
#!/usr/bin/env python3
import os
import subprocess
print("Starte Server...")
subprocess.run(["docker-compose", "up", "-d"])
print("Server gestartet.")

# Neues Skript
#!/usr/bin/env python3
import os
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))
from common import setup_logging, DockerUtils
logger = setup_logging("INFO")
logger.info("Starte Server...")
DockerUtils.start_docker_compose("docker-compose.yml")
logger.info("Server gestartet.")
```