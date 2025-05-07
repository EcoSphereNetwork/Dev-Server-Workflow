# Architektur: MCP-Server und n8n-Workflow Integration

## Übersicht

Die Integration von MCP-Servern in Docker-Containern mit n8n-Workflows ermöglicht eine nahtlose Kommunikation zwischen verschiedenen Diensten und Systemen. Diese Architektur nutzt das Model Context Protocol (MCP), um eine standardisierte Schnittstelle für KI-Agenten und Automatisierungssysteme bereitzustellen.

## Komponenten

### Docker-Container

```
+----------------------------------+
|           Docker Host            |
|                                  |
|  +------------+  +------------+  |
|  |    n8n     |  |   Nginx    |  |
|  +------------+  +------------+  |
|                                  |
|  +------------+  +------------+  |
|  | GitHub MCP |  | GitLab MCP |  |
|  +------------+  +------------+  |
|                                  |
|  +------------+  +------------+  |
|  |OpenProject |  | AppFlowy   |  |
|  |    MCP     |  |    MCP     |  |
|  +------------+  +------------+  |
|                                  |
|  +------------+  +------------+  |
|  | PostgreSQL |  |   Redis    |  |
|  +------------+  +------------+  |
|                                  |
+----------------------------------+
```

- **n8n**: Workflow-Automatisierungsplattform
- **Nginx**: Reverse Proxy für die Weiterleitung von Anfragen
- **MCP-Server**: Implementierungen des Model Context Protocols für verschiedene Dienste
- **PostgreSQL**: Datenbank für n8n
- **Redis**: Cache und Message Broker für die Kommunikation zwischen Containern

### MCP-Server

Jeder MCP-Server implementiert das Model Context Protocol und bietet Tools für die Interaktion mit einem spezifischen Dienst an.

```
+------------------+
|    MCP-Server    |
|                  |
| +-------------+  |
| | HTTP Server |  |
| +-------------+  |
|                  |
| +-------------+  |
| | JSON-RPC    |  |
| | Handler     |  |
| +-------------+  |
|                  |
| +-------------+  |
| | Tool        |  |
| | Registry    |  |
| +-------------+  |
|                  |
| +-------------+  |
| | Service     |  |
| | API Client  |  |
| +-------------+  |
|                  |
+------------------+
```

- **HTTP Server**: Empfängt HTTP-Anfragen
- **JSON-RPC Handler**: Verarbeitet JSON-RPC-Anfragen gemäß dem MCP-Protokoll
- **Tool Registry**: Verwaltet die verfügbaren Tools
- **Service API Client**: Kommuniziert mit dem entsprechenden Dienst (GitHub, GitLab, etc.)

### n8n-Nodes

Die benutzerdefinierten n8n-Nodes ermöglichen die Interaktion mit MCP-Servern innerhalb von n8n-Workflows.

```
+------------------+
|    n8n-Nodes     |
|                  |
| +-------------+  |
| | MCP Node    |  |
| +-------------+  |
|                  |
| +-------------+  |
| | MCP Trigger |  |
| | Node        |  |
| +-------------+  |
|                  |
+------------------+
```

- **MCP Node**: Ruft Tools auf MCP-Servern auf
- **MCP Trigger Node**: Startet Workflows basierend auf Events von MCP-Servern

## Datenfluss

```
+--------+    JSON-RPC    +-----------+    API     +--------+
|  n8n   | ------------> | MCP-Server | ---------> | Service |
+--------+                +-----------+            +--------+
    ^                          |                       |
    |                          v                       v
    |                    +-----------+            +--------+
    +-------------------- |   Redis   | <--------- | Events |
                         +-----------+            +--------+
```

1. n8n sendet JSON-RPC-Anfragen an MCP-Server
2. MCP-Server kommunizieren mit den entsprechenden Diensten
3. Dienste senden Events zurück an MCP-Server
4. MCP-Server speichern Events in Redis
5. n8n-Trigger-Nodes fragen Events von Redis ab

## Kommunikationsprotokolle

### MCP-Protokoll (JSON-RPC 2.0)

```json
// Anfrage
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.listTools",
  "params": {}
}

// Antwort
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "name": "github_create_issue",
      "description": "Create a new issue in a GitHub repository",
      "parameter_schema": {
        "type": "object",
        "properties": {
          "repository": {
            "type": "string",
            "description": "The repository in format owner/repo"
          },
          "title": {
            "type": "string",
            "description": "The title of the issue"
          },
          // ...
        },
        "required": ["repository", "title"]
      }
    },
    // ...
  ]
}
```

### n8n-Workflow-Format

```json
{
  "name": "GitHub Issue to GitLab Issue",
  "nodes": [
    {
      "parameters": {
        "pollInterval": 10,
        "eventTypes": ["github"]
      },
      "name": "GitHub MCP Trigger",
      "type": "n8n-nodes-mcp.mcpTrigger",
      // ...
    },
    // ...
  ],
  "connections": {
    // ...
  }
}
```

## Sicherheit

- **API-Schlüssel**: Jeder MCP-Server verwendet API-Schlüssel für die Authentifizierung mit dem entsprechenden Dienst
- **HTTPS**: Nginx ist für SSL/TLS-Terminierung konfiguriert
- **Container-Isolation**: Jeder MCP-Server läuft in einem eigenen Container
- **Netzwerk-Segmentierung**: Docker-Netzwerke isolieren die Kommunikation zwischen Containern

## Skalierbarkeit

- **Horizontale Skalierung**: Mehrere Instanzen von MCP-Servern können hinter einem Load Balancer betrieben werden
- **Vertikale Skalierung**: Container-Ressourcen können je nach Bedarf angepasst werden
- **Microservices-Architektur**: Neue MCP-Server können einfach hinzugefügt werden, ohne bestehende Komponenten zu beeinträchtigen

## Erweiterbarkeit

- **Neue MCP-Server**: Weitere Dienste können durch Implementierung neuer MCP-Server integriert werden
- **Benutzerdefinierte Tools**: Jeder MCP-Server kann neue Tools hinzufügen
- **Workflow-Vorlagen**: Neue Workflows können als Vorlagen bereitgestellt werden