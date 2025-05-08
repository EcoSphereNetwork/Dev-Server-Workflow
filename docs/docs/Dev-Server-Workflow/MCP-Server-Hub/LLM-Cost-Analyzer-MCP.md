# LLM Cost Analyzer MCP Server

Der LLM Cost Analyzer MCP Server ist ein MCP-kompatibler Server zur Analyse der Komplexität von Aufgaben und Berechnung der Kosten für verschiedene LLM-Modelle. Er wählt automatisch das passende LLM (lokal oder Cloud) basierend auf der Komplexität aus und optimiert die Kosten durch Verwendung lokaler LLMs für einfachere Aufgaben.

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

### Mit dem MCP Hub

```bash
# Installiere den LLM Cost Analyzer MCP Server mit dem MCP Hub
mcp-hub install llm-cost-analyzer
```

### Manuelle Installation

```bash
# Klone das Repository
git clone https://github.com/yourusername/llm-cost-analyzer-mcp.git
cd llm-cost-analyzer-mcp

# Installiere Abhängigkeiten
poetry install

# Umgebungsvariablen einrichten
cp .env.example .env
# .env mit API-Keys und Konfiguration bearbeiten
```

## Verwendung

### Starten des Servers

```bash
# Mit dem MCP Hub
mcp-hub start llm-cost-analyzer

# Manuell
cd /path/to/llm-cost-analyzer-mcp
poetry run python -m llm_cost_analyzer_mcp

# Oder mit uvicorn direkt
poetry run uvicorn llm_cost_analyzer_mcp.main:app --host 0.0.0.0 --port 8000
```

### API-Endpunkte

- `POST /api/v1/analyze`: Analysiert die Komplexität einer Aufgabe
- `POST /api/v1/estimate`: Berechnet die Kosten für verschiedene LLM-Modelle
- `POST /api/v1/report`: Generiert einen menschenlesbaren Kostenbericht
- `GET /api/v1/models`: Listet verfügbare LLM-Modelle auf
- `GET /mcp-info`: Gibt Informationen über die MCP-Kompatibilität zurück
- `WebSocket /api/v1/ws/mcp`: MCP-WebSocket-Endpunkt für die Kommunikation mit anderen MCP-Servern

### MCP-Integration

Der LLM Cost Analyzer MCP Server kann nahtlos in das MCP-Ökosystem integriert werden. Er bietet folgende MCP-Funktionen:

- **Komplexitätsanalyse**: Analysiert die Komplexität von Aufgaben und wählt das passende LLM aus
- **Kostenberechnung**: Berechnet die Kosten für verschiedene LLM-Modelle
- **Kostenoptimierung**: Optimiert die Kosten durch Verwendung lokaler LLMs für einfachere Aufgaben
- **Modellverwaltung**: Verwaltet verfügbare LLM-Modelle und deren Eigenschaften

### MCP-Nachrichten

Der LLM Cost Analyzer MCP Server unterstützt folgende MCP-Nachrichtentypen:

#### analyze_complexity

Analysiert die Komplexität eines Prompts.

```json
{
  "type": "analyze_complexity",
  "request_id": "123",
  "prompt": "Der zu analysierende Prompt"
}
```

Antwort:

```json
{
  "type": "complexity_result",
  "request_id": "123",
  "complexity": "medium",
  "recommended_model": "gpt-3.5-turbo"
}
```

#### estimate_cost

Schätzt die Kosten für einen Prompt.

```json
{
  "type": "estimate_cost",
  "request_id": "123",
  "prompt": "Der Prompt, für den die Kosten geschätzt werden sollen",
  "model_ids": ["gpt-3.5-turbo", "gpt-4-turbo"],
  "expected_output_length": 1000
}
```

Antwort:

```json
{
  "type": "cost_estimate_result",
  "request_id": "123",
  "cost_estimate": {
    "estimated_input_tokens": 100,
    "estimated_output_tokens": 150,
    "complexity": "medium",
    "recommended_model": {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "provider": "OpenAI"
    },
    "cost_estimates": [
      {
        "model": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "OpenAI",
        "input_tokens": 100,
        "output_tokens": 150,
        "input_cost": 0.00005,
        "output_cost": 0.000225,
        "total_cost": 0.000275
      },
      {
        "model": "gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "provider": "OpenAI",
        "input_tokens": 100,
        "output_tokens": 150,
        "input_cost": 0.001,
        "output_cost": 0.0045,
        "total_cost": 0.0055
      }
    ]
  }
}
```

#### generate_report

Generiert einen Kostenbericht.

```json
{
  "type": "generate_report",
  "request_id": "123",
  "prompt": "Der Prompt, für den die Kosten geschätzt werden sollen",
  "model_ids": ["gpt-3.5-turbo", "gpt-4-turbo"],
  "expected_output_length": 1000
}
```

Antwort:

```json
{
  "type": "report_result",
  "request_id": "123",
  "report": "# Aufgabenkostenschätzungsbericht\n\n## Aufgabenkomplexität: medium\n\n## Token-Schätzungen\n- Geschätzte Input-Tokens: 100\n- Geschätzte Output-Tokens: 150\n- Gesamttokens: 250\n\n## Empfohlenes Modell\n- Modell: GPT-3.5 Turbo (OpenAI)\n\n## Kostenschätzungen\n\n| Modell | Anbieter | Input-Kosten | Output-Kosten | Gesamtkosten |\n|-------|----------|------------|-------------|------------|\n| GPT-3.5 Turbo | OpenAI | $0.000050 | $0.000225 | $0.000275 |\n| GPT-4 Turbo | OpenAI | $0.001000 | $0.004500 | $0.005500 |\n"
}
```

#### list_models

Listet verfügbare Modelle auf.

```json
{
  "type": "list_models",
  "request_id": "123",
  "model_type": "cloud"
}
```

Antwort:

```json
{
  "type": "models_list",
  "request_id": "123",
  "models": [
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "provider": "OpenAI",
      "type": "cloud",
      "context_length": 16385,
      "input_cost": 0.5,
      "output_cost": 1.5,
      "complexity_handling": 7.5,
      "quality_score": 8.0,
      "token_processing_speed": 1000,
      "multimodal_capable": false,
      "metadata": {}
    },
    {
      "id": "gpt-4-turbo",
      "name": "GPT-4 Turbo",
      "provider": "OpenAI",
      "type": "cloud",
      "context_length": 128000,
      "input_cost": 10.0,
      "output_cost": 30.0,
      "complexity_handling": 9.5,
      "quality_score": 9.5,
      "token_processing_speed": 800,
      "multimodal_capable": false,
      "metadata": {}
    }
  ]
}
```

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