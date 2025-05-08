#!/bin/bash

# Skript zum Starten der Ollama-MCP-Bridge

set -e

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starte Ollama und MCP-Bridge ===${NC}"

# Prüfe, ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Prüfe, ob Docker Compose installiert ist
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Erstelle .env-Datei, wenn sie nicht existiert
if [ ! -f .env ]; then
    echo -e "${YELLOW}Erstelle .env-Datei...${NC}"
    cat > .env << EOF
# Ollama-Konfiguration
OLLAMA_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_BASE_URL=http://ollama:11434

# API-Keys
GITHUB_TOKEN=your-github-token
BRAVE_API_KEY=your-brave-api-key
EOF
    echo -e "${YELLOW}Bitte bearbeiten Sie die .env-Datei und setzen Sie die korrekten API-Keys.${NC}"
    echo -e "${YELLOW}Drücken Sie eine Taste, um fortzufahren...${NC}"
    read -n 1
fi

# Starte die Container
echo -e "${YELLOW}Starte Ollama und MCP-Bridge...${NC}"
docker-compose up -d

# Warte auf den Start der Container
echo -e "${YELLOW}Warte auf den Start der Container...${NC}"
sleep 10

# Prüfe, ob die Container laufen
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}Ollama und MCP-Bridge wurden erfolgreich gestartet!${NC}"
else
    echo -e "${RED}Es gab ein Problem beim Starten der Container. Bitte überprüfen Sie die Logs mit 'docker-compose logs'.${NC}"
    exit 1
fi

# Lade das Modell, wenn es noch nicht vorhanden ist
MODEL=$(grep OLLAMA_MODEL .env | cut -d= -f2)
echo -e "${YELLOW}Prüfe, ob das Modell ${MODEL} bereits heruntergeladen wurde...${NC}"
if ! docker-compose exec ollama ollama list | grep -q "$MODEL"; then
    echo -e "${YELLOW}Lade das Modell ${MODEL} herunter...${NC}"
    docker-compose exec ollama ollama pull "$MODEL"
    echo -e "${GREEN}Modell ${MODEL} wurde erfolgreich heruntergeladen!${NC}"
else
    echo -e "${GREEN}Modell ${MODEL} ist bereits vorhanden.${NC}"
fi

echo -e "${GREEN}=== Ollama und MCP-Bridge sind bereit! ===${NC}"
echo -e "${BLUE}Ollama ist verfügbar unter: http://localhost:11434${NC}"
echo -e "${BLUE}MCP-Bridge ist verfügbar unter: http://localhost:8000${NC}"
echo -e "${BLUE}MCP-Endpunkt: http://localhost:8000/mcp${NC}"
echo -e "${BLUE}Chat-Endpunkt: http://localhost:8000/chat${NC}"