# Installationsanleitung

Diese Anleitung beschreibt die Installation und Konfiguration der n8n Workflow Integration für AFFiNE, AppFlowy, GitLab/GitHub, OpenProject und OpenHands.

## Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass folgende Voraussetzungen erfüllt sind:

- Python 3.6+ ist installiert
- Docker und Docker Compose sind installiert (für lokale n8n-Installation)
- Sie haben API-Keys für die zu integrierenden Dienste

## Installation

### 1. Repository klonen

Klonen Sie das Repository und wechseln Sie in das Verzeichnis:

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Konfigurationsdatei erstellen

Kopieren Sie die Vorlage für die Konfigurationsdatei und passen Sie sie an:

```bash
cp src/env-template .env
```

Öffnen Sie die `.env`-Datei in einem Texteditor und füllen Sie alle benötigten Werte aus:

```
# n8n Konfiguration
N8N_URL=http://localhost:5678
N8N_USER=admin
N8N_PASSWORD=password
N8N_API_KEY=your_api_key_here

# GitHub/GitLab Konfiguration
GITHUB_TOKEN=your_github_token_here

# OpenProject Konfiguration
OPENPROJECT_URL=https://your-openproject-instance.com
OPENPROJECT_TOKEN=your_openproject_token_here

# Weitere Konfigurationen...
```

### 3. Installation mit dem Setup-Skript

Verwenden Sie das Setup-Skript, um n8n zu installieren und die Workflows einzurichten:

```bash
python setup.py install --env-file .env
```

Dieses Skript führt folgende Aktionen aus:
- Installation von n8n mit Docker (wenn `--no-install` nicht angegeben ist)
- Einrichtung der Credentials für die verschiedenen Dienste
- Erstellung und Aktivierung der Workflows
- Einrichtung des MCP-Servers (wenn `--mcp` angegeben ist)

### 4. Spezifische Workflows installieren

Sie können auch spezifische Workflows installieren:

```bash
python setup.py install --env-file .env --workflows github document openhands
```

Verfügbare Workflows:
- `github`: GitHub zu OpenProject Integration
- `document`: Dokumenten-Synchronisierung
- `openhands`: OpenHands Integration
- `discord`: Discord Benachrichtigungen
- `timetracking`: Zeit-Tracking
- `ai`: KI-gestützte Zusammenfassungen
- `mcp`: MCP Integration
- `all`: Alle Workflows (Standard)

### 5. MCP-Server einrichten

Um den MCP-Server für die Integration mit OpenHands einzurichten:

```bash
python setup.py install --env-file .env --mcp
```

Dies erstellt die MCP-Server-Konfiguration und generiert die `openhands-mcp-config.json`-Datei, die Sie in Ihre OpenHands-Konfiguration integrieren können.

## Testen der Installation

Sie können die Installation testen mit:

```bash
python setup.py test
```

Dies überprüft, ob alle erforderlichen Dateien vorhanden sind und ob die Konfiguration korrekt ist.

## Manuelle Installation

Wenn Sie n8n manuell installieren möchten, können Sie das Setup-Skript mit der Option `--no-install` ausführen:

```bash
python setup.py install --env-file .env --no-install
```

In diesem Fall müssen Sie n8n selbst installieren und konfigurieren, bevor Sie die Workflows einrichten.

## Fehlerbehebung

### n8n ist nicht erreichbar

Wenn n8n nicht erreichbar ist, überprüfen Sie:
- Ob Docker läuft
- Ob n8n korrekt gestartet wurde
- Ob die URL in der `.env`-Datei korrekt ist

### API-Key-Probleme

Wenn Sie Probleme mit dem API-Key haben:
- Stellen Sie sicher, dass der API-Key in der `.env`-Datei korrekt ist
- Versuchen Sie, einen neuen API-Key zu generieren
- Überprüfen Sie die n8n-Logs auf Fehler

### Workflow-Aktivierung schlägt fehl

Wenn die Workflow-Aktivierung fehlschlägt:
- Überprüfen Sie, ob n8n korrekt konfiguriert ist
- Stellen Sie sicher, dass alle erforderlichen Credentials eingerichtet sind
- Überprüfen Sie die n8n-Logs auf Fehler

### MCP-Server-Probleme

Wenn der MCP-Server nicht funktioniert:
- Stellen Sie sicher, dass aiohttp installiert ist (`pip install aiohttp`)
- Überprüfen Sie, ob die n8n-URL und der API-Key korrekt sind
- Überprüfen Sie die Logs des MCP-Servers auf Fehler