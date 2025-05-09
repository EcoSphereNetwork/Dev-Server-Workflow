#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Common library for MCP scripts
# This file contains shared functions and variables used across multiple MCP scripts

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../.."

# Standardkonfiguration
DEFAULT_LOG_DIR="/tmp/mcp-logs"
DEFAULT_MCP_HTTP_PORT=3333
DEFAULT_N8N_URL="http://localhost:5678"
DEFAULT_OPENHANDS_PORT=3000
DEFAULT_OLLAMA_PORT=8000
DEFAULT_OLLAMA_MODEL="qwen2.5-coder:7b-instruct"
DEFAULT_OLLAMA_BASE_URL="http://localhost:11434"

# Lade Umgebungsvariablen aus .env, falls vorhanden
if [ -f "${BASE_DIR}/.env" ]; then
    source "${BASE_DIR}/.env"
fi

# Setze Standardwerte, falls nicht in .env definiert
LOG_DIR=${LOG_DIR:-"$DEFAULT_LOG_DIR"}
MCP_HTTP_PORT=${MCP_HTTP_PORT:-$DEFAULT_MCP_HTTP_PORT}
N8N_URL=${N8N_URL:-"$DEFAULT_N8N_URL"}
N8N_API_KEY=${N8N_API_KEY:-""}
OPENHANDS_PORT=${OPENHANDS_PORT:-$DEFAULT_OPENHANDS_PORT}
OLLAMA_PORT=${OLLAMA_PORT:-$DEFAULT_OLLAMA_PORT}
OLLAMA_MODEL=${OLLAMA_MODEL:-"$DEFAULT_OLLAMA_MODEL"}
OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-"$DEFAULT_OLLAMA_BASE_URL"}
OPENHANDS_STATE_DIR=${OPENHANDS_STATE_DIR:-"$HOME/.openhands-state"}
OPENHANDS_WORKSPACE_DIR=${OPENHANDS_WORKSPACE_DIR:-"$HOME/openhands-workspace"}
OPENHANDS_CONFIG_DIR=${OPENHANDS_CONFIG_DIR:-"$HOME/.config/openhands"}
OPENHANDS_MAX_WORKERS=${OPENHANDS_MAX_WORKERS:-5}

# Funktion zum Anzeigen von Nachrichten
log() {
    log_info "${GREEN}[INFO]${NC} $1"
}

warn() {
    log_info "${YELLOW}[WARN]${NC} $1"
}

error() {
    log_info "${RED}[ERROR]${NC} $1"
}

info() {
    log_info "${BLUE}[INFO]${NC} $1"
}

# Funktion zum Überprüfen einer Paketversion
check_version() {
    local package=$1
    local min_version=$2
    local version_cmd=$3
    local version_regex=$4

    if ! command -v "$package" &> /dev/null; then
        return 1
    fi

    local version_output
    version_output=$($version_cmd)
    local current_version
    current_version=$(log_info "$version_output" | grep -oE "$version_regex" | head -1)

    if [ -z "$current_version" ]; then
        warn "Konnte die Version von $package nicht ermitteln."
        return 2
    fi

    # Vergleiche Versionen - nutze "sort -V" und kehre die Logik um, da wir prüfen, ob current >= min
    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" = "$min_version" ]; then
        log "$package Version $current_version gefunden (Minimum: $min_version)."
        return 0
    else
        warn "$package Version $current_version ist älter als die benötigte Version $min_version."
        return 3
    fi
}

# Funktion zum Einrichten eines Alias für docker-compose
setup_docker_compose_alias() {
    # Prüfen, ob docker compose Befehl verfügbar ist
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Prüfen, ob docker-compose Befehl verfügbar ist
        if ! command -v docker-compose &> /dev/null; then
            log "Richte Alias für docker-compose ein..."
            
            # Prüfen, welche Shell verwendet wird
            local shell_rc
            if [ -n "$ZSH_VERSION" ]; then
                shell_rc="$HOME/.zshrc"
            elif [ -n "$BASH_VERSION" ]; then
                shell_rc="$HOME/.bashrc"
            else
                # Standardmäßig .bashrc verwenden
                shell_rc="$HOME/.bashrc"
            fi
            
            # Prüfen, ob der Alias bereits existiert
            if ! grep -q "alias docker-compose='docker compose'" "$shell_rc"; then
                echo 'alias docker-compose="docker compose"' >> "$shell_rc"
                log "Alias zu $shell_rc hinzugefügt."
                log "Bitte führen Sie 'source $shell_rc' aus, oder starten Sie ein neues Terminal, um den Alias zu aktivieren."
                
                # Temporär für die aktuelle Sitzung einrichten
                alias docker-compose="docker compose"
                log "Alias temporär für die aktuelle Sitzung eingerichtet."
            else
                log "Alias existiert bereits in $shell_rc."
            fi
        else
            log "docker-compose Befehl ist bereits verfügbar."
        fi
    else
        warn "Docker Compose Plugin ist nicht installiert. Kann keinen Alias einrichten."
    fi
}

# Funktion zum Überprüfen, ob Docker installiert ist
check_docker() {
    log "Überprüfe Docker-Installation..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut."
        return 1
    fi
    
    # Überprüfe die Docker-Version
    check_version "docker" "20.10.0" "docker --version" "([0-9]+\.[0-9]+\.[0-9]+)"
    if [ $? -eq 0 ]; then
        log "Docker ist installiert und ausreichend aktuell."
    else
        warn "Docker ist installiert, aber möglicherweise nicht ausreichend aktuell."
        warn "Es wird empfohlen, Docker auf mindestens Version 20.10.0 zu aktualisieren."
    fi
    
    return 0
}

# Funktion zum Überprüfen, ob Docker Compose installiert ist
check_docker_compose() {
    log "Überprüfe Docker Compose-Installation..."
    
    # Prüfe zunächst das neue Docker-Compose-Plugin
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Versuche, die Version zu ermitteln
        docker_compose_version=$(docker compose version --short 2>/dev/null || docker compose version 2>/dev/null | grep -oE "v?[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        
        if [ -n "$docker_compose_version" ]; then
            # Entferne ein mögliches 'v' am Anfang
            docker_compose_version=${docker_compose_version#v}
            log "Docker Compose Plugin Version: $docker_compose_version"
            
            # Richte den Alias ein
            setup_docker_compose_alias
            
            return 0
        fi
    fi
    
    # Prüfe das eigenständige Docker-Compose-Binary
    if command -v docker-compose &> /dev/null; then
        log "Eigenständiges Docker Compose ist installiert."
        
        docker_compose_version=$(docker-compose --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        if [ -n "$docker_compose_version" ]; then
            log "Docker Compose Version: $docker_compose_version"
            
            # Vergleiche mit der Mindestversion
            if [ "$(printf '%s\n' "1.29.0" "$docker_compose_version" | sort -V | head -n1)" = "1.29.0" ]; then
                log "Docker Compose ist ausreichend aktuell."
                return 0
            else
                warn "Docker Compose Version ist älter als 1.29.0. Ein Update wird empfohlen."
            fi
        fi
    fi
    
    error "Docker Compose ist nicht installiert oder zu alt. Bitte installieren Sie Docker Compose."
    return 1
}

# Funktion zum Starten des Docker-Daemons
start_docker_daemon() {
    log "Überprüfe, ob der Docker-Daemon läuft..."
    
    if ! docker info &> /dev/null; then
        warn "Docker-Daemon läuft nicht. Versuche, ihn zu starten..."
        
        if command -v systemctl &> /dev/null; then
            sudo systemctl start docker
        elif command -v service &> /dev/null; then
            sudo service docker start
        else
            # Direkter Start des Docker-Daemons im Hintergrund
            sudo dockerd > /tmp/docker.log 2>&1 &
            sleep 5
        fi
        
        if ! docker info &> /dev/null; then
            error "Konnte den Docker-Daemon nicht starten. Bitte starten Sie ihn manuell."
            error "Verwenden Sie 'sudo systemctl start docker' oder 'sudo service docker start'."
            return 1
        fi
        
        log "Docker-Daemon wurde gestartet."
    else
        log "Docker-Daemon läuft bereits."
    fi
    
    return 0
}

# Funktion zum Erstellen der Log-Verzeichnisse
create_log_directories() {
    info "Erstelle Log-Verzeichnisse..."
    
    mkdir -p "$LOG_DIR"
    
    # Bereinige alte Log-Dateien, die älter als 7 Tage sind
    find "$LOG_DIR" -type f -name "*.log" -mtime +7 -delete
    
    log "Log-Verzeichnisse erstellt."
    return 0
}

# Funktion zum Überprüfen und Installieren von Python-Abhängigkeiten
check_python_dependencies() {
    log "Überprüfe Python-Abhängigkeiten..."
    
    # Prüfe Python 3
    if ! command -v python3 &> /dev/null; then
        error "Python 3 ist nicht installiert. Bitte installieren Sie Python 3."
        return 1
    fi
    
    # Prüfe pip3
    if ! command -v pip3 &> /dev/null; then
        error "pip3 ist nicht installiert. Bitte installieren Sie pip3."
        return 1
    fi
    
    # Prüfe, ob die benötigten Python-Pakete installiert sind
    local required_packages=("requests" "pyyaml")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        warn "Fehlende Python-Pakete: ${missing_packages[*]}"
        info "Installiere fehlende Python-Pakete..."
        pip3 install --user "${missing_packages[@]}"
    fi
    
    log "Alle Python-Abhängigkeiten sind installiert."
    return 0
}

# Funktion zum Starten eines MCP-Servers
start_mcp_server() {
    local name=$1
    local command=$2
    local args=$3
    local log_file="$LOG_DIR/$name.log"
    
    log_info "Starte MCP-Server: $name"
    log_info "Befehl: $command $args"
    log_info "Log-Datei: $log_file"
    
    # Starte den Server im Hintergrund
    eval "$command $args > $log_file 2>&1 &"
    local pid=$!
    
    log_info "PID: $pid"
    log_info "$pid" > "$LOG_DIR/$name.pid"
    
    # Warte kurz, um zu prüfen, ob der Server gestartet ist
    sleep 2
    if ! kill -0 $pid 2>/dev/null; then
        log_info "Fehler: Server $name konnte nicht gestartet werden"
        cat "$log_file"
        return 1
    fi
    
    log_info "Server $name erfolgreich gestartet"
    return 0
}

# Funktion zum Stoppen eines MCP-Servers
stop_mcp_server() {
    local name=$1
    local pid_file="$LOG_DIR/$name.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        log_info "Stoppe MCP-Server: $name (PID: $pid)"
        
        # Sende SIGTERM an den Prozess
        kill $pid 2>/dev/null || true
        
        # Warte kurz und prüfe, ob der Prozess beendet ist
        sleep 2
        if kill -0 $pid 2>/dev/null; then
            log_info "Server reagiert nicht, sende SIGKILL"
            kill -9 $pid 2>/dev/null || true
        fi
        
        rm -f "$pid_file"
        log_info "Server $name gestoppt"
    else
        log_info "Kein PID-File für Server $name gefunden"
    fi
}

# Funktion zum Stoppen aller MCP-Server
stop_all_servers() {
    log_info "Stoppe alle MCP-Server..."
    
    for pid_file in "$LOG_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            local name=$(basename "$pid_file" .pid)
            stop_mcp_server "$name"
        fi
    done
    
    log_info "Alle Server gestoppt"
}

# Funktion zum Starten der Docker-basierten MCP-Server
start_docker_mcp_servers() {
    info "Starte Docker-basierte MCP-Server..."
    
    # Überprüfe, ob das Docker-Compose-File existiert
    local docker_compose_dir="${BASE_DIR}/docker-mcp-servers"
    
    if [ ! -f "$docker_compose_dir/docker-compose.yml" ]; then
        if [ -f "$docker_compose_dir/docker-compose-full.yml" ]; then
            log "Kopiere docker-compose-full.yml nach docker-compose.yml..."
            cp "$docker_compose_dir/docker-compose-full.yml" "$docker_compose_dir/docker-compose.yml"
        else
            error "Docker-Compose-Datei nicht gefunden: $docker_compose_dir/docker-compose.yml"
            error "Bitte führen Sie zuerst install-mcp-servers.sh aus."
            return 1
        fi
    fi
    
    # Wechsle in das MCP-Servers-Verzeichnis und starte die Container
    cd "$docker_compose_dir"
    
    # Verwende docker-compose oder docker compose, je nachdem, was verfügbar ist
    if command -v docker-compose &> /dev/null; then
        log "Verwende docker-compose..."
        docker-compose up -d
    else
        log "Verwende docker compose..."
        docker compose up -d
    fi
    
    # Überprüfe, ob die Container gestartet wurden
    if command -v docker-compose &> /dev/null; then
        if docker-compose ps | grep -q "Exit"; then
            error "Einige Container konnten nicht gestartet werden. Bitte überprüfen Sie die Logs mit 'docker-compose logs'."
            return 1
        fi
    else
        if docker compose ps | grep -q "Exit"; then
            error "Einige Container konnten nicht gestartet werden. Bitte überprüfen Sie die Logs mit 'docker compose logs'."
            return 1
        fi
    fi
    
    log "Docker-basierte MCP-Server erfolgreich gestartet."
    log "MCP Inspector UI ist verfügbar unter: http://localhost:8080"
    
    # Zeige die gestarteten Container an
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    return 0
}

# Funktion zum Starten des n8n MCP-Servers
start_n8n_mcp_server() {
    info "Starte n8n MCP-Server..."
    
    if [ -z "$N8N_API_KEY" ]; then
        warn "API-Schlüssel für n8n nicht angegeben. Der n8n MCP-Server könnte eingeschränkt funktionieren."
    fi
    
    # Überprüfe, ob das Skript existiert
    if [ -f "${BASE_DIR}/src/n8n_mcp_server.py" ]; then
        log "Verwende n8n_mcp_server.py..."
        python3 "${BASE_DIR}/src/n8n_mcp_server.py" --n8n-url "$N8N_URL" --api-key "$N8N_API_KEY" &
        echo $! > "$LOG_DIR/n8n_mcp_server.pid"
        log "n8n MCP-Server gestartet (PID: $(cat "$LOG_DIR/n8n_mcp_server.pid"))"
    elif [ -f "${BASE_DIR}/src/n8n-mcp-server.py" ]; then
        log "Verwende n8n-mcp-server.py..."
        python3 "${BASE_DIR}/src/n8n-mcp-server.py" --n8n-url "$N8N_URL" --api-key "$N8N_API_KEY" &
        echo $! > "$LOG_DIR/n8n_mcp_server.pid"
        log "n8n MCP-Server gestartet (PID: $(cat "$LOG_DIR/n8n_mcp_server.pid"))"
    else
        warn "n8n MCP-Server-Skript nicht gefunden. Der n8n MCP-Server wurde nicht gestartet."
        return 1
    fi
    
    return 0
}

# Funktion zum Start des OpenHands MCP-Servers
start_openhands_mcp_server() {
    info "Starte OpenHands MCP-Server..."
    
    # Überprüfe, ob das Skript existiert
    if [ -f "${BASE_DIR}/src/openhands_mcp_server.py" ]; then
        log "Verwende openhands_mcp_server.py..."
        python3 "${BASE_DIR}/src/openhands_mcp_server.py" --max-workers "$OPENHANDS_MAX_WORKERS" &
        echo $! > "$LOG_DIR/openhands_mcp_server.pid"
        log "OpenHands MCP-Server gestartet (PID: $(cat "$LOG_DIR/openhands_mcp_server.pid"))"
    elif [ -f "${BASE_DIR}/src/openhands-mcp-server.py" ]; then
        log "Verwende openhands-mcp-server.py..."
        python3 "${BASE_DIR}/src/openhands-mcp-server.py" --max-workers "$OPENHANDS_MAX_WORKERS" &
        echo $! > "$LOG_DIR/openhands_mcp_server.pid"
        log "OpenHands MCP-Server gestartet (PID: $(cat "$LOG_DIR/openhands_mcp_server.pid"))"
    else
        warn "OpenHands MCP-Server-Skript nicht gefunden. Der OpenHands MCP-Server wurde nicht gestartet."
        return 1
    fi
    
    return 0
}

# Funktion zum Erstellen der OpenHands-Konfiguration
create_openhands_config() {
    info "Erstelle OpenHands-Konfiguration..."
    
    # Erstelle Verzeichnisse
    mkdir -p "$OPENHANDS_STATE_DIR"
    mkdir -p "$OPENHANDS_WORKSPACE_DIR"
    mkdir -p "$OPENHANDS_CONFIG_DIR"
    
    # Erstelle OpenHands Konfigurationsdatei
    cat > "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[core]
debug = false
disable_color = false
cache_dir = "/tmp/cache"
save_trajectory_path = "/.openhands-state/trajectories"
file_store_path = "/.openhands-state/file_store"
file_store = "memory"
file_uploads_allowed_extensions = [".*"]
file_uploads_max_file_size_mb = 0
file_uploads_restrict_file_types = false
max_budget_per_task = 0.0
max_iterations = 100
run_as_openhands = true
runtime = "docker"
default_agent = "CodeActAgent"
jwt_secret = "replace-with-a-secure-random-key"

[llm]
model = "claude-3-5-sonnet-20241022"
num_retries = 8
retry_max_wait = 120
retry_min_wait = 15
retry_multiplier = 2.0
drop_params = false
caching_prompt = true
temperature = 0.0
timeout = 0
top_p = 1.0
max_message_chars = 30000

[agent]
llm_config = "default"
function_calling = true
enable_browsing = true
enable_llm_editor = false
enable_jupyter = false
enable_history_truncation = true
enable_prompt_extensions = true

[sandbox]
timeout = 120
user_id = 1000
base_container_image = "docker.all-hands.dev/all-hands-ai/runtime:0.36-nikolaik"
use_host_network = false
runtime_binding_address = "0.0.0.0"
enable_auto_lint = false
initialize_plugins = true
volumes = "${OPENHANDS_WORKSPACE_DIR}:/workspace:rw"

[security]
confirmation_mode = false
security_analyzer = ""

[mcp]
# Standard MCP-Server über Stdio
stdio_servers = [
    { name = "filesystem", command = "npx", args = ["-y", "@modelcontextprotocol/server-filesystem"] },
    { name = "brave-search", command = "npx", args = ["-y", "@modelcontextprotocol/server-brave-search"], env = { BRAVE_API_KEY = "${BRAVE_API_KEY:-""}" } },
    { name = "github", command = "npx", args = ["-y", "@modelcontextprotocol/server-github"], env = { GITHUB_TOKEN = "${GITHUB_TOKEN:-""}" } },
    { name = "memory", command = "npx", args = ["-y", "@modelcontextprotocol/server-memory"] }
]

# SSE-Server für Ollama-MCP-Bridge
sse_servers = [
  "http://localhost:${OLLAMA_PORT}/mcp"
]
EOF
    
    # Erstelle Docker-Compose-Datei
    cat > "$HOME/openhands-docker-compose.yml" << EOF
version: "3"
services:
  openhands:
    image: docker.all-hands.dev/all-hands-ai/openhands:0.36
    ports:
      - "${OPENHANDS_PORT}:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${OPENHANDS_STATE_DIR}:/.openhands-state
      - ${OPENHANDS_CONFIG_DIR}:/config
      - ${OPENHANDS_WORKSPACE_DIR}:/workspace
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.36-nikolaik
      - LOG_ALL_EVENTS=true
      - CONFIG_PATH=/config/config.toml
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped
EOF
    
    log "OpenHands-Konfiguration erstellt."
    return 0
}

# Funktion zum Erstellen der Claude Desktop Konfiguration
create_claude_config() {
    info "Erstelle Claude Desktop Konfiguration..."
    
    # Erstelle Verzeichnis
    mkdir -p "$HOME/.config/Claude"
    
    # Erstelle Claude Desktop Konfiguration
    cat > "$HOME/.config/Claude/claude_desktop_config.json" << EOF
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY:-""}"
      }
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN:-""}"
      }
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    },
    "everything": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-everything"
      ]
    },
    "openhands": {
      "sseUrl": "http://localhost:${OPENHANDS_PORT}/mcp"
    },
    "ollama-bridge": {
      "sseUrl": "http://localhost:${OLLAMA_PORT}/mcp"
    }
  }
}
EOF
    
    log "Claude Desktop Konfiguration erstellt."
    return 0
}

# Funktion zum Erstellen der Start-Skripte
create_start_scripts() {
    info "Erstelle Start-Skripte..."
    
    # MCP-Inspektor
    cat > "$HOME/start-mcp-inspector.sh" << EOF
#!/bin/bash
npx @modelcontextprotocol/inspector
EOF
    chmod +x "$HOME/start-mcp-inspector.sh"
    
    # OpenHands
    cat > "$HOME/start-openhands.sh" << EOF
#!/bin/bash
docker compose -f $HOME/openhands-docker-compose.yml up -d
log_info "OpenHands gestartet unter http://localhost:${OPENHANDS_PORT}"
EOF
    chmod +x "$HOME/start-openhands.sh"
    
    # Ollama-MCP-Bridge
    if [ -d "$HOME/ollama-mcp-bridge" ]; then
        cat > "$HOME/start-ollama-bridge.sh" << EOF
#!/bin/bash
cd $HOME/ollama-mcp-bridge
npm start
EOF
        chmod +x "$HOME/start-ollama-bridge.sh"
        
        # Alles-in-einem-Starter
        cat > "$HOME/start-all-mcp.sh" << EOF
#!/bin/bash

# Starte alle MCP-Dienste
log_info "Starte alle MCP-Dienste..."

# Starte OpenHands
log_info "Starte OpenHands..."
$HOME/start-openhands.sh

# Starte Ollama-MCP-Bridge im Hintergrund
log_info "Starte Ollama-MCP-Bridge..."
$HOME/start-ollama-bridge.sh &
OLLAMA_BRIDGE_PID=\$!

log_info "Alle Dienste wurden gestartet!"
log_info "OpenHands ist unter http://localhost:${OPENHANDS_PORT} erreichbar."
log_info "OpenHands MCP ist unter http://localhost:${OPENHANDS_PORT}/mcp erreichbar."
log_info "Ollama-MCP-Bridge ist unter http://localhost:${OLLAMA_PORT}/mcp erreichbar."
log_info "Drücke STRG+C, um alle Dienste zu beenden."

# Warte auf Benutzerunterbrechung
trap "echo 'Stoppe Dienste...'; kill \$OLLAMA_BRIDGE_PID; docker compose -f '$HOME/openhands-docker-compose.yml' down; echo 'Alle Dienste gestoppt.'" INT
wait
EOF
        chmod +x "$HOME/start-all-mcp.sh"
    fi
    
    log "Start-Skripte erstellt."
    return 0
}

# Funktion zum Installieren der MCP-Server
install_mcp_servers() {
    info "Installiere MCP-Server..."
    
    # Prüfe, ob npm installiert ist
    if ! command -v npm &> /dev/null; then
        error "npm ist nicht installiert. Bitte installieren Sie npm."
        return 1
    fi
    
    # Installiere MCP-Server
    npm install -g @modelcontextprotocol/inspector
    npm install -g @modelcontextprotocol/server-filesystem
    npm install -g @modelcontextprotocol/server-brave-search
    npm install -g @modelcontextprotocol/server-github
    npm install -g @modelcontextprotocol/server-memory
    npm install -g @modelcontextprotocol/server-everything
    
    log "MCP-Server installiert."
    return 0
}

# Funktion zum Installieren der Ollama-MCP-Bridge
install_ollama_bridge() {
    info "Installiere Ollama-MCP-Bridge..."
    
    # Prüfe, ob git installiert ist
    if ! command -v git &> /dev/null; then
        error "git ist nicht installiert. Bitte installieren Sie git."
        return 1
    fi
    
    # Prüfe, ob npm installiert ist
    if ! command -v npm &> /dev/null; then
        error "npm ist nicht installiert. Bitte installieren Sie npm."
        return 1
    fi
    
    # Installiere TypeScript global
    npm install -g typescript
    
    # Klone und baue Ollama-MCP-Bridge
    if [ ! -d "$HOME/ollama-mcp-bridge" ]; then
        git clone https://github.com/patruff/ollama-mcp-bridge.git "$HOME/ollama-mcp-bridge"
        cd "$HOME/ollama-mcp-bridge"
        npm install
        npm run build
    else
        log "Ollama-MCP-Bridge ist bereits installiert."
    fi
    
    # Erstelle Ollama-MCP-Bridge Konfiguration
    cat > "$HOME/ollama-mcp-bridge/bridge_config.json" << EOF
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY:-""}"
      }
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN:-""}"
      }
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    }
  },
  "llm": {
    "model": "${OLLAMA_MODEL}",
    "baseUrl": "${OLLAMA_BASE_URL}"
  }
}
EOF
    
    log "Ollama-MCP-Bridge installiert und konfiguriert."
    return 0
}