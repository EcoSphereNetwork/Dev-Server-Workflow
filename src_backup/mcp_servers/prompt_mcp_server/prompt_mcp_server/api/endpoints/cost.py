"""
Cost API endpoints for the Prompt MCP Server.
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...core.llm_selector import LLMSelector
from ...core.task_cost_estimator import TaskCostEstimator
from ...core.template_manager import TemplateManager

# Create router
router = APIRouter()

# Create logger
logger = logging.getLogger(__name__)


# Create models
class CostEstimationRequest(BaseModel):
    """Cost estimation request model."""

    prompt: str = Field(..., description="The prompt to estimate cost for")
    model_ids: Optional[List[str]] = Field(None, description="Optional list of model IDs to estimate cost for")
    expected_output_length: Optional[int] = Field(None, description="Optional expected output length in characters")


# Create dependencies
def get_task_cost_estimator(
    llm_selector: LLMSelector = Depends(LLMSelector),
    template_manager: TemplateManager = Depends(TemplateManager),
):
    """Get task cost estimator dependency."""
    return TaskCostEstimator(llm_selector, template_manager)


@router.post("/estimate", response_model=Dict[str, Any])
async def estimate_cost(
    request: CostEstimationRequest,
    task_cost_estimator: TaskCostEstimator = Depends(get_task_cost_estimator),
) -> Dict[str, Any]:
    """
    Estimate the cost of processing a prompt with different models.

    Args:
        request: The cost estimation request

    Returns:
        A dictionary with cost estimates
    """
    try:
        return await task_cost_estimator.estimate_cost(
            prompt=request.prompt,
            model_ids=request.model_ids,
            expected_output_length=request.expected_output_length,
        )
    except Exception as e:
        logger.exception(f"Error estimating cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report", response_model=Dict[str, str])
async def generate_cost_report(
    request: CostEstimationRequest,
    task_cost_estimator: TaskCostEstimator = Depends(get_task_cost_estimator),
) -> Dict[str, str]:
    """
    Generate a human-readable cost report.

    Args:
        request: The cost estimation request

    Returns:
        A dictionary with the cost report
    """
    try:
        report = await task_cost_estimator.generate_cost_report(
            prompt=request.prompt,
            model_ids=request.model_ids,
            expected_output_length=request.expected_output_length,
        )
        return {"report": report}
    except Exception as e:
        logger.exception(f"Error generating cost report: {e}")
        raise HTTPException(status_code=500, detail=str(e))