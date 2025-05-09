#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Installationsskript für die Dev-Server CLI

set -e

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner anzeigen
log_info "${BLUE}"
log_info "╔═══════════════════════════════════════════════════════════╗"
log_info "║                                                           ║"
log_info "║   Dev-Server CLI Installation                             ║"
log_info "║                                                           ║"
log_info "╚═══════════════════════════════════════════════════════════╝"
log_info "${NC}"

# Pfade
CLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$CLI_DIR")"
INSTALL_DIR="/usr/local/bin"

# Prüfe, ob das Skript mit Root-Rechten ausgeführt wird
if [ "$EUID" -ne 0 ]; then
    log_info "${YELLOW}Dieses Skript benötigt Root-Rechte für die Installation.${NC}"
    log_info "${YELLOW}Bitte führen Sie es mit sudo aus:${NC}"
    log_info "${YELLOW}sudo $0${NC}"
    exit 1
fi

# Erstelle einen symbolischen Link
log_info "${YELLOW}Erstelle symbolischen Link für dev-server...${NC}"
ln -sf "$CLI_DIR/dev-server.sh" "$INSTALL_DIR/dev-server"
chmod +x "$CLI_DIR/dev-server.sh"

log_info "${GREEN}✅ Dev-Server CLI wurde erfolgreich installiert!${NC}"
log_info "${BLUE}Sie können die CLI jetzt mit dem Befehl 'dev-server' verwenden.${NC}"
log_info "${BLUE}Beispiel: dev-server help${NC}"

# Prüfe, ob ShellGPT installiert ist
if ! command -v sgpt &> /dev/null; then
    log_info "${YELLOW}ShellGPT ist nicht installiert. Möchten Sie es jetzt installieren? (j/n)${NC}"
    read -r install_sgpt
    if [[ "$install_sgpt" =~ ^[Jj]$ ]]; then
        log_info "${YELLOW}Installiere ShellGPT...${NC}"
        pip install shell-gpt
        if [ $? -eq 0 ]; then
            log_info "${GREEN}✅ ShellGPT wurde erfolgreich installiert!${NC}"
            log_info "${BLUE}Sie können es mit dem Befehl 'dev-server ai \"Ihre Frage\"' verwenden.${NC}"
        else
            log_info "${RED}❌ Fehler bei der Installation von ShellGPT.${NC}"
        fi
    fi
fi

# Prüfe, ob Llamafile heruntergeladen werden soll
log_info "${YELLOW}Möchten Sie Llamafile herunterladen? (j/n)${NC}"
read -r download_llamafile
if [[ "$download_llamafile" =~ ^[Jj]$ ]]; then
    log_info "${YELLOW}Lade Llamafile herunter...${NC}"
    mkdir -p "$CLI_DIR/models"
    wget -O "$CLI_DIR/models/Llama-3.2-3B-Instruct.Q6_K.llamafile" "https://huggingface.co/Mozilla/Llama-3.2-3B-Instruct-llamafile/resolve/main/Llama-3.2-3B-Instruct.Q6_K.llamafile?download=true"
    if [ $? -eq 0 ]; then
        chmod +x "$CLI_DIR/models/Llama-3.2-3B-Instruct.Q6_K.llamafile"
        log_info "${GREEN}✅ Llamafile wurde erfolgreich heruntergeladen!${NC}"
        log_info "${BLUE}Sie können es mit dem Befehl 'dev-server start llamafile' starten.${NC}"
    else
        log_info "${RED}❌ Fehler beim Herunterladen von Llamafile.${NC}"
    fi
fi

log_info "${GREEN}Installation abgeschlossen!${NC}"
log_info "${BLUE}Verwenden Sie 'dev-server menu' für das interaktive Menü oder 'dev-server help' für Hilfe.${NC}"