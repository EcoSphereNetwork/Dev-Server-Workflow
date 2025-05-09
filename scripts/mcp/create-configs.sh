#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Erstelle Konfigurationsdateien für MCP-Server und OpenHands
log_info "=== Erstelle Konfigurationsdateien ==="

# Lade Umgebungsvariablen
source .env

# Erstelle Ollama-MCP-Bridge Konfiguration
log_info "Erstelle Ollama-MCP-Bridge Konfiguration..."
cat > ./ollama-mcp-bridge/bridge_config.json << EOF1
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
    "model": "${OLLAMA_MODEL}",
    "baseUrl": "${OLLAMA_BASE_URL}"
  }
}
EOF1

# Erstelle Claude Desktop Konfiguration
log_info "Erstelle Claude Desktop Konfiguration..."
cat > "$HOME/.config/Claude/claude_desktop_config.json" << EOF2
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
EOF2

# Erstelle OpenHands Konfiguration
log_info "Erstelle OpenHands Konfiguration..."
mkdir -p "$OPENHANDS_CONFIG_DIR"
cat > "$OPENHANDS_CONFIG_DIR/config.toml" << EOF3
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
EOF3

# Erstelle Docker-Compose-Datei
log_info "Erstelle Docker-Compose-Datei..."
cat > "$HOME/openhands-docker-compose.yml" << EOF4
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
EOF4

log_info "Konfigurationsdateien erstellt."
