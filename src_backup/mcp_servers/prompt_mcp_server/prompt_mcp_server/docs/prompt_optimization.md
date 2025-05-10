# Prompt-Optimierung

Das Prompt-Optimierungsmodul ist verantwortlich für die Verbesserung von Benutzer-Prompts zu strukturierten Best-Practice-Prompts. Es analysiert die Struktur von Benutzer-Prompts und verwendet Templates, um optimierte Prompts zu generieren.

## Funktionen

Das Prompt-Optimierungsmodul bietet folgende Funktionen:

1. **Prompt-Analyse**: Analysiert die Struktur von Benutzer-Prompts
2. **Prompt-Optimierung**: Verbessert Benutzer-Prompts zu strukturierten Best-Practice-Prompts
3. **System-Prompt-Generierung**: Generiert System-Prompts basierend auf Benutzer-Prompts und Parametern

## Prompt-Analyse

Die Prompt-Analyse untersucht einen Benutzer-Prompt und extrahiert Schlüsselkomponenten:

- **Prompt-Typ**: Instruction, Question oder Statement
- **Domain**: Programming, Writing, Analysis oder General
- **Struktur**: Hat der Prompt eine Frage, eine Anweisung oder Kontext?

```python
def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
    """
    Analysiere die Struktur eines Prompts.

    Args:
        prompt: Der zu analysierende Prompt

    Returns:
        Ein Dictionary mit Analyseergebnissen
    """
    # Extrahiere Schlüsselkomponenten aus dem Prompt
    components = {
        "has_question": bool(re.search(r"\?", prompt)),
        "has_instruction": bool(re.search(r"\b(erstelle|generiere|schreibe|liste|erkläre|beschreibe|analysiere)\b", prompt.lower())),
        "has_context": len(prompt.split()) > 20,  # Einfache Heuristik: Längere Prompts enthalten wahrscheinlich Kontext
        "word_count": len(prompt.split()),
        "character_count": len(prompt),
    }
    
    # Identifiziere Prompt-Typ
    if components["has_instruction"]:
        components["prompt_type"] = "instruction"
    elif components["has_question"]:
        components["prompt_type"] = "question"
    else:
        components["prompt_type"] = "statement"
    
    # Identifiziere Themenbereich (einfache Heuristik)
    if re.search(r"\b(code|programmier|funktion|klasse|methode|api|entwickl|software)\b", prompt.lower()):
        components["domain"] = "programming"
    elif re.search(r"\b(text|schreib|artikel|blog|zusammenfass|essay|bericht)\b", prompt.lower()):
        components["domain"] = "writing"
    elif re.search(r"\b(analyse|daten|statistik|trend|vorhersage|modell)\b", prompt.lower()):
        components["domain"] = "analysis"
    else:
        components["domain"] = "general"
    
    return components
```

## Prompt-Optimierung

Die Prompt-Optimierung verwendet Templates, um Benutzer-Prompts zu verbessern:

```python
async def optimize_prompt(
    self,
    user_prompt: str,
    template_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Optimiere einen Benutzer-Prompt zu einem strukturierten Best-Practice-Prompt.

    Args:
        user_prompt: Der zu optimierende Benutzer-Prompt
        template_id: Optionale Template-ID zur Verwendung
        context: Optionaler Kontext für das Template

    Returns:
        Der optimierte Prompt
    """
    try:
        # Verwende Standard-Template, wenn keines angegeben ist
        if not template_id:
            template_id = "default"
        
        # Hole Template
        template = self.template_manager.get_template(template_id)
        if not template:
            logger.warning(f"Template {template_id} nicht gefunden, verwende Rohprompt")
            return user_prompt
        
        # Bereite Kontext vor
        ctx = context or {}
        ctx["user_prompt"] = user_prompt
        
        # Analysiere Prompt-Struktur
        prompt_analysis = self._analyze_prompt(user_prompt)
        ctx.update(prompt_analysis)
        
        # Rendere Template
        optimized_prompt = self.template_manager.render_template(template_id, ctx)
        
        return optimized_prompt
    
    except Exception as e:
        logger.exception(f"Fehler bei der Prompt-Optimierung: {e}")
        # Fallback auf Rohprompt
        return user_prompt
```

## System-Prompt-Generierung

Die System-Prompt-Generierung erstellt System-Prompts basierend auf Benutzer-Prompts und Parametern:

```python
async def generate_system_prompt(
    self,
    user_prompt: str,
    role: Optional[str] = None,
    style: Optional[str] = None,
    constraints: Optional[List[str]] = None,
) -> str:
    """
    Generiere einen System-Prompt basierend auf Benutzer-Prompt und Parametern.

    Args:
        user_prompt: Der Benutzer-Prompt
        role: Optionale Rolle für den Assistenten
        style: Optionaler Stil für die Antwort
        constraints: Optionale Einschränkungen für die Antwort

    Returns:
        Der generierte System-Prompt
    """
    try:
        # Analysiere Prompt
        prompt_analysis = self._analyze_prompt(user_prompt)
        
        # Wähle passende Rolle basierend auf Domain, wenn keine angegeben ist
        if not role:
            if prompt_analysis["domain"] == "programming":
                role = "erfahrener Softwareentwickler"
            elif prompt_analysis["domain"] == "writing":
                role = "professioneller Texter"
            elif prompt_analysis["domain"] == "analysis":
                role = "Datenanalyst"
            else:
                role = "hilfreicher Assistent"
        
        # Erstelle System-Prompt
        system_prompt = f"Du bist ein {role}. "
        
        # Füge Stil hinzu, wenn angegeben
        if style:
            system_prompt += f"Antworte in einem {style} Stil. "
        
        # Füge Einschränkungen hinzu, wenn angegeben
        if constraints:
            system_prompt += "Beachte folgende Einschränkungen: "
            for constraint in constraints:
                system_prompt += f"- {constraint}\n"
        
        return system_prompt
    
    except Exception as e:
        logger.exception(f"Fehler bei der System-Prompt-Generierung: {e}")
        # Fallback auf Standard-System-Prompt
        return "Du bist ein hilfreicher Assistent."
```

## Templates

Das Prompt-Optimierungsmodul verwendet Templates, um Benutzer-Prompts zu verbessern. Hier sind einige Beispiel-Templates:

### Default-Template

```jinja
{% if system_prompt %}
{{ system_prompt }}
{% else %}
Du bist ein hilfreicher Assistent, der präzise und informative Antworten gibt.
{% endif %}

{% if history %}
# Konversationsverlauf
{% for message in history %}
{% if message.role == 'user' %}
Benutzer: {{ message.content }}
{% elif message.role == 'assistant' %}
Assistent: {{ message.content }}
{% elif message.role == 'system' %}
System: {{ message.content }}
{% endif %}
{% endfor %}
{% endif %}

{% if prompt_type == 'instruction' %}
# Anweisung
{{ user_prompt }}

# Antwortformat
Beantworte die Anweisung klar und strukturiert. Gib bei Bedarf Beispiele.
{% elif prompt_type == 'question' %}
# Frage
{{ user_prompt }}

# Antwortformat
Beantworte die Frage präzise und informativ. Gib bei Bedarf zusätzlichen Kontext.
{% else %}
# Eingabe
{{ user_prompt }}

# Antwortformat
Reagiere auf die Eingabe in hilfreicher Weise.
{% endif %}
```

### Code-Template

```jinja
{% if system_prompt %}
{{ system_prompt }}
{% else %}
Du bist ein erfahrener Softwareentwickler, der sauberen, effizienten und gut dokumentierten Code schreibt.
{% endif %}

{% if history %}
# Konversationsverlauf
{% for message in history %}
{% if message.role == 'user' %}
Benutzer: {{ message.content }}
{% elif message.role == 'assistant' %}
Assistent: {{ message.content }}
{% elif message.role == 'system' %}
System: {{ message.content }}
{% endif %}
{% endfor %}
{% endif %}

# Programmieraufgabe
{{ user_prompt }}

# Antwortformat
Bitte folge diesen Richtlinien:
1. Schreibe sauberen, lesbaren und effizienten Code
2. Füge Kommentare hinzu, um komplexe Teile zu erklären
3. Erkläre deinen Ansatz kurz vor dem Code
4. Verwende Best Practices für die jeweilige Programmiersprache
5. Achte auf Fehlerbehandlung und Edge Cases

# Codeblock
```
// Dein Code hier
```

# Erklärung
Erkläre, wie der Code funktioniert und wie er verwendet werden kann.
```

## API-Endpunkte

Das Prompt-Optimierungsmodul stellt folgende API-Endpunkte bereit:

### Prompt optimieren

```http
POST /api/v1/optimize/prompt
```

Request-Body:

```json
{
  "prompt": "Der zu optimierende Prompt",
  "template_id": "default",  // Optional
  "context": {  // Optional
    "key": "value"
  }
}
```

Response:

```json
{
  "optimized_prompt": "Der optimierte Prompt"
}
```

### System-Prompt generieren

```http
POST /api/v1/optimize/system-prompt
```

Request-Body:

```json
{
  "prompt": "Der Benutzer-Prompt",
  "role": "erfahrener Softwareentwickler",  // Optional
  "style": "präzise und technisch",  // Optional
  "constraints": [  // Optional
    "Verwende nur Python 3.10+",
    "Achte auf Sicherheit"
  ]
}
```

Response:

```json
{
  "system_prompt": "Du bist ein erfahrener Softwareentwickler. Antworte in einem präzise und technisch Stil. Beachte folgende Einschränkungen: - Verwende nur Python 3.10+\n- Achte auf Sicherheit\n"
}
```