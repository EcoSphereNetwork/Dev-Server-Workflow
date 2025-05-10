"""
LLM models for the Prompt MCP Server.
"""

from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Model type enum."""

    LOCAL = "local"
    CLOUD = "cloud"


class ComplexityLevel(str, Enum):
    """Complexity level enum."""

    VERY_SIMPLE = "very_simple"
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"
    EXTREMELY_COMPLEX = "extremely_complex"


class LLMModel(BaseModel):
    """LLM model."""

    id: str = Field(..., description="The model ID")
    name: str = Field(..., description="The model name")
    provider: str = Field(..., description="The model provider")
    type: ModelType = Field(..., description="The model type (local or cloud)")
    context_length: int = Field(..., description="The maximum context length")
    input_cost: float = Field(..., description="The cost per 1M input tokens")
    output_cost: float = Field(..., description="The cost per 1M output tokens")
    complexity_handling: float = Field(..., description="The complexity handling score (1-10)")
    quality_score: float = Field(..., description="The quality score (1-10)")
    token_processing_speed: float = Field(..., description="The token processing speed (tokens/second)")
    multimodal_capable: bool = Field(default=False, description="Whether the model is multimodal capable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ComplexityAnalysis(BaseModel):
    """Complexity analysis result."""

    complexity: ComplexityLevel = Field(..., description="The complexity level")
    scores: Dict[str, int] = Field(..., description="The complexity scores")
    estimated_tokens: int = Field(..., description="The estimated token count")
    has_reasoning: bool = Field(..., description="Whether the task requires reasoning")
    has_creativity: bool = Field(..., description="Whether the task requires creativity")
    has_specialization: bool = Field(..., description="Whether the task requires specialization")