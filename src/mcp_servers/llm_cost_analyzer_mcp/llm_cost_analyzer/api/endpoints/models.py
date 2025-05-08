"""
Modell-API-Endpunkte für den LLM Cost Analyzer.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.llm_selector import LLMSelector
from ...models.llm import LLMModel, ModelType

# Erstelle Router
router = APIRouter()

# Erstelle Logger
logger = logging.getLogger(__name__)


# Erstelle Abhängigkeiten
def get_llm_selector():
    """Hole LLM-Selektor-Abhängigkeit."""
    return LLMSelector()


@router.get("", response_model=List[LLMModel])
async def list_models(
    llm_selector: LLMSelector = Depends(get_llm_selector),
    model_type: Optional[ModelType] = None,
) -> List[LLMModel]:
    """
    Liste alle verfügbaren Modelle auf.

    Args:
        model_type: Optionaler Filter nach Modelltyp (lokal oder Cloud)

    Returns:
        Liste von Modellen
    """
    return llm_selector.list_models(model_type=model_type)


@router.get("/{model_id}", response_model=LLMModel)
async def get_model(
    model_id: str,
    llm_selector: LLMSelector = Depends(get_llm_selector),
) -> LLMModel:
    """
    Hole ein bestimmtes Modell.

    Args:
        model_id: Die Modell-ID

    Returns:
        Das Modell
    """
    model = llm_selector.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Modell {model_id} nicht gefunden")
    return model