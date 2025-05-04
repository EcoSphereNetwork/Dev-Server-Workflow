#!/bin/bash

# Docker-Start-Skript für n8n Workflow Integration

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funktion zum Anzeigen von Hilfe
show_help() {
  echo -e "${YELLOW}n8n Workflow Integration - Docker-Steuerung${NC}"
  echo ""
  echo "Verwendung:"
  echo "  ./docker-start.sh [Befehl]"
  echo ""
  echo "Befehle:"
  echo "  start       Startet alle Container"
  echo "  stop        Stoppt alle Container"
  echo "  restart     Startet alle Container neu"
  echo "  status      Zeigt den Status aller Container an"
  echo "  logs        Zeigt die Logs aller Container an"
  echo "  setup       Führt das Setup-Skript aus"
  echo "  help        Zeigt diese Hilfe an"
  echo ""
  echo "Beispiele:"
  echo "  ./docker-start.sh start"
  echo "  ./docker-start.sh logs mcp-server"
}

# Überprüfe, ob Docker installiert ist
check_docker() {
  if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut.${NC}"
    exit 1
  fi

  if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose und versuchen Sie es erneut.${NC}"
    exit 1
  fi
}

# Überprüfe, ob die .env-Datei existiert
check_env_file() {
  if [ ! -f .env ]; then
    echo -e "${YELLOW}Warnung: .env-Datei nicht gefunden. Erstelle eine Beispiel-Datei...${NC}"
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
    echo -e "${GREEN}.env-Datei erstellt. Bitte passen Sie die Werte an Ihre Umgebung an.${NC}"
  fi
}

# Starte die Container
start_containers() {
  echo -e "${GREEN}Starte Container...${NC}"
  docker-compose up -d
  echo -e "${GREEN}Container gestartet. n8n ist unter http://localhost:5678 erreichbar.${NC}"
  echo -e "${GREEN}MCP-Server ist unter http://localhost:3000 erreichbar.${NC}"
}

# Stoppe die Container
stop_containers() {
  echo -e "${YELLOW}Stoppe Container...${NC}"
  docker-compose down
  echo -e "${GREEN}Container gestoppt.${NC}"
}

# Zeige den Status der Container an
show_status() {
  echo -e "${GREEN}Status der Container:${NC}"
  docker-compose ps
}

# Zeige die Logs der Container an
show_logs() {
  if [ -z "$1" ]; then
    echo -e "${GREEN}Logs aller Container:${NC}"
    docker-compose logs --tail=100
  else
    echo -e "${GREEN}Logs des Containers $1:${NC}"
    docker-compose logs --tail=100 "$1"
  fi
}

# Führe das Setup-Skript aus
run_setup() {
  echo -e "${GREEN}Führe Setup-Skript aus...${NC}"
  docker-compose run --rm setup
  echo -e "${GREEN}Setup abgeschlossen.${NC}"
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
      echo -e "${RED}Unbekannter Befehl: $1${NC}"
      show_help
      exit 1
      ;;
  esac
}

# Führe die Hauptfunktion aus
main "$@"
