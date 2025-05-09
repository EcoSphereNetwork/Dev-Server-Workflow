#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# MCP-Server-Testskript
# Dieses Skript testet die Funktionalität der MCP-Server.

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Standardwerte
SERVER=""
TOOL=""
ARGS="{}"

# Hilfe-Funktion
function show_help {
    log_info "${BLUE}MCP-Server-Testskript${NC}"
    echo ""
    log_info "Verwendung: $0 [Optionen]"
    echo ""
    log_info "Optionen:"
    log_info "  --server SERVER       Der zu testende MCP-Server (erforderlich)"
    log_info "  --tool TOOL           Das zu testende Tool (optional)"
    log_info "  --args ARGS           Die Argumente für das Tool im JSON-Format (optional)"
    log_info "  --help                Zeigt diese Hilfe an"
    echo ""
    log_info "Beispiele:"
    log_info "  $0 --server github-mcp                                # Testet den GitHub MCP-Server"
    log_info "  $0 --server github-mcp --tool list_repos              # Testet das Tool list_repos des GitHub MCP-Servers"
    log_info "  $0 --server github-mcp --tool create_issue --args '{\"owner\":\"user\",\"repo\":\"repo\",\"title\":\"Test\",\"body\":\"Test\"}'"
    echo ""
}

# Parameter verarbeiten
while [[ $# -gt 0 ]]; do
    case "$1" in
        --server)
            SERVER="$2"
            shift 2
            ;;
        --tool)
            TOOL="$2"
            shift 2
            ;;
        --args)
            ARGS="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_info "${RED}Unbekannte Option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfen, ob ein Server angegeben wurde
if [ -z "$SERVER" ]; then
    log_info "${RED}Fehler: Kein MCP-Server angegeben.${NC}"
    show_help
    exit 1
fi

# Verzeichnis zum Docker-Compose-Projekt wechseln
cd "$(dirname "$0")/.."

# Ermittle den Port des MCP-Servers
PORT=$(docker compose exec $SERVER env | grep MCP_PORT | cut -d= -f2)
if [ -z "$PORT" ]; then
    PORT=3000 # Standardport, falls nicht angegeben
fi

# Teste die Verbindung zum MCP-Server
log_info "${BLUE}Teste Verbindung zum MCP-Server $SERVER...${NC}"
if ! curl -s "http://$SERVER:$PORT/health" > /dev/null; then
    log_info "${RED}Verbindung zum MCP-Server $SERVER fehlgeschlagen.${NC}"
    exit 1
fi
log_info "${GREEN}Verbindung zum MCP-Server $SERVER erfolgreich.${NC}"

# Wenn kein Tool angegeben wurde, liste alle verfügbaren Tools auf
if [ -z "$TOOL" ]; then
    log_info "${BLUE}Liste verfügbare Tools des MCP-Servers $SERVER auf...${NC}"
    curl -s -X POST -H "Content-Type: application/json" -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.listTools"
    }' "http://$SERVER:$PORT/mcp" | jq .
else
    # Teste das angegebene Tool
    log_info "${BLUE}Teste Tool $TOOL des MCP-Servers $SERVER...${NC}"
    curl -s -X POST -H "Content-Type: application/json" -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.callTool",
        "params": {
            "name": "'$TOOL'",
            "arguments": '"$ARGS"'
        }
    }' "http://$SERVER:$PORT/mcp" | jq .
fi