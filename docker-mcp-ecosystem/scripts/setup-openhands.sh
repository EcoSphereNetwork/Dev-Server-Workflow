#!/bin/bash

# OpenHands-Setup-Skript
# Dieses Skript richtet OpenHands für die Verwendung mit den MCP-Servern ein.

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Standardwerte
OPENHANDS_CONFIG_DIR="$HOME/.config/openhands"
OPENHANDS_PORT=3000

# Hilfe-Funktion
function show_help {
    echo -e "${BLUE}OpenHands-Setup-Skript${NC}"
    echo ""
    echo "Verwendung: $0 [Optionen]"
    echo ""
    echo "Optionen:"
    echo "  --config-dir DIR       Das Konfigurationsverzeichnis für OpenHands (Standard: ~/.config/openhands)"
    echo "  --port PORT            Der Port, auf dem OpenHands laufen soll (Standard: 3000)"
    echo "  --help                 Zeigt diese Hilfe an"
    echo ""
    echo "Beispiele:"
    echo "  $0                                              # Richtet OpenHands mit Standardeinstellungen ein"
    echo "  $0 --config-dir /path/to/config --port 3333     # Richtet OpenHands mit benutzerdefinierten Einstellungen ein"
    echo ""
}

# Parameter verarbeiten
while [[ $# -gt 0 ]]; do
    case "$1" in
        --config-dir)
            OPENHANDS_CONFIG_DIR="$2"
            shift 2
            ;;
        --port)
            OPENHANDS_PORT="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unbekannte Option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Verzeichnis zum Docker-Compose-Projekt wechseln
cd "$(dirname "$0")/.."

# Erstelle das Konfigurationsverzeichnis, falls es nicht existiert
echo -e "${BLUE}Erstelle Konfigurationsverzeichnis für OpenHands...${NC}"
mkdir -p "$OPENHANDS_CONFIG_DIR"

# Erstelle die OpenHands-Konfigurationsdatei
echo -e "${BLUE}Erstelle OpenHands-Konfigurationsdatei...${NC}"
cat > "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[server]
port = $OPENHANDS_PORT
host = "0.0.0.0"

[mcp]
enabled = true

[mcp.servers]
EOF

# Füge alle MCP-Server zur Konfiguration hinzu
echo -e "${BLUE}Füge MCP-Server zur OpenHands-Konfiguration hinzu...${NC}"

# Brave Search MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.brave-search]
url = "http://brave-search-mcp:3001"
description = "Web-Suche mit Brave Search"

EOF

# Filesystem MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.filesystem]
url = "http://filesystem-mcp:3002"
description = "Dateisystem-Operationen"

EOF

# Grafana MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.grafana]
url = "http://grafana-mcp:3003"
description = "Grafana-Dashboard-Verwaltung"

EOF

# Hyperbrowser MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.hyperbrowser]
url = "http://hyperbrowser-mcp:3004"
description = "Webseiten-Navigation und -Interaktion"

EOF

# Wolfram Alpha MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.wolfram-alpha]
url = "http://wolfram-alpha-mcp:3005"
description = "Mathematische und wissenschaftliche Berechnungen"

EOF

# Oxylabs MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.oxylabs]
url = "http://oxylabs-mcp:3006"
description = "Web-Scraping mit Proxy-Unterstützung"

EOF

# E2B MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.e2b]
url = "http://e2b-mcp:3007"
description = "Code-Ausführung in verschiedenen Umgebungen"

EOF

# Desktop Commander MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.desktop-commander]
url = "http://desktop-commander-mcp:3008"
description = "Dateisystem-Operationen und Terminalbefehlsausführung"

EOF

# Sequential Thinking MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.sequential-thinking]
url = "http://sequential-thinking-mcp:3009"
description = "Strukturierte Problemlösung und schrittweise Analyse"

EOF

# Memory MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.memory]
url = "http://memory-mcp:3010"
description = "Persistente Speicherung von Informationen"

EOF

# Basic Memory MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.basic-memory]
url = "http://basic-memory-mcp:3011"
description = "Einfache Speicheroperationen"

EOF

# GitHub MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.github]
url = "http://github-mcp:3012"
description = "GitHub-Repository-Verwaltung und Issue-Tracking"

EOF

# GitHub Chat MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.github-chat]
url = "http://github-chat-mcp:3013"
description = "GitHub-Diskussionen und -Kommentare"

EOF

# GitLab MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.gitlab]
url = "http://gitlab-mcp:3014"
description = "GitLab-Repository-Verwaltung und Issue-Tracking"

EOF

# DuckDuckGo MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.duckduckgo]
url = "http://duckduckgo-mcp:3015"
description = "Websuche mit DuckDuckGo"

EOF

# Wikipedia MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.wikipedia]
url = "http://wikipedia-mcp:3016"
description = "Wikipedia-Artikel-Suche und -Abfrage"

EOF

# n8n MCP Server
cat >> "$OPENHANDS_CONFIG_DIR/config.toml" << EOF
[mcp.servers.n8n]
url = "http://n8n:5678/mcp-endpoint"
description = "n8n-Workflow-Automatisierung"

EOF

# Erstelle die Docker-Compose-Datei für OpenHands
echo -e "${BLUE}Erstelle Docker-Compose-Datei für OpenHands...${NC}"
cat > "$HOME/openhands-docker-compose.yml" << EOF
version: "3"
services:
  openhands:
    image: docker.all-hands.dev/all-hands-ai/openhands:latest
    ports:
      - "$OPENHANDS_PORT:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - $HOME/.openhands-state:/.openhands-state
      - $OPENHANDS_CONFIG_DIR:/config
      - $HOME/openhands-workspace:/workspace
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:latest-nikolaik
      - LOG_ALL_EVENTS=true
      - CONFIG_PATH=/config/config.toml
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped
    networks:
      - mcp-network

networks:
  mcp-network:
    external: true
EOF

# Erstelle das Start-Skript für OpenHands
echo -e "${BLUE}Erstelle Start-Skript für OpenHands...${NC}"
cat > "$HOME/start-openhands.sh" << EOF
#!/bin/bash
docker-compose -f $HOME/openhands-docker-compose.yml up -d
echo "OpenHands gestartet unter http://localhost:$OPENHANDS_PORT"
EOF
chmod +x "$HOME/start-openhands.sh"

echo -e "${GREEN}OpenHands wurde erfolgreich für die Verwendung mit den MCP-Servern eingerichtet.${NC}"
echo -e "${GREEN}Du kannst OpenHands mit dem folgenden Befehl starten:${NC}"
echo -e "${BLUE}$HOME/start-openhands.sh${NC}"