# Aufgabenkomplexitätsanalyse

Das Aufgabenkomplexitätsanalyse-Modul ist verantwortlich für die Analyse der Komplexität einer Aufgabe und die Bestimmung des passenden LLM-Modells. Es ist ein Schlüsselbestandteil des LLM-Selektor-Moduls.

## Komplexitätsfaktoren

Die Aufgabenkomplexitätsanalyse berücksichtigt folgende Faktoren:

1. **Länge**: Die Länge des Prompts in Zeichen
2. **Token-Anzahl**: Die geschätzte Anzahl der Tokens im Prompt
3. **Reasoning-Komplexität**: Ob die Aufgabe Reasoning erfordert
4. **Kreativitäts-Komplexität**: Ob die Aufgabe Kreativität erfordert
5. **Spezialisiertes Wissen-Komplexität**: Ob die Aufgabe spezialisiertes Wissen erfordert

Jeder Faktor wird auf einer Skala von 1-5 bewertet, und die Gesamtkomplexität wird als gewichteter Durchschnitt dieser Werte berechnet.

## Komplexitätslevel

Die Aufgabenkomplexitätsanalyse definiert folgende Komplexitätslevel:

- **VERY_SIMPLE**: Sehr einfache Aufgaben, die von einfachen Modellen bearbeitet werden können
- **SIMPLE**: Einfache Aufgaben, die ein Standardmodell erfordern
- **MEDIUM**: Aufgaben mittlerer Komplexität, die ein gutes Modell erfordern
- **COMPLEX**: Komplexe Aufgaben, die ein fortgeschrittenes Modell erfordern
- **VERY_COMPLEX**: Sehr komplexe Aufgaben, die ein hochwertiges Modell erfordern
- **EXTREMELY_COMPLEX**: Extrem komplexe Aufgaben, die die besten verfügbaren Modelle erfordern

## Komplexitätsanalyse-Algorithmus

Der Komplexitätsanalyse-Algorithmus funktioniert wie folgt:

1. Berechne den Längenwert basierend auf der Länge des Prompts
2. Schätze die Token-Anzahl und berechne den Token-Wert
3. Prüfe auf Reasoning-Indikatoren und berechne den Reasoning-Wert
4. Prüfe auf Kreativitäts-Indikatoren und berechne den Kreativitäts-Wert
5. Prüfe auf spezialisiertes Wissen-Indikatoren und berechne den spezialisierten Wissen-Wert
6. Berechne den Gesamt-Komplexitätswert als gewichteten Durchschnitt der einzelnen Werte
7. Ordne den Gesamt-Wert einem Komplexitätslevel zu

```python
def analyze_complexity(self, prompt: str) -> ComplexityLevel:
    """
    Analysiere die Komplexität eines Prompts.

    Args:
        prompt: Der zu analysierende Prompt

    Returns:
        Das Komplexitätslevel
    """
    # Berechne Komplexitätswert basierend auf verschiedenen Faktoren
    scores = {}
    
    # Längenwert
    length = len(prompt)
    if length < 100:
        scores["length"] = 1
    elif length < 500:
        scores["length"] = 2
    elif length < 1000:
        scores["length"] = 3
    elif length < 2000:
        scores["length"] = 4
    else:
        scores["length"] = 5
    
    # Token-Anzahl-Schätzung (grobe Annäherung)
    token_count = len(prompt.split())
    if token_count < 20:
        scores["tokens"] = 1
    elif token_count < 100:
        scores["tokens"] = 2
    elif token_count < 500:
        scores["tokens"] = 3
    elif token_count < 1000:
        scores["tokens"] = 4
    else:
        scores["tokens"] = 5
    
    # Reasoning-Komplexität
    reasoning_indicators = [
        r"why", r"how", r"explain", r"analyze", r"compare", r"contrast",
        r"evaluate", r"synthesize", r"critique", r"assess", r"reason"
    ]
    reasoning_score = 0
    for indicator in reasoning_indicators:
        if re.search(r"\b" + indicator + r"\b", prompt.lower()):
            reasoning_score += 1
    scores["reasoning"] = min(5, reasoning_score)
    
    # Kreativitäts-Komplexität
    creativity_indicators = [
        r"create", r"generate", r"design", r"imagine", r"story", r"creative",
        r"novel", r"unique", r"original", r"innovative", r"fiction"
    ]
    creativity_score = 0
    for indicator in creativity_indicators:
        if re.search(r"\b" + indicator + r"\b", prompt.lower()):
            creativity_score += 1
    scores["creativity"] = min(5, creativity_score)
    
    # Spezialisiertes Wissen-Komplexität
    specialized_indicators = [
        r"technical", r"scientific", r"medical", r"legal", r"financial",
        r"mathematical", r"code", r"programming", r"algorithm", r"physics",
        r"chemistry", r"biology", r"engineering", r"academic", r"research"
    ]
    specialized_score = 0
    for indicator in specialized_indicators:
        if re.search(r"\b" + indicator + r"\b", prompt.lower()):
            specialized_score += 1
    scores["specialized"] = min(5, specialized_score)
    
    # Berechne Gesamt-Komplexitätswert
    overall_score = (
        scores["length"] * 0.15 +
        scores["tokens"] * 0.15 +
        scores["reasoning"] * 0.3 +
        scores["creativity"] * 0.2 +
        scores["specialized"] * 0.2
    )
    
    # Ordne Gesamt-Wert einem Komplexitätslevel zu
    if overall_score < 1.5:
        return ComplexityLevel.VERY_SIMPLE
    elif overall_score < 2.5:
        return ComplexityLevel.SIMPLE
    elif overall_score < 3.5:
        return ComplexityLevel.MEDIUM
    elif overall_score < 4.0:
        return ComplexityLevel.COMPLEX
    elif overall_score < 4.5:
        return ComplexityLevel.VERY_COMPLEX
    else:
        return ComplexityLevel.EXTREMELY_COMPLEX
```

## Verwendung

### API-Endpunkt

```http
POST /api/v1/analyze
```

Request-Body:

```json
{
  "prompt": "Der zu analysierende Prompt"
}
```

Response:

```json
{
  "complexity": "medium",
  "recommended_model": "gpt-3.5-turbo"
}
```

### Programmatische Verwendung

```python
from llm_cost_analyzer.core.llm_selector import LLMSelector

# Initialisiere LLM-Selektor
llm_selector = LLMSelector()

# Analysiere Komplexität
prompt = "Erkläre die Relativitätstheorie in einfachen Worten."
complexity = llm_selector.analyze_complexity(prompt)

# Wähle Modell
model_id = llm_selector.select_model(complexity)
```

## Beispiele

### Sehr einfache Aufgabe

```
Was ist die Hauptstadt von Frankreich?
```

- Länge: 37 Zeichen (Wert: 1)
- Tokens: 7 Tokens (Wert: 1)
- Reasoning: Keine Reasoning-Indikatoren (Wert: 0)
- Kreativität: Keine Kreativitäts-Indikatoren (Wert: 0)
- Spezialisiertes Wissen: Keine spezialisierten Wissen-Indikatoren (Wert: 0)
- Gesamt-Wert: 0,3 (VERY_SIMPLE)
- Empfohlenes Modell: Lokales Modell oder günstigstes Cloud-Modell

### Einfache Aufgabe

```
Kannst du 5 beliebte Touristenattraktionen in Paris auflisten?
```

- Länge: 59 Zeichen (Wert: 1)
- Tokens: 10 Tokens (Wert: 1)
- Reasoning: Keine Reasoning-Indikatoren (Wert: 0)
- Kreativität: Keine Kreativitäts-Indikatoren (Wert: 0)
- Spezialisiertes Wissen: Keine spezialisierten Wissen-Indikatoren (Wert: 0)
- Gesamt-Wert: 0,3 (VERY_SIMPLE)
- Empfohlenes Modell: Lokales Modell oder günstigstes Cloud-Modell

### Aufgabe mittlerer Komplexität

```
Erkläre, wie der Treibhauseffekt funktioniert und warum er für den Klimawandel wichtig ist.
```

- Länge: 85 Zeichen (Wert: 1)
- Tokens: 15 Tokens (Wert: 1)
- Reasoning: "erkläre", "warum" (Wert: 2)
- Kreativität: Keine Kreativitäts-Indikatoren (Wert: 0)
- Spezialisiertes Wissen: "wissenschaftlich" (Wert: 1)
- Gesamt-Wert: 1,05 (SIMPLE)
- Empfohlenes Modell: Lokales Modell oder einfaches Cloud-Modell

### Komplexe Aufgabe

```
Analysiere die wirtschaftlichen Auswirkungen der Einführung eines bedingungslosen Grundeinkommens in entwickelten Ländern. Berücksichtige sowohl kurz- als auch langfristige Effekte, potenzielle Herausforderungen und wie es verschiedene sozioökonomische Gruppen beeinflussen könnte.
```

- Länge: 245 Zeichen (Wert: 2)
- Tokens: 37 Tokens (Wert: 2)
- Reasoning: "analysiere", "berücksichtige", "wie" (Wert: 3)
- Kreativität: Keine Kreativitäts-Indikatoren (Wert: 0)
- Spezialisiertes Wissen: "wirtschaftlich", "sozioökonomisch" (Wert: 2)
- Gesamt-Wert: 1,9 (SIMPLE)
- Empfohlenes Modell: Einfaches Cloud-Modell

### Sehr komplexe Aufgabe

```
Entwerfe eine umfassende Strategie für ein Tech-Startup zur Entwicklung und Vermarktung einer KI-gestützten Gesundheitslösung, die frühe Anzeichen chronischer Krankheiten vorhersagen kann. Berücksichtige technische Aspekte, ethische Implikationen, regulatorische Herausforderungen, Go-to-Market-Strategie und potenzielle Partnerschaften mit Gesundheitsdienstleistern. Analysiere auch potenzielle Risiken und wie man sie mindern kann.
```

- Länge: 380 Zeichen (Wert: 2)
- Tokens: 58 Tokens (Wert: 2)
- Reasoning: "analysiere", "wie", "strategie" (Wert: 3)
- Kreativität: "entwerfe", "strategie" (Wert: 2)
- Spezialisiertes Wissen: "technisch", "gesundheit", "regulatorisch", "KI" (Wert: 4)
- Gesamt-Wert: 2,7 (MEDIUM)
- Empfohlenes Modell: Gutes Cloud-Modell

### Extrem komplexe Aufgabe

```
Schreibe einen detaillierten Forschungsvorschlag zur Untersuchung des Potenzials von Quantencomputing bei der Lösung komplexer Proteinfaltungsprobleme, die zu Durchbrüchen in der Arzneimittelentdeckung führen könnten. Berücksichtige den theoretischen Hintergrund, die Methodik, die erwarteten Ergebnisse, potenzielle Herausforderungen und wie diese Forschung die Pharmaindustrie beeinflussen könnte. Der Vorschlag sollte wissenschaftlich fundiert sein und relevante mathematische Modelle und Algorithmen enthalten.
```

- Länge: 450 Zeichen (Wert: 2)
- Tokens: 67 Tokens (Wert: 2)
- Reasoning: "untersuchung", "wie", "herausforderungen" (Wert: 3)
- Kreativität: "durchbrüche", "vorschlag" (Wert: 2)
- Spezialisiertes Wissen: "quantencomputing", "proteinfaltung", "arzneimittelentdeckung", "pharma", "mathematische modelle", "algorithmen" (Wert: 5)
- Gesamt-Wert: 3,0 (MEDIUM)
- Empfohlenes Modell: Gutes Cloud-Modell