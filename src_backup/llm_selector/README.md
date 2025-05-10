# Automatic LLM Selector

Dieses System ermöglicht die automatische Auswahl des optimalen LLM (Language Model) basierend auf der Komplexität einer Aufgabe. Es analysiert eingehende Aufgaben, bestimmt deren Komplexität und wählt das kostengünstigste und leistungsfähigste Modell aus, das die Anforderungen erfüllen kann.

## Funktionen

- **Automatische Komplexitätsanalyse**: Analysiert Aufgabenbeschreibungen, um deren Komplexität zu bestimmen
- **Intelligente Modellauswahl**: Wählt das optimale Modell basierend auf Komplexität, Kosten und Qualitätsanforderungen
- **Kostenoptimierung**: Verwendet lokale Modelle für einfache Aufgaben und Cloud-Modelle nur für komplexe Anforderungen
- **Flexible Auswahlstrategien**: Unterstützt verschiedene Strategien (kosteneffizient, ausgewogen, hohe Qualität, schnellste Antwort)
- **API-Schnittstelle**: Bietet eine REST-API für die Integration in bestehende Systeme
- **n8n-Workflow**: Enthält einen n8n-Workflow für die einfache Integration in n8n-basierte Systeme

## Komponenten

Das System besteht aus folgenden Komponenten:

1. **Task Complexity Analyzer**: Analysiert Aufgabenbeschreibungen und bestimmt deren Komplexität
2. **Model Cost Estimator**: Berechnet die Kosten für verschiedene Modelle basierend auf der Aufgabenkomplexität
3. **LLM Selector**: Wählt das optimale Modell basierend auf Komplexität, Kosten und Qualitätsanforderungen
4. **LLM Selector API**: REST-API für die Integration in bestehende Systeme
5. **n8n-Workflow**: Workflow für die Integration in n8n-basierte Systeme

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python-Paketmanager)
- n8n (für den Workflow)

### Installation der Python-Abhängigkeiten

```bash
pip install fastapi uvicorn requests
```

### Starten der API

```bash
python llm_selector_api.py
```

Die API ist dann unter `http://localhost:5000` verfügbar.

### Importieren des n8n-Workflows

1. Öffnen Sie n8n
2. Gehen Sie zu "Workflows"
3. Klicken Sie auf "Import from File"
4. Wählen Sie die Datei `Automatic-LLM-Selector.json`

## Verwendung

### Über die API

#### Analyse einer Aufgabe

```bash
curl -X POST http://localhost:5000/analyze-task \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Erstelle eine Zusammenfassung des folgenden Textes...",
    "task_type": "summarization",
    "quality_threshold": 7.5
  }'
```

#### Auswahl eines Modells

```bash
curl -X POST http://localhost:5000/select-model \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Erstelle eine Zusammenfassung des folgenden Textes...",
    "task_type": "summarization",
    "selection_strategy": "balanced",
    "quality_threshold": 7.5
  }'
```

#### Kostenberechnung

```bash
curl -X POST http://localhost:5000/estimate-task-cost \
  -H "Content-Type: application/json" \
  -d '{
    "task_complexity": "medium",
    "quality_threshold": 7.5
  }'
```

### Über den Python-Client

```python
from llm_selector_client import select_model

result = select_model(
    api_url="http://localhost:5000",
    task_description="Erstelle eine Zusammenfassung des folgenden Textes...",
    task_type="summarization",
    selection_strategy="balanced",
    quality_threshold=7.5
)

print(result["summary"]["selected_model"])
```

### Über die Kommandozeile

```bash
python llm_selector_client.py select-model \
  --task "Erstelle eine Zusammenfassung des folgenden Textes..." \
  --type summarization \
  --strategy balanced \
  --quality 7.5
```

### Über den n8n-Workflow

1. Senden Sie eine POST-Anfrage an den Webhook-Endpunkt des Workflows
2. Fügen Sie die Aufgabenbeschreibung und andere Parameter hinzu
3. Der Workflow analysiert die Aufgabe und wählt das optimale Modell aus

## Komplexitätskategorien

Das System unterstützt folgende Komplexitätskategorien:

- **very_simple**: Sehr einfache Aufgaben (Klassifikation, kurze Antworten, einfache Fragen)
- **simple**: Einfache Aufgaben (Zusammenfassungen, kurze Texte, einfache Faktenrecherche)
- **medium**: Mittlere Komplexität (Standard-Codegeneration, detaillierte Antworten, Analysen)
- **complex**: Komplexe Aufgaben (Tiefe Textanalysen, fortgeschrittene Codegeneration, logisches Reasoning)
- **very_complex**: Sehr komplexe Aufgaben (Multi-step Reasoning, detaillierte Berichte, komplexe Problemlösung)
- **extremely_complex**: Extrem komplexe Aufgaben (Forschungssynthesen, hochkomplexe Logikketten, AI-Agenten-Systeme)

## Unterstützte Modelle

### Lokale Modelle

- **local-1.5b**: Sehr kleines Modell für einfache Aufgaben
- **local-3b**: Kleines Modell für einfache bis mittlere Aufgaben
- **local-7b**: Mittelgroßes Modell für mittlere Aufgaben
- **local-13b**: Größeres Modell für mittlere bis komplexe Aufgaben
- **local-34b**: Großes Modell für komplexe Aufgaben
- **local-70b**: Sehr großes Modell für sehr komplexe Aufgaben

### Cloud-Modelle

- **claude-3-5-sonnet**: Anthropic Claude 3.5 Sonnet
- **claude-3-opus**: Anthropic Claude 3 Opus
- **gpt-4o**: OpenAI GPT-4o
- **gpt-4o-mini**: OpenAI GPT-4o Mini

## Auswahlstrategien

Das System unterstützt folgende Auswahlstrategien:

- **cost_effective**: Wählt das kostengünstigste Modell, das die Anforderungen erfüllt
- **balanced**: Balanciert Kosten, Geschwindigkeit und Qualität
- **high_quality**: Priorisiert Qualität über Kosten
- **fastest**: Wählt das Modell mit der geringsten Latenz

## Anpassung

### Hinzufügen neuer Modelle

Um neue Modelle hinzuzufügen, bearbeiten Sie die `MODEL_DATABASE` in der Datei `llm_selector.py`:

```python
MODEL_DATABASE = {
    # Bestehendes Modell
    "local-1.5b": { ... },
    
    # Neues Modell
    "local-new-model": {
        "type": "local",
        "hardware_cost": 2000,
        "power_consumption_w": 200,
        "max_context": 4096,
        "max_output": 2048,
        "token_processing_speed": 80,
        "complexity_handling": 5.5,
        "quality_score": 6.0,
        "multimodal_capable": False,
        "maintenance_cost_per_month": 75
    }
}
```

### Anpassung der Komplexitätskategorien

Um die Komplexitätskategorien anzupassen, bearbeiten Sie die `COMPLEXITY_CATEGORIES` in der Datei `llm_selector.py`.

## Integration in bestehende Systeme

### Integration in n8n

1. Importieren Sie den Workflow `Automatic-LLM-Selector.json` in n8n
2. Konfigurieren Sie den Webhook-Endpunkt
3. Verbinden Sie den Workflow mit Ihren bestehenden Workflows

### Integration in andere Systeme

Verwenden Sie die REST-API, um das System in andere Systeme zu integrieren:

```python
import requests

def select_model_for_task(task_description):
    response = requests.post(
        "http://localhost:5000/select-model",
        json={
            "task_description": task_description,
            "selection_strategy": "balanced"
        }
    )
    result = response.json()
    return result["summary"]["selected_model"]

# Beispielverwendung
model = select_model_for_task("Erstelle eine Zusammenfassung des folgenden Textes...")
print(f"Ausgewähltes Modell: {model}")
```

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe die Datei LICENSE für weitere Informationen.