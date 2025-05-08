# MCP-Server-Überwachung

Diese Dokumentation beschreibt die Überwachungslösung für die MCP-Server im Dev-Server-Workflow-Projekt.

## Übersicht

Die Überwachungslösung basiert auf Prometheus und Grafana und ermöglicht die Überwachung der MCP-Server in Echtzeit. Sie bietet Einblicke in den Zustand, die Leistung und die Ressourcennutzung der MCP-Server.

## Komponenten

Die Überwachungslösung besteht aus den folgenden Komponenten:

1. **Prometheus**: Ein Open-Source-Überwachungs- und Alerting-System, das Metriken von den MCP-Servern sammelt und speichert.
2. **Grafana**: Ein Open-Source-Visualisierungstool, das die von Prometheus gesammelten Metriken in Dashboards darstellt.
3. **Node Exporter**: Ein Prometheus-Exporter, der System-Metriken vom Host-System sammelt.
4. **cAdvisor**: Ein Container-Monitoring-Tool, das Metriken von Docker-Containern sammelt.

## Installation

### Voraussetzungen

- Docker und Docker Compose
- Laufende MCP-Server

### Automatische Installation

Die einfachste Methode zur Installation der Überwachungslösung ist die Verwendung des Installationsskripts:

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-servers/monitoring
./start-monitoring.sh
```

### Manuelle Installation

Wenn Sie die Überwachungslösung manuell installieren möchten, folgen Sie diesen Schritten:

1. Wechseln Sie in das Monitoring-Verzeichnis:

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-servers/monitoring
```

2. Starten Sie die Docker-Container:

```bash
docker-compose up -d
```

## Zugriff auf die Überwachungstools

Nach der Installation können Sie auf die Überwachungstools über die folgenden URLs zugreifen:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (Benutzername: admin, Passwort: admin)
- **cAdvisor**: http://localhost:8081

## Konfiguration

### Prometheus-Konfiguration

Die Prometheus-Konfiguration befindet sich in der Datei `prometheus.yml`. Sie können diese Datei bearbeiten, um die Überwachung anzupassen, z.B. um zusätzliche Scrape-Targets hinzuzufügen oder die Scrape-Intervalle zu ändern.

### Grafana-Konfiguration

Grafana wird mit einer vorkonfigurierten Prometheus-Datenquelle und einem Dashboard für die MCP-Server bereitgestellt. Sie können weitere Dashboards erstellen oder die vorhandenen anpassen, indem Sie die Grafana-Weboberfläche verwenden.

## Überwachte Metriken

Die folgenden Metriken werden von den MCP-Servern überwacht:

- **Verfügbarkeit**: Ob die MCP-Server erreichbar sind
- **HTTP-Anfragen**: Anzahl der HTTP-Anfragen pro Sekunde
- **Antwortzeit**: Durchschnittliche Antwortzeit der MCP-Server
- **Fehlerrate**: Anzahl der HTTP-Fehler (5xx) pro Sekunde
- **Speichernutzung**: Speicherverbrauch der MCP-Server
- **CPU-Nutzung**: CPU-Auslastung der MCP-Server

## Alarme

Die Überwachungslösung kann so konfiguriert werden, dass sie Alarme auslöst, wenn bestimmte Bedingungen erfüllt sind, z.B. wenn ein MCP-Server nicht erreichbar ist oder wenn die Antwortzeit zu hoch ist.

Um Alarme zu konfigurieren, bearbeiten Sie die Datei `prometheus.yml` und fügen Sie Alerting-Regeln hinzu.

## Skalierbarkeit

Die Überwachungslösung kann für die Überwachung einer größeren Anzahl von MCP-Servern skaliert werden, indem Sie die Prometheus-Konfiguration anpassen und zusätzliche Ressourcen für Prometheus und Grafana bereitstellen.

Für eine Produktionsumgebung empfehlen wir die Verwendung von Prometheus Operator und Kubernetes für eine bessere Skalierbarkeit und Hochverfügbarkeit.

## Fehlerbehebung

Wenn Sie Probleme mit der Überwachungslösung haben:

1. Überprüfen Sie die Docker-Container-Logs:
   ```bash
   docker-compose logs prometheus
   docker-compose logs grafana
   ```

2. Überprüfen Sie, ob die MCP-Server Prometheus-Metriken bereitstellen:
   ```bash
   curl http://localhost:3001/metrics
   ```

3. Überprüfen Sie die Prometheus-Targets in der Prometheus-Weboberfläche:
   http://localhost:9090/targets

## Referenzen

- [Prometheus-Dokumentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana-Dokumentation](https://grafana.com/docs/grafana/latest/)
- [cAdvisor-Dokumentation](https://github.com/google/cadvisor)
- [Node Exporter-Dokumentation](https://github.com/prometheus/node_exporter)