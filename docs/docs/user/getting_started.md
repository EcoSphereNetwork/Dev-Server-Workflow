# Erste Schritte

Diese Dokumentation bietet einen umfassenden Leitfaden für den Einstieg in das Dev-Server-Workflow-Projekt.

## Übersicht

Das Dev-Server-Workflow-Projekt ist eine umfassende Lösung für die Integration von n8n-Workflows, MCP-Servern und OpenHands für KI-gestützte Automatisierung von Entwicklungsprozessen.

## Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass Sie Folgendes installiert haben:

- Python 3.8 oder höher
- Docker und Docker Compose
- Git
- Node.js und npm (für n8n)

## Installation

### 1. Klonen Sie das Repository

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Installieren Sie die Abhängigkeiten

```bash
# Erstellen Sie eine virtuelle Umgebung
python3 -m venv venv

# Aktivieren Sie die virtuelle Umgebung
# Unter Linux/macOS
source venv/bin/activate
# Unter Windows
venv\Scripts\activate

# Installieren Sie die Abhängigkeiten
pip install -r requirements.txt
```

### 3. Richten Sie die Umgebungsvariablen ein

Erstellen Sie eine `.env`-Datei im Stammverzeichnis des Projekts:

```bash
# Erstellen Sie die .env-Datei
cp .env.example .env

# Bearbeiten Sie die .env-Datei
nano .env
```

Füllen Sie die erforderlichen Umgebungsvariablen aus:

```
# n8n-Konfiguration
N8N_URL=http://localhost:5678
N8N_API_KEY=your-api-key

# OpenHands-Konfiguration
OPENHANDS_PORT=3000
OPENHANDS_API_KEY=your-api-key

# MCP-Server-Konfiguration
MCP_HTTP_PORT=3333
MCP_AUTH_TOKEN=your-auth-token

# LLM-Konfiguration
LLM_API_KEY=your-api-key
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
```

## Starten der Dienste

### Starten von n8n

```bash
# Starten Sie n8n
./scripts/start-n8n.sh
```

### Starten der MCP-Server

```bash
# Starten Sie alle MCP-Server
./scripts/start-all-mcp-servers.sh --http
```

### Starten von OpenHands

```bash
# Starten Sie OpenHands
./scripts/start-openhands.sh
```

## Verwendung

### Befehlszeilenschnittstelle

Das Projekt bietet eine Befehlszeilenschnittstelle für die Verwaltung des Systems:

```bash
./dev-server-cli.sh --help
```

### Web-Benutzeroberfläche

Das Projekt bietet auch eine webbasierte Benutzeroberfläche für die Verwaltung des Systems:

```bash
./start-web-ui.sh
```

Öffnen Sie dann http://localhost:8080 in Ihrem Browser.

## Beispiele

### Beispiel 1: Ausführen eines n8n-Workflows über MCP

```bash
# Führen Sie einen n8n-Workflow über MCP aus
curl -X POST http://localhost:3456/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "run_workflow",
      "arguments": {
        "workflow_id": "1",
        "parameters": {}
      }
    }
  }'
```

### Beispiel 2: Ausführen einer OpenHands-Aufgabe über MCP

```bash
# Führen Sie eine OpenHands-Aufgabe über MCP aus
curl -X POST http://localhost:3457/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "run_task",
      "arguments": {
        "task": "Analysiere den Code in der Datei example.py",
        "context": {
          "file": "example.py",
          "content": "def hello_world():\\n    print(\\"Hello, World!\\")"
        }
      }
    }
  }'
```

### Beispiel 3: Verwalten von Docker-Containern über MCP

```bash
# Verwalten Sie Docker-Container über MCP
curl -X POST http://localhost:3458/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "list_containers",
      "arguments": {
        "all": true
      }
    }
  }'
```

## Fehlerbehebung

### Häufige Probleme

#### Docker Compose-Probleme

Wenn Sie Probleme mit Docker Compose haben, versuchen Sie Folgendes:

```bash
# Stoppen Sie alle Container
docker-compose down

# Entfernen Sie alle Container
docker-compose rm -f

# Starten Sie die Container erneut
docker-compose up -d
```

#### n8n-Probleme

Wenn n8n nicht richtig funktioniert, versuchen Sie Folgendes:

```bash
# Starten Sie n8n neu
./scripts/stop-n8n.sh
./scripts/start-n8n.sh
```

#### MCP-Server-Probleme

Wenn MCP-Server nicht richtig funktionieren, versuchen Sie Folgendes:

```bash
# Starten Sie MCP-Server neu
./scripts/stop-all-mcp-servers.sh
./scripts/start-all-mcp-servers.sh --http
```

### Hilfe erhalten

Wenn Sie Hilfe benötigen, können Sie:

- Ein Issue auf GitHub öffnen
- Die Projektbetreuer kontaktieren
- Die Dokumentation überprüfen