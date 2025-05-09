#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Skript zum Testen der Ollama-MCP-Bridge

set -e

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info "${BLUE}=== Teste Ollama und MCP-Bridge ===${NC}"

# Prüfe, ob curl installiert ist
if ! command -v curl &> /dev/null; then
    log_info "${RED}curl ist nicht installiert. Bitte installieren Sie curl und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Prüfe, ob jq installiert ist
if ! command -v jq &> /dev/null; then
    log_info "${YELLOW}jq ist nicht installiert. Die Ausgabe wird nicht formatiert.${NC}"
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Teste Ollama-Gesundheitscheck
log_info "${YELLOW}Teste Ollama-Gesundheitscheck...${NC}"
if curl -s http://localhost:11434/api/health > /dev/null; then
    log_info "${GREEN}✅ Ollama ist gesund${NC}"
else
    log_info "${RED}❌ Ollama ist nicht erreichbar${NC}"
    exit 1
fi

# Teste MCP-Bridge-Gesundheitscheck
log_info "${YELLOW}Teste MCP-Bridge-Gesundheitscheck...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    log_info "${GREEN}✅ MCP-Bridge ist gesund${NC}"
else
    log_info "${RED}❌ MCP-Bridge ist nicht erreichbar${NC}"
    exit 1
fi

# Teste Ollama-Modelle
log_info "${YELLOW}Teste Ollama-Modelle...${NC}"
RESPONSE=$(curl -s http://localhost:11434/api/tags)
if [ "$JQ_AVAILABLE" = true ]; then
    log_info "$RESPONSE" | jq
else
    log_info "$RESPONSE"
fi

# Teste MCP-Endpunkt
log_info "${YELLOW}Teste MCP-Endpunkt...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/mcp \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"mcp.listTools","params":{}}')
if [ "$JQ_AVAILABLE" = true ]; then
    log_info "$RESPONSE" | jq
else
    log_info "$RESPONSE"
fi

# Teste Chat-Endpunkt
log_info "${YELLOW}Teste Chat-Endpunkt...${NC}"
log_info "${YELLOW}Sende eine einfache Anfrage an das LLM...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"prompt":"Sage Hallo Welt"}')
if [ "$JQ_AVAILABLE" = true ]; then
    log_info "$RESPONSE" | jq
else
    log_info "$RESPONSE"
fi

log_info "${GREEN}=== Tests abgeschlossen! ===${NC}"