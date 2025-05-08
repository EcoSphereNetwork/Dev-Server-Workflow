# Prompt MCP Server Architektur

Der Prompt MCP Server ist ein Master Control Program (MCP) Server für Prompt Engineering mit Templates, Memory und Pre-Prompts. Er verbessert Benutzer-Eingaben automatisch zu strukturierten Best-Practice-Prompts.

## Systemarchitektur

Der Prompt MCP Server besteht aus folgenden Komponenten:

1. **API-Server**: FastAPI-Server, der REST-API-Endpunkte bereitstellt
2. **Template-Manager**: Verwaltet Prompt-Templates und deren Rendering
3. **Memory-Manager**: Verwaltet Konversationsverlauf und Kontext
4. **Prompt-Optimierer**: Verbessert Benutzer-Prompts zu strukturierten Best-Practice-Prompts

```
┌─────────────────────────────────────────────────────────────────┐
│                      Prompt MCP Server                           │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  API-Server  │◄───┤ Config      │    │ Template-Manager    │  │
│  └─────┬───────┘    └─────────────┘    └──────────┬──────────┘  │
│        │                                          │             │
│        ▼                                          ▼             │
│  ┌─────────────┐                         ┌─────────────────────┐│
│  │ Router      │                         │ Templates           ││
│  └─────┬───────┘                         └─────────────────────┘│
│        │                                                        │
│        ▼                                                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Endpunkte   │◄───┤ Modelle     │    │ Memory-Manager      │  │
│  └─────┬───────┘    └─────────────┘    └──────────┬──────────┘  │
│        │                                          │             │
│        ▼                                          ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Chat        │◄───┤ Prompt-     │    │ Storage-Backend     │  │
│  │             │    │ Optimierer  │    │ (Redis/Chroma/Memory)  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Komponentendetails

### API-Server

Der API-Server ist mit FastAPI gebaut und stellt folgende Endpunkte bereit:

- `/api/v1/chat`: Chat-Endpunkte zum Senden von Nachrichten und Verwalten von Sitzungen
- `/api/v1/models`: Modell-Endpunkte zum Auflisten von Modellen
- `/api/v1/templates`: Template-Endpunkte zum Verwalten von Templates
- `/api/v1/optimize`: Optimierungs-Endpunkte zum Verbessern von Prompts

### Template-Manager

Der Template-Manager ist verantwortlich für:

- Laden von Templates aus dem Templates-Verzeichnis
- Rendern von Templates mit Kontext
- Verwalten von Template-CRUD-Operationen

Templates werden als Jinja2-Templates im Templates-Verzeichnis gespeichert und können verwendet werden, um Prompts für verschiedene LLMs zu formatieren.

### Memory-Manager

Der Memory-Manager ist verantwortlich für:

- Verwalten des Konversationsverlaufs
- Speichern und Abrufen von Chat-Sitzungen
- Unterstützung verschiedener Storage-Backends (in-memory, Redis, Chroma)

### Prompt-Optimierer

Der Prompt-Optimierer ist verantwortlich für:

- Analyse der Struktur von Benutzer-Prompts
- Optimierung von Benutzer-Prompts zu strukturierten Best-Practice-Prompts
- Generierung von System-Prompts basierend auf Benutzer-Prompts und Parametern

## Datenfluss

1. Ein Benutzer sendet eine Nachricht an den `/api/v1/chat`-Endpunkt
2. Der API-Server empfängt die Nachricht und leitet sie an den Chat-Endpunkt-Handler weiter
3. Der Chat-Endpunkt-Handler:
   - Holt oder erstellt eine Sitzung mit dem Memory-Manager
   - Fügt die Benutzernachricht zur Sitzung hinzu
   - Optimiert den Prompt mit dem Prompt-Optimierer
   - Generiert eine Antwort mit dem optimierten Prompt
   - Fügt die Assistentennachricht zur Sitzung hinzu
   - Gibt die Antwort an den Benutzer zurück

## Bereitstellung

Der Prompt MCP Server kann mit Docker und Docker Compose bereitgestellt werden:

```bash
# Baue und starte den Server
docker-compose up -d

# Stoppe den Server
docker-compose down
```

## Konfiguration

Der Prompt MCP Server kann über Umgebungsvariablen oder eine `.env`-Datei konfiguriert werden:

```
# API-Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Server-Konfiguration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Memory-Konfiguration
MEMORY_TYPE=in_memory  # in_memory, redis, chroma
REDIS_URL=redis://localhost:6379/0
CHROMA_PERSIST_DIRECTORY=/data/chroma

# Template-Konfiguration
TEMPLATES_DIRECTORY=templates
```