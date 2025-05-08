# n8n-Workflow-Integration

Diese Dokumentation beschreibt die n8n-Workflows, die das Herzstück der EcoSphere Network Workflow Integration bilden und die nahtlose Zusammenarbeit zwischen verschiedenen Entwicklungstools ermöglichen.

## Was ist n8n?

[n8n](https://n8n.io/) ist eine quelloffene Workflow-Automatisierungsplattform, die es ermöglicht, verschiedene Dienste und Anwendungen miteinander zu verbinden. Mit n8n können Sie Workflows erstellen, die auf bestimmte Ereignisse reagieren und automatisierte Aktionen ausführen.

## Übersicht der Workflow-Integration

Die EcoSphere Network Workflow Integration nutzt n8n, um folgende Systeme zu verbinden:

- **GitHub/GitLab**: Code-Repositories und Issue-Tracking
- **OpenProject**: Projektmanagement und Arbeitspaketeverwaltung
- **AFFiNE/AppFlowy**: Wissensmanagement und Dokumentation
- **OpenHands**: KI-gestützte Issue-Lösung
- **MCP-Server**: Erweiterbare Tool-Bereitstellung für KI-Agenten

Die Workflows automatisieren den Informationsfluss zwischen diesen Systemen und sorgen für Konsistenz und Effizienz im Entwicklungsprozess.

## Architektur der Workflow-Integration

Die Workflow-Integration folgt einer Hub-and-Spoke-Architektur, bei der ein zentraler Integration-Hub als Einstiegspunkt für alle Ereignisse dient. Diese Architektur bietet mehrere Vorteile:

- **Modularität**: Jeder Workflow kann unabhängig entwickelt und gewartet werden
- **Skalierbarkeit**: Neue Integrationen können einfach hinzugefügt werden
- **Robustheit**: Fehler in einem Workflow beeinträchtigen nicht die anderen
- **Wiederverwendbarkeit**: Gemeinsame Funktionen können in wiederverwendbaren Komponenten implementiert werden

### Workflow-Architekturdiagramm

```
                      +-------------------+
                      |                   |
                      | Integration Hub   |
                      |                   |
                      +--------+----------+
                               |
                               v
        +--------------------------------------------+
        |                      |                     |
+-------v------+      +--------v-------+    +--------v-------+
|              |      |                |    |                |
| GitHub zu    |      | GitLab zu      |    | MCP-Server zu  |
| OpenProject  |      | OpenProject    |    | OpenProject    |
|              |      |                |    |                |
+-------+------+      +--------+-------+    +--------+-------+
        |                      |                     |
        v                      v                     v
+-------+------------------------+--------------------+------+
|                                                           |
|                      OpenProject                          |
|                                                           |
+----------------------------+------------------------------+
                             |
                             v
                  +----------+-----------+
                  |                      |
                  |  AFFiNE / AppFlowy   |
                  |                      |
                  +----------------------+
```

### Datenfluss

1. **Ereigniserfassung**: Ereignisse werden über Webhooks oder API-Abfragen erfasst
2. **Normalisierung**: Der Integration-Hub normalisiert die Daten in ein einheitliches Format
3. **Routing**: Basierend auf dem Ereignistyp werden die Daten an die entsprechenden Workflows weitergeleitet
4. **Verarbeitung**: Die spezifischen Workflows verarbeiten die Daten und führen die erforderlichen Aktionen aus
5. **Synchronisierung**: Die Ergebnisse werden mit allen relevanten Systemen synchronisiert

## Implementierte Workflows

Die EcoSphere Network Workflow Integration umfasst folgende Hauptworkflows:

### 1. Integration-Hub (integration-hub.json)

**Zweck**: Zentraler Einstiegspunkt für alle Ereignisse, der die Weiterleitung an spezifische Workflows übernimmt.

**Funktionen**:
- **Ereignisnormalisierung**: Konvertiert verschiedene Ereignisformate in ein einheitliches Format
- **Intelligentes Routing**: Leitet Ereignisse basierend auf Typ und Inhalt an die richtigen Workflows weiter
- **Fehlerbehandlung**: Fängt Fehler ab und leitet sie an den Error-Handler-Workflow weiter
- **Protokollierung**: Protokolliert alle eingehenden Ereignisse für Audit-Zwecke

**Technische Details**:
- **Webhook-Endpunkt**: `/webhook/event`
- **Unterstützte Ereignisquellen**: GitHub, GitLab, OpenProject, MCP-Server
- **Ausgabeformat**: Normalisiertes JSON-Ereignisobjekt

### 2. GitHub zu OpenProject (github-to-openproject.json)

**Zweck**: Synchronisiert GitHub-Issues, Pull Requests und Commits mit OpenProject-Arbeitspaketen.

**Funktionen**:
- **Bidirektionale Synchronisierung**: Änderungen in beiden Systemen werden synchronisiert
- **Automatische Arbeitspaketeerstellung**: Erstellt Arbeitspakete in OpenProject für neue GitHub-Issues
- **Status-Mapping**: Mappt GitHub-Issue-Status auf OpenProject-Arbeitspaket-Status
- **Kommentar-Synchronisierung**: Synchronisiert Kommentare zwischen beiden Systemen

**Ereignis-Workflow-Beispiel**:
1. Ein neues Issue wird in GitHub erstellt
2. Der Integration-Hub empfängt das Ereignis und leitet es an den GitHub-zu-OpenProject-Workflow weiter
3. Der Workflow erstellt ein entsprechendes Arbeitspaket in OpenProject
4. Der Workflow aktualisiert das GitHub-Issue mit einem Link zum OpenProject-Arbeitspaket

**Webhook-Endpunkt**: `/webhook/github-to-openproject`

### 3. MCP-Server zu OpenProject (mcp-server-to-openproject.json)

**Zweck**: Integriert MCP-Server-Ereignisse und KI-Agenten-Aktionen mit OpenProject.

**Funktionen**:
- **KI-Analyse**: Analysiert MCP-Ereignisse mit einem LLM-Agenten
- **Automatische Kategorisierung**: Kategorisiert Ereignisse basierend auf ihrem Inhalt
- **Priorisierung**: Weist Ereignissen basierend auf ihrer Wichtigkeit Prioritäten zu
- **Benachrichtigungen**: Sendet Benachrichtigungen bei kritischen Ereignissen

**Webhook-Endpunkt**: `/webhook/mcp-server-to-openproject`

### 4. Fehlerbehandlung (error-handler.json)

**Zweck**: Zentralisierte Fehlerbehandlung für alle Workflows.

**Funktionen**:
- **Fehlerklassifizierung**: Kategorisiert Fehler nach Typ und Schweregrad
- **Automatische Wiederholung**: Versucht fehlgeschlagene Operationen automatisch erneut
- **Eskalation**: Eskaliert kritische Fehler an das Entwicklungsteam
- **Fehlerprotokollierung**: Protokolliert detaillierte Fehlerinformationen für die Analyse

**Webhook-Endpunkt**: `/webhook/error-handler`

## Installation und Konfiguration

### Voraussetzungen

- **n8n**: Version 0.214.0 oder höher
- **Docker und Docker Compose** (für die empfohlene Installationsmethode)
- **API-Zugangsdaten** für die zu integrierenden Dienste:
  - GitHub/GitLab Personal Access Token
  - OpenProject API-Token
  - AFFiNE/AppFlowy Zugangsdaten

### Installationsmethoden

#### Automatische Installation mit Docker (empfohlen)

Die einfachste Methode zur Installation der Workflows ist die Verwendung von Docker Compose:

```bash
# Repository klonen
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow

# Docker-Container starten
docker-compose up -d
```

Dies startet n8n und importiert automatisch alle Workflows.

#### Manuelle Installation mit dem Import-Skript

Wenn Sie bereits eine n8n-Instanz haben, können Sie das Import-Skript verwenden:

```bash
cd /workspace/Dev-Server-Workflow
./scripts/import-workflows.py --n8n-api-key YOUR_N8N_API_KEY --n8n-url http://localhost:5678
```

#### Manuelle Installation über die n8n-Weboberfläche

Sie können die Workflows auch manuell über die n8n-Weboberfläche importieren:

1. Öffnen Sie die n8n-Weboberfläche (standardmäßig http://localhost:5678)
2. Melden Sie sich an (Standardbenutzer: admin, Passwort: password)
3. Navigieren Sie zu "Workflows" → "Import from File"
4. Wählen Sie die JSON-Workflow-Dateien aus dem Verzeichnis `src/ESN_Initial-Szenario/n8n-workflows/`
5. Konfigurieren Sie die erforderlichen Credentials für jeden Workflow

### Konfiguration der Credentials

Für die korrekte Funktion der Workflows müssen folgende Credentials in n8n konfiguriert werden:

| Credential-Typ | Beschreibung | Erforderliche Berechtigungen |
|----------------|--------------|------------------------------|
| **GitHub API** | Für GitHub-Operationen | repo, read:user, read:org |
| **GitLab API** | Für GitLab-Operationen | api, read_repository, read_user |
| **OpenProject API** | Für OpenProject-Operationen | api_v3 |
| **HTTP Basic Auth** | Für AFFiNE/AppFlowy | - |
| **HTTP Header Auth** | Für MCP-Server | - |

### Umgebungsvariablen

Die folgenden Umgebungsvariablen können in n8n konfiguriert werden, um die Workflows anzupassen:

| Variable | Beschreibung | Standardwert |
|----------|--------------|--------------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | - |
| `GITLAB_TOKEN` | GitLab Personal Access Token | - |
| `OPENPROJECT_URL` | URL der OpenProject-Instanz | http://localhost:8080 |
| `OPENPROJECT_API_KEY` | API-Schlüssel für OpenProject | - |
| `APPFLOWY_URL` | URL der AFFiNE/AppFlowy-Instanz | http://localhost:3000 |
| `MCP_SERVERS_CONFIG` | JSON-Konfiguration der MCP-Server | siehe .env.example |
| `WEBHOOK_BASE_URL` | Basis-URL für Webhooks | http://localhost:5678 |

## Verwendung und Integration

### Webhook-Endpunkte

Die Workflows stellen folgende Webhook-Endpunkte bereit:

| Workflow | Webhook-Endpunkt | Beschreibung |
|----------|------------------|--------------|
| Integration-Hub | `/webhook/event` | Zentraler Einstiegspunkt für alle Ereignisse |
| GitHub zu OpenProject | `/webhook/github-to-openproject` | Direkter Endpunkt für GitHub-Ereignisse |
| MCP-Server zu OpenProject | `/webhook/mcp-server-to-openproject` | Direkter Endpunkt für MCP-Server-Ereignisse |
| Fehlerbehandlung | `/webhook/error-handler` | Endpunkt für Fehlerbehandlung |

### GitHub-Webhook einrichten

Um GitHub-Ereignisse automatisch zu verarbeiten:

1. Gehen Sie zu Ihrem GitHub-Repository → Settings → Webhooks → Add webhook
2. Geben Sie als Payload URL ein: `http://YOUR_SERVER:5678/webhook/github-to-openproject`
3. Wählen Sie Content type: `application/json`
4. Wählen Sie die Ereignisse aus, die den Webhook auslösen sollen (Issues, Pull Requests, Pushes)
5. Klicken Sie auf "Add webhook"

### Manuelles Testen der Workflows

Sie können die Workflows manuell mit curl testen:

```bash
# Test des Integration-Hubs
curl -X POST http://localhost:5678/webhook/event \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "github",
    "event_type": "issues",
    "action": "created",
    "payload": {
      "title": "Test Issue",
      "body": "This is a test issue",
      "state": "open",
      "repository": "username/repo",
      "html_url": "https://github.com/username/repo/issues/1"
    }
  }'
```

### Integration mit MCP-Servern

Die Workflows können mit den MCP-Servern integriert werden, um KI-Agenten Zugriff auf die Workflows zu geben:

1. Stellen Sie sicher, dass die MCP-Server laufen (siehe [MCP-Server-Dokumentation](MCP-Server-Implementation.md))
2. Konfigurieren Sie die MCP-Server-URLs in der `MCP_SERVERS_CONFIG`-Umgebungsvariable
3. Aktivieren Sie den MCP-zu-OpenProject-Workflow

## Fehlerbehebung und Wartung

### Automatische Fehlerbehandlung

Die Workflows verfügen über einen integrierten Fehlerbehandlungsmechanismus:

1. **Erkennung**: Fehler werden automatisch erkannt und an den Fehlerbehandlungs-Workflow weitergeleitet
2. **Wiederholung**: Fehlgeschlagene Operationen werden bis zu dreimal automatisch wiederholt
3. **Protokollierung**: Fehler werden detailliert protokolliert, einschließlich Stack-Traces und Kontextinformationen
4. **Benachrichtigung**: Bei kritischen Fehlern werden Benachrichtigungen gesendet
5. **Dokumentation**: Fehler werden in OpenProject und AFFiNE/AppFlowy dokumentiert

### Häufige Probleme und Lösungen

| Problem | Mögliche Ursachen | Lösungen |
|---------|-------------------|----------|
| Webhook-Fehler | - Falsche URL<br>- n8n nicht erreichbar<br>- Firewall blockiert Zugriff | - URL überprüfen<br>- n8n-Status prüfen<br>- Firewall-Einstellungen anpassen |
| Authentifizierungsfehler | - Ungültiger API-Schlüssel<br>- Fehlende Berechtigungen<br>- Abgelaufener Token | - API-Schlüssel erneuern<br>- Berechtigungen prüfen<br>- Token aktualisieren |
| Datenverarbeitungsfehler | - Unerwartetes Datenformat<br>- Fehlende Pflichtfelder<br>- Inkonsistente Daten | - Datenformat überprüfen<br>- Pflichtfelder ergänzen<br>- Daten bereinigen |

### Workflow-Überwachung

Die Workflows können mit den integrierten n8n-Tools überwacht werden:

1. **Ausführungsverlauf**: Zeigt alle Workflow-Ausführungen und deren Status
2. **Workflow-Editor**: Ermöglicht das Debuggen und Testen von Workflows
3. **Logs**: Zeigt detaillierte Logs für jede Workflow-Ausführung

## Erweiterung und Anpassung

### Hinzufügen neuer Integrationen

Um eine neue Integration hinzuzufügen:

1. **Workflow erstellen**: Erstellen Sie einen neuen n8n-Workflow für die Integration
2. **Hub erweitern**: Fügen Sie die neue Quelle zum Integration-Hub hinzu
3. **Normalisierung implementieren**: Erstellen Sie eine Normalisierungsfunktion für das neue Datenformat
4. **Testen**: Testen Sie die Integration mit realen Daten
5. **Dokumentieren**: Aktualisieren Sie die Dokumentation mit der neuen Integration

### Anpassen der Datenverarbeitung

Die Datenverarbeitung kann in den Function-Nodes angepasst werden:

```javascript
// Beispiel für eine angepasste Normalisierungsfunktion im Integration-Hub
function normalizeEvent(items) {
  const event = items[0].json;
  
  // Angepasste Normalisierungslogik hier implementieren
  
  return {
    json: {
      normalized_event: {
        // Normalisierte Daten
      }
    }
  };
}
```

### Erweiterte Funktionen implementieren

Die Workflows können mit zusätzlichen Funktionen erweitert werden:

- **Automatisierte Tests**: Implementieren Sie automatisierte Tests für die Workflows
- **Benutzerdefinierte Dashboards**: Erstellen Sie Dashboards zur Visualisierung der Workflow-Aktivitäten
- **Erweiterte Benachrichtigungen**: Fügen Sie zusätzliche Benachrichtigungskanäle hinzu (Slack, Discord, E-Mail)
- **KI-gestützte Verarbeitung**: Integrieren Sie KI-Modelle für erweiterte Datenanalyse und -verarbeitung

## Referenzen und weiterführende Dokumentation

### Externe Dokumentation

- [n8n-Dokumentation](https://docs.n8n.io/) - Offizielle Dokumentation der n8n-Plattform
- [OpenProject API-Dokumentation](https://www.openproject.org/docs/api/) - API-Referenz für OpenProject
- [GitHub API-Dokumentation](https://docs.github.com/en/rest) - GitHub REST API-Referenz
- [GitLab API-Dokumentation](https://docs.gitlab.com/ee/api/) - GitLab API-Referenz
- [Model Context Protocol Dokumentation](https://github.com/modelcontextprotocol/protocol) - MCP-Spezifikation

### Interne Dokumentation

- [MCP-Server-Implementierung](MCP-Server-Implementation.md) - Details zur MCP-Server-Implementierung
- [Installation und Konfiguration](Installation-Guide.md) - Ausführliche Installationsanleitung
- [GitHub-Integration](GitHub-Integration.md) - Spezifische Dokumentation zur GitHub-Integration
- [OpenHands-Integration](MCP-OpenHands.md) - Integration mit OpenHands
- [Fehlerbehebung](Troubleshooting.md) - Ausführliche Fehlerbehebungsanleitung