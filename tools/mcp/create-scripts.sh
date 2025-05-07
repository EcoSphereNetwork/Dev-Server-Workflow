#!/bin/bash

# Erstelle Start-Skripte für MCP-Server und OpenHands
echo "=== Erstelle Start-Skripte ==="

# Lade Umgebungsvariablen
source .env

# MCP-Inspektor
echo "Erstelle MCP-Inspektor-Skript..."
cat > "$HOME/start-mcp-inspector.sh" << 'EOF1'
#!/bin/bash
npx @modelcontextprotocol/inspector
EOF1
chmod +x "$HOME/start-mcp-inspector.sh"

# Ollama-MCP-Bridge
echo "Erstelle Ollama-MCP-Bridge-Skript..."
cat > "$HOME/start-ollama-bridge.sh" << EOF2
#!/bin/bash
cd $HOME/ollama-mcp-bridge
npm start
EOF2
chmod +x "$HOME/start-ollama-bridge.sh"

# OpenHands
echo "Erstelle OpenHands-Skript..."
cat > "$HOME/start-openhands.sh" << EOF3
#!/bin/bash
docker-compose -f $HOME/openhands-docker-compose.yml up -d
echo "OpenHands gestartet unter http://localhost:3000"
EOF3
chmod +x "$HOME/start-openhands.sh"

# Alles-in-einem-Starter
echo "Erstelle All-in-One-Skript..."
cat > "$HOME/start-all-mcp.sh" << EOF4
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
trap "echo 'Stoppe Dienste...'; kill \$OLLAMA_BRIDGE_PID; docker-compose -f '$HOME/openhands-docker-compose.yml' down; echo 'Alle Dienste gestoppt.'" INT
wait
EOF4
chmod +x "$HOME/start-all-mcp.sh"

echo "Start-Skripte erstellt."
