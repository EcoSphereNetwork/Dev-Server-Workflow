#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# MCP-Server-Verwaltungsskript
# Dieses Skript ermöglicht die Verwaltung der MCP-Server.

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Standardwerte
ACTION=""
SERVER=""
LOG_LINES=100

# Hilfe-Funktion
function show_help {
    log_info "${BLUE}MCP-Server-Verwaltungsskript${NC}"
    echo ""
    log_info "Verwendung: $0 [Optionen]"
    echo ""
    log_info "Aktionen:"
    log_info "  start                 Startet alle MCP-Server oder einen bestimmten MCP-Server"
    log_info "  stop                  Stoppt alle MCP-Server oder einen bestimmten MCP-Server"
    log_info "  restart               Startet alle MCP-Server oder einen bestimmten MCP-Server neu"
    log_info "  status                Zeigt den Status aller MCP-Server oder eines bestimmten MCP-Servers an"
    log_info "  logs                  Zeigt die Logs aller MCP-Server oder eines bestimmten MCP-Servers an"
    log_info "  list                  Listet alle verfügbaren MCP-Server auf"
    log_info "  inspect               Zeigt detaillierte Informationen zu einem bestimmten MCP-Server an"
    log_info "  test                  Testet die Verbindung zu einem bestimmten MCP-Server"
    log_info "  help                  Zeigt diese Hilfe an"
    echo ""
    log_info "Optionen:"
    log_info "  --server SERVER       Der MCP-Server, auf den die Aktion angewendet werden soll"
    log_info "  --lines LINES         Anzahl der anzuzeigenden Log-Zeilen (Standard: 100)"
    echo ""
    log_info "Beispiele:"
    log_info "  $0 start                          # Startet alle MCP-Server"
    log_info "  $0 start --server github-mcp      # Startet nur den GitHub MCP-Server"
    log_info "  $0 logs --server github-mcp       # Zeigt die Logs des GitHub MCP-Servers an"
    log_info "  $0 test --server github-mcp       # Testet die Verbindung zum GitHub MCP-Server"
    echo ""
}

# Parameter verarbeiten
while [[ $# -gt 0 ]]; do
    case "$1" in
        start|stop|restart|status|logs|list|inspect|test|help)
            ACTION="$1"
            shift
            ;;
        --server)
            SERVER="$2"
            shift 2
            ;;
        --lines)
            LOG_LINES="$2"
            shift 2
            ;;
        *)
            log_info "${RED}Unbekannte Option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfen, ob eine Aktion angegeben wurde
if [ -z "$ACTION" ]; then
    log_info "${RED}Fehler: Keine Aktion angegeben.${NC}"
    show_help
    exit 1
fi

# Hilfe anzeigen
if [ "$ACTION" == "help" ]; then
    show_help
    exit 0
fi

# Verzeichnis zum Docker-Compose-Projekt wechseln
cd "$(dirname "$0")/.."

# Aktionen ausführen
case "$ACTION" in
    start)
        if [ -z "$SERVER" ]; then
            log_info "${GREEN}Starte alle MCP-Server...${NC}"
            docker compose up -d
        else
            log_info "${GREEN}Starte den MCP-Server $SERVER...${NC}"
            docker compose up -d $SERVER
        fi
        ;;
    stop)
        if [ -z "$SERVER" ]; then
            log_info "${YELLOW}Stoppe alle MCP-Server...${NC}"
            docker compose down
        else
            log_info "${YELLOW}Stoppe den MCP-Server $SERVER...${NC}"
            docker compose stop $SERVER
        fi
        ;;
    restart)
        if [ -z "$SERVER" ]; then
            log_info "${GREEN}Starte alle MCP-Server neu...${NC}"
            docker compose restart
        else
            log_info "${GREEN}Starte den MCP-Server $SERVER neu...${NC}"
            docker compose restart $SERVER
        fi
        ;;
    status)
        if [ -z "$SERVER" ]; then
            log_info "${BLUE}Status aller MCP-Server:${NC}"
            docker compose ps
        else
            log_info "${BLUE}Status des MCP-Servers $SERVER:${NC}"
            docker compose ps $SERVER
        fi
        ;;
    logs)
        if [ -z "$SERVER" ]; then
            log_info "${BLUE}Logs aller MCP-Server (letzte $LOG_LINES Zeilen):${NC}"
            docker compose logs --tail=$LOG_LINES
        else
            log_info "${BLUE}Logs des MCP-Servers $SERVER (letzte $LOG_LINES Zeilen):${NC}"
            docker compose logs --tail=$LOG_LINES $SERVER
        fi
        ;;
    list)
        log_info "${BLUE}Verfügbare MCP-Server:${NC}"
        docker compose config --services | grep -E 'mcp$|mcp-bridge$'
        ;;
    inspect)
        if [ -z "$SERVER" ]; then
            log_info "${RED}Fehler: Kein MCP-Server für die Inspektion angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Detaillierte Informationen zum MCP-Server $SERVER:${NC}"
            docker compose exec $SERVER env
            log_info "\n${BLUE}Container-Informationen:${NC}"
            docker inspect mcp-$SERVER
        fi
        ;;
    test)
        if [ -z "$SERVER" ]; then
            log_info "${RED}Fehler: Kein MCP-Server für den Test angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Teste Verbindung zum MCP-Server $SERVER...${NC}"
            
            # Ermittle den Port des MCP-Servers
            PORT=$(docker compose exec $SERVER env | grep MCP_PORT | cut -d= -f2)
            if [ -z "$PORT" ]; then
                PORT=3000 # Standardport, falls nicht angegeben
            fi
            
            # Teste die Verbindung
            if curl -s "http://$SERVER:$PORT/health" > /dev/null; then
                log_info "${GREEN}Verbindung zum MCP-Server $SERVER erfolgreich.${NC}"
            else
                log_info "${RED}Verbindung zum MCP-Server $SERVER fehlgeschlagen.${NC}"
            fi
        fi
        ;;
    *)
        log_info "${RED}Unbekannte Aktion: $ACTION${NC}"
        show_help
        exit 1
        ;;
esac