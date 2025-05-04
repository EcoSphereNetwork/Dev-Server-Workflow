# Docker-Installation für n8n Workflow Integration

Diese Anleitung beschreibt, wie Sie die n8n Workflow Integration mit Docker installieren und betreiben können.

## Voraussetzungen

- Docker und Docker Compose sind installiert
- Git ist installiert (für das Klonen des Repositories)

## Installation

1. **Klonen des Repositories**

   ```bash
   git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
   cd Dev-Server-Workflow
   ```

2. **Konfiguration anpassen**

   Erstellen Sie eine `.env`-Datei mit Ihren Konfigurationsparametern oder verwenden Sie das Startskript, das eine Beispieldatei erstellt:

   ```bash
   ./docker-start.sh help
   ```

   Bearbeiten Sie dann die `.env`-Datei und passen Sie die Werte an Ihre Umgebung an:

   ```
   # n8n Konfiguration
   N8N_URL=http://localhost:5678
   N8N_USER=admin
   N8N_PASSWORD=password
   N8N_API_KEY=

   # GitHub/GitLab Konfiguration
   GITHUB_TOKEN=your_github_token_here

   # OpenProject Konfiguration
   OPENPROJECT_URL=https://your-openproject-instance.com
   OPENPROJECT_TOKEN=your_openproject_token_here

   # Weitere Konfigurationen...
   ```

3. **Container starten**

   Verwenden Sie das Startskript, um die Container zu starten:

   ```bash
   ./docker-start.sh start
   ```

   Dies startet drei Container:
   - **n8n**: Der n8n-Server, erreichbar unter http://localhost:5678
   - **mcp-server**: Der MCP-Server, erreichbar unter http://localhost:3000
   - **setup**: Ein temporärer Container, der das Setup-Skript ausführt und dann beendet wird

4. **Setup ausführen**

   Nachdem die Container gestartet sind, können Sie das Setup-Skript ausführen, um die Workflows und Credentials einzurichten:

   ```bash
   ./docker-start.sh setup
   ```

## Verwendung

Das Startskript bietet verschiedene Befehle zur Steuerung der Container:

- **start**: Startet alle Container
  ```bash
  ./docker-start.sh start
  ```

- **stop**: Stoppt alle Container
  ```bash
  ./docker-start.sh stop
  ```

- **restart**: Startet alle Container neu
  ```bash
  ./docker-start.sh restart
  ```

- **status**: Zeigt den Status aller Container an
  ```bash
  ./docker-start.sh status
  ```

- **logs**: Zeigt die Logs aller Container oder eines bestimmten Containers an
  ```bash
  ./docker-start.sh logs
  ./docker-start.sh logs mcp-server
  ```

- **setup**: Führt das Setup-Skript aus
  ```bash
  ./docker-start.sh setup
  ```

- **help**: Zeigt die Hilfe an
  ```bash
  ./docker-start.sh help
  ```

## Zugriff auf die Dienste

- **n8n**: http://localhost:5678
  - Benutzername: admin
  - Passwort: password (oder wie in der `.env`-Datei konfiguriert)

- **MCP-Server**: http://localhost:3000
  - Der MCP-Server bietet eine JSON-RPC-API, die von OpenHands verwendet werden kann

## Fehlerbehebung

### Container starten nicht

Überprüfen Sie die Logs der Container:

```bash
./docker-start.sh logs
```

### n8n ist nicht erreichbar

Überprüfen Sie, ob der n8n-Container läuft:

```bash
./docker-start.sh status
```

Überprüfen Sie die Logs des n8n-Containers:

```bash
./docker-start.sh logs n8n
```

### MCP-Server ist nicht erreichbar

Überprüfen Sie, ob der MCP-Server-Container läuft:

```bash
./docker-start.sh status
```

Überprüfen Sie die Logs des MCP-Server-Containers:

```bash
./docker-start.sh logs mcp-server
```

### Setup-Skript schlägt fehl

Überprüfen Sie die Logs des Setup-Containers:

```bash
./docker-start.sh logs setup
```

Stellen Sie sicher, dass die `.env`-Datei korrekt konfiguriert ist und alle erforderlichen Werte enthält.
