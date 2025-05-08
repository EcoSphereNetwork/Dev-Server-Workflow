"""
Chat API endpoints for the Prompt MCP Server.
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...core.llm_selector import LLMSelector
from ...core.memory_manager import MemoryManager
from ...core.template_manager import TemplateManager
from ...models.chat import ChatMessage, ChatResponse, ChatSession

# Create router
router = APIRouter()

# Create logger
logger = logging.getLogger(__name__)

# Create models
class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., description="The user message")
    session_id: Optional[str] = Field(None, description="The session ID")
    template_id: Optional[str] = Field(None, description="The template ID to use")
    model: Optional[str] = Field(None, description="The model to use")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the template")


# Create dependencies
def get_template_manager():
    """Get template manager dependency."""
    return TemplateManager()


def get_memory_manager():
    """Get memory manager dependency."""
    return MemoryManager()


def get_llm_selector():
    """Get LLM selector dependency."""
    return LLMSelector()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    template_manager: TemplateManager = Depends(get_template_manager),
    memory_manager: MemoryManager = Depends(get_memory_manager),
    llm_selector: LLMSelector = Depends(get_llm_selector),
) -> ChatResponse:
    """
    Chat endpoint.

    This endpoint processes a chat message and returns a response.
    """
    try:
        # Get or create session
        session = memory_manager.get_or_create_session(request.session_id)

        # Add user message to memory
        memory_manager.add_message(session.id, ChatMessage(role="user", content=request.message))

        # Get template if specified
        template = None
        if request.template_id:
            template = template_manager.get_template(request.template_id)
            if not template:
                raise HTTPException(status_code=404, detail=f"Template {request.template_id} not found")

        # Prepare context
        context = request.context or {}
        context["history"] = memory_manager.get_messages(session.id)
        if request.system_prompt:
            context["system_prompt"] = request.system_prompt

        # Select model based on complexity if not specified
        model = request.model
        if not model:
            complexity = llm_selector.analyze_complexity(request.message)
            model = llm_selector.select_model(complexity)

        # Generate response
        response_text = await llm_selector.generate(
            prompt=request.message,
            model=model,
            template=template,
            context=context,
        )

        # Add assistant message to memory
        memory_manager.add_message(session.id, ChatMessage(role="assistant", content=response_text))

        # Return response
        return ChatResponse(
            message=response_text,
            session_id=session.id,
            model=model,
        )

    except Exception as e:
        logger.exception(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[ChatSession])
async def list_sessions(
    memory_manager: MemoryManager = Depends(get_memory_manager),
) -> List[ChatSession]:
    """List all chat sessions."""
    return memory_manager.list_sessions()


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: str,
    memory_manager: MemoryManager = Depends(get_memory_manager),
) -> ChatSession:
    """Get a specific chat session."""
    session = memory_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session


@router.delete("/sessions/{session_id}", response_model=Dict[str, str])
async def delete_session(
    session_id: str,
    memory_manager: MemoryManager = Depends(get_memory_manager),
) -> Dict[str, str]:
    """Delete a chat session."""
    if not memory_manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return {"status": "success", "message": f"Session {session_id} deleted"}