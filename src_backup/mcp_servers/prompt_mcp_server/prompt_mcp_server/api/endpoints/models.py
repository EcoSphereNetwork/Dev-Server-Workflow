"""
Models API endpoints for the Prompt MCP Server.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...core.llm_selector import LLMSelector
from ...models.llm import LLMModel, ModelType

# Create router
router = APIRouter()

# Create logger
logger = logging.getLogger(__name__)


# Create dependencies
def get_llm_selector():
    """Get LLM selector dependency."""
    return LLMSelector()


@router.get("", response_model=List[LLMModel])
async def list_models(
    llm_selector: LLMSelector = Depends(get_llm_selector),
    model_type: Optional[ModelType] = None,
) -> List[LLMModel]:
    """
    List all available models.

    Args:
        model_type: Optional filter by model type (local or cloud)
    """
    return llm_selector.list_models(model_type=model_type)


@router.get("/{model_id}", response_model=LLMModel)
async def get_model(
    model_id: str,
    llm_selector: LLMSelector = Depends(get_llm_selector),
) -> LLMModel:
    """Get a specific model."""
    model = llm_selector.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return model


@router.post("/analyze", response_model=Dict[str, str])
async def analyze_complexity(
    request: Dict[str, str],
    llm_selector: LLMSelector = Depends(get_llm_selector),
) -> Dict[str, str]:
    """
    Analyze the complexity of a prompt.

    Args:
        request: A dictionary with a "prompt" key containing the text to analyze
    """
    if "prompt" not in request:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    complexity = llm_selector.analyze_complexity(request["prompt"])
    recommended_model = llm_selector.select_model(complexity)
    
    return {
        "complexity": complexity,
        "recommended_model": recommended_model,
    }