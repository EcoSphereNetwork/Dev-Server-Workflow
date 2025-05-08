"""
Analyse-API-Endpunkte für den LLM Cost Analyzer.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...core.llm_selector import LLMSelector

# Erstelle Router
router = APIRouter()

# Erstelle Logger
logger = logging.getLogger(__name__)


# Erstelle Modelle
class AnalyzeRequest(BaseModel):
    """Analyse-Anfrage-Modell."""

    prompt: str = Field(..., description="Der zu analysierende Prompt")


# Erstelle Abhängigkeiten
def get_llm_selector():
    """Hole LLM-Selektor-Abhängigkeit."""
    return LLMSelector()


@router.post("", response_model=Dict[str, Any])
async def analyze_complexity(
    request: AnalyzeRequest,
    llm_selector: LLMSelector = Depends(get_llm_selector),
) -> Dict[str, Any]:
    """
    Analysiere die Komplexität eines Prompts.

    Args:
        request: Die Analyse-Anfrage

    Returns:
        Ein Dictionary mit der Komplexitätsanalyse
    """
    try:
        complexity = llm_selector.analyze_complexity(request.prompt)
        recommended_model = llm_selector.select_model(complexity)
        
        return {
            "complexity": complexity,
            "recommended_model": recommended_model,
        }
    except Exception as e:
        logger.exception(f"Fehler bei der Komplexitätsanalyse: {e}")
        raise HTTPException(status_code=500, detail=str(e))