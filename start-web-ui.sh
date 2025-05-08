#!/bin/bash

# Start-Web-UI-Skript
# Startet die Web-UI für den Dev-Server

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Dev-Server Web-UI Starter ===${NC}"

# Prüfe, ob Docker und Docker Compose installiert sind
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose.${NC}"
    exit 1
fi

# Prüfe, ob die SSL-Zertifikate existieren
SSL_DIR="./docker/nginx/ssl"
if [ ! -d "$SSL_DIR" ]; then
    echo -e "${YELLOW}SSL-Verzeichnis nicht gefunden. Erstelle Verzeichnis...${NC}"
    mkdir -p "$SSL_DIR"
fi

if [ ! -f "$SSL_DIR/ecospherenet.work.crt" ] || [ ! -f "$SSL_DIR/ecospherenet.work.key" ]; then
    echo -e "${YELLOW}SSL-Zertifikate nicht gefunden. Erstelle selbstsignierte Zertifikate...${NC}"
    
    # Erstelle selbstsignierte Zertifikate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/ecospherenet.work.key" \
        -out "$SSL_DIR/ecospherenet.work.crt" \
        -subj "/C=DE/ST=Berlin/L=Berlin/O=EcoSphereNetwork/OU=Dev/CN=*.ecospherenet.work"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Fehler beim Erstellen der SSL-Zertifikate.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}SSL-Zertifikate erfolgreich erstellt.${NC}"
fi

# Starte die Web-UI
echo -e "${BLUE}Starte Dev-Server Web-UI...${NC}"
docker compose -f docker compose.web-ui.yml up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dev-Server Web-UI erfolgreich gestartet.${NC}"
    echo -e "${GREEN}Die Web-UI ist verfügbar unter: https://dev-server.ecospherenet.work${NC}"
    echo -e "${YELLOW}Hinweis: Stellen Sie sicher, dass die folgenden Einträge in Ihrer /etc/hosts-Datei vorhanden sind:${NC}"
    echo -e "${YELLOW}127.0.0.1 dev-server.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 n8n.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 appflowy.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 openproject.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 gitlab.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 affine.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 monitoring.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 docker.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 mcp.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 api.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 auth.ecospherenet.work${NC}"
    
    # Zeige Dienste und Ports an
    echo -e "${BLUE}Verfügbare Dienste:${NC}"
    echo -e "${GREEN}Dev-Server UI:${NC} https://dev-server.ecospherenet.work"
    echo -e "${GREEN}n8n:${NC} https://n8n.ecospherenet.work"
    echo -e "${GREEN}AppFlowy:${NC} https://appflowy.ecospherenet.work"
    echo -e "${GREEN}OpenProject:${NC} https://openproject.ecospherenet.work"
    echo -e "${GREEN}GitLab:${NC} https://gitlab.ecospherenet.work"
    echo -e "${GREEN}Affine:${NC} https://affine.ecospherenet.work"
    echo -e "${GREEN}Monitoring (Grafana):${NC} https://monitoring.ecospherenet.work"
    echo -e "${GREEN}Prometheus:${NC} https://monitoring.ecospherenet.work/prometheus/"
    echo -e "${GREEN}Alertmanager:${NC} https://monitoring.ecospherenet.work/alertmanager/"
    echo -e "${GREEN}Docker (Portainer):${NC} https://docker.ecospherenet.work"
    echo -e "${GREEN}MCP-Manager:${NC} https://mcp.ecospherenet.work"
    echo -e "${GREEN}API-Docs:${NC} https://api.ecospherenet.work"
    echo -e "${GREEN}Auth (Keycloak):${NC} https://auth.ecospherenet.work"
else
    echo -e "${RED}Fehler beim Starten der Web-UI.${NC}"
    exit 1
fi