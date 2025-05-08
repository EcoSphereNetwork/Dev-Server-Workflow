#!/bin/bash

# Skript zum Starten der MCP-Server-Docker-Container

# Konfiguration
MCP_SERVERS_DIR="/workspace/Dev-Server-Workflow/docker-mcp-servers"
ENV_FILE="$MCP_SERVERS_DIR/.env"
DOCKER_COMPOSE_FILE="$MCP_SERVERS_DIR/docker-compose.yml"

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

# Überprüfen, ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    error "Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut."
    exit 1
fi

# Überprüfen, ob Docker Compose installiert ist
if ! command -v docker compose &> /dev/null; then
    error "Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut."
    exit 1
fi

# Überprüfen, ob der Docker-Daemon läuft
if ! docker info &> /dev/null; then
    warn "Docker-Daemon scheint nicht zu laufen. Versuche, ihn zu starten..."
    
    # Versuchen, den Docker-Daemon zu starten
    if command -v systemctl &> /dev/null; then
        sudo systemctl start docker
    elif command -v service &> /dev/null; then
        sudo service docker start
    else
        # Direkter Start des Docker-Daemons im Hintergrund
        sudo dockerd > /tmp/docker.log 2>&1 &
        sleep 5
    fi
    
    # Erneut überprüfen
    if ! docker info &> /dev/null; then
        error "Docker-Daemon konnte nicht gestartet werden. Bitte starten Sie ihn manuell."
        exit 1
    fi
    
    log "Docker-Daemon wurde erfolgreich gestartet."
fi

# Ins MCP-Servers-Verzeichnis wechseln
cd "$MCP_SERVERS_DIR" || {
    error "Konnte nicht in das Verzeichnis $MCP_SERVERS_DIR wechseln."
    exit 1
}

# Überprüfen, ob die .env-Datei existiert
if [ ! -f "$ENV_FILE" ]; then
    warn ".env-Datei nicht gefunden. Erstelle sie aus der Vorlage..."
    
    if [ -f "$MCP_SERVERS_DIR/.env.example" ]; then
        cp "$MCP_SERVERS_DIR/.env.example" "$ENV_FILE"
        log ".env-Datei wurde aus der Vorlage erstellt. Bitte passen Sie sie nach Bedarf an."
    else
        # Erstelle eine minimale .env-Datei
        cat > "$ENV_FILE" << EOF
# MCP Server Environment Variables
REDIS_PASSWORD=redis_password
GITHUB_TOKEN=your_github_token
WORKSPACE_PATH=/workspace
DISPLAY=:0
EOF
        log "Minimale .env-Datei wurde erstellt. Bitte passen Sie sie nach Bedarf an."
    fi
    
    # Pause, damit der Benutzer die .env-Datei bearbeiten kann
    read -p "Drücken Sie Enter, um fortzufahren, nachdem Sie die .env-Datei bearbeitet haben..."
fi

# Docker-Images pullen
log "Pulling Docker-Images für MCP-Server..."
./pull-images.sh

# Docker-Container starten
log "Starte MCP-Server-Docker-Container..."
docker compose -f "$DOCKER_COMPOSE_FILE" up -d

# Überprüfen, ob alle Container gestartet wurden
log "Überprüfe den Status der Container..."
docker compose -f "$DOCKER_COMPOSE_FILE" ps

# Warten, bis alle Container bereit sind
log "Warte, bis alle Container bereit sind..."
sleep 10

# Teste die MCP-Server
log "Teste die MCP-Server..."
./test-mcp-servers.py

log "MCP-Server wurden gestartet und getestet."
log "Sie können die Container mit dem folgenden Befehl stoppen:"
log "  cd $MCP_SERVERS_DIR && ./stop-mcp-servers.sh"

# Zeige die verfügbaren MCP-Server-URLs an
log "Verfügbare MCP-Server-URLs:"
log "  Filesystem MCP: http://localhost:3001"
log "  Desktop Commander MCP: http://localhost:3002"
log "  Sequential Thinking MCP: http://localhost:3003"
log "  GitHub Chat MCP: http://localhost:3004"
log "  GitHub MCP: http://localhost:3005"
log "  Puppeteer MCP: http://localhost:3006"
log "  Basic Memory MCP: http://localhost:3007"
log "  Wikipedia MCP: http://localhost:3008"

# Zeige Hinweise zur Integration mit n8n und OpenHands
log "Integration mit n8n:"
log "  1. Starten Sie n8n mit: docker compose up -d n8n"
log "  2. Importieren Sie den Workflow aus: src/ESN_Initial-Szenario/n8n-workflows/enhanced-mcp-trigger.json"
log "  3. Konfigurieren Sie die MCP-Server-URLs in den n8n-Umgebungsvariablen"

log "Integration mit OpenHands:"
log "  1. Kopieren Sie die Datei docker-mcp-servers/openhands-mcp-config.json in Ihr OpenHands-Konfigurationsverzeichnis"
log "  2. Starten Sie OpenHands neu, um die MCP-Integration zu aktivieren"

exit 0