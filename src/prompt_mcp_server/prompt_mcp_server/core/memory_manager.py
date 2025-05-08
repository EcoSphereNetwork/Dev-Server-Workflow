"""
Memory manager for the Prompt MCP Server.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from ..models.chat import ChatMessage, ChatSession
from .config import settings

# Create logger
logger = logging.getLogger(__name__)


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

    def _init_in_memory(self) -> None:
        """Initialize in-memory storage."""
        logger.info("Initializing in-memory storage")
        # Nothing to do, sessions are already initialized

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

    def _save_session(self, session: ChatSession) -> None:
        """
        Save a session to the storage backend.

        Args:
            session: The session to save
        """
        try:
            if self.memory_type == "redis":
                self.redis.set(f"session:{session.id}", session.model_dump_json())
            
            elif self.memory_type == "chroma":
                # Update or create document in Chroma
                session_data = session.model_dump_json()
                self.chroma_collection.upsert(
                    ids=[session.id],
                    metadatas=[{"session_data": session_data}],
                    documents=[session_data]  # Store the session data as a document for potential semantic search
                )
            
            # For in-memory, no need to do anything as the session is already in self.sessions
        
        except Exception as e:
            logger.exception(f"Error saving session {session.id}: {e}")

    def list_sessions(self) -> List[ChatSession]:
        """
        List all sessions.

        Returns:
            List of sessions
        """
        return list(self.sessions.values())

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Get a session by ID.

        Args:
            session_id: The session ID

        Returns:
            The session if found, None otherwise
        """
        return self.sessions.get(session_id)

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