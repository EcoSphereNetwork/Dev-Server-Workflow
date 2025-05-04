# MCP-Server Implementierung für n8n

Diese Dokumentation beschreibt die Implementierung des Model Context Protocol (MCP) Servers für n8n, der es KI-Agenten ermöglicht, n8n-Workflows als Tools zu verwenden.

## Übersicht

Der MCP-Server fungiert als Brücke zwischen KI-Agenten (wie OpenHands) und n8n-Workflows. Er implementiert das standardisierte Model Context Protocol, das es KI-Agenten ermöglicht, verfügbare Tools zu entdecken und aufzurufen.

![MCP-Server Architektur](https://via.placeholder.com/800x400?text=MCP-Server-Architektur)

## Komponenten

Die Implementierung besteht aus folgenden Hauptkomponenten:

1. **n8n-mcp-server.py**: Der MCP-Server, der das Model Context Protocol implementiert
2. **n8n-setup-workflows-mcp.py**: Die Definition des n8n-Workflows für MCP-Integration
3. **openhands-mcp-config.json**: Die Konfigurationsdatei für OpenHands

## Funktionsweise

### MCP-Server (n8n-mcp-server.py)

Der MCP-Server implementiert das JSON-RPC-basierte Model Context Protocol und bietet folgende Funktionen:

- **Initialisierung**: Stellt eine Verbindung zur n8n-API her und lädt verfügbare Workflows
- **Tool-Auflistung**: Konvertiert n8n-Workflows in MCP-Tools und stellt sie KI-Agenten zur Verfügung
- **Tool-Ausführung**: Führt n8n-Workflows aus, wenn ein Tool aufgerufen wird
- **Fehlerbehandlung**: Bietet Fallback-Mechanismen, wenn die n8n-API nicht erreichbar ist

Der Server unterstützt standardmäßig drei vordefinierte Tools:

1. `create_github_issue`: Erstellt ein Issue in GitHub
2. `update_work_package`: Aktualisiert ein Arbeitspaket in OpenProject
3. `sync_documentation`: Synchronisiert Dokumentation zwischen AFFiNE und GitHub

Zusätzlich werden alle n8n-Workflows mit dem Tag "mcp" automatisch als Tools verfügbar gemacht.

### MCP-Workflow (n8n-setup-workflows-mcp.py)

Der n8n-Workflow für MCP-Integration:

- Stellt einen Webhook-Endpunkt unter `/mcp/endpoint` bereit
- Verarbeitet eingehende MCP-Anfragen
- Leitet Anfragen basierend auf dem Tool-Namen an die entsprechenden Nodes weiter
- Führt die angeforderte Aktion aus (z.B. GitHub Issue erstellen)
- Sendet das Ergebnis zurück an den MCP-Client

### OpenHands-Konfiguration (openhands-mcp-config.json)

Die Konfigurationsdatei für OpenHands definiert:

- Den Befehl zum Starten des MCP-Servers
- Umgebungsvariablen für die n8n-Verbindung
- Eine Liste von Tools, die automatisch genehmigt werden sollen

## Installation und Konfiguration

### Voraussetzungen

- Python 3.7+
- n8n-Instanz mit API-Zugriff
- OpenHands (optional)

### Installation

1. Führen Sie das Setup-Skript aus:

```bash
python n8n_setup_main.py --install --env-file .env --mcp
```

2. Das Skript wird:
   - Den MCP-Server installieren
   - Den MCP-Workflow in n8n erstellen
   - Eine OpenHands-Konfigurationsdatei generieren

3. Für systemweite Installation (optional):

```bash
sudo cp /tmp/n8n-mcp-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable n8n-mcp-server
sudo systemctl start n8n-mcp-server
```

### Konfiguration in OpenHands

1. Kopieren Sie die generierte `openhands-mcp-config.json` in Ihr OpenHands-Konfigurationsverzeichnis
2. Starten Sie OpenHands neu, um die MCP-Integration zu aktivieren
3. Die n8n-Workflows stehen nun als Tools in OpenHands zur Verfügung

## Testen

Zum Testen des MCP-Servers können Sie das mitgelieferte Test-Skript verwenden:

```bash
python test-mcp-server.py
```

Das Skript wird:
- Den MCP-Server starten
- Eine Initialisierungsanfrage senden
- Die verfügbaren Tools auflisten
- Ein Beispiel-Tool ausführen

## Erweitern der Funktionalität

### Hinzufügen neuer Tools

Um neue Tools hinzuzufügen:

1. Erstellen Sie einen neuen n8n-Workflow
2. Fügen Sie das Tag "mcp" zum Workflow hinzu
3. Stellen Sie sicher, dass der Workflow Eingabeparameter akzeptiert und Ergebnisse zurückgibt
4. Der MCP-Server wird das neue Tool automatisch erkennen und verfügbar machen

### Anpassen der Tool-Parameter

Die Parameter-Schemata für Tools können angepasst werden, indem Sie die `_extract_parameters_from_workflow`-Methode im MCP-Server erweitern.

## Fehlerbehebung

### MCP-Server startet nicht

- Überprüfen Sie, ob die n8n-URL und der API-Key korrekt sind
- Stellen Sie sicher, dass die n8n-Instanz läuft und erreichbar ist
- Überprüfen Sie die Berechtigungen der MCP-Server-Datei

### Tools werden nicht angezeigt

- Stellen Sie sicher, dass Ihre Workflows das Tag "mcp" haben
- Überprüfen Sie, ob die Workflows aktiviert sind
- Prüfen Sie die Logs des MCP-Servers auf Fehler

### Tool-Ausführung schlägt fehl

- Überprüfen Sie, ob der Workflow korrekt konfiguriert ist
- Stellen Sie sicher, dass alle erforderlichen Credentials in n8n eingerichtet sind
- Prüfen Sie die n8n-Logs auf Fehler bei der Workflow-Ausführung

## Sicherheitshinweise

- Der MCP-Server sollte nur in vertrauenswürdigen Umgebungen ausgeführt werden
- Verwenden Sie einen dedizierten n8n-API-Key mit eingeschränkten Berechtigungen
- Aktivieren Sie die automatische Genehmigung nur für vertrauenswürdige Tools