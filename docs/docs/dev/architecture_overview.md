# Architektur-Übersicht

Diese Dokumentation bietet einen umfassenden Überblick über die Architektur des Dev-Server-Workflow-Projekts.

## Kernkomponenten

Das Dev-Server-Workflow-Projekt besteht aus mehreren Kernkomponenten, die zusammenarbeiten, um eine umfassende Lösung für die Integration von n8n-Workflows, MCP-Servern und OpenHands für KI-gestützte Automatisierung von Entwicklungsprozessen zu bieten.

### MCP-Server

MCP (Model Context Protocol) Server stellen Tools für Clients über eine standardisierte Schnittstelle bereit. Jeder MCP-Server implementiert die `MCPServerInterface` und erweitert die `BaseMCPServer`-Klasse.

Die folgenden MCP-Server sind derzeit implementiert:

- **n8n MCP-Server**: Stellt n8n-Workflows als MCP-Tools bereit
- **OpenHands MCP-Server**: Ermöglicht die parallele Ausführung von OpenHands-Aufgaben
- **Docker MCP-Server**: Verwaltet Docker-Container über MCP
- **Generator MCP-Server**: Generiert dynamische MCP-Server
- **LLM Cost Analyzer MCP-Server**: Analysiert die Kosten von LLM-Anfragen
- **Prompt MCP-Server**: Verwaltet und optimiert Prompts für LLMs

### n8n-Integration

n8n ist eine Workflow-Automatisierungsplattform, die es ermöglicht, Workflows zu erstellen und auszuführen. Das Dev-Server-Workflow-Projekt integriert n8n, um Workflow-Automatisierungsfunktionen bereitzustellen.

Die n8n-Integration umfasst:

- **Workflow-Definitionen**: Vordefinierte Workflows für häufige Aufgaben
- **Setup-Skripte**: Skripte für die Installation und Konfiguration von n8n
- **MCP-Integration**: Integration von n8n mit dem MCP-Protokoll

### OpenHands-Integration

OpenHands ist eine Plattform für KI-gestützte Automatisierung. Das Dev-Server-Workflow-Projekt integriert OpenHands, um KI-gestützte Automatisierungsfunktionen bereitzustellen.

Die OpenHands-Integration umfasst:

- **MCP-Server**: MCP-Server für OpenHands
- **Konfiguration**: Konfigurationsdateien für OpenHands
- **Beispiele**: Beispiele für die Verwendung von OpenHands mit MCP

### CLI-Tools

Die CLI-Tools bieten eine Befehlszeilenschnittstelle für die Verwaltung des Systems:

- **Hauptschnittstelle**: `dev-server-cli.sh`
- **Interaktive Benutzeroberfläche**: `cli/interactive_ui.sh`
- **KI-Assistent**: `cli/ai_assistant_improved.sh`
- **Konfigurationsverwaltung**: `cli/config_manager.sh`
- **Fehlerbehandlung**: `cli/error_handler.sh`

### Gemeinsame Bibliotheken

Die gemeinsamen Bibliotheken bieten standardisierte Funktionen und Klassen für alle Komponenten:

- **Shell-Bibliothek**: `scripts/common/shell/common.sh`
- **Python-Bibliothek**: `src/core/`

## Architektur-Diagramm

```
+----------------------------------+
|           CLI-Tools              |
|  +----------------------------+  |
|  |     dev-server-cli.sh      |  |
|  +----------------------------+  |
|  |    interactive_ui.sh       |  |
|  +----------------------------+  |
|  |  ai_assistant_improved.sh  |  |
|  +----------------------------+  |
+----------------------------------+
              |
              v
+----------------------------------+
|        Gemeinsame Bibliotheken   |
|  +----------------------------+  |
|  |        common.sh           |  |
|  +----------------------------+  |
|  |        core/               |  |
|  +----------------------------+  |
+----------------------------------+
              |
              v
+----------------------------------+
|          MCP-Server              |
|  +----------------------------+  |
|  |     n8n MCP-Server         |  |
|  +----------------------------+  |
|  |   OpenHands MCP-Server     |  |
|  +----------------------------+  |
|  |    Docker MCP-Server       |  |
|  +----------------------------+  |
|  |   Generator MCP-Server     |  |
|  +----------------------------+  |
+----------------------------------+
              |
              v
+----------------------------------+
|        Externe Dienste           |
|  +----------------------------+  |
|  |           n8n              |  |
|  +----------------------------+  |
|  |        OpenHands           |  |
|  +----------------------------+  |
|  |          Docker            |  |
|  +----------------------------+  |
+----------------------------------+
```

## Code-Organisation

### Verzeichnisstruktur

```
Dev-Server-Workflow/
├── cli/                    # CLI-Tools
├── config/                 # Konfigurationsdateien
├── docs/                   # Dokumentation
│   ├── dev/                # Entwicklerdokumentation
│   ├── user/               # Benutzerdokumentation
│   └── api/                # API-Dokumentation
├── scripts/                # Skripte
│   ├── common/             # Gemeinsame Bibliotheken
│   ├── install/            # Installationsskripte
│   ├── setup/              # Setup-Skripte
│   └── monitoring/         # Überwachungsskripte
├── src/                    # Quellcode
│   ├── core/               # Kernmodule
│   ├── mcp/                # MCP-Server-Implementierungen
│   │   ├── base/           # Basis-MCP-Server-Klassen
│   │   ├── interfaces/     # MCP-Schnittstellen
│   │   └── servers/        # MCP-Server-Implementierungen
│   ├── n8n/                # n8n-Integration
│   ├── openhands/          # OpenHands-Integration
│   └── web_ui/             # Web-Benutzeroberfläche
├── docker/                 # Docker-Konfigurationen
│   ├── compose/            # Docker-Compose-Dateien
│   └── images/             # Dockerfiles
└── tests/                  # Tests
```

## Designprinzipien

### Modularität

Die Architektur ist modular gestaltet, wobei jede Komponente eine klar definierte Schnittstelle und Verantwortlichkeit hat. Dies ermöglicht eine einfache Erweiterung und Wartung.

### Standardisierung

Die Architektur verwendet standardisierte Schnittstellen und Protokolle, um die Interoperabilität zwischen Komponenten zu gewährleisten. Dazu gehört das Model Context Protocol (MCP) für die Kommunikation zwischen MCP-Servern und Clients.

### Wiederverwendbarkeit

Gemeinsame Funktionalitäten werden in wiederverwendbare Bibliotheken extrahiert, um Duplizierung zu vermeiden und Konsistenz im gesamten Codebase zu gewährleisten.

### Testbarkeit

Die Architektur ist so konzipiert, dass sie testbar ist, mit klarer Trennung der Belange und Dependency Injection, um Unit-Tests zu erleichtern.

### Sicherheit

Sicherheit ist ein wichtiger Aspekt der Architektur, mit angemessenen Authentifizierungs- und Autorisierungsmechanismen zum Schutz sensibler Daten und Operationen.

## Zukünftige Richtungen

### Zusätzliche MCP-Server

Die Architektur ist erweiterbar und ermöglicht die Hinzufügung neuer MCP-Server, um zusätzliche Funktionalitäten bereitzustellen.

### Verbesserte Web-Benutzeroberfläche

Eine webbasierte Benutzeroberfläche ist geplant, um eine benutzerfreundlichere Möglichkeit zur Verwaltung des Systems zu bieten.

### Tiefere OpenHands-Integration

Eine weitere Integration mit OpenHands ist geplant, um fortschrittlichere KI-gestützte Automatisierungsfunktionen bereitzustellen.

### LLM-Kostenabschätzung

Die Integration mit LLM-Kostenabschätzungstools ist geplant, um Einblicke in die Kosten der KI-gestützten Automatisierung zu geben.