#!/bin/bash

# Installationsskript für die Dev-Server CLI

set -e

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner anzeigen
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   Dev-Server CLI Installation                             ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Pfade
CLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$CLI_DIR")"
INSTALL_DIR="/usr/local/bin"

# Prüfe, ob das Skript mit Root-Rechten ausgeführt wird
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Dieses Skript benötigt Root-Rechte für die Installation.${NC}"
    echo -e "${YELLOW}Bitte führen Sie es mit sudo aus:${NC}"
    echo -e "${YELLOW}sudo $0${NC}"
    exit 1
fi

# Erstelle einen symbolischen Link
echo -e "${YELLOW}Erstelle symbolischen Link für dev-server...${NC}"
ln -sf "$CLI_DIR/dev-server.sh" "$INSTALL_DIR/dev-server"
chmod +x "$CLI_DIR/dev-server.sh"

echo -e "${GREEN}✅ Dev-Server CLI wurde erfolgreich installiert!${NC}"
echo -e "${BLUE}Sie können die CLI jetzt mit dem Befehl 'dev-server' verwenden.${NC}"
echo -e "${BLUE}Beispiel: dev-server help${NC}"

# Prüfe, ob ShellGPT installiert ist
if ! command -v sgpt &> /dev/null; then
    echo -e "${YELLOW}ShellGPT ist nicht installiert. Möchten Sie es jetzt installieren? (j/n)${NC}"
    read -r install_sgpt
    if [[ "$install_sgpt" =~ ^[Jj]$ ]]; then
        echo -e "${YELLOW}Installiere ShellGPT...${NC}"
        pip install shell-gpt
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ ShellGPT wurde erfolgreich installiert!${NC}"
            echo -e "${BLUE}Sie können es mit dem Befehl 'dev-server ai \"Ihre Frage\"' verwenden.${NC}"
        else
            echo -e "${RED}❌ Fehler bei der Installation von ShellGPT.${NC}"
        fi
    fi
fi

# Prüfe, ob Llamafile heruntergeladen werden soll
echo -e "${YELLOW}Möchten Sie Llamafile herunterladen? (j/n)${NC}"
read -r download_llamafile
if [[ "$download_llamafile" =~ ^[Jj]$ ]]; then
    echo -e "${YELLOW}Lade Llamafile herunter...${NC}"
    mkdir -p "$CLI_DIR/models"
    wget -O "$CLI_DIR/models/Llama-3.2-3B-Instruct.Q6_K.llamafile" "https://huggingface.co/Mozilla/Llama-3.2-3B-Instruct-llamafile/resolve/main/Llama-3.2-3B-Instruct.Q6_K.llamafile?download=true"
    if [ $? -eq 0 ]; then
        chmod +x "$CLI_DIR/models/Llama-3.2-3B-Instruct.Q6_K.llamafile"
        echo -e "${GREEN}✅ Llamafile wurde erfolgreich heruntergeladen!${NC}"
        echo -e "${BLUE}Sie können es mit dem Befehl 'dev-server start llamafile' starten.${NC}"
    else
        echo -e "${RED}❌ Fehler beim Herunterladen von Llamafile.${NC}"
    fi
fi

echo -e "${GREEN}Installation abgeschlossen!${NC}"
echo -e "${BLUE}Verwenden Sie 'dev-server menu' für das interaktive Menü oder 'dev-server help' für Hilfe.${NC}"