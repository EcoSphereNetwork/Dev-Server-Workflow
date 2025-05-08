#!/bin/bash

# Hauptinstallationsskript für das gesamte Dev-Server-Workflow-Projekt

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funktion zum Anzeigen von Nachrichten
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Funktion zum Überprüfen, ob ein Befehl erfolgreich ausgeführt wurde
check_result() {
    if [ $? -ne 0 ]; then
        error "$1"
        exit 1
    fi
}

# Funktion zum Anzeigen des Fortschritts
show_progress() {
    local step=$1
    local total=$2
    local description=$3
    
    echo -e "${GREEN}[${step}/${total}]${NC} ${description}"
}

# Hauptfunktion
main() {
    log "Starte Installation des Dev-Server-Workflow-Projekts..."
    
    # Anzahl der Schritte
    local total_steps=5
    local current_step=1
    
    # Schritt 1: Installiere die MCP-Server
    show_progress $current_step $total_steps "Installiere die MCP-Server..."
    ./install-mcp-servers.sh
    check_result "Installation der MCP-Server fehlgeschlagen."
    current_step=$((current_step + 1))
    
    # Schritt 2: Starte die MCP-Server
    show_progress $current_step $total_steps "Starte die MCP-Server..."
    cd docker-mcp-servers && ./start-mcp-servers.sh
    check_result "Starten der MCP-Server fehlgeschlagen."
    cd ..
    current_step=$((current_step + 1))
    
    # Schritt 3: Installiere n8n
    show_progress $current_step $total_steps "Installiere n8n..."
    
    # Überprüfe, ob n8n bereits installiert ist
    if ! command -v n8n &> /dev/null; then
        log "n8n ist nicht installiert. Installiere n8n..."
        npm install -g n8n
        check_result "Installation von n8n fehlgeschlagen."
    else
        log "n8n ist bereits installiert."
    fi
    
    # Starte n8n im Hintergrund
    log "Starte n8n im Hintergrund..."
    n8n start &
    sleep 10
    
    current_step=$((current_step + 1))
    
    # Schritt 4: Integriere die MCP-Server mit n8n
    show_progress $current_step $total_steps "Integriere die MCP-Server mit n8n..."
    
    # Frage nach dem n8n-API-Key
    read -p "Bitte geben Sie den n8n-API-Key ein: " n8n_api_key
    
    ./scripts/integrate-mcp-with-improved-n8n.py --n8n-api-key "$n8n_api_key"
    check_result "Integration der MCP-Server mit n8n fehlgeschlagen."
    current_step=$((current_step + 1))
    
    # Schritt 5: Integriere die MCP-Server mit OpenHands
    show_progress $current_step $total_steps "Integriere die MCP-Server mit OpenHands..."
    
    # Frage nach dem GitHub-Token
    read -p "Bitte geben Sie das GitHub-Token ein (oder drücken Sie Enter, um zu überspringen): " github_token
    
    # Frage nach dem OpenHands-Konfigurationsverzeichnis
    read -p "Bitte geben Sie das OpenHands-Konfigurationsverzeichnis ein (oder drücken Sie Enter, um zu überspringen): " openhands_config_dir
    
    if [ -n "$openhands_config_dir" ]; then
        if [ -n "$github_token" ]; then
            ./scripts/integrate-mcp-with-openhands.py --openhands-config-dir "$openhands_config_dir" --github-token "$github_token"
        else
            ./scripts/integrate-mcp-with-openhands.py --openhands-config-dir "$openhands_config_dir"
        fi
        check_result "Integration der MCP-Server mit OpenHands fehlgeschlagen."
    else
        log "Integration mit OpenHands übersprungen."
    fi
    
    # Installation abgeschlossen
    log "Installation des Dev-Server-Workflow-Projekts abgeschlossen!"
    log "Sie können die MCP-Server mit dem folgenden Befehl stoppen:"
    log "  cd docker-mcp-servers && ./stop-mcp-servers.sh"
    log "Sie können n8n mit dem folgenden Befehl stoppen:"
    log "  pkill -f n8n"
    
    return 0
}

# Führe die Hauptfunktion aus
main