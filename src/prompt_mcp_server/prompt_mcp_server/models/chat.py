"""
Chat models for the Prompt MCP Server.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="The role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="The timestamp of the message")


class ChatSession(BaseModel):
    """Chat session model."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="The session ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="The creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="The last update timestamp")
    messages: List[ChatMessage] = Field(default_factory=list, description="The messages in the session")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ChatResponse(BaseModel):
    """Chat response model."""

    message: str = Field(..., description="The assistant's response")
    session_id: str = Field(..., description="The session ID")
    model: str = Field(..., description="The model used for generation")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="The timestamp of the response")