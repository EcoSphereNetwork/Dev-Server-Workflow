#!/bin/bash

# Verbessertes Hauptinstallationsskript für das gesamte Dev-Server-Workflow-Projekt
# Überprüft Paketversionen und richtet Aliase ein

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

    # Vergleiche Versionen - nutze "sort -V" und kehre die Logik um, da wir prüfen, ob current >= min
    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" = "$min_version" ]; then
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
                echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
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
            if [ "$(printf '%s\n' "1.29.0" "$docker_compose_version" | sort -V | head -n1)" = "1.29.0" ]; then
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

# Funktion zum Installieren von n8n
install_n8n() {
    log "Installiere n8n..."
    
    # Überprüfe, ob n8n bereits installiert ist
    if command -v n8n &> /dev/null; then
        n8n_version=$(n8n --version 2>/dev/null | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        log "n8n ist bereits installiert (Version: $n8n_version)."
        
        # Überprüfe, ob ein Update erforderlich ist
        if [ "$(printf '%s\n' "0.225.0" "$n8n_version" | sort -V | head -n1)" = "0.225.0" ]; then
            log "n8n Version ist ausreichend aktuell."
            return 0
        else
            warn "n8n Version ist veraltet. Ein Update wird empfohlen."
            
            # Frage den Benutzer, ob n8n aktualisiert werden soll
            read -p "Möchten Sie n8n aktualisieren? (j/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Jj]$ ]]; then
                log "Aktualisiere n8n..."
                # Verwende npm, wenn es installiert ist
                if command -v npm &> /dev/null; then
                    npm update -g n8n
                else
                    warn "npm ist nicht installiert. Bitte installieren Sie npm und aktualisieren Sie n8n manuell."
                    return 1
                fi
            else
                log "n8n wird nicht aktualisiert."
                return 0
            fi
        fi
    else
        # Prüfe, ob npm installiert ist
        if ! command -v npm &> /dev/null; then
            warn "npm ist nicht installiert. Versuche, es zu installieren..."
            
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
                    log "Installiere npm mit apt..."
                    sudo apt-get update
                    sudo apt-get install -y nodejs npm
                    ;;
                fedora|centos|rhel)
                    log "Erkanntes Betriebssystem: $OS"
                    log "Installiere npm mit dnf..."
                    sudo dnf -y install nodejs npm
                    ;;
                arch|manjaro)
                    log "Erkanntes Betriebssystem: $OS"
                    log "Installiere npm mit pacman..."
                    sudo pacman -Sy nodejs npm
                    ;;
                *)
                    error "Nicht unterstütztes Betriebssystem: $OS"
                    error "Bitte installieren Sie npm manuell und führen Sie dann dieses Skript erneut aus."
                    return 1
                    ;;
            esac
        fi
        
        # Installiere n8n
        log "Installiere n8n über npm..."
        npm install -g n8n
        
        # Überprüfe, ob die Installation erfolgreich war
        if command -v n8n &> /dev/null; then
            n8n_version=$(n8n --version 2>/dev/null | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
            log "n8n wurde erfolgreich installiert (Version: $n8n_version)."
            return 0
        else
            error "n8n konnte nicht installiert werden. Bitte installieren Sie n8n manuell."
            return 1
        fi
    fi
    
    return 0
}

# Funktion zum Anzeigen des Fortschritts
show_progress() {
    local step=$1
    local total=$2
    local description=$3
    
    echo -e "${BLUE}[${step}/${total}]${NC} ${description}"
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
        if [ "$(printf '%s\n' "3.6.0" "$python_version" | sort -V | head -n1)" = "3.6.0" ]; then
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
    # Aktuelle Arbeitsverzeichnisse speichern
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    ROOT_DIR="$(dirname "$SCRIPT_DIR")"
    
    log "Starte Installation des Dev-Server-Workflow-Projekts..."
    
    # Anzahl der Schritte
    local total_steps=6
    local current_step=1
    
    # Schritt 1: Prüfe Abhängigkeiten
    show_progress $current_step $total_steps "Prüfe Abhängigkeiten..."
    check_docker || exit 1
    check_docker_compose || exit 1
    start_docker_daemon || exit 1
    check_python_dependencies || exit 1
    current_step=$((current_step + 1))
    
    # Schritt 2: Installiere die MCP-Server
    show_progress $current_step $total_steps "Installiere die MCP-Server..."
    if [ -f "$SCRIPT_DIR/install-mcp-servers.sh" ]; then
        "$SCRIPT_DIR/install-mcp-servers.sh"
        check_result "Installation der MCP-Server fehlgeschlagen."
    else
        warn "MCP-Server-Installationsskript nicht gefunden, überspringe..."
    fi
    current_step=$((current_step + 1))
    
    # Schritt 3: Starte die MCP-Server
    show_progress $current_step $total_steps "Starte die MCP-Server..."
    if [ -d "$ROOT_DIR/docker-mcp-servers" ]; then
        # Speichern des aktuellen Verzeichnisses
        CURRENT_DIR="$(pwd)"
        
        # Wechseln ins docker-mcp-servers-Verzeichnis
        cd "$ROOT_DIR/docker-mcp-servers"
        
        # Starten der MCP-Server
        if [ -f "./start-mcp-servers.sh" ]; then
            ./start-mcp-servers.sh
            check_result "Starten der MCP-Server fehlgeschlagen."
        else
            warn "start-mcp-servers.sh nicht gefunden im Verzeichnis docker-mcp-servers"
        fi
        
        # Zurück zum ursprünglichen Verzeichnis
        cd "$CURRENT_DIR"
    else
        warn "MCP-Server-Verzeichnis nicht gefunden, überspringe..."
    fi
    current_step=$((current_step + 1))
    
    # Schritt 4: Installiere n8n
    show_progress $current_step $total_steps "Installiere n8n..."
    
    # Überprüfe, ob n8n bereits installiert ist
    if ! command -v n8n &> /dev/null; then
        log "n8n ist nicht installiert. Installiere n8n..."
        install_n8n
        check_result "Installation von n8n fehlgeschlagen."
    else
        log "n8n ist bereits installiert."
    fi
    
    # Starte n8n im Hintergrund
    log "Starte n8n im Hintergrund..."
    n8n start &
    sleep 10
    
    current_step=$((current_step + 1))
    
    # Schritt 5: Integriere die MCP-Server mit n8n
    show_progress $current_step $total_steps "Integriere die MCP-Server mit n8n..."
    
    # Frage nach dem n8n-API-Key
    read -p "Bitte geben Sie den n8n-API-Key ein: " n8n_api_key
    
    if [ -f "$SCRIPT_DIR/integrate-mcp-with-n8n.py" ]; then
        python3 "$SCRIPT_DIR/integrate-mcp-with-n8n.py" --n8n-api-key "$n8n_api_key"
        check_result "Integration der MCP-Server mit n8n fehlgeschlagen."
    elif [ -f "$ROOT_DIR/docker-mcp-servers/n8n-mcp-integration.py" ]; then
        python3 "$ROOT_DIR/docker-mcp-servers/n8n-mcp-integration.py" --n8n-api-key "$n8n_api_key"
        check_result "Integration der MCP-Server mit n8n fehlgeschlagen."
    else
        warn "n8n-Integration-Skript nicht gefunden, überspringe..."
    fi
    
    current_step=$((current_step + 1))
    
    # Schritt 6: Integriere die MCP-Server mit OpenHands
    show_progress $current_step $total_steps "Integriere die MCP-Server mit OpenHands..."
    
    # Frage nach dem GitHub-Token
    read -p "Bitte geben Sie das GitHub-Token ein (oder drücken Sie Enter, um zu überspringen): " github_token
    
    # Frage nach dem OpenHands-Konfigurationsverzeichnis
    read -p "Bitte geben Sie das OpenHands-Konfigurationsverzeichnis ein (oder drücken Sie Enter, um zu überspringen): " openhands_config_dir
    
    if [ -n "$openhands_config_dir" ]; then
        if [ -n "$github_token" ]; then
            if [ -f "$SCRIPT_DIR/integrate-mcp-with-openhands.py" ]; then
                python3 "$SCRIPT_DIR/integrate-mcp-with-openhands.py" --openhands-config-dir "$openhands_config_dir" --github-token "$github_token"
                check_result "Integration der MCP-Server mit OpenHands fehlgeschlagen."
            elif [ -f "$ROOT_DIR/docker-mcp-servers/openhands-mcp-integration.py" ]; then
                python3 "$ROOT_DIR/docker-mcp-servers/openhands-mcp-integration.py" --openhands-config-dir "$openhands_config_dir" --github-token "$github_token"
                check_result "Integration der MCP-Server mit OpenHands fehlgeschlagen."
            else
                warn "OpenHands-Integration-Skript nicht gefunden, überspringe..."
            fi
        else
            if [ -f "$SCRIPT_DIR/integrate-mcp-with-openhands.py" ]; then
                python3 "$SCRIPT_DIR/integrate-mcp-with-openhands.py" --openhands-config-dir "$openhands_config_dir"
                check_result "Integration der MCP-Server mit OpenHands fehlgeschlagen."
            elif [ -f "$ROOT_DIR/docker-mcp-servers/openhands-mcp-integration.py" ]; then
                python3 "$ROOT_DIR/docker-mcp-servers/openhands-mcp-integration.py" --openhands-config-dir "$openhands_config_dir"
                check_result "Integration der MCP-Server mit OpenHands fehlgeschlagen."
            else
                warn "OpenHands-Integration-Skript nicht gefunden, überspringe..."
            fi
        fi
    else
        log "Integration mit OpenHands übersprungen."
    fi
    
    # Installation abgeschlossen
    log "Installation des Dev-Server-Workflow-Projekts abgeschlossen!"
    log "Sie können die MCP-Server mit dem folgenden Befehl stoppen:"
    log "  cd $ROOT_DIR/docker-mcp-servers && ./stop-mcp-servers.sh"
    log "Sie können n8n mit dem folgenden Befehl stoppen:"
    log "  pkill -f n8n"
    
    return 0
}

# Funktion zum Überprüfen, ob ein Befehl erfolgreich ausgeführt wurde
check_result() {
    if [ $? -ne 0 ]; then
        error "$1"
        exit 1
    fi
}

# Führe die Hauptfunktion aus
main
