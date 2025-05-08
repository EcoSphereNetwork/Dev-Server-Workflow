# MCP-Server und n8n-Workflow Integration

Dieses Projekt integriert Model Context Protocol (MCP) Server in Docker-Containern mit n8n-Workflows, um eine nahtlose Kommunikation zwischen verschiedenen Diensten zu ermöglichen.

## Architektur

Die Architektur besteht aus folgenden Komponenten:

1. **Docker-Container**:
   - n8n: Workflow-Automatisierung
   - MCP-Server: GitHub, GitLab, OpenProject, AppFlowy
   - PostgreSQL: Datenbank für n8n
   - Redis: Cache und Message Broker
   - Nginx: Reverse Proxy

2. **MCP-Server**:
   - Implementieren das Model Context Protocol
   - Bieten Tools für verschiedene Dienste an
   - Kommunizieren über JSON-RPC

3. **n8n-Workflows**:
   - Nutzen benutzerdefinierte MCP-Nodes
   - Automatisieren Prozesse zwischen verschiedenen Diensten
   - Reagieren auf Events von MCP-Servern

Weitere Details zur Architektur findest du in der [ARCHITECTURE.md](./ARCHITECTURE.md) Datei.

## Voraussetzungen

- Docker und Docker Compose
- Git
- Node.js (für die Entwicklung)
- API-Zugangsdaten für GitHub, GitLab, OpenProject, AppFlowy

## Installation

1. Repository klonen:
   ```bash
   git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
   cd Dev-Server-Workflow/docker
   ```

2. Umgebungsvariablen konfigurieren:
   ```bash
   cp .env.example .env
   # Bearbeite die .env-Datei mit deinen API-Zugangsdaten
   ```

3. Docker-Container starten:
   ```bash
   docker compose up -d
   ```

4. Auf n8n zugreifen:
   ```
   https://localhost/
   ```

## MCP-Server

### GitHub MCP-Server

Der GitHub MCP-Server bietet folgende Tools:
- `github_create_issue`: Erstellt ein neues Issue in einem GitHub-Repository
- `github_get_issues`: Ruft Issues aus einem GitHub-Repository ab
- `github_create_pull_request`: Erstellt einen neuen Pull Request in einem GitHub-Repository
- `github_get_repository`: Ruft Informationen über ein GitHub-Repository ab
- `github_get_file_content`: Ruft den Inhalt einer Datei aus einem GitHub-Repository ab

### GitLab MCP-Server

Der GitLab MCP-Server bietet folgende Tools:
- `gitlab_create_issue`: Erstellt ein neues Issue in einem GitLab-Projekt
- `gitlab_get_issues`: Ruft Issues aus einem GitLab-Projekt ab
- `gitlab_create_merge_request`: Erstellt einen neuen Merge Request in einem GitLab-Projekt
- `gitlab_get_project`: Ruft Informationen über ein GitLab-Projekt ab
- `gitlab_get_file_content`: Ruft den Inhalt einer Datei aus einem GitLab-Projekt ab

### OpenProject MCP-Server

Der OpenProject MCP-Server bietet folgende Tools:
- `openproject_create_work_package`: Erstellt ein neues Work Package in OpenProject
- `openproject_get_work_packages`: Ruft Work Packages aus OpenProject ab
- `openproject_update_work_package`: Aktualisiert ein bestehendes Work Package in OpenProject
- `openproject_get_project`: Ruft Informationen über ein OpenProject-Projekt ab
- `openproject_get_users`: Ruft Benutzer aus OpenProject ab

### AppFlowy MCP-Server

Der AppFlowy MCP-Server bietet folgende Tools:
- `appflowy_create_document`: Erstellt ein neues Dokument in AppFlowy
- `appflowy_get_documents`: Ruft Dokumente aus AppFlowy ab
- `appflowy_update_document`: Aktualisiert ein bestehendes Dokument in AppFlowy
- `appflowy_create_database`: Erstellt eine neue Datenbank in AppFlowy
- `appflowy_add_database_row`: Fügt eine Zeile zu einer AppFlowy-Datenbank hinzu

## n8n-Nodes

### MCP Node

Der MCP Node ermöglicht die Interaktion mit MCP-Servern und bietet folgende Operationen:
- `listTools`: Listet verfügbare Tools auf dem MCP-Server auf
- `callTool`: Ruft ein Tool auf dem MCP-Server auf

### MCP Trigger Node

Der MCP Trigger Node startet einen Workflow, wenn ein MCP-Server ein Event sendet. Er unterstützt folgende Event-Typen:
- GitHub Events
- GitLab Events
- OpenProject Events
- AppFlowy Events

## Workflows

### GitHub Issue zu GitLab Issue

Dieser Workflow erstellt automatisch ein GitLab Issue, wenn ein neues GitHub Issue erstellt wird. Der Workflow:
1. Wird durch ein GitHub Issue-Erstellungsereignis ausgelöst
2. Ruft die Details des GitHub Issues ab
3. Erstellt ein entsprechendes GitLab Issue
4. Fügt einen Kommentar zum GitHub Issue hinzu, der auf das GitLab Issue verweist
5. Sendet eine E-Mail-Benachrichtigung

### OpenProject Work Package zu AppFlowy Document

Dieser Workflow erstellt automatisch ein AppFlowy-Dokument, wenn ein neues OpenProject Work Package erstellt wird. Der Workflow:
1. Wird durch ein OpenProject Work Package-Erstellungsereignis ausgelöst
2. Ruft die Details des Work Packages ab
3. Erstellt ein entsprechendes AppFlowy-Dokument mit den Informationen aus dem Work Package
4. Aktualisiert das Work Package mit einem Link zum AppFlowy-Dokument
5. Sendet eine E-Mail-Benachrichtigung

## Entwicklung

### Hinzufügen eines neuen MCP-Servers

1. Erstelle einen neuen Ordner unter `mcp-servers/`:
   ```bash
   mkdir -p mcp-servers/new-service
   ```

2. Erstelle die erforderlichen Dateien:
   - `Dockerfile`
   - `package.json`
   - `server.js`

3. Implementiere das Model Context Protocol in `server.js`

4. Aktualisiere die Docker-Compose-Datei:
   ```yaml
   new-service-mcp:
     build:
       context: ./mcp-servers/new-service
       dockerfile: Dockerfile
     restart: always
     environment:
       - MCP_PORT=3005
       - ...
   ```

### Hinzufügen eines neuen Workflows

1. Erstelle eine neue JSON-Datei unter `workflows/`:
   ```bash
   touch workflows/new-workflow.json
   ```

2. Definiere den Workflow in der JSON-Datei

3. Importiere den Workflow in n8n:
   - Öffne n8n im Browser
   - Gehe zu "Workflows"
   - Klicke auf "Import from File"
   - Wähle die JSON-Datei aus
   - Konfiguriere die Credentials
   - Aktiviere den Workflow

### Anpassen der MCP-Server

Jeder MCP-Server kann angepasst werden, um zusätzliche Tools bereitzustellen:

1. Öffne die `server.js`-Datei des entsprechenden MCP-Servers
2. Füge ein neues Tool zur `handleListTools`-Funktion hinzu
3. Implementiere die entsprechende Handler-Funktion
4. Aktualisiere die `handleCallTool`-Funktion, um das neue Tool zu unterstützen

## Fehlerbehebung

### MCP-Server startet nicht

Überprüfe die Logs:
```bash
docker compose logs github-mcp
```

### n8n kann nicht mit MCP-Servern kommunizieren

Überprüfe die Nginx-Konfiguration und die Firewall-Einstellungen:
```bash
docker compose logs nginx
```

### Redis-Verbindungsprobleme

Überprüfe die Redis-Verbindung:
```bash
docker compose exec redis redis-cli ping
```

### Workflow-Ausführungsfehler

Überprüfe die n8n-Logs:
```bash
docker compose logs n8n
```

## Lizenz

MIT