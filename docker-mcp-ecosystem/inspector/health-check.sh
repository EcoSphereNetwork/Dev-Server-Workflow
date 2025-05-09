#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Überprüfe, ob der MCP Inspector UI-Server läuft
if curl -s http://localhost:6274 > /dev/null; then
    # Überprüfe, ob der MCP Inspector Proxy-Server läuft
    if curl -s http://localhost:6277/health > /dev/null; then
        exit 0
    fi
fi

exit 1