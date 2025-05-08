# OpenHands-Integration

Diese Dokumentation beschreibt die Integration des Dev-Server-Workflow-Systems mit OpenHands, einer Plattform für KI-gestützte Softwareentwicklung.

## Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Voraussetzungen](#voraussetzungen)
- [Installation und Konfiguration](#installation-und-konfiguration)
- [MCP-Integration](#mcp-integration)
- [Verwendung mit n8n-Workflows](#verwendung-mit-n8n-workflows)
- [Anpassung und Erweiterung](#anpassung-und-erweiterung)
- [Fehlerbehebung](#fehlerbehebung)

## Übersicht

OpenHands (früher OpenDevin) ist eine Plattform für KI-gestützte Softwareentwicklung, die es KI-Agenten ermöglicht, Entwicklungsaufgaben auszuführen. Die Integration mit dem Dev-Server-Workflow-System erweitert die Fähigkeiten von OpenHands durch:

- Zugriff auf spezialisierte MCP-Server für erweiterte Funktionen
- Integration mit n8n-Workflows für Automatisierung
- Verbindung zu Entwicklungstools und -plattformen

## Voraussetzungen

Bevor Sie die OpenHands-Integration einrichten, stellen Sie sicher, dass Sie folgende Voraussetzungen erfüllen:

- Docker und Docker Compose sind installiert
- Das Dev-Server-Workflow-System ist installiert und konfiguriert
- MCP-Server sind gestartet und funktionieren korrekt
- Sie haben einen API-Schlüssel für einen unterstützten LLM-Anbieter (z.B. Anthropic Claude)

## Installation und Konfiguration

### Automatische Installation

Die einfachste Methode zur Installation und Konfiguration der OpenHands-Integration ist die Verwendung des Integrationsskripts:

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-ecosystem
./integrate-with-openhands.sh
```

Dieses Skript führt folgende Schritte aus:
1. Überprüft, ob Docker installiert ist
2. Generiert eine OpenHands-Konfiguration mit MCP-Server-Integration
3. Startet OpenHands mit der generierten Konfiguration
4. Konfiguriert die Netzwerkintegration zwischen OpenHands und MCP-Servern

### Manuelle Installation

Für eine manuelle Installation folgen Sie diesen Schritten:

1. **OpenHands-Konfiguration generieren**:
   ```bash
   cd /workspace/Dev-Server-Workflow/docker-mcp-ecosystem
   ./generate-openhands-config.py --output ~/.config/openhands/config.toml
   ```

2. **OpenHands starten**:
   ```bash
   docker run -d \
     --name openhands \
     -p 3000:3000 \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v ~/.openhands-state:/.openhands-state \
     -v ~/.config/openhands:/config \
     -v ~/workspace:/workspace \
     --network mcp-network \
     -e CONFIG_PATH=/config/config.toml \
     docker.all-hands.dev/all-hands-ai/openhands:0.37
   ```

3. **Konfiguration aktualisieren** (bei Änderungen an MCP-Servern):
   ```bash
   ./update-openhands-config.sh
   ```

## MCP-Integration

OpenHands verwendet das Model Context Protocol (MCP), um mit externen Tools zu kommunizieren. Die Integration mit MCP-Servern erfolgt über zwei Methoden:

### 1. SSE-Server (Server-Sent Events)

SSE-Server sind externe MCP-Server, die über HTTP kommunizieren. Die Konfiguration erfolgt in der `config.toml` von OpenHands:

```toml
[mcp]
sse_servers = [
    "http://mcp-filesystem:3001/mcp",
    "http://mcp-desktop-commander:3002/mcp",
    "http://mcp-sequential-thinking:3003/mcp",
    "http://mcp-github-chat:3004/mcp",
    "http://mcp-github:3005/mcp",
    "http://mcp-puppeteer:3006/mcp",
    "http://mcp-basic-memory:3007/mcp",
    "http://mcp-wikipedia:3008/mcp"
]
```

### 2. Stdio-Server

Stdio-Server sind lokale Prozesse, die über Standard-Ein-/Ausgabe kommunizieren. Sie dienen als Fallback, wenn die SSE-Server nicht verfügbar sind:

```toml
stdio_servers = [
    {
        name = "filesystem-fallback",
        command = "npx",
        args = ["-y", "@modelcontextprotocol/server-filesystem"]
    },
    {
        name = "github-fallback",
        command = "npx",
        args = ["-y", "@modelcontextprotocol/server-github"],
        env = {
            "GITHUB_TOKEN" = "${GITHUB_TOKEN}"
        }
    },
    {
        name = "memory-fallback",
        command = "npx",
        args = ["-y", "@modelcontextprotocol/server-memory"]
    }
]
```

## Verwendung mit n8n-Workflows

OpenHands kann mit n8n-Workflows integriert werden, um komplexe Automatisierungen zu ermöglichen:

### 1. OpenHands-Aktionen in n8n-Workflows

Sie können n8n-Workflows erstellen, die OpenHands-Aktionen auslösen:

1. Erstellen Sie einen neuen Workflow in n8n
2. Fügen Sie einen HTTP-Request-Knoten hinzu
3. Konfigurieren Sie den Knoten für einen POST-Request an die OpenHands-API
4. Definieren Sie die Aktion und Parameter im Request-Body

Beispiel für einen HTTP-Request an OpenHands:
```json
{
  "action": "executeTask",
  "parameters": {
    "task": "Analysiere das Repository und erstelle einen Bericht",
    "repository": "https://github.com/username/repo"
  }
}
```

### 2. n8n-Workflows von OpenHands auslösen

OpenHands kann auch n8n-Workflows auslösen:

1. Erstellen Sie einen Webhook-Trigger in n8n
2. Konfigurieren Sie OpenHands, um den Webhook aufzurufen
3. Übergeben Sie Daten von OpenHands an den Workflow

## Anpassung und Erweiterung

Sie können die OpenHands-Integration anpassen und erweitern:

### 1. Benutzerdefinierte MCP-Server

Entwickeln Sie eigene MCP-Server für spezifische Funktionen und integrieren Sie sie mit OpenHands:

1. Erstellen Sie einen neuen MCP-Server
2. Fügen Sie ihn zur Docker-Compose-Konfiguration hinzu
3. Aktualisieren Sie die OpenHands-Konfiguration

### 2. Anpassung der OpenHands-Konfiguration

Passen Sie die OpenHands-Konfiguration an Ihre Bedürfnisse an:

```toml
[core]
debug = true  # Aktiviert Debug-Logging
save_trajectory_path = "/.openhands-state/trajectories"  # Pfad für Trajektorien

[llm]
model = "claude-3-5-sonnet-20241022"  # LLM-Modell
temperature = 0.2  # Kreativität des Modells

[agent]
enable_browsing = true  # Aktiviert Web-Browsing
enable_prompt_extensions = true  # Aktiviert Prompt-Erweiterungen
```

### 3. Integration mit CI/CD-Pipelines

Integrieren Sie OpenHands in CI/CD-Pipelines für automatisierte Code-Reviews, Tests und Deployments.

## Fehlerbehebung

### Häufige Probleme

1. **Verbindungsprobleme mit MCP-Servern**:
   - Überprüfen Sie, ob die MCP-Server laufen: `docker ps | grep mcp`
   - Überprüfen Sie die Netzwerkkonfiguration: `docker network inspect mcp-network`
   - Stellen Sie sicher, dass OpenHands im selben Netzwerk ist: `docker network inspect mcp-network | grep openhands`

2. **OpenHands startet nicht**:
   - Überprüfen Sie die Logs: `docker logs openhands`
   - Überprüfen Sie die Konfiguration: `cat ~/.config/openhands/config.toml`
   - Stellen Sie sicher, dass alle erforderlichen Volumes gemountet sind

3. **LLM-API-Probleme**:
   - Überprüfen Sie den API-Schlüssel
   - Stellen Sie sicher, dass das gewählte Modell verfügbar ist
   - Überprüfen Sie die Netzwerkverbindung zum LLM-Anbieter

### Diagnose

Verwenden Sie folgende Befehle zur Diagnose von Problemen:

```bash
# OpenHands-Logs anzeigen
docker logs openhands

# OpenHands-Container-Status überprüfen
docker inspect openhands

# MCP-Server-Status überprüfen
./monitor-mcp-servers.py

# OpenHands-Konfiguration validieren
./validate-openhands-config.py
```

### Neustart und Zurücksetzen

Bei Problemen können Sie folgende Schritte ausführen:

1. **OpenHands neustarten**:
   ```bash
   docker restart openhands
   ```

2. **OpenHands-Konfiguration zurücksetzen**:
   ```bash
   ./generate-openhands-config.py --reset --output ~/.config/openhands/config.toml
   docker restart openhands
   ```

3. **Vollständiges Zurücksetzen**:
   ```bash
   docker stop openhands
   docker rm openhands
   rm -rf ~/.openhands-state/*
   ./integrate-with-openhands.sh
   ```