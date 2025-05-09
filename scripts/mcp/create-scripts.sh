#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Erstelle Start-Skripte für MCP-Server und OpenHands
log_info "=== Erstelle Start-Skripte ==="

# Lade Umgebungsvariablen
source .env

# MCP-Inspektor
log_info "Erstelle MCP-Inspektor-Skript..."
cat > "$HOME/start-mcp-inspector.sh" << 'EOF1'
#!/bin/bash
npx @modelcontextprotocol/inspector
EOF1
chmod +x "$HOME/start-mcp-inspector.sh"

# Ollama-MCP-Bridge
log_info "Erstelle Ollama-MCP-Bridge-Skript..."
cat > "$HOME/start-ollama-bridge.sh" << EOF2
#!/bin/bash
cd $HOME/ollama-mcp-bridge
npm start
EOF2
chmod +x "$HOME/start-ollama-bridge.sh"

# OpenHands
log_info "Erstelle OpenHands-Skript..."
cat > "$HOME/start-openhands.sh" << EOF3
#!/bin/bash
docker compose -f $HOME/openhands-docker-compose.yml up -d
log_info "OpenHands gestartet unter http://localhost:3000"
EOF3
chmod +x "$HOME/start-openhands.sh"

# Alles-in-einem-Starter
log_info "Erstelle All-in-One-Skript..."
cat > "$HOME/start-all-mcp.sh" << EOF4
#!/bin/bash

# Starte alle MCP-Dienste
log_info "Starte alle MCP-Dienste..."

# Starte OpenHands
log_info "Starte OpenHands..."
$HOME/start-openhands.sh

# Starte Ollama-MCP-Bridge im Hintergrund
log_info "Starte Ollama-MCP-Bridge..."
$HOME/start-ollama-bridge.sh &
OLLAMA_BRIDGE_PID=\$!

log_info "Alle Dienste wurden gestartet!"
log_info "OpenHands ist unter http://localhost:3000 erreichbar."
log_info "Ollama-MCP-Bridge ist unter http://localhost:8000/mcp erreichbar."
log_info "Drücke STRG+C, um alle Dienste zu beenden."

# Warte auf Benutzerunterbrechung
trap "echo 'Stoppe Dienste...'; kill \$OLLAMA_BRIDGE_PID; docker compose -f '$HOME/openhands-docker-compose.yml' down; echo 'Alle Dienste gestoppt.'" INT
wait
EOF4
chmod +x "$HOME/start-all-mcp.sh"

log_info "Start-Skripte erstellt."
