# Templates

Das Templates-Modul ist verantwortlich für die Verwaltung von Prompt-Templates. Es bietet Funktionalität zum Laden, Speichern, Rendern und Verwalten von Templates.

## Template-Manager

Der Template-Manager ist die Hauptklasse des Templates-Moduls. Er bietet folgende Funktionen:

1. **Template-Verwaltung**: Laden, Speichern, Erstellen, Aktualisieren und Löschen von Templates
2. **Template-Rendering**: Rendern von Templates mit Kontext

```python
class TemplateManager:
    """Template manager class."""

    def __init__(self):
        """Initialize the template manager."""
        self.templates: Dict[str, Template] = {}
        self.promplate_templates: Dict[str, PromplateTemplate] = {}
        self.templates_dir = Path(settings.TEMPLATES_DIRECTORY)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._load_templates()
```

## Template-Modell

Das Template-Modell definiert die Struktur eines Templates:

```python
class Template(BaseModel):
    """Template model."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="The template ID")
    name: str = Field(..., description="The template name")
    description: Optional[str] = Field(None, description="The template description")
    content: str = Field(..., description="The template content")
    type: TemplateType = Field(default=TemplateType.CHAT, description="The template type")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="The creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="The last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Tags for the template")
```

## Template-Typen

Templates können verschiedene Typen haben:

```python
class TemplateType(str, Enum):
    """Template type enum."""

    CHAT = "chat"
    COMPLETION = "completion"
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    CUSTOM = "custom"
```

## Template-Verwaltung

Der Template-Manager bietet folgende Funktionen zur Template-Verwaltung:

### Templates auflisten

```python
def list_templates(self, skip: int = 0, limit: int = 100) -> List[Template]:
    """
    List all templates.

    Args:
        skip: Number of templates to skip
        limit: Maximum number of templates to return

    Returns:
        List of templates
    """
    return list(self.templates.values())[skip:skip + limit]
```

### Template abrufen

```python
def get_template(self, template_id: str) -> Optional[Template]:
    """
    Get a template by ID.

    Args:
        template_id: The template ID

    Returns:
        The template if found, None otherwise
    """
    return self.templates.get(template_id)
```

### Template erstellen

```python
def create_template(self, template_create: TemplateCreate) -> Template:
    """
    Create a new template.

    Args:
        template_create: The template creation data

    Returns:
        The created template
    """
    # Create template
    template = Template(
        name=template_create.name,
        description=template_create.description,
        content=template_create.content,
        type=template_create.type,
        metadata=template_create.metadata or {},
        tags=template_create.tags or [],
    )

    # Add template
    self.templates[template.id] = template
    self.promplate_templates[template.id] = PromplateTemplate(template.content)

    # Save templates
    self._save_templates()

    return template
```

### Template aktualisieren

```python
def update_template(self, template_id: str, template_update: TemplateUpdate) -> Optional[Template]:
    """
    Update a template.

    Args:
        template_id: The template ID
        template_update: The template update data

    Returns:
        The updated template if found, None otherwise
    """
    # Get template
    template = self.templates.get(template_id)
    if not template:
        return None

    # Update template
    if template_update.name is not None:
        template.name = template_update.name
    if template_update.description is not None:
        template.description = template_update.description
    if template_update.content is not None:
        template.content = template_update.content
        self.promplate_templates[template.id] = PromplateTemplate(template.content)
    if template_update.type is not None:
        template.type = template_update.type
    if template_update.metadata is not None:
        template.metadata = template_update.metadata
    if template_update.tags is not None:
        template.tags = template_update.tags
    
    template.updated_at = datetime.utcnow()

    # Save templates
    self._save_templates()

    return template
```

### Template löschen

```python
def delete_template(self, template_id: str) -> bool:
    """
    Delete a template.

    Args:
        template_id: The template ID

    Returns:
        True if the template was deleted, False otherwise
    """
    # Check if template exists
    if template_id not in self.templates:
        return False

    # Delete template
    del self.templates[template_id]
    del self.promplate_templates[template_id]

    # Save templates
    self._save_templates()

    return True
```

## Template-Rendering

Der Template-Manager bietet eine Funktion zum Rendern von Templates mit Kontext:

```python
def render_template(self, template_id: str, context: Dict[str, Any]) -> str:
    """
    Render a template with the given context.

    Args:
        template_id: The template ID
        context: The context to render the template with

    Returns:
        The rendered template
    """
    # Get template
    template = self.promplate_templates.get(template_id)
    if not template:
        raise ValueError(f"Template {template_id} not found")

    # Render template
    return template.render(**context)
```

## API-Endpunkte

Das Templates-Modul stellt folgende API-Endpunkte bereit:

### Templates auflisten

```http
GET /api/v1/templates
```

Response:

```json
[
  {
    "id": "default",
    "name": "Default",
    "description": "Default template for chat",
    "content": "...",
    "type": "chat",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "metadata": {},
    "tags": ["chat", "default"]
  },
  ...
]
```

### Template abrufen

```http
GET /api/v1/templates/{template_id}
```

Response:

```json
{
  "id": "default",
  "name": "Default",
  "description": "Default template for chat",
  "content": "...",
  "type": "chat",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "metadata": {},
  "tags": ["chat", "default"]
}
```

### Template erstellen

```http
POST /api/v1/templates
```

Request-Body:

```json
{
  "name": "Custom",
  "description": "Custom template for chat",
  "content": "...",
  "type": "chat",
  "metadata": {},
  "tags": ["chat", "custom"]
}
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Custom",
  "description": "Custom template for chat",
  "content": "...",
  "type": "chat",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "metadata": {},
  "tags": ["chat", "custom"]
}
```

### Template aktualisieren

```http
PUT /api/v1/templates/{template_id}
```

Request-Body:

```json
{
  "name": "Updated Custom",
  "description": "Updated custom template for chat",
  "content": "...",
  "type": "chat",
  "metadata": {},
  "tags": ["chat", "custom", "updated"]
}
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Updated Custom",
  "description": "Updated custom template for chat",
  "content": "...",
  "type": "chat",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "metadata": {},
  "tags": ["chat", "custom", "updated"]
}
```

### Template löschen

```http
DELETE /api/v1/templates/{template_id}
```

Response:

```json
{
  "success": true
}
```

### Template rendern

```http
POST /api/v1/templates/{template_id}/render
```

Request-Body:

```json
{
  "context": {
    "user_prompt": "Erkläre die Relativitätstheorie in einfachen Worten.",
    "prompt_type": "instruction",
    "domain": "general"
  }
}
```

Response:

```json
{
  "rendered_template": "..."
}
```