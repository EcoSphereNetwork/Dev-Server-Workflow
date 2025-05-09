#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Monitoring-Funktionen für die Dev-Server CLI

# Lade Konfiguration
source "$(dirname "$0")/config.sh"

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funktion zum Überprüfen eines Dienstes
check_service() {
    local service="$1"
    
    log_info "${BLUE}=== Überprüfe Dienst: $service ===${NC}"
    
    if systemctl is-active --quiet "$service"; then
        log_info "${GREEN}✅ Dienst $service ist aktiv${NC}"
        systemctl status "$service" | head -n 3
    else
        log_info "${RED}❌ Dienst $service ist nicht aktiv${NC}"
        systemctl status "$service" | head -n 3
    fi
}

# Funktion zum Abrufen von Logs
get_logs() {
    local service="$1"
    local lines="${2:-100}"
    
    log_info "${BLUE}=== Logs für Dienst: $service ===${NC}"
    
    if [ -f "/var/log/$service.log" ]; then
        tail -n "$lines" "/var/log/$service.log"
    elif [ -f "$LOGS_DIR/$service.log" ]; then
        tail -n "$lines" "$LOGS_DIR/$service.log"
    elif systemctl is-active --quiet "$service"; then
        journalctl -u "$service" -n "$lines"
    else
        log_info "${RED}❌ Keine Logs für Dienst $service gefunden${NC}"
    fi
}

# Funktion zum Überprüfen der Festplattennutzung
check_disk() {
    local path="${1:-/}"
    
    log_info "${BLUE}=== Festplattennutzung für $path ===${NC}"
    
    df -h "$path"
}

# Funktion zum Überprüfen der Speichernutzung
check_memory() {
    log_info "${BLUE}=== Speichernutzung ===${NC}"
    
    free -h
}

# Funktion zum Überprüfen der CPU-Auslastung
check_cpu() {
    log_info "${BLUE}=== CPU-Auslastung ===${NC}"
    
    top -bn1 | head -n 20
}

# Funktion zum Überprüfen eines Ports
check_port() {
    local port="$1"
    
    log_info "${BLUE}=== Überprüfe Port: $port ===${NC}"
    
    if command -v netstat > /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            log_info "${GREEN}✅ Port $port ist in Verwendung${NC}"
            netstat -tuln | grep ":$port "
        else
            log_info "${RED}❌ Port $port ist nicht in Verwendung${NC}"
        fi
    elif command -v ss > /dev/null; then
        if ss -tuln | grep -q ":$port "; then
            log_info "${GREEN}✅ Port $port ist in Verwendung${NC}"
            ss -tuln | grep ":$port "
        else
            log_info "${RED}❌ Port $port ist nicht in Verwendung${NC}"
        fi
    else
        log_info "${YELLOW}⚠️ Weder netstat noch ss ist verfügbar${NC}"
    fi
}

# Funktion zum Überprüfen einer URL
check_url() {
    local url="$1"
    local timeout="${2:-5}"
    
    log_info "${BLUE}=== Überprüfe URL: $url ===${NC}"
    
    if curl -s --head --request GET --max-time "$timeout" "$url" | grep "200 OK" > /dev/null; then
        log_info "${GREEN}✅ URL $url ist erreichbar${NC}"
    else
        log_info "${RED}❌ URL $url ist nicht erreichbar${NC}"
    fi
}

# Funktion zum Überprüfen eines Docker-Containers
check_container() {
    local container="$1"
    
    log_info "${BLUE}=== Überprüfe Container: $container ===${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
        log_info "${GREEN}✅ Container $container läuft${NC}"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "$container"
    else
        log_info "${RED}❌ Container $container läuft nicht${NC}"
        
        if docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
            log_info "${YELLOW}⚠️ Container $container existiert, läuft aber nicht${NC}"
            docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "$container"
        else
            log_info "${RED}❌ Container $container existiert nicht${NC}"
        fi
    fi
}

# Funktion zum Anzeigen von Container-Statistiken
container_stats() {
    local container="${1:-all}"
    
    log_info "${BLUE}=== Container-Statistiken für $container ===${NC}"
    
    if [ "$container" = "all" ]; then
        docker stats --no-stream
    else
        docker stats --no-stream "$container"
    fi
}

# Funktion zum Überprüfen von Prometheus-Metriken
check_prometheus() {
    local metric="$1"
    local prometheus_url="${2:-http://localhost:9090}"
    
    log_info "${BLUE}=== Prometheus-Metriken für $metric ===${NC}"
    
    if [ -z "$metric" ]; then
        log_info "${YELLOW}⚠️ Kein Metrik-Name angegeben${NC}"
        return 1
    fi
    
    local query_url="$prometheus_url/api/v1/query?query=$metric"
    
    if curl -s "$query_url" | jq . > /dev/null; then
        curl -s "$query_url" | jq .
    else
        log_info "${RED}❌ Fehler beim Abrufen der Prometheus-Metriken${NC}"
    fi
}

# Funktion zum Anzeigen der Systemübersicht
system_overview() {
    log_info "${BLUE}=== Systemübersicht ===${NC}"
    
    log_info "${CYAN}Hostname:${NC} $(hostname)"
    log_info "${CYAN}Kernel:${NC} $(uname -r)"
    log_info "${CYAN}Uptime:${NC} $(uptime -p)"
    log_info "${CYAN}CPU-Auslastung:${NC}"
    top -bn1 | head -n 3 | tail -n 2
    log_info "${CYAN}Speichernutzung:${NC}"
    free -h | head -n 2
    log_info "${CYAN}Festplattennutzung:${NC}"
    df -h / | head -n 2
    log_info "${CYAN}Laufende Docker-Container:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || log_info "Docker ist nicht installiert oder läuft nicht"
}

# Funktion zum Anzeigen der Dienste-Übersicht
services_overview() {
    log_info "${BLUE}=== Dienste-Übersicht ===${NC}"
    
    # MCP-Server Status
    if docker ps | grep -q "mcp-"; then
        log_info "${GREEN}✅ MCP-Server (Docker):${NC} Läuft"
    else
        log_info "${RED}❌ MCP-Server (Docker):${NC} Gestoppt"
    fi
    
    # n8n Status
    if docker ps | grep -q "n8n"; then
        log_info "${GREEN}✅ n8n:${NC} Läuft"
    else
        log_info "${RED}❌ n8n:${NC} Gestoppt"
    fi
    
    # Ollama Status
    if docker ps | grep -q "ollama"; then
        log_info "${GREEN}✅ Ollama:${NC} Läuft"
    else
        log_info "${RED}❌ Ollama:${NC} Gestoppt"
    fi
    
    # OpenHands Status
    if docker ps | grep -q "openhands"; then
        log_info "${GREEN}✅ OpenHands:${NC} Läuft"
    else
        log_info "${RED}❌ OpenHands:${NC} Gestoppt"
    fi
    
    # AppFlowy Status
    if docker ps | grep -q "appflowy"; then
        log_info "${GREEN}✅ AppFlowy:${NC} Läuft"
    else
        log_info "${RED}❌ AppFlowy:${NC} Gestoppt"
    fi
    
    # Llamafile Status
    if pgrep -f "llamafile" > /dev/null; then
        log_info "${GREEN}✅ Llamafile:${NC} Läuft"
    else
        log_info "${RED}❌ Llamafile:${NC} Gestoppt"
    fi
    
    # Web-UI Status
    if pgrep -f "npm.*start" > /dev/null && [ -d "$WEB_UI_DIR" ]; then
        log_info "${GREEN}✅ Web-UI:${NC} Läuft"
    else
        log_info "${RED}❌ Web-UI:${NC} Gestoppt"
    fi
}

# Funktion zum Anzeigen der Netzwerkübersicht
network_overview() {
    log_info "${BLUE}=== Netzwerkübersicht ===${NC}"
    
    log_info "${CYAN}Netzwerkschnittstellen:${NC}"
    ip -br addr
    
    log_info "${CYAN}Offene Ports:${NC}"
    if command -v netstat > /dev/null; then
        netstat -tuln | grep LISTEN
    elif command -v ss > /dev/null; then
        ss -tuln | grep LISTEN
    else
        log_info "${YELLOW}⚠️ Weder netstat noch ss ist verfügbar${NC}"
    fi
    
    log_info "${CYAN}Docker-Netzwerke:${NC}"
    docker network ls 2>/dev/null || log_info "Docker ist nicht installiert oder läuft nicht"
}

# Hauptfunktion
main() {
    local action="$1"
    shift
    local args="$@"
    
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
            check_memory
            ;;
        "check-cpu")
            check_cpu
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
        "system-overview")
            system_overview
            ;;
        "services-overview")
            services_overview
            ;;
        "network-overview")
            network_overview
            ;;
        *)
            log_info "${RED}Unbekannte Aktion: $action${NC}"
            log_info "Verfügbare Aktionen: check-service, get-logs, check-disk, check-memory, check-cpu, check-port, check-url, check-container, container-stats, check-prometheus, system-overview, services-overview, network-overview"
            return 1
            ;;
    esac
}

# Führe die Hauptfunktion aus, wenn das Skript direkt ausgeführt wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        log_info "${RED}Keine Aktion angegeben${NC}"
        log_info "Verwendung: $0 <Aktion> [Argumente...]"
        log_info "Verfügbare Aktionen: check-service, get-logs, check-disk, check-memory, check-cpu, check-port, check-url, check-container, container-stats, check-prometheus, system-overview, services-overview, network-overview"
        exit 1
    fi
    
    main "$@"
fi
