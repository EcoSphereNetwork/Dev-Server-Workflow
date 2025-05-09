#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Aktualisiert die OpenHands-Konfiguration basierend auf der aktuellen Docker-Compose-Konfiguration

set -e

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Standardwerte
OPENHANDS_CONFIG_DIR="${OPENHANDS_CONFIG_DIR:-$HOME/.config/openhands}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# Banner anzeigen
log_info "${BLUE}"
log_info "╔═══════════════════════════════════════════════════════════╗"
log_info "║                                                           ║"
log_info "║   OpenHands Konfiguration aktualisieren                   ║"
log_info "║                                                           ║"
log_info "╚═══════════════════════════════════════════════════════════╝"
log_info "${NC}"

# Prüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    log_info "${RED}Python 3 ist nicht installiert. Bitte installieren Sie Python 3 und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Prüfe, ob die erforderlichen Python-Pakete installiert sind
log_info "${YELLOW}Prüfe Python-Abhängigkeiten...${NC}"
python3 -c "import yaml, toml" 2>/dev/null || {
    log_info "${YELLOW}Installiere erforderliche Python-Pakete...${NC}"
    pip install pyyaml toml
}

# Generiere die OpenHands-Konfiguration
log_info "${YELLOW}Generiere OpenHands-Konfiguration...${NC}"
./generate-openhands-config.py --github-token "$GITHUB_TOKEN" --output "$OPENHANDS_CONFIG_DIR/config.toml"

# Prüfe, ob OpenHands läuft
log_info "${YELLOW}Prüfe, ob OpenHands läuft...${NC}"
if docker ps | grep -q "openhands"; then
    log_info "${YELLOW}OpenHands läuft. Möchten Sie es neu starten, um die Änderungen zu übernehmen? (j/n)${NC}"
    read -r RESTART_OPENHANDS
    if [[ "$RESTART_OPENHANDS" =~ ^[Jj]$ ]]; then
        log_info "${YELLOW}Starte OpenHands neu...${NC}"
        "$HOME/restart-openhands.sh"
        
        # Warte auf den Neustart von OpenHands
        log_info "${YELLOW}Warte auf den Neustart von OpenHands...${NC}"
        sleep 10
        
        # Prüfe, ob OpenHands läuft
        if curl -s "http://localhost:3000/health" | grep -q "ok"; then
            log_info "${GREEN}OpenHands wurde erfolgreich neu gestartet!${NC}"
        else
            log_info "${YELLOW}OpenHands scheint nicht zu laufen. Bitte prüfen Sie die Logs mit 'docker logs openhands'.${NC}"
        fi
    else
        log_info "${YELLOW}OpenHands wurde nicht neu gestartet. Die Änderungen werden erst nach einem Neustart wirksam.${NC}"
    fi
else
    log_info "${YELLOW}OpenHands läuft nicht. Sie können es mit '$HOME/start-openhands.sh' starten.${NC}"
fi

log_info "${GREEN}OpenHands-Konfiguration wurde aktualisiert!${NC}"