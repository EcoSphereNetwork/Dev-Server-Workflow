#!/bin/bash

# Vereinfachtes Setup-Skript für MCP-Server und OpenHands
# Verwendet die gemeinsame Bibliothek für konsistente Funktionen und Konfigurationen

# Basisverzeichnis
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

info "=== Einfaches MCP-Server und OpenHands Setup ==="

# Erstelle eine einfache .env-Datei, falls nicht vorhanden
if [ ! -f "${BASE_DIR}/.env" ]; then
    info "Erstelle einfache .env-Datei..."
    cat > "${BASE_DIR}/.env" << EOF
# ---------- API-Keys ----------
BRAVE_API_KEY=""
GITHUB_TOKEN=""

# ---------- Ollama-Konfiguration ----------
OLLAMA_MODEL="qwen2.5-coder:7b-instruct"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_PORT=8000

# ---------- OpenHands-Konfiguration ----------
OPENHANDS_PORT=3000
OPENHANDS_STATE_DIR="$HOME/.openhands-state"
OPENHANDS_WORKSPACE_DIR="$HOME/openhands-workspace"
OPENHANDS_CONFIG_DIR="$HOME/.config/openhands"
OPENHANDS_MAX_WORKERS=5

# ---------- n8n Konfiguration ----------
N8N_URL="http://localhost:5678"
N8N_API_KEY=""
MCP_HTTP_PORT=3333

# ---------- Logging Konfiguration ----------
LOG_DIR="/tmp/mcp-logs"
EOF
    warn "Bitte fülle die API-Keys in der .env-Datei aus, falls benötigt."
fi

# Lade die .env-Datei
source "${BASE_DIR}/.env"

# Installiere MCP-Server
install_mcp_servers

# Erstelle Konfigurationen
create_openhands_config
create_claude_config

# Erstelle Start-Skripte
create_start_scripts

info "=== Installation abgeschlossen ==="
log ""
log "Verfügbare Befehle:"
log "  $HOME/start-mcp-inspector.sh - Starte den MCP-Inspektor zum Testen der Server"
log "  $HOME/start-openhands.sh - Starte OpenHands"
log ""
log "Wichtige URLs:"
log "  OpenHands: http://localhost:${OPENHANDS_PORT}"
log "  OpenHands MCP: http://localhost:${OPENHANDS_PORT}/mcp"
log "  MCP-Inspektor: http://localhost:6274"
log ""
log "Starte Claude Desktop neu, um die MCP-Server zu aktivieren."
