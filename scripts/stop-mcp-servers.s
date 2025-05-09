#!/bin/bash
# Verbessertes Skript zum Stoppen der MCP-Server mit besserer Fehlerbehandlung

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
LOG_DIR="/tmp/mcp-logs"
MCP_SERVERS_DIR="${BASE_DIR%/*}/docker-mcp-servers"

# Aktuelle Operation für Fehlerbehandlung
CURRENT_OPERATION=""
CURRENT_CONTAINER=""

# Funktion zum Anzeigen von Nachrichten
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

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

# Funktion zum Stoppen der Docker Compose MCP-Server
stop_docker_compose_servers() {
    info "Stoppe Docker Compose MCP-Server..."
    
    # Überprüfe, ob das Docker-Compose-File existiert
    if [ ! -f "$MCP_SERVERS_DIR/docker-compose.yml" ]; then
        warn "Docker-Compose-Datei nicht gefunden: $MCP_SERVERS_DIR/docker-compose.yml"
        warn "Es sind möglicherweise keine Docker Compose MCP-Server gestartet."
        return 0
    fi
    
    # Setze aktuelle Operation
    CURRENT_OPERATION="docker_compose_down"
    CURRENT_CONTAINER="all"
    
    # Wechsle in das MCP-Servers-Verzeichnis und stoppe die Container
    cd "$MCP_SERVERS_DIR"
    
    # Verwende docker-compose oder docker compose, je nachdem, was verfügbar ist
    if command -v docker-compose &> /dev/null; then
        log "Verwende docker-compose..."
        docker-compose down
    else
        log "Verwende docker compose..."
        docker compose down
    fi
    
    log "Docker Compose MCP-Server erfolgreich gestoppt."
    return 0
}

# Funktion zum Stoppen des n8n MCP-Servers
stop_n8n_mcp_server() {
    info "Stoppe n8n MCP-Server..."
    
    local pid_file="$LOG_DIR/n8n_mcp_server.pid"
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
    
    local pid_file="$LOG_DIR/openhands_mcp_server.pid"
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
    
    local pid_file="$LOG_DIR/generator_mcp_server.pid"
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
    local generator_servers_dir="${BASE_DIR%/*}/generated_servers"
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
    rm -f "$LOG_DIR"/*.pid
    
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
    stop_docker_compose_servers
    exit $?
fi

# Hauptfunktion
main() {
    # Setze aktuelle Operation
    CURRENT_OPERATION="stop_mcp_servers"
    
    # Stoppe entsprechende Server
    if [ "$STOP_ALL" = true ]; then
        info "Stoppe alle MCP-Server..."
        
        # Stoppe zuerst die Docker Compose MCP-Server
        stop_docker_compose_servers
        
        # Stoppe dann die anderen Server
        stop_n8n_mcp_server
        stop_openhands_mcp_server
        stop_generator_mcp_server
        
        # Zum Schluss stoppe alle übrigen MCP-Server-Prozesse
        stop_all_mcp_processes
    else
        # Stoppe nur die ausgewählten Server
        if [ "$STOP_DOCKER" = true ]; then
            stop_docker_compose_servers
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
