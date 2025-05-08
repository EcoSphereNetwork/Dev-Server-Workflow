# Installationsanleitung

Diese Anleitung beschreibt die Installation und Konfiguration der EcoSphere Network Workflow Integration mit n8n und MCP-Servern.

## Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass folgende Voraussetzungen erfüllt sind:

- **Docker und Docker Compose** (empfohlen für einfache Installation)
- **Python 3.8+** (für manuelle Installation)
- **Git** (zum Klonen des Repositories)
- **API-Zugangsdaten** für folgende Dienste (je nach Bedarf):
  - GitHub oder GitLab Personal Access Token
  - OpenProject API-Token
  - AFFiNE/AppFlowy Zugangsdaten
  - Discord Webhook URL (optional)

## Installationsmethoden

Es gibt zwei Hauptmethoden zur Installation des Systems:

1. **Docker-Installation** (empfohlen): Einfache Installation mit Docker Compose
2. **Manuelle Installation**: Für fortgeschrittene Benutzer oder spezielle Anforderungen

## Docker-Installation (empfohlen)

### 1. Repository klonen

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Konfigurationsdatei erstellen

```bash
cp .env.example .env
```

Bearbeiten Sie die `.env`-Datei und fügen Sie Ihre API-Zugangsdaten ein:

```ini
# n8n Konfiguration
N8N_URL=http://localhost:5678
N8N_USER=admin
N8N_PASSWORD=password

# GitHub/GitLab Konfiguration
GITHUB_TOKEN=your_github_token_here

# OpenProject Konfiguration
OPENPROJECT_URL=https://your-openproject-instance.com
OPENPROJECT_TOKEN=your_openproject_token_here

# MCP Server Konfiguration
MCP_SERVER_PORT=3000
```

### 3. Docker-Container starten

```bash
docker-compose up -d
```

Dies startet folgende Container:
- **n8n**: Workflow-Automatisierungsplattform (Port 5678)
- **mcp-server**: MCP-Server für die Integration mit OpenHands (Port 3000)
- **setup**: Einmaliger Container zur Konfiguration der Workflows

### 4. MCP-Server starten

```bash
cd docker-mcp-servers
./start-mcp-servers.sh
```

Dies startet die folgenden MCP-Server:
- **Filesystem MCP**: Dateisystem-Operationen (Port 3001)
- **Desktop Commander MCP**: Terminal-Befehle (Port 3002)
- **Sequential Thinking MCP**: Strukturierte Problemlösung (Port 3003)
- **GitHub Chat MCP**: GitHub-Diskussionen (Port 3004)
- **GitHub MCP**: GitHub-Repository-Management (Port 3005)
- **Puppeteer MCP**: Web-Browsing (Port 3006)
- **Basic Memory MCP**: Schlüssel-Wert-Speicher (Port 3007)
- **Wikipedia MCP**: Wikipedia-Suche (Port 3008)
- **MCP Inspector UI**: Weboberfläche für MCP-Server (Port 8080)

## Manuelle Installation

### 1. Repository klonen

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Konfigurationsdatei erstellen

```bash
cp src/env-template .env
```

Bearbeiten Sie die `.env`-Datei mit Ihren API-Zugangsdaten.

### 3. Python-Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. n8n installieren (falls noch nicht vorhanden)

```bash
npm install n8n -g
```

### 5. Workflows einrichten

```bash
python setup.py install --env-file .env
```

Dieses Skript führt folgende Aktionen aus:
- Einrichtung der Credentials für die verschiedenen Dienste
- Erstellung und Aktivierung der Workflows
- Einrichtung des MCP-Servers (wenn `--mcp` angegeben ist)

### 6. Spezifische Workflows installieren

Sie können auch spezifische Workflows installieren:

```bash
python setup.py install --env-file .env --workflows github document openhands
```

Verfügbare Workflows:
- `github`: GitHub zu OpenProject Integration
- `document`: Dokumenten-Synchronisierung
- `openhands`: OpenHands Integration
- `discord`: Discord Benachrichtigungen
- `timetracking`: Zeit-Tracking
- `ai`: KI-gestützte Zusammenfassungen
- `mcp`: MCP Integration
- `all`: Alle Workflows (Standard)

### 7. MCP-Server einrichten

```bash
python setup.py install --env-file .env --mcp
```

Dies erstellt die MCP-Server-Konfiguration und generiert die `openhands-mcp-config.json`-Datei.

## Überprüfung der Installation

### Testen der n8n-Installation

Überprüfen Sie, ob n8n korrekt läuft:

```bash
# Bei Docker-Installation
docker-compose ps

# Bei manueller Installation
curl http://localhost:5678/healthz
```

### Testen der MCP-Server

Überprüfen Sie, ob die MCP-Server korrekt laufen:

```bash
cd docker-mcp-servers
./test-mcp-servers.py
```

Oder testen Sie einen spezifischen MCP-Server:

```bash
./test-mcp-servers.py --server filesystem-mcp
```

### Überprüfen der Workflows

Öffnen Sie die n8n-Weboberfläche unter http://localhost:5678 und melden Sie sich an (Standard: admin/password).
Überprüfen Sie, ob die Workflows korrekt importiert und aktiviert wurden.

## Zugriff auf die Komponenten

Nach erfolgreicher Installation können Sie auf folgende Komponenten zugreifen:

- **n8n**: http://localhost:5678 (Benutzername: admin, Passwort: password)
- **MCP Inspector UI**: http://localhost:8080
- **MCP-Server API**: http://localhost:3000

## Fehlerbehebung

### Docker-bezogene Probleme

#### Container starten nicht

```bash
# Überprüfen Sie den Status der Container
docker-compose ps

# Überprüfen Sie die Logs
docker-compose logs n8n
docker-compose logs mcp-server
```

#### Netzwerkprobleme

```bash
# Überprüfen Sie die Docker-Netzwerke
docker network ls
docker network inspect n8n-network
```

### n8n-bezogene Probleme

#### n8n ist nicht erreichbar

- Überprüfen Sie, ob der n8n-Container läuft: `docker-compose ps n8n`
- Überprüfen Sie die n8n-Logs: `docker-compose logs n8n`
- Stellen Sie sicher, dass Port 5678 nicht von einem anderen Dienst verwendet wird

#### Workflow-Aktivierung schlägt fehl

- Überprüfen Sie, ob alle erforderlichen Credentials eingerichtet sind
- Überprüfen Sie die n8n-Logs auf spezifische Fehlermeldungen
- Stellen Sie sicher, dass die API-Tokens gültig sind und die richtigen Berechtigungen haben

### MCP-Server-Probleme

#### MCP-Server starten nicht

```bash
# Überprüfen Sie den Status der MCP-Server
cd docker-mcp-servers
docker-compose ps

# Überprüfen Sie die Logs
docker-compose logs filesystem-mcp
```

#### Verbindungsprobleme zwischen n8n und MCP-Servern

- Stellen Sie sicher, dass beide im selben Docker-Netzwerk sind oder über die richtigen Ports kommunizieren können
- Überprüfen Sie die Firewall-Einstellungen
- Testen Sie die Verbindung mit `curl http://localhost:3001/health`

## Weitere Ressourcen

- [MCP-Server-Dokumentation](MCP-Server-Implementation.md)
- [Workflow-Integration](Workflow-Integration.md)
- [OpenHands-Integration](MCP-OpenHands.md)
- [Ausführliche Fehlerbehebung](Troubleshooting.md)