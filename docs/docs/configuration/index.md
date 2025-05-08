# Konfigurationsanleitung

Diese Anleitung beschreibt die Konfiguration des Dev-Server-Workflow-Systems mit dem neuen zentralisierten Konfigurationsmanagement.

## Überblick

Das Dev-Server-Workflow-System verwendet ein zentralisiertes Konfigurationsmanagement, das verschiedene Konfigurationsformate unterstützt:

- **Umgebungsvariablen** (`.env`-Dateien)
- **JSON-Konfigurationsdateien**
- **YAML-Konfigurationsdateien** (wenn `yq` installiert ist)
- **Bash-Konfigurationsdateien** (`config.sh`)

## Konfigurationsmanager

Der Konfigurationsmanager (`cli/config_manager.sh`) bietet eine einheitliche API für den Zugriff auf Konfigurationseinstellungen in verschiedenen Formaten.

### Grundlegende Verwendung

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

### Beispiele

```bash
# n8n-Port in .env-Datei setzen
./cli/config_manager.sh save env .env N8N_PORT 5678

# GitHub-Token aus .env-Datei abrufen
token=$(./cli/config_manager.sh get env .env GITHUB_TOKEN)

# Alle Konfigurationsschlüssel in .env-Datei auflisten
./cli/config_manager.sh list env .env

# JSON-Konfiguration laden
./cli/config_manager.sh load json config/mcp-server-config.json MCP_SERVER

# YAML-Konfiguration laden (wenn yq installiert ist)
./cli/config_manager.sh load yaml config/prometheus-config.yml PROMETHEUS
```

## Hauptkonfigurationsdatei (.env)

Die Hauptkonfigurationsdatei ist `.env` im Stammverzeichnis des Projekts. Sie enthält die grundlegenden Konfigurationseinstellungen für alle Komponenten.

### Beispiel-Konfiguration

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

## Komponentenspezifische Konfiguration

### n8n-Konfiguration

Die n8n-Konfiguration wird in der `.env`-Datei und in `docker-compose.yml` definiert.

Wichtige Konfigurationsparameter:

| Parameter | Beschreibung | Standardwert |
|-----------|--------------|--------------|
| `N8N_PORT` | Port für n8n | 5678 |
| `N8N_URL` | URL für n8n | http://localhost:5678 |
| `N8N_USER` | Benutzername für n8n | admin |
| `N8N_PASSWORD` | Passwort für n8n | password |
| `N8N_ENCRYPTION_KEY` | Verschlüsselungsschlüssel für n8n | your_encryption_key_min_32_chars |

### MCP-Server-Konfiguration

Die MCP-Server-Konfiguration wird in der `.env`-Datei, in `docker-compose.yml` und in spezifischen JSON-Konfigurationsdateien definiert.

Wichtige Konfigurationsparameter:

| Parameter | Beschreibung | Standardwert |
|-----------|--------------|--------------|
| `MCP_PORT` | Basis-Port für MCP-Server | 3333 |
| `MCP_AUTH_TOKEN` | Authentifizierungstoken für MCP-Server | your_mcp_auth_token |

Spezifische MCP-Server-Konfiguration:

```json
{
  "server_name": "desktop-commander-mcp",
  "port": 3333,
  "max_workers": 5,
  "log_level": "info",
  "auth_token": "your_mcp_auth_token"
}
```

### Web-UI-Konfiguration

Die Web-UI-Konfiguration wird in der `.env`-Datei und in `docker-compose.web-ui.yml` definiert.

Wichtige Konfigurationsparameter:

| Parameter | Beschreibung | Standardwert |
|-----------|--------------|--------------|
| `WEB_UI_PORT` | Port für die Web-UI | 8080 |
| `WEB_UI_API_URL` | URL für die Web-UI-API | http://localhost:3333 |

### Monitoring-Konfiguration

Die Monitoring-Konfiguration wird in der `.env`-Datei und in spezifischen YAML-Konfigurationsdateien definiert.

Wichtige Konfigurationsparameter:

| Parameter | Beschreibung | Standardwert |
|-----------|--------------|--------------|
| `PROMETHEUS_PORT` | Port für Prometheus | 9090 |
| `GRAFANA_PORT` | Port für Grafana | 3000 |

## Dependency Management

Das Dependency Management System (`src/common/dependency_manager.sh`) verwaltet die Abhängigkeiten zwischen Komponenten.

### Grundlegende Verwendung

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

### Abhängigkeitsgraph

Der Abhängigkeitsgraph definiert die Beziehungen zwischen den Komponenten:

```
n8n: (keine Abhängigkeiten)
prometheus: (keine Abhängigkeiten)
grafana: prometheus
mcp-inspector-ui: (keine Abhängigkeiten)
desktop-commander-mcp: (keine Abhängigkeiten)
filesystem-mcp: (keine Abhängigkeiten)
github-mcp: (keine Abhängigkeiten)
memory-mcp: (keine Abhängigkeiten)
prompt-mcp: n8n
openhands-mcp: n8n
generator-mcp: n8n
web-ui: n8n,mcp-inspector-ui
```

## CLI-Konfiguration

Die CLI-Konfiguration wird in `cli/config.sh` definiert.

Wichtige Konfigurationsparameter:

| Parameter | Beschreibung | Standardwert |
|-----------|--------------|--------------|
| `BASE_DIR` | Basisverzeichnis des Projekts | /workspace/Dev-Server-Workflow |
| `LOG_LEVEL` | Logging-Level (debug, info, warn, error) | info |

## Umgebungsvariablen

Alle Konfigurationsoptionen können über Umgebungsvariablen gesetzt werden. Die wichtigsten sind:

| Variable | Beschreibung | Standardwert |
|----------|--------------|--------------|
| `N8N_PORT` | Port für n8n | 5678 |
| `MCP_PORT` | Basis-Port für MCP-Server | 3333 |
| `PROMETHEUS_PORT` | Port für Prometheus | 9090 |
| `GRAFANA_PORT` | Port für Grafana | 3000 |
| `LOG_LEVEL` | Logging-Level (debug, info, warn, error) | info |

## Erweiterte Konfiguration

### Fehlerbehandlung

Die Fehlerbehandlung wird in `cli/error_handler.sh` konfiguriert.

Wichtige Konfigurationsparameter:

| Parameter | Beschreibung | Standardwert |
|-----------|--------------|--------------|
| `ERROR_LOG_FILE` | Pfad zur Fehlerprotokolldatei | /workspace/Dev-Server-Workflow/logs/error.log |

### Monitoring

Das Monitoring wird in `src/monitoring/prometheus_exporter.py` konfiguriert.

Wichtige Konfigurationsparameter:

| Parameter | Beschreibung | Standardwert |
|-----------|--------------|--------------|
| `--port` | Port für den Prometheus-Exporter | 9090 |
| `--interval` | Intervall in Sekunden zwischen Metriksammlungen | 15 |
| `--debug` | Debug-Logging aktivieren | false |

### Service Worker für Web-UI

Der Service Worker für die Web-UI wird in `frontend/src/serviceWorker.js` konfiguriert.

Wichtige Konfigurationsparameter:

| Parameter | Beschreibung | Standardwert |
|-----------|--------------|--------------|
| `CACHE_NAME` | Name des Cache für die Web-UI | dev-server-workflow-v1 |
| `URLS_TO_CACHE` | URLs, die im Cache gespeichert werden sollen | ['/index.html', '/static/css/main.css', ...] |

## Konfiguration über die interaktive Benutzeroberfläche

Die interaktive Benutzeroberfläche (`cli/interactive_ui.sh`) bietet eine benutzerfreundliche Möglichkeit, das System zu konfigurieren.

```bash
# Interaktive Benutzeroberfläche starten
./cli/interactive_ui.sh
```

In der interaktiven Benutzeroberfläche können Sie:

1. Die Konfiguration anzeigen und bearbeiten
2. Umgebungsvariablen setzen
3. Die Docker-Compose-Konfiguration anzeigen
4. Komponenten starten und stoppen
5. Logs anzeigen
6. Backups erstellen und wiederherstellen

## Konfiguration über die CLI

Die CLI (`dev-server-cli.sh`) bietet eine Befehlszeilenschnittstelle für die Konfiguration des Systems.

```bash
# Konfiguration anzeigen
./dev-server-cli.sh config

# Konfigurationswert setzen
./dev-server-cli.sh config save env .env N8N_PORT 5678

# Konfigurationswert abrufen
./dev-server-cli.sh config get env .env N8N_PORT
```

## Fehlerbehebung

### Konfigurationsprobleme

#### Konfigurationsdatei nicht gefunden

```bash
# Überprüfen, ob die Konfigurationsdatei existiert
ls -la .env

# Beispielkonfigurationsdatei kopieren, wenn sie nicht existiert
cp .env.example .env
```

#### Ungültige Konfigurationswerte

```bash
# Konfigurationswerte überprüfen
./cli/config_manager.sh list env .env

# Konfigurationswert korrigieren
./cli/config_manager.sh save env .env N8N_PORT 5678
```

#### Abhängigkeitsprobleme

```bash
# Abhängigkeiten überprüfen
./src/common/dependency_manager.sh list

# Komponente und ihre Abhängigkeiten starten
./src/common/dependency_manager.sh start web-ui
```

## Weitere Ressourcen

- [Installationsanleitung](../installation/comprehensive-guide.md)
- [Architekturübersicht](../Dev-Server-Workflow/ARCHITECTURE.md)
- [Entwicklungsanleitung](../development/guide.md)
- [API-Referenz](../api/reference.md)
- [Fehlerbehebung](../troubleshooting/index.md)