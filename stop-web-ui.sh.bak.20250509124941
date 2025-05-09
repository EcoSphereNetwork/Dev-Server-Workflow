#!/bin/bash

# Stop-Web-UI-Skript
# Stoppt die Web-UI für den Dev-Server

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Dev-Server Web-UI Stopper ===${NC}"

# Prüfe, ob Docker und Docker Compose installiert sind
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose.${NC}"
    exit 1
fi

# Stoppe die Web-UI
echo -e "${BLUE}Stoppe Dev-Server Web-UI...${NC}"
docker compose -f docker compose.web-ui.yml down

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dev-Server Web-UI erfolgreich gestoppt.${NC}"
else
    echo -e "${RED}Fehler beim Stoppen der Web-UI.${NC}"
    exit 1
fi