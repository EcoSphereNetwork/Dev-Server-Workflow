# EcoSphere Network Workflow Integration

![EcoSphere Network Logo](/img/logo.png)

## Übersicht

Die EcoSphere Network Workflow Integration ist eine umfassende Lösung zur Integration verschiedener Entwicklungstools und -plattformen. Sie ermöglicht eine nahtlose Zusammenarbeit zwischen GitHub/GitLab, OpenProject, AFFiNE/AppFlowy und OpenHands durch automatisierte Workflows und KI-gestützte Prozesse.

## Hauptkomponenten

Das Projekt besteht aus zwei Hauptkomponenten:

1. **n8n Workflow Integration**: Eine Sammlung von n8n-Workflows zur Automatisierung von Prozessen zwischen verschiedenen Tools.
2. **MCP Server Ökosystem**: Eine Implementierung des Model Context Protocols (MCP) für die Integration von KI-Agenten mit den Workflows.

## Funktionen

- **GitHub/GitLab zu OpenProject**: Synchronisierung von Issues und Pull Requests
- **Dokumenten-Synchronisierung**: Synchronisierung von Dokumenten zwischen AFFiNE/AppFlowy, GitHub und OpenProject
- **OpenHands Integration**: KI-gestützte Lösung von Issues und Erstellung von Pull Requests
- **MCP Server**: Bereitstellung von Tools für KI-Agenten zur Interaktion mit dem Entwicklungsökosystem

## Schnellstart

### Docker-Installation (empfohlen)

```bash
# Klonen des Repositories
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow

# Starten der Docker-Container
docker-compose up -d
```

### MCP-Server starten

```bash
cd docker-mcp-servers
./start-mcp-servers.sh
```

## Dokumentationsstruktur

Diese Dokumentation ist in folgende Abschnitte unterteilt:

- **[Installation und Konfiguration](Installation-Guide.md)**: Anleitung zur Installation und Konfiguration des Systems
- **[Workflows](Workflow-Integration.md)**: Beschreibung der verfügbaren n8n-Workflows
- **[MCP Server](MCP-Server-Implementation.md)**: Dokumentation der MCP-Server-Implementierung
- **[OpenHands Integration](MCP-OpenHands.md)**: Integration mit OpenHands
- **[Fehlerbehebung](Troubleshooting.md)**: Hilfe bei häufigen Problemen

## Architektur

Die Architektur des Systems basiert auf einem modularen Ansatz, bei dem verschiedene Komponenten über definierte Schnittstellen miteinander kommunizieren:

```
+----------------+    +----------------+    +----------------+
|                |    |                |    |                |
|  GitHub/GitLab |<-->|      n8n       |<-->|   OpenProject  |
|                |    |                |    |                |
+----------------+    +-------+--------+    +----------------+
                             ^
                             |
                             v
+----------------+    +------+--------+    +----------------+
|                |    |               |    |                |
| AFFiNE/AppFlowy|<-->|  MCP Servers  |<-->|   OpenHands    |
|                |    |               |    |                |
+----------------+    +---------------+    +----------------+
```

## Beitragen

Wir freuen uns über Beiträge zum Projekt! Weitere Informationen finden Sie in der [CONTRIBUTING.md](https://github.com/EcoSphereNetwork/Dev-Server-Workflow/blob/main/CONTRIBUTING.md) Datei.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen finden Sie in der [LICENSE](https://github.com/EcoSphereNetwork/Dev-Server-Workflow/blob/main/LICENSE) Datei.