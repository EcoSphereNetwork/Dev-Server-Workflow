#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Docker-Start-Skript für n8n Workflow Integration

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funktion zum Anzeigen von Hilfe
show_help() {
  log_info "${YELLOW}n8n Workflow Integration - Docker-Steuerung${NC}"
  echo ""
  log_info "Verwendung:"
  log_info "  ./docker-start.sh [Befehl]"
  echo ""
  log_info "Befehle:"
  log_info "  start       Startet alle Container"
  log_info "  stop        Stoppt alle Container"
  log_info "  restart     Startet alle Container neu"
  log_info "  status      Zeigt den Status aller Container an"
  log_info "  logs        Zeigt die Logs aller Container an"
  log_info "  setup       Führt das Setup-Skript aus"
  log_info "  help        Zeigt diese Hilfe an"
  echo ""
  log_info "Beispiele:"
  log_info "  ./docker-start.sh start"
  log_info "  ./docker-start.sh logs mcp-server"
}

# Überprüfe, ob Docker installiert ist
check_docker() {
  if ! command -v docker &> /dev/null; then
    log_info "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut.${NC}"
    exit 1
  fi

  if ! command -v docker compose &> /dev/null; then
    log_info "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut.${NC}"
    exit 1
  fi
}

# Überprüfe, ob die .env-Datei existiert
check_env_file() {
  if [ ! -f .env ]; then
    log_info "${YELLOW}Warnung: .env-Datei nicht gefunden. Erstelle eine Beispiel-Datei...${NC}"
    cat > .env << 'ENVEOF'
# n8n Konfiguration
N8N_URL=http://localhost:5678
N8N_USER=admin
N8N_PASSWORD=password
N8N_API_KEY=

# GitHub/GitLab Konfiguration
GITHUB_TOKEN=

# OpenProject Konfiguration
OPENPROJECT_URL=
OPENPROJECT_TOKEN=

# Weitere Konfigurationen...
ENVEOF
    log_info "${GREEN}.env-Datei erstellt. Bitte passen Sie die Werte an Ihre Umgebung an.${NC}"
  fi
}

# Starte die Container
start_containers() {
  log_info "${GREEN}Starte Container...${NC}"
  docker compose up -d
  log_info "${GREEN}Container gestartet. n8n ist unter http://localhost:5678 erreichbar.${NC}"
  log_info "${GREEN}MCP-Server ist unter http://localhost:3000 erreichbar.${NC}"
}

# Stoppe die Container
stop_containers() {
  log_info "${YELLOW}Stoppe Container...${NC}"
  docker compose down
  log_info "${GREEN}Container gestoppt.${NC}"
}

# Zeige den Status der Container an
show_status() {
  log_info "${GREEN}Status der Container:${NC}"
  docker compose ps
}

# Zeige die Logs der Container an
show_logs() {
  if [ -z "$1" ]; then
    log_info "${GREEN}Logs aller Container:${NC}"
    docker compose logs --tail=100
  else
    log_info "${GREEN}Logs des Containers $1:${NC}"
    docker compose logs --tail=100 "$1"
  fi
}

# Führe das Setup-Skript aus
run_setup() {
  log_info "${GREEN}Führe Setup-Skript aus...${NC}"
  docker compose run --rm setup
  log_info "${GREEN}Setup abgeschlossen.${NC}"
}

# Hauptfunktion
main() {
  check_docker
  check_env_file

  case "$1" in
    start)
      start_containers
      ;;
    stop)
      stop_containers
      ;;
    restart)
      stop_containers
      start_containers
      ;;
    status)
      show_status
      ;;
    logs)
      show_logs "$2"
      ;;
    setup)
      run_setup
      ;;
    help|"")
      show_help
      ;;
    *)
      log_info "${RED}Unbekannter Befehl: $1${NC}"
      show_help
      exit 1
      ;;
  esac
}

# Führe die Hauptfunktion aus
main "$@"
