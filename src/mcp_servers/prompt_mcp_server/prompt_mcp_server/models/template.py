"""
Template models for the Prompt MCP Server.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class TemplateType(str, Enum):
    """Template type enum."""

    CHAT = "chat"
    COMPLETION = "completion"
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    CUSTOM = "custom"


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


class TemplateCreate(BaseModel):
    """Template creation model."""

    name: str = Field(..., description="The template name")
    description: Optional[str] = Field(None, description="The template description")
    content: str = Field(..., description="The template content")
    type: TemplateType = Field(default=TemplateType.CHAT, description="The template type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(None, description="Tags for the template")


class TemplateUpdate(BaseModel):
    """Template update model."""

    name: Optional[str] = Field(None, description="The template name")
    description: Optional[str] = Field(None, description="The template description")
    content: Optional[str] = Field(None, description="The template content")
    type: Optional[TemplateType] = Field(None, description="The template type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tags: Optional[List[str]] = Field(None, description="Tags for the template")