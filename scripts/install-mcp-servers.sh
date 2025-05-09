#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Verbessertes Installationsskript für MCP-Server mit Versionsprüfung

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion zum Anzeigen von Nachrichten
log() {
    log_info "${GREEN}[INFO]${NC} $1"
}

warn() {
    log_info "${YELLOW}[WARN]${NC} $1"
}

error() {
    log_info "${RED}[ERROR]${NC} $1"
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
    current_version=$(log_info "$version_output" | grep -oE "$version_regex" | head -1)

    if [ -z "$current_version" ]; then
        warn "Konnte die Version von $package nicht ermitteln."
        return 2
    fi

    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" != "$min_version" ]; then
        log "$package Version $current_version gefunden (Minimum: $min_version)."
        return 0
    else
        warn "$package Version $current_version ist älter als die benötigte Version $min_version."
        return 3
    fi
}

# Funktion zum Einrichten eines Alias für docker-compose
setup_docker_compose_alias() {
    # Prüfen, ob docker compose Befehl verfügbar ist
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Prüfen, ob docker-compose Befehl verfügbar ist
        if ! command -v docker-compose &> /dev/null; then
            log "Richte Alias für docker-compose ein..."
            
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
                log "Bitte führen Sie 'source $shell_rc' aus, oder starten Sie ein neues Terminal, um den Alias zu aktivieren."
                
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

# Funktion zum Überprüfen, ob Docker installiert ist
check_docker() {
    log "Überprüfe Docker-Installation..."
    
    if ! command -v docker &> /dev/null; then
        warn "Docker ist nicht installiert. Versuche, es zu installieren..."
        
        # Erkennen des Betriebssystems und der Paketmanager
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        else
            OS=$(uname -s)
        fi
        
        case $OS in
            ubuntu|debian|linuxmint)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Docker mit apt..."
                sudo apt-get update
                sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
                curl -fsSL https://download.docker.com/linux/"$OS"/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                log_info "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                sudo apt-get update
                sudo apt-get install -y docker-ce docker-ce-cli containerd.io
                ;;
            fedora|centos|rhel)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Docker mit dnf/yum..."
                sudo dnf -y install dnf-plugins-core
                sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
                sudo dnf -y install docker-ce docker-ce-cli containerd.io
                ;;
            arch|manjaro)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Docker mit pacman..."
                sudo pacman -Sy docker
                ;;
            *)
                error "Nicht unterstütztes Betriebssystem: $OS"
                error "Bitte installieren Sie Docker manuell: https://docs.docker.com/engine/install/"
                return 1
                ;;
        esac
        
        # Starte Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Füge den aktuellen Benutzer zur Docker-Gruppe hinzu
        sudo usermod -aG docker "$USER"
        
        log "Docker wurde installiert. Bitte starten Sie die Shell neu, um die Docker-Gruppe zu aktivieren."
        log "Führen Sie dann dieses Skript erneut aus."
        exit 0
    fi
    
    # Überprüfe die Docker-Version
    check_version "docker" "20.10.0" "docker --version" "([0-9]+\.[0-9]+\.[0-9]+)"
    if [ $? -eq 0 ]; then
        log "Docker ist installiert und ausreichend aktuell."
    else
        warn "Docker ist installiert, aber möglicherweise nicht ausreichend aktuell."
        warn "Es wird empfohlen, Docker auf mindestens Version 20.10.0 zu aktualisieren."
    fi
    
    return 0
}

# Funktion zum Überprüfen, ob Docker Compose installiert ist
check_docker_compose() {
    log "Überprüfe Docker Compose-Installation..."
    
    # Prüfe zunächst das neue Docker-Compose-Plugin
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Versuche, die Version zu ermitteln
        docker_compose_version=$(docker compose version --short 2>/dev/null || docker compose version 2>/dev/null | grep -oE "v?[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        
        if [ -n "$docker_compose_version" ]; then
            # Entferne ein mögliches 'v' am Anfang
            docker_compose_version=${docker_compose_version#v}
            log "Docker Compose Plugin Version: $docker_compose_version"
            
            # Richte den Alias ein
            setup_docker_compose_alias
            
            return 0
        fi
    fi
    
    # Prüfe das eigenständige Docker-Compose-Binary
    if command -v docker-compose &> /dev/null; then
        log "Eigenständiges Docker Compose ist installiert."
        
        docker_compose_version=$(docker-compose --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        if [ -n "$docker_compose_version" ]; then
            log "Docker Compose Version: $docker_compose_version"
            
            # Vergleiche mit der Mindestversion
            if [ "$(printf '%s\n' "1.29.0" "$docker_compose_version" | sort -V | head -n1)" != "1.29.0" ]; then
                log "Docker Compose ist ausreichend aktuell."
                return 0
            else
                warn "Docker Compose Version ist älter als 1.29.0. Ein Update wird empfohlen."
            fi
        fi
    fi
    
    # Wenn wir hier ankommen, müssen wir Docker Compose installieren oder aktualisieren
    warn "Docker Compose ist nicht installiert oder zu alt. Versuche zu installieren/aktualisieren..."
    
    # Erkennen des Betriebssystems und der Paketmanager
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        OS=$(uname -s)
    fi
    
    case $OS in
        ubuntu|debian|linuxmint)
            log "Erkanntes Betriebssystem: $OS"
            log "Installiere Docker Compose Plugin mit apt..."
            sudo apt-get update
            sudo apt-get install -y docker-compose-plugin
            ;;
        fedora|centos|rhel)
            log "Erkanntes Betriebssystem: $OS"
            log "Installiere Docker Compose Plugin mit dnf..."
            sudo dnf -y install docker-compose-plugin
            ;;
        arch|manjaro)
            log "Erkanntes Betriebssystem: $OS"
            log "Installiere Docker Compose mit pacman..."
            sudo pacman -Sy docker-compose
            ;;
        *)
            # Fallback auf das Docker-Compose-Binary
            log "Installiere Docker Compose Binary direkt..."
            COMPOSE_VERSION="v2.20.3"
            sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            log "Docker Compose $COMPOSE_VERSION wurde installiert."
            ;;
    esac
    
    # Prüfe, ob die Installation erfolgreich war
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin wurde erfolgreich installiert."
        # Richte den Alias ein
        setup_docker_compose_alias
        return 0
    elif command -v docker-compose &> /dev/null; then
        log "Eigenständiges Docker Compose wurde erfolgreich installiert."
        return 0
    else
        error "Docker Compose konnte nicht installiert werden. Bitte installieren Sie Docker Compose manuell."
        return 1
    fi
}

# Funktion zum Starten des Docker-Daemons
start_docker_daemon() {
    log "Überprüfe, ob der Docker-Daemon läuft..."
    
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

# Funktion zum Kopieren der Docker-Compose-Datei
copy_docker_compose() {
    local src_file="$1"
    local dst_file="$2"
    
    log "Kopiere Docker-Compose-Datei von $src_file nach $dst_file..."
    
    if [ ! -f "$src_file" ]; then
        error "Docker-Compose-Datei nicht gefunden: $src_file"
        return 1
    fi
    
    # Prüfe, ob das Zielverzeichnis existiert
    mkdir -p "$(dirname "$dst_file")"
    
    cp "$src_file" "$dst_file"
    log "Docker-Compose-Datei wurde kopiert: $dst_file"
    return 0
}

# Funktion zum Überprüfen und Installieren von Python-Abhängigkeiten
check_python_dependencies() {
    log "Überprüfe Python-Installation und Abhängigkeiten..."
    
    # Prüfe Python-Version
    if ! command -v python3 &> /dev/null; then
        warn "Python 3 ist nicht installiert. Versuche zu installieren..."
        
        # Erkennen des Betriebssystems und der Paketmanager
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        else
            OS=$(uname -s)
        fi
        
        case $OS in
            ubuntu|debian|linuxmint)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Python 3 mit apt..."
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
                ;;
            fedora|centos|rhel)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Python 3 mit dnf..."
                sudo dnf -y install python3 python3-pip python3-devel
                ;;
            arch|manjaro)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Python 3 mit pacman..."
                sudo pacman -Sy python python-pip
                ;;
            *)
                error "Nicht unterstütztes Betriebssystem: $OS"
                error "Bitte installieren Sie Python 3 manuell."
                return 1
                ;;
        esac
    fi
    
    # Prüfe Python-Version
    python_version=$(python3 --version 2>&1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
    if [ -n "$python_version" ]; then
        log "Python Version: $python_version"
        
        # Vergleiche mit der Mindestversion
        if [ "$(printf '%s\n' "3.6.0" "$python_version" | sort -V | head -n1)" != "3.6.0" ]; then
            log "Python ist ausreichend aktuell."
        else
            warn "Python Version ist älter als 3.6.0. Ein Update wird empfohlen."
        fi
    fi
    
    # Prüfe pip-Installation
    if ! command -v pip3 &> /dev/null; then
        warn "pip3 ist nicht installiert. Versuche zu installieren..."
        
        # Erkennen des Betriebssystems und der Paketmanager
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        else
            OS=$(uname -s)
        fi
        
        case $OS in
            ubuntu|debian|linuxmint)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere pip3 mit apt..."
                sudo apt-get update
                sudo apt-get install -y python3-pip
                ;;
            fedora|centos|rhel)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere pip3 mit dnf..."
                sudo dnf -y install python3-pip
                ;;
            arch|manjaro)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere pip mit pacman..."
                sudo pacman -Sy python-pip
                ;;
            *)
                # Fallback auf get-pip.py
                log "Installiere pip mit get-pip.py..."
                curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                python3 get-pip.py --user
                rm get-pip.py
                ;;
        esac
    fi
    
    # Installiere benötigte Python-Pakete
    log "Installiere benötigte Python-Pakete..."
    pip3 install --user requests pyyaml
    
    return 0
}

# Hauptfunktion
main() {
    log "Starte Installation der MCP-Server..."
    
    # Überprüfe, ob Docker installiert ist
    check_docker || exit 1
    
    # Überprüfe, ob Docker Compose installiert ist
    check_docker_compose || exit 1
    
    # Starte den Docker-Daemon
    start_docker_daemon || exit 1
    
    # Überprüfe Python-Abhängigkeiten
    check_python_dependencies || exit 1
    
    # Kopiere die Docker-Compose-Datei, wenn Pfade angegeben sind
    if [ $# -eq 2 ]; then
        copy_docker_compose "$1" "$2" || exit 1
    else
        log "Standard-Docker-Compose-Datei wird verwendet."
        
        # Pfade für Docker-Compose-Dateien
        src_file="/workspace/Dev-Server-Workflow/docker-mcp-servers/docker-compose-full.yml"
        dst_file="/workspace/Dev-Server-Workflow/docker-mcp-servers/docker-compose.yml"
        
        if [ -f "$src_file" ]; then
            copy_docker_compose "$src_file" "$dst_file" || exit 1
        else
            warn "Quell-Docker-Compose-Datei nicht gefunden: $src_file"
            warn "Bitte geben Sie die Pfade zur Quell- und Ziel-Docker-Compose-Datei an."
        fi
    fi
    
    # Starte die MCP-Server
    log "Starte die MCP-Server..."
    if [ -f "/workspace/Dev-Server-Workflow/scripts/start-mcp-servers.sh" ]; then
        cd /workspace/Dev-Server-Workflow && ./scripts/start-mcp-servers.sh
    else
        cd /workspace/Dev-Server-Workflow && ./start-mcp-servers.sh
    fi
    
    # Integriere die MCP-Server mit OpenHands
    log "Integriere die MCP-Server mit OpenHands..."
    if [ -f "/workspace/Dev-Server-Workflow/scripts/integrate-mcp-with-openhands.py" ]; then
        cd /workspace/Dev-Server-Workflow && python3 ./scripts/integrate-mcp-with-openhands.py
    fi
    
    log "Installation der MCP-Server abgeschlossen."
    log "Sie können die MCP-Server mit dem folgenden Befehl starten:"
    log "  cd /workspace/Dev-Server-Workflow && ./scripts/start-mcp-servers.sh"
    log "Sie können die MCP-Server mit dem folgenden Befehl stoppen:"
    log "  cd /workspace/Dev-Server-Workflow/docker-mcp-servers && ./stop-mcp-servers.sh"
    
    return 0
}

# Führe die Hauptfunktion aus
main "$@"
