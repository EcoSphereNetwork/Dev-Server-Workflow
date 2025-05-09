#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

# Verbessertes Skript zum Starten der MCP-Server mit Versionsprüfung und besserer Fehlerbehandlung

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfiguration
N8N_URL=${N8N_URL:-"http://localhost:5678"}
N8N_API_KEY=${N8N_API_KEY:-""}
OPENHANDS_MAX_WORKERS=${OPENHANDS_MAX_WORKERS:-5}
GENERATOR_SERVERS_DIR=${GENERATOR_SERVERS_DIR:-"generated_servers"}
MCP_SERVERS_DIR="${BASE_DIR%/*}/docker-mcp-servers"
LOG_DIR="/tmp/mcp-logs"

# Aktuelle Operation für Fehlerbehandlung
CURRENT_OPERATION=""
CURRENT_CONTAINER=""

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

# Funktion zum Anzeigen von Hilfe
show_help() {
    log_info "${BLUE}MCP-Server Starter${NC}"
    log_info "Dieses Skript startet die MCP-Server für das Dev-Server-Workflow-Projekt."
    echo ""
    log_info "Verwendung:"
    log_info "  $0 [Optionen]"
    echo ""
    log_info "Optionen:"
    log_info "  -h, --help                Zeigt diese Hilfe an"
    log_info "  -n, --n8n-url URL         URL der n8n-Instanz (Standard: $N8N_URL)"
    log_info "  -k, --api-key KEY         API-Schlüssel für n8n"
    log_info "  -w, --max-workers N       Maximale Anzahl von Worker-Threads für OpenHands (Standard: $OPENHANDS_MAX_WORKERS)"
    log_info "  -d, --servers-dir DIR     Verzeichnis für generierte Server (Standard: $GENERATOR_SERVERS_DIR)"
    log_info "  -v, --verbose             Ausführliche Ausgabe"
    log_info "  -a, --all                 Alle MCP-Server starten"
    log_info "  --n8n                     n8n MCP-Server starten"
    log_info "  --openhands               OpenHands MCP-Server starten"
    log_info "  --generator               MCP-Server-Generator starten"
    echo ""
    log_info "Umgebungsvariablen:"
    log_info "  N8N_URL                   URL der n8n-Instanz"
    log_info "  N8N_API_KEY               API-Schlüssel für n8n"
    log_info "  OPENHANDS_MAX_WORKERS     Maximale Anzahl von Worker-Threads für OpenHands"
    log_info "  GENERATOR_SERVERS_DIR     Verzeichnis für generierte Server"
    echo ""
    log_info "Beispiel:"
    log_info "  $0 --all -k my-api-key"
    log_info "  $0 --n8n --openhands -k my-api-key -w 10"
}

# Funktion zum Einrichten eines Alias für docker-compose
setup_docker_compose_alias() {
    # Prüfen, ob docker compose Befehl verfügbar ist
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Prüfen, ob docker-compose Befehl verfügbar ist
        if ! command -v docker-compose &> /dev/null; then
            info "Richte Alias für docker-compose ein..."
            
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
                warn "Bitte führen Sie 'source $shell_rc' aus, oder starten Sie ein neues Terminal, um den Alias zu aktivieren."
                
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

# Funktion zum Überprüfen der Docker-Installation
check_docker() {
    info "Überprüfe Docker-Installation..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut."
        return 1
}

# Funktion zum Starten des Docker-Daemons
start_docker_daemon() {
    info "Überprüfe, ob der Docker-Daemon läuft..."
    
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

# Funktion zum Starten der MCP-Server
start_mcp_servers() {
    info "Starte MCP-Server..."
    
    # Überprüfe, ob das Docker-Compose-File existiert
    if [ ! -f "$MCP_SERVERS_DIR/docker-compose.yml" ]; then
        if [ -f "$MCP_SERVERS_DIR/docker-compose-full.yml" ]; then
            log "Kopiere docker-compose-full.yml nach docker-compose.yml..."
            cp "$MCP_SERVERS_DIR/docker-compose-full.yml" "$MCP_SERVERS_DIR/docker-compose.yml"
        else
            error "Docker-Compose-Datei nicht gefunden: $MCP_SERVERS_DIR/docker-compose.yml"
            error "Bitte führen Sie zuerst install-mcp-servers.sh aus."
            return 1
        fi
    fi
    
    # Setze aktuelle Operation
    CURRENT_OPERATION="docker_compose_up"
    CURRENT_CONTAINER="all"
    
    # Wechsle in das MCP-Servers-Verzeichnis und starte die Container
    cd "$MCP_SERVERS_DIR"
    
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
    
    log "MCP-Server erfolgreich gestartet."
    log "MCP Inspector UI ist verfügbar unter: http://localhost:8080"
    
    # Zeige die gestarteten Container an
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    return 0
}

# Funktion zum Start des n8n MCP-Servers
start_n8n_mcp_server() {
    info "Starte n8n MCP-Server..."
    
    if [ -z "$N8N_API_KEY" ]; then
        warn "API-Schlüssel für n8n nicht angegeben. Der n8n MCP-Server könnte eingeschränkt funktionieren."
    fi
    
    # Überprüfe, ob das Skript existiert
    if [ -f "${BASE_DIR%/*}/src/n8n_mcp_server.py" ]; then
        log "Verwende n8n_mcp_server.py..."
        python3 "${BASE_DIR%/*}/src/n8n_mcp_server.py" --n8n-url "$N8N_URL" --api-key "$N8N_API_KEY" &
        echo $! > "$LOG_DIR/n8n_mcp_server.pid"
        log "n8n MCP-Server gestartet (PID: $(cat "$LOG_DIR/n8n_mcp_server.pid"))"
    elif [ -f "${BASE_DIR%/*}/src/n8n-mcp-server.py" ]; then
        log "Verwende n8n-mcp-server.py..."
        python3 "${BASE_DIR%/*}/src/n8n-mcp-server.py" --n8n-url "$N8N_URL" --api-key "$N8N_API_KEY" &
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
    if [ -f "${BASE_DIR%/*}/src/openhands_mcp_server.py" ]; then
        log "Verwende openhands_mcp_server.py..."
        python3 "${BASE_DIR%/*}/src/openhands_mcp_server.py" --max-workers "$OPENHANDS_MAX_WORKERS" &
        echo $! > "$LOG_DIR/openhands_mcp_server.pid"
        log "OpenHands MCP-Server gestartet (PID: $(cat "$LOG_DIR/openhands_mcp_server.pid"))"
    elif [ -f "${BASE_DIR%/*}/src/openhands-mcp-server.py" ]; then
        log "Verwende openhands-mcp-server.py..."
        python3 "${BASE_DIR%/*}/src/openhands-mcp-server.py" --max-workers "$OPENHANDS_MAX_WORKERS" &
        echo $! > "$LOG_DIR/openhands_mcp_server.pid"
        log "OpenHands MCP-Server gestartet (PID: $(cat "$LOG_DIR/openhands_mcp_server.pid"))"
    else
        warn "OpenHands MCP-Server-Skript nicht gefunden. Der OpenHands MCP-Server wurde nicht gestartet."
        return 1
    fi
    
    return 0
}

# Funktion zum Start des MCP-Server-Generators
start_generator_mcp_server() {
    info "Starte MCP-Server-Generator..."
    
    # Erstelle das Verzeichnis für generierte Server, falls es nicht existiert
    mkdir -p "$GENERATOR_SERVERS_DIR"
    
    # Überprüfe, ob das Skript existiert
    if [ -f "${BASE_DIR%/*}/src/generator_mcp_server.py" ]; then
        log "Verwende generator_mcp_server.py..."
        python3 "${BASE_DIR%/*}/src/generator_mcp_server.py" --servers-dir "$GENERATOR_SERVERS_DIR" &
        echo $! > "$LOG_DIR/generator_mcp_server.pid"
        log "MCP-Server-Generator gestartet (PID: $(cat "$LOG_DIR/generator_mcp_server.pid"))"
    elif [ -f "${BASE_DIR%/*}/src/generator-mcp-server.py" ]; then
        log "Verwende generator-mcp-server.py..."
        python3 "${BASE_DIR%/*}/src/generator-mcp-server.py" --servers-dir "$GENERATOR_SERVERS_DIR" &
        echo $! > "$LOG_DIR/generator_mcp_server.pid"
        log "MCP-Server-Generator gestartet (PID: $(cat "$LOG_DIR/generator_mcp_server.pid"))"
    else
        warn "MCP-Server-Generator-Skript nicht gefunden. Der MCP-Server-Generator wurde nicht gestartet."
        return 1
    fi
    
    return 0
}

# Funktion zum Überprüfen und Installieren von Python-Abhängigkeiten
check_python_dependencies() {
    info "Prüfe Python-Abhängigkeiten..."
    
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

# Standardwerte
START_ALL=false
START_N8N=false
START_OPENHANDS=false
START_GENERATOR=false
VERBOSE_FLAG=""

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

# Wenn keine spezifischen Server ausgewählt wurden und nicht alle gestartet werden sollen,
# starte standardmäßig die MCP-Server mit Docker Compose
if [ "$START_ALL" = false ] && [ "$START_N8N" = false ] && [ "$START_OPENHANDS" = false ] && [ "$START_GENERATOR" = false ]; then
    # Setze Standard auf Docker Compose MCP-Server
    info "Keine spezifischen Server ausgewählt. Starte die MCP-Server mit Docker Compose..."
    
    # Prüfe Abhängigkeiten
    check_docker || exit 1
    check_docker_compose || exit 1
    start_docker_daemon || exit 1
    create_log_directories
    
    # Starte die MCP-Server
    start_mcp_servers
    
    exit $?
fi

# Hauptfunktion
main() {
    # Prüfe Abhängigkeiten
    check_docker || exit 1
    check_docker_compose || exit 1
    start_docker_daemon || exit 1
    check_python_dependencies || exit 1
    create_log_directories
    
    # Starte entsprechende Server
    if [ "$START_ALL" = true ]; then
        info "Starte alle MCP-Server..."
        
        # Starte die Docker Compose MCP-Server
        start_mcp_servers
        
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
}

# Führe die Hauptfunktion aus
main
    fi
    
    # Überprüfe die Docker-Version
    local docker_version
    docker_version=$(docker --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
    
    if [ -n "$docker_version" ]; then
        log "Docker Version: $docker_version"
        
        # Vergleiche mit der Mindestversion
        if [ "$(printf '%s\n' "20.10.0" "$docker_version" | sort -V | head -n1)" = "20.10.0" ]; then
            log "Docker ist ausreichend aktuell."
        else
            warn "Docker Version ist älter als 20.10.0. Ein Update wird empfohlen."
        fi
    else
        warn "Konnte die Docker-Version nicht ermitteln."
    fi
    
    return 0
}

# Funktion zum Überprüfen der Docker Compose-Installation
check_docker_compose() {
    info "Überprüfe Docker Compose-Installation..."
    
    # Prüfe zunächst das neue Docker-Compose-Plugin
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Versuche, die Version zu ermitteln
        local docker_compose_version
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
        
        local docker_compose_version
        docker_compose_version=$(docker-compose --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        
        if [ -n "$docker_compose_version" ]; then
            log "Docker Compose Version: $docker_compose_version"
            
            # Vergleiche mit der Mindestversion
            if [ "$(printf '%s\n' "1.29.0" "$docker_compose_version" | sort -V | head -n1)" != "1.29.0" ]; then
                log "Docker Compose ist ausreichend aktuell."
                return 0
            else
                warn "Docker Compose Version ist älter als 1.29.0. Ein Update wird empfohlen."
                # Aber wir können es trotzdem nutzen
                return 0
            fi
        fi
    fi
    
    # Wenn wir hier ankommen, fehlt Docker Compose
    error "Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut."
    error "Sie können Docker Compose mit folgendem Befehl installieren:"
    error "sudo apt-get install docker-compose-plugin"
    return 1
