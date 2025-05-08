#!/bin/bash

# Skript zur Behebung von Problemen mit dem MCP-Setup und Änderung des OpenHands-Ports

echo "=== Behebe Probleme mit dem MCP-Setup ==="

# Definiere den benutzerdefinierten Port für OpenHands
CUSTOM_PORT=3333

# 1. Starte Ollama-Service neu
echo "1. Starte Ollama-Service neu..."
sudo systemctl restart ollama || echo "Konnte Ollama-Service nicht neu starten. Möglicherweise läuft er nicht als Systemdienst."
sleep 5

# 2. Versuche erneut, das Ollama-Modell zu ziehen
echo "2. Ziehe Ollama-Modell..."
ollama pull qwen2.5-coder:7b-instruct || echo "Konnte Ollama-Modell nicht ziehen. Stelle sicher, dass Ollama läuft."

# 3. Installiere TypeScript global
echo "3. Installiere TypeScript global..."
sudo npm install -g typescript || npm install -g typescript

# 4. Korrigiere den Pfad zur Ollama-MCP-Bridge
echo "4. Korrigiere den Pfad zur Ollama-MCP-Bridge..."
OLLAMA_BRIDGE_DIR="$HOME/ollama-mcp-bridge"

# Prüfe, ob das Verzeichnis existiert
if [ ! -d "$OLLAMA_BRIDGE_DIR" ]; then
    echo "Erstelle Ollama-MCP-Bridge Verzeichnis..."
    mkdir -p "$OLLAMA_BRIDGE_DIR"
    
    echo "Klone Ollama-MCP-Bridge Repository..."
    git clone https://github.com/patruff/ollama-mcp-bridge.git "$OLLAMA_BRIDGE_DIR"
    
    echo "Installiere Abhängigkeiten..."
    cd "$OLLAMA_BRIDGE_DIR"
    npm install
    
    echo "Baue Ollama-MCP-Bridge..."
    npm run build || echo "Konnte Ollama-MCP-Bridge nicht bauen. Möglicherweise fehlen Berechtigungen."
fi

# 5. Aktualisiere das Start-Skript für Ollama-MCP-Bridge
echo "5. Aktualisiere das Start-Skript für Ollama-MCP-Bridge..."
cat > "$HOME/start-ollama-bridge.sh" << EOFSCRIPT
#!/bin/bash
cd $OLLAMA_BRIDGE_DIR
npm start
EOFSCRIPT
chmod +x "$HOME/start-ollama-bridge.sh"

# 6. Erstelle eine package.json im Home-Verzeichnis als Fallback
echo "6. Erstelle eine package.json im Home-Verzeichnis als Fallback..."
if [ ! -f "$HOME/package.json" ]; then
    cat > "$HOME/package.json" << EOFPACKAGE
{
  "name": "home-directory",
  "version": "1.0.0",
  "description": "Fallback package.json for npm commands",
  "scripts": {
    "start": "echo 'No start script defined'"
  }
}
EOFPACKAGE
fi

# 7. Aktualisiere die Docker-Compose-Datei für OpenHands mit benutzerdefiniertem Port
echo "7. Aktualisiere die Docker-Compose-Datei für OpenHands mit Port $CUSTOM_PORT..."
cat > "$HOME/openhands-docker-compose.yml" << EOFDOCKER
version: "3"
services:
  openhands:
    image: docker.all-hands.dev/all-hands-ai/openhands:0.36
    ports:
      - "$CUSTOM_PORT:3000"
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
EOFDOCKER

# 8. Aktualisiere das Start-Skript für OpenHands
echo "8. Aktualisiere das Start-Skript für OpenHands..."
cat > "$HOME/start-openhands.sh" << EOFOPENHANDS
#!/bin/bash
docker compose -f $HOME/openhands-docker-compose.yml up -d
echo "OpenHands gestartet unter http://localhost:$CUSTOM_PORT"
EOFOPENHANDS
chmod +x "$HOME/start-openhands.sh"

# 9. Aktualisiere das All-in-One-Skript
echo "9. Aktualisiere das All-in-One-Skript..."
cat > "$HOME/start-all-mcp.sh" << EOFALL
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
echo "OpenHands ist unter http://localhost:$CUSTOM_PORT erreichbar."
echo "OpenHands MCP ist unter http://localhost:$CUSTOM_PORT/mcp erreichbar."
echo "Ollama-MCP-Bridge ist unter http://localhost:8000/mcp erreichbar."
echo "Drücke STRG+C, um alle Dienste zu beenden."

# Warte auf Benutzerunterbrechung
trap "echo 'Stoppe Dienste...'; kill \$OLLAMA_BRIDGE_PID; docker compose -f '$HOME/openhands-docker-compose.yml' down; echo 'Alle Dienste gestoppt.'" INT
wait
EOFALL
chmod +x "$HOME/start-all-mcp.sh"

# 10. Aktualisiere die Claude Desktop Konfiguration für den neuen Port
echo "10. Aktualisiere die Claude Desktop Konfiguration für den neuen Port..."
mkdir -p "$HOME/.config/Claude"
cat > "$HOME/.config/Claude/claude_desktop_config.json" << EOFCLAUDE
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
      "sseUrl": "http://localhost:$CUSTOM_PORT/mcp"
    }
  }
}
EOFCLAUDE

echo "=== Problembehebung abgeschlossen ==="
echo ""
echo "OpenHands wurde konfiguriert, um auf Port $CUSTOM_PORT zu laufen."
echo ""
echo "Bitte führe folgende Befehle aus, um die Dienste zu starten:"
echo "  $HOME/start-openhands.sh - Starte OpenHands"
echo "  $HOME/start-ollama-bridge.sh - Starte Ollama-MCP-Bridge"
echo "  $HOME/start-all-mcp.sh - Starte alle Dienste"
echo ""
echo "Wichtige URLs:"
echo "  OpenHands: http://localhost:$CUSTOM_PORT"
echo "  OpenHands MCP: http://localhost:$CUSTOM_PORT/mcp"
echo "  Ollama-MCP-Bridge: http://localhost:8000/mcp"
echo "  MCP-Inspektor: http://localhost:6274"
echo ""
echo "Starte Claude Desktop neu, um die Änderungen zu übernehmen."
