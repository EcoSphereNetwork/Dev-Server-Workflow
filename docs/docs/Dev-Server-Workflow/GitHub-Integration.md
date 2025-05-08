# GitHub-Integration für MCP-Server

Diese Dokumentation beschreibt die Integration der MCP-Server mit GitHub.

## Übersicht

Die GitHub-Integration ermöglicht es den MCP-Servern, mit GitHub zu interagieren, um Repositories zu verwalten, Issues zu erstellen, Pull Requests zu kommentieren und vieles mehr. Die Integration besteht aus zwei Hauptkomponenten:

1. **GitHub MCP Server**: Ein MCP-Server, der die GitHub API verwendet, um mit GitHub zu interagieren.
2. **GitHub Chat MCP Server**: Ein MCP-Server, der speziell für die Interaktion mit GitHub-Diskussionen und -Kommentaren konzipiert ist.

## Voraussetzungen

- GitHub-Konto
- GitHub Personal Access Token mit den erforderlichen Berechtigungen
- Laufende MCP-Server

## GitHub Personal Access Token

Um die GitHub-Integration zu verwenden, benötigen Sie einen GitHub Personal Access Token mit den folgenden Berechtigungen:

- `repo`: Vollständiger Zugriff auf private und öffentliche Repositories
- `read:user`: Lesen von Benutzerinformationen
- `read:org`: Lesen von Organisationsinformationen (optional, nur erforderlich, wenn Sie mit Organisationsrepositorien arbeiten)

### Token erstellen

1. Gehen Sie zu [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Klicken Sie auf "Generate new token"
3. Geben Sie einen Namen für das Token ein, z.B. "MCP Server Integration"
4. Wählen Sie die erforderlichen Berechtigungen aus:
   - `repo`
   - `read:user`
   - `read:org` (optional)
5. Klicken Sie auf "Generate token"
6. Kopieren Sie das generierte Token (es wird nur einmal angezeigt)

### Token-Sicherheit

Der GitHub Personal Access Token gewährt Zugriff auf Ihre GitHub-Repositories und sollte daher sicher aufbewahrt werden. Beachten Sie die folgenden Sicherheitshinweise:

- Teilen Sie das Token nicht mit anderen Personen
- Speichern Sie das Token nicht in öffentlichen Repositories
- Verwenden Sie ein Token mit minimalen Berechtigungen
- Rotieren Sie das Token regelmäßig
- Überwachen Sie die Verwendung des Tokens

## Integration konfigurieren

### Automatische Konfiguration

Die einfachste Methode zur Konfiguration der GitHub-Integration ist die Verwendung des Integrationsskripts:

```bash
cd /workspace/Dev-Server-Workflow
./scripts/github-integration.py --github-token YOUR_GITHUB_TOKEN --repo OWNER/REPO
```

Das Skript führt die folgenden Schritte aus:

1. Validiert den GitHub-Token
2. Überprüft die Token-Berechtigungen
3. Aktualisiert die `.env`-Datei mit dem Token
4. Konfiguriert einen GitHub-Webhook für das Repository (optional)

### Manuelle Konfiguration

Wenn Sie die GitHub-Integration manuell konfigurieren möchten, folgen Sie diesen Schritten:

1. Bearbeiten Sie die `.env`-Datei und fügen Sie Ihren GitHub-Token hinzu:

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-servers
echo "GITHUB_TOKEN=YOUR_GITHUB_TOKEN" >> .env
```

2. Starten Sie die MCP-Server neu:

```bash
cd /workspace/Dev-Server-Workflow/docker-mcp-servers
./stop-mcp-servers.sh
./start-mcp-servers.sh
```

3. Konfigurieren Sie einen GitHub-Webhook (optional):

   a. Gehen Sie zu Ihrem GitHub-Repository
   b. Klicken Sie auf "Settings" > "Webhooks" > "Add webhook"
   c. Geben Sie die Webhook-URL ein: `http://YOUR_SERVER_URL:5678/webhook/github-to-openproject`
   d. Wählen Sie "Content type: application/json"
   e. Wählen Sie die Ereignisse aus, die den Webhook auslösen sollen (z.B. Issues, Pull Requests, Pushes)
   f. Klicken Sie auf "Add webhook"

## Verwendung

### GitHub MCP Server

Der GitHub MCP Server bietet die folgenden Funktionen:

- Repository-Informationen abrufen
- Issues erstellen, aktualisieren und schließen
- Pull Requests erstellen, aktualisieren und schließen
- Commits und Branches verwalten
- Dateien lesen und schreiben

Beispiel für die Verwendung des GitHub MCP Servers:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "create_github_issue",
    "arguments": {
      "owner": "OWNER",
      "repo": "REPO",
      "title": "Test Issue",
      "body": "This is a test issue created by the GitHub MCP Server"
    }
  }
}
```

### GitHub Chat MCP Server

Der GitHub Chat MCP Server bietet die folgenden Funktionen:

- Kommentare zu Issues erstellen
- Kommentare zu Pull Requests erstellen
- Auf Kommentare antworten
- Diskussionen erstellen und verwalten

Beispiel für die Verwendung des GitHub Chat MCP Servers:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.callTool",
  "params": {
    "name": "create_github_comment",
    "arguments": {
      "owner": "OWNER",
      "repo": "REPO",
      "issue_number": 1,
      "body": "This is a test comment created by the GitHub Chat MCP Server"
    }
  }
}
```

## Integration mit n8n

Die GitHub-Integration kann mit n8n-Workflows verwendet werden, um automatisierte Prozesse zu erstellen. Die n8n-Workflows können die GitHub-Ereignisse verarbeiten und entsprechende Aktionen ausführen.

Beispiel für einen n8n-Workflow, der GitHub-Issues in OpenProject-Arbeitspakete konvertiert:

1. GitHub-Webhook-Trigger: Empfängt GitHub-Ereignisse
2. Switch-Node: Filtert nach Issue-Ereignissen
3. HTTP-Request-Node: Ruft Details zum Issue ab
4. OpenProject-Node: Erstellt ein Arbeitspaket in OpenProject
5. HTTP-Response-Node: Sendet eine Antwort an GitHub

## Fehlerbehebung

Wenn Sie Probleme mit der GitHub-Integration haben:

1. Überprüfen Sie, ob der GitHub-Token gültig ist:
   ```bash
   curl -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/user
   ```

2. Überprüfen Sie die Token-Berechtigungen:
   ```bash
   curl -I -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/user
   ```
   Suchen Sie nach dem Header `X-OAuth-Scopes`, der die Berechtigungen des Tokens anzeigt.

3. Überprüfen Sie die Logs der MCP-Server:
   ```bash
   docker-compose logs github-mcp
   docker-compose logs github-chat-mcp
   ```

4. Überprüfen Sie die Webhook-Konfiguration:
   a. Gehen Sie zu Ihrem GitHub-Repository
   b. Klicken Sie auf "Settings" > "Webhooks"
   c. Klicken Sie auf den Webhook
   d. Überprüfen Sie die "Recent Deliveries", um zu sehen, ob der Webhook erfolgreich ausgelöst wurde

## Referenzen

- [GitHub API-Dokumentation](https://docs.github.com/en/rest)
- [GitHub Webhooks-Dokumentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks/about-webhooks)
- [GitHub Personal Access Tokens-Dokumentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)