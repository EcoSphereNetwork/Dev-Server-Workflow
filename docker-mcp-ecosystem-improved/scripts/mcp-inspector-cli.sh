#!/bin/bash

# MCP Inspector CLI-Skript
# Dieses Skript ermöglicht die Verwendung des MCP Inspector im CLI-Modus
# für die Interaktion mit MCP-Servern.

# Standardwerte
METHOD="tools/list"
SERVER=""
TOOL_NAME=""
TOOL_ARGS=()
CONFIG_FILE="/app/config/config.json"

# Hilfe-Funktion
function show_help {
    echo "Verwendung: $0 [Optionen]"
    echo ""
    echo "Optionen:"
    echo "  --server SERVER       MCP-Server aus der Konfigurationsdatei"
    echo "  --method METHOD       Methode (tools/list, tools/call, resources/list, prompts/list)"
    echo "  --tool-name NAME      Name des Tools (für tools/call)"
    echo "  --tool-arg KEY=VALUE  Argument für das Tool (mehrfach möglich)"
    echo "  --help                Diese Hilfe anzeigen"
    echo ""
    echo "Beispiele:"
    echo "  $0 --server github --method tools/list"
    echo "  $0 --server desktop-commander --method tools/call --tool-name read_file --tool-arg path=/workspace/README.md"
    echo ""
}

# Parameter verarbeiten
while [[ $# -gt 0 ]]; do
    case "$1" in
        --server)
            SERVER="$2"
            shift 2
            ;;
        --method)
            METHOD="$2"
            shift 2
            ;;
        --tool-name)
            TOOL_NAME="$2"
            shift 2
            ;;
        --tool-arg)
            TOOL_ARGS+=("$2")
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unbekannte Option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfen, ob ein Server angegeben wurde
if [ -z "$SERVER" ]; then
    echo "Fehler: Kein Server angegeben."
    show_help
    exit 1
fi

# Befehl zusammenstellen
CMD="docker exec mcp-inspector-ui npx @modelcontextprotocol/inspector --cli --config $CONFIG_FILE --server $SERVER --method $METHOD"

# Tool-Name hinzufügen, wenn angegeben
if [ -n "$TOOL_NAME" ]; then
    CMD="$CMD --tool-name $TOOL_NAME"
fi

# Tool-Argumente hinzufügen, wenn vorhanden
for arg in "${TOOL_ARGS[@]}"; do
    CMD="$CMD --tool-arg $arg"
done

# Befehl ausführen
eval $CMD