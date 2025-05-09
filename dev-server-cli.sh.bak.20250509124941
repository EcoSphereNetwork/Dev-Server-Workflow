#!/bin/bash
# Dev-Server CLI mit verbesserter Paket- und Versionsverwaltung
# Dieses Skript bietet eine Befehlszeilenschnittstelle für die Verwaltung des Dev-Server-Workflows

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

# Funktion zum Einrichten eines Alias für docker-compose
setup_docker_compose_alias() {
    # Prüfen, ob docker compose Befehl verfügbar ist
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        echo -e "${GREEN}Docker Compose Plugin ist installiert.${NC}"
        
        # Prüfen, ob docker-compose Befehl verfügbar ist
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${BLUE}Richte Alias für docker-compose ein...${NC}"
            
            # Prüfen, welche Shell verwendet wird
            local shell_rc
            if [ -n "$ZSH_VERSION" ]; then
                shell_rc="$HOME/.zshrc"
            elif [ -n "$BASH_VERSION" ]; then
                shell_rc="$HOME/.bashrc"
            else
                # Standardmäßig .bashrc verwenden
                shell_rc="$HOME/.bashrc"
            fi
            
            # Prüfen, ob der Alias bereits existiert
            if ! grep -q "alias docker-compose='docker compose'" "$shell_rc"; then
                echo 'alias docker-compose="docker compose"' >> "$shell_rc"
                echo -e "${GREEN}Alias zu $shell_rc hinzugefügt.${NC}"
                echo -e "${YELLOW}Bitte führen Sie 'source $shell_rc' aus, oder starten Sie ein neues Terminal, um den Alias zu aktivieren.${NC}"
                
                # Temporär für die aktuelle Sitzung einrichten
                alias docker-compose="docker compose"
                echo -e "${GREEN}Alias temporär für die aktuelle Sitzung eingerichtet.${NC}"
            else
                echo -e "${GREEN}Alias existiert bereits in $shell_rc.${NC}"
            fi
        else
            echo -e "${GREEN}docker-compose Befehl ist bereits verfügbar.${NC}"
        fi
    else
        echo -e "${YELLOW}Docker Compose Plugin ist nicht installiert. Kann keinen Alias einrichten.${NC}"
    fi
}

# Funktion zum Überprüfen einer Paketversion
check_version() {
    local package=$1
    local min_version=$2
    local version_cmd=$3
    local version_regex=$4

    if ! command -v "$package" &> /dev/null; then
        return 1
    fi

    local version_output
    version_output=$($version_cmd)
    local current_version
    current_version=$(echo "$version_output" | grep -oE "$version_regex" | head -1)

    if [ -z "$current_version" ]; then
        echo -e "${YELLOW}Konnte die Version von $package nicht ermitteln.${NC}"
        return 2
    }

    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" != "$min_version" ]; then
        echo -e "${GREEN}$package Version $current_version gefunden (Minimum: $min_version).${NC}"
        return 0
    else
        echo -e "${YELLOW}$package Version $current_version ist älter als die benötigte Version $min_version.${NC}"
        return 3
    fi
}

# Funktion zum Überprüfen und Installieren von Abhängigkeiten
check_dependencies() {
    echo -e "${BLUE}Überprüfe Abhängigkeiten...${NC}"
    
    # Prüfe Docker-Installation
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
        echo -e "${YELLOW}Installationsanweisungen: https://docs.docker.com/get-docker/${NC}"
        return 1
    fi
    
    # Prüfe Docker-Version
    check_version "docker" "20.10.0" "docker --version" "([0-9]+\.[0-9]+\.[0-9]+)"
    if [ $? -eq 3 ]; then
        echo -e "${YELLOW}Docker Version ist veraltet. Ein Update wird empfohlen.${NC}"
    fi
    
    # Prüfe Docker Compose Installation
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        echo -e "${GREEN}Docker Compose Plugin ist installiert.${NC}"
        
        # Richte den docker-compose Alias ein
        setup_docker_compose_alias
        
    elif command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}Eigenständiges Docker Compose ist installiert.${NC}"
        
        # Prüfe Version
        check_version "docker-compose" "1.29.0" "docker-compose --version" "([0-9]+\.[0-9]+\.[0-9]+)"
        if [ $? -eq 3 ]; then
            echo -e "${YELLOW}Docker Compose ist veraltet. Ein Update wird empfohlen.${NC}"
        fi
    else
        echo -e "${RED}Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose.${NC}"
        echo -e "${YELLOW}Installationsanweisungen: https://docs.docker.com/compose/install/${NC}"
        return 1
    fi
    
    # Prüfe Python-Installation
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 ist nicht installiert. Bitte installieren Sie Python 3.${NC}"
        return 1
    fi
    
    # Prüfe Python-Version
    check_version "python3" "3.6.0" "python3 --version" "([0-9]+\.[0-9]+\.[0-9]+)"
    if [ $? -eq 3 ]; then
        echo -e "${YELLOW}Python-Version ist veraltet. Ein Update wird empfohlen.${NC}"
    fi
    
    # Prüfe pip-Installation
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}pip3 ist nicht installiert. Bitte installieren Sie pip3.${NC}"
        return 1
    fi
    
    # Prüfe vorhandene Python-Pakete
    required_packages=("pyyaml" "requests" "docker")
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &>/dev/null; then
            echo -e "${YELLOW}Python-Paket '$package' ist nicht installiert. Installiere...${NC}"
            pip3 install --user "$package"
        else
            echo -e "${GREEN}Python-Paket '$package' ist installiert.${NC}"
        fi
    done
    
    echo -e "${GREEN}Alle Abhängigkeiten sind installiert.${NC}"
    return 0
}

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
    echo "  --check-deps              Überprüft die erforderlichen Abhängigkeiten"
    echo "  --setup-alias             Richtet einen Alias für docker-compose ein"
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
    echo "Komponenten:"
    echo "  n8n                       Workflow-Automatisierung"
    echo "  web-ui                    Web-Benutzeroberfläche"
    echo "  mcp                       MCP-Server für AI-Integration"
    echo "  all                       Alle Komponenten"
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
        --check-deps)
            check_dependencies
            exit $?
            ;;
        --setup-alias)
            setup_docker_compose_alias
            exit 0
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

# Bestimme Docker Compose Befehl basierend auf dem, was installiert ist
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}Weder Docker Compose Plugin noch eigenständiges Docker Compose sind installiert.${NC}"
    echo -e "${YELLOW}Bitte installieren Sie Docker Compose: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

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
        echo -e "${BLUE}Status der Komponenten:${NC}"
        
        # Prüfe Docker-Container
        echo -e "\n${GREEN}Docker-Container:${NC}"
        $DOCKER_COMPOSE_CMD ps
        
        # Prüfe n8n
        echo -e "\n${GREEN}n8n-Status:${NC}"
        if pgrep -f "n8n" > /dev/null; then
            echo -e "${GREEN}n8n läuft${NC}"
        else
            echo -e "${RED}n8n läuft nicht${NC}"
        fi
        
        # Prüfe MCP-Server
        echo -e "\n${GREEN}MCP-Server-Status:${NC}"
        if [[ -f "${BASE_DIR}/src/common/dependency_manager.sh" ]]; then
            "${BASE_DIR}/src/common/dependency_manager.sh" list
        else
            echo -e "${YELLOW}Dependency Manager nicht gefunden, prüfe Docker-Container...${NC}"
            docker ps --filter "name=mcp"
        fi
        ;;
    start)
        # Starte eine Komponente
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Keine Komponente angegeben${NC}"
            echo "Verwendung: $0 start <komponente>"
            exit 1
        fi
        
        COMPONENT="$1"
        
        case "$COMPONENT" in
            n8n)
                echo -e "${BLUE}Starte n8n...${NC}"
                if command -v n8n &> /dev/null; then
                    n8n start &
                    echo -e "${GREEN}n8n wurde gestartet.${NC}"
                else
                    echo -e "${RED}n8n ist nicht installiert.${NC}"
                    echo -e "${YELLOW}Installieren Sie n8n mit 'npm install -g n8n'${NC}"
                    exit 1
                fi
                ;;
            web-ui)
                echo -e "${BLUE}Starte Web-UI...${NC}"
                if [[ -f "${BASE_DIR}/start-web-ui.sh" ]]; then
                    "${BASE_DIR}/start-web-ui.sh"
                else
                    echo -e "${RED}Web-UI-Startskript nicht gefunden${NC}"
                    exit 1
                fi
                ;;
            mcp)
                echo -e "${BLUE}Starte MCP-Server...${NC}"
                if [[ -f "${BASE_DIR}/scripts/start-mcp-servers.sh" ]]; then
                    "${BASE_DIR}/scripts/start-mcp-servers.sh" --all
                elif [[ -f "${BASE_DIR}/start-mcp-servers.sh" ]]; then
                    "${BASE_DIR}/start-mcp-servers.sh" --all
                else
                    echo -e "${RED}MCP-Server-Startskript nicht gefunden${NC}"
                    exit 1
                fi
                ;;
            all)
                echo -e "${BLUE}Starte alle Komponenten...${NC}"
                
                # Starte n8n
                if command -v n8n &> /dev/null; then
                    echo -e "${BLUE}Starte n8n...${NC}"
                    n8n start &
                    echo -e "${GREEN}n8n wurde gestartet.${NC}"
                else
                    echo -e "${YELLOW}n8n ist nicht installiert, überspringe...${NC}"
                fi
                
                # Starte Web-UI
                if [[ -f "${BASE_DIR}/start-web-ui.sh" ]]; then
                    echo -e "${BLUE}Starte Web-UI...${NC}"
                    "${BASE_DIR}/start-web-ui.sh"
                else
                    echo -e "${YELLOW}Web-UI-Startskript nicht gefunden, überspringe...${NC}"
                fi
                
                # Starte MCP-Server
                if [[ -f "${BASE_DIR}/scripts/start-mcp-servers.sh" ]]; then
                    echo -e "${BLUE}Starte MCP-Server...${NC}"
                    "${BASE_DIR}/scripts/start-mcp-servers.sh" --all
                elif [[ -f "${BASE_DIR}/start-mcp-servers.sh" ]]; then
                    echo -e "${BLUE}Starte MCP-Server...${NC}"
                    "${BASE_DIR}/start-mcp-servers.sh" --all
                else
                    echo -e "${YELLOW}MCP-Server-Startskript nicht gefunden, überspringe...${NC}"
                fi
                
                echo -e "${GREEN}Alle Komponenten wurden gestartet.${NC}"
                ;;
            *)
                if [[ -f "${BASE_DIR}/src/common/dependency_manager.sh" ]]; then
                    "${BASE_DIR}/src/common/dependency_manager.sh" start "$COMPONENT"
                else
                    echo -e "${RED}Unbekannte Komponente: $COMPONENT${NC}"
                    echo "Bekannte Komponenten: n8n, web-ui, mcp, all"
                    exit 1
                fi
                ;;
        esac
        ;;
    stop)
        # Stoppe eine Komponente
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Keine Komponente angegeben${NC}"
            echo "Verwendung: $0 stop <komponente>"
            exit 1
        fi
        
        COMPONENT="$1"
        
        case "$COMPONENT" in
            n8n)
                echo -e "${BLUE}Stoppe n8n...${NC}"
                pkill -f "n8n" || true
                echo -e "${GREEN}n8n wurde gestoppt.${NC}"
                ;;
            web-ui)
                echo -e "${BLUE}Stoppe Web-UI...${NC}"
                if [[ -f "${BASE_DIR}/stop-web-ui.sh" ]]; then
                    "${BASE_DIR}/stop-web-ui.sh"
                else
                    echo -e "${YELLOW}Web-UI-Stoppskript nicht gefunden, verwende Docker Compose...${NC}"
                    $DOCKER_COMPOSE_CMD -f "docker-compose.web-ui.yml" down
                    echo -e "${GREEN}Web-UI wurde gestoppt.${NC}"
                fi
                ;;
            mcp)
                echo -e "${BLUE}Stoppe MCP-Server...${NC}"
                if [[ -f "${BASE_DIR}/scripts/stop-mcp-servers.sh" ]]; then
                    "${BASE_DIR}/scripts/stop-mcp-servers.sh" --all
                elif [[ -f "${BASE_DIR}/stop-mcp-servers.sh" ]]; then
                    "${BASE_DIR}/stop-mcp-servers.sh" --all
                else
                    echo -e "${RED}MCP-Server-Stoppskript nicht gefunden${NC}"
                    exit 1
                fi
                ;;
            all)
                echo -e "${BLUE}Stoppe alle Komponenten...${NC}"
                
                # Stoppe n8n
                echo -e "${BLUE}Stoppe n8n...${NC}"
                pkill -f "n8n" || true
                echo -e "${GREEN}n8n wurde gestoppt.${NC}"
                
                # Stoppe Web-UI
                if [[ -f "${BASE_DIR}/stop-web-ui.sh" ]]; then
                    echo -e "${BLUE}Stoppe Web-UI...${NC}"
                    "${BASE_DIR}/stop-web-ui.sh"
                else
                    echo -e "${YELLOW}Web-UI-Stoppskript nicht gefunden, verwende Docker Compose...${NC}"
                    $DOCKER_COMPOSE_CMD -f "docker-compose.web-ui.yml" down || true
                    echo -e "${GREEN}Web-UI wurde gestoppt.${NC}"
                fi
                
                # Stoppe MCP-Server
                if [[ -f "${BASE_DIR}/scripts/stop-mcp-servers.sh" ]]; then
                    echo -e "${BLUE}Stoppe MCP-Server...${NC}"
                    "${BASE_DIR}/scripts/stop-mcp-servers.sh" --all
                elif [[ -f "${BASE_DIR}/stop-mcp-servers.sh" ]]; then
                    echo -e "${BLUE}Stoppe MCP-Server...${NC}"
                    "${BASE_DIR}/stop-mcp-servers.sh" --all
                else
                    echo -e "${YELLOW}MCP-Server-Stoppskript nicht gefunden, überspringe...${NC}"
                fi
                
                echo -e "${GREEN}Alle Komponenten wurden gestoppt.${NC}"
                ;;
            *)
                if [[ -f "${BASE_DIR}/src/common/dependency_manager.sh" ]]; then
                    "${BASE_DIR}/src/common/dependency_manager.sh" stop "$COMPONENT"
                else
                    echo -e "${RED}Unbekannte Komponente: $COMPONENT${NC}"
                    echo "Bekannte Komponenten: n8n, web-ui, mcp, all"
                    exit 1
                fi
                ;;
        esac
        ;;
    restart)
        # Starte eine Komponente neu
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Keine Komponente angegeben${NC}"
            echo "Verwendung: $0 restart <komponente>"
            exit 1
        fi
        
        COMPONENT="$1"
        
        # Führe stop und dann start aus
        "$0" stop "$COMPONENT" && "$0" start "$COMPONENT"
        ;;
    logs)
        # Zeige Logs einer Komponente an
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}Keine Komponente angegeben${NC}"
            echo "Verwendung: $0 logs <komponente>"
            exit 1
        fi
        
        COMPONENT="$1"
        
        case "$COMPONENT" in
            n8n)
                echo -e "${BLUE}Zeige Logs von n8n an...${NC}"
                echo -e "${YELLOW}n8n-Logs sind nicht über dieses Skript verfügbar.${NC}"
                echo "Bitte starten Sie n8n im Vordergrund oder prüfen Sie die n8n-Logdateien."
                ;;
            web-ui)
                echo -e "${BLUE}Zeige Logs der Web-UI an...${NC}"
                $DOCKER_COMPOSE_CMD -f "docker-compose.web-ui.yml" logs --tail=100
                ;;
            mcp)
                echo -e "${BLUE}Zeige Logs der MCP-Server an...${NC}"
                if [[ -d "/tmp/mcp-logs" ]]; then
                    cat /tmp/mcp-logs/*.log 2>/dev/null || echo -e "${YELLOW}Keine Log-Dateien gefunden.${NC}"
                else
                    echo -e "${YELLOW}MCP-Server-Logs nicht gefunden.${NC}"
                    echo "Bitte prüfen Sie die Docker-Logs:"
                    docker logs $(docker ps --filter "name=mcp" -q)
                fi
                ;;
            *)
                # Prüfe, ob die Komponente ein Docker-Container ist
                if docker ps --format "{{.Names}}" | grep -q "$COMPONENT"; then
                    docker logs "$COMPONENT"
                else
                    echo -e "${RED}Komponente $COMPONENT ist kein laufender Docker-Container${NC}"
                    exit 1
                fi
                ;;
        esac
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
        "$0" stop all
        
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
