# Repository-Struktur

Dieses Dokument beschreibt die Struktur des Dev-Server-Workflow-Repositories nach der Aufräumaktion.

## Hauptverzeichnisse

- **docker-mcp-ecosystem**: Vollständige Docker-Compose-Konfiguration für das MCP-Server-Ökosystem mit Monitoring, Logging und weiteren Diensten.
- **docker-mcp-servers**: Minimale Docker-Compose-Konfiguration für die MCP-Server, die für die Integration mit OpenHands und n8n benötigt werden.
- **docs**: Dokumentation des Projekts.
- **scripts**: Skripte für die Installation, Konfiguration und Wartung des Projekts.
- **src**: Quellcode für die n8n-Integration und MCP-Server-Implementierung.

## Wichtige Dateien

- **IMPLEMENTATION_PLAN.md**: Detaillierter Implementierungsplan für das MCP-Server-Ökosystem und die n8n-Workflows.
- **README.md**: Hauptdokumentation des Projekts.
- **docker compose.yml**: Docker-Compose-Konfiguration für die n8n-Integration.
- **Dockerfile**: Dockerfile für den n8n-MCP-Server.

## docker-mcp-ecosystem

Dieses Verzeichnis enthält eine vollständige Docker-Compose-Konfiguration für das MCP-Server-Ökosystem mit zusätzlichen Diensten wie Monitoring, Logging und weiteren Tools. Es ist für fortgeschrittene Benutzer gedacht, die ein vollständiges Ökosystem benötigen.

## docker-mcp-servers

Dieses Verzeichnis enthält eine minimale Docker-Compose-Konfiguration für die MCP-Server, die für die Integration mit OpenHands und n8n benötigt werden. Es ist für Benutzer gedacht, die nur die MCP-Server benötigen.

Die folgenden MCP-Server sind enthalten:

1. **Filesystem MCP Server** (`mcp/filesystem`)
2. **Desktop Commander MCP Server** (`mcp/desktop-commander`)
3. **Sequential Thinking MCP Server** (`mcp/sequentialthinking`)
4. **GitHub Chat MCP Server** (`mcp/github-chat`)
5. **GitHub MCP Server** (`mcp/github`)
6. **Puppeteer MCP Server** (`mcp/puppeteer`)
7. **Basic Memory MCP Server** (`mcp/basic-memory`)
8. **Wikipedia MCP Server** (`mcp/wikipedia-mcp`)

## docs

Dieses Verzeichnis enthält die Dokumentation des Projekts, einschließlich:

- **Installation-Guide.md**: Anleitung zur Installation des Projekts.
- **MCP-Integration.md**: Anleitung zur Integration des MCP-Servers mit n8n und OpenHands.
- **MCP-OpenHands.md**: Anleitung zur Integration des MCP-Servers mit OpenHands.
- **MCP-Server-Implementation.md**: Anleitung zur Implementierung des MCP-Servers.
- **Troubleshooting.md**: Anleitung zur Fehlerbehebung.
- **Workflow-Integration.md**: Anleitung zur Integration der n8n-Workflows.

## scripts

Dieses Verzeichnis enthält Skripte für die Installation, Konfiguration und Wartung des Projekts, einschließlich:

- **cleanup.sh**: Skript zur Bereinigung des Projekts.
- **deploy.sh**: Skript zur Bereitstellung des Projekts.
- **init.sh**: Skript zur Initialisierung des Projekts.
- **mcp/**: Skripte für die MCP-Server-Integration.

## src

Dieses Verzeichnis enthält den Quellcode für die n8n-Integration und MCP-Server-Implementierung, einschließlich:

- **n8n_mcp_server.py**: Implementierung des MCP-Servers für n8n.
- **n8n_setup_main.py**: Haupteinstiegspunkt für die Installation.
- **n8n_setup_workflows_mcp.py**: Definition des n8n-Workflows für MCP-Integration.
- **ESN_Initial-Szenario/**: Implementierung des initialen Szenarios für das EcoSphere Network.