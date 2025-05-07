#!/bin/bash

# Installiere MCP-Server und OpenHands
echo "=== Installiere MCP-Server und OpenHands ==="

# Erstelle .env-Datei, falls nicht vorhanden
if [ ! -f ".env" ]; then
    cat > .env << 'ENVEOF'
# API-Keys
BRAVE_API_KEY=""
GITHUB_TOKEN=""
GITLAB_TOKEN=""
GITLAB_URL="https://gitlab.ecospherenet.work"
WOLFRAM_APP_ID=""

# GitHub Benutzerinformationen
GITHUB_USERNAME="161sam"
GITHUB_EMAIL="sschimmelpfennig@proton.me"

# Pfad-Konfigurationen
WORKSPACE_PATH="/home/sam"

# Ollama-Konfiguration
OLLAMA_MODEL="qwen2.5-coder:7b-instruct"
OLLAMA_BASE_URL="http://localhost:11434"

# OpenHands-Konfiguration
OPENHANDS_STATE_DIR="/home/sam/.openhands-state"
OPENHANDS_WORKSPACE_DIR="/home/sam/openhands-workspace"
OPENHANDS_CONFIG_DIR="/home/sam/.config/openhands"
ENVEOF
    echo "Bitte fülle die API-Keys in der .env-Datei aus und starte das Script erneut."
    exit 1
fi

# Lade Umgebungsvariablen
source .env

# Erstelle Verzeichnisse
mkdir -p "$HOME/.config/Claude"
mkdir -p "$OPENHANDS_STATE_DIR"
mkdir -p "$OPENHANDS_WORKSPACE_DIR"
mkdir -p "$OPENHANDS_CONFIG_DIR"

# Installiere MCP-Server
echo "Installiere MCP-Server..."
npm install -g @modelcontextprotocol/inspector
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-everything

# Installiere Ollama-MCP-Bridge
echo "Installiere Ollama-MCP-Bridge..."
if [ ! -d "ollama-mcp-bridge" ]; then
    git clone https://github.com/patruff/ollama-mcp-bridge.git
    cd ollama-mcp-bridge
    npm install
    npm run build
    cd ..
fi

# Erstelle Konfigurationsdateien
./create-configs.sh

# Erstelle Start-Skripte
./create-scripts.sh

echo "=== Installation abgeschlossen ==="
echo "Führe './start-all-mcp.sh' aus, um alle Dienste zu starten."
