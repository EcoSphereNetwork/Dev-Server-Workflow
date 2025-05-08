# MCP-Server Implementierung

Diese Dokumentation beschreibt die Implementierung des Model Context Protocol (MCP) Server-Ökosystems, das KI-Agenten wie OpenHands ermöglicht, mit verschiedenen Systemen zu interagieren.

## Was ist das Model Context Protocol (MCP)?

Das Model Context Protocol ist ein standardisiertes Protokoll, das es KI-Agenten ermöglicht, mit externen Tools und Diensten zu interagieren. Es definiert:

- Wie Tools entdeckt werden können
- Wie Tools aufgerufen werden können
- Wie Ergebnisse zurückgegeben werden

MCP verwendet JSON-RPC 2.0 als Kommunikationsprotokoll und ermöglicht es KI-Agenten, Tools dynamisch zu entdecken und zu nutzen.

## MCP-Server-Ökosystem

Das MCP-Server-Ökosystem besteht aus mehreren spezialisierten MCP-Servern, die jeweils unterschiedliche Funktionen bereitstellen:

![MCP-Server Architektur](/img/mcp-architecture.png)

### Implementierte MCP-Server

1. **Filesystem MCP**: Dateisystem-Operationen (Lesen, Schreiben, Suchen)
2. **Desktop Commander MCP**: Terminal-Befehle und Desktop-Operationen
3. **Sequential Thinking MCP**: Strukturierte Problemlösung
4. **GitHub Chat MCP**: Interaktion mit GitHub-Diskussionen
5. **GitHub MCP**: GitHub-Repository-Management
6. **Puppeteer MCP**: Web-Browsing und Interaktion mit Webseiten
7. **Basic Memory MCP**: Einfache Schlüssel-Wert-Speicherung
8. **Wikipedia MCP**: Suche und Abrufen von Informationen aus Wikipedia
9. **n8n MCP**: Integration mit n8n-Workflows

## Architektur und Funktionsweise

### Docker-basierte Implementierung

Alle MCP-Server sind als Docker-Container implementiert, was folgende Vorteile bietet:

- **Isolation**: Jeder MCP-Server läuft in seiner eigenen Umgebung
- **Skalierbarkeit**: Server können unabhängig voneinander skaliert werden
- **Portabilität**: Einfache Bereitstellung in verschiedenen Umgebungen
- **Ressourcenbeschränkungen**: Kontrolle über CPU- und Speichernutzung

Die Container kommunizieren über ein gemeinsames Docker-Netzwerk und verwenden Redis für Caching und Kommunikation.

### MCP-Protokoll-Implementierung

Jeder MCP-Server implementiert das JSON-RPC 2.0-basierte Model Context Protocol mit folgenden Endpunkten:

- **/health**: Gesundheitsstatus des Servers (HTTP GET)
- **/mcp**: Hauptendpunkt für MCP-Anfragen (HTTP POST)

Die wichtigsten MCP-Methoden sind:

- **mcp.listTools**: Gibt eine Liste der verfügbaren Tools zurück
- **mcp.callTool**: Ruft ein Tool mit den angegebenen Argumenten auf

### Beispiel für eine MCP-Anfrage

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "mcp.listTools",
  "params": {}
}
```

### Beispiel für eine MCP-Antwort

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "name": "read_file",
      "description": "Read the content of a file",
      "parameter_schema": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "Path to the file"
          }
        },
        "required": ["path"]
      }
    }
  ]
}
```

### n8n MCP-Server

Der n8n MCP-Server (`n8n_mcp_server.py`) ist eine spezielle Implementierung, die n8n-Workflows als MCP-Tools verfügbar macht:

- **Dynamische Tool-Erkennung**: Erkennt automatisch n8n-Workflows mit dem Tag "mcp"
- **Workflow-Ausführung**: Führt n8n-Workflows über die n8n-API aus
- **Ergebnisverarbeitung**: Konvertiert n8n-Workflow-Ergebnisse in MCP-Antworten

### OpenHands-Integration

Die Integration mit OpenHands erfolgt über eine JSON-Konfigurationsdatei (`openhands-mcp-config.json`), die:

- Die URLs der MCP-Server definiert
- Die Authentifizierungsmethoden festlegt
- Optionale Konfigurationsparameter enthält

Beispiel für eine OpenHands-MCP-Konfiguration:

```json
{
  "mcp": {
    "servers": [
      {
        "name": "filesystem-mcp",
        "url": "http://localhost:3001",
        "description": "File system operations"
      },
      {
        "name": "github-mcp",
        "url": "http://localhost:3005",
        "description": "GitHub repository management"
      }
    ]
  }
}
```

## Bereitstellung der MCP-Server

### Docker Compose (empfohlen)

Die einfachste Methode zur Bereitstellung der MCP-Server ist die Verwendung von Docker Compose:

```bash
cd docker-mcp-servers
./start-mcp-servers.sh
```

Dies startet alle MCP-Server mit den richtigen Konfigurationen und Netzwerkeinstellungen.

### Kubernetes-Bereitstellung

Für Produktionsumgebungen bieten wir auch Kubernetes-Manifeste:

```bash
cd kubernetes
./deploy-mcp-servers.sh
```

Weitere Informationen finden Sie in der [Kubernetes-Dokumentation](MCP-Server-Kubernetes.md).

### Manuelle Bereitstellung

Für fortgeschrittene Benutzer oder Entwicklungszwecke können die MCP-Server auch manuell gestartet werden:

```bash
# n8n MCP-Server starten
python src/n8n_mcp_server.py --port 3000 --host 0.0.0.0
```

## Überwachung und Wartung

### Gesundheitsüberwachung

Alle MCP-Server bieten einen `/health`-Endpunkt zur Überwachung:

```bash
curl http://localhost:3001/health
```

### Umfassende Überwachung mit Prometheus und Grafana

Wir bieten eine vollständige Überwachungslösung mit Prometheus und Grafana:

```bash
cd docker-mcp-servers/monitoring
./start-monitoring.sh
```

Weitere Informationen finden Sie in der [Monitoring-Dokumentation](MCP-Server-Monitoring.md).

### Logging

Alle MCP-Server schreiben Logs in standardisiertem Format. In der Docker-Umgebung können die Logs wie folgt angezeigt werden:

```bash
docker-compose logs filesystem-mcp
```

## Testen der MCP-Server

Zum Testen der MCP-Server können Sie das mitgelieferte Test-Skript verwenden:

```bash
cd docker-mcp-servers
./test-mcp-servers.py
```

Das Skript führt folgende Aktionen aus:
- Überprüft die Erreichbarkeit aller MCP-Server
- Ruft die verfügbaren Tools von jedem Server ab
- Führt Beispiel-Tool-Aufrufe durch
- Generiert einen Testbericht

## Erweitern des MCP-Ökosystems

### Hinzufügen neuer Tools zu bestehenden MCP-Servern

Um neue Tools zu einem bestehenden MCP-Server hinzuzufügen:

1. **Für n8n MCP-Server**:
   - Erstellen Sie einen neuen n8n-Workflow
   - Fügen Sie das Tag "mcp" zum Workflow hinzu
   - Stellen Sie sicher, dass der Workflow Eingabeparameter akzeptiert und Ergebnisse zurückgibt

2. **Für andere MCP-Server**:
   - Erweitern Sie die entsprechende Server-Implementierung
   - Registrieren Sie das neue Tool in der Tool-Registry
   - Implementieren Sie die Tool-Logik

### Implementieren eines neuen MCP-Servers

Um einen völlig neuen MCP-Server zu implementieren:

1. Erstellen Sie eine neue Docker-Container-Definition
2. Implementieren Sie die MCP-Protokoll-Endpunkte
3. Definieren Sie die Tools und ihre Parameter
4. Fügen Sie den Server zur Docker-Compose-Konfiguration hinzu

## Fehlerbehebung

### Allgemeine Probleme

| Problem | Mögliche Ursachen | Lösungen |
|---------|-------------------|----------|
| MCP-Server startet nicht | - Docker-Dienst läuft nicht<br>- Port bereits belegt<br>- Redis nicht erreichbar | - Docker-Dienst starten<br>- Port-Konfiguration ändern<br>- Redis-Verbindung überprüfen |
| Tool-Ausführung schlägt fehl | - Fehlende Berechtigungen<br>- Ungültige Parameter<br>- Interner Serverfehler | - Berechtigungen überprüfen<br>- Parameter validieren<br>- Server-Logs analysieren |
| Verbindungsprobleme | - Netzwerkkonfiguration<br>- Firewall-Einstellungen<br>- DNS-Probleme | - Netzwerkkonfiguration prüfen<br>- Firewall-Regeln anpassen<br>- DNS-Einstellungen überprüfen |

### Spezifische Fehlermeldungen

- **"Connection refused"**: Der MCP-Server ist nicht erreichbar oder läuft nicht
- **"Method not found"**: Die angeforderte MCP-Methode wird nicht unterstützt
- **"Tool not found"**: Das angeforderte Tool existiert nicht oder ist nicht registriert
- **"Invalid parameters"**: Die übergebenen Parameter entsprechen nicht dem erwarteten Schema

## Sicherheitshinweise

- **Netzwerkisolation**: Betreiben Sie die MCP-Server in einem isolierten Netzwerk
- **Zugriffssteuerung**: Beschränken Sie den Zugriff auf die MCP-Server auf vertrauenswürdige Clients
- **Ressourcenbeschränkungen**: Verwenden Sie die Docker-Ressourcenbeschränkungen, um DoS-Angriffe zu verhindern
- **Regelmäßige Updates**: Halten Sie alle Container und Abhängigkeiten aktuell
- **Logging und Überwachung**: Überwachen Sie die MCP-Server auf verdächtige Aktivitäten

## Weitere Ressourcen

- [MCP-Server-Tools-Referenz](MCP-SERVERS.md)
- [Kubernetes-Deployment](MCP-Server-Kubernetes.md)
- [Monitoring-Lösung](MCP-Server-Monitoring.md)
- [OpenHands-Integration](MCP-OpenHands.md)
- [GitHub-Integration](GitHub-Integration.md)