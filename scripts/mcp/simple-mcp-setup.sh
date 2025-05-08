#!/bin/bash

# Einfaches Setup-Skript für MCP-Server und OpenHands

# Erstelle Verzeichnisse
mkdir -p "$HOME/.config/Claude"
mkdir -p "$HOME/.openhands-state"
mkdir -p "$HOME/openhands-workspace"
mkdir -p "$HOME/.config/openhands"

# Installiere MCP-Server
npm install -g @modelcontextprotocol/inspector
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-everything

# Erstelle Claude Desktop Konfiguration
cat > "$HOME/.config/Claude/claude_desktop_config.json" << 'EOF1'
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
      "sseUrl": "http://localhost:3000/mcp"
    }
  }
}
EOF1

# Erstelle OpenHands Docker-Compose-Datei
cat > "$HOME/openhands-docker-compose.yml" << 'EOF2'
version: "3"
services:
  openhands:
    image: docker.all-hands.dev/all-hands-ai/openhands:0.36
    ports:
      - "3000:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - $HOME/.openhands-state:/.openhands-state
      - $HOME/.config/openhands:/config
      - $HOME/openhands-workspace:/workspace
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.36-nikolaik
      - LOG_ALL_EVENTS=true
      - CONFIG_PATH=/config/config.toml
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped
EOF2

# Erstelle OpenHands Konfigurationsdatei
cat > "$HOME/.config/openhands/config.toml" << 'EOF3'
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
EOF3

# Erstelle Start-Skript für OpenHands
cat > "$HOME/start-openhands.sh" << 'EOF4'
#!/bin/bash
docker compose -f $HOME/openhands-docker-compose.yml up -d
echo "OpenHands gestartet unter http://localhost:3000"
EOF4
chmod +x "$HOME/start-openhands.sh"

# Erstelle MCP-Inspektor-Skript
cat > "$HOME/start-mcp-inspector.sh" << 'EOF5'
#!/bin/bash
npx @modelcontextprotocol/inspector
EOF5
chmod +x "$HOME/start-mcp-inspector.sh"

echo "=== Installation abgeschlossen ==="
echo ""
echo "Verfügbare Befehle:"
echo "  $HOME/start-mcp-inspector.sh - Starte den MCP-Inspektor zum Testen der Server"
echo "  $HOME/start-openhands.sh - Starte OpenHands"
echo ""
echo "Wichtige URLs:"
echo "  OpenHands: http://localhost:3000"
echo "  OpenHands MCP: http://localhost:3000/mcp"
echo "  MCP-Inspektor: http://localhost:6274"
echo ""
echo "Starte Claude Desktop neu, um die MCP-Server zu aktivieren."
