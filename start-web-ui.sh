#!/bin/bash

# Verbessertes Start-Web-UI-Skript mit Versionsprüfung und Docker-Compose-Alias
# Startet die Web-UI für den Dev-Server

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Dev-Server Web-UI Starter ===${NC}"

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

# Funktion zum Überprüfen einer Paketversion
check_version() {
    local package=$1
    local min_version=$2
    local version_cmd=$3
    local version_regex=$4

    if ! command -v "$package" &> /dev/null; then
        return 1
    fi

    local version_output
    version_output=$($version_cmd)
    local current_version
    current_version=$(echo "$version_output" | grep -oE "$version_regex" | head -1)

    if [ -z "$current_version" ]; then
        echo -e "${YELLOW}Konnte die Version von $package nicht ermitteln.${NC}"
        return 2
    }

    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" != "$min_version" ]; then
        echo -e "${GREEN}$package Version $current_version gefunden (Minimum: $min_version).${NC}"
        return 0
    else
        echo -e "${YELLOW}$package Version $current_version ist älter als die benötigte Version $min_version.${NC}"
        return 3
    fi
}

# Prüfe, ob Docker installiert ist
echo -e "${BLUE}Prüfe Docker-Installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
    exit 1
fi

# Prüfe Docker-Version
check_version "docker" "20.10.0" "docker --version" "([0-9]+\.[0-9]+\.[0-9]+)"
if [ $? -eq 1 ]; then
    echo -e "${RED}Docker ist nicht installiert oder nicht in PATH. Bitte installieren Sie Docker.${NC}"
    exit 1
elif [ $? -eq 3 ]; then
    echo -e "${YELLOW}Docker-Version ist älter als empfohlen. Ein Update wird empfohlen.${NC}"
fi

# Prüfe, ob Docker Compose installiert ist
echo -e "${BLUE}Prüfe Docker Compose-Installation...${NC}"
# Prüfe zuerst das Docker Compose Plugin
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo -e "${GREEN}Docker Compose Plugin ist installiert.${NC}"
    
    # Richte den docker-compose Alias ein
    setup_docker_compose_alias
    
    # Verwende das Docker Compose Plugin
    DOCKER_COMPOSE_CMD="docker compose"
    
elif command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}Eigenständiges Docker Compose ist installiert.${NC}"
    # Prüfe die Version
    check_version "docker-compose" "1.29.0" "docker-compose --version" "([0-9]+\.[0-9]+\.[0-9]+)"
    if [ $? -eq 3 ]; then
        echo -e "${YELLOW}Docker Compose Version ist älter als empfohlen. Ein Update wird empfohlen.${NC}"
    fi
    
    # Verwende das eigenständige Docker Compose
    DOCKER_COMPOSE_CMD="docker-compose"
    
else
    echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose.${NC}"
    exit 1
fi

# Prüfe, ob die SSL-Zertifikate existieren
SSL_DIR="./docker/nginx/ssl"
if [ ! -d "$SSL_DIR" ]; then
    echo -e "${YELLOW}SSL-Verzeichnis nicht gefunden. Erstelle Verzeichnis...${NC}"
    mkdir -p "$SSL_DIR"
fi

if [ ! -f "$SSL_DIR/ecospherenet.work.crt" ] || [ ! -f "$SSL_DIR/ecospherenet.work.key" ]; then
    echo -e "${YELLOW}SSL-Zertifikate nicht gefunden. Erstelle selbstsignierte Zertifikate...${NC}"
    
    # Prüfe, ob openssl installiert ist
    if ! command -v openssl &> /dev/null; then
        echo -e "${YELLOW}OpenSSL ist nicht installiert. Versuche es zu installieren...${NC}"
        
        # Erkenne das Betriebssystem
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        else
            OS=$(uname -s)
        fi
        
        case $OS in
            ubuntu|debian|linuxmint)
                echo -e "${BLUE}Erkannte Distribution: $OS${NC}"
                sudo apt-get update && sudo apt-get install -y openssl
                ;;
            fedora|centos|rhel)
                echo -e "${BLUE}Erkannte Distribution: $OS${NC}"
                sudo dnf install -y openssl
                ;;
            arch|manjaro)
                echo -e "${BLUE}Erkannte Distribution: $OS${NC}"
                sudo pacman -Sy openssl
                ;;
            *)
                echo -e "${RED}Nicht unterstützte Distribution. Bitte installieren Sie OpenSSL manuell.${NC}"
                exit 1
                ;;
        esac
    fi
    
    # Erstelle selbstsignierte Zertifikate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/ecospherenet.work.key" \
        -out "$SSL_DIR/ecospherenet.work.crt" \
        -subj "/C=DE/ST=Berlin/L=Berlin/O=EcoSphereNetwork/OU=Dev/CN=*.ecospherenet.work"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Fehler beim Erstellen der SSL-Zertifikate.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}SSL-Zertifikate erfolgreich erstellt.${NC}"
fi

# Prüfe, ob die Docker Compose-Datei existiert
DOCKER_COMPOSE_FILE="docker-compose.web-ui.yml"
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo -e "${RED}Docker Compose-Datei $DOCKER_COMPOSE_FILE nicht gefunden.${NC}"
    exit 1
fi

# Starte die Web-UI
echo -e "${BLUE}Starte Dev-Server Web-UI...${NC}"
$DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dev-Server Web-UI erfolgreich gestartet.${NC}"
    echo -e "${GREEN}Die Web-UI ist verfügbar unter: https://dev-server.ecospherenet.work${NC}"
    echo -e "${YELLOW}Hinweis: Stellen Sie sicher, dass die folgenden Einträge in Ihrer /etc/hosts-Datei vorhanden sind:${NC}"
    echo -e "${YELLOW}127.0.0.1 dev-server.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 n8n.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 appflowy.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 openproject.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 gitlab.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 affine.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 monitoring.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 docker.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 mcp.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 api.ecospherenet.work${NC}"
    echo -e "${YELLOW}127.0.0.1 auth.ecospherenet.work${NC}"
    
    # Zeige Dienste und Ports an
    echo -e "${BLUE}Verfügbare Dienste:${NC}"
    echo -e "${GREEN}Dev-Server UI:${NC} https://dev-server.ecospherenet.work"
    echo -e "${GREEN}n8n:${NC} https://n8n.ecospherenet.work"
    echo -e "${GREEN}AppFlowy:${NC} https://appflowy.ecospherenet.work"
    echo -e "${GREEN}OpenProject:${NC} https://openproject.ecospherenet.work"
    echo -e "${GREEN}GitLab:${NC} https://gitlab.ecospherenet.work"
    echo -e "${GREEN}Affine:${NC} https://affine.ecospherenet.work"
    echo -e "${GREEN}Monitoring (Grafana):${NC} https://monitoring.ecospherenet.work"
    echo -e "${GREEN}Prometheus:${NC} https://monitoring.ecospherenet.work/prometheus/"
    echo -e "${GREEN}Alertmanager:${NC} https://monitoring.ecospherenet.work/alertmanager/"
    echo -e "${GREEN}Docker (Portainer):${NC} https://docker.ecospherenet.work"
    echo -e "${GREEN}MCP-Manager:${NC} https://mcp.ecospherenet.work"
    echo -e "${GREEN}API-Docs:${NC} https://api.ecospherenet.work"
    echo -e "${GREEN}Auth (Keycloak):${NC} https://auth.ecospherenet.work"
else
    echo -e "${RED}Fehler beim Starten der Web-UI.${NC}"
    exit 1
fi
