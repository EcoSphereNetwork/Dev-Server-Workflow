#!/bin/bash
# Skript zum Starten der MCP-Server mit Versionsprüfung

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Fehlerbehandlung einbinden
if [[ -f "${BASE_DIR}/cli/error_handler.sh" ]]; then
    source "${BASE_DIR}/cli/error_handler.sh"
fi

# Konfigurationsmanager einbinden
if [[ -f "${BASE_DIR}/cli/config_manager.sh" ]]; then
    source "${BASE_DIR}/cli/config_manager.sh"
    # Alle Konfigurationen laden
    if [[ "$(type -t load_all_configs)" == "function" ]]; then
        load_all_configs
    fi
fi

# Konfiguration
N8N_URL=${N8N_URL:-"http://localhost:5678"}
N8N_API_KEY=${N8N_API_KEY:-""}
OPENHANDS_MAX_WORKERS=${OPENHANDS_MAX_WORKERS:-5}
GENERATOR_SERVERS_DIR=${GENERATOR_SERVERS_DIR:-"generated_servers"}
MCP_SERVERS_DIR="/workspace/Dev-Server-Workflow/docker-mcp-servers"
LOG_DIR="/tmp/mcp-logs"

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Aktuelle Operation für Fehlerbehandlung
CURRENT_OPERATION=""
CURRENT_CONTAINER=""

# Funktion zum Anzeigen von Hilfe
show_help() {
    echo -e "${BLUE}MCP-Server Starter${NC}"
    echo "Dieses Skript startet die MCP-Server für das Dev-Server-Workflow-Projekt."
    echo ""
    echo "Verwendung:"
    echo "  $0 [Optionen]"
    echo ""
    echo "Optionen:"
    echo "  -h, --help                Zeigt diese Hilfe an"
    echo "  -n, --n8n-url URL         URL der n8n-Instanz (Standard: $N8N_URL)"
    echo "  -k, --api-key KEY         API-Schlüssel für n8n"
    echo "  -w, --max-workers N       Maximale Anzahl von Worker-Threads für OpenHands (Standard: $OPENHANDS_MAX_WORKERS)"
    echo "  -d, --servers-dir DIR     Verzeichnis für generierte Server (Standard: $GENERATOR_SERVERS_DIR)"
    echo "  -v, --verbose             Ausführliche Ausgabe"
    echo "  -a, --all                 Alle MCP-Server starten"
    echo "  --n8n                     n8n MCP-Server starten"
    echo "  --openhands               OpenHands MCP-Server starten"
    echo "  --generator               MCP-Server-Generator starten"
    echo ""
    echo "Umgebungsvariablen:"
    echo "  N8N_URL                   URL der n8n-Instanz"
    echo "  N8N_API_KEY               API-Schlüssel für n8n"
    echo "  OPENHANDS_MAX_WORKERS     Maximale Anzahl von Worker-Threads für OpenHands"
    echo "  GENERATOR_SERVERS_DIR     Verzeichnis für generierte Server"
    echo ""
    echo "Beispiel:"
    echo "  $0 --all -k my-api-key"
    echo "  $0 --n8n --openhands -k my-api-key -w 10"
}

# Funktion zum Einrichten eines Alias für docker-compose
setup_docker_compose_alias() {
    # Prüfen, ob docker compose Befehl verfügbar ist
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        echo -e "${GREEN}Docker Compose Plugin ist installiert.${NC}"
        
        # Prüfen, ob docker-compose Befehl verfügbar ist
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${BLUE}Richte Alias für docker-compose ein...${NC}"
            
            # Prüfen, welche Shell verwendet wird
            local shell_rc
            if [ -n "$ZSH_VERSION" ]; then
                shell_rc="$HOME/.zshrc"
            elif [ -n "$BASH_VERSION" ]; then
                shell_rc="$HOME/.bashrc"
            else
                # Standardmäßig .bashrc verwenden
                shell_rc="$HOME/.bashrc"
            fi
            
            # Prüfen, ob der Alias bereits existiert
            if ! grep -q "alias docker-compose='docker compose'" "$shell_rc"; then
                echo 'alias docker-compose="docker compose"' >> "$shell_rc"
                echo -e "${GREEN}Alias zu $shell_rc hinzugefügt.${NC}"
                echo -e "${YELLOW}Bitte führen Sie 'source $shell_rc' aus, oder starten Sie ein neues Terminal, um den Alias zu aktivieren.${NC}"
                
                # Temporär für die aktuelle Sitzung einrichten
                alias docker-compose="docker compose"
                echo -e "${GREEN}Alias temporär für die aktuelle Sitzung eingerichtet.${NC}"
            else
                echo -e "${GREEN}Alias existiert bereits in $shell_rc.${NC}"
            fi
        else
            echo -e "${GREEN}docker-compose Befehl ist bereits verfügbar.${NC}"
        fi
    else
        echo -e "${YELLOW}Docker Compose Plugin ist nicht installiert. Kann keinen Alias einrichten.${NC}"
    fi
}

# Funktion zum Überprüfen der Docker-Installation
check_docker() {
    echo -e "${BLUE}Überprüfe Docker-Installation...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut.${NC}"
        return 1
    fi
    
    # Überprüfe die Docker-Version
    local docker_version
    docker_version=$(docker --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
    
    if [ -n "$docker_version" ]; then
        echo -e "${GREEN}Docker Version: $docker_version${NC}"
        
        # Vergleiche mit der Mindestversion
        if [ "$(printf '%s\n' "20.10.0" "$docker_version" | sort -V | head -n1)" != "20.10.0" ]; then
            echo -e "${GREEN}Docker ist ausreichend aktuell.${NC}"
        else
            echo -e "${YELLOW}Docker Version ist älter als 20.10.0. Ein Update wird empfohlen.${NC}"
        fi
    else
        echo -e "${YELLOW}Konnte die Docker-Version nicht ermitteln.${NC}"
    fi
    
    return 0
}

# Funktion zum Überprüfen der Docker Compose-Installation
check_docker_compose() {
    echo -e "${BLUE}Überprüfe Docker Compose-Installation...${NC}"
    
    # Prüfe zunächst das neue Docker-Compose-Plugin
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        echo -e "${GREEN}Docker Compose Plugin ist installiert.${NC}"
        
        # Versuche, die Version zu ermitteln
        local docker_compose_version
        docker_compose_version=$(docker compose version --short 2>/dev/null || docker compose version 2>/dev/null | grep -oE "v?[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        
        if [ -n "$docker_compose_version" ]; then
            # Entferne ein mögliches 'v' am Anfang
            docker_compose_version=${docker_compose_version#v}
            echo -e "${GREEN}Docker Compose Plugin Version: $docker_compose_version${NC}"
            
            # Richte den Alias ein
            setup_docker_compose_alias
            
            return 0
        fi
    fi
    
    # Prüfe das eigenständige Docker-Compose-Binary
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}Eigenständiges Docker Compose ist installiert.${NC}"
        
        local docker_compose_version
        docker_compose_version=$(docker-compose --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        
        if [ -n "$docker_compose_version" ]; then
            echo -e "${GREEN}Docker Compose Version: $docker_compose_version${NC}"
            
            # Vergleiche mit der Mindestversion
            if [ "$(printf '%s\n' "1.29.0" "$docker_compose_version" | sort -V | head -n1)" != "1.29.0" ]; then
                echo -e "${GREEN}Docker Compose ist ausreichend aktuell.${NC}"
                return 0
            else
                echo -e "${YELLOW}Docker Compose Version ist älter als 1.29.0. Ein Update wird empfohlen.${NC}"
                # Aber wir können es trotzdem nutzen
                return 0
            fi
        fi
    fi
    
    # Wenn wir hier ankommen, fehlt Docker Compose
    echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut.${NC}"
    echo -e "${YELLOW}Sie können Docker Compose mit folgendem Befehl installieren:${NC}"
    echo -e "${YELLOW}sudo apt-get install docker-compose-plugin${NC}"
    return 1
