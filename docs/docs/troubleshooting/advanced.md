# Erweiterte Fehlerbehebung

Diese Anleitung bietet erweiterte Fehlerbehebungstechniken für das Dev-Server-Workflow-System.

## Fehlerbehandlungssystem

Das Dev-Server-Workflow-System verwendet ein verbessertes Fehlerbehandlungssystem, das in `cli/error_handler.sh` implementiert ist. Dieses System bietet:

- Strikte Fehlerbehandlung mit `set -euo pipefail`
- Rollback-Mechanismen für fehlgeschlagene Operationen
- Detaillierte Fehlerprotokolle
- Einheitliche Fehlerbehandlungsstrategie

### Fehlerprotokolle

Fehlerprotokolle werden in der Datei `/workspace/Dev-Server-Workflow/logs/error.log` gespeichert. Sie können die Protokolle mit folgendem Befehl anzeigen:

```bash
cat /workspace/Dev-Server-Workflow/logs/error.log
```

Oder die letzten 50 Zeilen:

```bash
tail -n 50 /workspace/Dev-Server-Workflow/logs/error.log
```

### Fehlerbehandlungsfunktionen

Das Fehlerbehandlungssystem bietet verschiedene Funktionen zur Überprüfung von Bedingungen und zur Behandlung von Fehlern:

```bash
# Befehl überprüfen
check_command "docker" "Docker ist nicht installiert. Installieren Sie Docker mit: apt-get install docker.io"

# Datei überprüfen
check_file "/path/to/file" "true"  # true = Datei erstellen, wenn sie nicht existiert

# Verzeichnis überprüfen
check_directory "/path/to/dir" "true"  # true = Verzeichnis erstellen, wenn es nicht existiert

# Eingabe validieren
validate_input "input" "pattern" "Ungültiges Eingabeformat"

# Befehl mit Timeout ausführen
execute_with_timeout "5s" "curl http://localhost:5678"

# Container-Status überprüfen
check_container_running "n8n"

# Netzwerkverbindung überprüfen
check_network "localhost" "5678" "5"
```

## Häufige Probleme und Lösungen

### Docker-bezogene Probleme

#### Container starten nicht

**Problem**: Docker-Container starten nicht oder stürzen sofort ab.

**Lösung**:

1. Überprüfen Sie den Status der Container:

```bash
docker ps -a
```

2. Überprüfen Sie die Container-Logs:

```bash
docker logs <container-name>
```

3. Überprüfen Sie, ob die erforderlichen Ports verfügbar sind:

```bash
netstat -tuln | grep <port>
```

4. Überprüfen Sie, ob die erforderlichen Volumes existieren:

```bash
docker volume ls
```

5. Überprüfen Sie die Docker-Compose-Konfiguration:

```bash
docker compose -f <compose-file> config
```

#### Netzwerkprobleme

**Problem**: Container können nicht miteinander kommunizieren.

**Lösung**:

1. Überprüfen Sie, ob die Container im selben Netzwerk sind:

```bash
docker network inspect <network-name>
```

2. Überprüfen Sie, ob die Container die richtigen IP-Adressen haben:

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container-name>
```

3. Überprüfen Sie, ob die Ports korrekt zugeordnet sind:

```bash
docker port <container-name>
```

4. Testen Sie die Verbindung zwischen Containern:

```bash
docker exec <container-name> ping <other-container-name>
```

### n8n-bezogene Probleme

#### n8n ist nicht erreichbar

**Problem**: n8n ist nicht über den Browser erreichbar.

**Lösung**:

1. Überprüfen Sie, ob der n8n-Container läuft:

```bash
docker ps | grep n8n
```

2. Überprüfen Sie die n8n-Logs:

```bash
docker logs n8n
```

3. Überprüfen Sie, ob der Port korrekt zugeordnet ist:

```bash
docker port n8n
```

4. Testen Sie die Verbindung:

```bash
curl http://localhost:5678
```

5. Überprüfen Sie die Firewall-Einstellungen:

```bash
sudo ufw status
```

#### Workflow-Aktivierung schlägt fehl

**Problem**: n8n-Workflows können nicht aktiviert werden.

**Lösung**:

1. Überprüfen Sie, ob alle erforderlichen Credentials eingerichtet sind:

```bash
# Öffnen Sie die n8n-Weboberfläche und navigieren Sie zu Credentials
```

2. Überprüfen Sie die n8n-Logs auf spezifische Fehlermeldungen:

```bash
docker logs n8n
```

3. Überprüfen Sie, ob die API-Tokens gültig sind:

```bash
./cli/config_manager.sh get env .env GITHUB_TOKEN
```

4. Importieren Sie den Workflow erneut:

```bash
# Exportieren Sie den Workflow aus n8n und importieren Sie ihn erneut
```

### MCP-Server-Probleme

#### MCP-Server starten nicht

**Problem**: MCP-Server starten nicht oder stürzen sofort ab.

**Lösung**:

1. Überprüfen Sie den Status der MCP-Server:

```bash
docker ps | grep mcp
```

2. Überprüfen Sie die MCP-Server-Logs:

```bash
docker logs <mcp-server-name>
```

3. Überprüfen Sie die MCP-Server-Konfiguration:

```bash
./cli/config_manager.sh list json <mcp-server-config-file>
```

4. Starten Sie den MCP-Server neu:

```bash
./src/common/dependency_manager.sh restart <mcp-server-name>
```

5. Überprüfen Sie die Abhängigkeiten des MCP-Servers:

```bash
./src/common/dependency_manager.sh dependencies <mcp-server-name>
```

#### Verbindungsprobleme zwischen n8n und MCP-Servern

**Problem**: n8n kann nicht mit den MCP-Servern kommunizieren.

**Lösung**:

1. Überprüfen Sie, ob beide im selben Docker-Netzwerk sind:

```bash
docker network inspect dev-server-network
```

2. Überprüfen Sie die IP-Adressen der Container:

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' n8n
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <mcp-server-name>
```

3. Testen Sie die Verbindung:

```bash
docker exec n8n curl http://<mcp-server-ip>:<mcp-server-port>/health
```

4. Überprüfen Sie die Firewall-Einstellungen:

```bash
sudo ufw status
```

5. Überprüfen Sie die MCP-Server-Konfiguration in n8n:

```bash
# Öffnen Sie die n8n-Weboberfläche und überprüfen Sie die MCP-Server-Konfiguration
```

### Web-UI-Probleme

#### Web-UI ist nicht erreichbar

**Problem**: Die Web-UI ist nicht über den Browser erreichbar.

**Lösung**:

1. Überprüfen Sie, ob der Web-UI-Container läuft:

```bash
docker ps | grep web-ui
```

2. Überprüfen Sie die Web-UI-Logs:

```bash
docker logs web-ui
```

3. Überprüfen Sie, ob der Port korrekt zugeordnet ist:

```bash
docker port web-ui
```

4. Testen Sie die Verbindung:

```bash
curl http://localhost:8080
```

5. Überprüfen Sie die Firewall-Einstellungen:

```bash
sudo ufw status
```

#### Offline-Modus funktioniert nicht

**Problem**: Die Offline-Unterstützung für die Web-UI funktioniert nicht.

**Lösung**:

1. Überprüfen Sie, ob der Service Worker registriert ist:

```bash
# Öffnen Sie die Browser-Entwicklertools und navigieren Sie zu Application > Service Workers
```

2. Überprüfen Sie, ob die erforderlichen Assets im Cache gespeichert sind:

```bash
# Öffnen Sie die Browser-Entwicklertools und navigieren Sie zu Application > Cache Storage
```

3. Überprüfen Sie, ob die Offline-Seite korrekt geladen wird:

```bash
# Deaktivieren Sie die Netzwerkverbindung und laden Sie die Seite neu
```

4. Aktualisieren Sie den Service Worker:

```bash
# Öffnen Sie die Browser-Entwicklertools, navigieren Sie zu Application > Service Workers und klicken Sie auf "Unregister"
# Laden Sie die Seite neu, um den Service Worker erneut zu registrieren
```

### Konfigurationsprobleme

#### Konfigurationsdatei nicht gefunden

**Problem**: Konfigurationsdatei wird nicht gefunden.

**Lösung**:

1. Überprüfen Sie, ob die Konfigurationsdatei existiert:

```bash
ls -la <config-file>
```

2. Erstellen Sie die Konfigurationsdatei aus der Beispieldatei:

```bash
cp <example-config-file> <config-file>
```

3. Überprüfen Sie die Berechtigungen der Konfigurationsdatei:

```bash
chmod 644 <config-file>
```

#### Ungültige Konfigurationswerte

**Problem**: Konfigurationswerte sind ungültig oder fehlen.

**Lösung**:

1. Überprüfen Sie die Konfigurationswerte:

```bash
./cli/config_manager.sh list env <config-file>
```

2. Setzen Sie die fehlenden oder ungültigen Werte:

```bash
./cli/config_manager.sh save env <config-file> <key> <value>
```

3. Validieren Sie die Konfiguration:

```bash
./cli/config_manager.sh validate env <config-file>
```

### Dependency Management Probleme

#### Abhängigkeitsprobleme

**Problem**: Komponenten starten nicht in der richtigen Reihenfolge.

**Lösung**:

1. Überprüfen Sie die Abhängigkeiten:

```bash
./src/common/dependency_manager.sh list
```

2. Überprüfen Sie die Abhängigkeiten einer bestimmten Komponente:

```bash
./src/common/dependency_manager.sh dependencies <component>
```

3. Überprüfen Sie die abhängigen Komponenten:

```bash
./src/common/dependency_manager.sh dependents <component>
```

4. Starten Sie die Komponente und ihre Abhängigkeiten:

```bash
./src/common/dependency_manager.sh start <component>
```

5. Stoppen Sie die Komponente und ihre abhängigen Komponenten:

```bash
./src/common/dependency_manager.sh stop <component>
```

### Monitoring-Probleme

#### Prometheus-Exporter startet nicht

**Problem**: Der Prometheus-Exporter startet nicht.

**Lösung**:

1. Überprüfen Sie, ob Python und die erforderlichen Pakete installiert sind:

```bash
python --version
pip list | grep prometheus-client
```

2. Installieren Sie die erforderlichen Pakete:

```bash
pip install prometheus-client psutil docker
```

3. Überprüfen Sie die Prometheus-Exporter-Logs:

```bash
cat /workspace/Dev-Server-Workflow/logs/prometheus_exporter.log
```

4. Starten Sie den Prometheus-Exporter manuell:

```bash
python src/monitoring/prometheus_exporter.py --debug
```

#### Metriken werden nicht angezeigt

**Problem**: Metriken werden nicht in Prometheus oder Grafana angezeigt.

**Lösung**:

1. Überprüfen Sie, ob der Prometheus-Exporter läuft:

```bash
ps aux | grep prometheus_exporter
```

2. Überprüfen Sie, ob Prometheus läuft:

```bash
docker ps | grep prometheus
```

3. Überprüfen Sie, ob Grafana läuft:

```bash
docker ps | grep grafana
```

4. Testen Sie den Prometheus-Exporter:

```bash
curl http://localhost:9090/metrics
```

5. Überprüfen Sie die Prometheus-Konfiguration:

```bash
docker exec prometheus cat /etc/prometheus/prometheus.yml
```

## Erweiterte Diagnose

### Systemdiagnose

Führen Sie eine vollständige Systemdiagnose durch:

```bash
./dev-server-cli.sh diagnose
```

Dies führt folgende Überprüfungen durch:

1. Überprüfung der Systemvoraussetzungen
2. Überprüfung der Docker-Installation
3. Überprüfung der Konfigurationsdateien
4. Überprüfung der Container-Status
5. Überprüfung der Netzwerkverbindungen
6. Überprüfung der Logs
7. Überprüfung der Abhängigkeiten

### Komponentendiagnose

Führen Sie eine Diagnose für eine bestimmte Komponente durch:

```bash
./dev-server-cli.sh diagnose <component>
```

### Protokollanalyse

Analysieren Sie die Protokolle auf Fehler:

```bash
./dev-server-cli.sh logs-analyze
```

Dies analysiert die Protokolle aller Komponenten und zeigt häufige Fehler und Warnungen an.

### Leistungsanalyse

Analysieren Sie die Leistung des Systems:

```bash
./dev-server-cli.sh performance
```

Dies zeigt Leistungsmetriken wie CPU-Auslastung, Speicherverbrauch und Netzwerkverkehr an.

## Wiederherstellung

### Backup wiederherstellen

Wenn alle anderen Methoden fehlschlagen, können Sie ein Backup wiederherstellen:

```bash
./dev-server-cli.sh restore <backup-file>
```

### System zurücksetzen

Setzen Sie das System auf die Standardeinstellungen zurück:

```bash
./dev-server-cli.sh reset
```

Dies stoppt alle Container, löscht alle Daten und setzt die Konfiguration auf die Standardwerte zurück.

### Neuinstallation

Wenn alle anderen Methoden fehlschlagen, können Sie das System neu installieren:

```bash
# Alle Container stoppen und entfernen
./dev-server-cli.sh stop-all
docker compose down -v

# Repository neu klonen
cd ..
rm -rf Dev-Server-Workflow
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow

# System neu installieren
cp .env.example .env
# Bearbeiten Sie die .env-Datei
./dev-server-cli.sh start-all
```

## Weitere Ressourcen

- [Installationsanleitung](../installation/comprehensive-guide.md)
- [Konfigurationsanleitung](../configuration/index.md)
- [Fehlerbehandlungsanleitung](../troubleshooting/index.md)
- [Docker-Dokumentation](https://docs.docker.com/)
- [n8n-Dokumentation](https://docs.n8n.io/)
- [Prometheus-Dokumentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana-Dokumentation](https://grafana.com/docs/)