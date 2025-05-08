# Implementierungsplan für MCP-Server-Ökosystem und n8n-Workflows

## Übersicht

Dieser Implementierungsplan beschreibt die Verbesserung und Erweiterung des MCP-Server-Ökosystems und der n8n-Workflows im Dev-Server-Workflow-Projekt. Der Plan umfasst die Integration verschiedener MCP-Server als Docker-Container, die Verbesserung der n8n-Workflows und die Schaffung einer nahtlosen Verbindung zwischen allen Komponenten.

## Inhaltsverzeichnis

1. [Ziele und Anforderungen](#1-ziele-und-anforderungen)
2. [Architektur](#2-architektur)
3. [MCP-Server-Implementierung](#3-mcp-server-implementierung)
4. [n8n-Workflow-Verbesserungen](#4-n8n-workflow-verbesserungen)
5. [Integration und Konnektivität](#5-integration-und-konnektivität)
6. [Sicherheit und Berechtigungen](#6-sicherheit-und-berechtigungen)
7. [Monitoring und Logging](#7-monitoring-und-logging)
8. [Dokumentation](#8-dokumentation)
9. [Testplan](#9-testplan)
10. [Rollout-Strategie](#10-rollout-strategie)
11. [Wartung und Support](#11-wartung-und-support)

## 1. Ziele und Anforderungen

### 1.1 Hauptziele

- Integration aller spezifizierten MCP-Server als Docker-Container
- Verbesserung der bestehenden n8n-Workflows für optimale Nutzung der MCP-Server
- Schaffung einer nahtlosen Verbindung zwischen OpenHands, MCP-Servern und n8n
- Implementierung eines sicheren und skalierbaren MCP-Server-Ökosystems
- Bereitstellung einer umfassenden Dokumentation für Entwickler und Benutzer

### 1.2 Anforderungen

- Alle MCP-Server müssen als Docker-Container implementiert werden
- Die Container müssen sicher konfiguriert sein (Least-Privilege-Prinzip)
- Die n8n-Workflows müssen die MCP-Server-Funktionalitäten optimal nutzen
- Das System muss skalierbar und erweiterbar sein
- Die Implementierung muss gut dokumentiert sein

## 2. Architektur

### 2.1 Gesamtarchitektur

```
+----------------------------------+
|           OpenHands              |
+----------------+----------------+
                 |
                 v
+----------------+----------------+
|        MCP-Server-Ökosystem     |
|                                 |
|  +-------------+  +----------+  |
|  | Brave Search|  | Filesystem|  |
|  +-------------+  +----------+  |
|                                 |
|  +-------------+  +----------+  |
|  | GitHub      |  | GitLab   |  |
|  +-------------+  +----------+  |
|                                 |
|  +-------------+  +----------+  |
|  | Memory      |  | Wolfram  |  |
|  +-------------+  +----------+  |
|                                 |
|  +-------------+  +----------+  |
|  | Desktop Cmd |  | Wikipedia|  |
|  +-------------+  +----------+  |
|                                 |
|  +-------------+  +----------+  |
|  | DuckDuckGo  |  | Grafana  |  |
|  +-------------+  +----------+  |
|                                 |
|  +-------------+  +----------+  |
|  | Hyperbrowser|  | Oxylabs  |  |
|  +-------------+  +----------+  |
|                                 |
|  +-------------+  +----------+  |
|  | E2B         |  | Inspector|  |
|  +-------------+  +----------+  |
|                                 |
+----------------+----------------+
                 |
                 v
+----------------+----------------+
|            n8n-Workflows        |
|                                 |
|  +-------------+  +----------+  |
|  | MCP-Trigger |  | MCP-Integ|  |
|  +-------------+  +----------+  |
|                                 |
|  +-------------+  +----------+  |
|  | GitHub-Integ|  | GitLab-Int|  |
|  +-------------+  +----------+  |
|                                 |
|  +-------------+  +----------+  |
|  | OpenProject |  | AppFlowy |  |
|  +-------------+  +----------+  |
|                                 |
+----------------------------------+
```

### 2.2 Container-Architektur

Alle MCP-Server werden als Docker-Container implementiert und über ein gemeinsames Docker-Netzwerk verbunden. Die Container werden über Docker Compose orchestriert und können unabhängig voneinander gestartet, gestoppt und aktualisiert werden.

### 2.3 Workflow-Architektur

Die n8n-Workflows werden verbessert, um die MCP-Server-Funktionalitäten optimal zu nutzen. Sie werden in folgende Kategorien unterteilt:

- **MCP-Trigger-Workflows**: Reagieren auf Ereignisse von MCP-Servern
- **MCP-Integration-Workflows**: Integrieren MCP-Server mit anderen Systemen
- **Tool-spezifische Workflows**: Nutzen spezifische Funktionen einzelner MCP-Server

## 3. MCP-Server-Implementierung

### 3.1 Brave Search MCP-Server

**Docker-Image**: `mcp/brave-search`

**Konfiguration**:
```yaml
brave-search-mcp:
  image: mcp/brave-search:latest
  container_name: mcp-brave-search
  restart: always
  environment:
    - MCP_PORT=3001
    - BRAVE_API_KEY=${BRAVE_API_KEY}
  volumes:
    - brave_search_data:/data
  networks:
    - mcp-network
```

**Funktionen**:
- Suche im Web mit der Brave Search API
- Unterstützung für verschiedene Suchfilter und -parameter
- Caching von Suchergebnissen für bessere Performance

### 3.2 Filesystem MCP-Server

**Docker-Image**: `mcp/filesystem`

**Konfiguration**:
```yaml
filesystem-mcp:
  image: mcp/filesystem:latest
  container_name: mcp-filesystem
  restart: always
  environment:
    - MCP_PORT=3002
    - ALLOWED_PATHS=/workspace
  volumes:
    - ${WORKSPACE_PATH:-/workspace}:/workspace:rw
  networks:
    - mcp-network
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  cap_add:
    - CHOWN
    - FOWNER
    - SETGID
    - SETUID
```

**Funktionen**:
- Dateisystem-Operationen (Lesen, Schreiben, Suchen)
- Verzeichnislistung und -navigation
- Dateiinhaltsanalyse

### 3.3 Grafana MCP-Server

**Docker-Image**: `mcp/grafana`

**Konfiguration**:
```yaml
grafana-mcp:
  image: mcp/grafana:latest
  container_name: mcp-grafana
  restart: always
  environment:
    - MCP_PORT=3003
    - GRAFANA_URL=${GRAFANA_URL}
    - GRAFANA_API_KEY=${GRAFANA_API_KEY}
  networks:
    - mcp-network
```

**Funktionen**:
- Abfrage von Grafana-Dashboards und -Panels
- Erstellung und Aktualisierung von Dashboards
- Alarmkonfiguration und -abfrage

### 3.4 Hyperbrowser MCP-Server

**Docker-Image**: `mcp/hyperbrowser`

**Konfiguration**:
```yaml
hyperbrowser-mcp:
  image: mcp/hyperbrowser:latest
  container_name: mcp-hyperbrowser
  restart: always
  environment:
    - MCP_PORT=3004
  volumes:
    - hyperbrowser_data:/data
  networks:
    - mcp-network
```

**Funktionen**:
- Webseiten-Navigation und -Interaktion
- Screenshot-Erstellung
- Datenextraktion aus Webseiten

### 3.5 Wolfram Alpha MCP-Server

**Docker-Image**: `mcp/wolfram-alpha`

**Konfiguration**:
```yaml
wolfram-alpha-mcp:
  image: mcp/wolfram-alpha:latest
  container_name: mcp-wolfram-alpha
  restart: always
  environment:
    - MCP_PORT=3005
    - WOLFRAM_APP_ID=${WOLFRAM_APP_ID}
  networks:
    - mcp-network
```

**Funktionen**:
- Mathematische Berechnungen
- Wissenschaftliche Abfragen
- Datenvisualisierung

### 3.6 Oxylabs MCP-Server

**Docker-Image**: `mcp/oxylabs`

**Konfiguration**:
```yaml
oxylabs-mcp:
  image: mcp/oxylabs:latest
  container_name: mcp-oxylabs
  restart: always
  environment:
    - MCP_PORT=3006
    - OXYLABS_USERNAME=${OXYLABS_USERNAME}
    - OXYLABS_PASSWORD=${OXYLABS_PASSWORD}
  networks:
    - mcp-network
```

**Funktionen**:
- Web-Scraping mit Proxy-Unterstützung
- SERP-Scraping (Search Engine Results Page)
- E-Commerce-Datenextraktion

### 3.7 E2B MCP-Server

**Docker-Image**: `mcp/e2b`

**Konfiguration**:
```yaml
e2b-mcp:
  image: mcp/e2b:latest
  container_name: mcp-e2b
  restart: always
  environment:
    - MCP_PORT=3007
    - E2B_API_KEY=${E2B_API_KEY}
  networks:
    - mcp-network
```

**Funktionen**:
- Code-Ausführung in verschiedenen Umgebungen
- Dateimanipulation
- Terminalzugriff

### 3.8 Desktop Commander MCP-Server

**Docker-Image**: Basierend auf `https://github.com/wonderwhy-er/DesktopCommanderMCP`

**Konfiguration**:
```yaml
desktop-commander-mcp:
  build:
    context: ./desktop-commander
    dockerfile: Dockerfile
  container_name: mcp-desktop-commander
  restart: always
  environment:
    - MCP_PORT=3008
    - ALLOWED_DIRECTORIES=["/workspace"]
    - BLOCKED_COMMANDS=["rm -rf /", "sudo", "su"]
  volumes:
    - ${WORKSPACE_PATH:-/workspace}:/workspace:rw
  networks:
    - mcp-network
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  cap_add:
    - CHOWN
    - FOWNER
    - SETGID
    - SETUID
```

**Funktionen**:
- Dateisystem-Operationen
- Terminalbefehlsausführung
- Prozessverwaltung
- Textbearbeitung

### 3.9 Sequential Thinking MCP-Server

**Docker-Image**: Basierend auf `https://github.com/modelcontextprotocol/servers/blob/2025.4.6/src/sequentialthinking/Dockerfile`

**Konfiguration**:
```yaml
sequential-thinking-mcp:
  build:
    context: ./sequential-thinking
    dockerfile: Dockerfile
  container_name: mcp-sequential-thinking
  restart: always
  environment:
    - MCP_PORT=3009
  networks:
    - mcp-network
```

**Funktionen**:
- Strukturierte Problemlösung
- Schrittweise Analyse
- Logisches Denken

### 3.10 Memory MCP-Server

**Docker-Image**: `mcp/memory`

**Konfiguration**:
```yaml
memory-mcp:
  image: mcp/memory:latest
  container_name: mcp-memory
  restart: always
  environment:
    - MCP_PORT=3010
  volumes:
    - memory_data:/data
  networks:
    - mcp-network
```

**Funktionen**:
- Persistente Speicherung von Informationen
- Abfrage und Aktualisierung von gespeicherten Daten
- Kontextuelle Informationsabfrage

### 3.11 Basic Memory MCP-Server

**Docker-Image**: `mcp/basic-memory`

**Konfiguration**:
```yaml
basic-memory-mcp:
  image: mcp/basic-memory:latest
  container_name: mcp-basic-memory
  restart: always
  environment:
    - MCP_PORT=3011
  volumes:
    - basic_memory_data:/data
  networks:
    - mcp-network
```

**Funktionen**:
- Einfache Speicheroperationen
- Schlüssel-Wert-Speicherung
- Temporäre Datenspeicherung

### 3.12 GitHub MCP-Server

**Docker-Image**: `mcp/github`

**Konfiguration**:
```yaml
github-mcp:
  image: mcp/github:latest
  container_name: mcp-github
  restart: always
  environment:
    - MCP_PORT=3012
    - GITHUB_TOKEN=${GITHUB_TOKEN}
  networks:
    - mcp-network
```

**Funktionen**:
- Repository-Verwaltung
- Issue-Tracking
- Pull-Request-Verwaltung
- Code-Analyse

### 3.13 GitHub Chat MCP-Server

**Docker-Image**: `mcp/github-chat`

**Konfiguration**:
```yaml
github-chat-mcp:
  image: mcp/github-chat:latest
  container_name: mcp-github-chat
  restart: always
  environment:
    - MCP_PORT=3013
    - GITHUB_TOKEN=${GITHUB_TOKEN}
  networks:
    - mcp-network
```

**Funktionen**:
- Diskussionen und Kommentare
- Code-Review-Kommentare
- Issue-Kommentare

### 3.14 GitLab MCP-Server

**Docker-Image**: `mcp/gitlab`

**Konfiguration**:
```yaml
gitlab-mcp:
  image: mcp/gitlab:latest
  container_name: mcp-gitlab
  restart: always
  environment:
    - MCP_PORT=3014
    - GITLAB_TOKEN=${GITLAB_TOKEN}
    - GITLAB_URL=${GITLAB_URL}
  networks:
    - mcp-network
```

**Funktionen**:
- Repository-Verwaltung
- Issue-Tracking
- Merge-Request-Verwaltung
- CI/CD-Pipeline-Verwaltung

### 3.15 DuckDuckGo MCP-Server

**Docker-Image**: `mcp/duckduckgo`

**Konfiguration**:
```yaml
duckduckgo-mcp:
  image: mcp/duckduckgo:latest
  container_name: mcp-duckduckgo
  restart: always
  environment:
    - MCP_PORT=3015
  networks:
    - mcp-network
```

**Funktionen**:
- Websuche mit DuckDuckGo
- Instant Answers
- Bildersuche

### 3.16 Wikipedia MCP-Server

**Docker-Image**: `mcp/wikipedia-mcp`

**Konfiguration**:
```yaml
wikipedia-mcp:
  image: mcp/wikipedia-mcp:latest
  container_name: mcp-wikipedia
  restart: always
  environment:
    - MCP_PORT=3016
  networks:
    - mcp-network
```

**Funktionen**:
- Artikel-Suche und -Abfrage
- Zusammenfassungen
- Kategorien und Themen

## 4. n8n-Workflow-Verbesserungen

### 4.1 MCP-Trigger-Workflow

Der bestehende MCP-Trigger-Workflow wird verbessert, um Ereignisse von allen MCP-Servern zu empfangen und zu verarbeiten.

**Verbesserungen**:
- Unterstützung für mehrere MCP-Server-Quellen
- Dynamische Konfiguration der MCP-Server-URLs und API-Keys
- Verbesserte Fehlerbehandlung und Wiederholungslogik
- Normalisierung der Ereignisdaten für konsistente Weiterverarbeitung

**Implementierung**:
```javascript
// Beispiel für verbesserten MCP-Trigger-Node
{
  "parameters": {
    "pollTimes": {
      "item": [
        {
          "mode": "everyX",
          "value": 1,
          "unit": "minutes"
        }
      ]
    },
    "mcpServers": "={{ $env.MCP_SERVERS }}",
    "options": {
      "response": {
        "response": {
          "fullResponse": true,
          "responseFormat": "json"
        }
      }
    }
  },
  "type": "n8n-nodes-base.mcpTrigger",
  "typeVersion": 2,
  "position": [240, 300],
  "id": "mcp-events-poller"
}
```

### 4.2 MCP-Integration-Workflow

Der bestehende MCP-Integration-Workflow wird verbessert, um die Funktionen aller MCP-Server zu nutzen und mit anderen Systemen zu integrieren.

**Verbesserungen**:
- Unterstützung für alle implementierten MCP-Server
- Dynamische Routing-Logik basierend auf dem Tool-Namen
- Verbesserte Fehlerbehandlung und Wiederholungslogik
- Erweiterte Datenvalidierung und -transformation

**Implementierung**:
```javascript
// Beispiel für verbesserten MCP-Integration-Node
{
  "parameters": {
    "httpMethod": "POST",
    "path": "mcp-endpoint",
    "options": {
      "responseMode": "responseNode"
    }
  },
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1,
  "position": [240, 300],
  "id": "mcp-endpoint-webhook"
}
```

### 4.3 Tool-spezifische Workflows

Für jeden MCP-Server werden spezifische Workflows erstellt, die dessen Funktionen optimal nutzen.

**Beispiel für Brave-Search-Workflow**:
```javascript
{
  "name": "Brave Search Integration",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "brave-search",
        "options": {}
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300],
      "id": "brave-search-webhook"
    },
    {
      "parameters": {
        "url": "http://brave-search-mcp:3001/mcp",
        "method": "POST",
        "jsonParameters": true,
        "bodyParametersJson": "={\n  \"jsonrpc\": \"2.0\",\n  \"id\": 1,\n  \"method\": \"mcp.callTool\",\n  \"params\": {\n    \"name\": \"search\",\n    \"arguments\": {\n      \"query\": $json.query,\n      \"count\": $json.count || 10\n    }\n  }\n}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [460, 300],
      "id": "brave-search-request"
    },
    {
      "parameters": {
        "mode": "jsonToJson",
        "jsonInput": "={{ $json.result }}",
        "options": {}
      },
      "type": "n8n-nodes-base.itemLists",
      "typeVersion": 1,
      "position": [680, 300],
      "id": "process-search-results"
    }
  ],
  "connections": {
    "brave-search-webhook": {
      "main": [
        [
          {
            "node": "brave-search-request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "brave-search-request": {
      "main": [
        [
          {
            "node": "process-search-results",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## 5. Integration und Konnektivität

### 5.1 OpenHands-Integration

Die Integration mit OpenHands wird verbessert, um alle MCP-Server nahtlos zu nutzen.

**Konfiguration**:
```json
{
  "mcp": {
    "servers": [
      {
        "name": "brave-search",
        "url": "http://brave-search-mcp:3001",
        "description": "Web-Suche mit Brave Search"
      },
      {
        "name": "filesystem",
        "url": "http://filesystem-mcp:3002",
        "description": "Dateisystem-Operationen"
      },
      {
        "name": "grafana",
        "url": "http://grafana-mcp:3003",
        "description": "Grafana-Dashboard-Verwaltung"
      },
      // Weitere MCP-Server...
    ]
  }
}
```

### 5.2 n8n-Integration

Die Integration mit n8n wird verbessert, um alle MCP-Server nahtlos zu nutzen.

**Konfiguration**:
```javascript
// n8n-Umgebungsvariablen
{
  "MCP_SERVERS": [
    {
      "name": "brave-search",
      "url": "http://brave-search-mcp:3001",
      "apiKey": "{{ $env.BRAVE_API_KEY }}"
    },
    {
      "name": "filesystem",
      "url": "http://filesystem-mcp:3002"
    },
    {
      "name": "grafana",
      "url": "http://grafana-mcp:3003",
      "apiKey": "{{ $env.GRAFANA_API_KEY }}"
    },
    // Weitere MCP-Server...
  ]
}
```

### 5.3 MCP-Server-Kommunikation

Die Kommunikation zwischen den MCP-Servern wird über das Docker-Netzwerk ermöglicht.

**Konfiguration**:
```yaml
networks:
  mcp-network:
    driver: bridge
```

## 6. Sicherheit und Berechtigungen

### 6.1 Container-Sicherheit

Alle Container werden nach dem Least-Privilege-Prinzip konfiguriert.

**Maßnahmen**:
- Verwendung von `no-new-privileges:true`
- Entfernen aller Capabilities mit `cap_drop: [ALL]`
- Hinzufügen nur der notwendigen Capabilities
- Beschränkung der Dateisystemzugriffe
- Verwendung von Read-Only-Volumes wo möglich

### 6.2 API-Schlüssel-Verwaltung

API-Schlüssel werden sicher verwaltet und nicht im Klartext gespeichert.

**Maßnahmen**:
- Verwendung von Umgebungsvariablen für API-Schlüssel
- Speicherung sensibler Daten in einer `.env`-Datei
- Verwendung von Docker Secrets für Produktionsumgebungen

### 6.3 Netzwerksicherheit

Die Netzwerkkommunikation wird abgesichert.

**Maßnahmen**:
- Verwendung eines isolierten Docker-Netzwerks
- Exposition nur der notwendigen Ports
- Verwendung von HTTPS für externe Kommunikation

## 7. Monitoring und Logging

### 7.1 Container-Monitoring

Alle Container werden überwacht, um Probleme frühzeitig zu erkennen.

**Implementierung**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:${MCP_PORT}/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 7.2 Logging

Alle Container schreiben Logs in ein einheitliches Format.

**Implementierung**:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 7.3 Metriken

Wichtige Metriken werden gesammelt und visualisiert.

**Implementierung**:
- Verwendung von Prometheus für Metrik-Sammlung
- Verwendung von Grafana für Metrik-Visualisierung
- Sammlung von Container-Metriken, MCP-Server-Metriken und n8n-Workflow-Metriken

## 8. Dokumentation

### 8.1 Benutzerhandbuch

Ein umfassendes Benutzerhandbuch wird erstellt, das die Verwendung des MCP-Server-Ökosystems beschreibt.

**Inhalte**:
- Installation und Konfiguration
- Verwendung der MCP-Server
- Integration mit OpenHands und n8n
- Fehlerbehebung

### 8.2 Entwicklerhandbuch

Ein Entwicklerhandbuch wird erstellt, das die Erweiterung des MCP-Server-Ökosystems beschreibt.

**Inhalte**:
- Architektur und Design
- Hinzufügen neuer MCP-Server
- Anpassung bestehender MCP-Server
- Entwicklung neuer n8n-Workflows

### 8.3 API-Dokumentation

Eine API-Dokumentation wird erstellt, die die Schnittstellen der MCP-Server beschreibt.

**Inhalte**:
- Verfügbare Methoden und Parameter
- Beispielanfragen und -antworten
- Fehlerbehandlung
- Authentifizierung und Autorisierung

## 9. Testplan

### 9.1 Komponententests

Jeder MCP-Server wird einzeln getestet.

**Tests**:
- Funktionalitätstests für alle Tools
- Fehlerbehandlungstests
- Performance-Tests
- Sicherheitstests

### 9.2 Integrationstests

Die Integration zwischen den Komponenten wird getestet.

**Tests**:
- OpenHands-MCP-Server-Integration
- n8n-MCP-Server-Integration
- MCP-Server-MCP-Server-Integration

### 9.3 End-to-End-Tests

Das gesamte System wird end-to-end getestet.

**Tests**:
- Vollständige Workflow-Tests
- Benutzerinteraktionstests
- Fehlerszenarien

## 10. Rollout-Strategie

### 10.1 Phasen

Der Rollout erfolgt in mehreren Phasen.

**Phase 1: Grundlegende MCP-Server**
- Brave Search
- Filesystem
- GitHub
- Memory
- Desktop Commander

**Phase 2: Erweiterte MCP-Server**
- Grafana
- Wolfram Alpha
- GitLab
- Wikipedia
- DuckDuckGo

**Phase 3: Spezialisierte MCP-Server**
- Hyperbrowser
- Oxylabs
- E2B
- Sequential Thinking
- GitHub Chat

### 10.2 Zeitplan

Der Rollout erfolgt nach folgendem Zeitplan:

- **Woche 1-2**: Implementierung der Phase-1-Server
- **Woche 3-4**: Implementierung der Phase-2-Server
- **Woche 5-6**: Implementierung der Phase-3-Server
- **Woche 7-8**: Integration und Tests
- **Woche 9-10**: Dokumentation und Finalisierung

## 11. Wartung und Support

### 11.1 Updates

Regelmäßige Updates der MCP-Server und n8n-Workflows werden durchgeführt.

**Prozess**:
- Wöchentliche Überprüfung auf neue Versionen
- Monatliche Updates der Container-Images
- Quartalsmäßige Überprüfung der Gesamtarchitektur

### 11.2 Support

Ein Support-System wird eingerichtet, um Probleme zu beheben.

**Kanäle**:
- GitHub Issues für technische Probleme
- Dokumentation für häufige Fragen
- E-Mail-Support für dringende Probleme

### 11.3 Erweiterungen

Das System wird kontinuierlich erweitert und verbessert.

**Prozess**:
- Sammlung von Feedback und Anforderungen
- Priorisierung von Erweiterungen
- Implementierung und Tests
- Dokumentation und Rollout