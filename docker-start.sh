#!/bin/bash

# Verbessertes Docker-Start-Skript für das Dev-Server-Workflow-Projekt
# Dieses Skript startet die Docker-Container für das Projekt

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Standardwerte
ACTION="help"
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
PRODUCTION=false
VERBOSE=false

# Funktion zum Anzeigen von Hilfe
show_help() {
    log_info "${BLUE}Docker-Start-Skript für Dev-Server-Workflow${NC}"
    log_info "Dieses Skript verwaltet die Docker-Container für das Projekt."
    echo ""
    log_info "Verwendung:"
    log_info "  $0 [Aktion] [Optionen]"
    echo ""
    log_info "Aktionen:"
    log_info "  start       Startet die Docker-Container"
    log_info "  stop        Stoppt die Docker-Container"
    log_info "  restart     Startet die Docker-Container neu"
    log_info "  status      Zeigt den Status der Docker-Container an"
    log_info "  logs        Zeigt die Logs der Docker-Container an"
    log_info "  setup       Führt das Setup für die Docker-Container aus"
    log_info "  help        Zeigt diese Hilfe an"
    echo ""
    log_info "Optionen:"
    log_info "  -e, --env FILE      Verwendet die angegebene .env-Datei (Standard: .env)"
    log_info "  -f, --file FILE     Verwendet die angegebene Docker-Compose-Datei (Standard: docker-compose.yml)"
    log_info "  -p, --production    Verwendet die Produktionskonfiguration (docker-compose.production.yml)"
    log_info "  -v, --verbose       Ausführliche Ausgabe"
    log_info "  -h, --help          Zeigt diese Hilfe an"
    echo ""
    log_info "Beispiele:"
    log_info "  $0 start            Startet die Docker-Container"
    log_info "  $0 stop             Stoppt die Docker-Container"
    log_info "  $0 restart          Startet die Docker-Container neu"
    log_info "  $0 status           Zeigt den Status der Docker-Container an"
    log_info "  $0 logs             Zeigt die Logs der Docker-Container an"
    log_info "  $0 setup            Führt das Setup für die Docker-Container aus"
    log_info "  $0 start -p         Startet die Docker-Container mit der Produktionskonfiguration"
    log_info "  $0 start -e .env.local  Startet die Docker-Container mit der angegebenen .env-Datei"
}

# Funktion zum Starten der Docker-Container
start_containers() {
    log_info "Starte Docker-Container..."
    
    # Prüfe, ob die .env-Datei existiert
    if [ ! -f "$ENV_FILE" ]; then
        log_warn ".env-Datei nicht gefunden: $ENV_FILE"
        log_info "Erstelle .env-Datei aus Vorlage..."
        
        if [ -f ".env.example" ]; then
            cp ".env.example" "$ENV_FILE"
            log_info ".env-Datei aus .env.example erstellt."
        else
            log_error "Keine .env.example-Datei gefunden. Bitte erstellen Sie eine .env-Datei manuell."
            exit 1
        fi
    fi
    
    # Prüfe, ob die Docker-Compose-Datei existiert
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_warn "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
        
        if [ "$PRODUCTION" = true ]; then
            log_info "Verwende Produktionskonfiguration..."
            COMPOSE_FILE="docker-compose.production.yml"
        else
            log_info "Kopiere docker-compose.yml aus docker/compose/mcp-servers/docker-compose.yml..."
            cp "docker/compose/mcp-servers/docker-compose.yml" "$COMPOSE_FILE"
        fi
        
        if [ ! -f "$COMPOSE_FILE" ]; then
            log_error "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
            exit 1
        fi
    fi
    
    # Starte die Docker-Container
    if [ "$VERBOSE" = true ]; then
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --verbose
    else
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    fi
    
    log_info "Docker-Container erfolgreich gestartet."
    log_info "Verwenden Sie '$0 status' um den Status der Container anzuzeigen."
    log_info "Verwenden Sie '$0 logs' um die Logs der Container anzuzeigen."
}

# Funktion zum Stoppen der Docker-Container
stop_containers() {
    log_info "Stoppe Docker-Container..."
    
    # Prüfe, ob die Docker-Compose-Datei existiert
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_warn "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
        
        if [ "$PRODUCTION" = true ]; then
            log_info "Verwende Produktionskonfiguration..."
            COMPOSE_FILE="docker-compose.production.yml"
        fi
        
        if [ ! -f "$COMPOSE_FILE" ]; then
            log_error "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
            exit 1
        fi
    fi
    
    # Stoppe die Docker-Container
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    log_info "Docker-Container erfolgreich gestoppt."
}

# Funktion zum Anzeigen des Status der Docker-Container
show_status() {
    log_info "Status der Docker-Container:"
    
    # Prüfe, ob die Docker-Compose-Datei existiert
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_warn "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
        
        if [ "$PRODUCTION" = true ]; then
            log_info "Verwende Produktionskonfiguration..."
            COMPOSE_FILE="docker-compose.production.yml"
        fi
        
        if [ ! -f "$COMPOSE_FILE" ]; then
            log_error "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
            exit 1
        fi
    fi
    
    # Zeige den Status der Docker-Container an
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
}

# Funktion zum Anzeigen der Logs der Docker-Container
show_logs() {
    log_info "Logs der Docker-Container:"
    
    # Prüfe, ob die Docker-Compose-Datei existiert
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_warn "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
        
        if [ "$PRODUCTION" = true ]; then
            log_info "Verwende Produktionskonfiguration..."
            COMPOSE_FILE="docker-compose.production.yml"
        fi
        
        if [ ! -f "$COMPOSE_FILE" ]; then
            log_error "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
            exit 1
        fi
    fi
    
    # Zeige die Logs der Docker-Container an
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs
}

# Funktion zum Ausführen des Setups für die Docker-Container
setup_containers() {
    log_info "Führe Setup für Docker-Container aus..."
    
    # Prüfe, ob die .env-Datei existiert
    if [ ! -f "$ENV_FILE" ]; then
        log_warn ".env-Datei nicht gefunden: $ENV_FILE"
        log_info "Erstelle .env-Datei aus Vorlage..."
        
        if [ -f ".env.example" ]; then
            cp ".env.example" "$ENV_FILE"
            log_info ".env-Datei aus .env.example erstellt."
        else
            log_error "Keine .env.example-Datei gefunden. Bitte erstellen Sie eine .env-Datei manuell."
            exit 1
        fi
    fi
    
    # Prüfe, ob die Docker-Compose-Datei existiert
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_warn "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
        
        if [ "$PRODUCTION" = true ]; then
            log_info "Verwende Produktionskonfiguration..."
            COMPOSE_FILE="docker-compose.production.yml"
        else
            log_info "Kopiere docker-compose.yml aus docker/compose/mcp-servers/docker-compose.yml..."
            cp "docker/compose/mcp-servers/docker-compose.yml" "$COMPOSE_FILE"
        fi
        
        if [ ! -f "$COMPOSE_FILE" ]; then
            log_error "Docker-Compose-Datei nicht gefunden: $COMPOSE_FILE"
            exit 1
        fi
    fi
    
    # Führe das Setup für die Docker-Container aus
    if [ -f "docker-mcp-servers/setup.sh" ]; then
        log_info "Führe docker-mcp-servers/setup.sh aus..."
        bash "docker-mcp-servers/setup.sh"
    else
        log_warn "Keine setup.sh-Datei gefunden. Überspringe Setup."
    fi
    
    log_info "Setup für Docker-Container abgeschlossen."
}

# Parse Kommandozeilenargumente
while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|status|logs|setup|help)
            ACTION="$1"
            shift
            ;;
        -e|--env)
            ENV_FILE="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -p|--production)
            PRODUCTION=true
            COMPOSE_FILE="docker-compose.production.yml"
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unbekannte Option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Führe die entsprechende Aktion aus
case $ACTION in
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
        show_logs
        ;;
    setup)
        setup_containers
        ;;
    help|*)
        show_help
        ;;
esac

exit 0