#!/bin/bash

# Verbessertes Start-Web-UI-Skript mit Versionsprüfung und Docker-Compose-Alias
# Startet die Web-UI für den Dev-Server

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Aktuelle Operation für Fehlerbehandlung
CURRENT_OPERATION=""

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

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

info "=== Dev-Server Web-UI Starter ==="

# Funktion zum Einrichten eines Alias für docker-compose
setup_docker_compose_alias() {
    # Prüfen, ob docker compose Befehl verfügbar ist
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Prüfen, ob docker-compose Befehl verfügbar ist
        if ! command -v docker-compose &> /dev/null; then
            info "Richte Alias für docker-compose ein..."
            
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
                log "Alias zu $shell_rc hinzugefügt."
                warn "Bitte führen Sie 'source $shell_rc' aus, oder starten Sie ein neues Terminal, um den Alias zu aktivieren."
                
                # Temporär für die aktuelle Sitzung einrichten
                alias docker-compose="docker compose"
                log "Alias temporär für die aktuelle Sitzung eingerichtet."
            else
                log "Alias existiert bereits in $shell_rc."
            fi
        else
            log "docker-compose Befehl ist bereits verfügbar."
        fi
    else
        warn "Docker Compose Plugin ist nicht installiert. Kann keinen Alias einrichten."
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
        warn "Konnte die Version von $package nicht ermitteln."
        return 2
    fi

    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" = "$min_version" ]; then
        log "$package Version $current_version gefunden (Minimum: $min_version)."
        return 0
    else
        warn "$package Version $current_version ist älter als die benötigte Version $min_version."
        return 3
    fi
}

# Funktion zum Starten des Docker-Daemons
start_docker_daemon() {
    info "Überprüfe, ob der Docker-Daemon läuft..."
    
    if ! docker info &> /dev/null; then
        warn "Docker-Daemon läuft nicht. Versuche, ihn zu starten..."
        
        if command -v systemctl &> /dev/null; then
            sudo systemctl start docker
        elif command -v service &> /dev/null; then
            sudo service docker start
        else
            # Direkter Start des Docker-Daemons im Hintergrund
            sudo dockerd > /tmp/docker.log 2>&1 &
            sleep 5
        fi
        
        if ! docker info &> /dev/null; then
            error "Konnte den Docker-Daemon nicht starten. Bitte starten Sie ihn manuell."
            error "Verwenden Sie 'sudo systemctl start docker' oder 'sudo service docker start'."
            return 1
        fi
        
        log "Docker-Daemon wurde gestartet."
    else
        log "Docker-Daemon läuft bereits."
    fi
    
    return 0
}

# Funktion zum Generieren von SSL-Zertifikaten
generate_ssl_certs() {
    local ssl_dir="$1"
    local domain="$2"
    
    info "Generiere SSL-Zertifikate für $domain..."
    
    # Erstelle das SSL-Verzeichnis, falls es nicht existiert
    mkdir -p "$ssl_dir"
    
    # Erstelle selbstsignierte Zertifikate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$ssl_dir/$domain.key" \
        -out "$ssl_dir/$domain.crt" \
        -subj "/C=DE/ST=Berlin/L=Berlin/O=EcoSphereNetwork/OU=Dev/CN=*.$domain" \
        -addext "subjectAltName=DNS:*.$domain,DNS:$domain"
    
    log "SSL-Zertifikate für $domain erfolgreich erstellt."
    
    return 0
}

# Funktion zur Fehlerbehandlung
handle_error() {
    local exit_code=$1
    local line_number=$2
    local command=$3
    
    error "Fehler in Zeile $line_number mit Exit-Code $exit_code beim Ausführen von: $command"
    
    # Versuche, fehlgeschlagene Operationen zu bereinigen
    if [ "$CURRENT_OPERATION" = "docker_compose_up" ]; then
        warn "Docker Compose up fehlgeschlagen. Versuche, Container zu stoppen..."
        if command -v docker &> /dev/null; then
            docker stop $(docker ps -q --filter "name=dev-server") 2>/dev/null || true
        fi
    elif [ "$CURRENT_OPERATION" = "generate_ssl_certs" ]; then
        warn "Generieren von SSL-Zertifikaten fehlgeschlagen."
    fi
    
    exit $exit_code
}

# Richte Fehlerbehandlung ein
trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR

# Hauptfunktion
main() {
    # Prüfe, ob Docker installiert ist
    info "Prüfe Docker-Installation..."
    if ! command -v docker &> /dev/null; then
        error "Docker ist nicht installiert. Bitte installieren Sie Docker."
        exit 1
    fi

    # Prüfe Docker-Version
    check_version "docker" "20.10.0" "docker --version" "([0-9]+\.[0-9]+\.[0-9]+)"
    if [ $? -eq 1 ]; then
        error "Docker ist nicht installiert oder nicht in PATH. Bitte installieren Sie Docker."
        exit 1
    elif [ $? -eq 3 ]; then
        warn "Docker-Version ist älter als empfohlen. Ein Update wird empfohlen."
    fi

    # Prüfe, ob der Docker-Daemon läuft
    start_docker_daemon || exit 1

    # Prüfe, ob Docker Compose installiert ist
    info "Prüfe Docker Compose-Installation..."
    # Prüfe zuerst das Docker Compose Plugin
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Richte den docker-compose Alias ein
        setup_docker_compose_alias
        
        # Verwende das Docker Compose Plugin
        DOCKER_COMPOSE_CMD="docker compose"
        
    elif command -v docker-compose &> /dev/null; then
        log "Eigenständiges Docker Compose ist installiert."
        # Prüfe die Version
        check_version "docker-compose" "1.29.0" "docker-compose --version" "([0-9]+\.[0-9]+\.[0-9]+)"
        if [ $? -eq 3 ]; then
            warn "Docker Compose Version ist älter als empfohlen. Ein Update wird empfohlen."
        fi
        
        # Verwende das eigenständige Docker Compose
        DOCKER_COMPOSE_CMD="docker-compose"
        
    else
        error "Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose."
        exit 1
    fi

    # Prüfe, ob die SSL-Zertifikate existieren
    SSL_DIR="./docker/nginx/ssl"
    DOMAIN="ecospherenet.work"
    if [ ! -d "$SSL_DIR" ]; then
        info "SSL-Verzeichnis nicht gefunden. Erstelle Verzeichnis..."
        mkdir -p "$SSL_DIR"
    fi

    if [ ! -f "$SSL_DIR/$DOMAIN.crt" ] || [ ! -f "$SSL_DIR/$DOMAIN.key" ]; then
        warn "SSL-Zertifikate nicht gefunden. Erstelle selbstsignierte Zertifikate..."
        
        # Prüfe, ob openssl installiert ist
        if ! command -v openssl &> /dev/null; then
            warn "OpenSSL ist nicht installiert. Versuche es zu installieren..."
            
            # Erkenne das Betriebssystem
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                OS=$ID
            else
                OS=$(uname -s)
            fi
            
            case $OS in
                ubuntu|debian|linuxmint)
                    info "Erkannte Distribution: $OS"
                    sudo apt-get update && sudo apt-get install -y openssl
                    ;;
                fedora|centos|rhel)
                    info "Erkannte Distribution: $OS"
                    sudo dnf install -y openssl
                    ;;
                arch|manjaro)
                    info "Erkannte Distribution: $OS"
                    sudo pacman -Sy openssl
                    ;;
                *)
                    error "Nicht unterstützte Distribution. Bitte installieren Sie OpenSSL manuell."
                    exit 1
                    ;;
            esac
        fi
        
        # Setze aktuelle Operation
        CURRENT_OPERATION="generate_ssl_certs"
        
        # Generiere SSL-Zertifikate
        generate_ssl_certs "$SSL_DIR" "$DOMAIN"
    else
        log "SSL-Zertifikate wurden gefunden."
    fi

    # Prüfe, ob die Docker Compose-Datei existiert
    DOCKER_COMPOSE_FILE="docker-compose.web-ui.yml"
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        error "Docker Compose-Datei $DOCKER_COMPOSE_FILE nicht gefunden."
        exit 1
    fi

    # Starte die Web-UI
    info "Starte Dev-Server Web-UI..."
    
    # Setze aktuelle Operation
    CURRENT_OPERATION="docker_compose_up"
    
    # Starte Docker Compose
    $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" up -d

    if [ $? -eq 0 ]; then
        log "Dev-Server Web-UI erfolgreich gestartet."
        
        # Zeige Dienste und Ports an
        info "Verfügbare Dienste:"
        echo -e "${GREEN}Dev-Server UI:${NC} https://dev-server.$DOMAIN"
        echo -e "${GREEN}n8n:${NC} https://n8n.$DOMAIN"
        echo -e "${GREEN}AppFlowy:${NC} https://appflowy.$DOMAIN"
        echo -e "${GREEN}OpenProject:${NC} https://openproject.$DOMAIN"
        echo -e "${GREEN}GitLab:${NC} https://gitlab.$DOMAIN"
        echo -e "${GREEN}Affine:${NC} https://affine.$DOMAIN"
        echo -e "${GREEN}Monitoring (Grafana):${NC} https://monitoring.$DOMAIN"
        echo -e "${GREEN}Prometheus:${NC} https://monitoring.$DOMAIN/prometheus/"
        echo -e "${GREEN}Alertmanager:${NC} https://monitoring.$DOMAIN/alertmanager/"
        echo -e "${GREEN}Docker (Portainer):${NC} https://docker.$DOMAIN"
        echo -e "${GREEN}MCP-Manager:${NC} https://mcp.$DOMAIN"
        echo -e "${GREEN}API-Docs:${NC} https://api.$DOMAIN"
        echo -e "${GREEN}Auth (Keycloak):${NC} https://auth.$DOMAIN"
        
        warn "Hinweis: Stellen Sie sicher, dass die folgenden Einträge in Ihrer /etc/hosts-Datei vorhanden sind:"
        echo -e "${YELLOW}127.0.0.1 dev-server.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 n8n.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 appflowy.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 openproject.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 gitlab.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 affine.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 monitoring.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 docker.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 mcp.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 api.$DOMAIN${NC}"
        echo -e "${YELLOW}127.0.0.1 auth.$DOMAIN${NC}"
    else
        error "Fehler beim Starten der Web-UI."
        exit 1
    fi
}

# Führe die Hauptfunktion aus
main
