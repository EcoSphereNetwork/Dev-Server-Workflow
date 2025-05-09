#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


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
log_info "${BLUE}"
log_info "╔═══════════════════════════════════════════════════════════╗"
log_info "║                                                           ║"
log_info "║   MCP-Server OpenHands Integration                        ║"
log_info "║                                                           ║"
log_info "╚═══════════════════════════════════════════════════════════╝"
log_info "${NC}"

# Prüfe, ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    log_info "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Prüfe, ob Docker Compose installiert ist
if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_info "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Prüfe, ob die MCP-Server laufen
log_info "${YELLOW}Prüfe, ob die MCP-Server laufen...${NC}"
if ! docker ps | grep -q "mcp-filesystem"; then
    log_info "${YELLOW}Die MCP-Server scheinen nicht zu laufen. Möchten Sie sie jetzt starten? (j/n)${NC}"
    read -r START_SERVERS
    if [[ "$START_SERVERS" =~ ^[Jj]$ ]]; then
        log_info "${YELLOW}Starte MCP-Server...${NC}"
        ./start-mcp-ecosystem.sh
    else
        log_info "${YELLOW}Bitte starten Sie die MCP-Server manuell mit ./start-mcp-ecosystem.sh${NC}"
        log_info "${YELLOW}Die Integration wird fortgesetzt, aber OpenHands wird möglicherweise nicht korrekt funktionieren.${NC}"
    fi
fi

# Erstelle die OpenHands-Konfigurationsverzeichnisse
log_info "${YELLOW}Erstelle OpenHands-Konfigurationsverzeichnisse...${NC}"
mkdir -p "$OPENHANDS_CONFIG_DIR"
mkdir -p "$OPENHANDS_STATE_DIR"
mkdir -p "$OPENHANDS_WORKSPACE_DIR"

# Kopiere die TOML-Konfigurationsdatei
log_info "${YELLOW}Kopiere OpenHands-Konfigurationsdatei...${NC}"
cp openhands-config.toml "$OPENHANDS_CONFIG_DIR/config.toml"

# Ersetze Umgebungsvariablen in der Konfigurationsdatei
log_info "${YELLOW}Passe Konfiguration an...${NC}"
sed -i "s|\${GITHUB_TOKEN}|$GITHUB_TOKEN|g" "$OPENHANDS_CONFIG_DIR/config.toml"
sed -i "s|volumes = \"/workspace:/workspace:rw\"|volumes = \"$OPENHANDS_WORKSPACE_DIR:/workspace:rw\"|g" "$OPENHANDS_CONFIG_DIR/config.toml"

# Erstelle Docker-Compose-Datei für OpenHands
log_info "${YELLOW}Erstelle Docker-Compose-Datei für OpenHands...${NC}"
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
log_info "${YELLOW}Erstelle Start-Skript für OpenHands...${NC}"
cat > "$HOME/start-openhands.sh" << EOF
#!/bin/bash

# Starte OpenHands mit Docker Compose
cd \$HOME
docker compose -f openhands-docker-compose.yml up -d

log_info "OpenHands wurde gestartet und ist verfügbar unter:"
log_info "  http://localhost:${OPENHANDS_PORT}"
log_info "  MCP-Endpunkt: http://localhost:${OPENHANDS_PORT}/mcp"
EOF
chmod +x "$HOME/start-openhands.sh"

# Erstelle Stop-Skript für OpenHands
log_info "${YELLOW}Erstelle Stop-Skript für OpenHands...${NC}"
cat > "$HOME/stop-openhands.sh" << EOF
#!/bin/bash

# Stoppe OpenHands mit Docker Compose
cd \$HOME
docker compose -f openhands-docker-compose.yml down

log_info "OpenHands wurde gestoppt."
EOF
chmod +x "$HOME/stop-openhands.sh"

# Erstelle Restart-Skript für OpenHands
log_info "${YELLOW}Erstelle Restart-Skript für OpenHands...${NC}"
cat > "$HOME/restart-openhands.sh" << EOF
#!/bin/bash

# Starte OpenHands neu mit Docker Compose
cd \$HOME
docker compose -f openhands-docker-compose.yml restart

log_info "OpenHands wurde neu gestartet und ist verfügbar unter:"
log_info "  http://localhost:${OPENHANDS_PORT}"
log_info "  MCP-Endpunkt: http://localhost:${OPENHANDS_PORT}/mcp"
EOF
chmod +x "$HOME/restart-openhands.sh"

# Frage, ob OpenHands jetzt gestartet werden soll
log_info "${YELLOW}Möchten Sie OpenHands jetzt starten? (j/n)${NC}"
read -r START_OPENHANDS
if [[ "$START_OPENHANDS" =~ ^[Jj]$ ]]; then
    log_info "${YELLOW}Starte OpenHands...${NC}"
    "$HOME/start-openhands.sh"
    
    # Warte auf den Start von OpenHands
    log_info "${YELLOW}Warte auf den Start von OpenHands...${NC}"
    sleep 10
    
    # Prüfe, ob OpenHands läuft
    if curl -s "http://localhost:${OPENHANDS_PORT}/health" | grep -q "ok"; then
        log_info "${GREEN}OpenHands wurde erfolgreich gestartet!${NC}"
    else
        log_info "${YELLOW}OpenHands scheint nicht zu laufen. Bitte prüfen Sie die Logs mit 'docker logs openhands'.${NC}"
    fi
else
    log_info "${YELLOW}OpenHands wurde nicht gestartet. Sie können es später mit '$HOME/start-openhands.sh' starten.${NC}"
fi

# Zusammenfassung anzeigen
log_info "${GREEN}"
log_info "╔═══════════════════════════════════════════════════════════╗"
log_info "║                                                           ║"
log_info "║   MCP-Server OpenHands Integration abgeschlossen!         ║"
log_info "║                                                           ║"
log_info "╚═══════════════════════════════════════════════════════════╝"
log_info "${NC}"
log_info "${BLUE}OpenHands-Konfiguration:${NC}"
log_info "  Konfigurationsverzeichnis: ${OPENHANDS_CONFIG_DIR}"
log_info "  Zustandsverzeichnis: ${OPENHANDS_STATE_DIR}"
log_info "  Workspace-Verzeichnis: ${OPENHANDS_WORKSPACE_DIR}"
log_info "  Port: ${OPENHANDS_PORT}"
echo -e ""
log_info "${BLUE}Nützliche Befehle:${NC}"
log_info "  Starten: ${HOME}/start-openhands.sh"
log_info "  Stoppen: ${HOME}/stop-openhands.sh"
log_info "  Neustarten: ${HOME}/restart-openhands.sh"
echo -e ""
log_info "${BLUE}OpenHands-URL:${NC}"
log_info "  http://localhost:${OPENHANDS_PORT}"
log_info "  MCP-Endpunkt: http://localhost:${OPENHANDS_PORT}/mcp"
echo -e ""
log_info "${YELLOW}Hinweis: Stellen Sie sicher, dass die MCP-Server laufen, bevor Sie OpenHands verwenden.${NC}"