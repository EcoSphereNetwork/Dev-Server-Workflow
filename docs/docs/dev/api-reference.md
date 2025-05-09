# API-Referenz

Diese Dokumentation beschreibt die APIs der verschiedenen Komponenten des Dev-Server-Workflow-Projekts.

## Gemeinsame Bibliotheken

### Shell-Bibliothek

Die Shell-Bibliothek `scripts/common/shell/common.sh` bietet folgende Funktionen:

#### Logging-Funktionen

```bash
log_debug "Debug-Nachricht"    # Protokolliert eine Debug-Nachricht
log_info "Info-Nachricht"      # Protokolliert eine Informationsnachricht
log_warn "Warnungsnachricht"   # Protokolliert eine Warnungsnachricht
log_error "Fehlermeldung"      # Protokolliert eine Fehlermeldung
```

#### Fehlerbehandlung

```bash
set_operation "operation_name"   # Setzt die aktuelle Operation für die Fehlerbehandlung
set_container "container_name"   # Setzt den aktuellen Container für die Fehlerbehandlung
set_component "component_name"   # Setzt die aktuelle Komponente für die Fehlerbehandlung
handle_error $? $LINENO "$BASH_COMMAND"  # Behandelt einen Fehler
```

#### Abhängigkeitsprüfung

```bash
check_command "command_name" "installation_hint"  # Prüft, ob ein Befehl verfügbar ist
check_file "file_path" "create_if_not_exists"     # Prüft, ob eine Datei existiert
check_directory "directory_path" "create_if_not_exists"  # Prüft, ob ein Verzeichnis existiert
check_docker                                      # Prüft, ob Docker installiert ist und läuft
check_docker_compose                              # Prüft, ob Docker Compose installiert ist
start_docker_daemon                               # Startet den Docker-Daemon
check_python_dependencies                         # Prüft, ob alle Python-Abhängigkeiten installiert sind
```

#### Docker-Funktionen

```bash
start_docker_mcp_servers                          # Startet die MCP-Server mit Docker Compose
stop_docker_mcp_servers                           # Stoppt die MCP-Server mit Docker Compose
check_container_running "container_name"          # Prüft, ob ein Container läuft
check_container_exists "container_name"           # Prüft, ob ein Container existiert
start_container "container_name" "image_name" "port_mapping" "environment" "volume_mapping" "network"  # Startet einen Container
stop_container "container_name"                   # Stoppt einen Container
```

#### Server-Verwaltung

```bash
start_mcp_server "server_name" "command" "args"   # Startet einen MCP-Server
stop_mcp_server "server_name"                     # Stoppt einen MCP-Server
stop_all_mcp_processes                            # Stoppt alle MCP-Server-Prozesse
start_n8n_mcp_server                              # Startet den n8n MCP-Server
start_openhands_mcp_server                        # Startet den OpenHands MCP-Server
```

#### Konfigurationsverwaltung

```bash
load_env_file "env_file_path"                     # Lädt Umgebungsvariablen aus einer .env-Datei
save_env_file "env_file_path" "var1" "var2" "var3"  # Speichert Umgebungsvariablen in einer .env-Datei
create_openhands_config "config_file_path"        # Erstellt eine OpenHands-Konfigurationsdatei
create_claude_config "config_file_path"           # Erstellt eine Claude-Konfigurationsdatei
create_start_scripts                              # Erstellt Start-Skripte
```

### Python-Bibliothek

Die Python-Bibliothek `scripts/common/python/common.py` bietet folgende Klassen und Funktionen:

#### Logging

```python
logger = setup_logging(level="INFO", log_file="app.log")  # Konfiguriert das Logging
logger.debug("Debug-Nachricht")                           # Protokolliert eine Debug-Nachricht
logger.info("Informationsnachricht")                      # Protokolliert eine Informationsnachricht
logger.warning("Warnungsnachricht")                       # Protokolliert eine Warnungsnachricht
logger.error("Fehlermeldung")                             # Protokolliert eine Fehlermeldung
```

#### Konfigurationsmanagement

```python
config_manager = ConfigManager()                          # Erstellt einen Konfigurationsmanager
config = config_manager.load_json_config("config_name", default={})  # Lädt eine JSON-Konfigurationsdatei
config = config_manager.load_yaml_config("config_name", default={})  # Lädt eine YAML-Konfigurationsdatei
config_manager.save_json_config("config_name", config)    # Speichert eine Konfiguration als JSON-Datei
config_manager.save_yaml_config("config_name", config)    # Speichert eine Konfiguration als YAML-Datei
config = config_manager.load_env_file(".env")             # Lädt Umgebungsvariablen aus einer .env-Datei
config = config_manager.load_env_config(prefix="APP_")    # Lädt Umgebungsvariablen mit einem Präfix
```

#### Docker-Hilfsfunktionen

```python
DockerUtils.check_docker_installed()                      # Prüft, ob Docker installiert ist
DockerUtils.check_docker_running()                        # Prüft, ob Docker läuft
DockerUtils.check_docker_compose_installed()              # Prüft, ob Docker Compose installiert ist
DockerUtils.get_docker_compose_command()                  # Ermittelt den Docker Compose-Befehl
DockerUtils.start_docker_compose("docker-compose.yml")    # Startet Docker Compose
DockerUtils.stop_docker_compose("docker-compose.yml")     # Stoppt Docker Compose
DockerUtils.get_docker_container_id("container_name")     # Ermittelt die ID eines Containers
DockerUtils.is_docker_container_running("container_name") # Prüft, ob ein Container läuft
DockerUtils.get_docker_container_logs("container_name")   # Ruft die Logs eines Containers ab
```

#### Prozessverwaltung

```python
ProcessManager.is_process_running(pid)                    # Prüft, ob ein Prozess läuft
ProcessManager.is_process_running_by_name("process_name") # Prüft, ob ein Prozess mit dem Namen läuft
ProcessManager.kill_process(pid, force=False)             # Beendet einen Prozess
ProcessManager.kill_process_by_name("process_name", force=False)  # Beendet Prozesse mit dem Namen
ProcessManager.start_process(["command", "arg1", "arg2"], log_file="app.log", pid_file="app.pid")  # Startet einen Prozess
```

#### Netzwerkfunktionen

```python
NetworkUtils.is_port_in_use(port, host="localhost")       # Prüft, ob ein Port verwendet wird
NetworkUtils.find_free_port(start_port=8000, end_port=9000, host="localhost")  # Findet einen freien Port
NetworkUtils.wait_for_port(port, host="localhost", timeout=30)  # Wartet, bis ein Port verfügbar ist
```

#### Systemfunktionen

```python
SystemUtils.get_system_info()                             # Ruft Systeminformationen ab
SystemUtils.check_command("command")                      # Prüft, ob ein Befehl verfügbar ist
SystemUtils.check_python_package("package")               # Prüft, ob ein Python-Paket installiert ist
SystemUtils.install_python_package("package")             # Installiert ein Python-Paket
```

#### Kommandozeilenargumente

```python
args = parse_arguments("Beschreibung des Skripts", "Epilog für die Hilfe")  # Parst Kommandozeilenargumente
```

## MCP-Server-APIs

### n8n MCP-Server

Der n8n MCP-Server implementiert das Model Context Protocol und bietet folgende Funktionen:

#### mcp.listTools

Listet alle verfügbaren Tools auf.

**Anfrage:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.listTools"
}
```

**Antwort:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "name": "workflow_github_to_openproject",
      "description": "Führt den n8n-Workflow 'GitHub to OpenProject' aus",
      "parameter_schema": {
        "type": "object",
        "properties": {
          "repository": {
            "type": "string",
            "description": "GitHub-Repository"
          },
          "issue_number": {
            "type": "integer",
            "description": "GitHub-Issue-Nummer"
          }
        }
      }
    },
    // Weitere Tools...
  ]
}
```

#### mcp.callTool

Ruft ein Tool auf.

**Anfrage:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "mcp.callTool",
  "params": {
    "name": "workflow_github_to_openproject",
    "arguments": {
      "repository": "EcoSphereNetwork/Dev-Server-Workflow",
      "issue_number": 42
    }
  }
}
```

**Antwort:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "success": true,
    "execution_id": "550e8400-e29b-41d4-a716-446655440000",
    "data": {
      // Workflow-spezifische Daten
    }
  }
}
```

### OpenHands MCP-Server

Der OpenHands MCP-Server implementiert das Model Context Protocol und bietet folgende Funktionen:

#### mcp.listTools

Listet alle verfügbaren Tools auf.

**Anfrage:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.listTools"
}
```

**Antwort:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "name": "create_agent",
      "description": "Erstellt einen neuen OpenHands-Agenten",
      "parameter_schema": {
        "type": "object",
        "properties": {
          "config_file": {
            "type": "string",
            "description": "Pfad zur Konfigurationsdatei"
          }
        }
      }
    },
    // Weitere Tools...
  ]
}
```

#### mcp.callTool

Ruft ein Tool auf.

**Anfrage:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "mcp.callTool",
  "params": {
    "name": "execute_task",
    "arguments": {
      "agent_id": "550e8400-e29b-41d4-a716-446655440000",
      "task": "Erstelle ein neues GitHub-Repository",
      "context": {
        "repository_name": "new-repo",
        "description": "Ein neues Repository"
      }
    }
  }
}
```

**Antwort:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running"
  }
}
```

## CLI-APIs

### dev-server-cli.sh

Die Hauptschnittstelle `dev-server-cli.sh` bietet folgende Befehle:

#### status

Zeigt den Status aller Komponenten an.

```bash
./dev-server-cli.sh status
```

#### start

Startet eine Komponente.

```bash
./dev-server-cli.sh start <komponente>
```

#### stop

Stoppt eine Komponente.

```bash
./dev-server-cli.sh stop <komponente>
```

#### restart

Startet eine Komponente neu.

```bash
./dev-server-cli.sh restart <komponente>
```

#### logs

Zeigt die Logs einer Komponente an.

```bash
./dev-server-cli.sh logs <komponente>
```

#### config

Verwaltet die Konfiguration des Systems.

```bash
./dev-server-cli.sh config list <typ> <datei>
./dev-server-cli.sh config get <typ> <datei> <schlüssel>
./dev-server-cli.sh config save <typ> <datei> <schlüssel> <wert>
./dev-server-cli.sh config delete <typ> <datei> <schlüssel>
```

#### workflow

Verwaltet n8n-Workflows.

```bash
./dev-server-cli.sh workflow list
./dev-server-cli.sh workflow run <workflow>
./dev-server-cli.sh workflow activate <workflow>
./dev-server-cli.sh workflow deactivate <workflow>
```

#### openhands

Verwaltet OpenHands.

```bash
./dev-server-cli.sh openhands execute <task>
./dev-server-cli.sh openhands config
```

#### ai

Verwendet den KI-Assistenten.

```bash
./dev-server-cli.sh ai <frage oder befehl>
```

#### diagnose

Führt Diagnosen durch.

```bash
./dev-server-cli.sh diagnose
./dev-server-cli.sh diagnose network
./dev-server-cli.sh diagnose component <komponente>
```

### ai_assistant_improved.sh

Der KI-Assistent `cli/ai_assistant_improved.sh` bietet folgende Funktionen:

#### process_nl_command

Verarbeitet einen natürlichsprachlichen Befehl.

```bash
./cli/ai_assistant_improved.sh "Starte alle MCP-Server"
```

#### process_nl_question

Verarbeitet eine natürlichsprachliche Frage.

```bash
./cli/ai_assistant_improved.sh "Wie kann ich einen neuen Workflow erstellen?"
```

## n8n-APIs

### n8n REST API

Die n8n REST API bietet folgende Endpunkte:

#### GET /api/v1/workflows

Ruft alle Workflows ab.

**Anfrage:**
```http
GET /api/v1/workflows HTTP/1.1
Host: localhost:5678
X-N8N-API-KEY: your-api-key
```

**Antwort:**
```json
[
  {
    "id": "1",
    "name": "GitHub to OpenProject",
    "active": true,
    "createdAt": "2023-01-01T00:00:00.000Z",
    "updatedAt": "2023-01-01T00:00:00.000Z",
    "tags": ["mcp"]
  },
  // Weitere Workflows...
]
```

#### POST /api/v1/workflows/{id}/execute

Führt einen Workflow aus.

**Anfrage:**
```http
POST /api/v1/workflows/1/execute HTTP/1.1
Host: localhost:5678
X-N8N-API-KEY: your-api-key
Content-Type: application/json

{
  "workflowData": {
    "id": "1"
  },
  "executionId": "550e8400-e29b-41d4-a716-446655440000",
  "runData": {
    "repository": "EcoSphereNetwork/Dev-Server-Workflow",
    "issue_number": 42
  }
}
```

**Antwort:**
```json
{
  "data": {
    // Workflow-spezifische Daten
  }
}
```

## OpenHands-APIs

### OpenHands REST API

Die OpenHands REST API bietet folgende Endpunkte:

#### POST /api/v1/agents

Erstellt einen neuen Agenten.

**Anfrage:**
```http
POST /api/v1/agents HTTP/1.1
Host: localhost:3000
Content-Type: application/json

{
  "config_file": "/path/to/config.json"
}
```

**Antwort:**
```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "config_file": "/path/to/config.json",
  "api_available": true
}
```

#### POST /api/v1/tasks

Erstellt eine neue Aufgabe.

**Anfrage:**
```http
POST /api/v1/tasks HTTP/1.1
Host: localhost:3000
Content-Type: application/json

{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "task": "Erstelle ein neues GitHub-Repository",
  "context": {
    "repository_name": "new-repo",
    "description": "Ein neues Repository"
  }
}
```

**Antwort:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running"
}
```

#### GET /api/v1/tasks/{id}

Ruft den Status einer Aufgabe ab.

**Anfrage:**
```http
GET /api/v1/tasks/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:3000
```

**Antwort:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    // Aufgabenspezifische Daten
  }
}
```