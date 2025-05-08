# Implementierung der n8n Workflow Integration

Dieses Dokument beschreibt die Implementierung der n8n Workflow Integration für AFFiNE, AppFlowy, GitHub/GitLab, OpenProject und OpenHands.

## Implementierte Workflows

Folgende Workflows wurden implementiert:

1. **GitHub zu OpenProject Integration** (`GITHUB_OPENPROJECT_WORKFLOW`)
   - Synchronisiert Issues und Pull Requests zwischen GitHub/GitLab und OpenProject
   - Erstellt Arbeitspakete in OpenProject für GitHub Issues
   - Aktualisiert den Status von Arbeitspaketen bei Pull Requests

2. **Dokumenten-Synchronisierung** (`DOCUMENT_SYNC_WORKFLOW` und `DOCUMENT_SYNC_ENHANCED_WORKFLOW`)
   - Synchronisiert Dokumente zwischen AFFiNE/AppFlowy, GitHub und OpenProject
   - Erkennt und löst Konflikte bei gleichzeitigen Änderungen
   - Sendet Benachrichtigungen bei Konflikten

3. **OpenHands Integration** (`OPENHANDS_WORKFLOW`)
   - Integriert OpenHands für die KI-gestützte Lösung von Issues
   - Verarbeitet OpenHands-generierte Pull Requests
   - Aktualisiert den Status in OpenProject
   - Erstellt Dokumente in AFFiNE/AppFlowy zur Dokumentation der Änderungen

4. **Discord Benachrichtigungen** (`DISCORD_NOTIFICATION_WORKFLOW`)
   - Sendet Benachrichtigungen über GitHub/GitLab-Ereignisse an Discord
   - Unterstützt verschiedene Ereignistypen (Issues, Pull Requests, Commits)
   - Formatiert Nachrichten für bessere Lesbarkeit

5. **Zeit-Tracking** (`TIME_TRACKING_WORKFLOW`)
   - Extrahiert Zeit-Tracking-Informationen aus Commit-Nachrichten
   - Überträgt Zeiteinträge nach OpenProject
   - Generiert Zeitberichte

6. **KI-gestützte Zusammenfassungen** (`AI_SUMMARY_WORKFLOW`)
   - Erzeugt wöchentliche Zusammenfassungen von Repository-Aktivitäten
   - Nutzt KI für die Generierung von Zusammenfassungen
   - Verteilt Ergebnisse an AFFiNE/AppFlowy und OpenProject

7. **MCP Integration** (`MCP_SERVER_WORKFLOW`)
   - Implementiert das Model Context Protocol für n8n
   - Ermöglicht KI-Agenten, n8n-Workflows als Tools zu verwenden
   - Stellt eine JSON-RPC-Schnittstelle für die Kommunikation bereit

## Implementierungsdetails

### Workflow-Aktivierung

Alle Workflows werden nach der Erstellung automatisch aktiviert, um sicherzustellen, dass sie sofort einsatzbereit sind. Dies wird durch die Funktion `activate_workflow` in `n8n-setup-utils.py` implementiert.

### Credential-Management

Die Implementierung unterstützt die automatische Konfiguration von Credentials für verschiedene Dienste:
- GitHub/GitLab
- OpenProject
- AFFiNE/AppFlowy
- Discord
- OpenHands

### MCP-Server

Der MCP-Server (`n8n-mcp-server.py`) implementiert das Model Context Protocol und ermöglicht es KI-Agenten, n8n-Workflows als Tools zu verwenden. Der Server:
- Lädt verfügbare Workflows aus n8n
- Konvertiert sie in MCP-Tools
- Verarbeitet Tool-Aufrufe und führt die entsprechenden Workflows aus
- Bietet Fallback-Mechanismen für Fehlerbehandlung

### OpenHands-Integration

Die OpenHands-Integration ermöglicht die automatische Lösung von Issues durch KI. Die Konfigurationsdatei `openhands-mcp-config.json` definiert:
- Den Befehl zum Starten des MCP-Servers
- Umgebungsvariablen für die n8n-Verbindung
- Eine Liste von Tools, die automatisch genehmigt werden sollen

## Verwendung

Um die Workflows zu verwenden, führen Sie das Setup-Skript aus:

```bash
python src/n8n_setup_main.py --install --env-file .env --workflows github document openhands discord timetracking ai mcp --mcp
```

Dies wird:
- n8n lokal installieren (wenn `--install` angegeben ist)
- Die angegebenen Workflows erstellen und aktivieren
- Den MCP-Server einrichten (wenn `--mcp` angegeben ist)

## Testen

Zum Testen der Implementierung kann das Skript `test-workflows.py` verwendet werden:

```bash
python test-workflows.py
```

Dies überprüft:
- Die Existenz aller Workflow-Dateien
- Die Konfiguration des MCP-Servers
- Die OpenHands-Integration

## Erweiterung

Die Implementierung kann leicht erweitert werden, indem:
- Neue Workflow-Definitionen in entsprechenden Dateien erstellt werden
- Die neuen Workflows in `n8n-setup-workflows.py` importiert werden
- Die Workflow-Erstellung in `n8n-setup-main.py` hinzugefügt wird

## Bekannte Einschränkungen

- Die Implementierung erfordert eine laufende n8n-Instanz
- Einige Funktionen erfordern zusätzliche Konfiguration in den Zieldiensten (z.B. Webhook-Einrichtung in GitHub)
- Die MCP-Integration ist auf die definierten Tools beschränkt