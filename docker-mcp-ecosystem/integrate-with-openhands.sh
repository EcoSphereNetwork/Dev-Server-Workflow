#!/bin/bash

# MCP-Server OpenHands Integration
# Dieses Skript integriert die MCP-Server mit OpenHands

set -e

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Standardwerte
OPENHANDS_CONFIG_DIR="${OPENHANDS_CONFIG_DIR:-$HOME/.config/openhands}"
OPENHANDS_STATE_DIR="${OPENHANDS_STATE_DIR:-$HOME/.openhands-state}"
OPENHANDS_WORKSPACE_DIR="${OPENHANDS_WORKSPACE_DIR:-$HOME/workspace}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
OPENHANDS_PORT="${OPENHANDS_PORT:-3000}"

# Banner anzeigen
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   MCP-Server OpenHands Integration                        ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Prüfe, ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Prüfe, ob Docker Compose installiert ist
if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Prüfe, ob die MCP-Server laufen
echo -e "${YELLOW}Prüfe, ob die MCP-Server laufen...${NC}"
if ! docker ps | grep -q "mcp-filesystem"; then
    echo -e "${YELLOW}Die MCP-Server scheinen nicht zu laufen. Möchten Sie sie jetzt starten? (j/n)${NC}"
    read -r START_SERVERS
    if [[ "$START_SERVERS" =~ ^[Jj]$ ]]; then
        echo -e "${YELLOW}Starte MCP-Server...${NC}"
        ./start-mcp-ecosystem.sh
    else
        echo -e "${YELLOW}Bitte starten Sie die MCP-Server manuell mit ./start-mcp-ecosystem.sh${NC}"
        echo -e "${YELLOW}Die Integration wird fortgesetzt, aber OpenHands wird möglicherweise nicht korrekt funktionieren.${NC}"
    fi
fi

# Erstelle die OpenHands-Konfigurationsverzeichnisse
echo -e "${YELLOW}Erstelle OpenHands-Konfigurationsverzeichnisse...${NC}"
mkdir -p "$OPENHANDS_CONFIG_DIR"
mkdir -p "$OPENHANDS_STATE_DIR"
mkdir -p "$OPENHANDS_WORKSPACE_DIR"

# Kopiere die TOML-Konfigurationsdatei
echo -e "${YELLOW}Kopiere OpenHands-Konfigurationsdatei...${NC}"
cp openhands-config.toml "$OPENHANDS_CONFIG_DIR/config.toml"

# Ersetze Umgebungsvariablen in der Konfigurationsdatei
echo -e "${YELLOW}Passe Konfiguration an...${NC}"
sed -i "s|\${GITHUB_TOKEN}|$GITHUB_TOKEN|g" "$OPENHANDS_CONFIG_DIR/config.toml"
sed -i "s|volumes = \"/workspace:/workspace:rw\"|volumes = \"$OPENHANDS_WORKSPACE_DIR:/workspace:rw\"|g" "$OPENHANDS_CONFIG_DIR/config.toml"

# Erstelle Docker-Compose-Datei für OpenHands
echo -e "${YELLOW}Erstelle Docker-Compose-Datei für OpenHands...${NC}"
cat > "$HOME/openhands-docker-compose.yml" << EOF
version: "3"
services:
  openhands:
    image: docker.all-hands.dev/all-hands-ai/openhands:0.36
    ports:
      - "${OPENHANDS_PORT}:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${OPENHANDS_STATE_DIR}:/.openhands-state
      - ${OPENHANDS_CONFIG_DIR}:/config
      - ${OPENHANDS_WORKSPACE_DIR}:/workspace
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.36-nikolaik
      - LOG_ALL_EVENTS=true
      - CONFIG_PATH=/config/config.toml
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    extra_hosts:
      - host.docker.internal:host-gateway
    networks:
      - mcp-network
      - default
    restart: unless-stopped

networks:
  mcp-network:
    external: true
EOF

# Erstelle Start-Skript für OpenHands
echo -e "${YELLOW}Erstelle Start-Skript für OpenHands...${NC}"
cat > "$HOME/start-openhands.sh" << EOF
#!/bin/bash

# Starte OpenHands mit Docker Compose
cd \$HOME
docker compose -f openhands-docker-compose.yml up -d

echo "OpenHands wurde gestartet und ist verfügbar unter:"
echo "  http://localhost:${OPENHANDS_PORT}"
echo "  MCP-Endpunkt: http://localhost:${OPENHANDS_PORT}/mcp"
EOF
chmod +x "$HOME/start-openhands.sh"

# Erstelle Stop-Skript für OpenHands
echo -e "${YELLOW}Erstelle Stop-Skript für OpenHands...${NC}"
cat > "$HOME/stop-openhands.sh" << EOF
#!/bin/bash

# Stoppe OpenHands mit Docker Compose
cd \$HOME
docker compose -f openhands-docker-compose.yml down

echo "OpenHands wurde gestoppt."
EOF
chmod +x "$HOME/stop-openhands.sh"

# Erstelle Restart-Skript für OpenHands
echo -e "${YELLOW}Erstelle Restart-Skript für OpenHands...${NC}"
cat > "$HOME/restart-openhands.sh" << EOF
#!/bin/bash

# Starte OpenHands neu mit Docker Compose
cd \$HOME
docker compose -f openhands-docker-compose.yml restart

echo "OpenHands wurde neu gestartet und ist verfügbar unter:"
echo "  http://localhost:${OPENHANDS_PORT}"
echo "  MCP-Endpunkt: http://localhost:${OPENHANDS_PORT}/mcp"
EOF
chmod +x "$HOME/restart-openhands.sh"

# Frage, ob OpenHands jetzt gestartet werden soll
echo -e "${YELLOW}Möchten Sie OpenHands jetzt starten? (j/n)${NC}"
read -r START_OPENHANDS
if [[ "$START_OPENHANDS" =~ ^[Jj]$ ]]; then
    echo -e "${YELLOW}Starte OpenHands...${NC}"
    "$HOME/start-openhands.sh"
    
    # Warte auf den Start von OpenHands
    echo -e "${YELLOW}Warte auf den Start von OpenHands...${NC}"
    sleep 10
    
    # Prüfe, ob OpenHands läuft
    if curl -s "http://localhost:${OPENHANDS_PORT}/health" | grep -q "ok"; then
        echo -e "${GREEN}OpenHands wurde erfolgreich gestartet!${NC}"
    else
        echo -e "${YELLOW}OpenHands scheint nicht zu laufen. Bitte prüfen Sie die Logs mit 'docker logs openhands'.${NC}"
    fi
else
    echo -e "${YELLOW}OpenHands wurde nicht gestartet. Sie können es später mit '$HOME/start-openhands.sh' starten.${NC}"
fi

# Zusammenfassung anzeigen
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   MCP-Server OpenHands Integration abgeschlossen!         ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${BLUE}OpenHands-Konfiguration:${NC}"
echo -e "  Konfigurationsverzeichnis: ${OPENHANDS_CONFIG_DIR}"
echo -e "  Zustandsverzeichnis: ${OPENHANDS_STATE_DIR}"
echo -e "  Workspace-Verzeichnis: ${OPENHANDS_WORKSPACE_DIR}"
echo -e "  Port: ${OPENHANDS_PORT}"
echo -e ""
echo -e "${BLUE}Nützliche Befehle:${NC}"
echo -e "  Starten: ${HOME}/start-openhands.sh"
echo -e "  Stoppen: ${HOME}/stop-openhands.sh"
echo -e "  Neustarten: ${HOME}/restart-openhands.sh"
echo -e ""
echo -e "${BLUE}OpenHands-URL:${NC}"
echo -e "  http://localhost:${OPENHANDS_PORT}"
echo -e "  MCP-Endpunkt: http://localhost:${OPENHANDS_PORT}/mcp"
echo -e ""
echo -e "${YELLOW}Hinweis: Stellen Sie sicher, dass die MCP-Server laufen, bevor Sie OpenHands verwenden.${NC}"