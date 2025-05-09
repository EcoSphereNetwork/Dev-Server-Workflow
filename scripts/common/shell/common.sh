#!/bin/bash
# Gemeinsame Shell-Bibliothek für das Dev-Server-Workflow-Projekt
# Diese Bibliothek enthält gemeinsame Funktionen für alle Shell-Skripte

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
if [[ -z "${BASE_DIR:-}" ]]; then
    # Wenn BASE_DIR nicht gesetzt ist, setze es auf das Verzeichnis des Projekts
    export BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"
fi

# Verzeichnisse
export SCRIPTS_DIR="${BASE_DIR}/scripts"
export COMMON_DIR="${SCRIPTS_DIR}/common"
export SHELL_LIB_DIR="${COMMON_DIR}/shell"
export PYTHON_LIB_DIR="${COMMON_DIR}/python"
export SRC_DIR="${BASE_DIR}/src"
export LOGS_DIR="${BASE_DIR}/logs"
export CONFIG_DIR="${BASE_DIR}/config"
export DATA_DIR="${BASE_DIR}/data"
export DOCKER_DIR="${BASE_DIR}/docker-mcp-servers"

# Erstelle Verzeichnisse, falls sie nicht existieren
mkdir -p "${LOGS_DIR}" "${CONFIG_DIR}" "${DATA_DIR}"

# Farben für die Ausgabe
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[0;33m'
export BLUE='\033[0;34m'
export PURPLE='\033[0;35m'
export CYAN='\033[0;36m'
export NC='\033[0m' # No Color

# Log-Level
export LOG_DEBUG=0
export LOG_INFO=1
export LOG_WARN=2
export LOG_ERROR=3

# Aktuelles Log-Level (Standard: INFO)
export CURRENT_LOG_LEVEL=${LOG_INFO}

# Setze Log-Level aus Umgebungsvariable, falls verfügbar
if [[ -n "${LOG_LEVEL:-}" ]]; then
    case "${LOG_LEVEL}" in
        debug) export CURRENT_LOG_LEVEL=${LOG_DEBUG} ;;
        info) export CURRENT_LOG_LEVEL=${LOG_INFO} ;;
        warn) export CURRENT_LOG_LEVEL=${LOG_WARN} ;;
        error) export CURRENT_LOG_LEVEL=${LOG_ERROR} ;;
    esac
fi

# Aktuelle Operation für Fehlerbehandlung
export CURRENT_OPERATION=""
export CURRENT_CONTAINER=""
export CURRENT_COMPONENT=""
export ERROR_LOG_FILE="${LOGS_DIR}/error.log"

# Erstelle Log-Verzeichnis, falls es nicht existiert
mkdir -p "$(dirname "$ERROR_LOG_FILE")"

# Fehlercodes
declare -A ERROR_CODES=(
    ["SUCCESS"]=0
    ["GENERAL_ERROR"]=1
    ["INVALID_ARGUMENT"]=2
    ["FILE_NOT_FOUND"]=3
    ["PERMISSION_DENIED"]=4
    ["COMMAND_NOT_FOUND"]=5
    ["NETWORK_ERROR"]=6
    ["TIMEOUT"]=7
    ["CONTAINER_ERROR"]=10
    ["DOCKER_ERROR"]=11
    ["CONFIG_ERROR"]=20
    ["DEPENDENCY_ERROR"]=30
    ["VALIDATION_ERROR"]=40
    ["UNKNOWN_ERROR"]=99
)

# Logging-Funktionen
log_debug() {
    if [[ ${CURRENT_LOG_LEVEL} -le ${LOG_DEBUG} ]]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
        echo "[$(date +"%Y-%m-%d %H:%M:%S")] DEBUG: $1" >> "${LOGS_DIR}/debug.log"
    fi
}

log_info() {
    if [[ ${CURRENT_LOG_LEVEL} -le ${LOG_INFO} ]]; then
        echo -e "${GREEN}[INFO]${NC} $1"
        echo "[$(date +"%Y-%m-%d %H:%M:%S")] INFO: $1" >> "${LOGS_DIR}/info.log"
    fi
}

log_warn() {
    if [[ ${CURRENT_LOG_LEVEL} -le ${LOG_WARN} ]]; then
        echo -e "${YELLOW}[WARN]${NC} $1"
        echo "[$(date +"%Y-%m-%d %H:%M:%S")] WARN: $1" >> "${LOGS_DIR}/warn.log"
    fi
}

log_error() {
    if [[ ${CURRENT_LOG_LEVEL} -le ${LOG_ERROR} ]]; then
        echo -e "${RED}[ERROR]${NC} $1"
        echo "[$(date +"%Y-%m-%d %H:%M:%S")] ERROR: $1" >> "${LOGS_DIR}/error.log"
    fi
}

# Alias für Kompatibilität mit älteren Skripten
debug() { log_debug "$1"; }
info() { log_info "$1"; }
warn() { log_warn "$1"; }
error() { log_error "$1"; }
log() { log_info "$1"; }

# Fehlerbehandlung
handle_error() {
    local exit_code=$1
    local line_number=$2
    local command="$3"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    # Logge den Fehler
    log_error "Befehl '$command' in Zeile $line_number fehlgeschlagen mit Code $exit_code"
    echo "[$timestamp] ERROR: Befehl '$command' in Zeile $line_number fehlgeschlagen mit Code $exit_code" >> "$ERROR_LOG_FILE"

    # Führe Rollback-Aktionen basierend auf der aktuellen Operation durch
    case "$CURRENT_OPERATION" in
        "start_container")
            log_warn "Rollback: Stoppe fehlgeschlagenen Container: $CURRENT_CONTAINER"
            echo "[$timestamp] ROLLBACK: Stoppe fehlgeschlagenen Container: $CURRENT_CONTAINER" >> "$ERROR_LOG_FILE"
            docker stop "$CURRENT_CONTAINER" 2>/dev/null || true
            ;;
        "install_component")
            log_warn "Rollback: Entferne fehlgeschlagene Installation: $CURRENT_COMPONENT"
            echo "[$timestamp] ROLLBACK: Entferne fehlgeschlagene Installation: $CURRENT_COMPONENT" >> "$ERROR_LOG_FILE"
            # Füge spezifische Rollback-Logik hier ein
            ;;
        "update_config")
            log_warn "Rollback: Stelle vorherige Konfiguration wieder her"
            echo "[$timestamp] ROLLBACK: Stelle vorherige Konfiguration wieder her" >> "$ERROR_LOG_FILE"
            # Füge spezifische Rollback-Logik hier ein
            ;;
        "network_operation")
            log_warn "Rollback: Bereinige Netzwerkressourcen"
            echo "[$timestamp] ROLLBACK: Bereinige Netzwerkressourcen" >> "$ERROR_LOG_FILE"
            # Füge spezifische Rollback-Logik hier ein
            ;;
        "docker_compose_down")
            log_warn "Docker Compose down fehlgeschlagen. Versuche, Container zu stoppen..."
            if command -v docker &> /dev/null; then
                docker stop $(docker ps -q --filter "name=mcp-") 2>/dev/null || true
            fi
            ;;
        *)
            log_info "Keine spezifische Rollback-Aktion definiert für Operation: $CURRENT_OPERATION"
            echo "[$timestamp] INFO: Keine spezifische Rollback-Aktion definiert für Operation: $CURRENT_OPERATION" >> "$ERROR_LOG_FILE"
            ;;
    esac

    return $exit_code
}

# Funktion zum Setzen der aktuellen Operation
set_operation() {
    CURRENT_OPERATION="$1"
    log_info "Starte Operation: $CURRENT_OPERATION"
}

# Funktion zum Setzen des aktuellen Containers
set_container() {
    CURRENT_CONTAINER="$1"
    log_info "Arbeite mit Container: $CURRENT_CONTAINER"
}

# Funktion zum Setzen der aktuellen Komponente
set_component() {
    CURRENT_COMPONENT="$1"
    log_info "Arbeite mit Komponente: $CURRENT_COMPONENT"
}

# Funktion zum Überprüfen, ob ein Befehl verfügbar ist
check_command() {
    local cmd="$1"
    local install_hint="${2:-}"
    
    if ! command -v "$cmd" &> /dev/null; then
        log_error "Benötigter Befehl nicht gefunden: $cmd"
        if [[ -n "$install_hint" ]]; then
            log_warn "Hinweis: $install_hint"
        fi
        return ${ERROR_CODES["COMMAND_NOT_FOUND"]}
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Funktion zum Überprüfen, ob eine Datei existiert
check_file() {
    local file="$1"
    local create="${2:-false}"
    
    if [[ ! -f "$file" ]]; then
        if [[ "$create" == "true" ]]; then
            log_warn "Datei nicht gefunden, erstelle: $file"
            touch "$file" || return ${ERROR_CODES["PERMISSION_DENIED"]}
        else
            log_error "Benötigte Datei nicht gefunden: $file"
            return ${ERROR_CODES["FILE_NOT_FOUND"]}
        fi
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Funktion zum Überprüfen, ob ein Verzeichnis existiert
check_directory() {
    local dir="$1"
    local create="${2:-false}"
    
    if [[ ! -d "$dir" ]]; then
        if [[ "$create" == "true" ]]; then
            log_warn "Verzeichnis nicht gefunden, erstelle: $dir"
            mkdir -p "$dir" || return ${ERROR_CODES["PERMISSION_DENIED"]}
        else
            log_error "Benötigtes Verzeichnis nicht gefunden: $dir"
            return ${ERROR_CODES["FILE_NOT_FOUND"]}
        fi
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Funktion zum Validieren einer Eingabe
validate_input() {
    local input="$1"
    local pattern="$2"
    local error_message="${3:-Ungültiges Eingabeformat}"
    
    if [[ ! "$input" =~ $pattern ]]; then
        log_error "$error_message"
        return ${ERROR_CODES["VALIDATION_ERROR"]}
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Funktion zum Ausführen eines Befehls mit Timeout
execute_with_timeout() {
    local timeout="$1"
    local cmd="${@:2}"
    
    # Überprüfe, ob der timeout-Befehl existiert
    if ! command -v timeout &> /dev/null; then
        log_warn "'timeout'-Befehl nicht gefunden, führe ohne Timeout aus"
        $cmd
        return $?
    fi
    
    timeout "$timeout" $cmd
    local exit_code=$?
    
    if [[ $exit_code -eq 124 ]]; then
        log_error "Befehl nach $timeout Sekunden abgebrochen: $cmd"
        return ${ERROR_CODES["TIMEOUT"]}
    fi
    
    return $exit_code
}

# Docker-Funktionen
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut."
        log_info "Sie können Docker mit folgendem Befehl installieren:"
        log_info "curl -fsSL https://get.docker.com | sh"
        return 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker-Daemon läuft nicht. Bitte starten Sie den Docker-Daemon und versuchen Sie es erneut."
        return 1
    fi

    log_debug "Docker ist installiert und läuft."
    return 0
}

check_docker_compose() {
    log_info "Überprüfe Docker Compose-Installation..."
    
    # Prüfe zunächst das neue Docker-Compose-Plugin
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log_info "Docker Compose Plugin ist installiert."
        
        # Versuche, die Version zu ermitteln
        local docker_compose_version
        docker_compose_version=$(docker compose version --short 2>/dev/null || echo "")
        
        if [ -n "$docker_compose_version" ]; then
            log_info "Docker Compose Version: $docker_compose_version"

            # Vergleiche mit der Mindestversion
            if [ "$(printf '%s\n' "1.29.0" "$docker_compose_version" | sort -V | head -n1)" != "1.29.0" ]; then
                log_info "Docker Compose ist ausreichend aktuell."
                return 0
            else
                log_warn "Docker Compose Version ist älter als 1.29.0. Ein Update wird empfohlen."
                # Aber wir können es trotzdem nutzen
                return 0
            fi
        fi
    fi
    
    # Prüfe das alte docker-compose-Kommando
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose (Standalone) ist installiert."
        
        # Versuche, die Version zu ermitteln
        local docker_compose_version
        docker_compose_version=$(docker-compose version --short 2>/dev/null || echo "")
        
        if [ -n "$docker_compose_version" ]; then
            log_info "Docker Compose Version: $docker_compose_version"
            return 0
        fi
    fi

    # Wenn wir hier ankommen, fehlt Docker Compose
    log_error "Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut."
    log_error "Sie können Docker Compose mit folgendem Befehl installieren:"
    log_error "sudo apt-get install docker-compose-plugin"
    return 1
}

start_docker_daemon() {
    if docker info &> /dev/null; then
        log_debug "Docker-Daemon läuft bereits."
        return 0
    fi

    log_info "Starte Docker-Daemon..."
    
    # Versuche, den Docker-Daemon zu starten
    if command -v systemctl &> /dev/null; then
        log_debug "Verwende systemctl zum Starten des Docker-Daemons..."
        sudo systemctl start docker
    elif command -v service &> /dev/null; then
        log_debug "Verwende service zum Starten des Docker-Daemons..."
        sudo service docker start
    else
        log_debug "Starte Docker-Daemon im Hintergrund..."
        sudo dockerd > /dev/null 2>&1 &
        sleep 5
    fi

    # Überprüfe, ob der Docker-Daemon jetzt läuft
    if docker info &> /dev/null; then
        log_info "Docker-Daemon erfolgreich gestartet."
        return 0
    else
        log_error "Konnte Docker-Daemon nicht starten."
        return 1
    fi
}

check_container_running() {
    local container_name="$1"
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

check_container_exists() {
    local container_name="$1"
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

start_container() {
    local container_name="$1"
    local image_name="$2"
    local port_mapping="$3"
    local environment="$4"
    local volume_mapping="$5"
    local network="$6"
    
    if check_container_running "${container_name}"; then
        log_info "Container ${container_name} läuft bereits"
        return 0
    fi
    
    if check_container_exists "${container_name}"; then
        log_debug "Starte existierenden Container ${container_name}"
        docker start "${container_name}"
        return $?
    fi
    
    log_debug "Erstelle und starte Container ${container_name}"
    
    local cmd="docker run -d --name ${container_name}"
    
    if [[ -n "${port_mapping}" ]]; then
        cmd="${cmd} ${port_mapping}"
    fi
    
    if [[ -n "${environment}" ]]; then
        cmd="${cmd} ${environment}"
    fi
    
    if [[ -n "${volume_mapping}" ]]; then
        cmd="${cmd} ${volume_mapping}"
    fi
    
    if [[ -n "${network}" ]]; then
        cmd="${cmd} --network ${network}"
    fi
    
    cmd="${cmd} ${image_name}"
    
    log_debug "Führe Befehl aus: ${cmd}"
    eval "${cmd}"
    return $?
}

stop_container() {
    local container_name="$1"
    
    if ! check_container_running "${container_name}"; then
        log_info "Container ${container_name} läuft nicht"
        return 0
    fi
    
    log_debug "Stoppe Container ${container_name}"
    docker stop "${container_name}"
    return $?
}

# Funktion zum Starten der Docker Compose MCP-Server
start_docker_mcp_servers() {
    log_info "Starte Docker Compose MCP-Server..."
    
    # Überprüfe, ob das Docker-Compose-File existiert
    if [ ! -f "${DOCKER_DIR}/docker-compose.yml" ]; then
        log_error "Docker-Compose-Datei nicht gefunden: ${DOCKER_DIR}/docker-compose.yml"
        return 1
    fi
    
    # Setze aktuelle Operation
    set_operation "docker_compose_up"
    
    # Wechsle in das MCP-Servers-Verzeichnis und starte die Container
    cd "${DOCKER_DIR}"
    
    # Verwende docker-compose oder docker compose, je nachdem, was verfügbar ist
    if command -v docker-compose &> /dev/null; then
        log_info "Verwende docker-compose..."
        docker-compose up -d
    else
        log_info "Verwende docker compose..."
        docker compose up -d
    fi
    
    if [ $? -eq 0 ]; then
        log_info "Docker Compose MCP-Server erfolgreich gestartet."
        return 0
    else
        log_error "Fehler beim Starten der Docker Compose MCP-Server."
        return 1
    fi
}

# Funktion zum Stoppen der Docker Compose MCP-Server
stop_docker_mcp_servers() {
    log_info "Stoppe Docker Compose MCP-Server..."
    
    # Überprüfe, ob das Docker-Compose-File existiert
    if [ ! -f "${DOCKER_DIR}/docker-compose.yml" ]; then
        log_warn "Docker-Compose-Datei nicht gefunden: ${DOCKER_DIR}/docker-compose.yml"
        log_warn "Es sind möglicherweise keine Docker Compose MCP-Server gestartet."
        return 0
    fi
    
    # Setze aktuelle Operation
    set_operation "docker_compose_down"
    set_container "all"
    
    # Wechsle in das MCP-Servers-Verzeichnis und stoppe die Container
    cd "${DOCKER_DIR}"
    
    # Verwende docker-compose oder docker compose, je nachdem, was verfügbar ist
    if command -v docker-compose &> /dev/null; then
        log_info "Verwende docker-compose..."
        docker-compose down
    else
        log_info "Verwende docker compose..."
        docker compose down
    fi
    
    if [ $? -eq 0 ]; then
        log_info "Docker Compose MCP-Server erfolgreich gestoppt."
        return 0
    else
        log_error "Fehler beim Stoppen der Docker Compose MCP-Server."
        return 1
    fi
}

# Funktion zum Starten eines MCP-Servers
start_mcp_server() {
    local server_name="$1"
    local command="$2"
    local args="${@:3}"
    
    log_info "Starte MCP-Server: $server_name"
    
    # Erstelle Log-Verzeichnis, falls es nicht existiert
    mkdir -p "$LOGS_DIR"
    
    # Setze aktuelle Operation
    set_operation "start_mcp_server"
    set_component "$server_name"
    
    # Starte den MCP-Server
    log_debug "Starte MCP-Server mit Befehl: $command $args"
    nohup $command $args > "$LOGS_DIR/${server_name}.log" 2>&1 &
    
    # Speichere die PID
    echo $! > "$LOGS_DIR/${server_name}.pid"
    
    log_info "MCP-Server $server_name gestartet (PID: $(cat "$LOGS_DIR/${server_name}.pid"))"
    return 0
}

# Funktion zum Stoppen eines MCP-Servers
stop_mcp_server() {
    local server_name="$1"
    
    log_info "Stoppe MCP-Server: $server_name"
    
    # Setze aktuelle Operation
    set_operation "stop_mcp_server"
    set_component "$server_name"
    
    # Überprüfe, ob die PID-Datei existiert
    if [ ! -f "$LOGS_DIR/${server_name}.pid" ]; then
        log_warn "PID-Datei für MCP-Server $server_name nicht gefunden."
        return 0
    fi
    
    # Hole die PID
    local pid
    pid=$(cat "$LOGS_DIR/${server_name}.pid")
    
    # Überprüfe, ob der Prozess läuft
    if ! ps -p "$pid" > /dev/null; then
        log_warn "MCP-Server $server_name läuft nicht (PID: $pid)."
        rm -f "$LOGS_DIR/${server_name}.pid"
        return 0
    fi
    
    # Stoppe den Prozess
    log_debug "Beende Prozess mit PID $pid..."
    kill "$pid"
    
    # Warte kurz und überprüfe, ob der Prozess beendet wurde
    sleep 1
    if ps -p "$pid" > /dev/null; then
        log_warn "Prozess reagiert nicht, verwende SIGKILL..."
        kill -9 "$pid"
    fi
    
    # Entferne die PID-Datei
    rm -f "$LOGS_DIR/${server_name}.pid"
    
    log_info "MCP-Server $server_name gestoppt."
    return 0
}

# Funktion zum Starten des n8n MCP-Servers
start_n8n_mcp_server() {
    log_info "Starte n8n MCP-Server..."
    
    # Überprüfe, ob die Umgebungsvariablen gesetzt sind
    if [ -z "${N8N_URL:-}" ]; then
        export N8N_URL="http://localhost:5678"
        log_warn "N8N_URL nicht gesetzt, verwende Standard: $N8N_URL"
    fi
    
    if [ -z "${N8N_API_KEY:-}" ]; then
        log_warn "N8N_API_KEY nicht gesetzt, n8n MCP-Server könnte nicht korrekt funktionieren."
    fi
    
    # Überprüfe, ob das Skript existiert
    if [ -f "${SRC_DIR}/n8n_mcp_server.py" ]; then
        log_debug "Verwende n8n_mcp_server.py..."
        python3 "${SRC_DIR}/n8n_mcp_server.py" --n8n-url "${N8N_URL}" --api-key "${N8N_API_KEY:-}" ${VERBOSE_FLAG:-} &
        echo $! > "$LOGS_DIR/n8n_mcp_server.pid"
        log_info "n8n MCP-Server gestartet (PID: $(cat "$LOGS_DIR/n8n_mcp_server.pid"))"
    elif [ -f "${SRC_DIR}/mcp/n8n_mcp_server.py" ]; then
        log_debug "Verwende mcp/n8n_mcp_server.py..."
        python3 "${SRC_DIR}/mcp/n8n_mcp_server.py" --n8n-url "${N8N_URL}" --api-key "${N8N_API_KEY:-}" ${VERBOSE_FLAG:-} &
        echo $! > "$LOGS_DIR/n8n_mcp_server.pid"
        log_info "n8n MCP-Server gestartet (PID: $(cat "$LOGS_DIR/n8n_mcp_server.pid"))"
    else
        log_error "n8n MCP-Server-Skript nicht gefunden. Der n8n MCP-Server wurde nicht gestartet."
        return 1
    fi
    
    return 0
}

# Funktion zum Starten des OpenHands MCP-Servers
start_openhands_mcp_server() {
    log_info "Starte OpenHands MCP-Server..."
    
    # Überprüfe, ob die Umgebungsvariablen gesetzt sind
    if [ -z "${OPENHANDS_PORT:-}" ]; then
        export OPENHANDS_PORT="3000"
        log_warn "OPENHANDS_PORT nicht gesetzt, verwende Standard: $OPENHANDS_PORT"
    fi
    
    if [ -z "${OPENHANDS_MAX_WORKERS:-}" ]; then
        export OPENHANDS_MAX_WORKERS="5"
        log_warn "OPENHANDS_MAX_WORKERS nicht gesetzt, verwende Standard: $OPENHANDS_MAX_WORKERS"
    fi
    
    # Überprüfe, ob das Skript existiert
    if [ -f "${SRC_DIR}/openhands_mcp_server.py" ]; then
        log_debug "Verwende openhands_mcp_server.py..."
        python3 "${SRC_DIR}/openhands_mcp_server.py" --port "${OPENHANDS_PORT}" --max-workers "${OPENHANDS_MAX_WORKERS}" ${VERBOSE_FLAG:-} &
        echo $! > "$LOGS_DIR/openhands_mcp_server.pid"
        log_info "OpenHands MCP-Server gestartet (PID: $(cat "$LOGS_DIR/openhands_mcp_server.pid"))"
    elif [ -f "${SRC_DIR}/mcp/openhands_server.py" ]; then
        log_debug "Verwende mcp/openhands_server.py..."
        python3 "${SRC_DIR}/mcp/openhands_server.py" --port "${OPENHANDS_PORT}" --max-workers "${OPENHANDS_MAX_WORKERS}" ${VERBOSE_FLAG:-} &
        echo $! > "$LOGS_DIR/openhands_mcp_server.pid"
        log_info "OpenHands MCP-Server gestartet (PID: $(cat "$LOGS_DIR/openhands_mcp_server.pid"))"
    else
        log_error "OpenHands MCP-Server-Skript nicht gefunden. Der OpenHands MCP-Server wurde nicht gestartet."
        return 1
    fi
    
    return 0
}

# Funktion zum Überprüfen der Python-Abhängigkeiten
check_python_dependencies() {
    log_info "Überprüfe Python-Abhängigkeiten..."
    
    # Überprüfe, ob Python installiert ist
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 ist nicht installiert. Bitte installieren Sie Python 3 und versuchen Sie es erneut."
        return 1
    fi
    
    # Liste der benötigten Python-Pakete
    local required_packages=("aiohttp" "pyyaml" "requests" "python-dotenv")
    local missing_packages=()
    
    # Überprüfe, ob die benötigten Pakete installiert sind
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    # Installiere fehlende Pakete
    if [ ${#missing_packages[@]} -gt 0 ]; then
        log_warn "Folgende Python-Pakete fehlen: ${missing_packages[*]}"
        log_info "Installiere fehlende Pakete..."
        
        python3 -m pip install "${missing_packages[@]}" || {
            log_error "Fehler beim Installieren der Python-Pakete."
            return 1
        }
    fi
    
    log_info "Alle Python-Abhängigkeiten sind installiert."
    return 0
}

# Funktion zum Erstellen der Log-Verzeichnisse
create_log_directories() {
    log_debug "Erstelle Log-Verzeichnisse..."
    
    # Erstelle das Log-Verzeichnis, falls es nicht existiert
    mkdir -p "$LOGS_DIR"
    
    # Erstelle Unterverzeichnisse für verschiedene Komponenten
    mkdir -p "$LOGS_DIR/n8n"
    mkdir -p "$LOGS_DIR/openhands"
    mkdir -p "$LOGS_DIR/docker"
    mkdir -p "$LOGS_DIR/mcp"
    
    log_debug "Log-Verzeichnisse erstellt."
    return 0
}

# Funktion zum Laden von Umgebungsvariablen aus einer .env-Datei
load_env_file() {
    local env_file="${1:-.env}"
    
    log_debug "Lade Umgebungsvariablen aus $env_file..."
    
    # Überprüfe, ob die Datei existiert
    if [ ! -f "$env_file" ]; then
        log_warn "Umgebungsvariablendatei $env_file nicht gefunden."
        return 1
    fi
    
    # Lade die Umgebungsvariablen
    while IFS='=' read -r key value; do
        # Überspringe Kommentare und leere Zeilen
        [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
        
        # Entferne Anführungszeichen aus dem Wert
        value="${value%\"}"
        value="${value#\"}"
        value="${value%\'}"
        value="${value#\'}"
        
        # Exportiere die Variable
        export "$key=$value"
        log_debug "Umgebungsvariable geladen: $key"
    done < "$env_file"
    
    log_info "Umgebungsvariablen aus $env_file geladen."
    return 0
}

# Funktion zum Speichern von Umgebungsvariablen in eine .env-Datei
save_env_file() {
    local env_file="${1:-.env}"
    local variables=("${@:2}")
    
    log_debug "Speichere Umgebungsvariablen in $env_file..."
    
    # Erstelle ein Backup der vorhandenen Datei, falls sie existiert
    if [ -f "$env_file" ]; then
        cp "$env_file" "${env_file}.bak"
        log_debug "Backup erstellt: ${env_file}.bak"
    fi
    
    # Schreibe die Umgebungsvariablen in die Datei
    echo "# Umgebungsvariablen für das Dev-Server-Workflow-Projekt" > "$env_file"
    echo "# Automatisch generiert am $(date)" >> "$env_file"
    echo "" >> "$env_file"
    
    for var in "${variables[@]}"; do
        if [ -n "${!var:-}" ]; then
            echo "$var=${!var}" >> "$env_file"
        fi
    done
    
    log_info "Umgebungsvariablen in $env_file gespeichert."
    return 0
}

# Funktion zum Erstellen einer OpenHands-Konfiguration
create_openhands_config() {
    local config_file="${1:-${CONFIG_DIR}/openhands-config.json}"
    
    log_info "Erstelle OpenHands-Konfiguration in $config_file..."
    
    # Erstelle das Verzeichnis, falls es nicht existiert
    mkdir -p "$(dirname "$config_file")"
    
    # Erstelle die Konfigurationsdatei
    cat > "$config_file" << EOF
{
  "api": {
    "port": ${OPENHANDS_PORT:-3000},
    "host": "0.0.0.0",
    "api_key": "${OPENHANDS_API_KEY:-}"
  },
  "llm": {
    "provider": "${LLM_PROVIDER:-ollama}",
    "api_key": "${LLM_API_KEY:-}",
    "model": "${LLM_MODEL:-qwen2.5-coder:7b-instruct}",
    "base_url": "${LLM_BASE_URL:-http://localhost:11434/api}"
  },
  "mcp": {
    "enabled": true,
    "servers": [
      {
        "name": "n8n",
        "url": "http://localhost:${MCP_PORT:-3333}",
        "auth_token": "${MCP_AUTH_TOKEN:-}"
      }
    ]
  },
  "workspace": {
    "path": "${OPENHANDS_WORKSPACE_DIR:-$HOME/openhands-workspace}",
    "max_workers": ${OPENHANDS_MAX_WORKERS:-5}
  },
  "logging": {
    "level": "${LOG_LEVEL:-info}",
    "file": "${LOGS_DIR}/openhands.log"
  }
}
EOF
    
    log_info "OpenHands-Konfiguration erstellt: $config_file"
    return 0
}

# Funktion zum Erstellen einer Claude-Konfiguration
create_claude_config() {
    local config_file="${1:-${CONFIG_DIR}/claude-config.json}"
    
    log_info "Erstelle Claude-Konfiguration in $config_file..."
    
    # Erstelle das Verzeichnis, falls es nicht existiert
    mkdir -p "$(dirname "$config_file")"
    
    # Erstelle die Konfigurationsdatei
    cat > "$config_file" << EOF
{
  "api": {
    "key": "${CLAUDE_API_KEY:-}",
    "model": "${CLAUDE_MODEL:-claude-3-5-sonnet-20240620}",
    "base_url": "${CLAUDE_BASE_URL:-https://api.anthropic.com/v1}"
  },
  "parameters": {
    "temperature": ${CLAUDE_TEMPERATURE:-0.7},
    "max_tokens": ${CLAUDE_MAX_TOKENS:-4096},
    "top_p": ${CLAUDE_TOP_P:-0.9}
  },
  "system_prompt": "${CLAUDE_SYSTEM_PROMPT:-Du bist Claude, ein KI-Assistent von Anthropic. Du hilfst Benutzern bei der Lösung von Problemen und beantwortest Fragen.}"
}
EOF
    
    log_info "Claude-Konfiguration erstellt: $config_file"
    return 0
}

# Funktion zum Erstellen von Start-Skripten
create_start_scripts() {
    log_info "Erstelle Start-Skripte..."
    
    # Erstelle das Skript zum Starten der MCP-Server
    cat > "${BASE_DIR}/start-mcp-servers.sh" << 'EOF'
#!/bin/bash

# Skript zum Starten der MCP-Server
# Verwendet die gemeinsame Bibliothek für konsistente Funktionen und Konfigurationen

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

# Standardwerte für Kommandozeilenargumente
START_ALL=false
START_N8N=false
START_OPENHANDS=false
START_GENERATOR=false
VERBOSE_FLAG=""
GENERATOR_SERVERS_DIR=${GENERATOR_SERVERS_DIR:-"generated_servers"}

# Funktion zum Anzeigen von Hilfe
show_help() {
    echo -e "${BLUE}MCP-Server Starter${NC}"
    echo "Dieses Skript startet die MCP-Server für das Dev-Server-Workflow-Projekt."
    echo ""
    echo "Verwendung:"
    echo "  $0 [Optionen]"
    echo ""
    echo "Optionen:"
    echo "  -h, --help                Zeigt diese Hilfe an"
    echo "  -n, --n8n-url URL         URL der n8n-Instanz (Standard: $N8N_URL)"
    echo "  -k, --api-key KEY         API-Schlüssel für n8n"
    echo "  -w, --max-workers N       Maximale Anzahl von Worker-Threads für OpenHands (Standard: $OPENHANDS_MAX_WORKERS)"
    echo "  -d, --servers-dir DIR     Verzeichnis für generierte Server (Standard: $GENERATOR_SERVERS_DIR)"
    echo "  -v, --verbose             Ausführliche Ausgabe"
    echo "  -a, --all                 Alle MCP-Server starten"
    echo "  --n8n                     n8n MCP-Server starten"
    echo "  --openhands               OpenHands MCP-Server starten"
    echo "  --generator               MCP-Server-Generator starten"
    echo ""
    echo "Umgebungsvariablen:"
    echo "  N8N_URL                   URL der n8n-Instanz"
    echo "  N8N_API_KEY               API-Schlüssel für n8n"
    echo "  OPENHANDS_MAX_WORKERS     Maximale Anzahl von Worker-Threads für OpenHands"
    echo "  GENERATOR_SERVERS_DIR     Verzeichnis für generierte Server"
    echo ""
    echo "Beispiel:"
    echo "  $0 --all -k my-api-key"
    echo "  $0 --n8n --openhands -k my-api-key -w 10"
}

# Funktion zum Start des MCP-Server-Generators
start_generator_mcp_server() {
    info "Starte MCP-Server-Generator..."
    
    # Erstelle das Verzeichnis für generierte Server, falls es nicht existiert
    mkdir -p "$GENERATOR_SERVERS_DIR"
    
    # Überprüfe, ob das Skript existiert
    if [ -f "${BASE_DIR}/src/generator_mcp_server.py" ]; then
        log "Verwende generator_mcp_server.py..."
        python3 "${BASE_DIR}/src/generator_mcp_server.py" --servers-dir "$GENERATOR_SERVERS_DIR" &
        echo $! > "$LOGS_DIR/generator_mcp_server.pid"
        log "MCP-Server-Generator gestartet (PID: $(cat "$LOGS_DIR/generator_mcp_server.pid"))"
    elif [ -f "${BASE_DIR}/src/generator-mcp-server.py" ]; then
        log "Verwende generator-mcp-server.py..."
        python3 "${BASE_DIR}/src/generator-mcp-server.py" --servers-dir "$GENERATOR_SERVERS_DIR" &
        echo $! > "$LOGS_DIR/generator_mcp_server.pid"
        log "MCP-Server-Generator gestartet (PID: $(cat "$LOGS_DIR/generator_mcp_server.pid"))"
    elif [ -f "${BASE_DIR}/src/mcp/generator_server.py" ]; then
        log "Verwende mcp/generator_server.py..."
        python3 "${BASE_DIR}/src/mcp/generator_server.py" --servers-dir "$GENERATOR_SERVERS_DIR" &
        echo $! > "$LOGS_DIR/generator_mcp_server.pid"
        log "MCP-Server-Generator gestartet (PID: $(cat "$LOGS_DIR/generator_mcp_server.pid"))"
    else
        warn "MCP-Server-Generator-Skript nicht gefunden. Der MCP-Server-Generator wurde nicht gestartet."
        return 1
    fi
    
    return 0
}

# Parse Kommandozeilenargumente
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -n|--n8n-url)
            N8N_URL="$2"
            shift 2
            ;;
        -k|--api-key)
            N8N_API_KEY="$2"
            shift 2
            ;;
        -w|--max-workers)
            OPENHANDS_MAX_WORKERS="$2"
            shift 2
            ;;
        -d|--servers-dir)
            GENERATOR_SERVERS_DIR="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE_FLAG="--verbose"
            shift
            ;;
        -a|--all)
            START_ALL=true
            shift
            ;;
        --n8n)
            START_N8N=true
            shift
            ;;
        --openhands)
            START_OPENHANDS=true
            shift
            ;;
        --generator)
            START_GENERATOR=true
            shift
            ;;
        *)
            error "Unbekannte Option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Hauptfunktion
main() {
    info "=== Starte MCP-Server ==="
    
    # Prüfe Abhängigkeiten
    check_docker || exit 1
    check_docker_compose || exit 1
    start_docker_daemon || exit 1
    check_python_dependencies || exit 1
    create_log_directories
    
    # Wenn keine spezifischen Server ausgewählt wurden und nicht alle gestartet werden sollen,
    # starte standardmäßig die MCP-Server mit Docker Compose
    if [ "$START_ALL" = false ] && [ "$START_N8N" = false ] && [ "$START_OPENHANDS" = false ] && [ "$START_GENERATOR" = false ]; then
        # Setze Standard auf Docker Compose MCP-Server
        info "Keine spezifischen Server ausgewählt. Starte die MCP-Server mit Docker Compose..."
        
        # Starte die MCP-Server
        start_docker_mcp_servers
        
        log "MCP Inspector UI ist verfügbar unter: http://localhost:8080"
        log "Zum Stoppen der MCP-Server verwenden Sie: stop-mcp-servers.sh"
        return 0
    fi
    
    # Starte entsprechende Server
    if [ "$START_ALL" = true ]; then
        info "Starte alle MCP-Server..."
        
        # Starte die Docker Compose MCP-Server
        start_docker_mcp_servers
        
        # Starte die anderen Server
        start_n8n_mcp_server
        start_openhands_mcp_server
        start_generator_mcp_server
    else
        # Starte nur die ausgewählten Server
        if [ "$START_N8N" = true ]; then
            start_n8n_mcp_server
        fi
        
        if [ "$START_OPENHANDS" = true ]; then
            start_openhands_mcp_server
        fi
        
        if [ "$START_GENERATOR" = true ]; then
            start_generator_mcp_server
        fi
    fi
    
    info "MCP-Server-Start abgeschlossen."
    log "MCP Inspector UI ist verfügbar unter: http://localhost:8080"
    log "Zum Stoppen der MCP-Server verwenden Sie: stop-mcp-servers.sh"
    
    return 0
}

# Führe die Hauptfunktion aus
main
EOF
    
    # Mache das Skript ausführbar
    chmod +x "${BASE_DIR}/start-mcp-servers.sh"
    
    # Erstelle das Skript zum Stoppen der MCP-Server
    cat > "${BASE_DIR}/stop-mcp-servers.sh" << 'EOF'
#!/bin/bash

# Skript zum Stoppen der MCP-Server
# Verwendet die gemeinsame Bibliothek für konsistente Funktionen und Konfigurationen

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

# Aktuelle Operation für Fehlerbehandlung
CURRENT_OPERATION=""
CURRENT_CONTAINER=""

# Funktion zum Anzeigen von Hilfe
show_help() {
    echo -e "${BLUE}MCP-Server Stopper${NC}"
    echo "Dieses Skript stoppt die MCP-Server für das Dev-Server-Workflow-Projekt."
    echo ""
    echo "Verwendung:"
    echo "  $0 [Optionen]"
    echo ""
    echo "Optionen:"
    echo "  -h, --help                Zeigt diese Hilfe an"
    echo "  -a, --all                 Alle MCP-Server stoppen"
    echo "  --docker                  Nur Docker-basierte MCP-Server stoppen"
    echo "  --n8n                     n8n MCP-Server stoppen"
    echo "  --openhands               OpenHands MCP-Server stoppen"
    echo "  --generator               MCP-Server-Generator stoppen"
    echo ""
    echo "Beispiel:"
    echo "  $0 --all"
    echo "  $0 --n8n --openhands"
}

# Funktion zum Stoppen des n8n MCP-Servers
stop_n8n_mcp_server() {
    info "Stoppe n8n MCP-Server..."
    
    local pid_file="$LOGS_DIR/n8n_mcp_server.pid"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Beende Prozess mit PID $pid..."
            kill "$pid"
            sleep 1
            
            # Überprüfe, ob der Prozess beendet wurde
            if ps -p "$pid" > /dev/null 2>&1; then
                warn "Prozess reagiert nicht, verwende SIGKILL..."
                kill -9 "$pid"
            fi
            
            log "n8n MCP-Server gestoppt."
        else
            warn "n8n MCP-Server läuft nicht (PID: $pid)."
        fi
        
        rm -f "$pid_file"
    else
        warn "n8n MCP-Server PID-Datei nicht gefunden: $pid_file"
        
        # Suche nach laufenden Python-Prozessen, die n8n_mcp_server.py ausführen
        local pids
        pids=$(pgrep -f "python3.*n8n[_-]mcp[_-]server\.py" || true)
        
        if [ -n "$pids" ]; then
            log "Gefundene n8n MCP-Server-Prozesse: $pids"
            
            for pid in $pids; do
                log "Beende Prozess mit PID $pid..."
                kill "$pid" 2>/dev/null || true
            done
            
            log "n8n MCP-Server-Prozesse beendet."
        else
            warn "Keine laufenden n8n MCP-Server-Prozesse gefunden."
        fi
    fi
    
    return 0
}

# Funktion zum Stoppen des OpenHands MCP-Servers
stop_openhands_mcp_server() {
    info "Stoppe OpenHands MCP-Server..."
    
    local pid_file="$LOGS_DIR/openhands_mcp_server.pid"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Beende Prozess mit PID $pid..."
            kill "$pid"
            sleep 1
            
            # Überprüfe, ob der Prozess beendet wurde
            if ps -p "$pid" > /dev/null 2>&1; then
                warn "Prozess reagiert nicht, verwende SIGKILL..."
                kill -9 "$pid"
            fi
            
            log "OpenHands MCP-Server gestoppt."
        else
            warn "OpenHands MCP-Server läuft nicht (PID: $pid)."
        fi
        
        rm -f "$pid_file"
    else
        warn "OpenHands MCP-Server PID-Datei nicht gefunden: $pid_file"
        
        # Suche nach laufenden Python-Prozessen, die openhands_mcp_server.py ausführen
        local pids
        pids=$(pgrep -f "python3.*openhands[_-]mcp[_-]server\.py" || true)
        
        if [ -n "$pids" ]; then
            log "Gefundene OpenHands MCP-Server-Prozesse: $pids"
            
            for pid in $pids; do
                log "Beende Prozess mit PID $pid..."
                kill "$pid" 2>/dev/null || true
            done
            
            log "OpenHands MCP-Server-Prozesse beendet."
        else
            warn "Keine laufenden OpenHands MCP-Server-Prozesse gefunden."
        fi
    fi
    
    return 0
}

# Funktion zum Stoppen des MCP-Server-Generators
stop_generator_mcp_server() {
    info "Stoppe MCP-Server-Generator..."
    
    local pid_file="$LOGS_DIR/generator_mcp_server.pid"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Beende Prozess mit PID $pid..."
            kill "$pid"
            sleep 1
            
            # Überprüfe, ob der Prozess beendet wurde
            if ps -p "$pid" > /dev/null 2>&1; then
                warn "Prozess reagiert nicht, verwende SIGKILL..."
                kill -9 "$pid"
            fi
            
            log "MCP-Server-Generator gestoppt."
        else
            warn "MCP-Server-Generator läuft nicht (PID: $pid)."
        fi
        
        rm -f "$pid_file"
    else
        warn "MCP-Server-Generator PID-Datei nicht gefunden: $pid_file"
        
        # Suche nach laufenden Python-Prozessen, die generator_mcp_server.py ausführen
        local pids
        pids=$(pgrep -f "python3.*generator[_-]mcp[_-]server\.py" || true)
        
        if [ -n "$pids" ]; then
            log "Gefundene MCP-Server-Generator-Prozesse: $pids"
            
            for pid in $pids; do
                log "Beende Prozess mit PID $pid..."
                kill "$pid" 2>/dev/null || true
            done
            
            log "MCP-Server-Generator-Prozesse beendet."
        else
            warn "Keine laufenden MCP-Server-Generator-Prozesse gefunden."
        fi
    fi
    
    # Stoppe auch alle generierten Server
    local generator_servers_dir="${BASE_DIR}/generated_servers"
    if [ -d "$generator_servers_dir" ]; then
        info "Stoppe generierte MCP-Server..."
        
        for pid_file in "$generator_servers_dir"/*/server.pid; do
            if [ -f "$pid_file" ]; then
                local pid
                pid=$(cat "$pid_file")
                local server_dir
                server_dir=$(dirname "$pid_file")
                local server_id
                server_id=$(basename "$server_dir")
                
                if ps -p "$pid" > /dev/null 2>&1; then
                    log "Beende generierten Server $server_id (PID: $pid)..."
                    kill "$pid" 2>/dev/null || true
                    
                    # Aktualisiere den Status in der Konfigurationsdatei
                    local config_file="$server_dir/config.json"
                    if [ -f "$config_file" ]; then
                        sed -i 's/"status": "running"/"status": "stopped"/g' "$config_file"
                    fi
                else
                    warn "Generierter Server $server_id läuft nicht (PID: $pid)."
                fi
                
                rm -f "$pid_file"
            fi
        done
    fi
    
    return 0
}

# Funktion zum Stoppen aller MCP-Server-Prozesse
stop_all_mcp_processes() {
    info "Stoppe alle MCP-Server-Prozesse..."
    
    # Suche nach allen Python-Prozessen, die MCP-Server ausführen
    local pids
    pids=$(pgrep -f "python3.*mcp[_-]server\.py" || true)
    
    if [ -n "$pids" ]; then
        log "Gefundene MCP-Server-Prozesse: $pids"
        
        for pid in $pids; do
            log "Beende Prozess mit PID $pid..."
            kill "$pid" 2>/dev/null || true
        done
        
        log "Alle MCP-Server-Prozesse beendet."
    else
        warn "Keine laufenden MCP-Server-Prozesse gefunden."
    fi
    
    # Bereinige PID-Dateien
    rm -f "$LOGS_DIR"/*.pid
    
    return 0
}

# Standardwerte
STOP_ALL=false
STOP_DOCKER=false
STOP_N8N=false
STOP_OPENHANDS=false
STOP_GENERATOR=false

# Parse Kommandozeilenargumente
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -a|--all)
            STOP_ALL=true
            shift
            ;;
        --docker)
            STOP_DOCKER=true
            shift
            ;;
        --n8n)
            STOP_N8N=true
            shift
            ;;
        --openhands)
            STOP_OPENHANDS=true
            shift
            ;;
        --generator)
            STOP_GENERATOR=true
            shift
            ;;
        *)
            error "Unbekannte Option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Wenn keine spezifischen Server ausgewählt wurden und nicht alle gestoppt werden sollen,
# stoppe standardmäßig die MCP-Server mit Docker Compose
if [ "$STOP_ALL" = false ] && [ "$STOP_DOCKER" = false ] && [ "$STOP_N8N" = false ] && [ "$STOP_OPENHANDS" = false ] && [ "$STOP_GENERATOR" = false ]; then
    # Setze Standard auf Docker Compose MCP-Server
    info "Keine spezifischen Server ausgewählt. Stoppe die MCP-Server mit Docker Compose..."
    stop_docker_mcp_servers
    exit $?
fi

# Hauptfunktion
main() {
    # Setze aktuelle Operation
    set_operation "stop_mcp_servers"
    
    # Stoppe entsprechende Server
    if [ "$STOP_ALL" = true ]; then
        info "Stoppe alle MCP-Server..."
        
        # Stoppe zuerst die Docker Compose MCP-Server
        stop_docker_mcp_servers
        
        # Stoppe dann die anderen Server
        stop_n8n_mcp_server
        stop_openhands_mcp_server
        stop_generator_mcp_server
        
        # Zum Schluss stoppe alle übrigen MCP-Server-Prozesse
        stop_all_mcp_processes
    else
        # Stoppe nur die ausgewählten Server
        if [ "$STOP_DOCKER" = true ]; then
            stop_docker_mcp_servers
        fi
        
        if [ "$STOP_N8N" = true ]; then
            stop_n8n_mcp_server
        fi
        
        if [ "$STOP_OPENHANDS" = true ]; then
            stop_openhands_mcp_server
        fi
        
        if [ "$STOP_GENERATOR" = true ]; then
            stop_generator_mcp_server
        fi
    fi
    
    info "MCP-Server-Stopp abgeschlossen."
}

# Fehlerbehandlung für unerwartete Fehler
handle_error() {
    local exit_code=$1
    local line_number=$2
    local command=$3
    
    error "Fehler in Zeile $line_number mit Exit-Code $exit_code beim Ausführen von: $command"
    
    # Versuche, fehlgeschlagene Operationen zu bereinigen
    if [ "$CURRENT_OPERATION" = "docker_compose_down" ]; then
        warn "Docker Compose down fehlgeschlagen. Versuche, Container zu stoppen..."
        if command -v docker &> /dev/null; then
            docker stop $(docker ps -q --filter "name=mcp-") 2>/dev/null || true
        fi
    fi
    
    info "MCP-Server-Stopp wurde mit Fehlern abgeschlossen."
    exit $exit_code
}

# Richte Fehlerbehandlung ein
trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR

# Führe die Hauptfunktion aus
main
EOF
    
    # Mache das Skript ausführbar
    chmod +x "${BASE_DIR}/stop-mcp-servers.sh"
    
    log_info "Start-Skripte erstellt."
    return 0
}

# Richte Fehlerbehandlung ein, wenn das Skript nicht als Bibliothek geladen wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR
    
    # Zeige Hilfe, wenn keine Argumente angegeben wurden
    if [[ $# -eq 0 ]]; then
        echo "Verwendung: $0 <Funktion> [Argumente...]"
        echo ""
        echo "Verfügbare Funktionen:"
        echo "  check_docker                     Überprüfe Docker-Installation"
        echo "  check_docker_compose             Überprüfe Docker Compose-Installation"
        echo "  start_docker_daemon              Starte Docker-Daemon"
        echo "  check_python_dependencies        Überprüfe Python-Abhängigkeiten"
        echo "  create_log_directories           Erstelle Log-Verzeichnisse"
        echo "  load_env_file <Datei>            Lade Umgebungsvariablen aus Datei"
        echo "  save_env_file <Datei> <Vars...>  Speichere Umgebungsvariablen in Datei"
        echo "  create_openhands_config <Datei>  Erstelle OpenHands-Konfiguration"
        echo "  create_claude_config <Datei>     Erstelle Claude-Konfiguration"
        echo "  create_start_scripts             Erstelle Start-Skripte"
        echo "  start_docker_mcp_servers         Starte Docker Compose MCP-Server"
        echo "  stop_docker_mcp_servers          Stoppe Docker Compose MCP-Server"
        echo "  start_n8n_mcp_server             Starte n8n MCP-Server"
        echo "  start_openhands_mcp_server       Starte OpenHands MCP-Server"
        exit 1
    fi
    
    # Führe die angeforderte Funktion aus
    "$@"
fi