#!/bin/bash

# Skript zum Stoppen der Ollama-MCP-Bridge

set -e

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Stoppe Ollama und MCP-Bridge ===${NC}"

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

# Stoppe die Container
echo -e "${YELLOW}Stoppe Ollama und MCP-Bridge...${NC}"
docker-compose down

echo -e "${GREEN}=== Ollama und MCP-Bridge wurden gestoppt! ===${NC}"