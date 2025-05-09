#!/bin/bash

# Verbessertes Skript zum Starten der MCP-Server
# Verwendet die gemeinsame Bibliothek für konsistente Funktionen und Konfigurationen

# Basisverzeichnis
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

info "=== Starte MCP-Server ==="

# Erstelle Log-Verzeichnis
create_log_directories

# Registriere Signal-Handler
trap stop_all_servers EXIT

# Stoppe alle laufenden Server
stop_all_servers

# Prüfe, ob die n8n MCP-Server-Datei existiert
N8N_MCP_SERVER_PATH=""
if [ -f "${BASE_DIR}/src/n8n_mcp_server.py" ]; then
    N8N_MCP_SERVER_PATH="${BASE_DIR}/src/n8n_mcp_server.py"
elif [ -f "${BASE_DIR}/src/n8n-mcp-server.py" ]; then
    N8N_MCP_SERVER_PATH="${BASE_DIR}/src/n8n-mcp-server.py"
elif [ -f "${BASE_DIR}/improved-n8n-mcp-server.py" ]; then
    N8N_MCP_SERVER_PATH="${BASE_DIR}/improved-n8n-mcp-server.py"
else
    warn "n8n MCP-Server-Skript nicht gefunden. Verwende Standard-Pfad."
    N8N_MCP_SERVER_PATH="/workspace/improved-n8n-mcp-server.py"
fi

# Starte den n8n MCP-Server im HTTP-Modus
start_mcp_server "n8n-mcp" "python3" "$N8N_MCP_SERVER_PATH --mode http --http-port $MCP_HTTP_PORT --n8n-url $N8N_URL --api-key $N8N_API_KEY"

# Installiere und starte den Filesystem MCP-Server
if ! command -v npx &> /dev/null; then
    warn "npx nicht gefunden, installiere @modelcontextprotocol/server-filesystem..."
    npm install -g @modelcontextprotocol/server-filesystem
fi

# Starte den Filesystem MCP-Server
start_mcp_server "filesystem-mcp" "npx" "-y @modelcontextprotocol/server-filesystem --port 3457"

# Starte den GitHub MCP-Server, falls GITHUB_TOKEN gesetzt ist
if [ -n "$GITHUB_TOKEN" ]; then
    start_mcp_server "github-mcp" "npx" "-y @modelcontextprotocol/server-github --port 3458"
fi

# Starte den Brave Search MCP-Server, falls BRAVE_API_KEY gesetzt ist
if [ -n "$BRAVE_API_KEY" ]; then
    start_mcp_server "brave-search-mcp" "npx" "-y @modelcontextprotocol/server-brave-search --port 3459"
fi

# Starte den Memory MCP-Server
start_mcp_server "memory-mcp" "npx" "-y @modelcontextprotocol/server-memory --port 3460"

info "Alle MCP-Server gestartet"
log "n8n MCP-Server: http://localhost:$MCP_HTTP_PORT/mcp"
log "Filesystem MCP-Server: stdio (PID in $LOG_DIR/filesystem-mcp.pid)"
if [ -n "$GITHUB_TOKEN" ]; then
    log "GitHub MCP-Server: stdio (PID in $LOG_DIR/github-mcp.pid)"
fi
if [ -n "$BRAVE_API_KEY" ]; then
    log "Brave Search MCP-Server: stdio (PID in $LOG_DIR/brave-search-mcp.pid)"
fi
log "Memory MCP-Server: stdio (PID in $LOG_DIR/memory-mcp.pid)"
log ""
log "Drücke STRG+C, um alle Server zu beenden"

# Halte das Skript am Laufen
while true; do
    sleep 1
done
