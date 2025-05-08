#!/bin/bash

# Monitoring-Management-Funktionen für die Dev-Server CLI

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

# Funktion zum Starten des Monitoring-Stacks
start_monitoring() {
    echo -e "${BLUE}=== Starte Monitoring-Stack ===${NC}"
    
    # Überprüfe, ob Docker installiert ist
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
        return 1
    fi
    
    # Überprüfe, ob Docker Compose installiert ist
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose.${NC}"
        return 1
    fi
    
    # Erstelle das Monitoring-Verzeichnis
    local monitoring_dir="${DATA_DIR}/monitoring"
    mkdir -p "$monitoring_dir"
    
    # Erstelle die Docker Compose-Datei
    local compose_file="${monitoring_dir}/docker-compose.yml"
    
    cat > "$compose_file" << EOF
version: '3'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ${monitoring_dir}/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - ${DOCKER_NETWORK}

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - ${DOCKER_NETWORK}

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    restart: always
    ports:
      - "9093:9093"
    volumes:
      - ${monitoring_dir}/alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    networks:
      - ${DOCKER_NETWORK}

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: always
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - ${DOCKER_NETWORK}

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    restart: always
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    networks:
      - ${DOCKER_NETWORK}

networks:
  ${DOCKER_NETWORK}:
    external: true

volumes:
  prometheus_data:
  grafana_data:
EOF
    
    # Erstelle das Prometheus-Konfigurationsverzeichnis
    mkdir -p "${monitoring_dir}/prometheus"
    
    # Erstelle die Prometheus-Konfigurationsdatei
    cat > "${monitoring_dir}/prometheus/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'docker'
    static_configs:
      - targets: ['cadvisor:8080']
EOF
    
    # Erstelle das Alertmanager-Konfigurationsverzeichnis
    mkdir -p "${monitoring_dir}/alertmanager"
    
    # Erstelle die Alertmanager-Konfigurationsdatei
    cat > "${monitoring_dir}/alertmanager/alertmanager.yml" << EOF
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF
    
    # Erstelle das Prometheus-Rules-Verzeichnis
    mkdir -p "${monitoring_dir}/prometheus/rules"
    
    # Erstelle die Prometheus-Rules-Datei
    cat > "${monitoring_dir}/prometheus/rules/alert.yml" << EOF
groups:
  - name: example
    rules:
      - alert: HighCPULoad
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU load (instance {{ \$labels.instance }})"
          description: "CPU load is > 80%\n  VALUE = {{ \$value }}\n  LABELS: {{ \$labels }}"

      - alert: HighMemoryLoad
        expr: (node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory load (instance {{ \$labels.instance }})"
          description: "Memory load is > 80%\n  VALUE = {{ \$value }}\n  LABELS: {{ \$labels }}"

      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes{fstype=~"ext4|xfs"} - node_filesystem_free_bytes{fstype=~"ext4|xfs"}) / node_filesystem_size_bytes{fstype=~"ext4|xfs"} * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage (instance {{ \$labels.instance }})"
          description: "Disk usage is > 80%\n  VALUE = {{ \$value }}\n  LABELS: {{ \$labels }}"
EOF
    
    # Erstelle das Docker-Netzwerk, falls es nicht existiert
    if ! docker network ls | grep -q "$DOCKER_NETWORK"; then
        echo -e "${YELLOW}Erstelle Docker-Netzwerk $DOCKER_NETWORK...${NC}"
        docker network create "$DOCKER_NETWORK"
    fi
    
    # Starte den Monitoring-Stack
    echo -e "${YELLOW}Starte Monitoring-Stack...${NC}"
    docker-compose -f "$compose_file" up -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Monitoring-Stack erfolgreich gestartet${NC}"
        echo -e "${BLUE}Prometheus:${NC} http://localhost:9090"
        echo -e "${BLUE}Grafana:${NC} http://localhost:3000 (admin/admin)"
        echo -e "${BLUE}Alertmanager:${NC} http://localhost:9093"
        echo -e "${BLUE}Node Exporter:${NC} http://localhost:9100"
        echo -e "${BLUE}cAdvisor:${NC} http://localhost:8080"
    else
        echo -e "${RED}❌ Fehler beim Starten des Monitoring-Stacks${NC}"
        return 1
    fi
}

# Funktion zum Stoppen des Monitoring-Stacks
stop_monitoring() {
    echo -e "${BLUE}=== Stoppe Monitoring-Stack ===${NC}"
    
    # Überprüfe, ob Docker installiert ist
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
        return 1
    fi
    
    # Überprüfe, ob Docker Compose installiert ist
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose ist nicht installiert. Bitte installieren Sie Docker Compose.${NC}"
        return 1
    fi
    
    # Monitoring-Verzeichnis
    local monitoring_dir="${DATA_DIR}/monitoring"
    local compose_file="${monitoring_dir}/docker-compose.yml"
    
    # Überprüfe, ob die Docker Compose-Datei existiert
    if [ ! -f "$compose_file" ]; then
        echo -e "${RED}❌ Docker Compose-Datei nicht gefunden: $compose_file${NC}"
        return 1
    fi
    
    # Stoppe den Monitoring-Stack
    echo -e "${YELLOW}Stoppe Monitoring-Stack...${NC}"
    docker-compose -f "$compose_file" down
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Monitoring-Stack erfolgreich gestoppt${NC}"
    else
        echo -e "${RED}❌ Fehler beim Stoppen des Monitoring-Stacks${NC}"
        return 1
    fi
}

# Funktion zum Neustarten des Monitoring-Stacks
restart_monitoring() {
    echo -e "${BLUE}=== Starte Monitoring-Stack neu ===${NC}"
    
    stop_monitoring
    sleep 2
    start_monitoring
}

# Funktion zum Anzeigen der Monitoring-Logs
show_monitoring_logs() {
    local service="$1"
    local lines="${2:-100}"
    
    echo -e "${BLUE}=== Zeige Monitoring-Logs für $service ===${NC}"
    
    # Überprüfe, ob Docker installiert ist
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
        return 1
    fi
    
    # Überprüfe, ob der Container existiert
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$service$"; then
        echo -e "${RED}❌ Container nicht gefunden: $service${NC}"
        echo -e "${YELLOW}Verfügbare Container:${NC}"
        docker ps -a --format '{{.Names}}'
        return 1
    fi
    
    # Zeige die Logs an
    docker logs --tail "$lines" "$service"
}

# Funktion zum Öffnen der Monitoring-Oberflächen im Browser
open_monitoring_ui() {
    local service="$1"
    
    echo -e "${BLUE}=== Öffne Monitoring-Oberfläche für $service ===${NC}"
    
    case "$service" in
        "prometheus")
            echo -e "${YELLOW}Öffne Prometheus...${NC}"
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:9090"
            elif command -v open &> /dev/null; then
                open "http://localhost:9090"
            else
                echo -e "${RED}❌ Kann Browser nicht öffnen. Bitte öffnen Sie http://localhost:9090 manuell.${NC}"
                return 1
            fi
            ;;
        "grafana")
            echo -e "${YELLOW}Öffne Grafana...${NC}"
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:3000"
            elif command -v open &> /dev/null; then
                open "http://localhost:3000"
            else
                echo -e "${RED}❌ Kann Browser nicht öffnen. Bitte öffnen Sie http://localhost:3000 manuell.${NC}"
                return 1
            fi
            ;;
        "alertmanager")
            echo -e "${YELLOW}Öffne Alertmanager...${NC}"
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:9093"
            elif command -v open &> /dev/null; then
                open "http://localhost:9093"
            else
                echo -e "${RED}❌ Kann Browser nicht öffnen. Bitte öffnen Sie http://localhost:9093 manuell.${NC}"
                return 1
            fi
            ;;
        "cadvisor")
            echo -e "${YELLOW}Öffne cAdvisor...${NC}"
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:8080"
            elif command -v open &> /dev/null; then
                open "http://localhost:8080"
            else
                echo -e "${RED}❌ Kann Browser nicht öffnen. Bitte öffnen Sie http://localhost:8080 manuell.${NC}"
                return 1
            fi
            ;;
        "node-exporter")
            echo -e "${YELLOW}Öffne Node Exporter...${NC}"
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:9100"
            elif command -v open &> /dev/null; then
                open "http://localhost:9100"
            else
                echo -e "${RED}❌ Kann Browser nicht öffnen. Bitte öffnen Sie http://localhost:9100 manuell.${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}❌ Unbekannter Dienst: $service${NC}"
            echo -e "${YELLOW}Verfügbare Dienste:${NC} prometheus, grafana, alertmanager, cadvisor, node-exporter"
            return 1
            ;;
    esac
}

# Funktion zum Anzeigen des Monitoring-Status
show_monitoring_status() {
    echo -e "${BLUE}=== Monitoring-Status ===${NC}"
    
    # Überprüfe, ob Docker installiert ist
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker ist nicht installiert. Bitte installieren Sie Docker.${NC}"
        return 1
    fi
    
    # Zeige den Status der Monitoring-Container an
    echo -e "${YELLOW}Monitoring-Container:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "prometheus|grafana|alertmanager|cadvisor|node-exporter" || echo -e "${RED}❌ Keine Monitoring-Container gefunden${NC}"
}

# Hauptfunktion
main() {
    local action="$1"
    shift
    local args="$@"
    
    case "$action" in
        "start")
            start_monitoring
            ;;
        "stop")
            stop_monitoring
            ;;
        "restart")
            restart_monitoring
            ;;
        "logs")
            if [ -z "$args" ]; then
                echo -e "${RED}❌ Kein Dienst angegeben${NC}"
                echo -e "${YELLOW}Verfügbare Dienste:${NC} prometheus, grafana, alertmanager, cadvisor, node-exporter"
                return 1
            fi
            show_monitoring_logs "$args"
            ;;
        "open")
            if [ -z "$args" ]; then
                echo -e "${RED}❌ Kein Dienst angegeben${NC}"
                echo -e "${YELLOW}Verfügbare Dienste:${NC} prometheus, grafana, alertmanager, cadvisor, node-exporter"
                return 1
            fi
            open_monitoring_ui "$args"
            ;;
        "status")
            show_monitoring_status
            ;;
        *)
            echo -e "${RED}❌ Unbekannte Aktion: $action${NC}"
            echo -e "${YELLOW}Verfügbare Aktionen:${NC} start, stop, restart, logs, open, status"
            return 1
            ;;
    esac
}

# Führe die Hauptfunktion aus, wenn das Skript direkt ausgeführt wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        echo -e "${RED}❌ Keine Aktion angegeben${NC}"
        echo -e "${YELLOW}Verfügbare Aktionen:${NC} start, stop, restart, logs, open, status"
        exit 1
    fi
    
    main "$@"
fi
