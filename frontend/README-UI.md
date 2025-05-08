# Dev-Server Web-UI

Die Dev-Server Web-UI ist eine Benutzeroberfläche für den Dev-Server, die es ermöglicht, verschiedene Dienste zu verwalten und zu überwachen.

## Funktionen

- **Dashboard**: Übersicht über den Status aller Komponenten
- **MCP-Server**: Verwaltung der MCP-Server
- **Workflows**: Verwaltung der n8n-Workflows
- **Dienste**: Integration verschiedener Dienste wie n8n, AppFlowy, OpenProject, GitLab und Affine
- **Einstellungen**: Konfiguration des Dev-Servers
- **KI-Assistent**: Integrierter KI-Assistent für die Steuerung des Dev-Servers

## Dienste-Integration

Die Web-UI ermöglicht die Integration verschiedener Dienste über die folgenden Subdomains:

- **n8n**: n8n.ecospherenet.work
- **AppFlowy**: appflowy.ecospherenet.work
- **OpenProject**: openproject.ecospherenet.work
- **GitLab**: gitlab.ecospherenet.work
- **Affine**: affine.ecospherenet.work
- **Dev-Server**: dev-server.ecospherenet.work

## Installation

### Voraussetzungen

- Docker und Docker Compose
- Node.js und npm (für die Entwicklung)
- Einträge in der /etc/hosts-Datei für die Subdomains

### Hosts-Datei konfigurieren

Fügen Sie die folgenden Einträge zu Ihrer /etc/hosts-Datei hinzu:

```
127.0.0.1 dev-server.ecospherenet.work
127.0.0.1 n8n.ecospherenet.work
127.0.0.1 appflowy.ecospherenet.work
127.0.0.1 openproject.ecospherenet.work
127.0.0.1 gitlab.ecospherenet.work
127.0.0.1 affine.ecospherenet.work
```

### Web-UI starten

```bash
./start-web-ui.sh
```

### Web-UI stoppen

```bash
./stop-web-ui.sh
```

## Entwicklung

### Abhängigkeiten installieren

```bash
cd frontend
npm install
```

### Entwicklungsserver starten

```bash
cd frontend
npm start
```

### Anwendung bauen

```bash
cd frontend
npm run build
```

### Electron-App starten

```bash
cd frontend
npm run electron-dev
```

### Electron-App bauen

```bash
cd frontend
npm run electron-build
```

## Konfiguration

Die Konfiguration der Dienste erfolgt in der Datei `src/config/services.ts`. Hier können Sie die URLs und andere Eigenschaften der Dienste anpassen.

## KI-Assistent

Der KI-Assistent ermöglicht die Steuerung des Dev-Servers über natürliche Sprache. Er kann über die Schaltfläche in der Navigationsleiste oder über die Tastenkombination `Strg+Shift+A` aufgerufen werden.

## Standalone-App

Die Standalone-App basiert auf Electron und bietet die gleichen Funktionen wie die Web-UI, jedoch mit zusätzlichen Funktionen für die Integration mit dem Betriebssystem.

### Funktionen der Standalone-App

- **Dienste-Integration**: Integration der Dienste in der Anwendung
- **Systembenachrichtigungen**: Benachrichtigungen über den Status der Dienste
- **Offline-Modus**: Verwendung der Anwendung ohne Internetverbindung
- **Automatischer Start**: Automatischer Start der Anwendung beim Systemstart