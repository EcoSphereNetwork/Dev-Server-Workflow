#!/bin/bash

# Skript zum Sammeln von Systeminformationen
# Erstellt von Claude am $(date)

# Erstelle einen Ergebnisordner, falls er nicht existiert
OUTPUT_DIR="system_info_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "Sammle Systeminformationen. Bitte warten..."
echo "Ergebnisse werden im Ordner $OUTPUT_DIR gespeichert."

# Funktion zum Ausführen eines Befehls und Speichern der Ausgabe
run_command() {
    local cmd="$1"
    local output_file="$2"
    
    echo "Führe aus: $cmd"
    echo "# Befehl: $cmd" > "$OUTPUT_DIR/$output_file"
    echo "# Ausgeführt am: $(date)" >> "$OUTPUT_DIR/$output_file"
    echo "# ------------------------------" >> "$OUTPUT_DIR/$output_file"
    
    # Führe den Befehl aus und leite die Ausgabe in die Datei um, auch wenn Fehler auftreten
    bash -c "$cmd" >> "$OUTPUT_DIR/$output_file" 2>&1 || echo "Fehler beim Ausführen von: $cmd" >> "$OUTPUT_DIR/$output_file"
    
    echo "Fertig: $output_file"
}

# Systeminformationen
run_command "cat /etc/os-release" "01_os_release.txt"
run_command "uname -a" "02_uname.txt"
run_command "hostname" "03_hostname.txt"
run_command "uptime" "04_uptime.txt"

# Docker-Informationen
run_command "docker --version" "05_docker_version.txt"
run_command "docker-compose --version" "06_docker_compose_version.txt"
run_command "docker info" "07_docker_info.txt"
run_command "docker ps -a" "08_docker_containers.txt"
run_command "docker images" "09_docker_images.txt"
run_command "docker network ls" "10_docker_networks.txt"
run_command "docker volume ls" "11_docker_volumes.txt"

# Docker-Compose-Dateien
run_command "cat docker-compose.yml 2>/dev/null || echo 'Datei nicht gefunden'" "12_docker_compose_yml.txt"
run_command "cat docker-mcp-servers/docker-compose.yml 2>/dev/null || echo 'Datei nicht gefunden'" "13_docker_mcp_servers_compose.txt"
run_command "find . -name 'docker-compose*.yml' -type f | xargs cat 2>/dev/null || echo 'Keine Docker-Compose-Dateien gefunden'" "14_all_docker_compose_files.txt"

# Netzwerkinformationen
run_command "ip addr" "15_ip_addr.txt"
run_command "ip route" "16_ip_route.txt"
run_command "sudo ss -tulpn" "17_open_ports.txt"
run_command "sudo netstat -tulpn 2>/dev/null || echo 'netstat nicht installiert'" "18_netstat.txt"
run_command "sudo lsof -i -P -n" "19_lsof_network.txt"
run_command "sudo lsof -i :8080" "20_port_8080_usage.txt"
run_command "sudo fuser 8080/tcp 2>/dev/null || echo 'fuser nicht installiert oder Port nicht belegt'" "21_fuser_8080.txt"

# Apache-Informationen
run_command "which apache2 2>/dev/null && apache2 -v || echo 'Apache nicht installiert'" "22_apache_version.txt"
run_command "sudo systemctl status apache2 2>/dev/null || echo 'Apache nicht installiert oder systemctl nicht verfügbar'" "23_apache_status.txt"
run_command "ls -la /etc/apache2/sites-enabled/ 2>/dev/null || echo 'Apache-Konfigurationsordner nicht gefunden'" "24_apache_sites.txt"
run_command "sudo cat /etc/apache2/sites-enabled/* 2>/dev/null || echo 'Keine Apache-Konfigurationsdateien gefunden'" "25_apache_config.txt"
run_command "sudo tail -n 50 /var/log/apache2/error.log 2>/dev/null || echo 'Apache-Fehlerlog nicht gefunden'" "26_apache_error_log.txt"
run_command "sudo tail -n 50 /var/log/apache2/access.log 2>/dev/null || echo 'Apache-Zugriffslog nicht gefunden'" "27_apache_access_log.txt"

# Nginx-Informationen (falls vorhanden)
run_command "which nginx 2>/dev/null && nginx -v || echo 'Nginx nicht installiert'" "28_nginx_version.txt"
run_command "sudo systemctl status nginx 2>/dev/null || echo 'Nginx nicht installiert oder systemctl nicht verfügbar'" "29_nginx_status.txt"
run_command "ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo 'Nginx-Konfigurationsordner nicht gefunden'" "30_nginx_sites.txt"
run_command "sudo cat /etc/nginx/sites-enabled/* 2>/dev/null || echo 'Keine Nginx-Konfigurationsdateien gefunden'" "31_nginx_config.txt"

# Firewall-Informationen
run_command "sudo ufw status 2>/dev/null || echo 'UFW nicht installiert'" "32_ufw_status.txt"
run_command "sudo iptables -L -n 2>/dev/null || echo 'iptables nicht verfügbar'" "33_iptables.txt"

# Systemdienste
run_command "sudo systemctl list-units --type=service --state=running" "34_running_services.txt"
run_command "sudo systemctl list-unit-files --state=enabled" "35_enabled_services.txt"

# Python-Umgebung
run_command "python3 --version" "36_python_version.txt"
run_command "pip3 list" "37_pip_packages.txt"

# Docker-Container-Logs
run_command "docker logs mcp-inspector 2>&1 || echo 'Container nicht gefunden'" "38_mcp_inspector_logs.txt"
run_command "docker logs mcp-github 2>&1 || echo 'Container nicht gefunden'" "39_mcp_github_logs.txt"
run_command "docker logs mcp-puppeteer 2>&1 || echo 'Container nicht gefunden'" "40_mcp_puppeteer_logs.txt"
run_command "docker logs mcp-filesystem 2>&1 || echo 'Container nicht gefunden'" "41_mcp_filesystem_logs.txt"

# N8N-Integration
run_command "cat scripts/integrate-mcp-with-n8n.py 2>/dev/null || echo 'Datei nicht gefunden'" "42_n8n_integration_script.txt"
run_command "cat .env 2>/dev/null || echo 'Datei nicht gefunden'" "43_env_file.txt"

# Fehlerhafte Python-Skripte
run_command "cat scripts/test-mcp-servers.py 2>/dev/null || echo 'Datei nicht gefunden'" "44_test_mcp_servers_script.txt"

# DNS-Informationen
run_command "cat /etc/hosts" "45_hosts_file.txt"
run_command "cat /etc/resolv.conf" "46_resolv_conf.txt"
run_command "dig ecospherenet.work || echo 'dig nicht installiert'" "47_dig_domain.txt"
run_command "host ecospherenet.work || echo 'host nicht installiert'" "48_host_domain.txt"
run_command "host n8n.ecospherenet.work || echo 'host nicht installiert'" "49_host_n8n.txt"

# Ressourcennutzung
run_command "free -h" "50_memory_usage.txt"
run_command "df -h" "51_disk_usage.txt"
run_command "top -n 1 -b" "52_top_processes.txt"

# Webserver-Test
run_command "curl -I http://localhost:8080 2>/dev/null || echo 'curl nicht installiert oder Port nicht erreichbar'" "53_curl_localhost_8080.txt"

# Erstelle eine Zusammenfassung
echo "# Zusammenfassung der gesammelten Informationen" > "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "# Erstellt am: $(date)" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "# ------------------------------" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

echo "## Betriebssystem" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
grep -e "^PRETTY_NAME=" "$OUTPUT_DIR/01_os_release.txt" | cut -d'"' -f2 >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

echo "## Kernel" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
cat "$OUTPUT_DIR/02_uname.txt" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

echo "## Docker-Version" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
cat "$OUTPUT_DIR/05_docker_version.txt" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

echo "## Laufende Docker-Container" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
grep -v "CONTAINER ID" "$OUTPUT_DIR/08_docker_containers.txt" | wc -l >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

echo "## Offene Ports (Top 10)" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
grep -v "^#" "$OUTPUT_DIR/17_open_ports.txt" | head -10 >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

echo "## Speichernutzung" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
grep "Mem:" "$OUTPUT_DIR/50_memory_usage.txt" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

echo "## Festplattennutzung" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
grep -v "^Filesystem" "$OUTPUT_DIR/51_disk_usage.txt" | grep -v "^tmpfs" | grep -v "^udev" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

echo "## Probleme mit Port 8080" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
cat "$OUTPUT_DIR/20_port_8080_usage.txt" >> "$OUTPUT_DIR/00_zusammenfassung.txt"
echo "" >> "$OUTPUT_DIR/00_zusammenfassung.txt"

# Finales Ergebnis
echo ""
echo "Alle Informationen wurden erfolgreich gesammelt und im Ordner $OUTPUT_DIR gespeichert."
echo "Du kannst die Zusammenfassung mit folgendem Befehl anzeigen:"
echo "  cat $OUTPUT_DIR/00_zusammenfassung.txt"
echo ""
