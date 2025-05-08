"""
LLM-Modelle für den LLM Cost Analyzer.
"""

from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Modelltyp-Enum."""

    LOCAL = "local"
    CLOUD = "cloud"


class ComplexityLevel(str, Enum):
    """Komplexitätslevel-Enum."""

    VERY_SIMPLE = "very_simple"
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"
    EXTREMELY_COMPLEX = "extremely_complex"


class LLMModel(BaseModel):
    """LLM-Modell."""

    id: str = Field(..., description="Die Modell-ID")
    name: str = Field(..., description="Der Modellname")
    provider: str = Field(..., description="Der Modellanbieter")
    type: ModelType = Field(..., description="Der Modelltyp (lokal oder Cloud)")
    context_length: int = Field(..., description="Die maximale Kontextlänge")
    input_cost: float = Field(..., description="Die Kosten pro 1M Input-Tokens")
    output_cost: float = Field(..., description="Die Kosten pro 1M Output-Tokens")
    complexity_handling: float = Field(..., description="Der Komplexitätshandhabungswert (1-10)")
    quality_score: float = Field(..., description="Der Qualitätswert (1-10)")
    token_processing_speed: float = Field(..., description="Die Token-Verarbeitungsgeschwindigkeit (Tokens/Sekunde)")
    multimodal_capable: bool = Field(default=False, description="Ob das Modell multimodale Fähigkeiten hat")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Zusätzliche Metadaten")


class ComplexityAnalysis(BaseModel):
    """Komplexitätsanalyse-Ergebnis."""

    complexity: ComplexityLevel = Field(..., description="Das Komplexitätslevel")
    scores: Dict[str, int] = Field(..., description="Die Komplexitätswerte")
    estimated_tokens: int = Field(..., description="Die geschätzte Token-Anzahl")
    has_reasoning: bool = Field(..., description="Ob die Aufgabe Reasoning erfordert")
    has_creativity: bool = Field(..., description="Ob die Aufgabe Kreativität erfordert")
    has_specialization: bool = Field(..., description="Ob die Aufgabe Spezialisierung erfordert")