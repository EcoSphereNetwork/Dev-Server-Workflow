# Implementierungsplan: n8n-Integration von GitLab, OpenProject und GitHub

Dieser Plan beschreibt die vollständige Implementierung einer n8n-basierten Integration zwischen GitLab, OpenProject und GitHub unter Verwendung der Community-Nodes.

## 1. Vorbereitung und Einrichtung

### 1.1 Installation der n8n-Umgebung

```bash
# Erstellung eines Verzeichnisses für n8n
mkdir -p /opt/n8n
cd /opt/n8n

# Erstellung einer Docker-Compose-Datei
cat > docker-compose.yml << EOF
version: '3'

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=${N8N_PORT:-5678}
      - N8N_PROTOCOL=${N8N_PROTOCOL:-http}
      - NODE_ENV=production
      - N8N_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD:-admin}
      - N8N_COMMUNITY_PACKAGES_ALLOW_INSTALL=true
      - N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
    volumes:
      - n8n_data:/home/node/.n8n
      - ./custom_nodes:/home/node/.n8n/custom

volumes:
  n8n_data:
EOF

# Verzeichnis für benutzerdefinierte Nodes erstellen
mkdir -p custom_nodes

# Starten der n8n-Instanz
docker-compose up -d
```

### 1.2 Installation der Community-Nodes

```bash
# Verzeichnis für die Installation wechseln
cd /opt/n8n/custom_nodes

# OpenProject-Node Installation
git clone https://github.com/vogl-electronic/n8n-nodes-openproject.git
cd n8n-nodes-openproject
npm install
npm run build
cd ..

# GitHub-Node Installation
git clone https://github.com/jeffdanielperso/n8n-nodes-github.git
cd n8n-nodes-github
npm install
npm run build
cd ..

# GitLab-Node Installation (RXAP)
git clone https://gitlab.com/rxap/packages.git rxap-packages
cd rxap-packages/packages/n8n/nodes/gitlab
npm install
npm run build
cd ../../../../

# Neustart des n8n-Containers
cd /opt/n8n
docker-compose restart
```

## 2. Konfiguration der Credentials

### 2.1 GitLab-Credentials

1. In GitLab navigieren zu: **Einstellungen** > **Zugriffstoken**
2. Erstellen eines Personal Access Tokens mit folgenden Scopes:
   - `api` (API-Zugriff)
   - `read_repository` (Repository lesen)
   - `write_repository` (Repository schreiben)
3. Token kopieren und sicher aufbewahren
4. In n8n unter **Credentials** eine neue GitLab-API-Credential erstellen:
   - Name: `GitLab-API`
   - GitLab URL: `https://gitlab.example.com` (anpassen)
   - Access Token: `[Ihr Token]`

### 2.2 OpenProject-Credentials

1. In OpenProject navigieren zu: **Mein Konto** > **Zugriffstoken**
2. Erstellen eines API-Tokens mit folgenden Berechtigungen:
   - `api_v3` (API Zugriff)
   - `work_package_read` (Work Packages lesen)
   - `work_package_write` (Work Packages schreiben)
3. Token kopieren und sicher aufbewahren
4. In n8n unter **Credentials** eine neue OpenProject-API-Credential erstellen:
   - Name: `OpenProject-API`
   - OpenProject URL: `https://openproject.example.com` (anpassen)
   - API-Token: `[Ihr Token]`

### 2.3 GitHub-Credentials

1. In GitHub navigieren zu: **Settings** > **Developer settings** > **Personal access tokens**
2. Erstellen eines Personal Access Tokens mit folgenden Scopes:
   - `repo` (Repository Zugriff)
   - `issues` (Issues verwalten)
3. Token kopieren und sicher aufbewahren
4. In n8n unter **Credentials** eine neue GitHub-API-Credential erstellen:
   - Name: `GitHub-API`
   - GitHub URL: `https://github.com` (bei Enterprise-Installation anpassen)
   - Access Token: `[Ihr Token]`

## 3. Mapping-Konfiguration

### 3.1 Projekt-Mapping

Erstellen Sie eine JSON-Datei mit dem Mapping zwischen GitLab-Projekt-IDs und OpenProject-Projekt-IDs:

```json
{
  "project_mapping": {
    "gitlab_to_openproject": {
      "123": "456",
      "124": "457",
      "125": "458"
    },
    "gitlab_to_github": {
      "123": "organization/repo1",
      "124": "organization/repo2",
      "125": "organization/repo3"
    }
  }
}
```

Speichern Sie diese Datei als `mapping_config.json` im n8n-Datenverzeichnis.

### 3.2 Status-Mapping

Erstellen Sie ein Mapping für den Status:

```json
{
  "status_mapping": {
    "gitlab_to_openproject": {
      "opened": "1",
      "reopened": "1",
      "closed": "5"
    },
    "openproject_to_gitlab": {
      "1": "reopened",
      "5": "closed"
    },
    "openproject_to_github": {
      "1": "open",
      "5": "closed"
    }
  }
}
```

### 3.3 Label/Typ-Mapping

Erstellen Sie ein Mapping für Labels und Typen:

```json
{
  "type_mapping": {
    "gitlab_labels_to_openproject_type": {
      "bug": "1",
      "feature": "2",
      "task": "3",
      "user-story": "4"
    },
    "openproject_type_to_github_labels": {
      "1": ["bug", "defect"],
      "2": ["feature", "enhancement"],
      "3": ["task"],
      "4": ["user-story"]
    }
  }
}
```

## 4. Webhook-Konfiguration

### 4.1 GitLab-Webhook Einrichtung

1. Navigieren Sie in GitLab zu: **Projekt-Einstellungen** > **Webhooks**
2. Erstellen Sie einen neuen Webhook:
   - URL: `https://n8n.example.com/webhook/gitlab-issue-webhook` (anpassen)
   - Secret Token: `[Geheimer Token]` (generieren und sicher aufbewahren)
   - Trigger-Ereignisse:
     - Issues
     - Comments
     - Merge Requests
3. Webhook speichern und testen

### 4.2 OpenProject-Webhook Einrichtung

Falls OpenProject Webhooks unterstützt:

1. Navigieren Sie in OpenProject zur Webhook-Konfiguration
2. Erstellen Sie einen neuen Webhook:
   - URL: `https://n8n.example.com/webhook/openproject-webhook` (anpassen)
   - Events:
     - WorkPackage created
     - WorkPackage updated
     - Comment added
3. Webhook speichern und testen

### 4.3 GitHub-Webhook Einrichtung

1. Navigieren Sie in GitHub zu: **Repository-Einstellungen** > **Webhooks**
2. Erstellen Sie einen neuen Webhook:
   - Payload URL: `https://n8n.example.com/webhook/github-webhook` (anpassen)
   - Content type: `application/json`
   - Secret: `[Geheimer Token]` (generieren und sicher aufbewahren)
   - Trigger-Ereignisse:
     - Issues
     - Issue comments
     - Pull requests
3. Webhook speichern und testen

## 5. Workflow-Implementierung

### 5.1 GitLab → OpenProject Workflow

Implementieren Sie den oben im Code-Beispiel gezeigten Workflow, der GitLab-Issues mit OpenProject synchronisiert:

1. Importieren Sie das Workflow-JSON in n8n
2. Passen Sie die Credentials-Referenzen an
3. Aktualisieren Sie die URLs und IDs entsprechend Ihrer Umgebung
4. Aktivieren Sie den Workflow

### 5.2 OpenProject → GitLab Workflow

Erstellen Sie einen komplementären Workflow für die Synchronisation von OpenProject zu GitLab:

1. Erstellen Sie einen neuen Workflow in n8n
2. Fügen Sie einen OpenProject-Webhook/Trigger hinzu
3. Extrahieren Sie die relevanten Work-Package-Daten
4. Prüfen Sie, ob das Work Package mit einem GitLab-Issue verknüpft ist
5. Transformieren Sie die OpenProject-Daten in das GitLab-Format
6. Aktualisieren Sie das GitLab-Issue über die GitLab-Node
7. Aktualisieren Sie das Referenz-Mapping
8. Aktivieren Sie den Workflow

### 5.3 GitHub-Integration Workflow

Erstellen Sie einen Workflow für die GitHub-Integration:

1. Implementieren Sie den im Code-Beispiel gezeigten Teil für die GitHub-Integration
2. Ergänzen Sie einen GitHub-Webhook für bidirektionale Synchronisation
3. Implementieren Sie die Transformation zwischen GitHub und den anderen Systemen
4. Aktivieren Sie den Workflow

## 6. Testen und Validierung

### 6.1 Test-Szenarien

Erstellen Sie Testfälle für die folgenden Szenarien:

1. **Neues GitLab-Issue**:
   - Erstellen Sie ein neues Issue in GitLab
   - Prüfen Sie, ob es korrekt in OpenProject und GitHub erscheint

2. **Status-Updates**:
   - Ändern Sie den Status eines Issues in GitLab
   - Prüfen Sie, ob der Status in OpenProject und GitHub aktualisiert wird

3. **Kommentarsynchronisation**:
   - Fügen Sie einen Kommentar in GitLab hinzu
   - Prüfen Sie, ob der Kommentar in OpenProject und GitHub erscheint

4. **Bidirektionale Updates**:
   - Aktualisieren Sie ein Work Package in OpenProject
   - Prüfen Sie, ob die Änderungen in GitLab und GitHub synchronisiert werden

### 6.2 Fehlerszenarien

Testen Sie auch Fehlerszenarien:

1. **Verbindungsabbrüche**:
   - Simulieren Sie einen API-Fehler oder Verbindungsabbruch
   - Prüfen Sie, ob der Workflow robust reagiert und wiederholt

2. **Ungültige Daten**:
   - Erzeugen Sie ungültige Daten (z.B. fehlende Pflichtfelder)
   - Prüfen Sie, ob die Fehlerbehandlung korrekt funktioniert

3. **Synchronisationsschleifen**:
   - Aktualisieren Sie Daten schnell in mehreren Systemen
   - Prüfen Sie, ob keine Schleifen entstehen

## 7. Produktions-Deployment

### 7.1 Übertragung in Produktion

1. Exportieren Sie die getesteten Workflows aus der Testumgebung
2. Importieren Sie die Workflows in die Produktionsumgebung
3. Aktualisieren Sie die Credentials und URLs für die Produktionsumgebung
4. Aktivieren Sie die Workflows in Produktion

### 7.2 Monitoring-Einrichtung

1. Konfigurieren Sie das Benachrichtigungssystem für Fehler (z.B. Slack, E-Mail)
2. Richten Sie ein Dashboard für die Workflow-Überwachung ein
3. Erstellen Sie regelmäßige Berichte über Synchronisationsstatistiken

### 7.3 Backup-Strategie

1. Konfigurieren Sie regelmäßige Backups der n8n-Daten
2. Dokumentieren Sie die Wiederherstellungsprozedur
3. Testen Sie die Wiederherstellung in einer separaten Umgebung

## 8. Wartung und Erweiterung

### 8.1 Regelmäßige Wartung

1. Planen Sie regelmäßige Überprüfungen der Workflows
2. Aktualisieren Sie n8n und die Community-Nodes regelmäßig
3. Überprüfen Sie die API-Tokens auf Gültigkeit

### 8.2 Geplante Erweiterungen

1. Implementieren Sie zusätzliche Synchronisationen (z.B. für Anhänge, Zeiterfassung)
2. Erweitern Sie die Berichtsfunktionen
3. Integrieren Sie weitere Systeme nach Bedarf

## 9. Dokumentation

### 9.1 Technische Dokumentation

1. Dokumentieren Sie die Workflow-Architektur
2. Erstellen Sie eine detaillierte Beschreibung aller Nodes und Konfigurationen
3. Dokumentieren Sie die Fehlerbehandlung und Wiederherstellungsprozesse

### 9.2 Benutzerhandbuch

1. Erstellen Sie eine Anleitung für Endbenutzer
2. Dokumentieren Sie typische Anwendungsfälle
3. Erstellen Sie eine FAQ für häufige Fragen und Probleme

## 10. Schulung und Übergabe

1. Schulen Sie das Administrationsteam zur Wartung des Systems
2. Schulen Sie die Endbenutzer über die neuen Funktionen
3. Übergeben Sie die Dokumentation und den Quellcode

Dieser Implementierungsplan bietet eine strukturierte Anleitung für die vollständige Integration von GitLab, OpenProject und GitHub mit n8n unter Verwendung der spezialisierten Community-Nodes. Durch die Befolgung dieses Plans kann eine robuste, wartbare und skalierbare Lösung implementiert werden.
