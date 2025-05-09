#!/bin/bash

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
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   OpenHands Konfiguration aktualisieren                   ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Prüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 ist nicht installiert. Bitte installieren Sie Python 3 und versuchen Sie es erneut.${NC}"
    exit 1
fi

# Prüfe, ob die erforderlichen Python-Pakete installiert sind
echo -e "${YELLOW}Prüfe Python-Abhängigkeiten...${NC}"
python3 -c "import yaml, toml" 2>/dev/null || {
    echo -e "${YELLOW}Installiere erforderliche Python-Pakete...${NC}"
    pip install pyyaml toml
}

# Generiere die OpenHands-Konfiguration
echo -e "${YELLOW}Generiere OpenHands-Konfiguration...${NC}"
./generate-openhands-config.py --github-token "$GITHUB_TOKEN" --output "$OPENHANDS_CONFIG_DIR/config.toml"

# Prüfe, ob OpenHands läuft
echo -e "${YELLOW}Prüfe, ob OpenHands läuft...${NC}"
if docker ps | grep -q "openhands"; then
    echo -e "${YELLOW}OpenHands läuft. Möchten Sie es neu starten, um die Änderungen zu übernehmen? (j/n)${NC}"
    read -r RESTART_OPENHANDS
    if [[ "$RESTART_OPENHANDS" =~ ^[Jj]$ ]]; then
        echo -e "${YELLOW}Starte OpenHands neu...${NC}"
        "$HOME/restart-openhands.sh"
        
        # Warte auf den Neustart von OpenHands
        echo -e "${YELLOW}Warte auf den Neustart von OpenHands...${NC}"
        sleep 10
        
        # Prüfe, ob OpenHands läuft
        if curl -s "http://localhost:3000/health" | grep -q "ok"; then
            echo -e "${GREEN}OpenHands wurde erfolgreich neu gestartet!${NC}"
        else
            echo -e "${YELLOW}OpenHands scheint nicht zu laufen. Bitte prüfen Sie die Logs mit 'docker logs openhands'.${NC}"
        fi
    else
        echo -e "${YELLOW}OpenHands wurde nicht neu gestartet. Die Änderungen werden erst nach einem Neustart wirksam.${NC}"
    fi
else
    echo -e "${YELLOW}OpenHands läuft nicht. Sie können es mit '$HOME/start-openhands.sh' starten.${NC}"
fi

echo -e "${GREEN}OpenHands-Konfiguration wurde aktualisiert!${NC}"