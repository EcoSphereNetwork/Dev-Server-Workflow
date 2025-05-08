#!/bin/bash

# Stop-Web-UI-Skript
# Stoppt den Dev-Server Web-UI-Server

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$WORKSPACE_DIR/cli/logs"
PID_FILE="$LOGS_DIR/web-ui.pid"

# Prüfe, ob die PID-Datei existiert
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}Keine PID-Datei gefunden. Der Web-UI-Server läuft möglicherweise nicht.${NC}"
    
    # Versuche, den Prozess trotzdem zu finden
    PID=$(pgrep -f "python3 -m src.web_ui.server")
    if [ -z "$PID" ]; then
        echo -e "${RED}Kein laufender Web-UI-Server-Prozess gefunden.${NC}"
        exit 1
    fi
else
    PID=$(cat "$PID_FILE")
fi

# Prüfe, ob der Prozess noch läuft
if ! ps -p $PID > /dev/null; then
    echo -e "${YELLOW}Der Prozess mit PID ${PID} läuft nicht mehr.${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

# Stoppe den Prozess
echo -e "${BLUE}Stoppe Web-UI-Server mit PID ${PID}...${NC}"
kill $PID

# Warte kurz und prüfe, ob der Prozess beendet wurde
sleep 2
if ps -p $PID > /dev/null; then
    echo -e "${YELLOW}Der Prozess reagiert nicht auf SIGTERM. Versuche SIGKILL...${NC}"
    kill -9 $PID
    sleep 1
fi

# Prüfe erneut
if ps -p $PID > /dev/null; then
    echo -e "${RED}Fehler beim Stoppen des Web-UI-Servers.${NC}"
    exit 1
else
    echo -e "${GREEN}Web-UI-Server erfolgreich gestoppt.${NC}"
    rm -f "$PID_FILE"
fi