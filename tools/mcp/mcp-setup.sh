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

# Erstelle Konfigurationsdatei für die Ollama-MCP-Bridge
BRIDGE_CONFIG_FILE="./ollama-mcp-bridge/bridge_config.json"
echo "Erstelle Bridge-Konfigurationsdatei unter: $BRIDGE_CONFIG_FILE"

cat > "$BRIDGE_CONFIG_FILE" << EOFBRIDGE
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    }
  },
  "llm": {
    "model": "${OLLAMA_MODEL:-qwen2.5-coder:7b-instruct}",
    "baseUrl": "${OLLAMA_BASE_URL:-http://localhost:11434}"
  }
}
EOFBRIDGE

# Erstelle Claude Desktop Konfigurationsdatei
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
echo "Erstelle Claude Desktop Konfigurationsdatei unter: $CONFIG_FILE"

cat > "$CONFIG_FILE" << EOFCLAUDE
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    },
    "everything": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-everything"
      ]
    },
    "ollama-bridge": {
      "sseUrl": "http://localhost:8000/mcp"
    },
    "openhands": {
      "sseUrl": "http://localhost:3000/mcp"
    }
  }
}
EOFCLAUDE

# Erstelle OpenHands Konfigurationsdatei
OPENHANDS_CONFIG_FILE="${OPENHANDS_CONFIG_DIR}/config.toml"
echo "Erstelle OpenHands Konfigurationsdatei unter: $OPENHANDS_CONFIG_FILE"

cat > "$OPENHANDS_CONFIG_FILE" << EOFOPENHANDS
[core]
debug = false
disable_color = false
cache_dir = "/tmp/cache"
save_trajectory_path = "${OPENHANDS_STATE_DIR}/trajectories"
file_store_path = "${OPENHANDS_STATE_DIR}/file_store"
file_store = "memory"
file_uploads_allowed_extensions = [".*"]
file_uploads_max_file_size_mb = 0
file_uploads_restrict_file_types = false
max_budget_per_task = 0.0
max_iterations = 100
run_as_openhands = true
runtime = "docker"
default_agent = "CodeActAgent"
jwt_secret = "replace-with-a-secure-random-key"

[llm]
model = "claude-3-5-sonnet-20241022"
num_retries = 8
retry_max_wait = 120
retry_min_wait = 15
retry_multiplier = 2.0
drop_params = false
caching_prompt = true
temperature = 0.0
timeout = 0
top_p = 1.0
max_message_chars = 30000

[agent]
llm_config = "default"
function_calling = true
enable_browsing = true
enable_llm_editor = false
enable_jupyter = false
enable_history_truncation = true
enable_prompt_extensions = true

[sandbox]
timeout = 120
user_id = 1000
base_container_image = "docker.all-hands.dev/all-hands-ai/runtime:0.36-nikolaik"
use_host_network = false
runtime_binding_address = "0.0.0.0"
enable_auto_lint = false
initialize_plugins = true
volumes = "${OPENHANDS_WORKSPACE_DIR}:/workspace:rw"

[security]
confirmation_mode = false
security_analyzer = ""

[mcp]
# SSE-Server für Ollama-MCP-Bridge
sse_servers = [
  "http://localhost:8000/mcp"
]

# Standard MCP-Server über Stdio
stdio_servers = [
    { name = "filesystem", command = "npx", args = ["-y", "@modelcontextprotocol/server-filesystem"] },
    { name = "brave-search", command = "npx", args = ["-y", "@modelcontextprotocol/server-brave-search"], env = { BRAVE_API_KEY = "${BRAVE_API_KEY}" } },
    { name = "github", command = "npx", args = ["-y", "@modelcontextprotocol/server-github"], env = { GITHUB_TOKEN = "${GITHUB_TOKEN}" } },
    { name = "memory", command = "npx", args = ["-y", "@modelcontextprotocol/server-memory"] }
]
EOFOPENHANDS

# Erstelle Docker-Compose-Datei für OpenHands
DOCKER_COMPOSE_FILE="$HOME/openhands-docker-compose.yml"
echo "Erstelle Docker-Compose-Datei unter: $DOCKER_COMPOSE_FILE"

cat > "$DOCKER_COMPOSE_FILE" << EOFDOCKER
version: "3"
services:
  openhands:
    image: docker.all-hands.dev/all-hands-ai/openhands:0.36
    ports:
      - "3000:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${OPENHANDS_STATE_DIR}:/.openhands-state
      - ${OPENHANDS_CONFIG_DIR}:/config
      - ${OPENHANDS_WORKSPACE_DIR}:/workspace
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.36-nikolaik
      - LOG_ALL_EVENTS=true
      - CONFIG_PATH=/config/config.toml
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped
EOFDOCKER

# Erstelle Start-Skripte
echo "Erstelle Start-Skripte..."

# MCP-Inspektor
MCP_INSPECTOR_SCRIPT="$HOME/start-mcp-inspector.sh"
cat > "$MCP_INSPECTOR_SCRIPT" << EOFMCPINSPECTOR
#!/bin/bash
npx @modelcontextprotocol/inspector
EOFMCPINSPECTOR
chmod +x "$MCP_INSPECTOR_SCRIPT"

# Ollama-MCP-Bridge
OLLAMA_BRIDGE_SCRIPT="$HOME/start-ollama-bridge.sh"
cat > "$OLLAMA_BRIDGE_SCRIPT" << EOFOLLAMA
#!/bin/bash
cd $HOME/ollama-mcp-bridge
npm start
EOFOLLAMA
chmod +x "$OLLAMA_BRIDGE_SCRIPT"

# OpenHands
OPENHANDS_SCRIPT="$HOME/start-openhands.sh"
cat > "$OPENHANDS_SCRIPT" << EOFOPENHANDS
#!/bin/bash
docker-compose -f $DOCKER_COMPOSE_FILE up -d
echo "OpenHands gestartet unter http://localhost:3000"
EOFOPENHANDS
chmod +x "$OPENHANDS_SCRIPT"

# Alles-in-einem-Starter
ALL_IN_ONE_SCRIPT="$HOME/start-all-mcp.sh"
cat > "$ALL_IN_ONE_SCRIPT" << EOFALL
#!/bin/bash

# Starte alle MCP-Dienste
echo "Starte alle MCP-Dienste..."

# Starte OpenHands
echo "Starte OpenHands..."
$HOME/start-openhands.sh

# Starte Ollama-MCP-Bridge im Hintergrund
echo "Starte Ollama-MCP-Bridge..."
$HOME/start-ollama-bridge.sh &
OLLAMA_BRIDGE_PID=\$!

echo "Alle Dienste wurden gestartet!"
echo "OpenHands ist unter http://localhost:3000 erreichbar."
echo "Ollama-MCP-Bridge ist unter http://localhost:8000/mcp erreichbar."
echo "Drücke STRG+C, um alle Dienste zu beenden."

# Warte auf Benutzerunterbrechung
trap "echo 'Stoppe Dienste...'; kill \$OLLAMA_BRIDGE_PID; docker-compose -f '$DOCKER_COMPOSE_FILE' down; echo 'Alle Dienste gestoppt.'" INT
wait
EOFALL
chmod +x "$ALL_IN_ONE_SCRIPT"

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
