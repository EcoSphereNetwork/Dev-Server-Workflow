#!/bin/bash

# MCP-Server und OpenHands Setup Script
# Dieses Script installiert und konfiguriert MCP-Server für Claude Desktop und OpenHands

echo "=== MCP-Server und OpenHands Setup ==="

# Verzeichnisse erstellen
MCP_DIR="$HOME/mcp-servers"
CONFIG_DIR="$HOME/.config/Claude"
OPENHANDS_STATE_DIR="$HOME/.openhands-state"
OPENHANDS_WORKSPACE_DIR="$HOME/openhands-workspace"
OPENHANDS_CONFIG_DIR="$HOME/.config/openhands"

mkdir -p "$MCP_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$OPENHANDS_STATE_DIR"
mkdir -p "$OPENHANDS_WORKSPACE_DIR"
mkdir -p "$OPENHANDS_CONFIG_DIR"

# Lade Umgebungsvariablen aus .env-Datei, falls vorhanden
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo "Lade Umgebungsvariablen aus .env-Datei..."
    set -a
    source "$ENV_FILE"
    set +a
else
    # Erstelle .env-Datei mit Standardwerten
    echo "Erstelle .env-Datei mit Standardwerten..."
    cat > "$ENV_FILE" << ENVEOF
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
    echo "Datei erstellt: $ENV_FILE"
    exit 1
fi

# Installiere MCP-Inspector für Debugging
echo "Installiere MCP-Inspector..."
npm install -g @modelcontextprotocol/inspector

# Installiere bekannte funktionierende MCP-Server
echo "Installiere bekannte funktionierende MCP-Server..."
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-everything

# Installiere Ollama, falls nicht vorhanden
if ! command -v ollama &> /dev/null; then
    echo "Installiere Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "Ollama wurde installiert."
else
    echo "Ollama ist bereits installiert."
fi

# Ziehe das Ollama-Modell
echo "Ziehe Ollama-Modell: ${OLLAMA_MODEL:-qwen2.5-coder:7b-instruct}..."
ollama pull "${OLLAMA_MODEL:-qwen2.5-coder:7b-instruct}"

# Installiere Ollama-MCP-Bridge
echo "Installiere Ollama-MCP-Bridge..."
if [ ! -d "ollama-mcp-bridge" ]; then
    git clone https://github.com/patruff/ollama-mcp-bridge.git
    cd ollama-mcp-bridge
    npm install
    npm run build
    cd ..
else
    echo "Ollama-MCP-Bridge ist bereits installiert."
fi

# Erstelle Konfigurationsdateien
./create-configs.sh

# Erstelle Start-Skripte
./create-scripts.sh

echo "=== Installation abgeschlossen ==="
echo ""
echo "Verfügbare Befehle:"
echo "  $HOME/start-mcp-inspector.sh - Starte den MCP-Inspektor zum Testen der Server"
echo "  $HOME/start-ollama-bridge.sh - Starte die Ollama-MCP-Bridge"
echo "  $HOME/start-openhands.sh - Starte OpenHands"
echo "  $HOME/start-all-mcp.sh - Starte alle Dienste"
echo ""
echo "Wichtige URLs:"
echo "  OpenHands: http://localhost:3000"
echo "  OpenHands MCP: http://localhost:3000/mcp"
echo "  Ollama-MCP-Bridge: http://localhost:8000/mcp"
echo "  MCP-Inspektor: http://localhost:6274"
echo ""
echo "Starte Claude Desktop neu, um die MCP-Server zu aktivieren."
