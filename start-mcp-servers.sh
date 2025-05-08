#!/bin/bash
# Skript zum Starten der MCP-Server

# Konfiguration
N8N_URL=${N8N_URL:-"http://localhost:5678"}
N8N_API_KEY=${N8N_API_KEY:-""}
OPENHANDS_MAX_WORKERS=${OPENHANDS_MAX_WORKERS:-5}

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo "  -v, --verbose             Ausführliche Ausgabe"
    echo "  -a, --all                 Alle MCP-Server starten"
    echo "  --n8n                     n8n MCP-Server starten"
    echo "  --openhands               OpenHands MCP-Server starten"
    echo ""
    echo "Umgebungsvariablen:"
    echo "  N8N_URL                   URL der n8n-Instanz"
    echo "  N8N_API_KEY               API-Schlüssel für n8n"
    echo "  OPENHANDS_MAX_WORKERS     Maximale Anzahl von Worker-Threads für OpenHands"
    echo ""
    echo "Beispiel:"
    echo "  $0 --all -k my-api-key"
    echo "  $0 --n8n --openhands -k my-api-key -w 10"
}

# Funktion zum Starten des n8n MCP-Servers
start_n8n_mcp_server() {
    echo -e "${BLUE}Starte n8n MCP-Server...${NC}"
    
    if [ -z "$N8N_API_KEY" ]; then
        echo -e "${RED}Fehler: API-Schlüssel für n8n nicht angegeben${NC}"
        echo "Bitte geben Sie einen API-Schlüssel mit -k oder --api-key an"
        exit 1
    fi
    
    # Starte den n8n MCP-Server im Hintergrund
    python3 src/mcp/n8n_server.py --n8n-url "$N8N_URL" --api-key "$N8N_API_KEY" $VERBOSE_FLAG &
    N8N_PID=$!
    
    echo -e "${GREEN}n8n MCP-Server gestartet (PID: $N8N_PID)${NC}"
    echo "URL: http://localhost:3000"
    
    # Speichere die PID
    echo $N8N_PID > n8n-mcp-server.pid
}

# Funktion zum Starten des OpenHands MCP-Servers
start_openhands_mcp_server() {
    echo -e "${BLUE}Starte OpenHands MCP-Server...${NC}"
    
    # Starte den OpenHands MCP-Server im Hintergrund
    python3 src/mcp/openhands_server.py --max-workers "$OPENHANDS_MAX_WORKERS" $VERBOSE_FLAG &
    OPENHANDS_PID=$!
    
    echo -e "${GREEN}OpenHands MCP-Server gestartet (PID: $OPENHANDS_PID)${NC}"
    echo "URL: http://localhost:3006"
    
    # Speichere die PID
    echo $OPENHANDS_PID > openhands-mcp-server.pid
}

# Standardwerte
START_N8N=false
START_OPENHANDS=false
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
        -v|--verbose)
            VERBOSE_FLAG="--verbose"
            shift
            ;;
        -a|--all)
            START_N8N=true
            START_OPENHANDS=true
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
        *)
            echo -e "${RED}Fehler: Unbekannte Option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfe, ob mindestens ein Server gestartet werden soll
if [ "$START_N8N" = false ] && [ "$START_OPENHANDS" = false ]; then
    echo -e "${YELLOW}Warnung: Kein Server zum Starten angegeben${NC}"
    echo "Bitte geben Sie mindestens einen Server mit --n8n, --openhands oder --all an"
    show_help
    exit 1
fi

# Starte die Server
if [ "$START_N8N" = true ]; then
    start_n8n_mcp_server
fi

if [ "$START_OPENHANDS" = true ]; then
    start_openhands_mcp_server
fi

echo -e "${GREEN}Alle Server gestartet${NC}"
echo "Zum Beenden der Server führen Sie 'kill \$(cat *.pid)' aus"