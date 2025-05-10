"""
LLM-Selektor für den LLM Cost Analyzer.

Dieses Modul bietet Funktionalität zur Auswahl des passenden LLMs basierend auf der Aufgabenkomplexität.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Union

from ..models.llm import LLMModel, ModelType, ComplexityLevel
from .config import settings

# Erstelle Logger
logger = logging.getLogger(__name__)


class LLMSelector:
    """LLM-Selektor-Klasse."""

    def __init__(self):
        """Initialisiere den LLM-Selektor."""
        self.models: Dict[str, LLMModel] = {}
        self._initialize_models()

    def _initialize_models(self) -> None:
        """Initialisiere verfügbare Modelle."""
        # Füge Cloud-Modelle hinzu
        if settings.OPENAI_API_KEY:
            self._add_openai_models()
        
        if settings.ANTHROPIC_API_KEY:
            self._add_anthropic_models()
        
        if settings.COHERE_API_KEY:
            self._add_cohere_models()
        
        # Füge lokale Modelle hinzu
        if settings.USE_LOCAL_MODELS:
            self._add_local_models()
        
        logger.info(f"{len(self.models)} Modelle initialisiert")

    def _add_openai_models(self) -> None:
        """Füge OpenAI-Modelle hinzu."""
        # GPT-3.5 Turbo
        self.models["gpt-3.5-turbo"] = LLMModel(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            provider="OpenAI",
            type=ModelType.CLOUD,
            context_length=16385,
            input_cost=0.5,  # $0.0005 pro 1K Tokens
            output_cost=1.5,  # $0.0015 pro 1K Tokens
            complexity_handling=7.5,
            quality_score=8.0,
            token_processing_speed=1000,
        )
        
        # GPT-4 Turbo
        self.models["gpt-4-turbo"] = LLMModel(
            id="gpt-4-turbo",
            name="GPT-4 Turbo",
            provider="OpenAI",
            type=ModelType.CLOUD,
            context_length=128000,
            input_cost=10.0,  # $0.01 pro 1K Tokens
            output_cost=30.0,  # $0.03 pro 1K Tokens
            complexity_handling=9.5,
            quality_score=9.5,
            token_processing_speed=800,
        )
        
        # GPT-4o
        self.models["gpt-4o"] = LLMModel(
            id="gpt-4o",
            name="GPT-4o",
            provider="OpenAI",
            type=ModelType.CLOUD,
            context_length=128000,
            input_cost=5.0,  # $0.005 pro 1K Tokens
            output_cost=15.0,  # $0.015 pro 1K Tokens
            complexity_handling=9.8,
            quality_score=9.8,
            token_processing_speed=900,
            multimodal_capable=True,
        )

    def _add_anthropic_models(self) -> None:
        """Füge Anthropic-Modelle hinzu."""
        # Claude 3 Haiku
        self.models["claude-3-haiku"] = LLMModel(
            id="claude-3-haiku",
            name="Claude 3 Haiku",
            provider="Anthropic",
            type=ModelType.CLOUD,
            context_length=200000,
            input_cost=0.25,  # $0.00025 pro 1K Tokens
            output_cost=1.25,  # $0.00125 pro 1K Tokens
            complexity_handling=7.0,
            quality_score=8.0,
            token_processing_speed=1200,
            multimodal_capable=True,
        )
        
        # Claude 3 Sonnet
        self.models["claude-3-sonnet"] = LLMModel(
            id="claude-3-sonnet",
            name="Claude 3 Sonnet",
            provider="Anthropic",
            type=ModelType.CLOUD,
            context_length=200000,
            input_cost=3.0,  # $0.003 pro 1K Tokens
            output_cost=15.0,  # $0.015 pro 1K Tokens
            complexity_handling=9.0,
            quality_score=9.2,
            token_processing_speed=1000,
            multimodal_capable=True,
        )
        
        # Claude 3 Opus
        self.models["claude-3-opus"] = LLMModel(
            id="claude-3-opus",
            name="Claude 3 Opus",
            provider="Anthropic",
            type=ModelType.CLOUD,
            context_length=200000,
            input_cost=15.0,  # $0.015 pro 1K Tokens
            output_cost=75.0,  # $0.075 pro 1K Tokens
            complexity_handling=9.9,
            quality_score=9.9,
            token_processing_speed=800,
            multimodal_capable=True,
        )

    def _add_cohere_models(self) -> None:
        """Füge Cohere-Modelle hinzu."""
        # Command R
        self.models["command-r"] = LLMModel(
            id="command-r",
            name="Command R",
            provider="Cohere",
            type=ModelType.CLOUD,
            context_length=128000,
            input_cost=1.0,  # $0.001 pro 1K Tokens
            output_cost=2.0,  # $0.002 pro 1K Tokens
            complexity_handling=8.0,
            quality_score=8.5,
            token_processing_speed=900,
        )
        
        # Command R+
        self.models["command-r-plus"] = LLMModel(
            id="command-r-plus",
            name="Command R+",
            provider="Cohere",
            type=ModelType.CLOUD,
            context_length=128000,
            input_cost=3.0,  # $0.003 pro 1K Tokens
            output_cost=15.0,  # $0.015 pro 1K Tokens
            complexity_handling=9.0,
            quality_score=9.0,
            token_processing_speed=850,
        )

    def _add_local_models(self) -> None:
        """Füge lokale Modelle hinzu."""
        # Füge Modelle aus den Einstellungen hinzu
        for model_name in settings.LOCAL_MODELS:
            model_id = f"local-{model_name}"
            self.models[model_id] = LLMModel(
                id=model_id,
                name=model_name,
                provider="Local",
                type=ModelType.LOCAL,
                context_length=8192,  # Standard-Kontextlänge
                input_cost=0.0,  # Lokale Modelle sind kostenlos
                output_cost=0.0,  # Lokale Modelle sind kostenlos
                complexity_handling=6.0,  # Standard-Komplexitätshandhabung
                quality_score=7.0,  # Standard-Qualitätswert
                token_processing_speed=500,  # Standard-Token-Verarbeitungsgeschwindigkeit
            )
        
        # Füge einige Standard-lokale Modelle hinzu, wenn keine angegeben sind
        if not settings.LOCAL_MODELS:
            # Llama 3 8B
            self.models["local-llama3-8b"] = LLMModel(
                id="local-llama3-8b",
                name="Llama 3 8B",
                provider="Local",
                type=ModelType.LOCAL,
                context_length=8192,
                input_cost=0.0,
                output_cost=0.0,
                complexity_handling=6.5,
                quality_score=7.5,
                token_processing_speed=600,
            )
            
            # Mistral 7B
            self.models["local-mistral-7b"] = LLMModel(
                id="local-mistral-7b",
                name="Mistral 7B",
                provider="Local",
                type=ModelType.LOCAL,
                context_length=8192,
                input_cost=0.0,
                output_cost=0.0,
                complexity_handling=6.0,
                quality_score=7.0,
                token_processing_speed=550,
            )

    def list_models(self, model_type: Optional[ModelType] = None) -> List[LLMModel]:
        """
        Liste alle verfügbaren Modelle auf.

        Args:
            model_type: Optionaler Filter nach Modelltyp (lokal oder Cloud)

        Returns:
            Liste von Modellen
        """
        if model_type:
            return [model for model in self.models.values() if model.type == model_type]
        return list(self.models.values())

    def get_model(self, model_id: str) -> Optional[LLMModel]:
        """
        Hole ein Modell anhand der ID.

        Args:
            model_id: Die Modell-ID

        Returns:
            Das Modell, wenn gefunden, sonst None
        """
        return self.models.get(model_id)

    def analyze_complexity(self, prompt: str) -> ComplexityLevel:
        """
        Analysiere die Komplexität eines Prompts.

        Args:
            prompt: Der zu analysierende Prompt

        Returns:
            Das Komplexitätslevel
        """
        # Berechne Komplexitätswert basierend auf verschiedenen Faktoren
        scores = {}
        
        # Längenwert
        length = len(prompt)
        if length < 100:
            scores["length"] = 1
        elif length < 500:
            scores["length"] = 2
        elif length < 1000:
            scores["length"] = 3
        elif length < 2000:
            scores["length"] = 4
        else:
            scores["length"] = 5
        
        # Token-Anzahl-Schätzung (grobe Annäherung)
        token_count = len(prompt.split())
        if token_count < 20:
            scores["tokens"] = 1
        elif token_count < 100:
            scores["tokens"] = 2
        elif token_count < 500:
            scores["tokens"] = 3
        elif token_count < 1000:
            scores["tokens"] = 4
        else:
            scores["tokens"] = 5
        
        # Reasoning-Komplexität
        reasoning_indicators = [
            r"why", r"how", r"explain", r"analyze", r"compare", r"contrast",
            r"evaluate", r"synthesize", r"critique", r"assess", r"reason"
        ]
        reasoning_score = 0
        for indicator in reasoning_indicators:
            if re.search(r"\b" + indicator + r"\b", prompt.lower()):
                reasoning_score += 1
        scores["reasoning"] = min(5, reasoning_score)
        
        # Kreativitäts-Komplexität
        creativity_indicators = [
            r"create", r"generate", r"design", r"imagine", r"story", r"creative",
            r"novel", r"unique", r"original", r"innovative", r"fiction"
        ]
        creativity_score = 0
        for indicator in creativity_indicators:
            if re.search(r"\b" + indicator + r"\b", prompt.lower()):
                creativity_score += 1
        scores["creativity"] = min(5, creativity_score)
        
        # Spezialisiertes Wissen-Komplexität
        specialized_indicators = [
            r"technical", r"scientific", r"medical", r"legal", r"financial",
            r"mathematical", r"code", r"programming", r"algorithm", r"physics",
            r"chemistry", r"biology", r"engineering", r"academic", r"research"
        ]
        specialized_score = 0
        for indicator in specialized_indicators:
            if re.search(r"\b" + indicator + r"\b", prompt.lower()):
                specialized_score += 1
        scores["specialized"] = min(5, specialized_score)
        
        # Berechne Gesamt-Komplexitätswert
        overall_score = (
            scores["length"] * 0.15 +
            scores["tokens"] * 0.15 +
            scores["reasoning"] * 0.3 +
            scores["creativity"] * 0.2 +
            scores["specialized"] * 0.2
        )
        
        # Ordne Gesamt-Wert einem Komplexitätslevel zu
        if overall_score < 1.5:
            return ComplexityLevel.VERY_SIMPLE
        elif overall_score < 2.5:
            return ComplexityLevel.SIMPLE
        elif overall_score < 3.5:
            return ComplexityLevel.MEDIUM
        elif overall_score < 4.0:
            return ComplexityLevel.COMPLEX
        elif overall_score < 4.5:
            return ComplexityLevel.VERY_COMPLEX
        else:
            return ComplexityLevel.EXTREMELY_COMPLEX

    def select_model(self, complexity: ComplexityLevel) -> str:
        """
        Wähle das passende Modell basierend auf der Komplexität.

        Args:
            complexity: Das Komplexitätslevel

        Returns:
            Die ausgewählte Modell-ID
        """
        # Definiere Modellauswahlstrategie basierend auf der Komplexität
        if complexity == ComplexityLevel.VERY_SIMPLE:
            # Für sehr einfache Aufgaben, verwende lokale Modelle, wenn verfügbar
            local_models = self.list_models(model_type=ModelType.LOCAL)
            if local_models:
                # Sortiere nach Qualitätswert und gib das beste zurück
                local_models.sort(key=lambda m: m.quality_score, reverse=True)
                return local_models[0].id
            # Fallback auf günstigstes Cloud-Modell
            return "gpt-3.5-turbo" if "gpt-3.5-turbo" in self.models else settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.SIMPLE:
            # Für einfache Aufgaben, verwende lokale Modelle, wenn verfügbar, sonst einfache Cloud-Modelle
            local_models = self.list_models(model_type=ModelType.LOCAL)
            if local_models:
                # Sortiere nach Qualitätswert und gib das beste zurück
                local_models.sort(key=lambda m: m.quality_score, reverse=True)
                return local_models[0].id
            # Verwende einfaches Cloud-Modell
            return "gpt-3.5-turbo" if "gpt-3.5-turbo" in self.models else settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.MEDIUM:
            # Für mittlere Komplexität, verwende gute Cloud-Modelle
            if "claude-3-haiku" in self.models:
                return "claude-3-haiku"
            if "gpt-3.5-turbo" in self.models:
                return "gpt-3.5-turbo"
            return settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.COMPLEX:
            # Für komplexe Aufgaben, verwende bessere Cloud-Modelle
            if "claude-3-sonnet" in self.models:
                return "claude-3-sonnet"
            if "gpt-4-turbo" in self.models:
                return "gpt-4-turbo"
            if "command-r-plus" in self.models:
                return "command-r-plus"
            return settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.VERY_COMPLEX:
            # Für sehr komplexe Aufgaben, verwende hochwertige Cloud-Modelle
            if "gpt-4o" in self.models:
                return "gpt-4o"
            if "claude-3-sonnet" in self.models:
                return "claude-3-sonnet"
            if "gpt-4-turbo" in self.models:
                return "gpt-4-turbo"
            return settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.EXTREMELY_COMPLEX:
            # Für extrem komplexe Aufgaben, verwende die besten verfügbaren Modelle
            if "claude-3-opus" in self.models:
                return "claude-3-opus"
            if "gpt-4o" in self.models:
                return "gpt-4o"
            if "gpt-4-turbo" in self.models:
                return "gpt-4-turbo"
            return settings.DEFAULT_MODEL
        
        # Standard-Fallback
        return settings.DEFAULT_MODEL