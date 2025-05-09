# Entwicklerdokumentation

Diese Dokumentation richtet sich an Entwickler, die am Dev-Server-Workflow-Projekt arbeiten oder es erweitern möchten.

## Architektur

Das Dev-Server-Workflow-Projekt besteht aus mehreren Hauptkomponenten:

1. **Gemeinsame Bibliotheken**: Standardisierte Funktionen und Klassen für Shell- und Python-Skripte
2. **MCP-Server**: Implementierungen des Model Context Protocol für verschiedene Dienste
3. **n8n-Integration**: Workflows und Integrationen für n8n
4. **OpenHands-Integration**: Integration mit OpenHands für KI-gestützte Automatisierung
5. **CLI-Tools**: Befehlszeilenschnittstelle für die Verwaltung des Systems
6. **Monitoring**: Überwachung und Protokollierung aller Komponenten

## Gemeinsame Bibliotheken

Das Projekt verwendet zwei Hauptbibliotheken:

- **Shell-Bibliothek** (`scripts/common/shell/common.sh`): Funktionen für Shell-Skripte
- **Python-Bibliothek** (`scripts/common/python/common.py`): Klassen und Funktionen für Python-Skripte

Diese Bibliotheken bieten standardisierte Funktionen für:

- Logging und Fehlerbehandlung
- Konfigurationsverwaltung
- Docker-Management
- Prozessverwaltung
- Netzwerkoperationen
- Systemoperationen

## MCP-Server

Die MCP-Server-Implementierungen umfassen:

- **n8n MCP-Server**: Stellt n8n-Workflows als MCP-Tools bereit
- **OpenHands MCP-Server**: Ermöglicht die parallele Ausführung von OpenHands-Aufgaben
- **Docker MCP-Server**: Verwaltet Docker-Container über MCP
- **Generator MCP-Server**: Generiert dynamische MCP-Server

## n8n-Integration

Die n8n-Integration umfasst:

- **Workflow-Definitionen**: Vordefinierte Workflows für gängige Aufgaben
- **Setup-Skripte**: Skripte zur Installation und Konfiguration von n8n
- **MCP-Integration**: Integration von n8n mit dem MCP-Protokoll

## OpenHands-Integration

Die OpenHands-Integration umfasst:

- **MCP-Server**: MCP-Server für OpenHands
- **Konfiguration**: Konfigurationsdateien für OpenHands
- **Beispiele**: Beispiele für die Verwendung von OpenHands mit MCP

## CLI-Tools

Die CLI-Tools umfassen:

- **Hauptschnittstelle**: `dev-server-cli.sh`
- **Interaktive Benutzeroberfläche**: `cli/interactive_ui.sh`
- **KI-Assistent**: `cli/ai_assistant_improved.sh`
- **Konfigurationsmanagement**: `cli/config_manager.sh`
- **Fehlerbehandlung**: `cli/error_handler.sh`

## Monitoring

Das Monitoring umfasst:

- **Prometheus-Exporter**: Metriken für alle Komponenten
- **Grafana-Dashboards**: Visualisierung der Metriken
- **Alertmanager**: Warnungen bei Problemen
- **Logging**: Zentralisierte Protokollierung

## Entwicklungsrichtlinien

### Code-Stil

- **Shell-Skripte**: Folgen Sie den [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- **Python-Skripte**: Folgen Sie [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Dokumentation**: Verwenden Sie Markdown für alle Dokumentation

### Fehlerbehandlung

- Verwenden Sie die standardisierten Fehlerbehandlungsfunktionen aus den gemeinsamen Bibliotheken
- Protokollieren Sie alle Fehler mit angemessenem Log-Level
- Implementieren Sie Wiederholungslogik für netzwerkbezogene Operationen

### Tests

- Schreiben Sie Unit-Tests für alle neuen Funktionen
- Implementieren Sie Integrationstests für Workflows
- Verwenden Sie End-to-End-Tests für komplexe Szenarien

### Versionierung

- Folgen Sie [Semantic Versioning](https://semver.org/)
- Dokumentieren Sie alle Änderungen im Changelog
- Taggen Sie Releases mit Git-Tags

## Erweiterung des Projekts

### Hinzufügen eines neuen MCP-Servers

1. Erstellen Sie eine neue Python-Datei im Verzeichnis `src/mcp/`
2. Implementieren Sie die MCP-Schnittstelle (listTools, callTool)
3. Fügen Sie den Server zur Docker-Compose-Konfiguration hinzu
4. Aktualisieren Sie die Dokumentation

### Hinzufügen eines neuen n8n-Workflows

1. Erstellen Sie den Workflow in n8n
2. Exportieren Sie den Workflow als JSON
3. Fügen Sie den Workflow zur Workflow-Bibliothek hinzu
4. Aktualisieren Sie die Setup-Skripte
5. Aktualisieren Sie die Dokumentation

### Hinzufügen eines neuen CLI-Befehls

1. Fügen Sie den Befehl zur Hauptschnittstelle hinzu
2. Implementieren Sie die Befehlslogik
3. Aktualisieren Sie die Hilfe-Dokumentation
4. Aktualisieren Sie die interaktive Benutzeroberfläche
5. Aktualisieren Sie die Dokumentation

## API-Referenz

Siehe [API-Referenz](api-reference.md) für detaillierte Informationen zu allen APIs.

## Entwicklungs-Roadmap

Siehe [Entwicklungs-Roadmap](roadmap.md) für geplante Funktionen und Verbesserungen.