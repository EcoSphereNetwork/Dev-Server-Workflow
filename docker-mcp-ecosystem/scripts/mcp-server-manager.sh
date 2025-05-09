#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# MCP-Server-Manager
# Dieses Skript ermöglicht die Verwaltung der MCP-Server im Ökosystem.

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Standardwerte
ACTION=""
SERVER=""
TOOL=""
ARGS=""

# Hilfe-Funktion
function show_help {
    log_info "${BLUE}MCP-Server-Manager${NC}"
    echo ""
    log_info "Verwendung: $0 [Optionen]"
    echo ""
    log_info "Aktionen:"
    log_info "  list-servers          Listet alle verfügbaren MCP-Server auf"
    log_info "  list-tools            Listet alle verfügbaren Tools eines MCP-Servers auf"
    log_info "  call-tool             Ruft ein Tool eines MCP-Servers auf"
    log_info "  list-resources        Listet alle verfügbaren Ressourcen eines MCP-Servers auf"
    log_info "  get-resource          Ruft eine Ressource eines MCP-Servers ab"
    log_info "  list-prompts          Listet alle verfügbaren Prompts eines MCP-Servers auf"
    log_info "  call-prompt           Ruft einen Prompt eines MCP-Servers auf"
    log_info "  help                  Zeigt diese Hilfe an"
    echo ""
    log_info "Optionen:"
    log_info "  --server SERVER       Der MCP-Server, auf den die Aktion angewendet werden soll"
    log_info "  --tool TOOL           Das Tool, das aufgerufen werden soll"
    log_info "  --args ARGS           Die Argumente für das Tool (JSON-Format)"
    log_info "  --resource RESOURCE   Die Ressource, die abgerufen werden soll"
    log_info "  --prompt PROMPT       Der Prompt, der aufgerufen werden soll"
    log_info "  --prompt-args ARGS    Die Argumente für den Prompt (JSON-Format)"
    echo ""
    log_info "Beispiele:"
    log_info "  $0 list-servers                                # Listet alle verfügbaren MCP-Server auf"
    log_info "  $0 list-tools --server github-mcp              # Listet alle Tools des GitHub MCP-Servers auf"
    log_info "  $0 call-tool --server desktop-commander-mcp --tool read_file --args '{\"path\":\"/workspace/README.md\"}'"
    log_info "  $0 list-resources --server memory-mcp          # Listet alle Ressourcen des Memory MCP-Servers auf"
    echo ""
}

# Parameter verarbeiten
while [[ $# -gt 0 ]]; do
    case "$1" in
        list-servers|list-tools|call-tool|list-resources|get-resource|list-prompts|call-prompt|help)
            ACTION="$1"
            shift
            ;;
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
        --resource)
            RESOURCE="$2"
            shift 2
            ;;
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --prompt-args)
            PROMPT_ARGS="$2"
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
cd /workspace/Dev-Server-Workflow/docker-mcp-ecosystem-improved

# Funktion zum Abrufen der MCP-Server-URL
get_server_url() {
    local server=$1
    local port=$(docker compose exec $server env | grep MCP_PORT | cut -d= -f2)
    log_info "http://$server:$port"
}

# Aktionen ausführen
case "$ACTION" in
    list-servers)
        log_info "${BLUE}Verfügbare MCP-Server:${NC}"
        docker compose config --services | grep -E 'mcp$|mcp-bridge$'
        ;;
    list-tools)
        if [ -z "$SERVER" ]; then
            log_info "${RED}Fehler: Kein MCP-Server angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Verfügbare Tools des MCP-Servers $SERVER:${NC}"
            SERVER_URL=$(get_server_url $SERVER)
            docker compose exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli $SERVER_URL --method tools/list
        fi
        ;;
    call-tool)
        if [ -z "$SERVER" ]; then
            log_info "${RED}Fehler: Kein MCP-Server angegeben.${NC}"
            exit 1
        elif [ -z "$TOOL" ]; then
            log_info "${RED}Fehler: Kein Tool angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Rufe Tool $TOOL des MCP-Servers $SERVER auf:${NC}"
            SERVER_URL=$(get_server_url $SERVER)
            if [ -z "$ARGS" ]; then
                docker compose exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli $SERVER_URL --method tools/call --tool-name $TOOL
            else
                # Extrahiere Schlüssel-Wert-Paare aus dem JSON und übergebe sie als einzelne Argumente
                ARGS_ARRAY=()
                for key in $(echo $ARGS | jq -r 'keys[]'); do
                    value=$(echo $ARGS | jq -r ".[\"$key\"]")
                    ARGS_ARRAY+=("--tool-arg" "$key=$value")
                done
                docker compose exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli $SERVER_URL --method tools/call --tool-name $TOOL "${ARGS_ARRAY[@]}"
            fi
        fi
        ;;
    list-resources)
        if [ -z "$SERVER" ]; then
            log_info "${RED}Fehler: Kein MCP-Server angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Verfügbare Ressourcen des MCP-Servers $SERVER:${NC}"
            SERVER_URL=$(get_server_url $SERVER)
            docker compose exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli $SERVER_URL --method resources/list
        fi
        ;;
    get-resource)
        if [ -z "$SERVER" ]; then
            log_info "${RED}Fehler: Kein MCP-Server angegeben.${NC}"
            exit 1
        elif [ -z "$RESOURCE" ]; then
            log_info "${RED}Fehler: Keine Ressource angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Rufe Ressource $RESOURCE des MCP-Servers $SERVER ab:${NC}"
            SERVER_URL=$(get_server_url $SERVER)
            docker compose exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli $SERVER_URL --method resources/get --resource-id $RESOURCE
        fi
        ;;
    list-prompts)
        if [ -z "$SERVER" ]; then
            log_info "${RED}Fehler: Kein MCP-Server angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Verfügbare Prompts des MCP-Servers $SERVER:${NC}"
            SERVER_URL=$(get_server_url $SERVER)
            docker compose exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli $SERVER_URL --method prompts/list
        fi
        ;;
    call-prompt)
        if [ -z "$SERVER" ]; then
            log_info "${RED}Fehler: Kein MCP-Server angegeben.${NC}"
            exit 1
        elif [ -z "$PROMPT" ]; then
            log_info "${RED}Fehler: Kein Prompt angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Rufe Prompt $PROMPT des MCP-Servers $SERVER auf:${NC}"
            SERVER_URL=$(get_server_url $SERVER)
            if [ -z "$PROMPT_ARGS" ]; then
                docker compose exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli $SERVER_URL --method prompts/call --prompt-id $PROMPT
            else
                # Extrahiere Schlüssel-Wert-Paare aus dem JSON und übergebe sie als einzelne Argumente
                ARGS_ARRAY=()
                for key in $(echo $PROMPT_ARGS | jq -r 'keys[]'); do
                    value=$(echo $PROMPT_ARGS | jq -r ".[\"$key\"]")
                    ARGS_ARRAY+=("--prompt-arg" "$key=$value")
                done
                docker compose exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli $SERVER_URL --method prompts/call --prompt-id $PROMPT "${ARGS_ARRAY[@]}"
            fi
        fi
        ;;
    *)
        log_info "${RED}Unbekannte Aktion: $ACTION${NC}"
        show_help
        exit 1
        ;;
esac