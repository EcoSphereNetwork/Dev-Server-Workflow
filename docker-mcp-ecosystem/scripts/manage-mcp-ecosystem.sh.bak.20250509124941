#!/bin/bash

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
    echo -e "${BLUE}MCP-Server-Ökosystem-Verwaltungsskript${NC}"
    echo ""
    echo "Verwendung: $0 [Optionen]"
    echo ""
    echo "Aktionen:"
    echo "  start                 Startet das gesamte Ökosystem oder einen bestimmten Dienst"
    echo "  stop                  Stoppt das gesamte Ökosystem oder einen bestimmten Dienst"
    echo "  restart               Startet das gesamte Ökosystem oder einen bestimmten Dienst neu"
    echo "  status                Zeigt den Status des gesamten Ökosystems oder eines bestimmten Dienstes an"
    echo "  logs                  Zeigt die Logs des gesamten Ökosystems oder eines bestimmten Dienstes an"
    echo "  list                  Listet alle verfügbaren Dienste auf"
    echo "  inspect               Zeigt detaillierte Informationen zu einem bestimmten Dienst an"
    echo "  exec                  Führt einen Befehl in einem bestimmten Dienst aus"
    echo "  update                Aktualisiert das gesamte Ökosystem oder einen bestimmten Dienst"
    echo "  backup                Erstellt ein Backup des gesamten Ökosystems oder eines bestimmten Dienstes"
    echo "  restore               Stellt ein Backup des gesamten Ökosystems oder eines bestimmten Dienstes wieder her"
    echo "  help                  Zeigt diese Hilfe an"
    echo ""
    echo "Optionen:"
    echo "  --service SERVICE     Der Dienst, auf den die Aktion angewendet werden soll"
    echo "  --lines LINES         Anzahl der anzuzeigenden Log-Zeilen (Standard: 100)"
    echo "  --command COMMAND     Der Befehl, der in einem Dienst ausgeführt werden soll"
    echo "  --backup-file FILE    Die Backup-Datei für Restore-Operationen"
    echo ""
    echo "Beispiele:"
    echo "  $0 start                          # Startet das gesamte Ökosystem"
    echo "  $0 start --service openhands      # Startet nur den OpenHands-Dienst"
    echo "  $0 logs --service github-mcp      # Zeigt die Logs des GitHub MCP-Servers an"
    echo "  $0 exec --service desktop-commander-mcp --command 'ls -la /workspace'  # Führt einen Befehl aus"
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
            echo -e "${RED}Unbekannte Option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfen, ob eine Aktion angegeben wurde
if [ -z "$ACTION" ]; then
    echo -e "${RED}Fehler: Keine Aktion angegeben.${NC}"
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
            echo -e "${GREEN}Starte das gesamte MCP-Server-Ökosystem...${NC}"
            docker compose up -d
        else
            echo -e "${GREEN}Starte den Dienst $SERVICE...${NC}"
            docker compose up -d $SERVICE
        fi
        ;;
    stop)
        if [ -z "$SERVICE" ]; then
            echo -e "${YELLOW}Stoppe das gesamte MCP-Server-Ökosystem...${NC}"
            docker compose down
        else
            echo -e "${YELLOW}Stoppe den Dienst $SERVICE...${NC}"
            docker compose stop $SERVICE
        fi
        ;;
    restart)
        if [ -z "$SERVICE" ]; then
            echo -e "${GREEN}Starte das gesamte MCP-Server-Ökosystem neu...${NC}"
            docker compose restart
        else
            echo -e "${GREEN}Starte den Dienst $SERVICE neu...${NC}"
            docker compose restart $SERVICE
        fi
        ;;
    status)
        if [ -z "$SERVICE" ]; then
            echo -e "${BLUE}Status des gesamten MCP-Server-Ökosystems:${NC}"
            docker compose ps
        else
            echo -e "${BLUE}Status des Dienstes $SERVICE:${NC}"
            docker compose ps $SERVICE
        fi
        ;;
    logs)
        if [ -z "$SERVICE" ]; then
            echo -e "${BLUE}Logs des gesamten MCP-Server-Ökosystems (letzte $LOG_LINES Zeilen):${NC}"
            docker compose logs --tail=$LOG_LINES
        else
            echo -e "${BLUE}Logs des Dienstes $SERVICE (letzte $LOG_LINES Zeilen):${NC}"
            docker compose logs --tail=$LOG_LINES $SERVICE
        fi
        ;;
    list)
        echo -e "${BLUE}Verfügbare Dienste im MCP-Server-Ökosystem:${NC}"
        docker compose config --services
        ;;
    inspect)
        if [ -z "$SERVICE" ]; then
            echo -e "${RED}Fehler: Kein Dienst für die Inspektion angegeben.${NC}"
            exit 1
        else
            echo -e "${BLUE}Detaillierte Informationen zum Dienst $SERVICE:${NC}"
            docker compose exec $SERVICE env
            echo -e "\n${BLUE}Container-Informationen:${NC}"
            docker inspect mcp-$SERVICE
        fi
        ;;
    exec)
        if [ -z "$SERVICE" ]; then
            echo -e "${RED}Fehler: Kein Dienst für die Befehlsausführung angegeben.${NC}"
            exit 1
        elif [ -z "$COMMAND" ]; then
            echo -e "${RED}Fehler: Kein Befehl für die Ausführung angegeben.${NC}"
            exit 1
        else
            echo -e "${BLUE}Führe Befehl '$COMMAND' im Dienst $SERVICE aus:${NC}"
            docker compose exec $SERVICE sh -c "$COMMAND"
        fi
        ;;
    update)
        if [ -z "$SERVICE" ]; then
            echo -e "${GREEN}Aktualisiere das gesamte MCP-Server-Ökosystem...${NC}"
            docker compose pull
            docker compose up -d
        else
            echo -e "${GREEN}Aktualisiere den Dienst $SERVICE...${NC}"
            docker compose pull $SERVICE
            docker compose up -d $SERVICE
        fi
        ;;
    backup)
        TIMESTAMP=$(date +%Y%m%d%H%M%S)
        if [ -z "$SERVICE" ]; then
            BACKUP_DIR="backups/full_backup_$TIMESTAMP"
            echo -e "${GREEN}Erstelle Backup des gesamten MCP-Server-Ökosystems in $BACKUP_DIR...${NC}"
            mkdir -p $BACKUP_DIR
            docker compose down
            tar -czf $BACKUP_DIR/volumes.tar.gz -C /var/lib/docker/volumes .
            cp -r * $BACKUP_DIR/
            docker compose up -d
        else
            BACKUP_DIR="backups/${SERVICE}_backup_$TIMESTAMP"
            echo -e "${GREEN}Erstelle Backup des Dienstes $SERVICE in $BACKUP_DIR...${NC}"
            mkdir -p $BACKUP_DIR
            docker compose stop $SERVICE
            VOLUME_NAME=$(docker inspect mcp-$SERVICE | grep -o '"Source": "/var/lib/docker/volumes/[^"]*' | sed 's/"Source": "//')
            if [ -n "$VOLUME_NAME" ]; then
                tar -czf $BACKUP_DIR/volume.tar.gz -C $VOLUME_NAME .
            fi
            cp -r $SERVICE $BACKUP_DIR/
            docker compose start $SERVICE
        fi
        echo -e "${GREEN}Backup abgeschlossen.${NC}"
        ;;
    restore)
        if [ -z "$BACKUP_FILE" ]; then
            echo -e "${RED}Fehler: Keine Backup-Datei für die Wiederherstellung angegeben.${NC}"
            exit 1
        elif [ ! -f "$BACKUP_FILE" ]; then
            echo -e "${RED}Fehler: Backup-Datei $BACKUP_FILE existiert nicht.${NC}"
            exit 1
        else
            if [ -z "$SERVICE" ]; then
                echo -e "${GREEN}Stelle das gesamte MCP-Server-Ökosystem aus $BACKUP_FILE wieder her...${NC}"
                docker compose down
                tar -xzf $BACKUP_FILE -C /var/lib/docker/volumes
                docker compose up -d
            else
                echo -e "${GREEN}Stelle den Dienst $SERVICE aus $BACKUP_FILE wieder her...${NC}"
                docker compose stop $SERVICE
                VOLUME_NAME=$(docker inspect mcp-$SERVICE | grep -o '"Source": "/var/lib/docker/volumes/[^"]*' | sed 's/"Source": "//')
                if [ -n "$VOLUME_NAME" ]; then
                    tar -xzf $BACKUP_FILE -C $VOLUME_NAME
                fi
                docker compose start $SERVICE
            fi
            echo -e "${GREEN}Wiederherstellung abgeschlossen.${NC}"
        fi
        ;;
    *)
        echo -e "${RED}Unbekannte Aktion: $ACTION${NC}"
        show_help
        exit 1
        ;;
esac