#!/bin/bash

# Start-Web-UI-Skript
# Startet den Dev-Server Web-UI-Server

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
WEB_UI_DIR="$WORKSPACE_DIR/src/web_ui"
LOGS_DIR="$WORKSPACE_DIR/cli/logs"

# Erstelle Logs-Verzeichnis, falls es nicht existiert
mkdir -p "$LOGS_DIR"

# Standardwerte
HOST="0.0.0.0"
PORT="8080"

# Hilfe anzeigen
show_help() {
    echo -e "${BLUE}Dev-Server Web-UI Starter${NC}"
    echo
    echo -e "Verwendung: ${YELLOW}start-web-ui.sh${NC} ${GREEN}[Optionen]${NC}"
    echo
    echo -e "${GREEN}Optionen:${NC}"
    echo -e "  ${YELLOW}-h, --help${NC}           Zeigt diese Hilfe an"
    echo -e "  ${YELLOW}-p, --port PORT${NC}      Port für den Web-UI-Server (Standard: 8080)"
    echo -e "  ${YELLOW}--host HOST${NC}          Host für den Web-UI-Server (Standard: 0.0.0.0)"
    echo
}

# Parameter verarbeiten
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            PORT="$2"
            shift
            shift
            ;;
        --host)
            HOST="$2"
            shift
            shift
            ;;
        *)
            echo -e "${RED}Unbekannte Option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Prüfe, ob Python und die erforderlichen Pakete installiert sind
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 ist nicht installiert. Bitte installieren Sie Python 3.${NC}"
    exit 1
fi

# Prüfe, ob die erforderlichen Python-Pakete installiert sind
echo -e "${BLUE}Prüfe Abhängigkeiten...${NC}"
python3 -c "import aiohttp, aiohttp_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installiere erforderliche Python-Pakete...${NC}"
    pip install -r "$WORKSPACE_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Fehler beim Installieren der Python-Pakete.${NC}"
        exit 1
    fi
fi

# Starte den Web-UI-Server
echo -e "${BLUE}Starte Dev-Server Web-UI auf ${HOST}:${PORT}...${NC}"
cd "$WORKSPACE_DIR"
nohup python3 -m src.web_ui.server --host "$HOST" --port "$PORT" > "$LOGS_DIR/web-ui.log" 2>&1 &
PID=$!

# Prüfe, ob der Server erfolgreich gestartet wurde
sleep 2
if ps -p $PID > /dev/null; then
    echo -e "${GREEN}Dev-Server Web-UI erfolgreich gestartet mit PID ${PID}.${NC}"
    echo -e "${GREEN}Web-UI ist verfügbar unter: http://${HOST}:${PORT}${NC}"
    echo -e "${BLUE}Logs werden geschrieben nach: ${LOGS_DIR}/web-ui.log${NC}"
    
    # Speichere PID für späteres Stoppen
    echo $PID > "$LOGS_DIR/web-ui.pid"
else
    echo -e "${RED}Fehler beim Starten des Web-UI-Servers.${NC}"
    echo -e "${YELLOW}Prüfen Sie die Logs für weitere Informationen: ${LOGS_DIR}/web-ui.log${NC}"
    exit 1
fi