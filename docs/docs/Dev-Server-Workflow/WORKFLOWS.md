# n8n-Workflows

Dieses Dokument beschreibt die n8n-Workflows für die Integration verschiedener Systeme im Dev-Server-Workflow-Projekt.

## Übersicht

Die n8n-Workflows bieten eine robuste und flexible Integration zwischen verschiedenen Systemen wie GitHub, GitLab, OpenProject, AppFlowy und den MCP-Servern. Die Workflows sind so konzipiert, dass sie nahtlos miteinander kommunizieren und Daten zwischen den verschiedenen Systemen synchronisieren.

## Workflows

### 1. Integration-Hub (integration-hub.json)

Der Integration-Hub ist der zentrale Einstiegspunkt für alle Ereignisse. Er normalisiert die eingehenden Daten und leitet sie an die entsprechenden spezifischen Workflows weiter.

**Funktionen:**
- Normalisierung der eingehenden Ereignisdaten
- Routing der Ereignisse basierend auf dem Quelltyp
- Bestimmung zusätzlicher Workflows, die ausgeführt werden sollen
- Fehlerbehandlung und Protokollierung

### 2. GitHub zu OpenProject (github-to-openproject.json)

Dieser Workflow synchronisiert GitHub-Issues, Pull Requests und Pushes mit OpenProject-Arbeitspaketen.

**Funktionen:**
- Normalisierung der GitHub-Ereignisdaten
- Suche nach existierenden Arbeitspaketen
- Erstellung oder Aktualisierung von Arbeitspaketen in OpenProject
- Synchronisierung mit AppFlowy

### 3. MCP-Server zu OpenProject (mcp-server-to-openproject.json)

Dieser Workflow synchronisiert MCP-Server-Ereignisse mit OpenProject-Arbeitspaketen.

**Funktionen:**
- Normalisierung der MCP-Ereignisdaten
- Analyse der Ereignisse mit einem LLM-Agenten
- Suche nach existierenden Arbeitspaketen
- Erstellung oder Aktualisierung von Arbeitspaketen in OpenProject
- Synchronisierung mit AppFlowy
- Benachrichtigung bei kritischen Ereignissen

### 4. Fehlerbehandlung (error-handler.json)

Dieser Workflow behandelt Fehler, die in anderen Workflows auftreten.

**Funktionen:**
- Formatierung der Fehlerinformationen
- Automatische Wiederholung bei temporären Fehlern
- Erstellung von Arbeitspaketen für Fehler in OpenProject
- Benachrichtigung bei Fehlern
- Protokollierung in AppFlowy

## Installation

### Automatische Installation

Die einfachste Methode zur Installation der verbesserten Workflows ist die Verwendung des Hauptinstallationsskripts:

```bash
cd /workspace/Dev-Server-Workflow
./install-all.sh
```

Das Skript führt die folgenden Schritte aus:

1. Installiert die MCP-Server
2. Startet die MCP-Server
3. Installiert n8n
4. Integriert die MCP-Server mit n8n
5. Integriert die MCP-Server mit OpenHands

### Manuelle Installation

Wenn Sie die verbesserten Workflows manuell installieren möchten, folgen Sie diesen Schritten:

1. Installieren Sie die MCP-Server:

```bash
cd /workspace/Dev-Server-Workflow
./install-mcp-servers.sh
```

2. Starten Sie die MCP-Server:

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-servers
./start-mcp-servers.sh
```

3. Installieren Sie n8n:

```bash
npm install -g n8n
```

4. Starten Sie n8n:

```bash
n8n start
```

5. Integrieren Sie die MCP-Server mit n8n:

```bash
cd /workspace/Dev-Server-Workflow
./scripts/integrate-mcp-with-n8n.py --n8n-api-key YOUR_N8N_API_KEY
```

6. Integrieren Sie die MCP-Server mit OpenHands:

```bash
cd /workspace/Dev-Server-Workflow
./scripts/integrate-mcp-with-openhands.py --openhands-config-dir /path/to/openhands/config --github-token YOUR_GITHUB_TOKEN
```

## Verwendung

### Auslösen der Workflows

Die Workflows können über ihre Webhook-Endpunkte ausgelöst werden:

- Integration-Hub: `http://localhost:5678/webhook/event`
- GitHub zu OpenProject: `http://localhost:5678/webhook/github-to-openproject`
- MCP zu OpenProject: `http://localhost:5678/webhook/mcp-to-openproject`

### Beispiel für eine Anfrage an den Integration-Hub

```bash
curl -X POST http://localhost:5678/webhook/event \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "github",
    "event_type": "issues",
    "title": "Test Issue",
    "description": "This is a test issue",
    "status": "open",
    "repository": "username/repo",
    "url": "https://github.com/username/repo/issues/1"
  }'
```

## Dokumentation

Weitere Informationen zu den verbesserten Workflows finden Sie in der folgenden Dokumentation:

- [Verbesserte Workflow-Integration](docs/docs/Dev-Server-Workflow/Improved-Workflow-Integration.md)
- [MCP-Server-Implementierungsanleitung](docs/docs/Dev-Server-Workflow/MCP-Server-Implementation-Guide.md)
- [MCP-OpenHands-Integration](docs/docs/Dev-Server-Workflow/MCP-OpenHands.md)

## Fehlerbehebung

### Workflow-Fehler

Wenn ein Workflow einen Fehler auslöst, wird der Fehlerbehandlungs-Workflow ausgeführt. Dieser Workflow:

1. Versucht, den fehlgeschlagenen Workflow bis zu dreimal erneut auszuführen
2. Erstellt ein Arbeitspaket in OpenProject mit den Fehlerdetails
3. Sendet eine Benachrichtigung über den Fehler
4. Protokolliert den Fehler in AppFlowy

### Häufige Probleme

- **Webhook-Fehler**: Stellen Sie sicher, dass die Webhook-URLs korrekt sind und die n8n-Instanz erreichbar ist.
- **Authentifizierungsfehler**: Überprüfen Sie die API-Schlüssel und Credentials in n8n.
- **Fehlende Umgebungsvariablen**: Stellen Sie sicher, dass alle erforderlichen Umgebungsvariablen konfiguriert sind.
- **Verbindungsprobleme**: Überprüfen Sie die Verbindung zu den externen Systemen (GitHub, GitLab, OpenProject, AppFlowy).