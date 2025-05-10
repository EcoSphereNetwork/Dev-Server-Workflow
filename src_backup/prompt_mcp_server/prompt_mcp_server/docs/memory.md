# Memory

Das Memory-Modul ist verantwortlich für die Verwaltung des Konversationsverlaufs und des Kontexts. Es bietet Funktionalität zum Speichern und Abrufen von Chat-Sitzungen und Nachrichten.

## Memory-Manager

Der Memory-Manager ist die Hauptklasse des Memory-Moduls. Er bietet folgende Funktionen:

1. **Sitzungsverwaltung**: Erstellen, Abrufen, Aktualisieren und Löschen von Chat-Sitzungen
2. **Nachrichtenverwaltung**: Hinzufügen und Abrufen von Nachrichten in einer Sitzung
3. **Storage-Backend**: Unterstützung verschiedener Storage-Backends (in-memory, Redis, Chroma)

```python
class MemoryManager:
    """Memory manager class."""

    def __init__(self):
        """Initialize the memory manager."""
        self.memory_type = settings.MEMORY_TYPE
        self.sessions: Dict[str, ChatSession] = {}
        
        # Initialize memory backend
        if self.memory_type == "redis":
            self._init_redis()
        elif self.memory_type == "chroma":
            self._init_chroma()
        else:
            # Default to in-memory
            self._init_in_memory()
```

## Chat-Modelle

Das Memory-Modul definiert folgende Modelle:

### Chat-Nachricht

```python
class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="The role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="The timestamp of the message")
```

### Chat-Sitzung

```python
class ChatSession(BaseModel):
    """Chat session model."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="The session ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="The creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="The last update timestamp")
    messages: List[ChatMessage] = Field(default_factory=list, description="The messages in the session")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
```

## Storage-Backends

Der Memory-Manager unterstützt verschiedene Storage-Backends:

### In-Memory

Das In-Memory-Backend speichert Sitzungen im Arbeitsspeicher. Es ist einfach und schnell, aber nicht persistent.

```python
def _init_in_memory(self) -> None:
    """Initialize in-memory storage."""
    logger.info("Initializing in-memory storage")
    # Nothing to do, sessions are already initialized
```

### Redis

Das Redis-Backend speichert Sitzungen in einer Redis-Datenbank. Es ist persistent und skalierbar.

```python
def _init_redis(self) -> None:
    """Initialize Redis storage."""
    try:
        import redis
        from redis.exceptions import RedisError

        if not settings.REDIS_URL:
            raise ValueError("REDIS_URL is required for Redis memory type")
        
        logger.info(f"Connecting to Redis at {settings.REDIS_URL}")
        self.redis = redis.from_url(settings.REDIS_URL)
        
        # Load sessions from Redis
        try:
            session_keys = self.redis.keys("session:*")
            for key in session_keys:
                session_data = self.redis.get(key)
                if session_data:
                    session = ChatSession.model_validate_json(session_data)
                    self.sessions[session.id] = session
            logger.info(f"Loaded {len(self.sessions)} sessions from Redis")
        except RedisError as e:
            logger.error(f"Error loading sessions from Redis: {e}")
    
    except ImportError:
        logger.error("Redis package not installed. Falling back to in-memory storage.")
        self.memory_type = "in_memory"
        self._init_in_memory()
    
    except Exception as e:
        logger.exception(f"Error initializing Redis: {e}")
        logger.warning("Falling back to in-memory storage")
        self.memory_type = "in_memory"
        self._init_in_memory()
```

### Chroma

Das Chroma-Backend speichert Sitzungen in einer Chroma-Datenbank. Es unterstützt semantische Suche.

```python
def _init_chroma(self) -> None:
    """Initialize Chroma storage."""
    try:
        import chromadb
        from chromadb.config import Settings

        logger.info("Initializing Chroma storage")
        persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        
        if persist_directory:
            self.chroma_client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        
        # Create or get collection
        self.chroma_collection = self.chroma_client.get_or_create_collection("chat_sessions")
        
        # Load sessions from Chroma
        try:
            results = self.chroma_collection.get()
            for i, session_id in enumerate(results.get("ids", [])):
                metadata = results.get("metadatas", [])[i]
                if metadata and "session_data" in metadata:
                    session = ChatSession.model_validate_json(metadata["session_data"])
                    self.sessions[session.id] = session
            logger.info(f"Loaded {len(self.sessions)} sessions from Chroma")
        except Exception as e:
            logger.error(f"Error loading sessions from Chroma: {e}")
    
    except ImportError:
        logger.error("Chroma package not installed. Falling back to in-memory storage.")
        self.memory_type = "in_memory"
        self._init_in_memory()
    
    except Exception as e:
        logger.exception(f"Error initializing Chroma: {e}")
        logger.warning("Falling back to in-memory storage")
        self.memory_type = "in_memory"
        self._init_in_memory()
```

## Sitzungsverwaltung

Der Memory-Manager bietet folgende Funktionen zur Sitzungsverwaltung:

### Sitzungen auflisten

```python
def list_sessions(self) -> List[ChatSession]:
    """
    List all sessions.

    Returns:
        List of sessions
    """
    return list(self.sessions.values())
```

### Sitzung abrufen

```python
def get_session(self, session_id: str) -> Optional[ChatSession]:
    """
    Get a session by ID.

    Args:
        session_id: The session ID

    Returns:
        The session if found, None otherwise
    """
    return self.sessions.get(session_id)
```

### Sitzung erstellen oder abrufen

```python
def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
    """
    Get a session by ID or create a new one.

    Args:
        session_id: The session ID (optional)

    Returns:
        The session
    """
    if session_id and session_id in self.sessions:
        return self.sessions[session_id]
    
    # Create new session
    session = ChatSession(id=session_id or str(uuid4()))
    self.sessions[session.id] = session
    self._save_session(session)
    
    return session
```

### Sitzung löschen

```python
def delete_session(self, session_id: str) -> bool:
    """
    Delete a session.

    Args:
        session_id: The session ID

    Returns:
        True if the session was deleted, False otherwise
    """
    if session_id not in self.sessions:
        return False
    
    # Delete session
    del self.sessions[session_id]
    
    # Delete from storage backend
    try:
        if self.memory_type == "redis":
            self.redis.delete(f"session:{session_id}")
        
        elif self.memory_type == "chroma":
            self.chroma_collection.delete(ids=[session_id])
    
    except Exception as e:
        logger.exception(f"Error deleting session {session_id}: {e}")
    
    return True
```

## Nachrichtenverwaltung

Der Memory-Manager bietet folgende Funktionen zur Nachrichtenverwaltung:

### Nachrichten abrufen

```python
def get_messages(self, session_id: str) -> List[ChatMessage]:
    """
    Get all messages for a session.

    Args:
        session_id: The session ID

    Returns:
        List of messages
    """
    session = self.get_session(session_id)
    if not session:
        return []
    
    return session.messages
```

### Nachricht hinzufügen

```python
def add_message(self, session_id: str, message: ChatMessage) -> None:
    """
    Add a message to a session.

    Args:
        session_id: The session ID
        message: The message to add
    """
    session = self.get_or_create_session(session_id)
    session.messages.append(message)
    session.updated_at = datetime.utcnow()
    self._save_session(session)
```

### Nachrichten löschen

```python
def clear_messages(self, session_id: str) -> bool:
    """
    Clear all messages for a session.

    Args:
        session_id: The session ID

    Returns:
        True if the messages were cleared, False otherwise
    """
    session = self.get_session(session_id)
    if not session:
        return False
    
    session.messages = []
    session.updated_at = datetime.utcnow()
    self._save_session(session)
    
    return True
```

## API-Endpunkte

Das Memory-Modul stellt folgende API-Endpunkte bereit:

### Sitzungen auflisten

```http
GET /api/v1/chat/sessions
```

Response:

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "messages": [
      {
        "role": "user",
        "content": "Hallo!",
        "timestamp": "2023-01-01T00:00:00Z"
      },
      {
        "role": "assistant",
        "content": "Hallo! Wie kann ich dir helfen?",
        "timestamp": "2023-01-01T00:00:00Z"
      }
    ],
    "metadata": {}
  },
  ...
]
```

### Sitzung abrufen

```http
GET /api/v1/chat/sessions/{session_id}
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Hallo!",
      "timestamp": "2023-01-01T00:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hallo! Wie kann ich dir helfen?",
      "timestamp": "2023-01-01T00:00:00Z"
    }
  ],
  "metadata": {}
}
```

### Sitzung erstellen

```http
POST /api/v1/chat/sessions
```

Request-Body:

```json
{
  "metadata": {
    "user_id": "123",
    "source": "web"
  }
}
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "messages": [],
  "metadata": {
    "user_id": "123",
    "source": "web"
  }
}
```

### Sitzung löschen

```http
DELETE /api/v1/chat/sessions/{session_id}
```

Response:

```json
{
  "success": true
}
```

### Nachrichten abrufen

```http
GET /api/v1/chat/sessions/{session_id}/messages
```

Response:

```json
[
  {
    "role": "user",
    "content": "Hallo!",
    "timestamp": "2023-01-01T00:00:00Z"
  },
  {
    "role": "assistant",
    "content": "Hallo! Wie kann ich dir helfen?",
    "timestamp": "2023-01-01T00:00:00Z"
  }
]
```

### Nachricht hinzufügen

```http
POST /api/v1/chat/sessions/{session_id}/messages
```

Request-Body:

```json
{
  "role": "user",
  "content": "Wie geht es dir?"
}
```

Response:

```json
{
  "role": "user",
  "content": "Wie geht es dir?",
  "timestamp": "2023-01-01T00:00:00Z"
}
```

### Nachrichten löschen

```http
DELETE /api/v1/chat/sessions/{session_id}/messages
```

Response:

```json
{
  "success": true
}
```