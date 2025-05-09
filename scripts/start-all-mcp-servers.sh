#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(cd "$BASE_DIR/.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$PARENT_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${PARENT_DIR}/.env"

# Standardwerte für Ports
N8N_MCP_PORT=${N8N_MCP_PORT:-3456}
OPENHANDS_MCP_PORT=${OPENHANDS_MCP_PORT:-3457}
DOCKER_MCP_PORT=${DOCKER_MCP_PORT:-3458}
GENERATOR_MCP_PORT=${GENERATOR_MCP_PORT:-3459}

# Standardwerte für andere Konfigurationen
N8N_URL=${N8N_URL:-http://localhost:5678}
N8N_API_KEY=${N8N_API_KEY:-}
OPENHANDS_MAX_WORKERS=${OPENHANDS_MAX_WORKERS:-5}
DOCKER_NETWORK=${DOCKER_NETWORK:-dev-server-network}
LOG_DIR=${LOG_DIR:-/tmp/mcp-logs}

# Erstelle Log-Verzeichnis
mkdir -p "$LOG_DIR"

# Funktion zum Anzeigen der Hilfe
show_help() {
    log_info "Verwendung: $0 [Optionen]"
    log_info ""
    log_info "Optionen:"
    log_info "  --n8n              Starte nur den n8n MCP-Server"
    log_info "  --openhands        Starte nur den OpenHands MCP-Server"
    log_info "  --docker           Starte nur den Docker MCP-Server"
    log_info "  --generator        Starte nur den Generator MCP-Server"
    log_info "  --all              Starte alle MCP-Server (Standard)"
    log_info "  --http             Starte die Server im HTTP-Modus (Standard: stdio)"
    log_info "  --verbose          Ausführliche Ausgabe"
    log_info "  --help             Zeigt diese Hilfe an"
    log_info ""
    log_info "Umgebungsvariablen:"
    log_info "  N8N_MCP_PORT       Port für den n8n MCP-Server (Standard: 3456)"
    log_info "  OPENHANDS_MCP_PORT Port für den OpenHands MCP-Server (Standard: 3457)"
    log_info "  DOCKER_MCP_PORT    Port für den Docker MCP-Server (Standard: 3458)"
    log_info "  GENERATOR_MCP_PORT Port für den Generator MCP-Server (Standard: 3459)"
    log_info "  N8N_URL            URL der n8n-Instanz (Standard: http://localhost:5678)"
    log_info "  N8N_API_KEY        API-Key für n8n"
    log_info "  OPENHANDS_MAX_WORKERS Maximale Anzahl von Worker-Threads für OpenHands (Standard: 5)"
    log_info "  DOCKER_NETWORK     Name des Docker-Netzwerks (Standard: dev-server-network)"
    log_info "  LOG_DIR            Verzeichnis für Log-Dateien (Standard: /tmp/mcp-logs)"
}

# Standardwerte für Kommandozeilenargumente
START_N8N=false
START_OPENHANDS=false
START_DOCKER=false
START_GENERATOR=false
START_ALL=true
MODE="stdio"
VERBOSE=""

# Parse Kommandozeilenargumente
while [[ $# -gt 0 ]]; do
    case "$1" in
        --n8n)
            START_N8N=true
            START_ALL=false
            shift
            ;;
        --openhands)
            START_OPENHANDS=true
            START_ALL=false
            shift
            ;;
        --docker)
            START_DOCKER=true
            START_ALL=false
            shift
            ;;
        --generator)
            START_GENERATOR=true
            START_ALL=false
            shift
            ;;
        --all)
            START_ALL=true
            shift
            ;;
        --http)
            MODE="http"
            shift
            ;;
        --verbose)
            VERBOSE="--log-level debug"
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unbekannte Option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Prüfe, ob Python installiert ist
check_command "python3" "Python 3 ist nicht installiert. Bitte installieren Sie Python 3."

# Prüfe, ob die MCP-Server-Skripte existieren
check_file "$PARENT_DIR/src/mcp/n8n_mcp_server_improved.py" "n8n MCP-Server-Skript nicht gefunden."
check_file "$PARENT_DIR/src/mcp/openhands_server_improved.py" "OpenHands MCP-Server-Skript nicht gefunden."
check_file "$PARENT_DIR/src/mcp/docker_mcp_server_improved.py" "Docker MCP-Server-Skript nicht gefunden."
check_file "$PARENT_DIR/src/mcp/base_mcp_server.py" "MCP-Server-Basisklasse nicht gefunden."

# Funktion zum Starten eines MCP-Servers
start_mcp_server() {
    local name="$1"
    local script="$2"
    local port="$3"
    local extra_args="$4"
    
    log_info "Starte $name MCP-Server auf Port $port..."
    
    # Erstelle den Befehl
    local cmd="python3 $script --port $port --mode $MODE $VERBOSE $extra_args"
    
    # Starte den Server
    if [ "$MODE" = "stdio" ]; then
        # Im stdio-Modus starten wir den Server im Hintergrund und leiten die Ausgabe in eine Datei um
        nohup $cmd > "$LOG_DIR/$name-mcp-server.log" 2>&1 &
        local pid=$!
        log_info "$name MCP-Server gestartet mit PID $pid"
        
        # Speichere die PID in einer Datei
        echo $pid > "$LOG_DIR/$name-mcp-server.pid"
    else
        # Im HTTP-Modus starten wir den Server im Hintergrund und leiten die Ausgabe in eine Datei um
        nohup $cmd > "$LOG_DIR/$name-mcp-server.log" 2>&1 &
        local pid=$!
        log_info "$name MCP-Server gestartet mit PID $pid"
        
        # Speichere die PID in einer Datei
        echo $pid > "$LOG_DIR/$name-mcp-server.pid"
        
        # Warte, bis der Server gestartet ist
        log_info "Warte, bis der $name MCP-Server verfügbar ist..."
        local max_attempts=30
        local attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if curl -s "http://localhost:$port/health" > /dev/null; then
                log_info "$name MCP-Server ist verfügbar"
                break
            fi
            attempt=$((attempt + 1))
            sleep 1
        done
        
        if [ $attempt -eq $max_attempts ]; then
            log_warn "$name MCP-Server ist nach $max_attempts Sekunden noch nicht verfügbar"
        fi
    fi
}

# Starte die MCP-Server
if [ "$START_ALL" = true ] || [ "$START_N8N" = true ]; then
    # Prüfe, ob der API-Key für n8n gesetzt ist
    if [ -z "$N8N_API_KEY" ]; then
        log_warn "N8N_API_KEY ist nicht gesetzt. Der n8n MCP-Server wird möglicherweise nicht korrekt funktionieren."
    fi
    
    start_mcp_server "n8n" "$PARENT_DIR/src/mcp/n8n_mcp_server_improved.py" "$N8N_MCP_PORT" "--n8n-url $N8N_URL --api-key $N8N_API_KEY"
fi

if [ "$START_ALL" = true ] || [ "$START_OPENHANDS" = true ]; then
    start_mcp_server "openhands" "$PARENT_DIR/src/mcp/openhands_server_improved.py" "$OPENHANDS_MCP_PORT" "--max-workers $OPENHANDS_MAX_WORKERS"
fi

if [ "$START_ALL" = true ] || [ "$START_DOCKER" = true ]; then
    start_mcp_server "docker" "$PARENT_DIR/src/mcp/docker_mcp_server_improved.py" "$DOCKER_MCP_PORT" "--docker-network $DOCKER_NETWORK"
fi

if [ "$START_ALL" = true ] || [ "$START_GENERATOR" = true ]; then
    # Der Generator MCP-Server ist noch nicht implementiert
    log_warn "Generator MCP-Server ist noch nicht implementiert"
fi

log_info "Alle MCP-Server wurden gestartet"
log_info "Logs werden in $LOG_DIR gespeichert"

if [ "$MODE" = "http" ]; then
    log_info "MCP-Server-Endpunkte:"
    [ "$START_ALL" = true ] || [ "$START_N8N" = true ] && log_info "  n8n MCP-Server: http://localhost:$N8N_MCP_PORT"
    [ "$START_ALL" = true ] || [ "$START_OPENHANDS" = true ] && log_info "  OpenHands MCP-Server: http://localhost:$OPENHANDS_MCP_PORT"
    [ "$START_ALL" = true ] || [ "$START_DOCKER" = true ] && log_info "  Docker MCP-Server: http://localhost:$DOCKER_MCP_PORT"
    [ "$START_ALL" = true ] || [ "$START_GENERATOR" = true ] && log_info "  Generator MCP-Server: http://localhost:$GENERATOR_MCP_PORT"
fi