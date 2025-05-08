# Neue Funktionen

Diese Dokumentation beschreibt die neuen Funktionen, die im Dev-Server-Workflow-System implementiert wurden.

## Überblick

Das Dev-Server-Workflow-System wurde mit folgenden neuen Funktionen erweitert:

1. **Zentralisiertes Konfigurationsmanagement**
2. **Verbesserte Fehlerbehandlung**
3. **Gemeinsame Bibliothek für geteilte Funktionalitäten**
4. **Dependency Management System**
5. **Verbesserte Benutzeroberfläche**
6. **Monitoring und Observability**
7. **Offline-Unterstützung für Web-UI**
8. **Backup und Wiederherstellung**
9. **Verbesserte Dokumentation**
10. **Sicherheitsverbesserungen**

## 1. Zentralisiertes Konfigurationsmanagement

Das zentralisierte Konfigurationsmanagement ermöglicht die einheitliche Verwaltung von Konfigurationen in verschiedenen Formaten.

### Hauptfunktionen

- Unterstützung für verschiedene Konfigurationsformate (`.env`, JSON, YAML)
- Einheitliche API für den Zugriff auf Konfigurationseinstellungen
- Automatisches Laden aller Konfigurationen beim Start
- Validierung von Konfigurationswerten

### Verwendung

```bash
# Konfiguration laden
./cli/config_manager.sh load env /path/to/.env [prefix]

# Konfiguration speichern
./cli/config_manager.sh save env /path/to/.env KEY VALUE [create_if_missing]

# Konfigurationswert abrufen
./cli/config_manager.sh get env /path/to/.env KEY [default_value]

# Konfigurationsschlüssel auflisten
./cli/config_manager.sh list env /path/to/.env

# Konfigurationsschlüssel löschen
./cli/config_manager.sh delete env /path/to/.env KEY

# Alle Konfigurationen laden
./cli/config_manager.sh load-all
```

### Weitere Informationen

- [Konfigurationsanleitung](../configuration/index.md)

## 2. Verbesserte Fehlerbehandlung

Die verbesserte Fehlerbehandlung bietet robustere Fehlerbehandlung und Rollback-Mechanismen.

### Hauptfunktionen

- Strikte Fehlerbehandlung mit `set -euo pipefail`
- Rollback-Mechanismen für fehlgeschlagene Operationen
- Detaillierte Fehlerprotokolle
- Einheitliche Fehlerbehandlungsstrategie

### Verwendung

```bash
# In Bash-Skripten einbinden
source "${BASE_DIR}/cli/error_handler.sh"

# Aktuelle Operation setzen
set_operation "start_container"
set_container "n8n"

# Fehlerbehandlung einrichten
trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR

# Abhängigkeiten prüfen
check_command "docker" "Install Docker: https://docs.docker.com/get-docker/"
check_file "/path/to/file" "true"
check_directory "/path/to/dir" "true"
```

### Weitere Informationen

- [Fehlerbehandlungsanleitung](../troubleshooting/index.md)

## 3. Gemeinsame Bibliothek für geteilte Funktionalitäten

Die gemeinsame Bibliothek reduziert Code-Duplikation zwischen `docker-mcp-ecosystem` und `docker-mcp-servers`.

### Hauptfunktionen

- Gemeinsame Funktionen für die Verwaltung von MCP-Servern
- Reduzierung von Code-Duplikation
- Einheitliche API für den Zugriff auf MCP-Server

### Verwendung

```bash
# In Bash-Skripten einbinden
source "${BASE_DIR}/src/common/mcp_server_lib.sh"

# MCP-Server starten
start_mcp_server "server-name" "docker compose.yml" ".env"

# MCP-Server stoppen
stop_mcp_server "server-name" "docker compose.yml" ".env"

# MCP-Server-Status abrufen
status=$(get_mcp_server_status "server-name")
```

### Weitere Informationen

- [MCP-Server-Anleitung](../mcp-servers/index.md)

## 4. Dependency Management System

Das Dependency Management System verwaltet automatisch die Abhängigkeiten zwischen Komponenten.

### Hauptfunktionen

- Automatisches Starten und Stoppen von Komponenten in der richtigen Reihenfolge
- Verwaltung von Abhängigkeiten zwischen Komponenten
- Visualisierung des Abhängigkeitsgraphen

### Verwendung

```bash
# Alle Komponenten und ihre Abhängigkeiten anzeigen
./src/common/dependency_manager.sh list

# Abhängigkeiten einer Komponente anzeigen
./src/common/dependency_manager.sh dependencies n8n

# Abhängige Komponenten anzeigen
./src/common/dependency_manager.sh dependents n8n

# Komponente starten (und ihre Abhängigkeiten)
./src/common/dependency_manager.sh start n8n

# Komponente stoppen (und ihre Abhängigen)
./src/common/dependency_manager.sh stop n8n

# Alle Komponenten starten
./src/common/dependency_manager.sh start-all

# Alle Komponenten stoppen
./src/common/dependency_manager.sh stop-all
```

### Weitere Informationen

- [Dependency Management Anleitung](../configuration/index.md#dependency-management)

## 5. Verbesserte Benutzeroberfläche

Die verbesserte Benutzeroberfläche bietet eine intuitivere Benutzererfahrung.

### Hauptfunktionen

- Interaktive Benutzeroberfläche mit Dialog
- Textbasierte Alternative für Umgebungen ohne Dialog
- Befehlszeilenschnittstelle für die Verwaltung des Systems

### Verwendung

```bash
# Interaktive Benutzeroberfläche starten
./cli/interactive_ui.sh

# CLI verwenden
./dev-server-cli.sh status
./dev-server-cli.sh start n8n
./dev-server-cli.sh stop web-ui
./dev-server-cli.sh logs n8n
```

### Weitere Informationen

- [Benutzeroberflächen-Anleitung](../cli/index.md)

## 6. Monitoring und Observability

Das Monitoring-System ermöglicht die Überwachung der Systemleistung und -gesundheit.

### Hauptfunktionen

- Prometheus-Exporter für Metriken
- Grafana-Dashboards für die Visualisierung
- Gesundheitschecks für alle Komponenten
- Detaillierte Protokollierung

### Verwendung

```bash
# Prometheus-Exporter starten
python src/monitoring/prometheus_exporter.py &

# Prometheus und Grafana starten
./dev-server-cli.sh start prometheus
./dev-server-cli.sh start grafana

# Metriken anzeigen
curl http://localhost:9090/metrics
```

### Weitere Informationen

- [Monitoring-Anleitung](../monitoring/index.md)

## 7. Offline-Unterstützung für Web-UI

Die Offline-Unterstützung für die Web-UI ermöglicht die Nutzung der Web-UI auch ohne Internetverbindung.

### Hauptfunktionen

- Service Worker für Offline-Unterstützung
- Caching von Assets für die Offline-Nutzung
- Offline-Seite für Benutzer ohne Internetverbindung
- Automatische Synchronisierung bei Wiederherstellung der Verbindung

### Verwendung

Die Offline-Unterstützung wird automatisch aktiviert, wenn die Web-UI geladen wird. Es sind keine zusätzlichen Schritte erforderlich.

### Weitere Informationen

- [Web-UI-Anleitung](../web-ui/index.md)

## 8. Backup und Wiederherstellung

Die Backup- und Wiederherstellungsfunktionen ermöglichen die Sicherung und Wiederherstellung von Daten und Konfigurationen.

### Hauptfunktionen

- Erstellung von Backups aller Konfigurationen und Daten
- Wiederherstellung von Backups
- Automatische Backups
- Backup-Verwaltung

### Verwendung

```bash
# Backup erstellen
./dev-server-cli.sh backup

# Backup wiederherstellen
./dev-server-cli.sh restore backup_20250508_123456.tar.gz

# Backups auflisten
./dev-server-cli.sh backup list
```

### Weitere Informationen

- [Backup-Anleitung](../backup/index.md)

## 9. Verbesserte Dokumentation

Die verbesserte Dokumentation bietet detailliertere Informationen zu allen Aspekten des Systems.

### Hauptfunktionen

- Detaillierte Installationsanleitung
- Umfassende Konfigurationsanleitung
- Dokumentation aller neuen Funktionen
- Fehlerbehebungsanleitung

### Weitere Informationen

- [Installationsanleitung](../installation/comprehensive-guide.md)
- [Konfigurationsanleitung](../configuration/index.md)
- [Fehlerbehebungsanleitung](../troubleshooting/index.md)

## 10. Sicherheitsverbesserungen

Die Sicherheitsverbesserungen erhöhen die Sicherheit des Systems.

### Hauptfunktionen

- Validierung von Benutzereingaben
- Sichere Standardwerte für Konfigurationseinstellungen
- Fehlerprüfung für alle kritischen Operationen
- Verbesserte Berechtigungsprüfungen

### Weitere Informationen

- [Sicherheitsanleitung](../security/index.md)

## Zusammenfassung

Die neuen Funktionen verbessern die Architektur, Code-Qualität, Fehlerbehandlung, Sicherheit, Dokumentation, Benutzerfreundlichkeit, Erweiterbarkeit, Performance und Integration des Dev-Server-Workflow-Systems erheblich. Sie machen das System robuster, benutzerfreundlicher und wartbarer.

Weitere Informationen zu den einzelnen Funktionen finden Sie in den entsprechenden Anleitungen.