# LLM Cost Analyzer Architektur

Der LLM Cost Analyzer ist ein Modul zur Analyse der Komplexität von Aufgaben und Berechnung der Kosten für verschiedene LLM-Modelle. Er wählt automatisch das passende LLM basierend auf der Komplexität der Aufgabe aus und optimiert die Kosten durch Verwendung lokaler LLMs für einfachere Aufgaben.

## Systemarchitektur

Der LLM Cost Analyzer besteht aus folgenden Komponenten:

1. **API-Server**: FastAPI-Server, der REST-API-Endpunkte bereitstellt
2. **LLM-Selektor**: Wählt das passende LLM basierend auf der Komplexität der Aufgabe aus
3. **Aufgabenkostenrechner**: Berechnet die Kosten für die Verarbeitung einer Aufgabe mit verschiedenen Modellen

```
┌─────────────────────────────────────────────────────────────────┐
│                      LLM Cost Analyzer                           │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  API-Server  │◄───┤ Config      │    │ LLM-Selektor        │  │
│  └─────┬───────┘    └─────────────┘    └──────────┬──────────┘  │
│        │                                          │             │
│        ▼                                          ▼             │
│  ┌─────────────┐                         ┌─────────────────────┐│
│  │ Router      │                         │ Aufgabenkostenrechner││
│  └─────┬───────┘                         └─────────────────────┘│
│        │                                                        │
│        ▼                                                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Endpunkte   │◄───┤ Modelle     │    │ Komplexitätsanalyse │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Komponentendetails

### API-Server

Der API-Server ist mit FastAPI gebaut und stellt folgende Endpunkte bereit:

- `/api/v1/analyze`: Endpunkte zur Analyse der Komplexität von Aufgaben
- `/api/v1/estimate`: Endpunkte zur Berechnung der Kosten für verschiedene Modelle
- `/api/v1/models`: Endpunkte zur Verwaltung von Modellen

### LLM-Selektor

Der LLM-Selektor ist verantwortlich für:

- Analyse der Komplexität einer Aufgabe
- Auswahl des passenden LLMs basierend auf der Komplexität
- Verwaltung verfügbarer LLMs

### Aufgabenkostenrechner

Der Aufgabenkostenrechner ist verantwortlich für:

- Schätzung der Anzahl der Tokens in einem Prompt
- Schätzung der erwarteten Anzahl der Tokens in der Antwort
- Berechnung der Kosten für die Verarbeitung einer Aufgabe mit verschiedenen Modellen
- Generierung von Kostenberichten

## Datenfluss

1. Ein Benutzer sendet einen Prompt an den `/api/v1/analyze`-Endpunkt
2. Der API-Server empfängt den Prompt und leitet ihn an den Analyze-Endpunkt-Handler weiter
3. Der Analyze-Endpunkt-Handler:
   - Analysiert die Komplexität des Prompts mit dem LLM-Selektor
   - Wählt das passende LLM basierend auf der Komplexität aus
   - Gibt die Komplexität und das empfohlene Modell zurück

4. Ein Benutzer sendet einen Prompt an den `/api/v1/estimate/cost`-Endpunkt
5. Der API-Server empfängt den Prompt und leitet ihn an den Estimate-Endpunkt-Handler weiter
6. Der Estimate-Endpunkt-Handler:
   - Berechnet die Kosten für die Verarbeitung des Prompts mit verschiedenen Modellen
   - Gibt die Kostenschätzungen zurück

## Bereitstellung

Der LLM Cost Analyzer kann mit Docker und Docker Compose bereitgestellt werden:

```bash
# Baue und starte den Server
docker compose up -d

# Stoppe den Server
docker compose down
```

## Konfiguration

Der LLM Cost Analyzer kann über Umgebungsvariablen oder eine `.env`-Datei konfiguriert werden:

```
# API-Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
COHERE_API_KEY=your_cohere_api_key

# LLM-Konfiguration
DEFAULT_MODEL=gpt-3.5-turbo
USE_LOCAL_MODELS=true
LOCAL_MODEL_ENDPOINT=http://localhost:8080/v1
LOCAL_MODELS=llama3-8b,mistral-7b

# Server-Konfiguration
HOST=0.0.0.0
PORT=8000
DEBUG=false
```