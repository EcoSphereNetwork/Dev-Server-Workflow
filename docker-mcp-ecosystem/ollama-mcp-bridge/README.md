# Ollama MCP Bridge

Diese Komponente verbindet lokale Large Language Models (LLMs) über Ollama mit dem Model Context Protocol (MCP). Die Bridge ermöglicht es Open-Source-Modellen, die gleichen Tools und Funktionen wie kommerzielle Modelle zu nutzen.

## Übersicht

Die Ollama-MCP-Bridge stellt eine Verbindung zwischen lokalen LLMs und MCP-Servern her, die verschiedene Funktionen bereitstellen:

- Dateisystemoperationen
- Websuche
- GitHub-Interaktionen
- Speicherfunktionen
- Und mehr

Die Bridge übersetzt zwischen den Ausgaben des LLMs und dem JSON-RPC-Protokoll des MCP, sodass jedes Ollama-kompatible Modell diese Tools nutzen kann.

## Aktuelle Konfiguration

- **LLM**: Qwen 2.5 7B (qwen2.5-coder:7b-instruct) über Ollama
- **MCP-Server**:
  - Filesystem MCP (`filesystem-mcp:3001`)
  - Desktop Commander MCP (`desktop-commander-mcp:3002`)
  - Sequential Thinking MCP (`sequential-thinking-mcp:3003`)
  - GitHub Chat MCP (`github-chat-mcp:3004`)
  - GitHub MCP (`github-mcp:3005`)
  - Puppeteer MCP (`puppeteer-mcp:3006`)
  - Basic Memory MCP (`basic-memory-mcp:3007`)
  - Wikipedia MCP (`wikipedia-mcp:3008`)

## Architektur

- **Bridge**: Kernkomponente, die die Werkzeugregistrierung und -ausführung verwaltet
- **LLM-Client**: Verarbeitet Ollama-Interaktionen und formatiert Werkzeugaufrufe
- **MCP-Client**: Verwaltet MCP-Server-Verbindungen und JSON-RPC-Kommunikation
- **Tool-Router**: Leitet Anfragen an den entsprechenden MCP-Server weiter

### Hauptfunktionen
- Unterstützung mehrerer MCP-Server mit dynamischem Routing
- Strukturierte Ausgabevalidierung für Werkzeugaufrufe
- Automatische Werkzeugerkennung aus Benutzeranfragen
- Robuste Prozessverwaltung für Ollama
- Detaillierte Protokollierung und Fehlerbehandlung

## Einrichtung

1. Starten Sie die Ollama-MCP-Bridge mit Docker Compose:
```bash
./start-ollama-bridge.sh
```

2. Das Skript führt folgende Schritte aus:
   - Erstellt eine .env-Datei, wenn sie nicht existiert
   - Startet die Docker-Container für Ollama und die MCP-Bridge
   - Lädt das konfigurierte Modell herunter, wenn es noch nicht vorhanden ist

3. Konfigurieren Sie die Zugangsdaten in der .env-Datei:
   - `GITHUB_TOKEN` für GitHub-Interaktionen
   - `BRAVE_API_KEY` für die Brave-Suche (optional)

## Konfiguration

Die Bridge wird über die Datei `bridge_config.json` konfiguriert:
- MCP-Server-Definitionen
- LLM-Einstellungen (Modell, Temperatur, etc.)
- Werkzeugberechtigungen und -pfade

Beispiel:
```json
{
  "mcpServers": {
    "filesystem": {
      "url": "http://filesystem-mcp:3001"
    },
    "github": {
      "url": "http://github-mcp:3005"
    },
    "memory": {
      "url": "http://basic-memory-mcp:3007"
    }
  },
  "llm": {
    "model": "qwen2.5-coder:7b-instruct",
    "baseUrl": "http://ollama:11434",
    "temperature": 0.7,
    "maxTokens": 4096
  }
}
```

## Verwendung

1. Testen Sie die Bridge mit dem Testskript:
```bash
./test-ollama-bridge.sh
```

2. Senden Sie Anfragen an den Chat-Endpunkt:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Erstelle eine Datei mit dem Namen test.txt im Verzeichnis /workspace"}'
```

3. Verwenden Sie die Bridge in Ihren Anwendungen:
   - MCP-Endpunkt: `http://localhost:8000/mcp`
   - Chat-Endpunkt: `http://localhost:8000/chat`
   - Gesundheitscheck: `http://localhost:8000/health`

Beispielinteraktionen:
```
> Suche im Web nach "neueste TypeScript-Funktionen"
[Verwendet den Brave Search MCP für die Suche]

> Erstelle einen neuen Ordner namens "projekt-docs"
[Verwendet den Filesystem MCP zum Erstellen des Verzeichnisses]

> Öffne die Webseite github.com
[Verwendet den Puppeteer MCP zum Öffnen der Webseite]
```

## Technische Details

### Werkzeugerkennung
Die Bridge enthält eine intelligente Werkzeugerkennung basierend auf der Benutzereingabe:
- Dateisystemoperationen: Erkannt durch Datei- und Verzeichnispfade
- Suchoperationen: Kontextuell an den entsprechenden Suchdienst weitergeleitet
- GitHub-Operationen: Erkannt durch Repository- und Issue-Referenzen

### Antwortverarbeitung
Antworten werden in mehreren Stufen verarbeitet:
1. Das LLM generiert strukturierte Werkzeugaufrufe
2. Die Bridge validiert und leitet an den entsprechenden MCP-Server weiter
3. Der MCP-Server führt die Operation aus und gibt das Ergebnis zurück
4. Die Bridge formatiert die Antwort für den Benutzer

## Erweiterte Funktionen

Diese Bridge bringt die Werkzeugfähigkeiten kommerzieller Modelle zu lokalen Open-Source-Modellen:
- Dateisystemmanipulation
- Websuche und -recherche
- Code- und GitHub-Interaktionen
- Browser-Automatisierung
- Persistenter Speicher
- Strukturiertes Denken

Alles läuft vollständig lokal mit Open-Source-Modellen.

## Zukünftige Verbesserungen

- Unterstützung für weitere MCP-Server
- Implementierung paralleler Werkzeugausführung
- Hinzufügen von Streaming-Antworten
- Verbesserte Fehlerbehandlung
- Hinzufügen von Konversationsgedächtnis
- Unterstützung weiterer Ollama-Modelle

## Verwandte Projekte

Diese Bridge integriert sich in das breitere MCP-Ökosystem:
- Model Context Protocol (MCP)
- OpenHands-Integration
- Ollama-Projekt
- Verschiedene MCP-Server-Implementierungen

Das Ergebnis ist ein leistungsstarker lokaler KI-Assistent, der viele Funktionen kommerzieller Modelle bietet, während er vollständig auf Ihrer eigenen Hardware läuft.
