#!/bin/bash

# Dev-Server CLI
# Eine umfassende CLI zur Verwaltung des Dev-Server-Workflows

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
SCRIPTS_DIR="$WORKSPACE_DIR/cli/scripts"
CONFIG_DIR="$WORKSPACE_DIR/cli/config"
LOGS_DIR="$WORKSPACE_DIR/cli/logs"
MODELS_DIR="$WORKSPACE_DIR/cli/models"

# Erstelle benötigte Verzeichnisse
mkdir -p "$SCRIPTS_DIR" "$CONFIG_DIR" "$LOGS_DIR" "$MODELS_DIR"

# Konfigurationsdatei
CONFIG_FILE="$CONFIG_DIR/dev-server.conf"

# Lade Konfiguration, wenn vorhanden
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    # Standardwerte
    LLAMAFILE_PATH="$MODELS_DIR/Llama-3.2-3B-Instruct.Q6_K.llamafile"
    LLAMAFILE_URL="https://huggingface.co/Mozilla/Llama-3.2-3B-Instruct-llamafile/resolve/main/Llama-3.2-3B-Instruct.Q6_K.llamafile?download=true"
    LLAMAFILE_PORT=8080
    SHELLGPT_INSTALLED=false
    VERBOSE_MODE=false
    
    # Erstelle Konfigurationsdatei
    cat > "$CONFIG_FILE" << EOF
# Dev-Server CLI Konfiguration
LLAMAFILE_PATH="$LLAMAFILE_PATH"
LLAMAFILE_URL="$LLAMAFILE_URL"
LLAMAFILE_PORT=8080
SHELLGPT_INSTALLED=false
VERBOSE_MODE=false
EOF
fi

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
    echo -e "  ${YELLOW}config${NC} ${CYAN}[Komponente]${NC}       Konfiguriert eine Komponente"
    echo -e "  ${YELLOW}list${NC} ${CYAN}[Ressourcentyp]${NC}      Listet verfügbare Ressourcen auf"
    echo -e "  ${YELLOW}install${NC} ${CYAN}[Komponente]${NC}      Installiert eine Komponente"
    echo -e "  ${YELLOW}update${NC} ${CYAN}[Komponente]${NC}       Aktualisiert eine Komponente"
    echo -e "  ${YELLOW}backup${NC} ${CYAN}[Komponente]${NC}       Erstellt ein Backup einer Komponente"
    echo -e "  ${YELLOW}restore${NC} ${CYAN}[Backup]${NC}          Stellt ein Backup wieder her"
    echo -e "  ${YELLOW}ai${NC} ${CYAN}[Prompt]${NC}               Führt einen KI-Befehl aus"
    echo -e "  ${YELLOW}menu${NC}                     Öffnet das interaktive Menü"
    echo
    echo -e "${GREEN}Komponenten:${NC}"
    echo -e "  ${CYAN}all${NC}                        Alle Komponenten"
    echo -e "  ${CYAN}mcp${NC}                        MCP-Server"
    echo -e "  ${CYAN}n8n${NC}                        n8n-Workflow-Engine"
    echo -e "  ${CYAN}ollama${NC}                     Ollama LLM-Server"
    echo -e "  ${CYAN}openhands${NC}                  OpenHands KI-Agent"
    echo -e "  ${CYAN}llamafile${NC}                  Llamafile LLM"
    echo -e "  ${CYAN}shellgpt${NC}                   ShellGPT CLI"
    echo
    echo -e "${GREEN}Beispiele:${NC}"
    echo -e "  ${YELLOW}dev-server status${NC}"
    echo -e "  ${YELLOW}dev-server start${NC} ${CYAN}mcp${NC}"
    echo -e "  ${YELLOW}dev-server logs${NC} ${CYAN}n8n${NC}"
    echo -e "  ${YELLOW}dev-server ai${NC} ${CYAN}\"Wie starte ich den MCP-Server?\"${NC}"
    echo -e "  ${YELLOW}dev-server menu${NC}"
}

# Statusfunktion
show_status() {
    echo -e "${BLUE}=== Dev-Server Status ===${NC}"
    
    # MCP-Server Status
    if docker ps | grep -q "mcp-"; then
        echo -e "${GREEN}✅ MCP-Server:${NC} Läuft"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "mcp-"
    else
        echo -e "${RED}❌ MCP-Server:${NC} Gestoppt"
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
    
    # Llamafile Status
    if pgrep -f "llamafile" > /dev/null; then
        echo -e "${GREEN}✅ Llamafile:${NC} Läuft"
        ps aux | grep "[l]lamafile" | awk '{print $2, $11, $12, $13}'
    else
        echo -e "${RED}❌ Llamafile:${NC} Gestoppt"
    fi
    
    # ShellGPT Status
    if [ "$SHELLGPT_INSTALLED" = true ] && command -v sgpt > /dev/null; then
        echo -e "${GREEN}✅ ShellGPT:${NC} Installiert"
        sgpt --version 2>/dev/null || echo "Version nicht verfügbar"
    else
        echo -e "${RED}❌ ShellGPT:${NC} Nicht installiert"
    fi
}

# Startfunktion
start_component() {
    local component="$1"
    
    case "$component" in
        "all")
            log "INFO" "Starte alle Komponenten..."
            start_component "mcp"
            start_component "n8n"
            start_component "ollama"
            start_component "openhands"
            start_component "llamafile"
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
                log "ERROR" "MCP-Server-Startskript nicht gefunden"
            fi
            ;;
        "n8n")
            log "INFO" "Starte n8n..."
            if docker ps | grep -q "n8n"; then
                log "WARNING" "n8n läuft bereits"
            else
                docker-compose -f "$WORKSPACE_DIR/docker-mcp-ecosystem/docker-compose.yml" up -d n8n
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "n8n erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten von n8n"
                fi
            fi
            ;;
        "ollama")
            log "INFO" "Starte Ollama..."
            if [ -f "$WORKSPACE_DIR/docker-mcp-ecosystem/ollama-mcp-bridge/start-ollama-bridge.sh" ]; then
                (cd "$WORKSPACE_DIR/docker-mcp-ecosystem/ollama-mcp-bridge" && ./start-ollama-bridge.sh)
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "Ollama erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten von Ollama"
                fi
            else
                log "ERROR" "Ollama-Startskript nicht gefunden"
            fi
            ;;
        "openhands")
            log "INFO" "Starte OpenHands..."
            if [ -f "$WORKSPACE_DIR/docker-mcp-ecosystem/integrate-with-openhands.sh" ]; then
                (cd "$WORKSPACE_DIR/docker-mcp-ecosystem" && ./integrate-with-openhands.sh)
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "OpenHands erfolgreich gestartet"
                else
                    log "ERROR" "Fehler beim Starten von OpenHands"
                fi
            else
                log "ERROR" "OpenHands-Startskript nicht gefunden"
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
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, llamafile"
            ;;
    esac
}

# Stoppfunktion
stop_component() {
    local component="$1"
    
    case "$component" in
        "all")
            log "INFO" "Stoppe alle Komponenten..."
            stop_component "llamafile"
            stop_component "openhands"
            stop_component "ollama"
            stop_component "n8n"
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
        "n8n")
            log "INFO" "Stoppe n8n..."
            docker-compose -f "$WORKSPACE_DIR/docker-mcp-ecosystem/docker-compose.yml" stop n8n
            if [ $? -eq 0 ]; then
                log "SUCCESS" "n8n erfolgreich gestoppt"
            else
                log "ERROR" "Fehler beim Stoppen von n8n"
            fi
            ;;
        "ollama")
            log "INFO" "Stoppe Ollama..."
            if [ -f "$WORKSPACE_DIR/docker-mcp-ecosystem/ollama-mcp-bridge/stop-ollama-bridge.sh" ]; then
                (cd "$WORKSPACE_DIR/docker-mcp-ecosystem/ollama-mcp-bridge" && ./stop-ollama-bridge.sh)
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "Ollama erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen von Ollama"
                fi
            else
                log "ERROR" "Ollama-Stoppskript nicht gefunden"
            fi
            ;;
        "openhands")
            log "INFO" "Stoppe OpenHands..."
            if [ -f "$HOME/stop-openhands.sh" ]; then
                "$HOME/stop-openhands.sh"
                if [ $? -eq 0 ]; then
                    log "SUCCESS" "OpenHands erfolgreich gestoppt"
                else
                    log "ERROR" "Fehler beim Stoppen von OpenHands"
                fi
            else
                log "ERROR" "OpenHands-Stoppskript nicht gefunden"
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
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, llamafile"
            ;;
    esac
}

# Neustartfunktion
restart_component() {
    local component="$1"
    
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
            docker-compose -f "$WORKSPACE_DIR/docker-mcp-ecosystem/docker-compose.yml" logs --tail="$lines" $(docker ps --format "{{.Names}}" | grep "mcp-")
            ;;
        "n8n")
            log "INFO" "Zeige n8n-Logs..."
            docker-compose -f "$WORKSPACE_DIR/docker-mcp-ecosystem/docker-compose.yml" logs --tail="$lines" n8n
            ;;
        "ollama")
            log "INFO" "Zeige Ollama-Logs..."
            docker-compose -f "$WORKSPACE_DIR/docker-mcp-ecosystem/ollama-mcp-bridge/docker-compose.yml" logs --tail="$lines" ollama ollama-mcp-bridge
            ;;
        "openhands")
            log "INFO" "Zeige OpenHands-Logs..."
            docker logs --tail="$lines" openhands
            ;;
        "llamafile")
            log "INFO" "Zeige Llamafile-Logs..."
            tail -n "$lines" "$LOGS_DIR/llamafile.log"
            ;;
        "cli")
            log "INFO" "Zeige CLI-Logs..."
            tail -n "$lines" "$LOGS_DIR/dev-server.log"
            ;;
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: mcp, n8n, ollama, openhands, llamafile, cli"
            ;;
    esac
}

# Installationsfunktion
install_component() {
    local component="$1"
    
    case "$component" in
        "llamafile")
            log "INFO" "Installiere Llamafile..."
            if [ -f "$LLAMAFILE_PATH" ]; then
                log "WARNING" "Llamafile ist bereits installiert"
            else
                log "INFO" "Lade Llamafile herunter..."
                wget -O "$LLAMAFILE_PATH" "$LLAMAFILE_URL"
                if [ $? -eq 0 ]; then
                    chmod +x "$LLAMAFILE_PATH"
                    log "SUCCESS" "Llamafile erfolgreich installiert"
                else
                    log "ERROR" "Fehler beim Herunterladen von Llamafile"
                fi
            fi
            ;;
        "shellgpt")
            log "INFO" "Installiere ShellGPT..."
            if command -v sgpt > /dev/null; then
                log "WARNING" "ShellGPT ist bereits installiert"
            else
                log "INFO" "Installiere ShellGPT mit pip..."
                pip install shell-gpt
                if [ $? -eq 0 ]; then
                    # Konfiguriere ShellGPT für die Verwendung mit Llamafile
                    mkdir -p "$HOME/.config/shell_gpt"
                    cat > "$HOME/.config/shell_gpt/config.yaml" << EOF
OPENAI_API_KEY: "sk-xxx"
OPENAI_API_HOST: "http://localhost:$LLAMAFILE_PORT/v1"
CHAT_CACHE_LENGTH: 100
CHAT_CACHE_PATH: "$HOME/.config/shell_gpt/chat_cache"
CACHE_LENGTH: 100
CACHE_PATH: "$HOME/.config/shell_gpt/cache"
REQUEST_TIMEOUT: 60
TEMPERATURE: 0.1
TOP_P: 1
MAX_TOKENS: 2048
SHELL_COMMAND_HISTORY_LENGTH: 100
SYSTEM_PROMPT: "You are a helpful AI assistant that provides accurate and concise information about the Dev-Server-Workflow project. You help users with commands, troubleshooting, and configuration of MCP servers, n8n workflows, Docker containers, and other components."
EOF
                    # Aktualisiere Konfiguration
                    sed -i "s/SHELLGPT_INSTALLED=false/SHELLGPT_INSTALLED=true/" "$CONFIG_FILE"
                    log "SUCCESS" "ShellGPT erfolgreich installiert und konfiguriert"
                else
                    log "ERROR" "Fehler bei der Installation von ShellGPT"
                fi
            fi
            ;;
        *)
            log "ERROR" "Unbekannte Komponente: $component"
            echo "Verfügbare Komponenten: llamafile, shellgpt"
            ;;
    esac
}

# Listenfunktion
list_resources() {
    local resource_type="$1"
    
    case "$resource_type" in
        "components")
            echo -e "${BLUE}=== Verfügbare Komponenten ===${NC}"
            echo -e "${CYAN}all${NC}         - Alle Komponenten"
            echo -e "${CYAN}mcp${NC}         - MCP-Server"
            echo -e "${CYAN}n8n${NC}         - n8n-Workflow-Engine"
            echo -e "${CYAN}ollama${NC}      - Ollama LLM-Server"
            echo -e "${CYAN}openhands${NC}   - OpenHands KI-Agent"
            echo -e "${CYAN}llamafile${NC}   - Llamafile LLM"
            echo -e "${CYAN}shellgpt${NC}    - ShellGPT CLI"
            ;;
        "mcp-servers")
            echo -e "${BLUE}=== Verfügbare MCP-Server ===${NC}"
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "mcp-" || echo "Keine MCP-Server gefunden"
            ;;
        "workflows")
            echo -e "${BLUE}=== Verfügbare n8n-Workflows ===${NC}"
            if docker ps | grep -q "n8n"; then
                curl -s http://localhost:5678/rest/workflows | jq -r '.data[] | "ID: \(.id) | Name: \(.name) | Active: \(.active)"' || echo "Fehler beim Abrufen der Workflows"
            else
                echo "n8n ist nicht gestartet. Starten Sie n8n mit 'dev-server start n8n'"
            fi
            ;;
        "models")
            echo -e "${BLUE}=== Verfügbare Modelle ===${NC}"
            if docker ps | grep -q "ollama"; then
                echo -e "${YELLOW}Ollama-Modelle:${NC}"
                docker exec ollama ollama list
            else
                echo "Ollama ist nicht gestartet. Starten Sie Ollama mit 'dev-server start ollama'"
            fi
            
            if [ -f "$LLAMAFILE_PATH" ]; then
                echo -e "${YELLOW}Llamafile-Modell:${NC}"
                echo "$(basename "$LLAMAFILE_PATH")"
            else
                echo "Llamafile ist nicht installiert. Installieren Sie es mit 'dev-server install llamafile'"
            fi
            ;;
        "containers")
            echo -e "${BLUE}=== Laufende Container ===${NC}"
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            ;;
        *)
            log "ERROR" "Unbekannter Ressourcentyp: $resource_type"
            echo "Verfügbare Ressourcentypen: components, mcp-servers, workflows, models, containers"
            ;;
    esac
}

# KI-Funktion
ai_command() {
    local prompt="$1"
    
    if [ -z "$prompt" ]; then
        log "ERROR" "Kein Prompt angegeben"
        return 1
    fi
    
    # Prüfe, ob ShellGPT installiert ist
    if [ "$SHELLGPT_INSTALLED" = true ] && command -v sgpt > /dev/null; then
        # Prüfe, ob Llamafile läuft
        if ! pgrep -f "llamafile" > /dev/null; then
            log "WARNING" "Llamafile läuft nicht. Starte Llamafile..."
            start_component "llamafile"
            sleep 5
        fi
        
        log "INFO" "Sende Anfrage an KI: $prompt"
        sgpt "$prompt"
    else
        log "ERROR" "ShellGPT ist nicht installiert. Installieren Sie es mit 'dev-server install shellgpt'"
    fi
}

# Interaktives Menü
show_menu() {
    while true; do
        clear
        echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║                ${YELLOW}Dev-Server Workflow CLI${BLUE}                  ║${NC}"
        echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
        echo
        echo -e "${GREEN}=== Hauptmenü ===${NC}"
        echo -e "${CYAN}1)${NC} Status anzeigen"
        echo -e "${CYAN}2)${NC} Komponenten verwalten"
        echo -e "${CYAN}3)${NC} Logs anzeigen"
        echo -e "${CYAN}4)${NC} Ressourcen auflisten"
        echo -e "${CYAN}5)${NC} Komponenten installieren"
        echo -e "${CYAN}6)${NC} KI-Assistent"
        echo -e "${CYAN}7)${NC} Konfiguration"
        echo -e "${CYAN}0)${NC} Beenden"
        echo
        read -p "Wählen Sie eine Option: " main_option
        
        case $main_option in
            1)
                clear
                show_status
                echo
                read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1
                ;;
            2)
                while true; do
                    clear
                    echo -e "${GREEN}=== Komponenten verwalten ===${NC}"
                    echo -e "${CYAN}1)${NC} Alle Komponenten starten"
                    echo -e "${CYAN}2)${NC} Alle Komponenten stoppen"
                    echo -e "${CYAN}3)${NC} MCP-Server starten"
                    echo -e "${CYAN}4)${NC} MCP-Server stoppen"
                    echo -e "${CYAN}5)${NC} n8n starten"
                    echo -e "${CYAN}6)${NC} n8n stoppen"
                    echo -e "${CYAN}7)${NC} Ollama starten"
                    echo -e "${CYAN}8)${NC} Ollama stoppen"
                    echo -e "${CYAN}9)${NC} OpenHands starten"
                    echo -e "${CYAN}10)${NC} OpenHands stoppen"
                    echo -e "${CYAN}11)${NC} Llamafile starten"
                    echo -e "${CYAN}12)${NC} Llamafile stoppen"
                    echo -e "${CYAN}0)${NC} Zurück zum Hauptmenü"
                    echo
                    read -p "Wählen Sie eine Option: " component_option
                    
                    case $component_option in
                        1) start_component "all"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        2) stop_component "all"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        3) start_component "mcp"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        4) stop_component "mcp"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        5) start_component "n8n"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        6) stop_component "n8n"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        7) start_component "ollama"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        8) stop_component "ollama"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        9) start_component "openhands"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        10) stop_component "openhands"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        11) start_component "llamafile"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        12) stop_component "llamafile"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        0) break ;;
                        *) echo -e "${RED}Ungültige Option${NC}"; sleep 1 ;;
                    esac
                done
                ;;
            3)
                while true; do
                    clear
                    echo -e "${GREEN}=== Logs anzeigen ===${NC}"
                    echo -e "${CYAN}1)${NC} MCP-Server-Logs"
                    echo -e "${CYAN}2)${NC} n8n-Logs"
                    echo -e "${CYAN}3)${NC} Ollama-Logs"
                    echo -e "${CYAN}4)${NC} OpenHands-Logs"
                    echo -e "${CYAN}5)${NC} Llamafile-Logs"
                    echo -e "${CYAN}6)${NC} CLI-Logs"
                    echo -e "${CYAN}0)${NC} Zurück zum Hauptmenü"
                    echo
                    read -p "Wählen Sie eine Option: " logs_option
                    
                    case $logs_option in
                        1) clear; show_logs "mcp"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        2) clear; show_logs "n8n"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        3) clear; show_logs "ollama"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        4) clear; show_logs "openhands"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        5) clear; show_logs "llamafile"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        6) clear; show_logs "cli"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        0) break ;;
                        *) echo -e "${RED}Ungültige Option${NC}"; sleep 1 ;;
                    esac
                done
                ;;
            4)
                while true; do
                    clear
                    echo -e "${GREEN}=== Ressourcen auflisten ===${NC}"
                    echo -e "${CYAN}1)${NC} Komponenten"
                    echo -e "${CYAN}2)${NC} MCP-Server"
                    echo -e "${CYAN}3)${NC} Workflows"
                    echo -e "${CYAN}4)${NC} Modelle"
                    echo -e "${CYAN}5)${NC} Container"
                    echo -e "${CYAN}0)${NC} Zurück zum Hauptmenü"
                    echo
                    read -p "Wählen Sie eine Option: " list_option
                    
                    case $list_option in
                        1) clear; list_resources "components"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        2) clear; list_resources "mcp-servers"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        3) clear; list_resources "workflows"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        4) clear; list_resources "models"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        5) clear; list_resources "containers"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        0) break ;;
                        *) echo -e "${RED}Ungültige Option${NC}"; sleep 1 ;;
                    esac
                done
                ;;
            5)
                while true; do
                    clear
                    echo -e "${GREEN}=== Komponenten installieren ===${NC}"
                    echo -e "${CYAN}1)${NC} Llamafile installieren"
                    echo -e "${CYAN}2)${NC} ShellGPT installieren"
                    echo -e "${CYAN}0)${NC} Zurück zum Hauptmenü"
                    echo
                    read -p "Wählen Sie eine Option: " install_option
                    
                    case $install_option in
                        1) install_component "llamafile"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        2) install_component "shellgpt"; read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1 ;;
                        0) break ;;
                        *) echo -e "${RED}Ungültige Option${NC}"; sleep 1 ;;
                    esac
                done
                ;;
            6)
                clear
                echo -e "${GREEN}=== KI-Assistent ===${NC}"
                echo -e "Geben Sie Ihre Frage ein (oder 'q' zum Beenden):"
                while true; do
                    echo -e "${YELLOW}> ${NC}"
                    read -e prompt
                    
                    if [ "$prompt" = "q" ]; then
                        break
                    fi
                    
                    ai_command "$prompt"
                    echo
                done
                ;;
            7)
                while true; do
                    clear
                    echo -e "${GREEN}=== Konfiguration ===${NC}"
                    echo -e "${CYAN}1)${NC} Konfiguration anzeigen"
                    echo -e "${CYAN}2)${NC} Llamafile-Pfad ändern"
                    echo -e "${CYAN}3)${NC} Llamafile-Port ändern"
                    echo -e "${CYAN}4)${NC} Verbose-Modus umschalten"
                    echo -e "${CYAN}0)${NC} Zurück zum Hauptmenü"
                    echo
                    read -p "Wählen Sie eine Option: " config_option
                    
                    case $config_option in
                        1)
                            clear
                            echo -e "${GREEN}=== Aktuelle Konfiguration ===${NC}"
                            cat "$CONFIG_FILE"
                            echo
                            read -p "Drücken Sie eine Taste, um fortzufahren..." -n 1
                            ;;
                        2)
                            read -p "Neuer Llamafile-Pfad: " new_path
                            sed -i "s|LLAMAFILE_PATH=.*|LLAMAFILE_PATH=\"$new_path\"|" "$CONFIG_FILE"
                            source "$CONFIG_FILE"
                            echo -e "${GREEN}Llamafile-Pfad aktualisiert${NC}"
                            sleep 1
                            ;;
                        3)
                            read -p "Neuer Llamafile-Port: " new_port
                            sed -i "s|LLAMAFILE_PORT=.*|LLAMAFILE_PORT=$new_port|" "$CONFIG_FILE"
                            source "$CONFIG_FILE"
                            echo -e "${GREEN}Llamafile-Port aktualisiert${NC}"
                            sleep 1
                            ;;
                        4)
                            if [ "$VERBOSE_MODE" = true ]; then
                                sed -i "s|VERBOSE_MODE=true|VERBOSE_MODE=false|" "$CONFIG_FILE"
                                VERBOSE_MODE=false
                                echo -e "${GREEN}Verbose-Modus deaktiviert${NC}"
                            else
                                sed -i "s|VERBOSE_MODE=false|VERBOSE_MODE=true|" "$CONFIG_FILE"
                                VERBOSE_MODE=true
                                echo -e "${GREEN}Verbose-Modus aktiviert${NC}"
                            fi
                            sleep 1
                            ;;
                        0) break ;;
                        *) echo -e "${RED}Ungültige Option${NC}"; sleep 1 ;;
                    esac
                done
                ;;
            0)
                echo -e "${GREEN}Auf Wiedersehen!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Ungültige Option${NC}"
                sleep 1
                ;;
        esac
    done
}

# Hauptfunktion
main() {
    # Prüfe, ob Docker installiert ist
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut."
        exit 1
    fi
    
    # Verarbeite Befehlszeilenargumente
    if [ $# -eq 0 ]; then
        show_menu
        exit 0
    fi
    
    command="$1"
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
                echo "Verwendung: dev-server start [Komponente]"
                echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, llamafile"
                exit 1
            fi
            start_component "$1"
            ;;
        "stop")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server stop [Komponente]"
                echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, llamafile"
                exit 1
            fi
            stop_component "$1"
            ;;
        "restart")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server restart [Komponente]"
                echo "Verfügbare Komponenten: all, mcp, n8n, ollama, openhands, llamafile"
                exit 1
            fi
            restart_component "$1"
            ;;
        "logs")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server logs [Komponente] [Anzahl der Zeilen]"
                echo "Verfügbare Komponenten: mcp, n8n, ollama, openhands, llamafile, cli"
                exit 1
            fi
            show_logs "$1" "${2:-100}"
            ;;
        "list")
            if [ $# -eq 0 ]; then
                log "ERROR" "Kein Ressourcentyp angegeben"
                echo "Verwendung: dev-server list [Ressourcentyp]"
                echo "Verfügbare Ressourcentypen: components, mcp-servers, workflows, models, containers"
                exit 1
            fi
            list_resources "$1"
            ;;
        "install")
            if [ $# -eq 0 ]; then
                log "ERROR" "Keine Komponente angegeben"
                echo "Verwendung: dev-server install [Komponente]"
                echo "Verfügbare Komponenten: llamafile, shellgpt"
                exit 1
            fi
            install_component "$1"
            ;;
        "ai")
            if [ $# -eq 0 ]; then
                log "ERROR" "Kein Prompt angegeben"
                echo "Verwendung: dev-server ai [Prompt]"
                exit 1
            fi
            ai_command "$*"
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
main "$@"