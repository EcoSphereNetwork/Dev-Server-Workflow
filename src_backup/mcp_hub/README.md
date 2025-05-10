# MCP Hub

Ein Hub für MCP Server, der das Suchen, Installieren und Verwalten von MCP Servern ermöglicht.

## Features

- **Server-Registry**: Verwaltet eine Registry von verfügbaren MCP Servern
- **Server-Installation**: Installiert MCP Server aus verschiedenen Quellen
- **Server-Verwaltung**: Startet, stoppt und überwacht MCP Server
- **GitHub-Integration**: Durchsucht GitHub-Repositories nach MCP Servern
- **Docker Hub-Integration**: Durchsucht Docker Hub nach MCP Server-Images
- **Kommandozeilenschnittstelle**: Bietet eine einfache Kommandozeilenschnittstelle für die Interaktion mit dem Hub

## Architektur

Der MCP Hub besteht aus folgenden Komponenten:

1. **Hub Manager**: Hauptklasse für die Verwaltung des Hubs
2. **Registry**: Verwaltet die Registry von verfügbaren MCP Servern
3. **Installer**: Installiert und deinstalliert MCP Server
4. **CLI**: Kommandozeilenschnittstelle für die Interaktion mit dem Hub

## Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/mcp-hub.git
cd mcp-hub

# Abhängigkeiten installieren
pip install -e .

# Oder mit Poetry
poetry install
```

## Verwendung

### Kommandozeilenschnittstelle

```bash
# Aktualisiere die Registry
mcp-hub update

# Suche nach MCP Servern
mcp-hub search llm

# Installiere einen MCP Server
mcp-hub install llm-cost-analyzer

# Liste alle installierten MCP Server auf
mcp-hub list

# Starte einen MCP Server
mcp-hub start llm-cost-analyzer

# Stoppe einen MCP Server
mcp-hub stop llm-cost-analyzer

# Zeige den Status eines MCP Servers an
mcp-hub status llm-cost-analyzer

# Füge ein Repository hinzu
mcp-hub add-repo https://github.com/punkpeye/awesome-mcp-servers

# Füge einen Docker Hub Benutzer hinzu
mcp-hub add-docker-user mcp
```

### Programmatische Verwendung

```python
from mcp_hub import MCPHubManager

# Erstelle den Hub Manager
hub_manager = MCPHubManager()

# Aktualisiere die Registry
hub_manager.update_registry()

# Suche nach MCP Servern
results = hub_manager.search_servers("llm")

# Installiere einen MCP Server
hub_manager.install_server("llm-cost-analyzer")

# Liste alle installierten MCP Server auf
servers = hub_manager.list_installed_servers()

# Starte einen MCP Server
hub_manager.start_server("llm-cost-analyzer")

# Stoppe einen MCP Server
hub_manager.stop_server("llm-cost-analyzer")

# Zeige den Status eines MCP Servers an
status = hub_manager.get_server_status("llm-cost-analyzer")
```

## Konfiguration

Der MCP Hub kann über eine Konfigurationsdatei konfiguriert werden:

```json
{
  "repositories": [
    "https://github.com/punkpeye/awesome-mcp-servers",
    "https://github.com/appcypher/awesome-mcp-servers"
  ],
  "docker_hub_users": [
    "mcp"
  ],
  "local_servers_path": "/path/to/mcp_servers",
  "auto_update": true,
  "update_interval_hours": 24
}
```

## Unterstützte Repositories

Der MCP Hub unterstützt folgende Repositories:

- [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- [awesome-mcp-servers](https://github.com/appcypher/awesome-mcp-servers)

## Unterstützte Docker Hub Benutzer

Der MCP Hub unterstützt folgende Docker Hub Benutzer:

- [mcp](https://hub.docker.com/u/mcp)

## Lizenz

MIT