# Dev-Server-Workflow Electron App

Diese Electron-App bietet eine Desktop-Anwendung für den Dev-Server-Workflow, mit der Sie n8n-Workflows, MCP-Server und OpenHands für die KI-gestützte Automatisierung von Entwicklungsprozessen integrieren können.

## Funktionen

- **Dashboard**: Übersicht über alle Komponenten und Systeminformationen
- **MCP-Server-Verwaltung**: Verwaltung von MCP-Servern
- **Workflow-Integration**: Integration mit n8n-Workflows
- **Dienste-Integration**: Integration mit verschiedenen Diensten wie n8n, AppFlowy, OpenProject, GitLab und Affine
- **KI-Assistent**: KI-gestützter Assistent für die Automatisierung von Entwicklungsprozessen
- **Benutzereinstellungen**: Anpassung der Anwendung an Ihre Bedürfnisse

## Voraussetzungen

- Node.js (v14 oder höher)
- npm (v6 oder höher)

## Installation

1. Klonen Sie das Repository:
   ```
   git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
   cd Dev-Server-Workflow/frontend
   ```

2. Installieren Sie die Abhängigkeiten:
   ```
   npm install
   ```

## Entwicklung

Starten Sie die Anwendung im Entwicklungsmodus:

```
./start-electron.sh --dev
```

oder

```
npm run electron:dev
```

## Build

Erstellen Sie ein AppImage für Linux:

```
./build-appimage.sh
```

oder

```
npm run electron:build
```

Die erstellten Dateien finden Sie im Verzeichnis `dist`.

## Verwendung

Nach dem Start der Anwendung können Sie:

1. Das Dashboard verwenden, um einen Überblick über alle Komponenten zu erhalten
2. MCP-Server verwalten
3. Workflows erstellen und verwalten
4. Dienste integrieren und verwalten
5. Den KI-Assistenten für die Automatisierung von Entwicklungsprozessen verwenden
6. Die Anwendung an Ihre Bedürfnisse anpassen

## Lizenz

MIT
