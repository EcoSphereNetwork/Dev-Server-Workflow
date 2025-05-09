#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(cd "$BASE_DIR/.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$PARENT_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${PARENT_DIR}/.env"

# Standardwerte für Konfigurationen
LOG_DIR=${LOG_DIR:-/tmp/mcp-logs}

# Funktion zum Anzeigen der Hilfe
show_help() {
    log_info "Verwendung: $0 [Optionen]"
    log_info ""
    log_info "Optionen:"
    log_info "  --n8n              Stoppe nur den n8n MCP-Server"
    log_info "  --openhands        Stoppe nur den OpenHands MCP-Server"
    log_info "  --docker           Stoppe nur den Docker MCP-Server"
    log_info "  --generator        Stoppe nur den Generator MCP-Server"
    log_info "  --all              Stoppe alle MCP-Server (Standard)"
    log_info "  --force            Erzwinge das Stoppen der Server"
    log_info "  --help             Zeigt diese Hilfe an"
}

# Standardwerte für Kommandozeilenargumente
STOP_N8N=false
STOP_OPENHANDS=false
STOP_DOCKER=false
STOP_GENERATOR=false
STOP_ALL=true
FORCE=false

# Parse Kommandozeilenargumente
while [[ $# -gt 0 ]]; do
    case "$1" in
        --n8n)
            STOP_N8N=true
            STOP_ALL=false
            shift
            ;;
        --openhands)
            STOP_OPENHANDS=true
            STOP_ALL=false
            shift
            ;;
        --docker)
            STOP_DOCKER=true
            STOP_ALL=false
            shift
            ;;
        --generator)
            STOP_GENERATOR=true
            STOP_ALL=false
            shift
            ;;
        --all)
            STOP_ALL=true
            shift
            ;;
        --force)
            FORCE=true
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

# Funktion zum Stoppen eines MCP-Servers
stop_mcp_server() {
    local name="$1"
    local pid_file="$LOG_DIR/$name-mcp-server.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        
        log_info "Stoppe $name MCP-Server (PID $pid)..."
        
        if [ "$FORCE" = true ]; then
            # Erzwinge das Stoppen des Servers
            kill -9 $pid 2>/dev/null || true
        else
            # Sende SIGTERM, um den Server ordnungsgemäß zu beenden
            kill $pid 2>/dev/null || true
            
            # Warte, bis der Server beendet ist
            local max_attempts=10
            local attempt=0
            while [ $attempt -lt $max_attempts ]; do
                if ! ps -p $pid > /dev/null; then
                    break
                fi
                attempt=$((attempt + 1))
                sleep 1
            done
            
            # Wenn der Server nach dem Timeout noch läuft, erzwinge das Stoppen
            if [ $attempt -eq $max_attempts ]; then
                log_warn "$name MCP-Server reagiert nicht, erzwinge das Stoppen..."
                kill -9 $pid 2>/dev/null || true
            fi
        fi
        
        # Entferne die PID-Datei
        rm -f "$pid_file"
        
        log_info "$name MCP-Server gestoppt"
    else
        log_warn "$name MCP-Server läuft nicht (keine PID-Datei gefunden)"
    fi
}

# Stoppe die MCP-Server
if [ "$STOP_ALL" = true ] || [ "$STOP_N8N" = true ]; then
    stop_mcp_server "n8n"
fi

if [ "$STOP_ALL" = true ] || [ "$STOP_OPENHANDS" = true ]; then
    stop_mcp_server "openhands"
fi

if [ "$STOP_ALL" = true ] || [ "$STOP_DOCKER" = true ]; then
    stop_mcp_server "docker"
fi

if [ "$STOP_ALL" = true ] || [ "$STOP_GENERATOR" = true ]; then
    stop_mcp_server "generator"
fi

log_info "Alle MCP-Server wurden gestoppt"