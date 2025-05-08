#!/bin/bash
# Installationsfunktionen für die Dev-Server CLI Komponenten

# Source common functions
source "$(dirname "$0")/functions.sh"

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funktion zum Überprüfen der Docker-Installation
check_docker_installed() {
    if command -v docker &> /dev/null; then
        log_info "Docker ist installiert."
        return 0
    else
        log_error "Docker ist nicht installiert."
        return 1
    fi
}

# Funktion zum Überprüfen der Docker Compose-Installation
check_docker_compose_installed() {
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose ist installiert."
        return 0
    else
        log_error "Docker Compose ist nicht installiert."
        return 1
    fi
}

# Funktion zum Installieren von Docker
install_docker() {
    log_info "Installiere Docker..."
    
    # Überprüfe, ob Docker bereits installiert ist
    if check_docker_installed; then
        log_info "Docker ist bereits installiert."
        return 0
    fi
    
    # Installiere Docker
    log_info "Installiere Docker-Abhängigkeiten..."
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    
    log_info "Füge Docker-Repository hinzu..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    
    log_info "Installiere Docker..."
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Füge den aktuellen Benutzer zur Docker-Gruppe hinzu
    log_info "Füge Benutzer zur Docker-Gruppe hinzu..."
    sudo usermod -aG docker $USER
    
    log_info "Docker wurde erfolgreich installiert. Bitte starten Sie Ihre Shell neu, damit die Gruppenänderungen wirksam werden."
    return 0
}

# Funktion zum Installieren von Docker Compose
install_docker_compose() {
    log_info "Installiere Docker Compose..."
    
    # Überprüfe, ob Docker Compose bereits installiert ist
    if check_docker_compose_installed; then
        log_info "Docker Compose ist bereits installiert."
        return 0
    fi
    
    # Installiere Docker Compose
    log_info "Lade Docker Compose herunter..."
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    log_info "Setze Berechtigungen..."
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_info "Docker Compose wurde erfolgreich installiert."
    return 0
}

# Funktion zum Installieren von n8n
install_n8n() {
    log_info "Installiere n8n..."
    
    # Überprüfe, ob Docker installiert ist
    if ! check_docker_installed; then
        log_warn "Docker ist nicht installiert. Installiere Docker..."
        install_docker
    fi
    
    # Überprüfe, ob Docker Compose installiert ist
    if ! check_docker_compose_installed; then
        log_warn "Docker Compose ist nicht installiert. Installiere Docker Compose..."
        install_docker_compose
    fi
    
    # Erstelle das Docker-Netzwerk, falls es nicht existiert
    if ! docker network ls | grep -q "$DOCKER_NETWORK"; then
        log_info "Erstelle Docker-Netzwerk $DOCKER_NETWORK..."
        docker network create "$DOCKER_NETWORK"
    fi
    
    # Erstelle das Datenverzeichnis
    log_info "Erstelle Datenverzeichnis für n8n..."
    mkdir -p "$N8N_DATA_DIR"
    
    # Erstelle die Docker Compose-Datei
    log_info "Erstelle Docker Compose-Datei für n8n..."
    local compose_file="${DATA_DIR}/n8n-docker-compose.yml"
    
    cat > "$compose_file" << EOF
version: '3'

services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "${N8N_PORT}:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - ${N8N_DATA_DIR}:/home/node/.n8n
    networks:
      - ${DOCKER_NETWORK}

networks:
  ${DOCKER_NETWORK}:
    external: true
EOF
    
    # Starte n8n
    log_info "Starte n8n..."
    docker-compose -f "$compose_file" up -d
    
    if [ $? -eq 0 ]; then
        log_success "n8n wurde erfolgreich installiert und gestartet. Web-Interface verfügbar unter http://localhost:${N8N_PORT}"
        return 0
    else
        log_error "Fehler beim Starten von n8n."
        return 1
    fi
}

# Funktion zum Installieren von MCP
install_mcp() {
    log_info "Installiere MCP-Server..."
    
    # Überprüfe, ob Git installiert ist
    if ! command -v git &> /dev/null; then
        log_warn "Git ist nicht installiert. Installiere Git..."
        sudo apt-get update
        sudo apt-get install -y git
    fi
    
    # Überprüfe, ob Python installiert ist
    if ! command -v python3 &> /dev/null; then
        log_warn "Python 3 ist nicht installiert. Installiere Python 3..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    fi
    
    # Klone das MCP-Repository
    log_info "Klone MCP-Repository..."
    local mcp_dir="${BASE_DIR}/docker-mcp-ecosystem"
    
    if [ -d "$mcp_dir" ]; then
        log_info "MCP-Repository existiert bereits. Aktualisiere..."
        (cd "$mcp_dir" && git pull)
    else
        log_info "Klone MCP-Repository..."
        git clone https://github.com/EcoSphereNetwork/docker-mcp-ecosystem.git "$mcp_dir"
    fi
    
    # Installiere Python-Abhängigkeiten
    log_info "Installiere Python-Abhängigkeiten..."
    pip3 install -r "${mcp_dir}/requirements.txt"
    
    # Erstelle Konfigurationsdatei
    log_info "Erstelle MCP-Konfigurationsdatei..."
    local config_file="${mcp_dir}/config.json"
    
    cat > "$config_file" << EOF
{
    "docker_mcp_port": ${DOCKER_MCP_PORT},
    "n8n_mcp_port": ${N8N_MCP_PORT},
    "mcp_auth_token": "${MCP_AUTH_TOKEN}",
    "n8n_url": "${N8N_URL}",
    "n8n_api_key": "${N8N_API_KEY}"
}
EOF
    
    # Setze Ausführungsrechte für Skripte
    log_info "Setze Ausführungsrechte für MCP-Skripte..."
    chmod +x "${mcp_dir}/start-mcp-ecosystem.sh"
    chmod +x "${mcp_dir}/stop-mcp-ecosystem.sh"
    
    log_success "MCP-Server wurde erfolgreich installiert. Starte mit 'dev-server start mcp'."
    return 0
}

# Funktion zum Installieren von OpenHands
install_openhands() {
    log_info "Installiere OpenHands..."
    
    # Überprüfe, ob Docker installiert ist
    if ! check_docker_installed; then
        log_warn "Docker ist nicht installiert. Installiere Docker..."
        install_docker
    fi
    
    # Erstelle das Docker-Netzwerk, falls es nicht existiert
    if ! docker network ls | grep -q "$DOCKER_NETWORK"; then
        log_info "Erstelle Docker-Netzwerk $DOCKER_NETWORK..."
        docker network create "$DOCKER_NETWORK"
    fi
    
    # Erstelle das Datenverzeichnis
    log_info "Erstelle Datenverzeichnis für OpenHands..."
    mkdir -p "$OPENHANDS_DATA_DIR"
    
    # Ziehe das OpenHands-Image
    log_info "Ziehe OpenHands-Image..."
    docker pull openhands/openhands:latest
    
    # Erstelle die Docker Compose-Datei
    log_info "Erstelle Docker Compose-Datei für OpenHands..."
    local compose_file="${DATA_DIR}/openhands-docker-compose.yml"
    
    cat > "$compose_file" << EOF
version: '3'

services:
  openhands:
    image: openhands/openhands:latest
    restart: always
    ports:
      - "${OPENHANDS_PORT}:8080"
    environment:
      - OPENHANDS_API_KEY=${OPENHANDS_API_KEY}
      - LLM_API_KEY=${ANTHROPIC_API_KEY}
      - LLM_MODEL=${CLAUDE_MODEL}
    volumes:
      - ${OPENHANDS_DATA_DIR}:/root/.config/openhands
    networks:
      - ${DOCKER_NETWORK}

networks:
  ${DOCKER_NETWORK}:
    external: true
EOF
    
    # Starte OpenHands
    log_info "Starte OpenHands..."
    docker-compose -f "$compose_file" up -d
    
    if [ $? -eq 0 ]; then
        log_success "OpenHands wurde erfolgreich installiert und gestartet. API verfügbar unter http://localhost:${OPENHANDS_PORT}"
        return 0
    else
        log_error "Fehler beim Starten von OpenHands."
        return 1
    fi
}

# Funktion zum Installieren von AppFlowy
install_appflowy() {
    log_info "Installiere AppFlowy..."
    
    # Überprüfe, ob Docker installiert ist
    if ! check_docker_installed; then
        log_warn "Docker ist nicht installiert. Installiere Docker..."
        install_docker
    fi
    
    # Erstelle das Docker-Netzwerk, falls es nicht existiert
    if ! docker network ls | grep -q "$DOCKER_NETWORK"; then
        log_info "Erstelle Docker-Netzwerk $DOCKER_NETWORK..."
        docker network create "$DOCKER_NETWORK"
    fi
    
    # Erstelle das Datenverzeichnis
    log_info "Erstelle Datenverzeichnis für AppFlowy..."
    local appflowy_data_dir="${DATA_DIR}/appflowy"
    mkdir -p "$appflowy_data_dir"
    
    # Erstelle die Docker Compose-Datei
    log_info "Erstelle Docker Compose-Datei für AppFlowy..."
    local compose_file="${DATA_DIR}/appflowy-docker-compose.yml"
    local appflowy_port=8080
    
    cat > "$compose_file" << EOF
version: '3'

services:
  appflowy-cloud:
    image: appflowy/appflowy-cloud:latest
    restart: always
    ports:
      - "${appflowy_port}:8080"
    environment:
      - AF_PG_USER=postgres
      - AF_PG_PASSWORD=password
      - AF_PG_HOST=postgres
      - AF_PG_PORT=5432
      - AF_PG_DB=appflowy
      - AF_REDIS_HOST=redis
      - AF_REDIS_PORT=6379
    volumes:
      - ${appflowy_data_dir}:/app/data
    depends_on:
      - postgres
      - redis
    networks:
      - ${DOCKER_NETWORK}

  postgres:
    image: postgres:14
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=appflowy
    volumes:
      - ${appflowy_data_dir}/postgres:/var/lib/postgresql/data
    networks:
      - ${DOCKER_NETWORK}

  redis:
    image: redis:7
    restart: always
    volumes:
      - ${appflowy_data_dir}/redis:/data
    networks:
      - ${DOCKER_NETWORK}

networks:
  ${DOCKER_NETWORK}:
    external: true
EOF
    
    # Starte AppFlowy
    log_info "Starte AppFlowy..."
    docker-compose -f "$compose_file" up -d
    
    if [ $? -eq 0 ]; then
        log_success "AppFlowy wurde erfolgreich installiert und gestartet. Verfügbar unter http://localhost:${appflowy_port}"
        
        # Aktualisiere die Konfigurationsdatei
        log_info "Aktualisiere Konfigurationsdatei..."
        local config_file="${CONFIG_DIR}/dev-server.conf"
        
        # Füge AppFlowy-Konfiguration hinzu, falls nicht vorhanden
        if ! grep -q "APPFLOWY_PORT" "$config_file"; then
            echo -e "\n# AppFlowy-Konfiguration" >> "$config_file"
            echo "APPFLOWY_PORT=${appflowy_port}" >> "$config_file"
            echo "APPFLOWY_DATA_DIR=\"${appflowy_data_dir}\"" >> "$config_file"
        fi
        
        return 0
    else
        log_error "Fehler beim Starten von AppFlowy."
        return 1
    fi
}

# Funktion zum Installieren von Llamafile
install_llamafile() {
    log_info "Installiere Llamafile..."
    
    # Erstelle das Modellverzeichnis
    log_info "Erstelle Modellverzeichnis..."
    mkdir -p "$MODELS_DIR"
    
    # Lade Llamafile herunter
    log_info "Lade Llamafile herunter..."
    wget -O "$LLAMAFILE_PATH" "$LLAMAFILE_URL"
    
    if [ $? -ne 0 ]; then
        log_error "Fehler beim Herunterladen von Llamafile."
        return 1
    fi
    
    # Setze Ausführungsrechte
    log_info "Setze Ausführungsrechte..."
    chmod +x "$LLAMAFILE_PATH"
    
    log_success "Llamafile wurde erfolgreich installiert. Starte mit 'dev-server start llamafile'."
    return 0
}

# Funktion zum Installieren von Ollama
install_ollama() {
    log_info "Installiere Ollama..."
    
    # Überprüfe, ob Docker installiert ist
    if ! check_docker_installed; then
        log_warn "Docker ist nicht installiert. Installiere Docker..."
        install_docker
    fi
    
    # Erstelle das Docker-Netzwerk, falls es nicht existiert
    if ! docker network ls | grep -q "$DOCKER_NETWORK"; then
        log_info "Erstelle Docker-Netzwerk $DOCKER_NETWORK..."
        docker network create "$DOCKER_NETWORK"
    fi
    
    # Erstelle das Datenverzeichnis
    log_info "Erstelle Datenverzeichnis für Ollama..."
    mkdir -p "$OLLAMA_DATA_DIR"
    
    # Ziehe das Ollama-Image
    log_info "Ziehe Ollama-Image..."
    docker pull ollama/ollama:latest
    
    # Erstelle die Docker Compose-Datei
    log_info "Erstelle Docker Compose-Datei für Ollama..."
    local compose_file="${DATA_DIR}/ollama-docker-compose.yml"
    
    cat > "$compose_file" << EOF
version: '3'

services:
  ollama:
    image: ollama/ollama:latest
    restart: always
    ports:
      - "${OLLAMA_PORT}:11434"
    volumes:
      - ${OLLAMA_DATA_DIR}:/root/.ollama
    networks:
      - ${DOCKER_NETWORK}

networks:
  ${DOCKER_NETWORK}:
    external: true
EOF
    
    # Starte Ollama
    log_info "Starte Ollama..."
    docker-compose -f "$compose_file" up -d
    
    if [ $? -eq 0 ]; then
        log_success "Ollama wurde erfolgreich installiert und gestartet. API verfügbar unter http://localhost:${OLLAMA_PORT}"
        
        # Ziehe das Standardmodell
        if [ -n "$OLLAMA_DEFAULT_MODEL" ]; then
            log_info "Ziehe Standardmodell ${OLLAMA_DEFAULT_MODEL}..."
            sleep 5 # Warte, bis Ollama initialisiert ist
            docker exec ollama ollama pull "$OLLAMA_DEFAULT_MODEL"
        fi
        
        return 0
    else
        log_error "Fehler beim Starten von Ollama."
        return 1
    fi
}

# Funktion zum Installieren der Web-UI
install_web_ui() {
    log_info "Installiere Web-UI..."
    
    # Überprüfe, ob Node.js installiert ist
    if ! command -v node &> /dev/null; then
        log_warn "Node.js ist nicht installiert. Installiere Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    # Überprüfe, ob npm installiert ist
    if ! command -v npm &> /dev/null; then
        log_warn "npm ist nicht installiert. Installiere npm..."
        sudo apt-get install -y npm
    fi
    
    # Überprüfe, ob das Web-UI-Verzeichnis existiert
    if [ ! -d "$WEB_UI_DIR" ]; then
        log_error "Web-UI-Verzeichnis existiert nicht: $WEB_UI_DIR"
        return 1
    fi
    
    # Installiere Abhängigkeiten
    log_info "Installiere Web-UI-Abhängigkeiten..."
    (cd "$WEB_UI_DIR" && npm install)
    
    if [ $? -ne 0 ]; then
        log_error "Fehler beim Installieren der Web-UI-Abhängigkeiten."
        return 1
    fi
    
    # Erstelle Build
    log_info "Erstelle Web-UI-Build..."
    (cd "$WEB_UI_DIR" && npm run build)
    
    if [ $? -ne 0 ]; then
        log_error "Fehler beim Erstellen des Web-UI-Builds."
        return 1
    fi
    
    log_success "Web-UI wurde erfolgreich installiert. Starte mit 'dev-server web-ui start'."
    return 0
}

# Funktion zum Installieren aller Komponenten
install_all() {
    log_info "Installiere alle Komponenten..."
    
    install_docker
    install_docker_compose
    install_n8n
    install_mcp
    install_openhands
    install_appflowy
    install_llamafile
    install_ollama
    install_web_ui
    
    log_success "Alle Komponenten wurden erfolgreich installiert."
    return 0
}

# Hauptfunktion zum Installieren einer Komponente
install_component() {
    local component="$1"
    
    case "$component" in
        "all")
            install_all
            ;;
        "docker")
            install_docker
            ;;
        "docker-compose")
            install_docker_compose
            ;;
        "n8n")
            install_n8n
            ;;
        "mcp")
            install_mcp
            ;;
        "openhands")
            install_openhands
            ;;
        "appflowy")
            install_appflowy
            ;;
        "llamafile")
            install_llamafile
            ;;
        "ollama")
            install_ollama
            ;;
        "web-ui")
            install_web_ui
            ;;
        *)
            log_error "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: all, docker, docker-compose, n8n, mcp, openhands, appflowy, llamafile, ollama, web-ui"
            return 1
            ;;
    esac
}

# Führe die Hauptfunktion aus, wenn das Skript direkt ausgeführt wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        log_error "Keine Komponente angegeben."
        echo "Verwendung: $0 <Komponente>"
        echo "Verfügbare Komponenten: all, docker, docker-compose, n8n, mcp, openhands, appflowy, llamafile, ollama, web-ui"
        exit 1
    fi
    
    install_component "$1"
fi