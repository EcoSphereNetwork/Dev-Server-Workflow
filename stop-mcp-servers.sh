#!/bin/bash
# Skript zum Stoppen der MCP-Server

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
        *)
            echo -e "${RED}Fehler: Unbekannte Option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfe, ob mindestens ein Server gestoppt werden soll
if [ "$STOP_N8N" = false ] && [ "$STOP_OPENHANDS" = false ]; then
    echo -e "${YELLOW}Warnung: Kein Server zum Stoppen angegeben${NC}"
    echo "Bitte geben Sie mindestens einen Server mit --n8n, --openhands oder --all an"
    show_help
    exit 1
fi

# Stoppe die Server
if [ "$STOP_N8N" = true ]; then
    stop_n8n_mcp_server
fi

if [ "$STOP_OPENHANDS" = true ]; then
    stop_openhands_mcp_server
fi

echo -e "${GREEN}Alle Server gestoppt${NC}"