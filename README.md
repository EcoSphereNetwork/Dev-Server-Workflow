# n8n Workflow Integration für AFFiNE, AppFlowy, GitHub/GitLab, OpenProject und OpenHands

<div align="center">
  <img src="./docs/static/img/logo.png" alt="Logo" width="200">
  <h1>EcoSphere Network Workflow Integration</h1>
  <p>Eine moderne, umfassende Lösung für die Integration von verschiedenen Tools im EcoSphere Network Ecosystem.</p>

  [![Contributors][contributors-shield]][contributors-url]
  [![Stars][stars-shield]][stars-url]
  [![Coverage][coverage-shield]][coverage-url]
  [![MIT License][license-shield]][license-url]
  <br/>
  [![Discord][discord-shield]][discord-url]
  [![Documentation][docs-shield]][docs-url]
  [![Project Credits][credits-shield]][credits-url]

  [Start Documentation](https://github.com/EcoSphereNetwork/ESN_Repo-Template/blob/main/docs/README.md) •
  [Report Bug](https://github.com/EcoSphereNetwork/ESN_Repo-Template/issues) •
  [Request Feature](https://github.com/EcoSphereNetwork/ESN_Repo-Template/issues)
</div>

## 📋 Inhaltsverzeichnis
- [Über das Projekt](#-über-das-projekt)
- [Wichtige Funktionen](#-wichtige-funktionen)
- [Erste Schritte](#-erste-schritte)
- [Projektstruktur](#-projektstruktur)
- [Dev-Server CLI](#-dev-server-cli)
- [Workflows](#-workflows)
- [OpenHands Integration](#-openhands-integration)
- [MCP Integration](#-mcp-integration)
- [Fehlerbehebung](#-fehlerbehebung)
- [Mitwirken](#-mitwirken)
- [Lizenz](#-lizenz)

## 🎯 Über das Projekt
Dieses Paket enthält modulare Skripte zur Einrichtung und Konfiguration von n8n-Workflows für die Integration der folgenden Tools:

- AFFiNE / AppFlowy (Wissensmanagement)
- GitLab / GitHub (Code-Repository)
- OpenProject (Projektmanagement)
- OpenHands (KI-gestützte Issue-Lösung)

Die Integration ermöglicht eine nahtlose Zusammenarbeit zwischen den verschiedenen Tools und automatisiert den Informationsfluss zwischen ihnen. Durch die Nutzung von n8n als zentrale Workflow-Automatisierungsplattform können komplexe Arbeitsprozesse vereinfacht und standardisiert werden.

## ✨ Wichtige Funktionen

### Kern-Features
- 🔄 **Automatisierung**: Automatische Synchronisierung von Daten zwischen allen beteiligten Systemen
- 🤖 **KI-Integration**: Integration von OpenHands für KI-gestützte Issue-Lösung
- 🌐 **Universelle Konnektivität**: Verbindung zu allen wichtigen Entwicklertools und -plattformen
- 📊 **Transparenz**: Automatisierte Berichte und Benachrichtigungen
- 🔌 **MCP Support**: Model Context Protocol Integration für fortschrittliche KI-Agenten

### Workflow-Tools
- 📝 **Dokumentensynchronisierung**: Automatische Synchronisierung von Dokumentationen zwischen AFFiNE/AppFlowy und GitHub
- 🐛 **Issue-Tracking**: Automatische Erstellung und Verfolgung von Issues in OpenProject
- 🕰️ **Zeit-Tracking**: Extraktion von Zeit-Tracking-Informationen aus Commit-Nachrichten
- 📢 **Discord-Integration**: Automatische Benachrichtigungen über wichtige Ereignisse

## 🚀 Erste Schritte

### Voraussetzungen
- **Für direkte Installation**: Python 3.6+
- **Für Docker-Installation**: Docker und Docker Compose
- Gültige API-Keys für die zu integrierenden Dienste

### Installation

#### 🐳 Option 1: Docker-Installation (empfohlen)

Die Docker-Installation ist der einfachste Weg, um die n8n Workflow Integration einzurichten. Sie benötigen nur Docker und Docker Compose.

1. **Klonen des Repositories**

   ```bash
   git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
   cd Dev-Server-Workflow
   ```

2. **Konfiguration erstellen**
   
   ```bash
   ./docker-start.sh help
   # Dies erstellt eine .env-Datei, wenn keine vorhanden ist
   # Bearbeiten Sie die .env-Datei und füllen Sie alle benötigten Werte aus
   ```

3. **Docker-Container starten**

   ```bash
   ./docker-start.sh start
   ```

4. **Setup ausführen**

   ```bash
   ./docker-start.sh setup
   ```

5. **Zugriff auf die Dienste**
   - n8n: http://localhost:5678 (Benutzername: admin, Passwort: password)
   - MCP-Server: http://localhost:3000

Weitere Befehle und Informationen zur Docker-Installation finden Sie in der [ausführlichen Docker-Anleitung](docs/docs/Dev-Server-Workflow/DOCKER.md).

#### Option 2: Direkte Installation

Wenn Sie eine direkte Installation ohne Docker bevorzugen:

1. **Klonen des Repositories**

   ```bash
   git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
   cd Dev-Server-Workflow
   ```

2. **Erstellen der Konfigurationsdatei**

   ```bash
   cp src/env-template .env
   # Bearbeiten Sie die .env Datei und füllen Sie alle benötigten Werte aus
   ```

3. **Installation und Konfiguration mit dem Setup-Skript**

   ```bash
   python setup.py install --env-file .env
   ```

   Oder für spezifische Workflows:

   ```bash
   python setup.py install --env-file .env --workflows github document openhands
   ```

   Für die MCP-Integration:

   ```bash
   python setup.py install --env-file .env --mcp
   ```

4. **Testen der Installation**

   ```bash
   python setup.py test
   ```

## 📁 Projektstruktur

```
Dev-Server-Workflow/
├── ARCHITECTURE.md            # Überblick über die Architektur und Beziehungen zwischen Komponenten
├── cli/                       # Dev-Server CLI für die Verwaltung aller Komponenten
├── docker-mcp-ecosystem/      # Vollständiges MCP-Server-Ökosystem mit Monitoring und Logging
├── docker-mcp-servers/        # Minimale MCP-Server-Konfiguration für OpenHands und n8n
├── docs/                      # Dokumentation
│   └── docs/                  # Detaillierte Dokumentation nach Themen
├── scripts/                   # Skripte für Installation, Konfiguration und Wartung
│   ├── generate-common-config.py # Generiert gemeinsame Konfigurationsdateien für beide Implementierungen
│   ├── test-implementations.py # Automatisierte Tests für beide Implementierungen
│   └── mcp/                   # Skripte für MCP-Server-Integration
├── src/                       # Quellcode
│   ├── n8n_mcp_server.py      # MCP-Server-Implementierung für n8n
│   ├── n8n_setup_main.py      # Haupteinstiegspunkt für die Installation
│   ├── n8n_setup_utils.py     # Hilfsfunktionen
│   ├── n8n_setup_install.py   # Funktionen für die Installation
│   ├── n8n_setup_credentials.py # Funktionen zur Einrichtung von Anmeldedaten
│   ├── n8n_setup_workflows_github.py # GitHub-Workflow-Definition
│   ├── n8n_setup_workflows_document.py # Dokumenten-Workflow-Definition
│   ├── n8n_setup_workflows_openhands.py # OpenHands-Workflow-Definition
│   ├── n8n_setup_workflows_mcp.py # MCP-Workflow-Definition
│   ├── n8n_setup_workflows_special.py # Spezielle Workflow-Definitionen
│   └── env-template           # Vorlage für die .env-Datei
├── docs/docs/Dev-Server-Workflow/IMPLEMENTATION_PLAN.md     # Detaillierter Implementierungsplan
├── docs/docs/Dev-Server-Workflow/REPOSITORY_STRUCTURE.md    # Dokumentation der Repository-Struktur
└── README.md                  # Hauptdokumentation
```

Weitere Details zur Repository-Struktur finden Sie in der [REPOSITORY_STRUCTURE.md](docs/docs/Dev-Server-Workflow/REPOSITORY_STRUCTURE.md) Datei.

### Architektur und Beziehungen zwischen Komponenten

Dieses Projekt enthält zwei alternative Implementierungen des MCP-Server-Ökosystems:

1. **docker-mcp-ecosystem**: Eine umfassende Lösung mit allen Komponenten (MCP-Server, n8n, Monitoring, OpenHands)
2. **docker-mcp-servers**: Eine fokussierte Lösung nur für die MCP-Server

Diese Implementierungen sind nicht dafür ausgelegt, gleichzeitig zu laufen, da sie die gleichen Ports und Container-Namen verwenden.

Für eine detaillierte Erklärung der Architektur, der Beziehungen zwischen den Komponenten und Empfehlungen, welche Implementierung für welchen Anwendungsfall zu verwenden ist, lesen Sie die [ARCHITECTURE.md](ARCHITECTURE.md) Datei.

## 🖥️ Dev-Server CLI

Die Dev-Server CLI ist eine umfassende Befehlszeilenschnittstelle zur Verwaltung aller Komponenten des Dev-Server-Workflows. Sie bietet eine einheitliche Schnittstelle zum Starten, Stoppen, Konfigurieren und Überwachen der verschiedenen Dienste sowie eine Integration mit KI-Modellen für die Unterstützung bei der Administration.

### Installation der CLI

```bash
# Installation der CLI
sudo ./cli/install.sh
```

### Grundlegende Befehle

```bash
# Hilfe anzeigen
dev-server help

# Status aller Komponenten anzeigen
dev-server status

# Interaktives Menü öffnen
dev-server menu

# Komponente starten
dev-server start mcp

# Komponente stoppen
dev-server stop n8n

# Logs anzeigen
dev-server logs ollama
```

### KI-Integration

Die CLI unterstützt zwei LLM-Backends für die KI-Integration:

1. **Llamafile** (lokal): Ein lokales LLM, das keine Internetverbindung benötigt
2. **Claude** (Anthropic API): Ein leistungsstarkes Cloud-LLM mit API-Zugriff

```bash
# KI-Befehl ausführen
dev-server ai "Wie starte ich den MCP-Server?"

# Zwischen LLMs wechseln
dev-server switch-llm llamafile
dev-server switch-llm claude
```

Weitere Informationen zur CLI finden Sie in der [CLI-Dokumentation](cli/README.md).

## 📊 Workflows

### 1. GitHub zu OpenProject Integration

Synchronisiert Issues und Pull Requests zwischen GitHub/GitLab und OpenProject.

- Issues in GitHub/GitLab werden als Arbeitspakete in OpenProject angelegt
- Pull Requests aktualisieren den Status von Arbeitspaketen
- Issues können mit dem "fix-me" Label versehen werden, um OpenHands zu aktivieren

### 2. Dokumenten-Synchronisierung

Synchronisiert Dokumente zwischen AFFiNE/AppFlowy, GitHub und OpenProject.

- Änderungen an Dokumenten in AFFiNE/AppFlowy werden nach GitHub und OpenProject repliziert
- Erkennung und Auflösung von Konflikten bei gleichzeitigen Änderungen
- Benachrichtigungen bei Konflikten

### 3. OpenHands Integration

Integriert OpenHands für die KI-gestützte Lösung von Issues.

- Erkennung und Verarbeitung von OpenHands-generierten Pull Requests
- Aktualisierung des Status in OpenProject
- Erstellung von Dokumenten in AFFiNE/AppFlowy zur Dokumentation der Änderungen
- Discord-Benachrichtigungen (optional)

### 4. Zusätzliche Workflows

- **Discord Benachrichtigungen**: Sendet Benachrichtigungen über GitHub/GitLab-Ereignisse an Discord
- **Zeit-Tracking**: Extrahiert Zeit-Tracking-Informationen aus Commit-Nachrichten und überträgt sie nach OpenProject
- **KI-gestützte Zusammenfassungen**: Erzeugt wöchentliche Zusammenfassungen von Repository-Aktivitäten

## 🤖 OpenHands Integration

Die OpenHands Integration ermöglicht die automatische Lösung von Issues durch KI. Dies funktioniert wie folgt:

1. Ein Issue wird in GitHub/GitLab erstellt und mit dem "fix-me" Label versehen oder mit `@openhands-agent` in einem Kommentar erwähnt.
2. Der OpenHands Issue Resolver wird aktiviert und analysiert das Issue.
3. OpenHands erstellt einen Pull Request mit der Lösung.
4. n8n erkennt den OpenHands-generierten PR und aktualisiert OpenProject und AFFiNE/AppFlowy.

### OpenHands Issue Resolver

Dieses Repository ist mit dem OpenHands Issue Resolver konfiguriert, der automatisch Issues in GitHub und GitLab lösen kann. Der Resolver kann auf zwei Arten aktiviert werden:

1. **Mit dem `fix-me` Label**: Fügen Sie das Label zu einem Issue hinzu, um den Resolver zu aktivieren.
2. **Mit `@openhands-agent` Erwähnung**: Erwähnen Sie `@openhands-agent` in einem Kommentar, um den Resolver zu aktivieren.

Für die vollständige Einrichtung und Konfiguration des OpenHands Issue Resolvers, siehe die [OpenHands Resolver Dokumentation](OPENHANDS_RESOLVER.md).

### n8n Workflow Integration

Für die Einrichtung der n8n Workflow Integration mit OpenHands:

```bash
python src/n8n_setup_main.py --workflows openhands --env-file .env
```

Die generierte Webhook-URL muss in der OpenHands-Konfiguration eingetragen werden, damit OpenHands n8n über erstellte PRs informieren kann.

## 🧩 MCP Integration

Dieses Repository unterstützt die Integration des Model Context Protocols (MCP) für die Verbindung zwischen OpenHands und n8n. Hiermit können KI-Agenten direkt mit n8n-Workflows interagieren.

### Verbesserte MCP-Skripte

Die MCP-Skripte wurden überarbeitet, um folgende Verbesserungen zu implementieren:

1. **Gemeinsame Bibliothek**: Eine zentrale Bibliothek (`scripts/common/mcp_common.sh`) wurde erstellt, die gemeinsame Funktionen und Konfigurationen enthält. Dies reduziert Code-Duplikation und verbessert die Wartbarkeit.

2. **Konsistente Konfiguration**: Umgebungsvariablen werden aus einer zentralen `.env`-Datei geladen und mit sinnvollen Standardwerten versehen.

3. **Verbesserte Fehlerbehandlung**: Die Skripte enthalten nun eine robustere Fehlerbehandlung und Logging.

4. **Modularisierung**: Die Funktionalität wurde in kleinere, wiederverwendbare Funktionen aufgeteilt.

5. **Dokumentation**: Alle Skripte enthalten ausführliche Kommentare und Hilfe-Funktionen.

### MCP-Server Implementierung

Wir haben folgende MCP-Server implementiert:

1. **Filesystem MCP Server** (`mcp/filesystem`): Ermöglicht Dateisystem-Operationen wie Lesen, Schreiben und Suchen von Dateien.
2. **Desktop Commander MCP Server** (`mcp/desktop-commander`): Ermöglicht die Ausführung von Terminal-Befehlen und Desktop-Operationen.
3. **Sequential Thinking MCP Server** (`mcp/sequentialthinking`): Bietet strukturierte Problemlösungsfähigkeiten.
4. **GitHub Chat MCP Server** (`mcp/github-chat`): Ermöglicht die Interaktion mit GitHub-Diskussionen und -Kommentaren.
5. **GitHub MCP Server** (`mcp/github`): Bietet GitHub-Repository-Management-Funktionen.
6. **Puppeteer MCP Server** (`mcp/puppeteer`): Ermöglicht Web-Browsing und Interaktion mit Webseiten.
7. **Basic Memory MCP Server** (`mcp/basic-memory`): Bietet einfache Schlüssel-Wert-Speicherung für KI-Agenten.
8. **Wikipedia MCP Server** (`mcp/wikipedia-mcp`): Ermöglicht die Suche und das Abrufen von Informationen aus Wikipedia.

Die MCP-Server sind als Docker-Container implementiert und können mit dem folgenden Befehl gestartet werden:

```bash
cd docker-mcp-servers
./setup.sh
```

Alternativ können Sie die verbesserten Skripte verwenden:

```bash
# Installation der MCP-Server
./scripts/mcp/install-mcp.sh

# Starten der MCP-Server
./start-mcp-servers.sh

# Stoppen der MCP-Server
./stop-mcp-servers.sh

# Beheben von Problemen mit MCP-Servern
./scripts/mcp/fix-mcp-errors.sh
```

### MCP-Server Konfiguration

1. Aktivieren Sie den MCP-Server:

```bash
python src/n8n_setup_main.py --install --env-file .env --mcp
```

2. Die Konfiguration für OpenHands wird in der Datei `openhands-mcp-config.json` erstellt.

3. Integrieren Sie diese in Ihr OpenHands-Setup:
   - Kopieren Sie die Datei in Ihr OpenHands-Verzeichnis
   - Fügen Sie den Pfad zur Konfiguration in die OpenHands-Umgebungsvariable ein oder konfigurieren Sie OpenHands entsprechend

### Verfügbare MCP-Tools

Die MCP-Server stellen folgende Tools bereit:

#### Filesystem MCP Server
- **read_file**: Liest den Inhalt einer Datei
- **write_file**: Schreibt Inhalt in eine Datei
- **list_directory**: Listet den Inhalt eines Verzeichnisses auf
- **search_files**: Sucht nach Dateien mit bestimmten Kriterien

#### Desktop Commander MCP Server
- **execute_command**: Führt einen Terminal-Befehl aus
- **edit_text**: Bearbeitet Text in einer Datei
- **open_application**: Öffnet eine Anwendung

#### GitHub MCP Server
- **create_issue**: Erstellt ein Issue in GitHub
- **create_pull_request**: Erstellt einen Pull Request
- **list_repositories**: Listet Repositories auf
- **get_repository_content**: Ruft den Inhalt eines Repositories ab

#### n8n-Workflows als MCP-Tools
- **create_github_issue**: Erstellt ein Issue in GitHub
- **update_work_package**: Aktualisiert ein Arbeitspaket in OpenProject
- **sync_documentation**: Synchronisiert Dokumentation zwischen AFFiNE/AppFlowy und GitHub

### Beispielnutzung in OpenHands

OpenHands kann die MCP-Tools wie folgt nutzen:

```python
# Beispiel für einen OpenHands-Agent, der ein GitHub-Issue erstellt
await agent.run("Erstelle ein GitHub-Issue für ein Problem mit der Login-Funktion")

# Der Agent kann das create_github_issue-Tool über die MCP-Schnittstelle verwenden

# Beispiel für einen OpenHands-Agent, der eine Datei liest
await agent.run("Lies den Inhalt der Datei README.md")

# Der Agent kann das read_file-Tool des Filesystem MCP Servers verwenden
```

## 🔧 Fehlerbehebung

Für eine detaillierte Anleitung zur Fehlerbehebung, siehe die [Troubleshooting-Dokumentation](./docs/docs/troubleshooting/index.md).

### GitHub Integration

- **Problem**: Webhook wird nicht ausgelöst
  **Lösung**: Überprüfen Sie die Webhook-Konfiguration in GitHub und stellen Sie sicher, dass das `Content-Type` auf `application/json` gesetzt ist

- **Problem**: OpenHands Issue-Resolver reagiert nicht auf Issues
  **Lösung**: Stellen Sie sicher, dass das Label "fix-me" korrekt hinzugefügt wurde und der LLM-API-Key korrekt konfiguriert ist

### n8n-Workflows

- **Problem**: Workflow-Ausführungen schlagen fehl
  **Lösung**: Überprüfen Sie die n8n-Logs und stellen Sie sicher, dass alle Credentials korrekt eingerichtet sind

- **Problem**: Webhook-URLs sind nicht erreichbar
  **Lösung**: Stellen Sie sicher, dass n8n öffentlich erreichbar ist oder konfigurieren Sie n8n für Webhook-Tunneling

### MCP Integration

- **Problem**: MCP-Server ist nicht erreichbar
  **Lösung**: Überprüfen Sie, ob der MCP-Server läuft und die Port-Weiterleitungen korrekt konfiguriert sind

- **Problem**: OpenHands kann keine Verbindung zum MCP-Server herstellen
  **Lösung**: Überprüfen Sie die Konfiguration in `openhands-mcp-config.json` und stellen Sie sicher, dass die Umgebungsvariablen korrekt gesetzt sind

### Docker Issues

- **Problem**: Docker-Container starten nicht
  **Lösung**: Überprüfen Sie die Docker-Logs mit `docker logs <container-name>` und stellen Sie sicher, dass alle erforderlichen Umgebungsvariablen gesetzt sind

- **Problem**: Port-Konflikte
  **Lösung**: Ändern Sie die Port-Mappings in der Docker-Compose-Datei oder stoppen Sie konkurrierende Dienste

## 🤝 Mitwirken

Wir freuen uns über Beiträge! Hier sind einige Möglichkeiten, wie Sie mitwirken können:

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/amazing-feature`)
3. Committen Sie Ihre Änderungen (`git commit -m 'feat: add amazing feature'`)
4. Pushen Sie zum Branch (`git push origin feature/amazing-feature`)
5. Öffnen Sie einen Pull Request

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen finden Sie in der [LICENSE](LICENSE)-Datei.

---

<div align="center">

### Repository-Aktivität

[![Repository Activity][activity-graph]][activity-url]

</div>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/YourOrganization/n8n-workflow-integration?style=for-the-badge&color=blue
[contributors-url]: https://github.com/YourOrganization/n8n-workflow-integration/graphs/contributors
[stars-shield]: https://img.shields.io/github/stars/YourOrganization/n8n-workflow-integration?style=for-the-badge&color=blue
[stars-url]: https://github.com/YourOrganization/n8n-workflow-integration/stargazers
[coverage-shield]: https://img.shields.io/codecov/c/github/YourOrganization/n8n-workflow-integration?style=for-the-badge&color=blue
[coverage-url]: https://codecov.io/github/YourOrganization/n8n-workflow-integration
[license-shield]: https://img.shields.io/github/license/YourOrganization/n8n-workflow-integration?style=for-the-badge&color=blue
[license-url]: https://github.com/YourOrganization/n8n-workflow-integration/blob/main/LICENSE
[discord-shield]: https://img.shields.io/badge/Discord-Join%20Us-purple?logo=discord&logoColor=white&style=for-the-badge
[discord-url]: https://discord.gg/cTWBHGkn
[docs-shield]: https://img.shields.io/badge/Documentation-000?logo=googledocs&logoColor=FFE165&style=for-the-badge
[docs-url]: https://github.com/YourOrganization/n8n-workflow-integration/wiki
[credits-shield]: https://img.shields.io/badge/Project-Credits-blue?style=for-the-badge&color=FFE165&logo=github&logoColor=white
[credits-url]: https://github.com/YourOrganization/n8n-workflow-integration/blob/main/docs/docs/Dev-Server-Workflow/CREDITS.md
[activity-graph]: https://repobeats.axiom.co/api/embed/8d1a53c73cf5523d0e52a6cc5b74bce75eecc801.svg
[activity-url]: https://repobeats.axiom.co
