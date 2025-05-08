#!/bin/bash
# Skript zum Stoppen der MCP-Server

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Fehlerbehandlung einbinden
if [[ -f "${BASE_DIR}/cli/error_handler.sh" ]]; then
    source "${BASE_DIR}/cli/error_handler.sh"
fi

# Konfigurationsmanager einbinden
if [[ -f "${BASE_DIR}/cli/config_manager.sh" ]]; then
    source "${BASE_DIR}/cli/config_manager.sh"
    # Alle Konfigurationen laden
    if [[ "$(type -t load_all_configs)" == "function" ]]; then
        load_all_configs
    fi
fi

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${BLUE}Stoppe n8n MCP-Server...${NC}"
    
    if [ -f n8n-mcp-server.pid ]; then
        PID=$(cat n8n-mcp-server.pid)
        
        if ps -p $PID > /dev/null; then
            kill $PID
            echo -e "${GREEN}n8n MCP-Server gestoppt (PID: $PID)${NC}"
        else
            echo -e "${YELLOW}n8n MCP-Server läuft nicht (PID: $PID)${NC}"
        fi
        
        rm n8n-mcp-server.pid
    else
        echo -e "${YELLOW}n8n MCP-Server PID-Datei nicht gefunden${NC}"
    fi
}

# Funktion zum Stoppen des OpenHands MCP-Servers
stop_openhands_mcp_server() {
    echo -e "${BLUE}Stoppe OpenHands MCP-Server...${NC}"
    
    if [ -f openhands-mcp-server.pid ]; then
        PID=$(cat openhands-mcp-server.pid)
        
        if ps -p $PID > /dev/null; then
            kill $PID
            echo -e "${GREEN}OpenHands MCP-Server gestoppt (PID: $PID)${NC}"
        else
            echo -e "${YELLOW}OpenHands MCP-Server läuft nicht (PID: $PID)${NC}"
        fi
        
        rm openhands-mcp-server.pid
    else
        echo -e "${YELLOW}OpenHands MCP-Server PID-Datei nicht gefunden${NC}"
    fi
}

# Standardwerte
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
            STOP_N8N=true
            STOP_OPENHANDS=true
            STOP_GENERATOR=true
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
            echo -e "${RED}Fehler: Unbekannte Option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfe, ob mindestens ein Server gestoppt werden soll
if [ "$STOP_N8N" = false ] && [ "$STOP_OPENHANDS" = false ] && [ "$STOP_GENERATOR" = false ]; then
    echo -e "${YELLOW}Warnung: Kein Server zum Stoppen angegeben${NC}"
    echo "Bitte geben Sie mindestens einen Server mit --n8n, --openhands, --generator oder --all an"
    show_help
    exit 1
fi

# Funktion zum Stoppen des MCP-Server-Generators
stop_generator_mcp_server() {
    echo -e "${BLUE}Stoppe MCP-Server-Generator...${NC}"
    
    if [ -f generator-mcp-server.pid ]; then
        PID=$(cat generator-mcp-server.pid)
        
        if ps -p $PID > /dev/null; then
            kill $PID
            echo -e "${GREEN}MCP-Server-Generator gestoppt (PID: $PID)${NC}"
        else
            echo -e "${YELLOW}MCP-Server-Generator läuft nicht (PID: $PID)${NC}"
        fi
        
        rm generator-mcp-server.pid
    else
        echo -e "${YELLOW}MCP-Server-Generator PID-Datei nicht gefunden${NC}"
    fi
    
    # Stoppe auch alle generierten Server
    if [ -d "generated_servers" ]; then
        echo -e "${BLUE}Stoppe generierte MCP-Server...${NC}"
        for pid_file in generated_servers/*/server.pid; do
            if [ -f "$pid_file" ]; then
                PID=$(cat "$pid_file")
                SERVER_DIR=$(dirname "$pid_file")
                SERVER_ID=$(basename "$SERVER_DIR")
                
                if ps -p $PID > /dev/null; then
                    kill $PID
                    echo -e "${GREEN}Generierter MCP-Server $SERVER_ID gestoppt (PID: $PID)${NC}"
                else
                    echo -e "${YELLOW}Generierter MCP-Server $SERVER_ID läuft nicht (PID: $PID)${NC}"
                fi
                
                rm "$pid_file"
                
                # Aktualisiere den Status in der Konfigurationsdatei
                CONFIG_FILE="$SERVER_DIR/config.json"
                if [ -f "$CONFIG_FILE" ]; then
                    # Verwende temporäre Datei für die Aktualisierung
                    TMP_FILE="$SERVER_DIR/config.tmp.json"
                    cat "$CONFIG_FILE" | sed 's/"status": "running"/"status": "stopped"/g' > "$TMP_FILE"
                    mv "$TMP_FILE" "$CONFIG_FILE"
                fi
            fi
        done
    fi
}

# Fehlerbehandlung einrichten
if [[ "$(type -t handle_error)" == "function" ]]; then
    trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR
fi

# Hauptfunktion
main() {
    # Setze aktuelle Operation
    CURRENT_OPERATION="stop_mcp_servers"
    
    # Stoppe die Server
    if [ "$STOP_N8N" = true ]; then
        CURRENT_OPERATION="stop_n8n_mcp_server"
        CURRENT_CONTAINER="n8n-mcp-server"
        stop_n8n_mcp_server
    fi
    
    if [ "$STOP_OPENHANDS" = true ]; then
        CURRENT_OPERATION="stop_openhands_mcp_server"
        CURRENT_CONTAINER="openhands-mcp-server"
        stop_openhands_mcp_server
    fi
    
    if [ "$STOP_GENERATOR" = true ]; then
        CURRENT_OPERATION="stop_generator_mcp_server"
        CURRENT_CONTAINER="generator-mcp-server"
        stop_generator_mcp_server
    fi
    
    # Wenn keine Server ausgewählt wurden, stoppe alle
    if [ "$STOP_N8N" = false ] && [ "$STOP_OPENHANDS" = false ] && [ "$STOP_GENERATOR" = false ]; then
        echo -e "${YELLOW}Keine Server ausgewählt. Stoppe alle Server...${NC}"
        
        CURRENT_OPERATION="stop_n8n_mcp_server"
        CURRENT_CONTAINER="n8n-mcp-server"
        stop_n8n_mcp_server
        
        CURRENT_OPERATION="stop_openhands_mcp_server"
        CURRENT_CONTAINER="openhands-mcp-server"
        stop_openhands_mcp_server
        
        CURRENT_OPERATION="stop_generator_mcp_server"
        CURRENT_CONTAINER="generator-mcp-server"
        stop_generator_mcp_server
    fi
    
    echo -e "${GREEN}Alle Server gestoppt${NC}"
}

# Führe die Hauptfunktion aus
main