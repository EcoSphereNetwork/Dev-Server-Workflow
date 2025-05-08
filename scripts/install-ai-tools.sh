#!/bin/bash

# Installationsscript für MCP-Server und OpenHands

echo "Starte Installation der MCP-Server für Claude Desktop und OpenHands..."

# Erstelle .env-Datei, falls nicht vorhanden
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo "Lade Umgebungsvariablen aus .env-Datei..."
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Keine .env-Datei gefunden, verwende Standardwerte."
fi

# Hauptverzeichnis für MCP-Server
MCP_DIR="$HOME/mcp-servers"
mkdir -p "$MCP_DIR"

# Erstelle Konfigurationsverzeichnis für Claude Desktop
CONFIG_DIR="$HOME/.config/Claude"
mkdir -p "$CONFIG_DIR"
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

# Prüfe verfügbare MCP-Server (bekannt funktionierend)
echo "Installiere bekannte funktionierende MCP-Server..."

# Array der bekannten funktionierenden Server
WORKING_SERVERS=(
    "@modelcontextprotocol/server-filesystem"
    "@modelcontextprotocol/server-brave-search"
    "@modelcontextprotocol/server-github"
    "@modelcontextprotocol/server-gitlab"
    "@modelcontextprotocol/server-memory"
    "@modelcontextprotocol/server-everything"
    "@patruff/server-flux"
    "@patruff/server-gmail-drive"
)

# Installiere jeden Server global
for server in "${WORKING_SERVERS[@]}"; do
    echo "Installiere $server..."
    npm install -g "$server" || echo "Fehler beim Installieren von $server, wird übersprungen."
done

# Alternative Installation mit Docker für Server, die mit npm Probleme haben
echo "Installiere Docker-basierte MCP-Server..."

# Erstelle die Claude Desktop Konfigurationsdatei
echo "Erstelle Claude Desktop Konfigurationsdatei unter: $CONFIG_FILE"

cat > "$CONFIG_FILE" <<EOL
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
    "gitlab": {
      "command": "npx", 
      "args": [
        "-y",
        "@modelcontextprotocol/server-gitlab"
      ],
      "env": {
        "GITLAB_TOKEN": "${GITLAB_TOKEN}",
        "GITLAB_URL": "${GITLAB_URL}"
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
    "flux": {
      "command": "npx",
      "args": [
        "-y",
        "@patruff/server-flux"
      ],
      "env": {
        "REPLICATE_API_TOKEN": "${REPLICATE_API_TOKEN}"
      }
    },
    "gmail-drive": {
      "command": "npx",
      "args": [
        "-y",
        "@patruff/server-gmail-drive"
      ]
    },
    "openhands": {
      "sseUrl": "http://localhost:3000/mcp"
    }
  }
}
EOL

# OpenHands Installation und Konfiguration
OPENHANDS_STATE_DIR="${OPENHANDS_STATE_DIR:-$HOME/.openhands-state}"
OPENHANDS_WORKSPACE_DIR="${OPENHANDS_WORKSPACE_DIR:-$HOME/openhands-workspace}"
OPENHANDS_CONFIG_DIR="${OPENHANDS_CONFIG_DIR:-$HOME/.config/openhands}"

mkdir -p "${OPENHANDS_STATE_DIR}"
mkdir -p "${OPENHANDS_WORKSPACE_DIR}"
mkdir -p "${OPENHANDS_CONFIG_DIR}"

# Erstelle OpenHands Konfigurationsdatei
echo "Erstelle OpenHands Konfigurationsdatei..."
OPENHANDS_CONFIG_FILE="${OPENHANDS_CONFIG_DIR}/config.toml"

cat > "$OPENHANDS_CONFIG_FILE" <<EOL
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
sse_servers = []

# Standard MCP-Server über Stdio
stdio_servers = [
    { name = "filesystem", command = "npx", args = ["-y", "@modelcontextprotocol/server-filesystem"] },
    { name = "brave-search", command = "npx", args = ["-y", "@modelcontextprotocol/server-brave-search"], env = { BRAVE_API_KEY = "${BRAVE_API_KEY}" } },
    { name = "github", command = "npx", args = ["-y", "@modelcontextprotocol/server-github"], env = { GITHUB_TOKEN = "${GITHUB_TOKEN}" } },
    { name = "memory", command = "npx", args = ["-y", "@modelcontextprotocol/server-memory"] }
]
EOL

# Erstelle Docker-Compose-Datei für OpenHands
DOCKER_COMPOSE_FILE="$HOME/openhands-docker-compose.yml"

cat > "$DOCKER_COMPOSE_FILE" <<EOL
version: '3'
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
EOL

# Erstelle MCP-Inspektor-Start-Script
MCP_INSPECTOR_SCRIPT="$HOME/start-mcp-inspector.sh"

cat > "$MCP_INSPECTOR_SCRIPT" <<EOL
#!/bin/bash

# Starte MCP-Inspektor für Server-Debugging
npx @modelcontextprotocol/inspector
EOL

chmod +x "$MCP_INSPECTOR_SCRIPT"

# Erstelle Start-Script für OpenHands
OPENHANDS_SCRIPT="$HOME/start-openhands.sh"

cat > "$OPENHANDS_SCRIPT" <<EOL
#!/bin/bash

# Starte OpenHands Container
docker compose -f $DOCKER_COMPOSE_FILE up -d
echo "OpenHands gestartet unter http://localhost:3000"
EOL

chmod +x "$OPENHANDS_SCRIPT"

echo "Installation abgeschlossen!"
echo "MCP-Server Konfiguration wurde in $CONFIG_FILE erstellt."
echo "OpenHands kann mit '$OPENHANDS_SCRIPT' gestartet werden."
echo "MCP-Inspektor kann mit '$MCP_INSPECTOR_SCRIPT' gestartet werden, um MCP-Server zu testen."
echo "Starte Claude Desktop neu, um die Änderungen zu übernehmen."
