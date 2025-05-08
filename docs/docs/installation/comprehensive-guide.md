# Umfassende Installationsanleitung

Diese Anleitung bietet eine detaillierte Schritt-für-Schritt-Anleitung zur Installation und Konfiguration des Dev-Server-Workflow-Systems mit allen seinen Komponenten, einschließlich der neuen Verbesserungen.

## Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass folgende Voraussetzungen erfüllt sind:

- **Docker**: Version 20.10.0 oder höher
- **Docker Compose**: Version 1.29.0 oder höher
- **Python**: Version 3.9 oder höher
- **Git**: Version 2.25.0 oder höher
- **Node.js**: Version 14.0.0 oder höher (für n8n und Frontend-Entwicklung)
- **npm**: Version 6.0.0 oder höher

Sie können die Versionen mit folgenden Befehlen überprüfen:

```bash
docker --version
docker-compose --version
python --version
git --version
node --version
npm --version
```

## Installation

### 1. Repository klonen

Klonen Sie das Repository und wechseln Sie in das Projektverzeichnis:

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Konfiguration einrichten

Kopieren Sie die Beispiel-Konfigurationsdatei und passen Sie sie an Ihre Bedürfnisse an:

```bash
cp .env.example .env
```

Öffnen Sie die `.env`-Datei in einem Texteditor und konfigurieren Sie die erforderlichen Parameter:

```ini
# Allgemeine Konfiguration
BASE_DIR=/workspace/Dev-Server-Workflow
LOG_LEVEL=info

# Docker-Konfiguration
DOCKER_NETWORK=dev-server-network

# n8n-Konfiguration
N8N_PORT=5678
N8N_URL=http://localhost:5678
N8N_USER=admin
N8N_PASSWORD=password
N8N_ENCRYPTION_KEY=your_encryption_key_min_32_chars

# MCP-Server-Konfiguration
MCP_PORT=3333
MCP_AUTH_TOKEN=your_mcp_auth_token

# GitHub-Konfiguration (optional)
GITHUB_TOKEN=your_github_token

# OpenProject-Konfiguration (optional)
OPENPROJECT_URL=https://openproject.example.com
OPENPROJECT_TOKEN=your_openproject_token

# Monitoring-Konfiguration
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### 3. Abhängigkeiten installieren

Installieren Sie die erforderlichen Python-Abhängigkeiten:

```bash
pip install -r requirements.txt
```

### 4. Neue CLI verwenden

Mit der neuen CLI können Sie das System einfach verwalten:

```bash
# Machen Sie die CLI ausführbar
chmod +x dev-server-cli.sh

# Zeigen Sie die Hilfe an
./dev-server-cli.sh help
```

### 5. System installieren und starten

Sie können das gesamte System mit einem einzigen Befehl installieren und starten:

```bash
# Interaktive Benutzeroberfläche starten
./dev-server-cli.sh ui

# ODER: Alle Komponenten direkt starten
./dev-server-cli.sh start-all
```

Alternativ können Sie die Komponenten einzeln starten:

```bash
# n8n starten
./dev-server-cli.sh start n8n

# MCP-Server starten
./dev-server-cli.sh start desktop-commander-mcp
./dev-server-cli.sh start filesystem-mcp
./dev-server-cli.sh start github-mcp
./dev-server-cli.sh start memory-mcp
./dev-server-cli.sh start prompt-mcp

# Web-UI starten
./dev-server-cli.sh start web-ui
```

### 6. Monitoring einrichten (optional)

Starten Sie den Prometheus-Exporter für das Monitoring:

```bash
# Prometheus-Exporter starten
python src/monitoring/prometheus_exporter.py &

# Prometheus und Grafana starten
./dev-server-cli.sh start prometheus
./dev-server-cli.sh start grafana
```

## Konfiguration

### Zentralisiertes Konfigurationsmanagement

Das neue zentralisierte Konfigurationsmanagement ermöglicht die einfache Verwaltung von Konfigurationen in verschiedenen Formaten:

```bash
# Konfiguration anzeigen
./cli/config_manager.sh list env .env

# Konfigurationswert setzen
./cli/config_manager.sh save env .env N8N_PORT 5678

# Konfigurationswert abrufen
./cli/config_manager.sh get env .env N8N_PORT
```

### Dependency Management

Das neue Dependency Management System verwaltet automatisch die Abhängigkeiten zwischen Komponenten:

```bash
# Alle Komponenten und ihre Abhängigkeiten anzeigen
./src/common/dependency_manager.sh list

# Abhängigkeiten einer Komponente anzeigen
./src/common/dependency_manager.sh dependencies n8n

# Abhängige Komponenten anzeigen
./src/common/dependency_manager.sh dependents n8n
```

### Fehlerbehandlung

Das verbesserte Fehlerbehandlungssystem bietet robustere Fehlerbehandlung und Rollback-Mechanismen:

```bash
# Fehlerbehandlung testen
./cli/error_handler.sh check_command docker "Docker ist nicht installiert"
./cli/error_handler.sh check_file /path/to/file true
```

## Komponenten

### n8n

n8n ist die Workflow-Automatisierungsplattform, die für die Integration verschiedener Dienste verwendet wird.

- **URL**: http://localhost:5678
- **Standardanmeldedaten**: admin/password

### MCP-Server

Die MCP-Server (Model Context Protocol) bieten eine standardisierte Schnittstelle für die Kommunikation mit verschiedenen Diensten.

- **Desktop Commander MCP**: http://localhost:3333
- **Filesystem MCP**: http://localhost:3334
- **GitHub MCP**: http://localhost:3335
- **Memory MCP**: http://localhost:3336
- **Prompt MCP**: http://localhost:3337

### Web-UI

Die Web-UI bietet eine benutzerfreundliche Oberfläche für die Verwaltung des Systems.

- **URL**: http://localhost:8080

### Monitoring

Das Monitoring-System ermöglicht die Überwachung der Systemleistung und -gesundheit.

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (Standardanmeldedaten: admin/admin)

## Backup und Wiederherstellung

Das System bietet Funktionen für Backup und Wiederherstellung:

```bash
# Backup erstellen
./dev-server-cli.sh backup

# Backup wiederherstellen
./dev-server-cli.sh restore backup_20250508_123456.tar.gz
```

## Fehlerbehebung

### Allgemeine Probleme

#### Komponente startet nicht

Überprüfen Sie den Status der Komponente:

```bash
./dev-server-cli.sh status
```

Überprüfen Sie die Logs:

```bash
./dev-server-cli.sh logs n8n
```

#### Netzwerkprobleme

Überprüfen Sie, ob das Docker-Netzwerk korrekt eingerichtet ist:

```bash
docker network ls
docker network inspect dev-server-network
```

#### Konfigurationsprobleme

Überprüfen Sie die Konfiguration:

```bash
./cli/config_manager.sh list env .env
```

### Spezifische Probleme

#### n8n ist nicht erreichbar

- Überprüfen Sie, ob der n8n-Container läuft: `docker ps | grep n8n`
- Überprüfen Sie die n8n-Logs: `docker logs n8n`
- Stellen Sie sicher, dass Port 5678 nicht von einem anderen Dienst verwendet wird

#### MCP-Server sind nicht erreichbar

- Überprüfen Sie, ob die MCP-Server-Container laufen: `docker ps | grep mcp`
- Überprüfen Sie die MCP-Server-Logs: `docker logs desktop-commander-mcp`
- Testen Sie die Verbindung: `curl http://localhost:3333/health`

#### Web-UI ist nicht erreichbar

- Überprüfen Sie, ob der Web-UI-Container läuft: `docker ps | grep web-ui`
- Überprüfen Sie die Web-UI-Logs: `docker logs web-ui`
- Stellen Sie sicher, dass Port 8080 nicht von einem anderen Dienst verwendet wird

## Erweiterte Konfiguration

### Umgebungsvariablen

Alle Konfigurationsoptionen können über Umgebungsvariablen gesetzt werden. Die wichtigsten sind:

| Variable | Beschreibung | Standardwert |
|----------|--------------|--------------|
| `N8N_PORT` | Port für n8n | 5678 |
| `MCP_PORT` | Basis-Port für MCP-Server | 3333 |
| `PROMETHEUS_PORT` | Port für Prometheus | 9090 |
| `GRAFANA_PORT` | Port für Grafana | 3000 |
| `LOG_LEVEL` | Logging-Level (debug, info, warn, error) | info |

### Konfigurationsdateien

Die wichtigsten Konfigurationsdateien sind:

- `.env`: Hauptkonfigurationsdatei
- `cli/config.sh`: Konfiguration für die CLI
- `docker-compose.yml`: Docker-Compose-Konfiguration
- `docker-compose.web-ui.yml`: Docker-Compose-Konfiguration für die Web-UI

### Anpassung der MCP-Server

Sie können die MCP-Server an Ihre Bedürfnisse anpassen:

```bash
# MCP-Server-Konfiguration bearbeiten
./dev-server-cli.sh config update-config desktop-commander-mcp max_workers 10
```

## Nächste Schritte

Nach der Installation können Sie:

1. Die [Workflow-Integration](../Dev-Server-Workflow/Workflow-Integration.md) konfigurieren
2. Die [OpenHands-Integration](../Dev-Server-Workflow/MCP-OpenHands.md) einrichten
3. Die [Web-UI](../Dev-Server-Workflow/Web-UI.md) anpassen
4. Das [Monitoring](../Dev-Server-Workflow/MCP-Server-Monitoring.md) konfigurieren

## Weitere Ressourcen

- [Architekturübersicht](../Dev-Server-Workflow/ARCHITECTURE.md)
- [Entwicklungsanleitung](../development/guide.md)
- [API-Referenz](../api/reference.md)
- [Fehlerbehebung](../troubleshooting/index.md)