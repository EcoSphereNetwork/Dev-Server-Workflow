#!/bin/bash
# Dev-Server CLI
# This script provides a command-line interface for managing the Dev-Server-Workflow

# Strikte Fehlerbehandlung aktivieren
set -euo pipefail

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Fehlerbehandlung einbinden
if [[ -f "${BASE_DIR}/cli/error_handler.sh" ]]; then
    source "${BASE_DIR}/cli/error_handler.sh"
fi

# Konfigurationsmanager einbinden
if [[ -f "${BASE_DIR}/cli/config_manager.sh" ]]; then
    source "${BASE_DIR}/cli/config_manager.sh"
    # Alle Konfigurationen laden
    if [[ "$(type -t load_all_configs)" == "function" ]]; then
        load_all_configs
    fi
fi

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Aktuelle Operation für Fehlerbehandlung
CURRENT_OPERATION="dev_server_cli"

# Fehlerbehandlung einrichten
if [[ "$(type -t handle_error)" == "function" ]]; then
    trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR
fi

# Funktion zum Anzeigen von Hilfe
show_help() {
    echo -e "${BLUE}Dev-Server CLI${NC}"
    echo "Dieses Skript bietet eine Befehlszeilenschnittstelle für die Verwaltung des Dev-Server-Workflows."
    echo ""
    echo "Verwendung:"
    echo "  $0 [Optionen] [Befehl]"
    echo ""
    echo "Optionen:"
    echo "  -h, --help                Zeigt diese Hilfe an"
    echo "  -v, --verbose             Aktiviert ausführliche Ausgabe"
    echo ""
    echo "Befehle:"
    echo "  ui                        Startet die interaktive Benutzeroberfläche"
    echo "  status                    Zeigt den Status aller Komponenten an"
    echo "  start <komponente>        Startet eine Komponente und ihre Abhängigkeiten"
    echo "  stop <komponente>         Stoppt eine Komponente und ihre Abhängigkeiten"
    echo "  restart <komponente>      Startet eine Komponente neu"
    echo "  logs <komponente>         Zeigt die Logs einer Komponente an"
    echo "  config                    Verwaltet die Konfiguration"
    echo "  backup                    Erstellt ein Backup"
    echo "  restore <backup>          Stellt ein Backup wieder her"
    echo "  monitor                   Überwacht die Systemressourcen"
    echo "  help                      Zeigt diese Hilfe an"
    echo ""
    echo "Beispiele:"
    echo "  $0 ui                     Startet die interaktive Benutzeroberfläche"
    echo "  $0 status                 Zeigt den Status aller Komponenten an"
    echo "  $0 start n8n              Startet n8n und seine Abhängigkeiten"
    echo "  $0 stop web-ui            Stoppt die Web-UI und ihre Abhängigkeiten"
    echo "  $0 logs n8n               Zeigt die Logs von n8n an"
}

# Standardwerte
VERBOSE=false

# Parse Kommandozeilenargumente
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

# Wenn kein Befehl angegeben wurde, zeige Hilfe an
if [[ $# -eq 0 ]]; then
    show_help
    exit 0
fi

# Befehl auslesen
COMMAND="$1"
shift

# Befehl ausführen
case "$COMMAND" in
    ui)
        # Starte interaktive Benutzeroberfläche
        if [[ -f "${BASE_DIR}/cli/interactive_ui.sh" ]]; then
            "${BASE_DIR}/cli/interactive_ui.sh"
        else
            echo -e "${RED}Interaktive Benutzeroberfläche nicht gefunden${NC}"
            exit 1
        fi
        ;;
    status)
        # Zeige Status aller Komponenten an
        if [[ -f "${BASE_DIR}/src/common/dependency_manager.sh" ]]; then
            "${BASE_DIR}/src/common/dependency_manager.sh" list
        else
            echo -e "${RED}Dependency Manager nicht gefunden${NC}"
            exit 1
        fi
        ;;
    start)
        # Starte eine Komponente
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Keine Komponente angegeben${NC}"
            echo "Verwendung: $0 start <komponente>"
            exit 1
        fi
        
        if [[ -f "${BASE_DIR}/src/common/dependency_manager.sh" ]]; then
            "${BASE_DIR}/src/common/dependency_manager.sh" start "$1"
        else
            echo -e "${RED}Dependency Manager nicht gefunden${NC}"
            exit 1
        fi
        ;;
    stop)
        # Stoppe eine Komponente
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Keine Komponente angegeben${NC}"
            echo "Verwendung: $0 stop <komponente>"
            exit 1
        fi
        
        if [[ -f "${BASE_DIR}/src/common/dependency_manager.sh" ]]; then
            "${BASE_DIR}/src/common/dependency_manager.sh" stop "$1"
        else
            echo -e "${RED}Dependency Manager nicht gefunden${NC}"
            exit 1
        fi
        ;;
    restart)
        # Starte eine Komponente neu
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Keine Komponente angegeben${NC}"
            echo "Verwendung: $0 restart <komponente>"
            exit 1
        fi
        
        if [[ -f "${BASE_DIR}/src/common/dependency_manager.sh" ]]; then
            "${BASE_DIR}/src/common/dependency_manager.sh" restart "$1"
        else
            echo -e "${RED}Dependency Manager nicht gefunden${NC}"
            exit 1
        fi
        ;;
    logs)
        # Zeige Logs einer Komponente an
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Keine Komponente angegeben${NC}"
            echo "Verwendung: $0 logs <komponente>"
            exit 1
        fi
        
        # Prüfe, ob die Komponente ein Docker-Container ist
        if docker ps --format "{{.Names}}" | grep -q "$1"; then
            docker logs "$1"
        else
            echo -e "${RED}Komponente $1 ist kein laufender Docker-Container${NC}"
            exit 1
        fi
        ;;
    config)
        # Verwalte Konfiguration
        if [[ -f "${BASE_DIR}/cli/config_manager.sh" ]]; then
            if [[ $# -eq 0 ]]; then
                # Zeige alle Konfigurationen an
                "${BASE_DIR}/cli/config_manager.sh" list "env" "${BASE_DIR}/.env"
            else
                # Führe Konfigurationsbefehl aus
                "${BASE_DIR}/cli/config_manager.sh" "$@"
            fi
        else
            echo -e "${RED}Konfigurationsmanager nicht gefunden${NC}"
            exit 1
        fi
        ;;
    backup)
        # Erstelle Backup
        BACKUP_DIR="${BASE_DIR}/backups"
        mkdir -p "$BACKUP_DIR"
        
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
        BACKUP_FILE="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
        
        echo -e "${BLUE}Erstelle Backup $BACKUP_NAME...${NC}"
        
        # Erstelle temporäres Verzeichnis
        TMP_DIR="${BACKUP_DIR}/tmp"
        mkdir -p "$TMP_DIR"
        
        # Kopiere Konfigurationsdateien
        cp "${BASE_DIR}/.env" "$TMP_DIR/" 2>/dev/null || true
        cp -r "${BASE_DIR}/config" "$TMP_DIR/" 2>/dev/null || true
        
        # Erstelle Backup-Info-Datei
        echo "Backup erstellt am: $(date)" > "$TMP_DIR/backup_info.txt"
        echo "Hostname: $(hostname)" >> "$TMP_DIR/backup_info.txt"
        echo "Benutzer: $(whoami)" >> "$TMP_DIR/backup_info.txt"
        echo "Docker-Version: $(docker --version)" >> "$TMP_DIR/backup_info.txt"
        echo "Laufende Container:" >> "$TMP_DIR/backup_info.txt"
        docker ps --format "{{.Names}}" >> "$TMP_DIR/backup_info.txt"
        
        # Erstelle Archiv
        tar -czf "$BACKUP_FILE" -C "$BACKUP_DIR/tmp" .
        
        # Lösche temporäres Verzeichnis
        rm -rf "$TMP_DIR"
        
        echo -e "${GREEN}Backup erstellt: $BACKUP_FILE${NC}"
        ;;
    restore)
        # Stelle Backup wieder her
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Kein Backup angegeben${NC}"
            echo "Verwendung: $0 restore <backup>"
            exit 1
        fi
        
        BACKUP_FILE="$1"
        
        # Prüfe, ob Backup existiert
        if [[ ! -f "$BACKUP_FILE" ]]; then
            # Versuche, Backup im Backup-Verzeichnis zu finden
            BACKUP_DIR="${BASE_DIR}/backups"
            if [[ -f "${BACKUP_DIR}/$BACKUP_FILE" ]]; then
                BACKUP_FILE="${BACKUP_DIR}/$BACKUP_FILE"
            elif [[ -f "${BACKUP_DIR}/${BACKUP_FILE}.tar.gz" ]]; then
                BACKUP_FILE="${BACKUP_DIR}/${BACKUP_FILE}.tar.gz"
            else
                echo -e "${RED}Backup $BACKUP_FILE nicht gefunden${NC}"
                exit 1
            fi
        fi
        
        echo -e "${BLUE}Stelle Backup $BACKUP_FILE wieder her...${NC}"
        
        # Erstelle temporäres Verzeichnis
        TMP_DIR="${BASE_DIR}/backups/tmp"
        mkdir -p "$TMP_DIR"
        
        # Extrahiere Backup
        tar -xzf "$BACKUP_FILE" -C "$TMP_DIR"
        
        # Stoppe alle Container
        echo -e "${BLUE}Stoppe alle Container...${NC}"
        if [[ -f "${BASE_DIR}/src/common/dependency_manager.sh" ]]; then
            "${BASE_DIR}/src/common/dependency_manager.sh" stop-all
        else
            docker compose -f "${BASE_DIR}/docker-compose.yml" down
        fi
        
        # Kopiere Konfigurationsdateien
        cp "$TMP_DIR/.env" "${BASE_DIR}/" 2>/dev/null || true
        cp -r "$TMP_DIR/config/"* "${BASE_DIR}/config/" 2>/dev/null || true
        
        # Lösche temporäres Verzeichnis
        rm -rf "$TMP_DIR"
        
        echo -e "${GREEN}Backup wiederhergestellt${NC}"
        echo -e "${YELLOW}Starten Sie die Container neu, um die Änderungen zu übernehmen${NC}"
        ;;
    monitor)
        # Überwache Systemressourcen
        echo -e "${BLUE}Überwache Systemressourcen...${NC}"
        echo -e "${BLUE}Drücken Sie Strg+C, um zu beenden${NC}"
        echo ""
        
        # Prüfe, ob htop installiert ist
        if command -v htop &> /dev/null; then
            htop
        else
            # Fallback auf top
            top
        fi
        ;;
    help)
        # Zeige Hilfe an
        show_help
        ;;
    *)
        # Unbekannter Befehl
        echo -e "${RED}Unbekannter Befehl: $COMMAND${NC}"
        show_help
        exit 1
        ;;
esac

exit 0