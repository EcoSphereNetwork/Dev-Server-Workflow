# Prompt MCP Server

Der Prompt MCP Server ist ein Master Control Program Server für Prompt Engineering mit Templates, Memory und Pre-Prompts. Er verbessert Benutzer-Prompts zu strukturierten Best-Practice-Prompts, verwaltet Prompt-Templates und den Konversationsverlauf.

## Features

- **Prompt-Optimierung**: Verbessert Benutzer-Prompts zu strukturierten Best-Practice-Prompts
- **Template-Verwaltung**: Verwaltet Prompt-Templates und deren Rendering
- **Memory-Management**: Verwaltet den Konversationsverlauf und Kontext
- **API-Endpunkte**: RESTful API für die Interaktion mit dem Server
- **MCP-Kompatibilität**: Vollständig kompatibel mit dem MCP-Protokoll für nahtlose Integration in das MCP-Ökosystem

## Architektur

Der Prompt MCP Server besteht aus folgenden Komponenten:

1. **Template-Manager**: Verwaltet Prompt-Templates und deren Rendering
2. **Memory-Manager**: Verwaltet den Konversationsverlauf und Kontext
3. **Prompt-Optimierer**: Verbessert Benutzer-Prompts zu strukturierten Best-Practice-Prompts
4. **API-Server**: Bietet RESTful API-Endpunkte für die Interaktion mit dem Server
5. **MCP-Interface**: Bietet eine MCP-konforme Schnittstelle für die Integration in das MCP-Ökosystem

## Installation

### Mit dem MCP Hub

```bash
# Installiere den Prompt MCP Server mit dem MCP Hub
mcp-hub install prompt-mcp-server
```

### Manuelle Installation

```bash
# Klone das Repository
git clone https://github.com/yourusername/prompt-mcp-server.git
cd prompt-mcp-server

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
mcp-hub start prompt-mcp-server

# Manuell
cd /path/to/prompt-mcp-server
poetry run python -m prompt_mcp_server

# Oder mit uvicorn direkt
poetry run uvicorn prompt_mcp_server.main:app --host 0.0.0.0 --port 8001
```

### API-Endpunkte

- `POST /api/v1/chat`: Chat-Endpunkte zum Senden von Nachrichten und Verwalten von Sitzungen
- `GET /api/v1/models`: Modell-Endpunkte zum Auflisten von Modellen
- `GET /api/v1/templates`: Template-Endpunkte zum Verwalten von Templates
- `POST /api/v1/optimize`: Optimierungs-Endpunkte zum Verbessern von Prompts
- `GET /mcp-info`: Gibt Informationen über die MCP-Kompatibilität zurück
- `WebSocket /api/v1/ws/mcp`: MCP-WebSocket-Endpunkt für die Kommunikation mit anderen MCP-Servern

### MCP-Integration

Der Prompt MCP Server kann nahtlos in das MCP-Ökosystem integriert werden. Er bietet folgende MCP-Funktionen:

- **Prompt-Optimierung**: Verbessert Benutzer-Prompts zu strukturierten Best-Practice-Prompts
- **Template-Verwaltung**: Verwaltet Prompt-Templates und deren Rendering
- **Memory-Management**: Verwaltet den Konversationsverlauf und Kontext
- **Chat-Funktionen**: Bietet Chat-Funktionen für die Interaktion mit LLMs

### MCP-Nachrichten

Der Prompt MCP Server unterstützt folgende MCP-Nachrichtentypen:

#### optimize_prompt

Optimiert einen Benutzer-Prompt zu einem strukturierten Best-Practice-Prompt.

```json
{
  "type": "optimize_prompt",
  "request_id": "123",
  "prompt": "Der zu optimierende Prompt",
  "template_id": "default",
  "context": {
    "key": "value"
  }
}
```

Antwort:

```json
{
  "type": "optimized_prompt",
  "request_id": "123",
  "prompt": "Der optimierte Prompt"
}
```

#### generate_system_prompt

Generiert einen System-Prompt basierend auf Benutzer-Prompt und Parametern.

```json
{
  "type": "generate_system_prompt",
  "request_id": "123",
  "prompt": "Der Benutzer-Prompt",
  "role": "erfahrener Softwareentwickler",
  "style": "präzise und technisch",
  "constraints": [
    "Verwende nur Python 3.10+",
    "Achte auf Sicherheit"
  ]
}
```

Antwort:

```json
{
  "type": "system_prompt",
  "request_id": "123",
  "prompt": "Du bist ein erfahrener Softwareentwickler. Antworte in einem präzise und technisch Stil. Beachte folgende Einschränkungen: - Verwende nur Python 3.10+\n- Achte auf Sicherheit\n"
}
```

#### chat_message

Sendet eine Chat-Nachricht.

```json
{
  "type": "chat_message",
  "request_id": "123",
  "session_id": "session-123",
  "message": {
    "role": "user",
    "content": "Hallo!"
  }
}
```

Antwort:

```json
{
  "type": "chat_response",
  "request_id": "123",
  "session_id": "session-123",
  "message": {
    "role": "assistant",
    "content": "Hallo! Wie kann ich dir helfen?",
    "timestamp": "2023-01-01T00:00:00Z"
  }
}
```

#### list_templates

Listet verfügbare Templates auf.

```json
{
  "type": "list_templates",
  "request_id": "123"
}
```

Antwort:

```json
{
  "type": "templates_list",
  "request_id": "123",
  "templates": [
    {
      "id": "default",
      "name": "Default",
      "description": "Default template for chat",
      "type": "chat"
    },
    {
      "id": "code",
      "name": "Code",
      "description": "Template for code generation",
      "type": "completion"
    }
  ]
}
```

## Templates

Der Prompt MCP Server verwendet Templates, um Benutzer-Prompts zu verbessern. Hier sind einige Beispiel-Templates:

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

## Konfiguration

Der Server kann über Umgebungsvariablen oder eine `.env`-Datei konfiguriert werden:

```
# API-Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Server-Konfiguration
HOST=0.0.0.0
PORT=8001
DEBUG=false

# Memory-Konfiguration
MEMORY_TYPE=in_memory  # in_memory, redis, chroma
REDIS_URL=redis://localhost:6379/0
CHROMA_PERSIST_DIRECTORY=/data/chroma

# Template-Konfiguration
TEMPLATES_DIRECTORY=templates

# MCP-Konfiguration
MCP_ENABLED=true
MCP_SERVER_ID=prompt-mcp-server
MCP_SERVER_NAME=Prompt MCP Server
```

## Lizenz

MIT