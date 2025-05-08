# Aufgabenkostenschätzungsmodul

Das Aufgabenkostenschätzungsmodul ist verantwortlich für die Berechnung der Kosten für die Verarbeitung einer Aufgabe mit verschiedenen LLM-Modellen. Es bietet Funktionalität zur:

1. Schätzung der Anzahl der Tokens in einem Prompt
2. Schätzung der erwarteten Anzahl der Tokens in der Antwort
3. Berechnung der Kosten für die Verarbeitung einer Aufgabe mit verschiedenen Modellen
4. Generierung eines menschenlesbaren Kostenberichts

## Architektur

Das Aufgabenkostenschätzungsmodul besteht aus folgenden Komponenten:

1. **TaskCostEstimator**: Die Hauptklasse, die Kostenschätzungsfunktionalität bereitstellt
2. **LLMSelector**: Wird verwendet, um das passende LLM basierend auf der Aufgabenkomplexität auszuwählen
3. **Kosten-API-Endpunkte**: REST-API-Endpunkte für die Kostenschätzung

## Verwendung

### API-Endpunkte

#### Kosten schätzen

```http
POST /api/v1/estimate/cost
```

Request-Body:

```json
{
  "prompt": "Der Prompt, für den die Kosten geschätzt werden sollen",
  "model_ids": ["gpt-3.5-turbo", "gpt-4-turbo"],  // Optional
  "expected_output_length": 1000  // Optional
}
```

Response:

```json
{
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
```

#### Kostenbericht generieren

```http
POST /api/v1/estimate/report
```

Request-Body:

```json
{
  "prompt": "Der Prompt, für den die Kosten geschätzt werden sollen",
  "model_ids": ["gpt-3.5-turbo", "gpt-4-turbo"],  // Optional
  "expected_output_length": 1000  // Optional
}
```

Response:

```json
{
  "report": "# Aufgabenkostenschätzungsbericht\n\n## Aufgabenkomplexität: medium\n\n## Token-Schätzungen\n- Geschätzte Input-Tokens: 100\n- Geschätzte Output-Tokens: 150\n- Gesamttokens: 250\n\n## Empfohlenes Modell\n- Modell: GPT-3.5 Turbo (OpenAI)\n\n## Kostenschätzungen\n\n| Modell | Anbieter | Input-Kosten | Output-Kosten | Gesamtkosten |\n|-------|----------|------------|-------------|------------|\n| GPT-3.5 Turbo | OpenAI | $0.000050 | $0.000225 | $0.000275 |\n| GPT-4 Turbo | OpenAI | $0.001000 | $0.004500 | $0.005500 |\n"
}
```

### Programmatische Verwendung

```python
from llm_cost_analyzer.core.llm_selector import LLMSelector
from llm_cost_analyzer.core.task_cost_estimator import TaskCostEstimator

# Initialisiere Abhängigkeiten
llm_selector = LLMSelector()

# Initialisiere Aufgabenkostenrechner
task_cost_estimator = TaskCostEstimator(llm_selector)

# Schätze Kosten
prompt = "Erkläre die Relativitätstheorie in einfachen Worten."
estimates = await task_cost_estimator.estimate_cost(prompt)

# Generiere Kostenbericht
report = await task_cost_estimator.generate_cost_report(prompt)
```

## Token-Schätzung

Das Modul verwendet eine einfache Heuristik zur Schätzung der Anzahl der Tokens in einem Text:

```python
def estimate_tokens(self, text: str) -> int:
    # Einfache Schätzung: 1 Token ≈ 4 Zeichen für englischen Text
    return len(text) // 4
```

Dies ist eine grobe Annäherung und mag nicht für alle Sprachen und Inhaltstypen genau sein. Für eine genauere Token-Zählung können modellspezifische Tokenizer verwendet werden.

## Kostenberechnung

Die Kosten werden basierend auf den Input- und Output-Tokens berechnet:

```
input_cost = (input_tokens / 1.000.000) * model.input_cost
output_cost = (output_tokens / 1.000.000) * model.output_cost
total_cost = input_cost + output_cost
```

Wobei:
- `input_tokens` ist die geschätzte Anzahl der Tokens im Prompt
- `output_tokens` ist die geschätzte Anzahl der Tokens in der Antwort
- `model.input_cost` sind die Kosten pro 1M Input-Tokens für das Modell
- `model.output_cost` sind die Kosten pro 1M Output-Tokens für das Modell