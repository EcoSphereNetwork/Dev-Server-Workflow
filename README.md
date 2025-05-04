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

Weitere Befehle und Informationen zur Docker-Installation finden Sie in der [ausführlichen Docker-Anleitung](DOCKER.md).

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
n8n-workflow-integration/
├── docs/                      # Dokumentation
│   └── docs/                  # Detaillierte Dokumentation nach Themen
├── src/                       # Quellcode
│   ├── n8n_setup_main.py      # Haupteinstiegspunkt für die Installation
│   ├── n8n_setup_utils.py     # Hilfsfunktionen
│   ├── n8n_setup_install.py   # Funktionen für die Installation
│   ├── n8n_setup_credentials.py # Funktionen zur Einrichtung von Anmeldedaten
│   ├── n8n_setup_workflows/   # Workflow-Definitionen
│   │   ├── n8n_setup_workflows_github.py
│   │   ├── n8n_setup_workflows_document.py
│   │   ├── n8n_setup_workflows_openhands.py
│   │   └── n8n_setup_workflows_special.py
│   └── env-template           # Vorlage für die .env-Datei
└── README.md                  # Hauptdokumentation
```

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

1. Ein Issue wird in GitHub/GitLab erstellt und mit dem "fix-me" Label versehen.
2. n8n erkennt dies und benachrichtigt OpenHands über die API.
3. OpenHands analysiert das Issue und erstellt einen Pull Request mit der Lösung.
4. n8n erkennt den OpenHands-generierten PR und aktualisiert OpenProject und AFFiNE/AppFlowy.

Für die Einrichtung:

```bash
python src/n8n_setup_main.py --workflows openhands --env-file .env
```

Die generierte Webhook-URL muss in der OpenHands-Konfiguration eingetragen werden, damit OpenHands n8n über erstellte PRs informieren kann.

## 🧩 MCP Integration

Dieses Repository unterstützt die Integration des Model Context Protocols (MCP) für die Verbindung zwischen OpenHands und n8n. Hiermit können KI-Agenten direkt mit n8n-Workflows interagieren.

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

Der MCP-Server stellt folgende n8n-Workflows als Tools bereit:

- **create_github_issue**: Erstellt ein Issue in GitHub
- **update_work_package**: Aktualisiert ein Arbeitspaket in OpenProject
- **sync_documentation**: Synchronisiert Dokumentation zwischen AFFiNE/AppFlowy und GitHub

### Beispielnutzung in OpenHands

OpenHands kann die n8n-Tools wie folgt nutzen:

```python
# Beispiel für einen OpenHands-Agent, der ein GitHub-Issue erstellt
await agent.run("Erstelle ein GitHub-Issue für ein Problem mit der Login-Funktion")

# Der Agent kann das create_github_issue-Tool über die MCP-Schnittstelle verwenden
```

## 🔧 Fehlerbehebung

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
[credits-url]: https://github.com/YourOrganization/n8n-workflow-integration/blob/main/CREDITS.md
[activity-graph]: https://repobeats.axiom.co/api/embed/8d1a53c73cf5523d0e52a6cc5b74bce75eecc801.svg
[activity-url]: https://repobeats.axiom.co
