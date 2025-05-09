#!/bin/bash

# Verbesserte MCP-Server und OpenHands Installation
# Verwendet die gemeinsame Bibliothek für konsistente Funktionen und Konfigurationen

# Basisverzeichnis
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

info "=== Installiere MCP-Server und OpenHands ==="

# Erstelle .env-Datei, falls nicht vorhanden
if [ ! -f "${BASE_DIR}/.env" ]; then
    info "Erstelle .env-Datei..."
    cat > "${BASE_DIR}/.env" << 'ENVEOF'
# ---------- API-Keys ----------
BRAVE_API_KEY=""
GITHUB_TOKEN=""
GITLAB_TOKEN=""
GITLAB_URL="https://gitlab.ecospherenet.work"
WOLFRAM_APP_ID=""

# ---------- GitHub Benutzerinformationen ----------
GITHUB_USERNAME="161sam"
GITHUB_EMAIL="sschimmelpfennig@proton.me"

# ---------- Pfad-Konfigurationen ----------
WORKSPACE_PATH="$HOME"

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
ENVEOF
    warn "Bitte fülle die API-Keys in der .env-Datei aus und starte das Script erneut."
    exit 1
fi

# Installiere MCP-Server
install_mcp_servers

# Installiere Ollama-MCP-Bridge
install_ollama_bridge

# Erstelle Konfigurationen
create_openhands_config
create_claude_config

# Erstelle Start-Skripte
create_start_scripts

info "=== Installation abgeschlossen ==="
log "Führe '$HOME/start-all-mcp.sh' aus, um alle Dienste zu starten."
log "OpenHands ist unter http://localhost:${OPENHANDS_PORT} erreichbar."
log "Ollama-MCP-Bridge ist unter http://localhost:${OLLAMA_PORT}/mcp erreichbar."
