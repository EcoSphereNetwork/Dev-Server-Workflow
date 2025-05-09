#!/bin/bash

# MCP-Server-Ökosystem-Einrichtungsskript
# Dieses Skript automatisiert die Einrichtung des MCP-Server-Ökosystems.

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion zum Überprüfen von Abhängigkeiten
check_dependencies() {
    echo -e "${BLUE}Überprüfe Abhängigkeiten...${NC}"
    
    # Überprüfe Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker ist nicht installiert. Bitte installiere Docker und versuche es erneut.${NC}"
        exit 1
    fi
    
    # Überprüfe Docker Compose
    if ! command -v docker compose &> /dev/null; then
        echo -e "${RED}Docker Compose ist nicht installiert. Bitte installiere Docker Compose und versuche es erneut.${NC}"
        exit 1
    fi
    
    # Überprüfe curl
    if ! command -v curl &> /dev/null; then
        echo -e "${YELLOW}curl ist nicht installiert. Einige Funktionen könnten nicht verfügbar sein.${NC}"
    fi
    
    # Überprüfe jq
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}jq ist nicht installiert. Einige Funktionen könnten nicht verfügbar sein.${NC}"
    fi
    
    echo -e "${GREEN}Alle erforderlichen Abhängigkeiten sind vorhanden.${NC}"
}

# Funktion zum Erstellen der Verzeichnisstruktur
create_directory_structure() {
    echo -e "${BLUE}Erstelle Verzeichnisstruktur...${NC}"
    
    mkdir -p nginx/ssl
    mkdir -p nginx/www
    mkdir -p gitlab/{config,logs,data}
    mkdir -p openproject/{assets,pgdata}
    mkdir -p logs
    mkdir -p backups
    
    echo -e "${GREEN}Verzeichnisstruktur erstellt.${NC}"
}

# Funktion zum Generieren von SSL-Zertifikaten
generate_ssl_certificates() {
    echo -e "${BLUE}Generiere selbstsignierte SSL-Zertifikate...${NC}"
    
    if [ ! -f nginx/ssl/server.crt ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/server.key \
            -out nginx/ssl/server.crt \
            -subj "/C=DE/ST=Berlin/L=Berlin/O=EcoSphereNetwork/OU=DevOps/CN=ecospherenet.work"
        
        echo -e "${GREEN}SSL-Zertifikate generiert.${NC}"
    else
        echo -e "${YELLOW}SSL-Zertifikate existieren bereits. Überspringe Generierung.${NC}"
    fi
}

# Funktion zum Erstellen der .env-Datei
create_env_file() {
    echo -e "${BLUE}Erstelle .env-Datei...${NC}"
    
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${GREEN}.env-Datei erstellt. Bitte passe die Werte in der .env-Datei an deine Bedürfnisse an.${NC}"
    else
        echo -e "${YELLOW}.env-Datei existiert bereits. Überspringe Erstellung.${NC}"
    fi
}

# Funktion zum Pullen der Docker-Images
pull_docker_images() {
    echo -e "${BLUE}Lade Docker-Images herunter...${NC}"
    
    docker compose pull
    
    echo -e "${GREEN}Docker-Images heruntergeladen.${NC}"
}

# Funktion zum Starten der Container
start_containers() {
    echo -e "${BLUE}Starte Container...${NC}"
    
    docker compose up -d
    
    echo -e "${GREEN}Container gestartet.${NC}"
}

# Funktion zum Überprüfen des Status der Container
check_container_status() {
    echo -e "${BLUE}Überprüfe Container-Status...${NC}"
    
    docker compose ps
    
    echo -e "${GREEN}Container-Status überprüft.${NC}"
}

# Funktion zum Anzeigen der Zugangsinformationen
show_access_information() {
    echo -e "${BLUE}Zugangsinformationen:${NC}"
    echo -e "${GREEN}OpenHands:${NC} http://openhands.ecospherenet.work"
    echo -e "${GREEN}n8n:${NC} http://n8n.ecospherenet.work"
    echo -e "${GREEN}GitLab:${NC} http://gitlab.ecospherenet.work"
    echo -e "${GREEN}OpenProject:${NC} http://openproject.eocspherenet.work"
    echo -e "${GREEN}AppFlowy:${NC} http://appflowy.ecospherenet.work"
    echo -e "${GREEN}MCP Inspector UI:${NC} http://inspector.ecospherenet.work"
    echo -e "${GREEN}MCP Server:${NC} http://mcp.ecospherenet.work"
    echo ""
    echo -e "${YELLOW}Hinweis:${NC} Stelle sicher, dass die Domains in deiner /etc/hosts-Datei oder in deinem DNS-Server konfiguriert sind."
    echo -e "Beispiel für /etc/hosts:"
    echo -e "127.0.0.1 openhands.ecospherenet.work n8n.ecospherenet.work gitlab.ecospherenet.work openproject.eocspherenet.work appflowy.ecospherenet.work inspector.ecospherenet.work mcp.ecospherenet.work"
}

# Hauptfunktion
main() {
    echo -e "${BLUE}=== MCP-Server-Ökosystem-Einrichtung ===${NC}"
    
    # Wechsle in das Projektverzeichnis
    cd /workspace/Dev-Server-Workflow/docker-mcp-ecosystem-improved
    
    # Führe die Einrichtungsschritte aus
    check_dependencies
    create_directory_structure
    generate_ssl_certificates
    create_env_file
    
    # Frage, ob Docker-Images heruntergeladen werden sollen
    read -p "Möchtest du die Docker-Images herunterladen? (j/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        pull_docker_images
    fi
    
    # Frage, ob Container gestartet werden sollen
    read -p "Möchtest du die Container starten? (j/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        start_containers
        check_container_status
    fi
    
    # Zeige Zugangsinformationen an
    show_access_information
    
    echo -e "${GREEN}=== MCP-Server-Ökosystem-Einrichtung abgeschlossen ===${NC}"
}

# Führe die Hauptfunktion aus
main