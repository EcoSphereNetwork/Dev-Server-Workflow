#!/bin/bash

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
    
    echo -e "${BLUE}=== Überprüfe Dienst: $service ===${NC}"
    
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✅ Dienst $service ist aktiv${NC}"
        systemctl status "$service" | head -n 3
    else
        echo -e "${RED}❌ Dienst $service ist nicht aktiv${NC}"
        systemctl status "$service" | head -n 3
    fi
}

# Funktion zum Abrufen von Logs
get_logs() {
    local service="$1"
    local lines="${2:-100}"
    
    echo -e "${BLUE}=== Logs für Dienst: $service ===${NC}"
    
    if [ -f "/var/log/$service.log" ]; then
        tail -n "$lines" "/var/log/$service.log"
    elif [ -f "$LOGS_DIR/$service.log" ]; then
        tail -n "$lines" "$LOGS_DIR/$service.log"
    elif systemctl is-active --quiet "$service"; then
        journalctl -u "$service" -n "$lines"
    else
        echo -e "${RED}❌ Keine Logs für Dienst $service gefunden${NC}"
    fi
}

# Funktion zum Überprüfen der Festplattennutzung
check_disk() {
    local path="${1:-/}"
    
    echo -e "${BLUE}=== Festplattennutzung für $path ===${NC}"
    
    df -h "$path"
}

# Funktion zum Überprüfen der Speichernutzung
check_memory() {
    echo -e "${BLUE}=== Speichernutzung ===${NC}"
    
    free -h
}

# Funktion zum Überprüfen der CPU-Auslastung
check_cpu() {
    echo -e "${BLUE}=== CPU-Auslastung ===${NC}"
    
    top -bn1 | head -n 20
}

# Funktion zum Überprüfen eines Ports
check_port() {
    local port="$1"
    
    echo -e "${BLUE}=== Überprüfe Port: $port ===${NC}"
    
    if command -v netstat > /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            echo -e "${GREEN}✅ Port $port ist in Verwendung${NC}"
            netstat -tuln | grep ":$port "
        else
            echo -e "${RED}❌ Port $port ist nicht in Verwendung${NC}"
        fi
    elif command -v ss > /dev/null; then
        if ss -tuln | grep -q ":$port "; then
            echo -e "${GREEN}✅ Port $port ist in Verwendung${NC}"
            ss -tuln | grep ":$port "
        else
            echo -e "${RED}❌ Port $port ist nicht in Verwendung${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Weder netstat noch ss ist verfügbar${NC}"
    fi
}

# Funktion zum Überprüfen einer URL
check_url() {
    local url="$1"
    local timeout="${2:-5}"
    
    echo -e "${BLUE}=== Überprüfe URL: $url ===${NC}"
    
    if curl -s --head --request GET --max-time "$timeout" "$url" | grep "200 OK" > /dev/null; then
        echo -e "${GREEN}✅ URL $url ist erreichbar${NC}"
    else
        echo -e "${RED}❌ URL $url ist nicht erreichbar${NC}"
    fi
}

# Funktion zum Überprüfen eines Docker-Containers
check_container() {
    local container="$1"
    
    echo -e "${BLUE}=== Überprüfe Container: $container ===${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
        echo -e "${GREEN}✅ Container $container läuft${NC}"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "$container"
    else
        echo -e "${RED}❌ Container $container läuft nicht${NC}"
        
        if docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
            echo -e "${YELLOW}⚠️ Container $container existiert, läuft aber nicht${NC}"
            docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "$container"
        else
            echo -e "${RED}❌ Container $container existiert nicht${NC}"
        fi
    fi
}

# Funktion zum Anzeigen von Container-Statistiken
container_stats() {
    local container="${1:-all}"
    
    echo -e "${BLUE}=== Container-Statistiken für $container ===${NC}"
    
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
    
    echo -e "${BLUE}=== Prometheus-Metriken für $metric ===${NC}"
    
    if [ -z "$metric" ]; then
        echo -e "${YELLOW}⚠️ Kein Metrik-Name angegeben${NC}"
        return 1
    fi
    
    local query_url="$prometheus_url/api/v1/query?query=$metric"
    
    if curl -s "$query_url" | jq . > /dev/null; then
        curl -s "$query_url" | jq .
    else
        echo -e "${RED}❌ Fehler beim Abrufen der Prometheus-Metriken${NC}"
    fi
}

# Funktion zum Anzeigen der Systemübersicht
system_overview() {
    echo -e "${BLUE}=== Systemübersicht ===${NC}"
    
    echo -e "${CYAN}Hostname:${NC} $(hostname)"
    echo -e "${CYAN}Kernel:${NC} $(uname -r)"
    echo -e "${CYAN}Uptime:${NC} $(uptime -p)"
    echo -e "${CYAN}CPU-Auslastung:${NC}"
    top -bn1 | head -n 3 | tail -n 2
    echo -e "${CYAN}Speichernutzung:${NC}"
    free -h | head -n 2
    echo -e "${CYAN}Festplattennutzung:${NC}"
    df -h / | head -n 2
    echo -e "${CYAN}Laufende Docker-Container:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "Docker ist nicht installiert oder läuft nicht"
}

# Funktion zum Anzeigen der Dienste-Übersicht
services_overview() {
    echo -e "${BLUE}=== Dienste-Übersicht ===${NC}"
    
    # MCP-Server Status
    if docker ps | grep -q "mcp-"; then
        echo -e "${GREEN}✅ MCP-Server (Docker):${NC} Läuft"
    else
        echo -e "${RED}❌ MCP-Server (Docker):${NC} Gestoppt"
    fi
    
    # n8n Status
    if docker ps | grep -q "n8n"; then
        echo -e "${GREEN}✅ n8n:${NC} Läuft"
    else
        echo -e "${RED}❌ n8n:${NC} Gestoppt"
    fi
    
    # Ollama Status
    if docker ps | grep -q "ollama"; then
        echo -e "${GREEN}✅ Ollama:${NC} Läuft"
    else
        echo -e "${RED}❌ Ollama:${NC} Gestoppt"
    fi
    
    # OpenHands Status
    if docker ps | grep -q "openhands"; then
        echo -e "${GREEN}✅ OpenHands:${NC} Läuft"
    else
        echo -e "${RED}❌ OpenHands:${NC} Gestoppt"
    fi
    
    # AppFlowy Status
    if docker ps | grep -q "appflowy"; then
        echo -e "${GREEN}✅ AppFlowy:${NC} Läuft"
    else
        echo -e "${RED}❌ AppFlowy:${NC} Gestoppt"
    fi
    
    # Llamafile Status
    if pgrep -f "llamafile" > /dev/null; then
        echo -e "${GREEN}✅ Llamafile:${NC} Läuft"
    else
        echo -e "${RED}❌ Llamafile:${NC} Gestoppt"
    fi
    
    # Web-UI Status
    if pgrep -f "npm.*start" > /dev/null && [ -d "$WEB_UI_DIR" ]; then
        echo -e "${GREEN}✅ Web-UI:${NC} Läuft"
    else
        echo -e "${RED}❌ Web-UI:${NC} Gestoppt"
    fi
}

# Funktion zum Anzeigen der Netzwerkübersicht
network_overview() {
    echo -e "${BLUE}=== Netzwerkübersicht ===${NC}"
    
    echo -e "${CYAN}Netzwerkschnittstellen:${NC}"
    ip -br addr
    
    echo -e "${CYAN}Offene Ports:${NC}"
    if command -v netstat > /dev/null; then
        netstat -tuln | grep LISTEN
    elif command -v ss > /dev/null; then
        ss -tuln | grep LISTEN
    else
        echo -e "${YELLOW}⚠️ Weder netstat noch ss ist verfügbar${NC}"
    fi
    
    echo -e "${CYAN}Docker-Netzwerke:${NC}"
    docker network ls 2>/dev/null || echo "Docker ist nicht installiert oder läuft nicht"
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
            echo -e "${RED}Unbekannte Aktion: $action${NC}"
            echo "Verfügbare Aktionen: check-service, get-logs, check-disk, check-memory, check-cpu, check-port, check-url, check-container, container-stats, check-prometheus, system-overview, services-overview, network-overview"
            return 1
            ;;
    esac
}

# Führe die Hauptfunktion aus, wenn das Skript direkt ausgeführt wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        echo -e "${RED}Keine Aktion angegeben${NC}"
        echo "Verwendung: $0 <Aktion> [Argumente...]"
        echo "Verfügbare Aktionen: check-service, get-logs, check-disk, check-memory, check-cpu, check-port, check-url, check-container, container-stats, check-prometheus, system-overview, services-overview, network-overview"
        exit 1
    fi
    
    main "$@"
fi
