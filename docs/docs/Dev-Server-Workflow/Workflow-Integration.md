# Workflow-Integration von AFFiNE, AppFlowy, GitLab/GitHub, OpenProject und OpenHands

Diese Dokumentation beschreibt die vollständige Integration der folgenden Tools in einem automatisierten Workflow:
- **OpenProject**: Zentrales Projektmanagement-Tool
- **GitLab/GitHub**: Code-Repository und Issue-Tracking
- **AFFiNE**: Wissensmanagement und Dokumentation
- **AppFlowy**: Alternativer Open-Source-Wissensmanager
- **OpenHands**: KI-gestützte Automatisierung für Issue-Lösung

## Übersicht der Architektur

Die Integration verwendet n8n als zentrale Workflow-Automatisierungsplattform und setzt auf Webhooks für die Kommunikation zwischen den verschiedenen Systemen. Zusätzlich wird in jedem GitHub-Repository der OpenHands Issue-Resolver eingerichtet, um eine KI-gestützte Lösung für einfache Issues zu ermöglichen.

![Workflow-Architektur](https://via.placeholder.com/800x400?text=Workflow-Architektur-Diagram)

## Voraussetzungen

- GitHub-Organisation oder GitLab-Gruppe mit Repository-Zugriff
- OpenProject-Instanz mit API-Zugriff
- AFFiNE oder AppFlowy mit API-Zugriff
- Docker und Docker Compose für n8n-Installation (optional)
- Python 3.6+ für die Setup-Skripte

## Einrichtungsschritte

### 1. Konfigurationsdatei vorbereiten

1. Kopieren Sie die `.env-template`-Datei zu `.env`
2. Füllen Sie alle benötigten Werte aus:
   - API-Keys für alle Dienste
   - URLs für Ihre Instanzen
   - Organisation und Repository-Konfiguration

### 2. OpenHands in GitHub-Repositories einrichten

Führen Sie das GitHub OpenHands-Resolver Setup-Skript aus:

```bash
pip install PyGithub
python github_workflow_setup.py --org IHRE_ORG --token GITHUB_TOKEN --llm-api-key IHR_LLM_API_KEY
```

Dieses Skript richtet den OpenHands Issue-Resolver in allen angegebenen Repositories ein. Zusätzliche Optionen:
- `--skip-repos`: Comma-separierte Liste von Repositories, die übersprungen werden sollen
- `--only-repos`: Comma-separierte Liste von Repositories, die ausschließlich verarbeitet werden sollen

### 3. n8n-Workflow-Integration einrichten

Führen Sie das n8n Workflow Setup-Skript aus:

```bash
pip install requests
python n8n_workflow_setup.py --install --env-file .env
```

Dieses Skript:
- Installiert optional n8n via Docker
- Richtet drei Haupt-Workflows ein:
  1. GitHub zu OpenProject Integration
  2. Dokumenten-Synchronisierung
  3. OpenHands Integration
- Konfiguriert alle benötigten Credentials
- Generiert Webhook-URLs für die Integration mit Ihren Tools

### 4. Webhooks in den Quellsystemen einrichten

#### GitHub/GitLab Webhooks

Richten Sie Webhooks in jedem Repository ein:
1. Navigieren Sie zu Repository > Settings > Webhooks
2. Fügen Sie die vom Setup-Skript generierte GitHub-Webhook-URL hinzu
3. Wählen Sie die Events: `Issues`, `Pull Requests` und `Push`

#### AFFiNE/AppFlowy Webhooks

Richten Sie entsprechende Webhooks in der Konfiguration von AFFiNE oder AppFlowy ein:
1. Navigieren Sie zu den Integration-Einstellungen
2. Fügen Sie die vom Setup-Skript generierte Dokument-Webhook-URL hinzu
3. Konfigurieren Sie den Webhook für `document_updated` Events

#### OpenHands Integration

Damit OpenHands Statusupdates an n8n senden kann:
1. Erstellen Sie eine Konfigurationsdatei für OpenHands
2. Fügen Sie die vom Setup-Skript generierte OpenHands-Webhook-URL hinzu

## Workflow-Beispiele

### 1. Issue-Tracking und Automatische Lösung

1. Ein Issue wird in GitHub/GitLab erstellt
2. n8n erkennt das neue Issue und:
   - Erstellt ein entsprechendes Arbeitspaket in OpenProject
   - Fügt das Label "fix-me" zum Issue hinzu (für OpenHands)
3. OpenHands versucht, das Issue zu lösen und erstellt einen PR
4. n8n erkennt den PR und:
   - Aktualisiert den Status des Arbeitspakets in OpenProject
   - Erstellt ein Dokument in AFFiNE/AppFlowy mit den Änderungen

### 2. Dokumentationsaktualisierung

1. Ein Dokument wird in AFFiNE/AppFlowy aktualisiert
2. n8n erkennt die Änderung und:
   - Aktualisiert entsprechende README-Dateien in GitHub/GitLab
   - Aktualisiert verknüpfte Arbeitspakete in OpenProject

## Fehlerbehebung

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

## Erweiterungsmöglichkeiten

### Erweiterte Dokumentensynchronisierung

Die bidirektionale Synchronisierung zwischen allen Systemen ermöglicht eine nahtlose Zusammenarbeit, bei der Änderungen in jedem System automatisch in allen anderen reflektiert werden.

**Implementierungsschritte:**
1. **Webhook-Erweiterung**: Konfigurieren Sie Webhooks in allen Systemen, die Änderungen an Dokumenten erkennen
2. **Konfliktlösung**: Implementieren Sie eine Strategie zur Konfliktlösung, wenn Dokumente in mehreren Systemen gleichzeitig bearbeitet werden
3. **Versionshistorie**: Führen Sie eine Versionshistorie ein, die Änderungen aus allen Systemen nachverfolgt
4. **Metadaten-Synchronisierung**: Synchronisieren Sie nicht nur Inhalte, sondern auch Metadaten wie Tags, Zuordnungen und Status

**n8n-Workflow-Konfiguration:**
- Erstellen Sie einen dedizierten Workflow für jede Synchronisierungsrichtung
- Verwenden Sie Funktionsknoten zur Transformation von Datenformaten zwischen den Systemen
- Setzen Sie "Throttle"-Knoten ein, um Synchronisierungsschleifen zu vermeiden
- Führen Sie Prüfsummen ein, um unnötige Updates zu vermeiden

### KI-gestützte Zusammenfassungen

Nutzen Sie die OpenHands-Infrastruktur, um automatisch Zusammenfassungen zu generieren und Dokumentation aus Code, Issues und Pull Requests zu erstellen.

**Implementierungsschritte:**
1. **Ereignisidentifikation**: Definieren Sie, welche Events Zusammenfassungen auslösen sollen (z.B. große PRs, Issue-Schließung)
2. **Prompt-Engineering**: Erstellen Sie spezialisierte Prompts für verschiedene Arten von Zusammenfassungen
3. **Integrationsendpunkte**: Richten Sie Endpunkte ein, die OpenHands mit den zu verarbeitenden Dokumenten versorgen
4. **Qualitätssicherung**: Implementieren Sie einen Review-Prozess für generierte Dokumentation

**n8n-Workflow-Beispiel:**
- Verwenden Sie einen zeitgesteuerten Trigger, um wöchentliche Zusammenfassungen von Aktivitäten zu generieren
- Sammeln Sie Daten aus allen Systemen in einem einheitlichen Format
- Rufen Sie die OpenHands API auf, um die Zusammenfassung zu generieren
- Verteilen Sie die Ergebnisse an AFFiNE/AppFlowy und fügen Sie Links in OpenProject ein

### Discord-Integration

Integration von Discord-Benachrichtigungen für wichtige Workflow-Ereignisse, um Teams in Echtzeit auf dem Laufenden zu halten.

**Implementierungsschritte:**
1. **Discord-Webhook einrichten**: Erstellen Sie einen Webhook in Ihrem Discord-Server
2. **Ereigniskategorisierung**: Definieren Sie verschiedene Kategorien von Ereignissen und ihre Wichtigkeit
3. **Nachrichtenformatierung**: Gestalten Sie informative und ansprechende Discord-Nachrichten mit Embeds
4. **Benutzer-Erwähnungen**: Konfigurieren Sie automatische @mentions basierend auf Zuständigkeiten

**n8n-Workflow-Konfiguration:**
- Fügen Sie Discord-Webhook-Knoten zu allen relevanten Workflows hinzu
- Verwenden Sie Bedingungsknoten, um zu entscheiden, welche Ereignisse eine Benachrichtigung auslösen
- Erstellen Sie benutzerdefinierte Funktionen zur Formatierung ansprechender Nachrichten
- Implementieren Sie eine Throttling-Logik, um Benachrichtigungsflut zu vermeiden

### Zeiterfassung

Integrieren Sie die Zeiterfassung zwischen OpenProject und GitHub/GitLab, um Entwicklungsaufwand direkt mit Projektmanagement zu verknüpfen.

**Implementierungsschritte:**
1. **Zeit-Tracking-Trigger**: Erfassen Sie Zeit-Tracking-Ereignisse aus Commit-Nachrichten oder speziellen Kommentaren
2. **Synchronisierungslogik**: Implementieren Sie bidirektionale Synchronisierung von Zeiteinträgen
3. **Berichterstellung**: Automatisieren Sie die Generierung von Zeitberichten und deren Verteilung
4. **Validierung**: Richten Sie Validierungsregeln für Zeiteinträge ein

**Umsetzungsbeispiel:**
- Überwachen Sie Commit-Nachrichten auf Zeit-Tracking-Muster (z.B. "#time 2h")
- Extrahieren Sie die aufgewendete Zeit und verbinden Sie sie mit dem entsprechenden Arbeitspaket
- Erstellen Sie automatisch Zeitbuchungen in OpenProject
- Generieren Sie wöchentliche Zeitberichte und verteilen Sie diese an Projektmanager

## Ressourcen

- [OpenProject API Dokumentation](https://www.openproject.org/docs/api/)
- [GitHub API Dokumentation](https://docs.github.com/en/rest)
- [n8n Dokumentation](https://docs.n8n.io/)
- [OpenHands Repository](https://github.com/All-Hands-AI/OpenHands)
