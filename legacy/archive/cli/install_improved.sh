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
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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
CONFIG_DIR="$CLI_DIR/config"
LOGS_DIR="$WORKSPACE_DIR/logs"
MODELS_DIR="$CLI_DIR/models"

# Erstelle benötigte Verzeichnisse
mkdir -p "$CONFIG_DIR" "$LOGS_DIR" "$MODELS_DIR"

# Prüfe, ob das Skript mit Root-Rechten ausgeführt wird
if [ "$EUID" -ne 0 ]; then
    log_info "${YELLOW}Dieses Skript benötigt Root-Rechte für die Installation.${NC}"
    log_info "${YELLOW}Bitte führen Sie es mit sudo aus:${NC}"
    log_info "${YELLOW}sudo $0${NC}"
    exit 1
fi

# Kopiere die verbesserten Skripte
log_info "${YELLOW}Kopiere verbesserte Skripte...${NC}"
cp "$CLI_DIR/dev-server-improved.sh" "$CLI_DIR/dev-server.sh"
cp "$CLI_DIR/config_improved.sh" "$CLI_DIR/config.sh"
cp "$CLI_DIR/ai_assistant_improved.sh" "$CLI_DIR/ai_assistant.sh"

# Setze Ausführungsrechte
chmod +x "$CLI_DIR/dev-server.sh"
chmod +x "$CLI_DIR/ai_assistant.sh"
chmod +x "$CLI_DIR/config.sh"
chmod +x "$CLI_DIR/install_components.sh"

# Erstelle einen symbolischen Link
log_info "${YELLOW}Erstelle symbolischen Link für dev-server...${NC}"
ln -sf "$CLI_DIR/dev-server.sh" "$INSTALL_DIR/dev-server"

log_info "${GREEN}✅ Dev-Server CLI wurde erfolgreich installiert!${NC}"
log_info "${BLUE}Sie können die CLI jetzt mit dem Befehl 'dev-server' verwenden.${NC}"
log_info "${BLUE}Beispiel: dev-server help${NC}"

# Prüfe, ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    log_info "${YELLOW}Docker ist nicht installiert. Möchten Sie es jetzt installieren? (j/n)${NC}"
    read -r install_docker
    if [[ "$install_docker" =~ ^[Jj]$ ]]; then
        log_info "${YELLOW}Installiere Docker...${NC}"
        "$CLI_DIR/install_components.sh" docker
        if [ $? -eq 0 ]; then
            log_info "${GREEN}✅ Docker wurde erfolgreich installiert!${NC}"
        else
            log_info "${RED}❌ Fehler bei der Installation von Docker.${NC}"
        fi
    fi
fi

# Prüfe, ob Docker Compose installiert ist
if ! command -v docker-compose &> /dev/null; then
    log_info "${YELLOW}Docker Compose ist nicht installiert. Möchten Sie es jetzt installieren? (j/n)${NC}"
    read -r install_docker_compose
    if [[ "$install_docker_compose" =~ ^[Jj]$ ]]; then
        log_info "${YELLOW}Installiere Docker Compose...${NC}"
        "$CLI_DIR/install_components.sh" docker-compose
        if [ $? -eq 0 ]; then
            log_info "${GREEN}✅ Docker Compose wurde erfolgreich installiert!${NC}"
        else
            log_info "${RED}❌ Fehler bei der Installation von Docker Compose.${NC}"
        fi
    fi
fi

# Prüfe, ob Llamafile heruntergeladen werden soll
log_info "${YELLOW}Möchten Sie Llamafile herunterladen? (j/n)${NC}"
read -r download_llamafile
if [[ "$download_llamafile" =~ ^[Jj]$ ]]; then
    log_info "${YELLOW}Lade Llamafile herunter...${NC}"
    "$CLI_DIR/install_components.sh" llamafile
    if [ $? -eq 0 ]; then
        log_info "${GREEN}✅ Llamafile wurde erfolgreich heruntergeladen!${NC}"
        log_info "${BLUE}Sie können es mit dem Befehl 'dev-server start llamafile' starten.${NC}"
    else
        log_info "${RED}❌ Fehler beim Herunterladen von Llamafile.${NC}"
    fi
fi

# Frage nach der Installation von Komponenten
log_info "${YELLOW}Möchten Sie weitere Komponenten installieren? (j/n)${NC}"
read -r install_components
if [[ "$install_components" =~ ^[Jj]$ ]]; then
    log_info "${YELLOW}Welche Komponenten möchten Sie installieren?${NC}"
    log_info "1) Alle Komponenten"
    log_info "2) n8n"
    log_info "3) MCP-Server"
    log_info "4) OpenHands"
    log_info "5) AppFlowy"
    log_info "6) Ollama"
    log_info "7) Web-UI"
    log_info "0) Keine"
    
    read -r component_choice
    
    case "$component_choice" in
        1)
            log_info "${YELLOW}Installiere alle Komponenten...${NC}"
            "$CLI_DIR/install_components.sh" all
            ;;
        2)
            log_info "${YELLOW}Installiere n8n...${NC}"
            "$CLI_DIR/install_components.sh" n8n
            ;;
        3)
            log_info "${YELLOW}Installiere MCP-Server...${NC}"
            "$CLI_DIR/install_components.sh" mcp
            ;;
        4)
            log_info "${YELLOW}Installiere OpenHands...${NC}"
            "$CLI_DIR/install_components.sh" openhands
            ;;
        5)
            log_info "${YELLOW}Installiere AppFlowy...${NC}"
            "$CLI_DIR/install_components.sh" appflowy
            ;;
        6)
            log_info "${YELLOW}Installiere Ollama...${NC}"
            "$CLI_DIR/install_components.sh" ollama
            ;;
        7)
            log_info "${YELLOW}Installiere Web-UI...${NC}"
            "$CLI_DIR/install_components.sh" web-ui
            ;;
        0)
            log_info "${BLUE}Keine Komponenten ausgewählt.${NC}"
            ;;
        *)
            log_info "${RED}Ungültige Auswahl.${NC}"
            ;;
    esac
fi

# Frage nach API-Schlüsseln
log_info "${YELLOW}Möchten Sie API-Schlüssel konfigurieren? (j/n)${NC}"
read -r configure_api_keys
if [[ "$configure_api_keys" =~ ^[Jj]$ ]]; then
    # Anthropic API-Schlüssel
    log_info "${YELLOW}Bitte geben Sie Ihren Anthropic API-Schlüssel ein (leer lassen, um zu überspringen):${NC}"
    read -r anthropic_api_key
    if [ -n "$anthropic_api_key" ]; then
        dev-server config llm-api-key "$anthropic_api_key"
    fi
    
    # GitHub-Token
    log_info "${YELLOW}Bitte geben Sie Ihr GitHub-Token ein (leer lassen, um zu überspringen):${NC}"
    read -r github_token
    if [ -n "$github_token" ]; then
        dev-server config github-token "$github_token"
    fi
    
    # n8n API-Schlüssel
    log_info "${YELLOW}Bitte geben Sie Ihren n8n API-Schlüssel ein (leer lassen, um zu überspringen):${NC}"
    read -r n8n_api_key
    if [ -n "$n8n_api_key" ]; then
        dev-server config n8n-api-key "$n8n_api_key"
    fi
fi

log_info "${GREEN}Installation abgeschlossen!${NC}"
log_info "${BLUE}Verwenden Sie 'dev-server menu' für das interaktive Menü oder 'dev-server help' für Hilfe.${NC}"