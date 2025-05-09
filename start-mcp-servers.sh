#!/bin/bash

# Verbessertes Skript zum Starten der MCP-Server
# Verwendet die gemeinsame Bibliothek für konsistente Funktionen und Konfigurationen

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Standardwerte für Kommandozeilenargumente
START_ALL=false
START_N8N=false
START_OPENHANDS=false
START_GENERATOR=false
VERBOSE_FLAG=""
GENERATOR_SERVERS_DIR=${GENERATOR_SERVERS_DIR:-"generated_servers"}

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

# Funktion zum Start des MCP-Server-Generators
start_generator_mcp_server() {
    info "Starte MCP-Server-Generator..."
    
    # Erstelle das Verzeichnis für generierte Server, falls es nicht existiert
    mkdir -p "$GENERATOR_SERVERS_DIR"
    
    # Überprüfe, ob das Skript existiert
    if [ -f "${BASE_DIR}/src/generator_mcp_server.py" ]; then
        log "Verwende generator_mcp_server.py..."
        python3 "${BASE_DIR}/src/generator_mcp_server.py" --servers-dir "$GENERATOR_SERVERS_DIR" &
        echo $! > "$LOG_DIR/generator_mcp_server.pid"
        log "MCP-Server-Generator gestartet (PID: $(cat "$LOG_DIR/generator_mcp_server.pid"))"
    elif [ -f "${BASE_DIR}/src/generator-mcp-server.py" ]; then
        log "Verwende generator-mcp-server.py..."
        python3 "${BASE_DIR}/src/generator-mcp-server.py" --servers-dir "$GENERATOR_SERVERS_DIR" &
        echo $! > "$LOG_DIR/generator_mcp_server.pid"
        log "MCP-Server-Generator gestartet (PID: $(cat "$LOG_DIR/generator_mcp_server.pid"))"
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