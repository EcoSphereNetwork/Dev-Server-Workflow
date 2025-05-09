#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# MCP-Server-Ökosystem-Verwaltungsskript
# Dieses Skript ermöglicht die Verwaltung des MCP-Server-Ökosystems.

# Standardwerte
ACTION=""
SERVICE=""
LOG_LINES=100

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hilfe-Funktion
function show_help {
    log_info "${BLUE}MCP-Server-Ökosystem-Verwaltungsskript${NC}"
    echo ""
    log_info "Verwendung: $0 [Optionen]"
    echo ""
    log_info "Aktionen:"
    log_info "  start                 Startet das gesamte Ökosystem oder einen bestimmten Dienst"
    log_info "  stop                  Stoppt das gesamte Ökosystem oder einen bestimmten Dienst"
    log_info "  restart               Startet das gesamte Ökosystem oder einen bestimmten Dienst neu"
    log_info "  status                Zeigt den Status des gesamten Ökosystems oder eines bestimmten Dienstes an"
    log_info "  logs                  Zeigt die Logs des gesamten Ökosystems oder eines bestimmten Dienstes an"
    log_info "  list                  Listet alle verfügbaren Dienste auf"
    log_info "  inspect               Zeigt detaillierte Informationen zu einem bestimmten Dienst an"
    log_info "  exec                  Führt einen Befehl in einem bestimmten Dienst aus"
    log_info "  update                Aktualisiert das gesamte Ökosystem oder einen bestimmten Dienst"
    log_info "  backup                Erstellt ein Backup des gesamten Ökosystems oder eines bestimmten Dienstes"
    log_info "  restore               Stellt ein Backup des gesamten Ökosystems oder eines bestimmten Dienstes wieder her"
    log_info "  help                  Zeigt diese Hilfe an"
    echo ""
    log_info "Optionen:"
    log_info "  --service SERVICE     Der Dienst, auf den die Aktion angewendet werden soll"
    log_info "  --lines LINES         Anzahl der anzuzeigenden Log-Zeilen (Standard: 100)"
    log_info "  --command COMMAND     Der Befehl, der in einem Dienst ausgeführt werden soll"
    log_info "  --backup-file FILE    Die Backup-Datei für Restore-Operationen"
    echo ""
    log_info "Beispiele:"
    log_info "  $0 start                          # Startet das gesamte Ökosystem"
    log_info "  $0 start --service openhands      # Startet nur den OpenHands-Dienst"
    log_info "  $0 logs --service github-mcp      # Zeigt die Logs des GitHub MCP-Servers an"
    log_info "  $0 exec --service desktop-commander-mcp --command 'ls -la /workspace'  # Führt einen Befehl aus"
    echo ""
}

# Parameter verarbeiten
while [[ $# -gt 0 ]]; do
    case "$1" in
        start|stop|restart|status|logs|list|inspect|exec|update|backup|restore|help)
            ACTION="$1"
            shift
            ;;
        --service)
            SERVICE="$2"
            shift 2
            ;;
        --lines)
            LOG_LINES="$2"
            shift 2
            ;;
        --command)
            COMMAND="$2"
            shift 2
            ;;
        --backup-file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        *)
            log_info "${RED}Unbekannte Option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfen, ob eine Aktion angegeben wurde
if [ -z "$ACTION" ]; then
    log_info "${RED}Fehler: Keine Aktion angegeben.${NC}"
    show_help
    exit 1
fi

# Hilfe anzeigen
if [ "$ACTION" == "help" ]; then
    show_help
    exit 0
fi

# Verzeichnis zum Docker-Compose-Projekt wechseln
cd /workspace/Dev-Server-Workflow/docker-mcp-ecosystem-improved

# Aktionen ausführen
case "$ACTION" in
    start)
        if [ -z "$SERVICE" ]; then
            log_info "${GREEN}Starte das gesamte MCP-Server-Ökosystem...${NC}"
            docker compose up -d
        else
            log_info "${GREEN}Starte den Dienst $SERVICE...${NC}"
            docker compose up -d $SERVICE
        fi
        ;;
    stop)
        if [ -z "$SERVICE" ]; then
            log_info "${YELLOW}Stoppe das gesamte MCP-Server-Ökosystem...${NC}"
            docker compose down
        else
            log_info "${YELLOW}Stoppe den Dienst $SERVICE...${NC}"
            docker compose stop $SERVICE
        fi
        ;;
    restart)
        if [ -z "$SERVICE" ]; then
            log_info "${GREEN}Starte das gesamte MCP-Server-Ökosystem neu...${NC}"
            docker compose restart
        else
            log_info "${GREEN}Starte den Dienst $SERVICE neu...${NC}"
            docker compose restart $SERVICE
        fi
        ;;
    status)
        if [ -z "$SERVICE" ]; then
            log_info "${BLUE}Status des gesamten MCP-Server-Ökosystems:${NC}"
            docker compose ps
        else
            log_info "${BLUE}Status des Dienstes $SERVICE:${NC}"
            docker compose ps $SERVICE
        fi
        ;;
    logs)
        if [ -z "$SERVICE" ]; then
            log_info "${BLUE}Logs des gesamten MCP-Server-Ökosystems (letzte $LOG_LINES Zeilen):${NC}"
            docker compose logs --tail=$LOG_LINES
        else
            log_info "${BLUE}Logs des Dienstes $SERVICE (letzte $LOG_LINES Zeilen):${NC}"
            docker compose logs --tail=$LOG_LINES $SERVICE
        fi
        ;;
    list)
        log_info "${BLUE}Verfügbare Dienste im MCP-Server-Ökosystem:${NC}"
        docker compose config --services
        ;;
    inspect)
        if [ -z "$SERVICE" ]; then
            log_info "${RED}Fehler: Kein Dienst für die Inspektion angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Detaillierte Informationen zum Dienst $SERVICE:${NC}"
            docker compose exec $SERVICE env
            log_info "\n${BLUE}Container-Informationen:${NC}"
            docker inspect mcp-$SERVICE
        fi
        ;;
    exec)
        if [ -z "$SERVICE" ]; then
            log_info "${RED}Fehler: Kein Dienst für die Befehlsausführung angegeben.${NC}"
            exit 1
        elif [ -z "$COMMAND" ]; then
            log_info "${RED}Fehler: Kein Befehl für die Ausführung angegeben.${NC}"
            exit 1
        else
            log_info "${BLUE}Führe Befehl '$COMMAND' im Dienst $SERVICE aus:${NC}"
            docker compose exec $SERVICE sh -c "$COMMAND"
        fi
        ;;
    update)
        if [ -z "$SERVICE" ]; then
            log_info "${GREEN}Aktualisiere das gesamte MCP-Server-Ökosystem...${NC}"
            docker compose pull
            docker compose up -d
        else
            log_info "${GREEN}Aktualisiere den Dienst $SERVICE...${NC}"
            docker compose pull $SERVICE
            docker compose up -d $SERVICE
        fi
        ;;
    backup)
        TIMESTAMP=$(date +%Y%m%d%H%M%S)
        if [ -z "$SERVICE" ]; then
            BACKUP_DIR="backups/full_backup_$TIMESTAMP"
            log_info "${GREEN}Erstelle Backup des gesamten MCP-Server-Ökosystems in $BACKUP_DIR...${NC}"
            mkdir -p $BACKUP_DIR
            docker compose down
            tar -czf $BACKUP_DIR/volumes.tar.gz -C /var/lib/docker/volumes .
            cp -r * $BACKUP_DIR/
            docker compose up -d
        else
            BACKUP_DIR="backups/${SERVICE}_backup_$TIMESTAMP"
            log_info "${GREEN}Erstelle Backup des Dienstes $SERVICE in $BACKUP_DIR...${NC}"
            mkdir -p $BACKUP_DIR
            docker compose stop $SERVICE
            VOLUME_NAME=$(docker inspect mcp-$SERVICE | grep -o '"Source": "/var/lib/docker/volumes/[^"]*' | sed 's/"Source": "//')
            if [ -n "$VOLUME_NAME" ]; then
                tar -czf $BACKUP_DIR/volume.tar.gz -C $VOLUME_NAME .
            fi
            cp -r $SERVICE $BACKUP_DIR/
            docker compose start $SERVICE
        fi
        log_info "${GREEN}Backup abgeschlossen.${NC}"
        ;;
    restore)
        if [ -z "$BACKUP_FILE" ]; then
            log_info "${RED}Fehler: Keine Backup-Datei für die Wiederherstellung angegeben.${NC}"
            exit 1
        elif [ ! -f "$BACKUP_FILE" ]; then
            log_info "${RED}Fehler: Backup-Datei $BACKUP_FILE existiert nicht.${NC}"
            exit 1
        else
            if [ -z "$SERVICE" ]; then
                log_info "${GREEN}Stelle das gesamte MCP-Server-Ökosystem aus $BACKUP_FILE wieder her...${NC}"
                docker compose down
                tar -xzf $BACKUP_FILE -C /var/lib/docker/volumes
                docker compose up -d
            else
                log_info "${GREEN}Stelle den Dienst $SERVICE aus $BACKUP_FILE wieder her...${NC}"
                docker compose stop $SERVICE
                VOLUME_NAME=$(docker inspect mcp-$SERVICE | grep -o '"Source": "/var/lib/docker/volumes/[^"]*' | sed 's/"Source": "//')
                if [ -n "$VOLUME_NAME" ]; then
                    tar -xzf $BACKUP_FILE -C $VOLUME_NAME
                fi
                docker compose start $SERVICE
            fi
            log_info "${GREEN}Wiederherstellung abgeschlossen.${NC}"
        fi
        ;;
    *)
        log_info "${RED}Unbekannte Aktion: $ACTION${NC}"
        show_help
        exit 1
        ;;
esac