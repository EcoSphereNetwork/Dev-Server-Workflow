# Technische Spezifikation: GitHub-GitLab-OpenProject Integration

## 1. Systemarchitektur

### 1.1 Überblick

Die Integration zwischen GitHub, GitLab und OpenProject wird durch eine Reihe von n8n-Workflows realisiert, die modular aufgebaut sind und miteinander interagieren. Die Architektur folgt einem ereignisgesteuerten Ansatz, wobei Webhooks und zeitgesteuerte Trigger die primären Auslösemechanismen darstellen.

```
+---------------+         +----------------+         +------------------+
|               |         |                |         |                  |
|    GitHub     |<------->|      n8n       |<------->|      GitLab      |
|               |         |   Workflows    |         |                  |
+---------------+         +----------------+         +------------------+
                                 ^
                                 |
                                 v
                          +----------------+
                          |                |
                          |   OpenProject  |
                          |                |
                          +----------------+
```

### 1.2 Hauptkomponenten

1. **n8n-Instanz**: Zentraler Integrationsserver, auf dem alle Workflows ausgeführt werden
2. **Workflows**: Modulare Prozessabläufe für spezifische Integrationsaufgaben
3. **Webhooks**: HTTP-Endpunkte für ereignisgesteuerte Triggermechanismen
4. **Credentials-Store**: Sichere Speicherung aller API-Zugangsschlüssel
5. **Referenz-Datenbank**: Mapping zwischen Objekten in verschiedenen Systemen

### 1.3 Kommunikationsflüsse

- **GitHub ↔ n8n**: Webhooks für Ereignisse, REST-API für Abfragen und Updates
- **GitLab ↔ n8n**: Webhooks für Ereignisse, REST-API für Abfragen und Updates
- **OpenProject ↔ n8n**: REST-API für Abfragen und Updates
- **Interworkflow-Kommunikation**: n8n-interne Mechanismen für Workflow-Triggers

## 2. Technische Spezifikation der n8n-Workflows

### 2.1 GitLab-OpenProject-Basis-Synchronisation

#### 2.1.1 Issue-Synchronisation (Workflow 1)

**Input-Trigger**:
- GitLab-Webhook: Issue Create/Update Event
- Timed Trigger: Alle 15 Minuten (Fallback)

**Konfigurationsparameter**:
- `GITLAB_PROJECT_IDS`: Liste der zu überwachenden GitLab-Projekt-IDs
- `OPENPROJECT_PROJECT_MAPPING`: JSON-Mapping zwischen GitLab- und OpenProject-Projekt-IDs
- `ISSUE_TYPE_MAPPING`: Mapping zwischen GitLab-Issue-Typen und OpenProject-Work-Package-Typen

**Prozessablauf**:
1. Event-Validierung und -Filterung
   - Prüfung auf relevante Projekte
   - Vermeidung von Synchronisationsschleifen durch Metadaten-Check

2. GitLab-Issue-Datenextraktion
   - Extraktion aller relevanten Felder (Titel, Beschreibung, Status, Zuweisungen, Labels)
   - Normalisierung der Daten in ein Zwischenformat

3. OpenProject-Status-Check
   - Abfrage, ob bereits ein Work Package mit Referenz zum GitLab-Issue existiert
   - Ermittlung des aktuellen Status bei existierendem Work Package

4. Transformation und Mapping
   - Umwandlung des GitLab-Issue-Formats in OpenProject-Work-Package-Format
   - Anwendung von konfigurierbaren Mapping-Regeln für Felder
   - JSON-Transformation mittels JSONata

5. OpenProject-API-Integration
   - Erstellung oder Aktualisierung des Work Package
   - HTTP-Request mit JSONata-transformierten Daten
   - OAuth2 oder Token-basierte Authentifizierung

6. Referenz-Aktualisierung
   - Speicherung der Mapping-Referenz zwischen GitLab-Issue-ID und OpenProject-Work-Package-ID
   - Zeitstempel der letzten Synchronisation
   - Quelle der letzten Änderung (für Schleifenerkennung)

7. Fehlerbehandlung
   - Wiederholungsversuche bei temporären API-Fehlern
   - Logging detaillierter Fehlerinformationen
   - Benachrichtigung bei kritischen Fehlern

**Node-Struktur**:
```
GitLab Webhook/Trigger
  ↓
Filter (relevante Projekte)
  ↓
GitLab Node (Issue-Details abrufen)
  ↓
Function Node (Synchronisationsschleifen-Check)
  ↓
HTTP Request Node (OpenProject existierendes Work Package prüfen)
  ↓
IF Node (existiert bereits?)
  ├── JA → HTTP Request Node (UPDATE Work Package)
  └── NEIN → HTTP Request Node (CREATE Work Package)
      ↓
Function Node (Referenz-Mapping aktualisieren)
  ↓
Error Workflow Trigger (bei Fehler)
```

#### 2.1.2 Status-Synchronisation (Workflow 2)

**Input-Trigger**:
- OpenProject-Webhook: Work Package Update Event
- Timed Trigger: Alle 15 Minuten (Fallback)

**Konfigurationsparameter**:
- `STATUS_MAPPING`: Bidirektionales Mapping zwischen GitLab-Issue-Status und OpenProject-Work-Package-Status
- `SYNC_DIRECTION_PRIORITY`: Konfiguration für Konfliktlösung bei gleichzeitigen Änderungen

**Prozessablauf**:
1. Event-Validierung
   - Prüfung, ob es sich um eine Status-Änderung handelt
   - Prüfung auf relevante Work Packages mit GitLab-Referenz

2. Referenz-Lookup
   - Abruf der GitLab-Issue-ID aus dem Referenz-Mapping
   - Ermittlung des letzten Synchronisationszeitpunkts

3. Änderungsvalidierung
   - Prüfung, ob die Änderung neuer ist als die letzte Synchronisation
   - Vermeidung von Synchronisationsschleifen

4. Status-Mapping
   - Umwandlung des OpenProject-Status in den entsprechenden GitLab-Status
   - Anwendung der konfigurierten Mapping-Regeln

5. GitLab-API-Update
   - Aktualisierung des GitLab-Issue-Status
   - Hinzufügen eines internen Kommentars zur Synchronisation

6. Referenz-Aktualisierung
   - Aktualisierung des Zeitstempels der letzten Synchronisation
   - Setzung der Änderungsquelle auf "OpenProject"

**Node-Struktur** (analog für GitHub):
```
OpenProject Webhook/Trigger
  ↓
Filter (relevante Work Packages)
  ↓
Function Node (Referenz-Lookup)
  ↓
IF Node (GitLab-Referenz vorhanden?)
  ├── JA → HTTP Request Node (GitLab-Issue-Status abrufen)
  │         ↓
  │       Function Node (Status-Mapping)
  │         ↓
  │       GitLab Node (Issue-Status aktualisieren)
  │         ↓
  │       Function Node (Referenz-Mapping aktualisieren)
  └── NEIN → End
```

### 2.2 GitHub-GitLab-Community-Bridge

#### 2.2.1 GitHub-Issue zu GitLab-Issue Synchronisation

**Input-Trigger**:
- GitHub-Webhook: Issue Create/Update Event
- Timed Trigger: Stündlich (Fallback)

**Konfigurationsparameter**:
- `GITHUB_REPOS`: Liste zu überwachender GitHub-Repositories
- `GITHUB_GITLAB_REPO_MAPPING`: Mapping zwischen GitHub- und GitLab-Repositories
- `RELEVANCE_CRITERIA`: Regeln zur Bestimmung relevanter Issues (Labels, Kommentare, etc.)

**Prozessablauf**:
1. Relevanz-Prüfung
   - Anwendung konfigurierter Filterkriterien
   - Prüfung auf Labels, die Relevanz für interne Entwicklung anzeigen

2. Duplikat-Prüfung
   - Suche nach bereits existierendem GitLab-Issue über Referenz-Mapping
   - Vermeidung von Duplikaten

3. GitHub-Issue-Datenextraktion
   - Abruf aller relevanten Felder (Titel, Beschreibung, Labels, Zuweisungen)
   - Anreicherung mit Community-Kontext (z.B. GitHub-Username)

4. Transformation und Erstellung
   - Umwandlung in GitLab-Issue-Format
   - Hinzufügen eines GitHub-Referenz-Links
   - Spezielles Label für Community-Issues

5. GitLab-API-Integration
   - Erstellung des GitLab-Issues
   - Setzung vordefinierter Labels und Zuweisungen

6. Referenz-Speicherung
   - Mapping zwischen GitHub-Issue-ID und GitLab-Issue-ID
   - Zeitstempel und Richtungsinformation

**Node-Struktur**:
```
GitHub Webhook/Trigger
  ↓
Filter (relevante Issues)
  ↓
Function Node (Duplikat-Prüfung)
  ↓
IF Node (bereits synchronisiert?)
  ├── JA → HTTP Request Node (GitLab-Issue aktualisieren)
  └── NEIN → Function Node (Transformation)
              ↓
            GitLab Node (Issue erstellen)
              ↓
            Function Node (Referenz-Mapping speichern)
```

#### 2.2.2 Community-Metriken-Sammlung

**Input-Trigger**:
- Timed Trigger: Täglich um Mitternacht

**Konfigurationsparameter**:
- `GITHUB_REPOS`: Liste zu überwachender GitHub-Repositories
- `METRIC_DEFINITIONS`: Definition zu sammelnder Metriken (Stars, Forks, Issues, etc.)
- `REPORT_FORMAT`: Konfiguration des Berichtsformats

**Prozessablauf**:
1. Repository-Iteration
   - Durchlaufen aller konfigurierten Repositories
   - Batchweise Verarbeitung zur Einhaltung von API-Limits

2. GitHub-API-Abfragen
   - Abruf von Repository-Statistiken (Stars, Forks, Watchers)
   - Abruf von Issue-Statistiken (Offen, Geschlossen, Zeit bis zum Schließen)
   - Abruf von Contributor-Statistiken

3. Datenaggregation
   - Zusammenführung der Daten nach Repositories und Produkten
   - Berechnung von Trends im Vergleich zu vorherigen Zeiträumen

4. Berichtserstellung
   - Formatierung der Daten nach konfiguriertem Format
   - Erstellung von Tabellen, Diagrammen oder JSON

5. OpenProject-Integration
   - Speicherung des Berichts als OpenProject-Dokument
   - Aktualisierung relevanter Work Packages mit Metrik-Daten

**Node-Struktur**:
```
Timer Trigger (Täglich)
  ↓
Function Node (Repository-Liste generieren)
  ↓
SplitInBatches Node
  ↓
GitHub Node (Statistiken abrufen) - mit Rate-Limit-Beachtung
  ↓
Merge Node (Alle Daten zusammenführen)
  ↓
Function Node (Datenaggregation und Trend-Analyse)
  ↓
Function Node (Berichtserstellung)
  ↓
HTTP Request Node (OpenProject Dokument erstellen/aktualisieren)
```

### 2.3 Dokumentations-Analyse und Roadmap-Generierung

#### 2.3.1 Dokumentationsextraktion und Analyse

**Input-Trigger**:
- Timed Trigger: Wöchentlich
- Manual Trigger: Durch Projektmanager auslösbar

**Konfigurationsparameter**:
- `GITLAB_DOC_PATHS`: Pfade zu relevanten Dokumentationsdateien in GitLab
- `EXTRACTION_PATTERNS`: Regex-Muster zur Extraktion strukturierter Informationen
- `ROADMAP_TEMPLATES`: Templates für verschiedene Roadmap-Typen

**Prozessablauf**:
1. Repository-Scan
   - Durchsuchen konfigurierter GitLab-Repositories
   - Identifikation relevanter Dokumentationsdateien (README, docs/, wiki/)

2. Inhaltsextraktion
   - Abruf der Markdown/Wiki-Inhalte über GitLab-API
   - Parsing der Inhalte nach vordefinierten Strukturen

3. Muster-Erkennung
   - Anwendung von Regex-Mustern zur Extraktion von Roadmap-Informationen
   - Identifikation von Meilensteinen, Zeitplänen, Features

4. Strukturierte Datengenerierung
   - Umwandlung der extrahierten Texte in strukturierte JSON-Daten
   - Validierung gegen vordefinierte Schemas

5. Speicherung und Kategorisierung
   - Speicherung der extrahierten Daten in einer strukturierten Datenbank
   - Kategorisierung nach Projekt, Produkt und Roadmap-Typ

**Node-Struktur**:
```
Timer/Manual Trigger
  ↓
GitLab Node (Repositories abrufen)
  ↓
Function Node (Dokument-Pfade identifizieren)
  ↓
GitLab Node (Dokumentinhalte abrufen)
  ↓
Function Node (Inhaltsextraktion mit Regex)
  ↓
Function Node (Strukturierte Daten generieren)
  ↓
Function Node (Speicherung und Kategorisierung)
```

#### 2.3.2 Roadmap-Generierung

**Input-Trigger**:
- Nach Abschluss des Dokumentationsanalyse-Workflows
- Manual Trigger: Durch Projektmanager auslösbar

**Konfigurationsparameter**:
- `ROADMAP_TYPES`: Definitionen verschiedener Roadmap-Typen (Entwicklung, Strategie, Finanzierung)
- `VISUALIZATION_TEMPLATES`: Templates für visuelle Darstellung in OpenProject
- `AGGREGATION_RULES`: Regeln zur Zusammenführung von Roadmap-Daten

**Prozessablauf**:
1. Datenabfrage
   - Abruf der strukturierten Roadmap-Daten aus der Datenbank
   - Filterung nach Roadmap-Typ und Zeitraum

2. Template-Anwendung
   - Auswahl des passenden Roadmap-Templates
   - Einsetzen der Daten in das Template

3. Aggregation (bei Bedarf)
   - Zusammenführung von Daten aus mehreren Repositories
   - Anwendung von Gewichtungsregeln

4. Roadmap-Erstellung
   - Generierung der finalen Roadmap im erforderlichen Format
   - Erstellung von Gantt-Diagrammen, Listen oder anderen Visualisierungen

5. OpenProject-Integration
   - Erstellung oder Aktualisierung der Roadmap in OpenProject
   - Verknüpfung mit relevanten Projekten und Work Packages

**Node-Struktur**:
```
Previous Workflow Trigger / Manual Trigger
  ↓
Function Node (Datenabfrage mit Filtern)
  ↓
Switch Node (nach Roadmap-Typ)
  ├── Entwicklung → Function Node (Entwicklungs-Template anwenden)
  ├── Strategie → Function Node (Strategie-Template anwenden)
  └── Finanzierung → Function Node (Finanzierungs-Template anwenden)
      ↓
Function Node (Aggregation bei Bedarf)
  ↓
Function Node (Roadmap-Dokument generieren)
  ↓
HTTP Request Node (OpenProject-Integration)
```

### 2.4 Release-Management-Workflow

#### 2.4.1 Release-Erstellung und -Verwaltung

**Input-Trigger**:
- GitLab-Webhook: Tag Creation Event
- GitLab-Webhook: Milestone Closed Event
- Manual Trigger: Durch Release-Manager

**Konfigurationsparameter**:
- `RELEASE_CRITERIA`: Kriterien zur Identifikation von Release-Tags
- `CHANGELOG_TEMPLATE`: Template für automatisch generierte Changelogs
- `NOTIFICATION_CHANNELS`: Konfiguration für Release-Benachrichtigungen

**Prozessablauf**:
1. Release-Validierung
   - Prüfung, ob das Tag den Release-Kriterien entspricht
   - Validierung von Version und Format

2. Changelog-Generierung
   - Sammlung aller Issues und Merge Requests seit dem letzten Release
   - Kategorisierung nach Typ (Feature, Bug, etc.)
   - Anwendung des konfigurierten Changelog-Templates

3. Assets-Sammlung
   - Identifikation relevanter Build-Artefakte
   - Zusammenstellung für den Release

4. GitHub-Release-Erstellung
   - Übertragung des Tags und der Commit-Informationen zu GitHub
   - Erstellung eines GitHub-Releases mit Changelog und Assets

5. OpenProject-Aktualisierung
   - Update des Release-Status in relevanten Work Packages
   - Aktualisierung von Roadmaps und Meilensteinen

6. Benachrichtigungen
   - Versand von Benachrichtigungen über konfigurierte Kanäle
   - Anpassung des Inhalts je nach Zielgruppe

**Node-Struktur**:
```
GitLab Webhook (Tag/Milestone) / Manual Trigger
  ↓
Function Node (Release-Validierung)
  ↓
GitLab Node (Issues und MRs abrufen)
  ↓
Function Node (Changelog generieren)
  ↓
GitLab Node (Assets sammeln)
  ↓
GitHub Node (Release erstellen)
  ↓
HTTP Request Node (OpenProject aktualisieren)
  ↓
Switch Node (nach Benachrichtigungskanal)
  ├── Email → Send Email Node
  ├── Slack → Slack Node
  └── Website → HTTP Request Node (Website-API)
```

### 2.5 Reporting und Überwachung

#### 2.5.1 Status-Bericht-Generierung

**Input-Trigger**:
- Timed Trigger: Täglich/Wöchentlich
- Manual Trigger: Durch Projektmanager

**Konfigurationsparameter**:
- `REPORT_TYPES`: Definitionen verschiedener Berichtstypen
- `KPI_DEFINITIONS`: Formeln zur Berechnung von KPIs
- `DISTRIBUTION_LIST`: Empfänger für verschiedene Berichtstypen

**Prozessablauf**:
1. Datensammlung
   - Abruf von Status-Informationen aus GitLab, GitHub und OpenProject
   - Filterung nach Zeitraum und Projekten

2. KPI-Berechnung
   - Anwendung vordefinierter Formeln auf die gesammelten Daten
   - Berechnung von Trends und Abweichungen

3. Berichtserstellung
   - Anwendung des passenden Berichts-Templates
   - Generierung von Tabellen, Diagrammen und Textzusammenfassungen

4. Abweichungsanalyse
   - Identifikation signifikanter Abweichungen von Zielen oder Plänen
   - Generierung von Warnungen und Empfehlungen

5. Verteilung
   - Speicherung des Berichts in OpenProject
   - Versand an konfigurierte Empfänger via Email oder andere Kanäle

**Node-Struktur**:
```
Timer/Manual Trigger
  ↓
Function Node (Datensammlung aus allen Systemen)
  ↓
Function Node (KPI-Berechnung)
  ↓
Function Node (Berichtserstellung)
  ↓
IF Node (Abweichungen gefunden?)
  ├── JA → Function Node (Warnungen generieren)
  └── NEIN → Direkt zur Verteilung
      ↓
HTTP Request Node (OpenProject-Speicherung)
  ↓
Send Email Node (Bericht versenden)
```

#### 2.5.2 System-Überwachung

**Input-Trigger**:
- Timed Trigger: Alle 30 Minuten

**Konfigurationsparameter**:
- `API_HEALTH_CHECKS`: Endpunkte zur Prüfung der API-Verfügbarkeit
- `WORKFLOW_MONITORS`: Liste zu überwachender Workflows und deren erwartete Ausführungszeitpunkte
- `ALERT_THRESHOLDS`: Schwellenwerte für Warnungen und kritische Alerts

**Prozessablauf**:
1. API-Verfügbarkeitsprüfung
   - Test aller konfigurierten API-Endpunkte
   - Messung von Antwortzeiten und Verfügbarkeit

2. Workflow-Überwachung
   - Prüfung der letzten Ausführungszeitpunkte aller konfigurierten Workflows
   - Vergleich mit erwarteten Ausführungsintervallen

3. Ressourcennutzung
   - Überwachung der n8n-Instanz (CPU, Speicher, Festplatte)
   - Prüfung auf Ressourcenengpässe

4. Log-Analyse
   - Suche nach Fehlern und Warnungen in Logs
   - Identifikation wiederkehrender Probleme

5. Alarmierung
   - Generierung von Benachrichtigungen bei Überschreitung von Schwellenwerten
   - Eskalation kritischer Probleme

**Node-Struktur**:
```
Timer Trigger (30 Minuten)
  ↓
Function Node (API-Checks)
  ↓
Function Node (Workflow-Überwachung)
  ↓
Function Node (Ressourcennutzung prüfen)
  ↓
Function Node (Log-Analyse)
  ↓
IF Node (Probleme gefunden?)
  ├── JA → Switch Node (nach Schweregrad)
  │         ├── Warnung → Slack Node (Warnung senden)
  │         └── Kritisch → Send Email Node + Slack Node (Alarm senden)
  └── NEIN → End
```

## 3. Datenmodelle und Schemas

### 3.1 Referenz-Mapping-Schema

```json
{
  "issue_mapping": {
    "gitlab-[ID]": {
      "openproject_id": "string",
      "github_id": "string",
      "last_sync": "ISO8601 timestamp",
      "sync_source": "gitlab|github|openproject",
      "metadata": {
        "custom_field1": "value1",
        "custom_field2": "value2"
      }
    }
  },
  "repository_mapping": {
    "gitlab-[REPO_ID]": {
      "github_repo": "owner/repo",
      "openproject_project_id": "number",
      "sync_config": {
        "issues": true,
        "milestones": true,
        "releases": true
      }
    }
  }
}
```

### 3.2 Konfigurationsschema

```json
{
  "general": {
    "logging_level": "info|warn|error|debug",
    "notification_email": "email@example.com",
    "error_retry_attempts": 3,
    "error_retry_delay": 60000
  },
  "gitlab": {
    "api_url": "https://gitlab.example.com/api/v4",
    "webhook_secret": "secret-token",
    "projects": [
      {
        "id": 123,
        "name": "example-project",
        "product": "example-product"
      }
    ]
  },
  "github": {
    "api_url": "https://api.github.com",
    "webhook_secret": "secret-token",
    "repositories": [
      {
        "full_name": "owner/repo",
        "product": "example-product"
      }
    ]
  },
  "openproject": {
    "api_url": "https://openproject.example.com/api/v3",
    "projects": [
      {
        "id": 456,
        "name": "Example Project",
        "product": "example-product"
      }
    ]
  },
  "mappings": {
    "status": {
      "gitlab_to_openproject": {
        "opened": "in-progress",
        "closed": "closed"
      },
      "openproject_to_gitlab": {
        "in-progress": "opened",
        "closed": "closed"
      }
    },
    "priority": {
      "gitlab_to_openproject": {
        "high": "high",
        "normal": "normal",
        "low": "low"
      }
    }
  }
}
```

### 3.3 Datenvalidierungsschema

Für die Datenvalidierung in den Transformationsschritten werden JSONSchema-Definitionen verwendet:

```json
{
  "openproject_work_package": {
    "type": "object",
    "required": ["subject", "type", "project"],
    "properties": {
      "subject": { "type": "string", "maxLength": 255 },
      "description": { "type": "string" },
      "type": { 
        "type": "object",
        "required": ["href"],
        "properties": {
          "href": { "type": "string" }
        }
      },
      "project": {
        "type": "object",
        "required": ["href"],
        "properties": {
          "href": { "type": "string" }
        }
      },
      "status": {
        "type": "object",
        "required": ["href"],
        "properties": {
          "href": { "type": "string" }
        }
      }
    }
  }
}
```

## 4. API-Integrationsspezifikationen

### 4.1 GitLab-API-Integration

**Basis-URL**: `https://gitlab.example.com/api/v4`

**Authentifizierung**:
- Methode: Private Token / OAuth2
- Header: `PRIVATE-TOKEN: [token]` oder `Authorization: Bearer [token]`

**Hauptendpunkte**:
- `GET /projects/:id/issues`: Abruf von Issues
- `POST /projects/:id/issues`: Erstellung eines Issues
- `PUT /projects/:id/issues/:issue_id`: Aktualisierung eines Issues
- `GET /projects/:id/repository/commits`: Abruf von Commits
- `GET /projects/:id/milestones`: Abruf von Meilensteinen
- `GET /projects/:id/merge_requests`: Abruf von Merge Requests

**Webhooks-Konfiguration**:
- URL: `http://n8n-server/webhook/gitlab-issues`
- Secret Token: Konfigurierbar
- Trigger-Events: Issues, Merge Requests, Tags, Milestones

**Rate-Limiting**:
- Bei lokalen GitLab-Installationen in der Regel keine Beschränkungen
- Implementierung einer Wartezeit von 100ms zwischen aufeinanderfolgenden Anfragen zur Schonung des Servers

### 4.2 GitHub-API-Integration

**Basis-URL**: `https://api.github.com`

**Authentifizierung**:
- Methode: OAuth2
- Header: `Authorization: Bearer [token]`

**Hauptendpunkte**:
- `GET /repos/:owner/:repo/issues`: Abruf von Issues
- `POST /repos/:owner/:repo/issues`: Erstellung eines Issues
- `PATCH /repos/:owner/:repo/issues/:issue_number`: Aktualisierung eines Issues
- `GET /repos/:owner/:repo/releases`: Abruf von Releases
- `POST /repos/:owner/:repo/releases`: Erstellung eines Releases
- `GET /repos/:owner/:repo/commits`: Abruf von Commits

**Webhooks-Konfiguration**:
- URL: `http://n8n-server/webhook/github-events`
- Secret: Konfigurierbar
- Trigger-Events: Issues, Pull Requests, Releases, Stars

**Rate-Limiting**:
- Standard: 5.000 Anfragen pro Stunde
- Implementierung einer exponentiellen Backoff-Strategie bei Rate-Limit-Fehlern
- Batching von Anfragen zur Minimierung der API-Aufrufe

### 4.3 OpenProject-API-Integration

**Basis-URL**: `https://openproject.example.com/api/v3`

**Authentifizierung**:
- Methode: API Token
- Header: `Authorization: Basic YXBpa2V5OltBUElfS0VZXQo=` (apikey:[API_KEY] in Base64)

**Hauptendpunkte**:
- `GET /work_packages`: Abruf von Work Packages
- `POST /projects/:id/work_packages`: Erstellung eines Work Package
- `PATCH /work_packages/:id`: Aktualisierung eines Work Package
- `GET /projects`: Abruf von Projekten
- `GET /statuses`: Abruf von Status-Definitionen
- `GET /types`: Abruf von Work-Package-Typen

**Besonderheiten**:
- HAL+JSON Format für Requests und Responses
- Komplexes Beziehungsmodell mit _links-Objekten
- Spezielle Behandlung von benutzerdefinierten Feldern

**Rate-Limiting**:
- Normalerweise keine strengen Limits bei lokalen Installationen
- Implementierung einer Verzögerung zwischen Anfragen zur Vermeidung von Serverlast

## 5. Fehlerbehandlung und Robustheit

### 5.1 Fehlertypen und -behandlung

1. **Temporäre Netzwerkfehler**
   - Automatische Wiederholung mit exponentieller Verzögerung
   - Maximal 3 Wiederholungsversuche

2. **API-Authentifizierungsfehler**
   - Sofortige Benachrichtigung an Administratoren
   - Keine automatischen Wiederholungen (erfordert menschliches Eingreifen)
   - Detailliertes Logging von Authentifizierungsproblemen

3. **Rate-Limiting-Fehler**
   - Dynamische Anpassung der Anfragerate
   - Automatische Wiederaufnahme nach Wartezeit
   - Priorisierung wichtiger Operationen

4. **Datenvalidierungsfehler**
   - Detaillierte Protokollierung ungültiger Daten
   - Teilweise Verarbeitung, wo möglich (Fortsetzung trotz einzelner Fehler)
   - Benachrichtigung bei systematischen Validierungsproblemen

5. **Systemfehler**
   - Failsafe-Modus bei kritischen Problemen
   - Automatischer Neustart fehlerhafter Workflows
   - Eskalation an Administratoren bei wiederholten Problemen

### 5.2 Robustheitsmaßnahmen

1. **Idempotente Operationen**
   - Alle Synchronisationsoperationen sind idempotent gestaltet
   - Wiederholte Ausführung führt zum gleichen Ergebnis
   - Vermeidung von Duplikaten durch Referenz-Tracking

2. **Transaktionsmanagement**
   - Atomare Operationen, wo möglich
   - Zwei-Phasen-Commits bei komplexen Operationen
   - Rollback-Mechanismen bei teilweise fehlgeschlagenen Operationen

3. **Statemonitoring**
   - Überwachung des Systemzustands
   - Automatische Wiederherstellung bei inkonsistenten Zuständen
   - Periodische Konsistenzprüfungen

4. **Datenredundanz**
   - Backup-Mechanismen für kritische Daten
   - Wiederherstellungspunkte für Referenz-Mappings
   - Regelmäßige Sicherung von Konfigurationen

5. **Circuit Breaker Pattern**
   - Unterbrechung von Operationen bei wiederholten Fehlern
   - Automatische Wiederaufnahme nach definierten Zeitintervallen
   - Degradierter Modus für nicht-kritische Funktionen

## 6. Sicherheitsmaßnahmen

### 6.1 Datensicherheit

1. **Credential-Management**
   - Verschlüsselte Speicherung aller API-Tokens und Geheimnisse
   - Rotation von Credentials nach konfigurierbaren Zeitplänen
   - Zugriffsschutz auf Credential-Speicher

2. **Datenübertragung**
   - TLS/SSL für alle API-Kommunikation
   - Verifizierung von Server-Zertifikaten
   - Keine Übertragung sensibler Daten in URL-Parametern

3. **Datenisolation**
   - Strikte Trennung von Produktionsdaten und Testdaten
   - Sandbox-Umgebungen für Tests
   - Minimale Datenübertragung (nur erforderliche Felder)

### 6.2 Zugriffssicherheit

1. **Webhook-Authentifizierung**
   - Verifizierung von Webhook-Signatures
   - Validierung von Secret-Tokens
   - IP-basierte Filterung (optional)

2. **Berechtigungsprüfung**
   - Minimale erforderliche Berechtigungen für API-Tokens
   - Regelmäßige Überprüfung von Berechtigungen
   - Trennung von Lese- und Schreibzugriffen

3. **Audit-Logging**
   - Detaillierte Protokollierung aller Zugriffe
   - Nachverfolgung von API-Aufrufen
   - Unveränderliche Audit-Logs

### 6.3 Compliance-Maßnahmen

1. **Datenschutz**
   - Vermeidung der Übertragung personenbezogener Daten, wo nicht erforderlich
   - Anonymisierung von Benutzerinformationen in Logs
   - Einhaltung von DSGVO-Anforderungen

2. **Zugriffskontrollen**
   - Rollenbasierte Zugriffskontrollen für n8n-Workflows
   - Beschränkung des Zugriffs auf sensible Workflows
   - Zwei-Faktor-Authentifizierung für administrative Zugriffe

3. **Regelmäßige Überprüfungen**
   - Sicherheitsaudits der Workflows
   - Überprüfung von Zugriffsberechtigungen
   - Penetrationstests der exponierten Webhooks

## 7. Leistungsoptimierung

### 7.1 Optimierungsstrategien

1. **Batch-Verarbeitung**
   - Zusammenfassung mehrerer Operationen in einer Anfrage
   - Verarbeitung von Daten in konfigurierbaren Batch-Größen
   - Prioritätsbasierte Batching-Strategien

2. **Caching**
   - Implementierung eines In-Memory-Cache für häufig abgerufene Daten
   - TTL-basierte Cache-Invalidierung
   - Selektives Caching für unveränderliche Daten

3. **Asynchrone Verarbeitung**
   - Entkopplung von zeitkritischen Operationen
   - Implementierung von Warteschlangen für nicht-kritische Updates
   - Parallelisierung unabhängiger Operationen

4. **Inkrementelle Synchronisation**
   - Übertragung nur geänderter Daten
   - Nutzung von Änderungszeitstempeln
   - Differenzielles Update statt vollständiger Ersetzung

### 7.2 Ressourcenverwaltung

1. **CPU-Optimierung**
   - Effiziente Algorithmen für Datentransformationen
   - Vermeidung redundanter Berechnungen
   - Lastverteilung bei ressourcenintensiven Operationen

2. **Speicheroptimierung**
   - Minimierung von Objektkopien in Transformationsprozessen
   - Streaming-basierte Verarbeitung großer Datensätze
   - Garbage-Collection-Strategien für temporäre Daten

3. **I/O-Optimierung**
   - Minimierung von API-Aufrufen durch Datenaggregation
   - Priorisierung wichtiger API-Operationen
   - Zeitplanung von I/O-intensiven Operationen in Nebenzeiten

### 7.3 Skalierungsstrategien

1. **Horizontale Skalierung**
   - Verteilung von Workflows auf mehrere n8n-Instanzen
   - Lastverteilung über Redis-Queue
   - Konsistente Datenspeicherung über gemeinsame Datenbank

2. **Vertikale Skalierung**
   - Optimierung von Ressourcenzuweisungen für n8n-Instanzen
   - Monitoring von Ressourcenverbrauch
   - Dynamische Anpassung von Containerressourcen

3. **Funktionale Partitionierung**
   - Trennung von Workflows nach Funktion
   - Isolation ressourcenintensiver Operationen
   - Priorisierung kritischer Workflows

## 8. Deployment und Betrieb

### 8.1 Deployment-Strategie

1. **Umgebungen**
   - Entwicklung: Für Workflow-Entwicklung und Tests
   - Staging: Für Integrationstest mit Testsystemen
   - Produktion: Für den produktiven Betrieb

2. **Versionierung**
   - Semantische Versionierung für Workflows
   - Historisierung von Workflow-Änderungen
   - Rollback-Möglichkeiten für fehlerhafte Updates

3. **Continuous Integration/Deployment**
   - Automatisierte Tests vor Deployment
   - Stufenweises Rollout von Änderungen
   - Automatisierte Validierung nach Deployment

### 8.2 Monitoring und Wartung

1. **Systemüberwachung**
   - Metriken-Sammlung (CPU, Speicher, Durchsatz)
   - Alarmierung bei Anomalien
   - Visualisierung von Trends

2. **Workflow-Überwachung**
   - Ausführungsstatistiken (Erfolg, Fehler, Dauer)
   - Durchsatzmetriken
   - Qualitätsmetriken (Datenvalidität, Synchronisationskonsistenz)

3. **Wartungsprozesse**
   - Geplante Wartungsfenster
   - Automatisierte Backup-Prozesse
   - Health-Checks nach Wartungsarbeiten

### 8.3 Notfallwiederherstellung

1. **Backup-Strategie**
   - Tägliche Sicherung aller Workflows
   - Stündliche Sicherung kritischer Daten (Referenz-Mappings)
   - Off-Site-Backups für Katastrophenschutz

2. **Wiederherstellungsprozesse**
   - Dokumentierte Wiederherstellungsabläufe
   - Regelmäßige Wiederherstellungstests
   - RTO (Recovery Time Objective) < 4 Stunden

3. **Hochverfügbarkeit**
   - Redundante n8n-Instanzen
   - Automatische Failover-Mechanismen
   - Geografisch verteilte Backups

## 9. Implementierungsdetails für n8n-spezifische Funktionen

### 9.1 JSONata-Transformationen

Für komplexe Datentransformationen werden JSONata-Ausdrücke verwendet, insbesondere in folgenden Bereichen:

1. **GitLab zu OpenProject Issue-Mapping**:
```
{
  "subject": $.title,
  "description": {
    "raw": "**GitLab Issue #" & $.iid & "**\n\n" & $.description & "\n\n---\n*Synchronisiert von GitLab*"
  },
  "_links": {
    "type": {
      "href": "/api/v3/types/" & $lookup($OPENPROJECT_TYPE_MAPPING, $.labels[0])
    },
    "status": {
      "href": "/api/v3/statuses/" & $lookup($OPENPROJECT_STATUS_MAPPING, $.state)
    },
    "project": {
      "href": "/api/v3/projects/" & $lookup($OPENPROJECT_PROJECT_MAPPING, $.project_id)
    }
  },
  "customField1": $.labels[0]
}
```

2. **OpenProject zu GitLab Status-Update**:
```
{
  "state_event": $lookup($GITLAB_STATUS_MAPPING, $substringAfter($.status._links.self.href, "statuses/"))
}
```

3. **Komplexe Aggregation für Reporting**:
```
{
  "summary": {
    "total_issues": $count($.issues),
    "open_issues": $count($.issues[state="opened"]),
    "closed_issues": $count($.issues[state="closed"]),
    "completion_rate": ($count($.issues[state="closed"]) / $count($.issues)) * 100
  },
  "by_label": $map(
    $distinct($.issues.labels[].*), 
    function($label) {
      {
        "label": $label,
        "count": $count($.issues[labels[*] ~> $contains($label)]),
        "open": $count($.issues[labels[*] ~> $contains($label) and state="opened"]),
        "closed": $count($.issues[labels[*] ~> $contains($label) and state="closed"])
      }
    }
  )
}
```

### 9.2 Webhook-Konfigurationen

Beispiel für eine GitLab-Webhook-Konfiguration in n8n:

```javascript
{
  "name": "GitLab Issue Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1,
  "position": [100, 300],
  "webhookId": "gitlab-issue-webhook",
  "httpMethod": "POST",
  "path": "gitlab-issues",
  "responseMode": "onReceived",
  "responseData": "firstEntryJson",
  "options": {
    "bodyContentType": "json",
    "responseHeaders": {
      "entries": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ]
    }
  }
}
```

### 9.3 Error-Handling mit n8n

Implementierung eines robusten Error-Handlings mit n8n-spezifischen Funktionen:

```javascript
// Function Node für Error-Handling
function handleError(node, msg, err) {
  const errorData = {
    timestamp: new Date().toISOString(),
    workflow: $workflow.id,
    node: node.name,
    error: err.message,
    input: JSON.stringify(msg),
    stack: err.stack
  };
  
  // Log error to dedicated error collection
  $node.context.errorLog = $node.context.errorLog || [];
  $node.context.errorLog.push(errorData);
  
  // Determine if retry is appropriate
  const isRetryable = err.message.includes('timeout') || 
                      err.message.includes('rate limit') ||
                      err.code === 'ECONNRESET';
  
  // Get retry count
  const retryCount = $node.context.retryCount || 0;
  
  if (isRetryable && retryCount < 3) {
    $node.context.retryCount = retryCount + 1;
    // Exponential backoff
    const waitTime = Math.pow(2, retryCount) * 1000;
    
    setTimeout(() => {
      // Re-execute the node with the same input
      $node.runWithInput(msg);
    }, waitTime);
    
    return { retry: true, count: $node.context.retryCount, waitTime };
  } else {
    // Critical error or retry exhausted
    if (process.env.ERROR_NOTIFICATION_WEBHOOK) {
      $http.post(process.env.ERROR_NOTIFICATION_WEBHOOK, {
        json: {
          text: `Error in workflow ${$workflow.id}, node ${node.name}: ${err.message}`
        }
      });
    }
    
    return { retry: false, error: errorData };
  }
}

// Usage in workflow
try {
  // Node operation here
} catch (error) {
  return handleError($node, $input.all(), error);
}
```

### 9.4 Workflow-Kommunikation in n8n

Implementierung der Kommunikation zwischen Workflows:

1. **Workflow-Trigger durch einen anderen Workflow**:
```javascript
// In einem Workflow, der einen anderen starten soll
const workflowTriggerNode = {
  "name": "Start Release Workflow",
  "type": "n8n-nodes-base.executeWorkflow",
  "typeVersion": 1,
  "position": [900, 300],
  "parameters": {
    "workflowId": "12345",
    "runWithIssueType": true,
    "data": "={{ $json }}"
  }
};
```

2. **Gemeinsame Daten über n8n-Variablen**:
```javascript
// Speichern von gemeinsamen Daten
const setVariableNode = {
  "name": "Store Reference Mapping",
  "type": "n8n-nodes-base.function",
  "typeVersion": 1,
  "position": [1100, 300],
  "parameters": {
    "functionCode": `
      // Get current mapping
      const mappingVar = process.env.REFERENCE_MAPPING || '{}';
      let mapping = JSON.parse(mappingVar);
      
      // Update with new mapping
      const gitlabId = $input.item.json.gitlabIssueId;
      const openProjectId = $input.item.json.openProjectWorkPackageId;
      
      if (!mapping.issues) mapping.issues = {};
      mapping.issues[\`gitlab-\${gitlabId}\`] = {
        openproject_id: openProjectId,
        last_sync: new Date().toISOString(),
        sync_source: 'gitlab'
      };
      
      // Store back to environment
      process.env.REFERENCE_MAPPING = JSON.stringify(mapping);
      
      return {mapping};
    `
  }
};
```

## 10. Teststrategien

### 10.1 Testebenen

1. **Unit-Tests**
   - Test einzelner Transformationslogiken
   - Validierung von JSONata-Ausdrücken
   - Überprüfung von Fehlerbehandlungsroutinen

2. **Integrationstests**
   - Test der Interaktion zwischen Workflows
   - Validierung von API-Integrationen mit Mock-Diensten
   - Überprüfung von Datenflüssen zwischen Komponenten

3. **Systemtests**
   - End-to-End-Tests vollständiger Szenarien
   - Validierung realer API-Interaktionen in Testumgebungen
   - Überprüfung von Fehlerszenarien und Wiederherstellungsprozessen

### 10.2 Testumgebungen

1. **Entwicklungsumgebung**
   - Lokale n8n-Instanz für Entwickler
   - Mock-Server für externe APIs
   - CI/CD-Pipeline mit automatisierten Tests

2. **Testumgebung**
   - Dedizierte n8n-Instanz
   - Testinstanzen von GitLab, GitHub und OpenProject
   - Isolierte Daten für reproduzierbare Tests

3. **Staging-Umgebung**
   - Produktionsähnliche Konfiguration
   - Kopien oder Testprojekte in den Produktivsystemen
   - Performancetests und Lastproben

### 10.3 Testautomatisierung

1. **Automatisierte Tests**
   - Unit-Tests mit Jest für Transformationslogik
   - API-Integrationstests mit Postman/Newman
   - End-to-End-Tests mit Cypress oder ähnlichen Tools

2. **Continous Integration**
   - Automatische Testausführung bei Code-Änderungen
   - Validierung von Workflows vor Deployment
   - Automatisierte Berichte über Testergebnisse

3. **Monitoring-basierte Tests**
   - Synthetische Transaktionen für kontinuierliche Validierung
   - Canary-Tests in Produktion
   - A/B-Tests für Workflow-Optimierungen

## 11. Dokumentation

### 11.1 Entwicklerdokumentation

1. **Architekturübersicht**
   - Systemkomponenten und ihre Interaktionen
   - Datenflussdiagramme
   - Technologiestacks und Abhängigkeiten

2. **Workflow-Dokumentation**
   - Detaillierte Beschreibung jedes Workflows
   - Node-Konfigurationen und Parameter
   - Fehlerbehandlungsstrategien

3. **API-Dokumentation**
   - Verwendete Endpunkte und ihre Parameter
   - Authentifizierungsmethoden
   - Beispielanfragen und -antworten

### 11.2 Betriebsdokumentation

1. **Installationsanleitung**
   - Voraussetzungen und Abhängigkeiten
   - Schritt-für-Schritt-Installationsanweisungen
   - Konfigurationsoptionen

2. **Betriebshandbuch**
   - Überwachungs- und Wartungsprozesse
   - Problembehandlungsanleitungen
   - Backup- und Wiederherstellungsverfahren

3. **Sicherheitsrichtlinien**
   - Zugriffskontrollen und Berechtigungen
   - Credential-Management
   - Sicherheitsaudits und -überprüfungen

### 11.3 Benutzerdokumentation

1. **Administratorhandbuch**
   - Konfiguration und Anpassung
   - Benutzerverwaltung
   - Systemüberwachung

2. **Endbenutzerhandbuch**
   - Übersicht über Integrationsfunktionen
   - Erwartetes Verhalten der Synchronisation
   - Häufig gestellte Fragen

3. **Schulungsmaterialien**
   - Einführungsvideos
   - Schritt-für-Schritt-Anleitungen
   - Best Practices

## 12. Roadmap und zukünftige Erweiterungen

### 12.1 Kurzfristige Erweiterungen (3-6 Monate)

1. **Erweiterte Berichterstattung**
   - Dashboards für Synchronisationsstatistiken
   - Anpassbare Berichtsvorlagen
   - Integration mit Business Intelligence-Tools

2. **Verbesserte Benutzeroberfläche**
   - Administrationsinterface für Konfiguration
   - Visualisierung von Synchronisationsstatus
   - Self-Service-Portal für Projektmanager

3. **Erweitertes API-Mapping**
   - Unterstützung zusätzlicher Feldtypen
   - Benutzerdefinierte Transformationsregeln
   - Verbesserte Fehlerbehandlung

### 12.2 Mittelfristige Erweiterungen (6-12 Monate)

1. **KI-gestützte Analysen**
   - Automatische Kategorisierung von Issues
   - Vorhersage von Projekt-Meilensteinen
   - Erkennung von Problembereichen

2. **Multi-Instance-Support**
   - Unterstützung mehrerer GitLab/GitHub-Instanzen
   - Föderierte Synchronisation
   - Instance-übergreifende Aggregation

3. **Erweiterte Automatisierung**
   - Regelbasierte Automatisierungen
   - Event-basierte Trigger für Geschäftsprozesse
   - Workflow-Approval-Prozesse

### 12.3 Langfristige Vision (1-2 Jahre)

1. **Plattform-Erweiterung**
   - Integration weiterer DevOps-Tools (Jira, Azure DevOps)
   - Unterstützung zusätzlicher Projektmanagement-Systeme
   - Erweitertes Ökosystem von Integrationen

2. **Unternehmensweites Management**
   - Organisationsübergreifende Synchronisation
   - Governance-Funktionen
   - Compliance- und Audit-Features

3. **Self-Learning-System**
   - Automatische Optimierung von Workflows
   - Selbstheilende Integrationen
   - Proaktive Problemerkennung

## 13. Abschluss und Vorbehalt

Diese technische Spezifikation bildet die Grundlage für die Implementierung des n8n-basierten Integrationssystems zwischen GitHub, GitLab und OpenProject. Sie ist als lebendiges Dokument zu verstehen, das während der Implementierungsphase verfeinert und angepasst werden kann.

Die tatsächliche Implementierung kann aufgrund von technischen Einschränkungen oder neuen Anforderungen von dieser Spezifikation abweichen. Alle wesentlichen Änderungen sind zu dokumentieren und mit den relevanten Stakeholdern abzustimmen.
