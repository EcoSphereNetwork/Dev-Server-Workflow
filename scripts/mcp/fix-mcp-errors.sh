#!/bin/bash

# Verbessertes Skript zur Behebung von Problemen mit dem MCP-Setup
# Verwendet die gemeinsame Bibliothek für konsistente Funktionen und Konfigurationen

# Basisverzeichnis
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

info "=== Behebe Probleme mit dem MCP-Setup ==="

# Aktualisiere die .env-Datei mit dem benutzerdefinierten Port
if [ -f "${BASE_DIR}/.env" ]; then
    info "Aktualisiere .env-Datei mit benutzerdefinierten Ports..."
    
    # Prüfe, ob OPENHANDS_PORT bereits in der .env-Datei existiert
    if ! grep -q "^OPENHANDS_PORT=" "${BASE_DIR}/.env"; then
        log_info "OPENHANDS_PORT=3333" >> "${BASE_DIR}/.env"
    else
        # Aktualisiere den Wert
        sed -i 's/^OPENHANDS_PORT=.*/OPENHANDS_PORT=3333/' "${BASE_DIR}/.env"
    fi
    
    # Lade die aktualisierte .env-Datei
    source "${BASE_DIR}/.env"
fi

# 1. Starte Ollama-Service neu
info "1. Starte Ollama-Service neu..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart ollama || warn "Konnte Ollama-Service nicht neu starten. Möglicherweise läuft er nicht als Systemdienst."
else
    warn "systemctl nicht gefunden. Kann Ollama-Service nicht neu starten."
fi
sleep 5

# 2. Versuche erneut, das Ollama-Modell zu ziehen
info "2. Ziehe Ollama-Modell..."
if command -v ollama &> /dev/null; then
    ollama pull "$OLLAMA_MODEL" || warn "Konnte Ollama-Modell nicht ziehen. Stelle sicher, dass Ollama läuft."
else
    warn "ollama nicht gefunden. Kann Ollama-Modell nicht ziehen."
fi

# 3. Installiere TypeScript global
info "3. Installiere TypeScript global..."
if command -v npm &> /dev/null; then
    sudo npm install -g typescript || npm install -g typescript
else
    warn "npm nicht gefunden. Kann TypeScript nicht installieren."
fi

# 4. Installiere Ollama-MCP-Bridge
info "4. Installiere Ollama-MCP-Bridge..."
install_ollama_bridge

# 5. Erstelle eine package.json im Home-Verzeichnis als Fallback
info "5. Erstelle eine package.json im Home-Verzeichnis als Fallback..."
if [ ! -f "$HOME/package.json" ]; then
    cat > "$HOME/package.json" << EOF
{
  "name": "home-directory",
  "version": "1.0.0",
  "description": "Fallback package.json for npm commands",
  "scripts": {
    "start": "echo 'No start script defined'"
  }
}
EOF
fi

# 6. Aktualisiere die Konfigurationen
info "6. Aktualisiere die Konfigurationen..."
create_openhands_config
create_claude_config

# 7. Aktualisiere die Start-Skripte
info "7. Aktualisiere die Start-Skripte..."
create_start_scripts

info "=== Problembehebung abgeschlossen ==="
log ""
log "OpenHands wurde konfiguriert, um auf Port $OPENHANDS_PORT zu laufen."
log ""
log "Bitte führe folgende Befehle aus, um die Dienste zu starten:"
log "  $HOME/start-openhands.sh - Starte OpenHands"
log "  $HOME/start-ollama-bridge.sh - Starte Ollama-MCP-Bridge"
log "  $HOME/start-all-mcp.sh - Starte alle Dienste"
log ""
log "Wichtige URLs:"
log "  OpenHands: http://localhost:$OPENHANDS_PORT"
log "  OpenHands MCP: http://localhost:$OPENHANDS_PORT/mcp"
log "  Ollama-MCP-Bridge: http://localhost:$OLLAMA_PORT/mcp"
log "  MCP-Inspektor: http://localhost:6274"
log ""
log "Starte Claude Desktop neu, um die Änderungen zu übernehmen."
