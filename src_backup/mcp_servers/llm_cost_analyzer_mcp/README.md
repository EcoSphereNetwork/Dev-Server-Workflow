# LLM Cost Analyzer MCP Server

Ein MCP Server zur Analyse der Komplexität von Aufgaben und Berechnung der Kosten für verschiedene LLM-Modelle.

## Features

- **Komplexitätsanalyse**: Analysiert die Komplexität von Aufgaben basierend auf verschiedenen Faktoren
- **LLM-Auswahl**: Wählt das passende LLM basierend auf der Komplexität der Aufgabe
- **Kostenberechnung**: Berechnet die Kosten für verschiedene LLM-Modelle (lokal und Cloud)
- **Kostenoptimierung**: Optimiert die Kosten durch Verwendung lokaler LLMs für einfachere Aufgaben
- **API-Endpunkte**: RESTful API für die Interaktion mit dem Modul
- **MCP-Kompatibilität**: Vollständig kompatibel mit dem MCP-Protokoll für nahtlose Integration in das MCP-Ökosystem

## Architektur

Der LLM Cost Analyzer MCP Server besteht aus folgenden Komponenten:

1. **Komplexitätsanalysator**: Analysiert die Komplexität von Aufgaben
2. **LLM-Selektor**: Wählt das passende LLM basierend auf der Komplexität
3. **Kostenrechner**: Berechnet die Kosten für verschiedene LLM-Modelle
4. **API-Server**: Bietet RESTful API-Endpunkte für die Interaktion mit dem Modul
5. **MCP-Interface**: Bietet eine MCP-konforme Schnittstelle für die Integration in das MCP-Ökosystem

## Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/llm-cost-analyzer-mcp.git
cd llm-cost-analyzer-mcp

# Abhängigkeiten installieren
poetry install

# Umgebungsvariablen einrichten
cp .env.example .env
# .env mit API-Keys und Konfiguration bearbeiten
```

## Verwendung

```bash
# Server starten
poetry run python -m llm_cost_analyzer_mcp

# Oder mit uvicorn direkt
poetry run uvicorn llm_cost_analyzer_mcp.main:app --host 0.0.0.0 --port 8000
```

## API-Endpunkte

- `POST /api/v1/analyze`: Analysiert die Komplexität einer Aufgabe
- `POST /api/v1/estimate`: Berechnet die Kosten für verschiedene LLM-Modelle
- `POST /api/v1/report`: Generiert einen menschenlesbaren Kostenbericht
- `GET /api/v1/models`: Listet verfügbare LLM-Modelle auf
- `GET /mcp-info`: Gibt Informationen über die MCP-Kompatibilität zurück
- `WebSocket /api/v1/ws/mcp`: MCP-WebSocket-Endpunkt für die Kommunikation mit anderen MCP-Servern

## MCP-Integration

Der LLM Cost Analyzer MCP Server kann nahtlos in das MCP-Ökosystem integriert werden. Er bietet folgende MCP-Funktionen:

- **Komplexitätsanalyse**: Analysiert die Komplexität von Aufgaben und wählt das passende LLM aus
- **Kostenberechnung**: Berechnet die Kosten für verschiedene LLM-Modelle
- **Kostenoptimierung**: Optimiert die Kosten durch Verwendung lokaler LLMs für einfachere Aufgaben
- **Modellverwaltung**: Verwaltet verfügbare LLM-Modelle und deren Eigenschaften

## Konfiguration

Der Server kann über Umgebungsvariablen oder eine `.env`-Datei konfiguriert werden:

```
# API-Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# LLM-Konfiguration
DEFAULT_MODEL=gpt-3.5-turbo
USE_LOCAL_MODELS=true
LOCAL_MODEL_ENDPOINT=http://localhost:8080/v1

# Server-Konfiguration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# MCP-Konfiguration
MCP_ENABLED=true
MCP_SERVER_ID=llm-cost-analyzer
MCP_SERVER_NAME=LLM Cost Analyzer
```

## Lizenz

MIT