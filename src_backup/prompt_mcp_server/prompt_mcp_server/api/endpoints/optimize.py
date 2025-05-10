"""
Optimierungs-API-Endpunkte für den Prompt MCP Server.
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...core.prompt_optimizer import PromptOptimizer
from ...core.template_manager import TemplateManager

# Erstelle Router
router = APIRouter()

# Erstelle Logger
logger = logging.getLogger(__name__)


# Erstelle Modelle
class OptimizePromptRequest(BaseModel):
    """Prompt-Optimierungs-Anfrage-Modell."""

    prompt: str = Field(..., description="Der zu optimierende Prompt")
    template_id: Optional[str] = Field(None, description="Die zu verwendende Template-ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Zusätzlicher Kontext für das Template")


class SystemPromptRequest(BaseModel):
    """System-Prompt-Anfrage-Modell."""

    prompt: str = Field(..., description="Der Benutzer-Prompt")
    role: Optional[str] = Field(None, description="Optionale Rolle für den Assistenten")
    style: Optional[str] = Field(None, description="Optionaler Stil für die Antwort")
    constraints: Optional[List[str]] = Field(None, description="Optionale Einschränkungen für die Antwort")


# Erstelle Abhängigkeiten
def get_prompt_optimizer(
    template_manager: TemplateManager = Depends(TemplateManager),
):
    """Hole Prompt-Optimierer-Abhängigkeit."""
    return PromptOptimizer(template_manager)


@router.post("/prompt", response_model=Dict[str, str])
async def optimize_prompt(
    request: OptimizePromptRequest,
    prompt_optimizer: PromptOptimizer = Depends(get_prompt_optimizer),
) -> Dict[str, str]:
    """
    Optimiere einen Benutzer-Prompt zu einem strukturierten Best-Practice-Prompt.

    Args:
        request: Die Prompt-Optimierungs-Anfrage

    Returns:
        Ein Dictionary mit dem optimierten Prompt
    """
    try:
        optimized_prompt = await prompt_optimizer.optimize_prompt(
            user_prompt=request.prompt,
            template_id=request.template_id,
            context=request.context,
        )
        return {"optimized_prompt": optimized_prompt}
    except Exception as e:
        logger.exception(f"Fehler bei der Prompt-Optimierung: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-prompt", response_model=Dict[str, str])
async def generate_system_prompt(
    request: SystemPromptRequest,
    prompt_optimizer: PromptOptimizer = Depends(get_prompt_optimizer),
) -> Dict[str, str]:
    """
    Generiere einen System-Prompt basierend auf Benutzer-Prompt und Parametern.

    Args:
        request: Die System-Prompt-Anfrage

    Returns:
        Ein Dictionary mit dem generierten System-Prompt
    """
    try:
        system_prompt = await prompt_optimizer.generate_system_prompt(
            user_prompt=request.prompt,
            role=request.role,
            style=request.style,
            constraints=request.constraints,
        )
        return {"system_prompt": system_prompt}
    except Exception as e:
        logger.exception(f"Fehler bei der System-Prompt-Generierung: {e}")
        raise HTTPException(status_code=500, detail=str(e))