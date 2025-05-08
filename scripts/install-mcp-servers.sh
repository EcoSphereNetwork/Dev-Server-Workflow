#!/bin/bash

# Hauptinstallationsskript für MCP-Server

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
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

# Funktion zum Überprüfen, ob Docker installiert ist
check_docker() {
    if ! command -v docker &> /dev/null; then
        warn "Docker ist nicht installiert. Versuche, es zu installieren..."
        
        # Installiere Docker
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
        else
            error "Konnte Docker nicht automatisch installieren. Bitte installieren Sie Docker manuell."
            return 1
        fi
        
        # Starte Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Füge den aktuellen Benutzer zur Docker-Gruppe hinzu
        sudo usermod -aG docker $USER
        
        log "Docker wurde installiert. Bitte starten Sie die Shell neu, um die Docker-Gruppe zu aktivieren."
        log "Führen Sie dann dieses Skript erneut aus."
        exit 0
    fi
    
    log "Docker ist installiert."
    return 0
}

# Funktion zum Überprüfen, ob Docker Compose installiert ist
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        warn "Docker Compose ist nicht installiert. Versuche, es zu installieren..."
        
        # Installiere Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        if ! command -v docker-compose &> /dev/null; then
            error "Konnte Docker Compose nicht installieren. Bitte installieren Sie Docker Compose manuell."
            return 1
        fi
    fi
    
    log "Docker Compose ist installiert."
    return 0
}

# Funktion zum Starten des Docker-Daemons
start_docker_daemon() {
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
    
    if [ ! -f "$src_file" ]; then
        error "Docker-Compose-Datei nicht gefunden: $src_file"
        return 1
    fi
    
    cp "$src_file" "$dst_file"
    log "Docker-Compose-Datei wurde kopiert: $dst_file"
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
    
    # Kopiere die Docker-Compose-Datei
    copy_docker_compose "/workspace/Dev-Server-Workflow/docker-mcp-servers/docker-compose-full.yml" "/workspace/Dev-Server-Workflow/docker-mcp-servers/docker-compose.yml" || exit 1
    
    # Starte die MCP-Server
    log "Starte die MCP-Server..."
    cd /workspace/Dev-Server-Workflow && ./scripts/start-mcp-servers.sh
    
    # Integriere die MCP-Server mit OpenHands
    log "Integriere die MCP-Server mit OpenHands..."
    cd /workspace/Dev-Server-Workflow && ./scripts/integrate-mcp-with-openhands.py
    
    log "Installation der MCP-Server abgeschlossen."
    log "Sie können die MCP-Server mit dem folgenden Befehl starten:"
    log "  cd /workspace/Dev-Server-Workflow && ./scripts/start-mcp-servers.sh"
    log "Sie können die MCP-Server mit dem folgenden Befehl stoppen:"
    log "  cd /workspace/Dev-Server-Workflow/docker-mcp-servers && ./stop-mcp-servers.sh"
    
    return 0
}

# Führe die Hauptfunktion aus
main