# Anleitung zur Einrichtung von MCP-Servern und OpenHands

Diese Anleitung hilft dir bei der Einrichtung von MCP-Servern für Claude Desktop und OpenHands.

## Voraussetzungen

- Node.js und npm installiert
- Docker und Docker Compose installiert
- Claude Desktop für Linux installiert

## Verfügbare Skripte

Dieses Repository enthält mehrere Skripte zur Einrichtung und Konfiguration von MCP-Servern:

- `simple-mcp-setup.sh`: Einfaches Setup-Skript für MCP-Server und OpenHands
- `fix-claude-config.sh`: Skript zur Korrektur der Claude Desktop Konfigurationsdatei
- `custom-openhands-setup.sh`: Skript für benutzerdefinierten Port und Workspace-Pfad
- `mcp-setup.sh`: Vollständiges Setup-Skript mit Umgebungsvariablen
- `create-configs.sh`: Skript zum Erstellen der Konfigurationsdateien
- `create-scripts.sh`: Skript zum Erstellen der Start-Skripte
- `install-mcp.sh`: Hauptinstallationsskript

## Einfache Installation

### Schritt 1: Einfaches Setup-Skript ausführen

```bash
./simple-mcp-setup.sh
```

Das Skript wird:
- Die benötigten MCP-Server installieren
- Die Konfigurationsdateien für Claude Desktop erstellen
- Die Konfigurationsdateien für OpenHands erstellen
- Start-Skripte für OpenHands und den MCP-Inspektor erstellen

### Schritt 2: API-Keys konfigurieren

Bearbeite die Claude Desktop Konfigurationsdatei, um deine API-Keys hinzuzufügen:

```bash
nano ~/.config/Claude/claude_desktop_config.json
```

Füge deine API-Keys in die entsprechenden Felder ein:

```json
"env": {
  "GITHUB_TOKEN": "dein_github_token_hier"
}
```

### Schritt 3: OpenHands starten

Starte OpenHands mit dem erstellten Skript:

```bash
~/start-openhands.sh
```

### Schritt 4: Claude Desktop neu starten

Starte Claude Desktop neu, damit es die MCP-Server erkennt:

```bash
claude-desktop
```

## Erweiterte Installation

### Vollständige Installation mit Umgebungsvariablen

1. Erstelle eine `.env`-Datei mit deinen API-Keys und Konfigurationen:

```bash
# API-Keys
BRAVE_API_KEY="dein_brave_api_key"
GITHUB_TOKEN="dein_github_token"
GITLAB_TOKEN="dein_gitlab_token"
GITLAB_URL="https://gitlab.ecospherenet.work"
WOLFRAM_APP_ID="dein_wolfram_app_id"

# GitHub Benutzerinformationen
GITHUB_USERNAME="dein_github_username"
GITHUB_EMAIL="deine_email@example.com"

# Ollama-Konfiguration
OLLAMA_MODEL="qwen2.5-coder:7b-instruct"
OLLAMA_BASE_URL="http://localhost:11434"

# OpenHands-Konfiguration
OPENHANDS_STATE_DIR="/home/user/.openhands-state"
OPENHANDS_WORKSPACE_DIR="/home/user/openhands-workspace"
OPENHANDS_CONFIG_DIR="/home/user/.config/openhands"
```

2. Führe das vollständige Setup-Skript aus:

```bash
./mcp-setup.sh
```

### Benutzerdefinierter Port und Workspace

Wenn du OpenHands mit einem benutzerdefinierten Port (z.B. 3333) und einem benutzerdefinierten Workspace-Pfad (z.B. /home/sam) konfigurieren möchtest:

```bash
./custom-openhands-setup.sh
```

Dieses Skript konfiguriert:
- OpenHands, um auf Port 3333 zu laufen
- Den Workspace-Pfad auf /home/sam
- Die Claude Desktop Konfiguration für den neuen Port

## Fehlerbehebung

### Claude Desktop erkennt die MCP-Server nicht

Verwende das Fix-Skript, um die Claude Desktop Konfiguration zu korrigieren:

```bash
./fix-claude-config.sh
```

### OpenHands startet nicht

Überprüfe die Docker-Logs:

```bash
docker-compose -f ~/openhands-docker-compose.yml logs
```

### MCP-Server funktionieren nicht

Verwende den MCP-Inspektor, um zu überprüfen, ob die Server korrekt funktionieren:

```bash
~/start-mcp-inspector.sh
```

Der MCP-Inspektor ist unter http://localhost:6274 erreichbar.

## Nützliche Befehle

- OpenHands starten: `~/start-openhands.sh`
- MCP-Inspektor starten: `~/start-mcp-inspector.sh`
- Ollama-MCP-Bridge starten: `~/start-ollama-bridge.sh`
- Alle Dienste starten: `~/start-all-mcp.sh`
- OpenHands stoppen: `docker-compose -f ~/openhands-docker-compose.yml down`
- MCP-Server neu installieren: `npm install -g @modelcontextprotocol/server-name`

### Behebung von Installationsproblemen

Wenn du Probleme mit der Installation hast, kannst du das Fehlerbehebungsskript ausführen:

```bash
./fix-mcp-errors.sh
```

Dieses Skript behebt folgende Probleme:
- Ollama-Service-Probleme
- Ollama-Modell-Download-Probleme
- TypeScript-Installationsprobleme
- Ollama-MCP-Bridge-Pfadprobleme
- Konfiguriert OpenHands, um auf Port 3333 zu laufen
