#!/bin/bash

# Dev-Server CLI
# Eine umfassende CLI zur Verwaltung des Dev-Server-Workflows

# Setze Fehlermodus
set -e

# Farbdefinitionen
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Pfade
CLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$CLI_DIR")"
CONFIG_DIR="$CLI_DIR/config"
LOGS_DIR="$WORKSPACE_DIR/logs"
MODELS_DIR="$CLI_DIR/models"

# Erstelle benötigte Verzeichnisse
mkdir -p "$CONFIG_DIR" "$LOGS_DIR" "$MODELS_DIR"

# Konfigurationsdatei
CONFIG_FILE="$CONFIG_DIR/dev-server.conf"

# Lade Konfiguration
source "$CLI_DIR/config_improved.sh"

# Lade Funktionen
source "$CLI_DIR/functions.sh"

# Logfunktion
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        *)
            echo -e "[LOG] $message"
            ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOGS_DIR/dev-server.log"
}

# Hilfefunktion
show_help() {
    echo -e "${BLUE}Dev-Server CLI${NC} - Eine umfassende CLI zur Verwaltung des Dev-Server-Workflows"
    echo
    echo -e "Verwendung: ${YELLOW}dev-server${NC} ${GREEN}[Befehl]${NC} ${CYAN}[Optionen]${NC}"
    echo
    echo -e "${GREEN}Verfügbare Befehle:${NC}"
    echo -e "  ${YELLOW}help${NC}                     Zeigt diese Hilfe an"
    echo -e "  ${YELLOW}status${NC}                   Zeigt den Status aller Komponenten an"
    echo -e "  ${YELLOW}start${NC} ${CYAN}[Komponente]${NC}        Startet eine Komponente"
    echo -e "  ${YELLOW}stop${NC} ${CYAN}[Komponente]${NC}         Stoppt eine Komponente"
    echo -e "  ${YELLOW}restart${NC} ${CYAN}[Komponente]${NC}      Startet eine Komponente neu"
    echo -e "  ${YELLOW}logs${NC} ${CYAN}[Komponente]${NC}         Zeigt die Logs einer Komponente an"
    echo -e "  ${YELLOW}config${NC} ${CYAN}[Option] [Wert]${NC}    Konfiguriert eine Option
                                Optionen: llm-api-key, github-token, openproject-token,
                                n8n-api-key, workspace-path, openhands-docker-mcp"
    echo -e "  ${YELLOW}web-ui${NC} ${CYAN}[Aktion]${NC}           Verwaltet die Web-UI
                                Aktionen: start, stop, logs, open"
    echo -e "  ${YELLOW}list${NC} ${CYAN}[Ressourcentyp]${NC}      Listet verfügbare Ressourcen auf"
    echo -e "  ${YELLOW}install${NC} ${CYAN}[Komponente]${NC}      Installiert eine Komponente"
    echo -e "  ${YELLOW}switch-llm${NC} ${CYAN}[LLM]${NC}          Wechselt zwischen LLMs (llamafile, claude)"
    echo -e "  ${YELLOW}update${NC} ${CYAN}[Komponente]${NC}       Aktualisiert eine Komponente"
    echo -e "  ${YELLOW}backup${NC} ${CYAN}[Komponente]${NC}       Erstellt ein Backup einer Komponente"
    echo -e "  ${YELLOW}restore${NC} ${CYAN}[Backup]${NC}          Stellt ein Backup wieder her"
    echo
    echo -e "${GREEN}Erweiterte Befehle:${NC}"
    echo -e "  ${YELLOW}package${NC} ${CYAN}[Aktion] [Paket] [Manager] [Optionen]${NC}    Paketmanagement"
    echo -e "                                Aktionen: install, uninstall, update, upgrade, check"
    echo -e "                                Manager: apt, pip, pip3, npm, npx, dpkg"
    echo -e "  ${YELLOW}configure${NC} ${CYAN}[Aktion] [Datei] [Schlüssel] [Wert] [Extra]${NC}    Konfigurationsmanagement"
    echo -e "                                Aktionen: set, get, comment, uncomment, set-json, get-json,"
    echo -e "                                          set-yaml, get-yaml, set-xml, get-xml, set-env, get-env"
    echo -e "  ${YELLOW}monitor${NC} ${CYAN}[Aktion] [Argumente...]${NC}    Monitoring-Funktionen"
    echo -e "                                Aktionen: check-service, get-logs, check-disk, check-memory,"
    echo -e "                                          check-cpu, check-port, check-url, check-container,"
    echo -e "                                          container-stats, check-prometheus"
    echo -e "  ${YELLOW}ai${NC} ${CYAN}[Prompt]${NC}               Führt einen KI-Befehl aus"
    echo -e "  ${YELLOW}menu${NC}                     Öffnet das interaktive Menü"
    echo
    echo -e "${GREEN}Komponenten:${NC}"
    echo -e "  ${CYAN}all${NC}                        Alle Komponenten"
    echo -e "  ${CYAN}mcp${NC}                        MCP-Server (Docker Container)"
    echo -e "  ${CYAN}n8n-mcp${NC}                    n8n MCP-Server"
    echo -e "  ${CYAN}docker-mcp${NC}                 Docker MCP-Server"
    echo -e "  ${CYAN}monitoring${NC}                 Monitoring Stack (Prometheus, Grafana, Alertmanager)"
    echo -e "  ${CYAN}n8n${NC}                        n8n-Workflow-Engine"
    echo -e "  ${CYAN}ollama${NC}                     Ollama LLM-Server"
    echo -e "  ${CYAN}openhands${NC}                  OpenHands KI-Agent"
    echo -e "  ${CYAN}appflowy${NC}                   AppFlowy Notizen-App"
    echo -e "  ${CYAN}llamafile${NC}                  Llamafile LLM"
    echo -e "  ${CYAN}web-ui${NC}                     Web-UI für die Verwaltung aller Komponenten"
    echo
    echo -e "${GREEN}Beispiele:${NC}"
    echo -e "  ${YELLOW}dev-server status${NC}"
    echo -e "  ${YELLOW}dev-server start${NC} ${CYAN}mcp${NC}"
    echo -e "  ${YELLOW}dev-server logs${NC} ${CYAN}n8n${NC}"
    echo -e "  ${YELLOW}dev-server ai${NC} ${CYAN}\"Wie starte ich den MCP-Server?\"${NC}"
    echo -e "  ${YELLOW}dev-server install${NC} ${CYAN}appflowy${NC}"
    echo -e "  ${YELLOW}dev-server menu${NC}"
}

# Statusfunktion
show_status() {
    echo -e "${BLUE}=== Dev-Server Status ===${NC}"
    
    # MCP-Server Status
    if docker ps | grep -q "mcp-"; then
        echo -e "${GREEN}✅ MCP-Server (Docker):${NC} Läuft"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "mcp-"
    else
        echo -e "${RED}❌ MCP-Server (Docker):${NC} Gestoppt"
    fi
    
    # n8n MCP Server Status
    if pgrep -f "n8n_mcp_server.py" > /dev/null; then
        echo -e "${GREEN}✅ n8n MCP-Server:${NC} Läuft"
        ps aux | grep "[n]8n_mcp_server.py" | awk '{print $2, $11, $12, $13}'
    else
        echo -e "${RED}❌ n8n MCP-Server:${NC} Gestoppt"
    fi
    
    # Docker MCP Server Status
    if pgrep -f "docker_mcp_server.py" > /dev/null; then
        echo -e "${GREEN}✅ Docker MCP-Server:${NC} Läuft"
        ps aux | grep "[d]ocker_mcp_server.py" | awk '{print $2, $11, $12, $13}'
    else
        echo -e "${RED}❌ Docker MCP-Server:${NC} Gestoppt"
    fi
    
    # n8n Status
    if docker ps | grep -q "n8n"; then
        echo -e "${GREEN}✅ n8n:${NC} Läuft"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "n8n"
    else
        echo -e "${RED}❌ n8n:${NC} Gestoppt"
    fi
    
    # Ollama Status
    if docker ps | grep -q "ollama"; then
        echo -e "${GREEN}✅ Ollama:${NC} Läuft"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "ollama"
    else
        echo -e "${RED}❌ Ollama:${NC} Gestoppt"
    fi
    
    # OpenHands Status
    if docker ps | grep -q "openhands"; then
        echo -e "${GREEN}✅ OpenHands:${NC} Läuft"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "openhands"
    else
        echo -e "${RED}❌ OpenHands:${NC} Gestoppt"
    fi
    
    # AppFlowy Status
    if docker ps | grep -q "appflowy"; then
        echo -e "${GREEN}✅ AppFlowy:${NC} Läuft"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "appflowy"
    else
        echo -e "${RED}❌ AppFlowy:${NC} Gestoppt"
    fi
    
    # Llamafile Status
    if pgrep -f "llamafile" > /dev/null; then
        echo -e "${GREEN}✅ Llamafile:${NC} Läuft"
        ps aux | grep "[l]lamafile" | awk '{print $2, $11, $12, $13}'
    else
        echo -e "${RED}❌ Llamafile:${NC} Gestoppt"
    fi
    
    # Web-UI Status
    if pgrep -f "npm.*start" > /dev/null && [ -d "$WEB_UI_DIR" ]; then
        echo -e "${GREEN}✅ Web-UI:${NC} Läuft"
        ps aux | grep "[n]pm.*start" | awk '{print $2, $11, $12, $13}'
    else
        echo -e "${RED}❌ Web-UI:${NC} Gestoppt"
    fi
    
    # LLM-Konfiguration
    echo -e "\n${BLUE}=== LLM-Konfiguration ===${NC}"
    echo -e "Aktives LLM: ${CYAN}$ACTIVE_LLM${NC}"
    
    if [ "$ACTIVE_LLM" == "llamafile" ]; then
        if [ -f "$LLAMAFILE_PATH" ]; then
            echo -e "Llamafile: ${GREEN}Installiert${NC} ($LLAMAFILE_PATH)"
        else
            echo -e "Llamafile: ${RED}Nicht installiert${NC}"
        fi
    elif [ "$ACTIVE_LLM" == "claude" ]; then
        if [ -n "$ANTHROPIC_API_KEY" ]; then
            echo -e "Claude API-Schlüssel: ${GREEN}Konfiguriert${NC}"
            echo -e "Claude Modell: ${CYAN}$CLAUDE_MODEL${NC}"
        else
            echo -e "Claude API-Schlüssel: ${RED}Nicht konfiguriert${NC}"
        fi
    fi
}

# Startfunktion
start_component() {
    local component="$1"
    
    case "$component" in
        "all")
            log "INFO" "Starte alle Komponenten..."
            start_component "mcp"
            start_component "n8n-mcp"
            start_component "docker-mcp"
            start_component "n8n"
            start_component "ollama"
            start_component "openhands"
            start_component "appflowy"
            start_component "llamafile"
            start_component "web-ui"
            ;;
        "mcp")
            log "INFO" "Starte MCP-Server..."
            if [ -f "$WORKSPACE_DIR/docker-mcp-ecosystem/start-mcp-ecosystem.sh" ]; then
                (cd "$WORKSPACE_DIR/docker-mcp-ecosystem" && ./start-mcp-ecosystem.sh)
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "MCP-Server erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten der MCP-Server"
                fi
            else
                log "ERROR" "MCP-Server-Startskript nicht gefunden. Bitte installieren Sie MCP zuerst mit 'dev-server install mcp'"
            fi
            ;;
        "n8n-mcp")
            log "INFO" "Starte n8n MCP-Server..."
            if [ -f "$WORKSPACE_DIR/cli/functions.sh" ]; then
                source "$WORKSPACE_DIR/cli/functions.sh"
                start_mcp "n8n"
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "n8n MCP-Server erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten des n8n MCP-Servers"
                fi
            else
                log "ERROR" "CLI-Funktionen nicht gefunden"
            fi
            ;;
        "docker-mcp")
            log "INFO" "Starte Docker MCP-Server..."
            if [ -f "$WORKSPACE_DIR/cli/functions.sh" ]; then
                source "$WORKSPACE_DIR/cli/functions.sh"
                start_mcp "docker"
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "Docker MCP-Server erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten des Docker MCP-Servers"
                fi
            else
                log "ERROR" "CLI-Funktionen nicht gefunden"
            fi
            ;;
        "n8n")
            log "INFO" "Starte n8n..."
            local compose_file="${DATA_DIR}/n8n-docker-compose.yml"
            
            if [ -f "$compose_file" ]; then
                docker-compose -f "$compose_file" up -d
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "n8n erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten von n8n"
                fi
            else
                log "ERROR" "n8n Docker Compose-Datei nicht gefunden. Bitte installieren Sie n8n zuerst mit 'dev-server install n8n'"
            fi
            ;;
        "ollama")
            log "INFO" "Starte Ollama..."
            local compose_file="${DATA_DIR}/ollama-docker-compose.yml"
            
            if [ -f "$compose_file" ]; then
                docker-compose -f "$compose_file" up -d
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "Ollama erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten von Ollama"
                fi
            else
                log "ERROR" "Ollama Docker Compose-Datei nicht gefunden. Bitte installieren Sie Ollama zuerst mit 'dev-server install ollama'"
            fi
            ;;
        "openhands")
            log "INFO" "Starte OpenHands..."
            local compose_file="${DATA_DIR}/openhands-docker-compose.yml"
            
            if [ -f "$compose_file" ]; then
                docker-compose -f "$compose_file" up -d
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "OpenHands erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten von OpenHands"
                fi
            else
                log "ERROR" "OpenHands Docker Compose-Datei nicht gefunden. Bitte installieren Sie OpenHands zuerst mit 'dev-server install openhands'"
            fi
            ;;
        "appflowy")
            log "INFO" "Starte AppFlowy..."
            local compose_file="${DATA_DIR}/appflowy-docker-compose.yml"
            
            if [ -f "$compose_file" ]; then
                docker-compose -f "$compose_file" up -d
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "AppFlowy erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten von AppFlowy"
                fi
            else
                log "ERROR" "AppFlowy Docker Compose-Datei nicht gefunden. Bitte installieren Sie AppFlowy zuerst mit 'dev-server install appflowy'"
            fi
            ;;
        "llamafile")
            log "INFO" "Starte Llamafile..."
            if pgrep -f "llamafile" > /dev/null; then
                log "WARNING" "Llamafile läuft bereits"
            else
                if [ -f "$LLAMAFILE_PATH" ]; then
                    chmod +x "$LLAMAFILE_PATH"
                    nohup "$LLAMAFILE_PATH" --port "$LLAMAFILE_PORT" --host 0.0.0.0 > "$LOGS_DIR/llamafile.log" 2>&1 &
                    log "SUCCESS" "Llamafile erfolgreich gestartet auf Port $LLAMAFILE_PORT"
                else
                    log "ERROR" "Llamafile nicht gefunden. Bitte installieren Sie es zuerst mit 'dev-server install llamafile'"
                fi
            fi
            ;;
        "web-ui")
            log "INFO" "Starte Web-UI..."
            if [ -d "$WEB_UI_DIR" ]; then
                if pgrep -f "npm.*start" > /dev/null; then
                    log "WARNING" "Web-UI läuft bereits"
                else
                    (cd "$WEB_UI_DIR" && nohup npm start > "$LOGS_DIR/web-ui.log" 2>&1 &)
                    log "SUCCESS" "Web-UI erfolgreich gestartet auf Port $WEB_UI_PORT"
                fi
            else
                log "ERROR" "Web-UI-Verzeichnis nicht gefunden. Bitte installieren Sie die Web-UI zuerst mit 'dev-server install web-ui'"
            fi
            ;;
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: all, mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
            ;;
    esac
}

# Stoppfunktion
stop_component() {
    local component="$1"
    
    case "$component" in
        "all")
            log "INFO" "Stoppe alle Komponenten..."
            stop_component "web-ui"
            stop_component "llamafile"
            stop_component "appflowy"
            stop_component "openhands"
            stop_component "ollama"
            stop_component "n8n"
            stop_component "docker-mcp"
            stop_component "n8n-mcp"
            stop_component "mcp"
            ;;
        "mcp")
            log "INFO" "Stoppe MCP-Server..."
            if [ -f "$WORKSPACE_DIR/docker-mcp-ecosystem/stop-mcp-ecosystem.sh" ]; then
                (cd "$WORKSPACE_DIR/docker-mcp-ecosystem" && ./stop-mcp-ecosystem.sh)
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "MCP-Server erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen der MCP-Server"
                fi
            else
                log "ERROR" "MCP-Server-Stoppskript nicht gefunden"
            fi
            ;;
        "n8n-mcp")
            log "INFO" "Stoppe n8n MCP-Server..."
            if [ -f "$WORKSPACE_DIR/cli/functions.sh" ]; then
                source "$WORKSPACE_DIR/cli/functions.sh"
                stop_mcp "n8n"
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "n8n MCP-Server erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen des n8n MCP-Servers"
                fi
            else
                log "ERROR" "CLI-Funktionen nicht gefunden"
            fi
            ;;
        "docker-mcp")
            log "INFO" "Stoppe Docker MCP-Server..."
            if [ -f "$WORKSPACE_DIR/cli/functions.sh" ]; then
                source "$WORKSPACE_DIR/cli/functions.sh"
                stop_mcp "docker"
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "Docker MCP-Server erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen des Docker MCP-Servers"
                fi
            else
                log "ERROR" "CLI-Funktionen nicht gefunden"
            fi
            ;;
        "n8n")
            log "INFO" "Stoppe n8n..."
            local compose_file="${DATA_DIR}/n8n-docker-compose.yml"
            
            if [ -f "$compose_file" ]; then
                docker-compose -f "$compose_file" down
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "n8n erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen von n8n"
                fi
            else
                docker stop n8n 2>/dev/null || true
                log "WARNING" "n8n Docker Compose-Datei nicht gefunden. Versuche, Container direkt zu stoppen."
            fi
            ;;
        "ollama")
            log "INFO" "Stoppe Ollama..."
            local compose_file="${DATA_DIR}/ollama-docker-compose.yml"
            
            if [ -f "$compose_file" ]; then
                docker-compose -f "$compose_file" down
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "Ollama erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen von Ollama"
                fi
            else
                docker stop ollama 2>/dev/null || true
                log "WARNING" "Ollama Docker Compose-Datei nicht gefunden. Versuche, Container direkt zu stoppen."
            fi
            ;;
        "openhands")
            log "INFO" "Stoppe OpenHands..."
            local compose_file="${DATA_DIR}/openhands-docker-compose.yml"
            
            if [ -f "$compose_file" ]; then
                docker-compose -f "$compose_file" down
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "OpenHands erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen von OpenHands"
                fi
            else
                docker stop openhands 2>/dev/null || true
                log "WARNING" "OpenHands Docker Compose-Datei nicht gefunden. Versuche, Container direkt zu stoppen."
            fi
            ;;
        "appflowy")
            log "INFO" "Stoppe AppFlowy..."
            local compose_file="${DATA_DIR}/appflowy-docker-compose.yml"
            
            if [ -f "$compose_file" ]; then
                docker-compose -f "$compose_file" down
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "AppFlowy erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen von AppFlowy"
                fi
            else
                docker stop appflowy-cloud postgres redis 2>/dev/null || true
                log "WARNING" "AppFlowy Docker Compose-Datei nicht gefunden. Versuche, Container direkt zu stoppen."
            fi
            ;;
        "llamafile")
            log "INFO" "Stoppe Llamafile..."
            if pgrep -f "llamafile" > /dev/null; then
                pkill -f "llamafile"
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "Llamafile erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen von Llamafile"
                fi
            else
                log "WARNING" "Llamafile läuft nicht"
            fi
            ;;
        "web-ui")
            log "INFO" "Stoppe Web-UI..."
            if pgrep -f "npm.*start" > /dev/null; then
                pkill -f "npm.*start"
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "Web-UI erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen der Web-UI"
                fi
            else
                log "WARNING" "Web-UI läuft nicht"
            fi
            ;;
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: all, mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
            ;;
    esac
}

# Neustartfunktion
restart_component() {
    local component="$1"
    
    log "INFO" "Starte $component neu..."
    stop_component "$component"
    sleep 2
    start_component "$component"
}

# Logfunktion
show_logs() {
    local component="$1"
    local lines="${2:-100}"
    
    case "$component" in
        "mcp")
            log "INFO" "Zeige MCP-Server-Logs..."
            if [ -f "$LOGS_DIR/mcp_server.log" ]; then
                tail -n "$lines" -f "$LOGS_DIR/mcp_server.log"
            else
                log "ERROR" "MCP-Server-Logdatei nicht gefunden"
            fi
            ;;
        "n8n-mcp")
            log "INFO" "Zeige n8n MCP-Server-Logs..."
            if [ -f "$LOGS_DIR/mcp_server.log" ]; then
                tail -n "$lines" -f "$LOGS_DIR/mcp_server.log"
            else
                log "ERROR" "n8n MCP-Server-Logdatei nicht gefunden"
            fi
            ;;
        "docker-mcp")
            log "INFO" "Zeige Docker MCP-Server-Logs..."
            if [ -f "$LOGS_DIR/docker_mcp_server.log" ]; then
                tail -n "$lines" -f "$LOGS_DIR/docker_mcp_server.log"
            else
                log "ERROR" "Docker MCP-Server-Logdatei nicht gefunden"
            fi
            ;;
        "n8n")
            log "INFO" "Zeige n8n-Logs..."
            docker logs -f --tail "$lines" n8n 2>/dev/null || log "ERROR" "n8n-Container nicht gefunden"
            ;;
        "ollama")
            log "INFO" "Zeige Ollama-Logs..."
            docker logs -f --tail "$lines" ollama 2>/dev/null || log "ERROR" "Ollama-Container nicht gefunden"
            ;;
        "openhands")
            log "INFO" "Zeige OpenHands-Logs..."
            docker logs -f --tail "$lines" openhands 2>/dev/null || log "ERROR" "OpenHands-Container nicht gefunden"
            ;;
        "appflowy")
            log "INFO" "Zeige AppFlowy-Logs..."
            docker logs -f --tail "$lines" appflowy-cloud 2>/dev/null || log "ERROR" "AppFlowy-Container nicht gefunden"
            ;;
        "llamafile")
            log "INFO" "Zeige Llamafile-Logs..."
            if [ -f "$LOGS_DIR/llamafile.log" ]; then
                tail -n "$lines" -f "$LOGS_DIR/llamafile.log"
            else
                log "ERROR" "Llamafile-Logdatei nicht gefunden"
            fi
            ;;
        "web-ui")
            log "INFO" "Zeige Web-UI-Logs..."
            if [ -f "$LOGS_DIR/web-ui.log" ]; then
                tail -n "$lines" -f "$LOGS_DIR/web-ui.log"
            else
                log "ERROR" "Web-UI-Logdatei nicht gefunden"
            fi
            ;;
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
            ;;
    esac
}

# Konfigurationsfunktion
configure() {
    local option="$1"
    local value="$2"
    
    case "$option" in
        "llm-api-key")
            log "INFO" "Setze LLM API-Schlüssel..."
            sed -i "s/^ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=\"$value\"/" "$CONFIG_FILE"
            log "SUCCESS" "LLM API-Schlüssel erfolgreich gesetzt"
            ;;
        "github-token")
            log "INFO" "Setze GitHub-Token..."
            sed -i "s/^GITHUB_TOKEN=.*/GITHUB_TOKEN=\"$value\"/" "$CONFIG_FILE"
            log "SUCCESS" "GitHub-Token erfolgreich gesetzt"
            ;;
        "openproject-token")
            log "INFO" "Setze OpenProject-Token..."
            sed -i "s/^OPENPROJECT_TOKEN=.*/OPENPROJECT_TOKEN=\"$value\"/" "$CONFIG_FILE"
            log "SUCCESS" "OpenProject-Token erfolgreich gesetzt"
            ;;
        "n8n-api-key")
            log "INFO" "Setze n8n API-Schlüssel..."
            sed -i "s/^N8N_API_KEY=.*/N8N_API_KEY=\"$value\"/" "$CONFIG_FILE"
            log "SUCCESS" "n8n API-Schlüssel erfolgreich gesetzt"
            ;;
        "workspace-path")
            log "INFO" "Setze Workspace-Pfad..."
            sed -i "s|^BASE_DIR=.*|BASE_DIR=\"$value\"|" "$CONFIG_FILE"
            log "SUCCESS" "Workspace-Pfad erfolgreich gesetzt"
            ;;
        "active-llm")
            log "INFO" "Setze aktives LLM..."
            if [ "$value" == "llamafile" ] || [ "$value" == "claude" ]; then
                sed -i "s/^ACTIVE_LLM=.*/ACTIVE_LLM=\"$value\"/" "$CONFIG_FILE"
                log "SUCCESS" "Aktives LLM erfolgreich auf $value gesetzt"
            else
                log "ERROR" "Ungültiges LLM: $value. Verfügbare Optionen: llamafile, claude"
            fi
            ;;
        *)
            log "ERROR" "Unbekannte Option: $option"
            echo "Verfügbare Optionen: llm-api-key, github-token, openproject-token, n8n-api-key, workspace-path, active-llm"
            ;;
    esac
}

# Web-UI-Verwaltungsfunktion
manage_web_ui() {
    local action="$1"
    
    case "$action" in
        "start")
            log "INFO" "Starte Web-UI..."
            start_component "web-ui"
            ;;
        "stop")
            log "INFO" "Stoppe Web-UI..."
            stop_component "web-ui"
            ;;
        "logs")
            log "INFO" "Zeige Web-UI-Logs..."
            show_logs "web-ui"
            ;;
        "open")
            log "INFO" "Öffne Web-UI im Browser..."
            if command -v xdg-open > /dev/null; then
                xdg-open "http://localhost:$WEB_UI_PORT"
            elif command -v open > /dev/null; then
                open "http://localhost:$WEB_UI_PORT"
            else
                log "ERROR" "Kann Browser nicht öffnen. Bitte öffnen Sie http://localhost:$WEB_UI_PORT manuell."
            fi
            ;;
        *)
            log "ERROR" "Unbekannte Aktion: $action"
            echo "Verfügbare Aktionen: start, stop, logs, open"
            ;;
    esac
}

# LLM-Wechselfunktion
switch_llm() {
    local llm="$1"
    
    case "$llm" in
        "llamafile")
            log "INFO" "Wechsle zu Llamafile..."
            configure "active-llm" "llamafile"
            ;;
        "claude")
            log "INFO" "Wechsle zu Claude..."
            configure "active-llm" "claude"
            ;;
        *)
            log "ERROR" "Unbekanntes LLM: $llm"
            echo "Verfügbare LLMs: llamafile, claude"
            ;;
    esac
}

# Installationsfunktion
install() {
    local component="$1"
    
    log "INFO" "Installiere $component..."
    source "$CLI_DIR/install_components.sh"
    install_component "$component"
}

# Aktualisierungsfunktion
update() {
    local component="$1"
    
    log "INFO" "Aktualisiere $component..."
    
    case "$component" in
        "all")
            log "INFO" "Aktualisiere alle Komponenten..."
            update "mcp"
            update "n8n"
            update "ollama"
            update "openhands"
            update "appflowy"
            update "llamafile"
            update "web-ui"
            ;;
        "mcp")
            log "INFO" "Aktualisiere MCP-Server..."
            if [ -d "$WORKSPACE_DIR/docker-mcp-ecosystem" ]; then
                (cd "$WORKSPACE_DIR/docker-mcp-ecosystem" && git pull)
                log "SUCCESS" "MCP-Server erfolgreich aktualisiert"
            else
                log "ERROR" "MCP-Server-Verzeichnis nicht gefunden. Bitte installieren Sie MCP zuerst mit 'dev-server install mcp'"
            fi
            ;;
        "n8n")
            log "INFO" "Aktualisiere n8n..."
            docker pull n8nio/n8n:latest
            log "SUCCESS" "n8n erfolgreich aktualisiert"
            ;;
        "ollama")
            log "INFO" "Aktualisiere Ollama..."
            docker pull ollama/ollama:latest
            log "SUCCESS" "Ollama erfolgreich aktualisiert"
            ;;
        "openhands")
            log "INFO" "Aktualisiere OpenHands..."
            docker pull openhands/openhands:latest
            log "SUCCESS" "OpenHands erfolgreich aktualisiert"
            ;;
        "appflowy")
            log "INFO" "Aktualisiere AppFlowy..."
            docker pull appflowy/appflowy-cloud:latest
            log "SUCCESS" "AppFlowy erfolgreich aktualisiert"
            ;;
        "llamafile")
            log "INFO" "Aktualisiere Llamafile..."
            install "llamafile"
            ;;
        "web-ui")
            log "INFO" "Aktualisiere Web-UI..."
            if [ -d "$WEB_UI_DIR" ]; then
                (cd "$WEB_UI_DIR" && git pull && npm install)
                log "SUCCESS" "Web-UI erfolgreich aktualisiert"
            else
                log "ERROR" "Web-UI-Verzeichnis nicht gefunden. Bitte installieren Sie die Web-UI zuerst mit 'dev-server install web-ui'"
            fi
            ;;
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
            ;;
    esac
}

# Backup-Funktion
backup() {
    local component="$1"
    
    log "INFO" "Erstelle Backup von $component..."
    
    # Erstelle Backup-Verzeichnis
    local backup_dir="$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)_$component"
    mkdir -p "$backup_dir"
    
    case "$component" in
        "all")
            log "INFO" "Erstelle Backup aller Komponenten..."
            backup "mcp"
            backup "n8n"
            backup "ollama"
            backup "openhands"
            backup "appflowy"
            backup "config"
            ;;
        "mcp")
            log "INFO" "Erstelle Backup von MCP-Server..."
            if [ -d "$WORKSPACE_DIR/docker-mcp-ecosystem" ]; then
                tar -czf "$backup_dir/mcp.tar.gz" -C "$WORKSPACE_DIR" docker-mcp-ecosystem
                log "SUCCESS" "MCP-Server-Backup erfolgreich erstellt: $backup_dir/mcp.tar.gz"
            else
                log "ERROR" "MCP-Server-Verzeichnis nicht gefunden"
            fi
            ;;
        "n8n")
            log "INFO" "Erstelle Backup von n8n..."
            if [ -d "$N8N_DATA_DIR" ]; then
                tar -czf "$backup_dir/n8n.tar.gz" -C "$(dirname "$N8N_DATA_DIR")" "$(basename "$N8N_DATA_DIR")"
                log "SUCCESS" "n8n-Backup erfolgreich erstellt: $backup_dir/n8n.tar.gz"
            else
                log "ERROR" "n8n-Datenverzeichnis nicht gefunden"
            fi
            ;;
        "ollama")
            log "INFO" "Erstelle Backup von Ollama..."
            if [ -d "$OLLAMA_DATA_DIR" ]; then
                tar -czf "$backup_dir/ollama.tar.gz" -C "$(dirname "$OLLAMA_DATA_DIR")" "$(basename "$OLLAMA_DATA_DIR")"
                log "SUCCESS" "Ollama-Backup erfolgreich erstellt: $backup_dir/ollama.tar.gz"
            else
                log "ERROR" "Ollama-Datenverzeichnis nicht gefunden"
            fi
            ;;
        "openhands")
            log "INFO" "Erstelle Backup von OpenHands..."
            if [ -d "$OPENHANDS_DATA_DIR" ]; then
                tar -czf "$backup_dir/openhands.tar.gz" -C "$(dirname "$OPENHANDS_DATA_DIR")" "$(basename "$OPENHANDS_DATA_DIR")"
                log "SUCCESS" "OpenHands-Backup erfolgreich erstellt: $backup_dir/openhands.tar.gz"
            else
                log "ERROR" "OpenHands-Datenverzeichnis nicht gefunden"
            fi
            ;;
        "appflowy")
            log "INFO" "Erstelle Backup von AppFlowy..."
            local appflowy_data_dir="${DATA_DIR}/appflowy"
            if [ -d "$appflowy_data_dir" ]; then
                tar -czf "$backup_dir/appflowy.tar.gz" -C "$(dirname "$appflowy_data_dir")" "$(basename "$appflowy_data_dir")"
                log "SUCCESS" "AppFlowy-Backup erfolgreich erstellt: $backup_dir/appflowy.tar.gz"
            else
                log "ERROR" "AppFlowy-Datenverzeichnis nicht gefunden"
            fi
            ;;
        "config")
            log "INFO" "Erstelle Backup der Konfiguration..."
            if [ -d "$CONFIG_DIR" ]; then
                tar -czf "$backup_dir/config.tar.gz" -C "$(dirname "$CONFIG_DIR")" "$(basename "$CONFIG_DIR")"
                log "SUCCESS" "Konfigurations-Backup erfolgreich erstellt: $backup_dir/config.tar.gz"
            else
                log "ERROR" "Konfigurationsverzeichnis nicht gefunden"
            fi
            ;;
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, appflowy, config"
            ;;
    esac
}

# Wiederherstellungsfunktion
restore() {
    local backup_file="$1"
    
    log "INFO" "Stelle Backup wieder her: $backup_file..."
    
    if [ ! -f "$backup_file" ]; then
        log "ERROR" "Backup-Datei nicht gefunden: $backup_file"
        return 1
    fi
    
    # Bestimme den Komponententyp anhand des Dateinamens
    local component=""
    if [[ "$backup_file" == *"mcp.tar.gz" ]]; then
        component="mcp"
    elif [[ "$backup_file" == *"n8n.tar.gz" ]]; then
        component="n8n"
    elif [[ "$backup_file" == *"ollama.tar.gz" ]]; then
        component="ollama"
    elif [[ "$backup_file" == *"openhands.tar.gz" ]]; then
        component="openhands"
    elif [[ "$backup_file" == *"appflowy.tar.gz" ]]; then
        component="appflowy"
    elif [[ "$backup_file" == *"config.tar.gz" ]]; then
        component="config"
    else
        log "ERROR" "Unbekannter Backup-Typ: $backup_file"
        return 1
    fi
    
    # Stoppe die Komponente
    log "INFO" "Stoppe $component vor der Wiederherstellung..."
    stop_component "$component"
    
    # Stelle das Backup wieder her
    case "$component" in
        "mcp")
            log "INFO" "Stelle MCP-Server wieder her..."
            tar -xzf "$backup_file" -C "$WORKSPACE_DIR"
            log "SUCCESS" "MCP-Server erfolgreich wiederhergestellt"
            ;;
        "n8n")
            log "INFO" "Stelle n8n wieder her..."
            tar -xzf "$backup_file" -C "$(dirname "$N8N_DATA_DIR")"
            log "SUCCESS" "n8n erfolgreich wiederhergestellt"
            ;;
        "ollama")
            log "INFO" "Stelle Ollama wieder her..."
            tar -xzf "$backup_file" -C "$(dirname "$OLLAMA_DATA_DIR")"
            log "SUCCESS" "Ollama erfolgreich wiederhergestellt"
            ;;
        "openhands")
            log "INFO" "Stelle OpenHands wieder her..."
            tar -xzf "$backup_file" -C "$(dirname "$OPENHANDS_DATA_DIR")"
            log "SUCCESS" "OpenHands erfolgreich wiederhergestellt"
            ;;
        "appflowy")
            log "INFO" "Stelle AppFlowy wieder her..."
            local appflowy_data_dir="${DATA_DIR}/appflowy"
            tar -xzf "$backup_file" -C "$(dirname "$appflowy_data_dir")"
            log "SUCCESS" "AppFlowy erfolgreich wiederhergestellt"
            ;;
        "config")
            log "INFO" "Stelle Konfiguration wieder her..."
            tar -xzf "$backup_file" -C "$(dirname "$CONFIG_DIR")"
            log "SUCCESS" "Konfiguration erfolgreich wiederhergestellt"
            ;;
    esac
    
    # Starte die Komponente wieder
    log "INFO" "Starte $component nach der Wiederherstellung..."
    start_component "$component"
}

# Paketmanagement-Funktion
manage_package() {
    local action="$1"
    local package="$2"
    local manager="$3"
    shift 3
    local options="$@"
    
    log "INFO" "Führe Paketmanagement aus: $action $package mit $manager $options..."
    source "$CLI_DIR/package_management.sh"
    
    case "$action" in
        "install")
            install_package "$package" "$manager" "$options"
            ;;
        "uninstall")
            uninstall_package "$package" "$manager" "$options"
            ;;
        "update")
            update_package "$package" "$manager" "$options"
            ;;
        "upgrade")
            upgrade_package "$package" "$manager" "$options"
            ;;
        "check")
            check_package "$package" "$manager"
            ;;
        *)
            log "ERROR" "Unbekannte Aktion: $action"
            echo "Verfügbare Aktionen: install, uninstall, update, upgrade, check"
            ;;
    esac
}

# Konfigurationsmanagement-Funktion
manage_configuration() {
    local action="$1"
    local file="$2"
    local key="$3"
    local value="$4"
    local extra="$5"
    
    log "INFO" "Führe Konfigurationsmanagement aus: $action $file $key $value $extra..."
    source "$CLI_DIR/config_management.sh"
    
    case "$action" in
        "set")
            set_config "$file" "$key" "$value"
            ;;
        "get")
            get_config "$file" "$key"
            ;;
        "comment")
            comment_config "$file" "$key"
            ;;
        "uncomment")
            uncomment_config "$file" "$key"
            ;;
        "set-json")
            set_json_config "$file" "$key" "$value"
            ;;
        "get-json")
            get_json_config "$file" "$key"
            ;;
        "set-yaml")
            set_yaml_config "$file" "$key" "$value"
            ;;
        "get-yaml")
            get_yaml_config "$file" "$key"
            ;;
        "set-xml")
            set_xml_config "$file" "$key" "$value"
            ;;
        "get-xml")
            get_xml_config "$file" "$key"
            ;;
        "set-env")
            set_env_config "$file" "$key" "$value"
            ;;
        "get-env")
            get_env_config "$file" "$key"
            ;;
        *)
            log "ERROR" "Unbekannte Aktion: $action"
            echo "Verfügbare Aktionen: set, get, comment, uncomment, set-json, get-json, set-yaml, get-yaml, set-xml, get-xml, set-env, get-env"
            ;;
    esac
}

# Monitoring-Funktion
monitor() {
    local action="$1"
    shift
    local args="$@"
    
    log "INFO" "Führe Monitoring aus: $action $args..."
    source "$CLI_DIR/monitoring.sh"
    
    case "$action" in
        "check-service")
            check_service "$args"
            ;;
        "get-logs")
            get_logs "$args"
            ;;
        "check-disk")
            check_disk "$args"
            ;;
        "check-memory")
            check_memory "$args"
            ;;
        "check-cpu")
            check_cpu "$args"
            ;;
        "check-port")
            check_port "$args"
            ;;
        "check-url")
            check_url "$args"
            ;;
        "check-container")
            check_container "$args"
            ;;
        "container-stats")
            container_stats "$args"
            ;;
        "check-prometheus")
            check_prometheus "$args"
            ;;
        *)
            log "ERROR" "Unbekannte Aktion: $action"
            echo "Verfügbare Aktionen: check-service, get-logs, check-disk, check-memory, check-cpu, check-port, check-url, check-container, container-stats, check-prometheus"
            ;;
    esac
}

# KI-Assistent-Funktion
ai_assistant() {
    local prompt="$@"
    
    log "INFO" "Führe KI-Assistent aus: $prompt..."
    "$CLI_DIR/ai_assistant_improved.sh" "$prompt"
}

# Menü-Funktion
show_menu() {
    log "INFO" "Öffne interaktives Menü..."
    "$CLI_DIR/menu.sh"
}

# Hauptfunktion
main() {
    local command="$1"
    shift
    
    case "$command" in
        "help")
            show_help
            ;;
        "status")
            show_status
            ;;
        "start")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server start <Komponente>"
                echo "Verfügbare Komponenten: all, mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
                exit 1
            fi
            start_component "$1"
            ;;
        "stop")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server stop <Komponente>"
                echo "Verfügbare Komponenten: all, mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
                exit 1
            fi
            stop_component "$1"
            ;;
        "restart")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server restart <Komponente>"
                echo "Verfügbare Komponenten: all, mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
                exit 1
            fi
            restart_component "$1"
            ;;
        "logs")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server logs <Komponente> [Anzahl Zeilen]"
                echo "Verfügbare Komponenten: mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
                exit 1
            fi
            show_logs "$1" "$2"
            ;;
        "config")
            if [ $# -lt 2 ]; then
                log "ERROR" "Unvollständige Parameter"
                echo "Verwendung: dev-server config <Option> <Wert>"
                echo "Verfügbare Optionen: llm-api-key, github-token, openproject-token, n8n-api-key, workspace-path, active-llm"
                exit 1
            fi
            configure "$1" "$2"
            ;;
        "web-ui")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Aktion angegeben"
                echo "Verwendung: dev-server web-ui <Aktion>"
                echo "Verfügbare Aktionen: start, stop, logs, open"
                exit 1
            fi
            manage_web_ui "$1"
            ;;
        "install")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server install <Komponente>"
                echo "Verfügbare Komponenten: all, docker, docker-compose, n8n, mcp, openhands, appflowy, llamafile, ollama, web-ui"
                exit 1
            fi
            install "$1"
            ;;
        "switch-llm")
            if [ $# -eq 0 ]; then
                log "ERROR" "Kein LLM angegeben"
                echo "Verwendung: dev-server switch-llm <LLM>"
                echo "Verfügbare LLMs: llamafile, claude"
                exit 1
            fi
            switch_llm "$1"
            ;;
        "update")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server update <Komponente>"
                echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, appflowy, llamafile, web-ui"
                exit 1
            fi
            update "$1"
            ;;
        "backup")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server backup <Komponente>"
                echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, appflowy, config"
                exit 1
            fi
            backup "$1"
            ;;
        "restore")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Backup-Datei angegeben"
                echo "Verwendung: dev-server restore <Backup-Datei>"
                exit 1
            fi
            restore "$1"
            ;;
        "package")
            if [ $# -lt 3 ]; then
                log "ERROR" "Unvollständige Parameter"
                echo "Verwendung: dev-server package <Aktion> <Paket> <Manager> [Optionen]"
                echo "Verfügbare Aktionen: install, uninstall, update, upgrade, check"
                echo "Verfügbare Manager: apt, pip, pip3, npm, npx, dpkg"
                exit 1
            fi
            manage_package "$1" "$2" "$3" "${@:4}"
            ;;
        "configure")
            if [ $# -lt 3 ]; then
                log "ERROR" "Unvollständige Parameter"
                echo "Verwendung: dev-server configure <Aktion> <Datei> <Schlüssel> [Wert] [Extra]"
                echo "Verfügbare Aktionen: set, get, comment, uncomment, set-json, get-json, set-yaml, get-yaml, set-xml, get-xml, set-env, get-env"
                exit 1
            fi
            manage_configuration "$1" "$2" "$3" "$4" "$5"
            ;;
        "monitor")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Aktion angegeben"
                echo "Verwendung: dev-server monitor <Aktion> [Argumente...]"
                echo "Verfügbare Aktionen: check-service, get-logs, check-disk, check-memory, check-cpu, check-port, check-url, check-container, container-stats, check-prometheus"
                exit 1
            fi
            monitor "$1" "${@:2}"
            ;;
        "ai")
            if [ $# -eq 0 ]; then
                log "ERROR" "Kein Prompt angegeben"
                echo "Verwendung: dev-server ai \"<Prompt>\""
                exit 1
            fi
            ai_assistant "$@"
            ;;
        "menu")
            show_menu
            ;;
        *)
            log "ERROR" "Unbekannter Befehl: $command"
            show_help
            exit 1
            ;;
    esac
}

# Führe die Hauptfunktion aus
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

main "$@"