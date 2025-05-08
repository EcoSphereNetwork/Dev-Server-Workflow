#!/bin/bash
# Skript zum Starten der MCP-Server

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

# Konfiguration
N8N_URL=${N8N_URL:-"http://localhost:5678"}
N8N_API_KEY=${N8N_API_KEY:-""}
OPENHANDS_MAX_WORKERS=${OPENHANDS_MAX_WORKERS:-5}
GENERATOR_SERVERS_DIR=${GENERATOR_SERVERS_DIR:-"generated_servers"}

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
            START_N8N=true
            START_OPENHANDS=true
            START_GENERATOR=true
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
            echo -e "${RED}Fehler: Unbekannte Option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfe, ob mindestens ein Server gestartet werden soll
if [ "$START_N8N" = false ] && [ "$START_OPENHANDS" = false ] && [ "$START_GENERATOR" = false ]; then
    echo -e "${YELLOW}Warnung: Kein Server zum Starten angegeben${NC}"
    echo "Bitte geben Sie mindestens einen Server mit --n8n, --openhands, --generator oder --all an"
    show_help
    exit 1
fi

# Funktion zum Starten des MCP-Server-Generators
start_generator_mcp_server() {
    echo -e "${BLUE}Starte MCP-Server-Generator...${NC}"
    
    # Erstelle das Verzeichnis für generierte Server, falls es nicht existiert
    mkdir -p "$GENERATOR_SERVERS_DIR"
    
    # Starte den MCP-Server-Generator im Hintergrund
    python3 src/mcp/generator_server.py --servers-dir "$GENERATOR_SERVERS_DIR" $VERBOSE_FLAG &
    GENERATOR_PID=$!
    
    echo -e "${GREEN}MCP-Server-Generator gestartet (PID: $GENERATOR_PID)${NC}"
    echo "URL: http://localhost:3007"
    
    # Speichere die PID
    echo $GENERATOR_PID > generator-mcp-server.pid
}

# Fehlerbehandlung einrichten
if [[ "$(type -t handle_error)" == "function" ]]; then
    trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR
fi

# Abhängigkeiten prüfen
check_dependencies() {
    echo -e "${BLUE}Prüfe Abhängigkeiten...${NC}"
    
    # Prüfe Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
        return 1
    fi
    
    # Prüfe Docker Compose
    if ! command -v docker compose &> /dev/null; then
        echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose.${NC}"
        return 1
    fi
    
    # Prüfe Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 ist nicht installiert. Bitte installieren Sie Python 3.${NC}"
        return 1
    fi
    
    # Prüfe pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}pip3 ist nicht installiert. Bitte installieren Sie pip3.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Alle Abhängigkeiten sind installiert.${NC}"
    return 0
}

# Hauptfunktion
main() {
    # Setze aktuelle Operation
    CURRENT_OPERATION="start_mcp_servers"
    
    # Prüfe Abhängigkeiten
    check_dependencies || exit 1
    
    # Erstelle Docker-Netzwerk, falls es nicht existiert
    if ! docker network ls | grep -q "dev-server-network"; then
        echo -e "${BLUE}Erstelle Docker-Netzwerk 'dev-server-network'...${NC}"
        docker network create dev-server-network
    fi
    
    # Starte die Server
    if [ "$START_N8N" = true ]; then
        CURRENT_OPERATION="start_n8n_mcp_server"
        CURRENT_CONTAINER="n8n-mcp-server"
        start_n8n_mcp_server
    fi
    
    if [ "$START_OPENHANDS" = true ]; then
        CURRENT_OPERATION="start_openhands_mcp_server"
        CURRENT_CONTAINER="openhands-mcp-server"
        start_openhands_mcp_server
    fi
    
    if [ "$START_GENERATOR" = true ]; then
        CURRENT_OPERATION="start_generator_mcp_server"
        CURRENT_CONTAINER="generator-mcp-server"
        start_generator_mcp_server
    fi
    
    # Wenn keine Server ausgewählt wurden, starte alle
    if [ "$START_N8N" = false ] && [ "$START_OPENHANDS" = false ] && [ "$START_GENERATOR" = false ]; then
        echo -e "${YELLOW}Keine Server ausgewählt. Starte alle Server...${NC}"
        
        CURRENT_OPERATION="start_n8n_mcp_server"
        CURRENT_CONTAINER="n8n-mcp-server"
        start_n8n_mcp_server
        
        CURRENT_OPERATION="start_openhands_mcp_server"
        CURRENT_CONTAINER="openhands-mcp-server"
        start_openhands_mcp_server
        
        CURRENT_OPERATION="start_generator_mcp_server"
        CURRENT_CONTAINER="generator-mcp-server"
        start_generator_mcp_server
    fi
    
    echo -e "${GREEN}Alle Server gestartet${NC}"
    echo "Zum Beenden der Server führen Sie './stop-mcp-servers.sh --all' aus"
}

# Führe die Hauptfunktion aus
main