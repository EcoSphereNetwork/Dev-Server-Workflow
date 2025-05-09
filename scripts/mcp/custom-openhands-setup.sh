#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Angepasstes Setup-Skript für OpenHands mit benutzerdefiniertem Port und Workspace

# Definiere den benutzerdefinierten Port und Workspace
CUSTOM_PORT=3333
WORKSPACE_DIR="/home/sam"
OPENHANDS_STATE_DIR="$HOME/.openhands-state"
OPENHANDS_CONFIG_DIR="$HOME/.config/openhands"

# Erstelle Verzeichnisse
mkdir -p "$OPENHANDS_STATE_DIR"
mkdir -p "$OPENHANDS_CONFIG_DIR"

# Erstelle angepasste Docker-Compose-Datei
cat > "$HOME/openhands-docker-compose.yml" << EOF1
version: "3"
services:
  openhands:
    image: docker.all-hands.dev/all-hands-ai/openhands:0.36
    ports:
      - "${CUSTOM_PORT}:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${OPENHANDS_STATE_DIR}:/.openhands-state
      - ${OPENHANDS_CONFIG_DIR}:/config
      - ${WORKSPACE_DIR}:/workspace
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.36-nikolaik
      - LOG_ALL_EVENTS=true
      - CONFIG_PATH=/config/config.toml
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped
EOF1

# Erstelle OpenHands Konfigurationsdatei
cat > "$OPENHANDS_CONFIG_DIR/config.toml" << EOF2
[core]
debug = false
disable_color = false
cache_dir = "/tmp/cache"
save_trajectory_path = "/.openhands-state/trajectories"
file_store_path = "/.openhands-state/file_store"
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
volumes = "/workspace:/workspace:rw"

[security]
confirmation_mode = false
security_analyzer = ""

[mcp]
# Standard MCP-Server über Stdio
stdio_servers = [
    { name = "filesystem", command = "npx", args = ["-y", "@modelcontextprotocol/server-filesystem"] },
    { name = "brave-search", command = "npx", args = ["-y", "@modelcontextprotocol/server-brave-search"] },
    { name = "github", command = "npx", args = ["-y", "@modelcontextprotocol/server-github"] },
    { name = "memory", command = "npx", args = ["-y", "@modelcontextprotocol/server-memory"] }
]
EOF2

# Aktualisiere die Claude Desktop Konfiguration für den neuen Port
cat > "$HOME/.config/Claude/claude_desktop_config.json" << EOF3
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
        "BRAVE_API_KEY": ""
      }
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": ""
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
    "openhands": {
      "sseUrl": "http://localhost:${CUSTOM_PORT}/mcp"
    }
  }
}
EOF3

# Erstelle Start-Skript für OpenHands
cat > "$HOME/start-openhands.sh" << EOF4
#!/bin/bash
docker compose -f $HOME/openhands-docker-compose.yml up -d
log_info "OpenHands gestartet unter http://localhost:${CUSTOM_PORT}"
EOF4
chmod +x "$HOME/start-openhands.sh"

log_info "=== Angepasste OpenHands-Konfiguration abgeschlossen ==="
echo ""
log_info "OpenHands wurde konfiguriert, um auf Port ${CUSTOM_PORT} zu laufen."
log_info "Der Workspace-Pfad wurde auf ${WORKSPACE_DIR} gesetzt."
echo ""
log_info "Starte OpenHands mit:"
log_info "  $HOME/start-openhands.sh"
echo ""
log_info "OpenHands wird verfügbar sein unter:"
log_info "  http://localhost:${CUSTOM_PORT}"
log_info "  MCP-Endpunkt: http://localhost:${CUSTOM_PORT}/mcp"
echo ""
log_info "Starte Claude Desktop neu, um die Änderungen zu übernehmen."
