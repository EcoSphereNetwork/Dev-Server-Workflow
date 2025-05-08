# Prometheus Exporter

Der Prometheus Exporter ist ein Python-Skript, das Metriken von den MCP-Servern und anderen Komponenten des Dev-Server-Workflow-Systems sammelt und für Prometheus exportiert.

## Überblick

Der Prometheus Exporter sammelt folgende Arten von Metriken:

- **Systemmetriken**: CPU-Auslastung, Speicherverbrauch, Festplattennutzung, Netzwerkverkehr
- **Docker-Metriken**: Container-Status, Container-CPU-Auslastung, Container-Speicherverbrauch, Container-Netzwerkverkehr
- **MCP-Server-Metriken**: Anfragen, Fehler, Antwortzeiten, Tool-Aufrufe, Gesundheitsstatus
- **n8n-Metriken**: Workflow-Ausführungen, Workflow-Fehler, Workflow-Ausführungszeiten

## Installation

Der Prometheus Exporter ist Teil des Dev-Server-Workflow-Systems und wird mit dem System installiert. Er benötigt folgende Python-Pakete:

- `prometheus_client`: Für die Prometheus-Integration
- `psutil`: Für Systemmetriken
- `docker`: Für Docker-Metriken

Diese Pakete werden automatisch installiert, wenn Sie die Abhängigkeiten des Systems installieren:

```bash
pip install -r requirements.txt
```

Alternativ können Sie die Pakete manuell installieren:

```bash
pip install prometheus_client psutil docker
```

## Verwendung

### Starten des Exporters

Sie können den Prometheus Exporter mit folgendem Befehl starten:

```bash
python src/monitoring/prometheus_exporter.py
```

Der Exporter startet einen HTTP-Server auf Port 9090, der die Metriken für Prometheus bereitstellt.

### Konfigurationsoptionen

Der Prometheus Exporter unterstützt folgende Kommandozeilenoptionen:

- `--port PORT`: Port für den HTTP-Server (Standard: 9090)
- `--interval INTERVAL`: Intervall in Sekunden zwischen Metriksammlungen (Standard: 15)
- `--debug`: Debug-Logging aktivieren

Beispiel:

```bash
python src/monitoring/prometheus_exporter.py --port 9091 --interval 30 --debug
```

### Metriken anzeigen

Sie können die Metriken mit folgendem Befehl anzeigen:

```bash
curl http://localhost:9090/metrics
```

## Metriken

### Systemmetriken

| Metrik | Beschreibung | Typ |
|--------|--------------|-----|
| `system_cpu_usage` | CPU-Auslastung in Prozent | Gauge |
| `system_memory_usage` | Speicherverbrauch in Prozent | Gauge |
| `system_disk_usage` | Festplattennutzung in Prozent | Gauge |
| `system_network_sent` | Gesendete Bytes | Gauge |
| `system_network_received` | Empfangene Bytes | Gauge |

### Docker-Metriken

| Metrik | Beschreibung | Typ | Labels |
|--------|--------------|-----|--------|
| `docker_container_count` | Anzahl der laufenden Docker-Container | Gauge | - |
| `docker_container_cpu` | Container-CPU-Auslastung in Prozent | Gauge | `container` |
| `docker_container_memory` | Container-Speicherverbrauch in Bytes | Gauge | `container` |
| `docker_container_network_in` | Container-Netzwerkverkehr (eingehend) in Bytes | Gauge | `container` |
| `docker_container_network_out` | Container-Netzwerkverkehr (ausgehend) in Bytes | Gauge | `container` |
| `docker_container_status` | Container-Status (1=running, 0=stopped) | Gauge | `container` |

### MCP-Server-Metriken

| Metrik | Beschreibung | Typ | Labels |
|--------|--------------|-----|--------|
| `mcp_server_request_count` | Anzahl der Anfragen an den MCP-Server | Counter | `server`, `endpoint` |
| `mcp_server_error_count` | Anzahl der Fehler vom MCP-Server | Counter | `server`, `endpoint` |
| `mcp_server_response_time` | Antwortzeit des MCP-Servers in Sekunden | Summary | `server`, `endpoint` |
| `mcp_server_tool_calls` | Anzahl der Tool-Aufrufe an den MCP-Server | Counter | `server`, `tool` |
| `mcp_server_health` | Gesundheitsstatus des MCP-Servers (1=healthy, 0=unhealthy) | Gauge | `server` |

### n8n-Metriken

| Metrik | Beschreibung | Typ | Labels |
|--------|--------------|-----|--------|
| `n8n_workflow_executions` | Anzahl der n8n-Workflow-Ausführungen | Counter | `workflow` |
| `n8n_workflow_errors` | Anzahl der n8n-Workflow-Fehler | Counter | `workflow` |
| `n8n_workflow_execution_time` | Ausführungszeit des n8n-Workflows in Sekunden | Summary | `workflow` |

## Integration mit Prometheus

Um den Prometheus Exporter mit Prometheus zu integrieren, fügen Sie folgende Konfiguration zu Ihrer `prometheus.yml`-Datei hinzu:

```yaml
scrape_configs:
  - job_name: 'dev-server-workflow'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']
```

## Integration mit Grafana

Um die Metriken in Grafana zu visualisieren, fügen Sie Prometheus als Datenquelle hinzu:

1. Öffnen Sie Grafana (http://localhost:3000)
2. Gehen Sie zu "Configuration" > "Data Sources"
3. Klicken Sie auf "Add data source"
4. Wählen Sie "Prometheus"
5. Geben Sie die URL des Prometheus-Servers ein (http://localhost:9090)
6. Klicken Sie auf "Save & Test"

Anschließend können Sie Dashboards erstellen, die die Metriken visualisieren.

### Beispiel-Dashboard

Ein Beispiel-Dashboard für das Dev-Server-Workflow-System könnte folgende Panels enthalten:

- **Systemübersicht**: CPU-Auslastung, Speicherverbrauch, Festplattennutzung, Netzwerkverkehr
- **Container-Übersicht**: Anzahl der laufenden Container, Container-Status
- **Container-Details**: CPU-Auslastung, Speicherverbrauch, Netzwerkverkehr pro Container
- **MCP-Server-Übersicht**: Gesundheitsstatus, Anfragen pro Sekunde, Fehlerrate
- **MCP-Server-Details**: Antwortzeiten, Tool-Aufrufe pro Server
- **n8n-Übersicht**: Workflow-Ausführungen, Workflow-Fehler, Workflow-Ausführungszeiten

## Fehlerbehebung

### Exporter startet nicht

Wenn der Prometheus Exporter nicht startet, überprüfen Sie Folgendes:

1. Überprüfen Sie, ob Python und die erforderlichen Pakete installiert sind:

```bash
python --version
pip list | grep prometheus-client
```

2. Installieren Sie die erforderlichen Pakete:

```bash
pip install prometheus_client psutil docker
```

3. Überprüfen Sie die Logs:

```bash
cat /workspace/Dev-Server-Workflow/logs/monitoring.log
```

4. Starten Sie den Exporter im Debug-Modus:

```bash
python src/monitoring/prometheus_exporter.py --debug
```

### Metriken werden nicht angezeigt

Wenn die Metriken nicht angezeigt werden, überprüfen Sie Folgendes:

1. Überprüfen Sie, ob der Exporter läuft:

```bash
ps aux | grep prometheus_exporter
```

2. Überprüfen Sie, ob der Exporter auf dem richtigen Port lauscht:

```bash
netstat -tuln | grep 9090
```

3. Testen Sie den Zugriff auf die Metriken:

```bash
curl http://localhost:9090/metrics
```

4. Überprüfen Sie die Logs:

```bash
cat /workspace/Dev-Server-Workflow/logs/monitoring.log
```

### Docker-Metriken werden nicht angezeigt

Wenn die Docker-Metriken nicht angezeigt werden, überprüfen Sie Folgendes:

1. Überprüfen Sie, ob der Docker-Client initialisiert werden kann:

```bash
python -c "import docker; client = docker.from_env(); print(client.containers.list())"
```

2. Überprüfen Sie, ob der Benutzer, der den Exporter ausführt, Zugriff auf den Docker-Socket hat:

```bash
ls -la /var/run/docker.sock
```

3. Fügen Sie den Benutzer zur Docker-Gruppe hinzu:

```bash
sudo usermod -aG docker $USER
```

### MCP-Server-Metriken werden nicht angezeigt

Wenn die MCP-Server-Metriken nicht angezeigt werden, überprüfen Sie Folgendes:

1. Überprüfen Sie, ob die MCP-Server laufen:

```bash
docker ps | grep mcp
```

2. Überprüfen Sie, ob die MCP-Server erreichbar sind:

```bash
curl http://localhost:3333/health
```

3. Überprüfen Sie die Logs der MCP-Server:

```bash
docker logs desktop-commander-mcp
```

## Erweiterte Konfiguration

### Anpassen der gesammelten Metriken

Sie können die gesammelten Metriken anpassen, indem Sie die Datei `src/monitoring/prometheus_exporter.py` bearbeiten. Die Metriken werden in den folgenden Abschnitten definiert:

- **Systemmetriken**: `# Define metrics` > `# System metrics`
- **Docker-Metriken**: `# Define metrics` > `# Docker metrics`
- **MCP-Server-Metriken**: `# Define metrics` > `# MCP server metrics`
- **n8n-Metriken**: `# Define metrics` > `# n8n metrics`

### Anpassen des Sammelintervalls

Sie können das Sammelintervall anpassen, indem Sie die Option `--interval` beim Starten des Exporters angeben:

```bash
python src/monitoring/prometheus_exporter.py --interval 30
```

Alternativ können Sie das Sammelintervall in der Datei `src/monitoring/prometheus_exporter.py` ändern:

```python
def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Prometheus Exporter for Dev-Server-Workflow')
    parser.add_argument('--port', type=int, default=9090, help='Port to expose metrics on')
    parser.add_argument('--interval', type=int, default=30, help='Interval in seconds between metric collections')  # Hier auf 30 Sekunden geändert
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # ...
```

### Anpassen des Ports

Sie können den Port anpassen, indem Sie die Option `--port` beim Starten des Exporters angeben:

```bash
python src/monitoring/prometheus_exporter.py --port 9091
```

Alternativ können Sie den Port in der Datei `src/monitoring/prometheus_exporter.py` ändern:

```python
def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Prometheus Exporter for Dev-Server-Workflow')
    parser.add_argument('--port', type=int, default=9091, help='Port to expose metrics on')  # Hier auf 9091 geändert
    parser.add_argument('--interval', type=int, default=15, help='Interval in seconds between metric collections')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # ...
```

## Weitere Ressourcen

- [Prometheus-Dokumentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana-Dokumentation](https://grafana.com/docs/)
- [prometheus_client-Dokumentation](https://github.com/prometheus/client_python)
- [psutil-Dokumentation](https://psutil.readthedocs.io/en/latest/)
- [docker-py-Dokumentation](https://docker-py.readthedocs.io/en/stable/)