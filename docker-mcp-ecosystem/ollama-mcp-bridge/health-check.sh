#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Überprüfe, ob die Ollama-MCP-Bridge läuft
if curl -s http://localhost:8000/health > /dev/null; then
    exit 0
else
    exit 1
fi