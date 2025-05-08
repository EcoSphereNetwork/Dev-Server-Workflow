"""
Schätzungs-API-Endpunkte für den LLM Cost Analyzer.
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...core.llm_selector import LLMSelector
from ...core.task_cost_estimator import TaskCostEstimator

# Erstelle Router
router = APIRouter()

# Erstelle Logger
logger = logging.getLogger(__name__)


# Erstelle Modelle
class CostEstimationRequest(BaseModel):
    """Kostenschätzungs-Anfrage-Modell."""

    prompt: str = Field(..., description="Der Prompt, für den die Kosten geschätzt werden sollen")
    model_ids: Optional[List[str]] = Field(None, description="Optionale Liste von Modell-IDs, für die die Kosten geschätzt werden sollen")
    expected_output_length: Optional[int] = Field(None, description="Optionale erwartete Ausgabelänge in Zeichen")


# Erstelle Abhängigkeiten
def get_task_cost_estimator(
    llm_selector: LLMSelector = Depends(LLMSelector),
):
    """Hole Aufgabenkostenrechner-Abhängigkeit."""
    return TaskCostEstimator(llm_selector)


@router.post("/cost", response_model=Dict[str, Any])
async def estimate_cost(
    request: CostEstimationRequest,
    task_cost_estimator: TaskCostEstimator = Depends(get_task_cost_estimator),
) -> Dict[str, Any]:
    """
    Schätze die Kosten für die Verarbeitung eines Prompts mit verschiedenen Modellen.

    Args:
        request: Die Kostenschätzungs-Anfrage

    Returns:
        Ein Dictionary mit Kostenschätzungen
    """
    try:
        return await task_cost_estimator.estimate_cost(
            prompt=request.prompt,
            model_ids=request.model_ids,
            expected_output_length=request.expected_output_length,
        )
    except Exception as e:
        logger.exception(f"Fehler bei der Kostenschätzung: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report", response_model=Dict[str, str])
async def generate_cost_report(
    request: CostEstimationRequest,
    task_cost_estimator: TaskCostEstimator = Depends(get_task_cost_estimator),
) -> Dict[str, str]:
    """
    Generiere einen menschenlesbaren Kostenbericht.

    Args:
        request: Die Kostenschätzungs-Anfrage

    Returns:
        Ein Dictionary mit dem Kostenbericht
    """
    try:
        report = await task_cost_estimator.generate_cost_report(
            prompt=request.prompt,
            model_ids=request.model_ids,
            expected_output_length=request.expected_output_length,
        )
        return {"report": report}
    except Exception as e:
        logger.exception(f"Fehler bei der Generierung des Kostenberichts: {e}")
        raise HTTPException(status_code=500, detail=str(e))