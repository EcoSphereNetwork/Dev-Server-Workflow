"""
LLM selector for the Prompt MCP Server.

This module provides functionality to select the appropriate LLM based on task complexity.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Union

from ..models.llm import LLMModel, ModelType, ComplexityLevel
from ..models.template import Template
from .config import settings

# Create logger
logger = logging.getLogger(__name__)


class LLMSelector:
    """LLM selector class."""

    def __init__(self):
        """Initialize the LLM selector."""
        self.models: Dict[str, LLMModel] = {}
        self._initialize_models()

    def _initialize_models(self) -> None:
        """Initialize available models."""
        # Add cloud models
        if settings.OPENAI_API_KEY:
            self._add_openai_models()
        
        if settings.ANTHROPIC_API_KEY:
            self._add_anthropic_models()
        
        if settings.COHERE_API_KEY:
            self._add_cohere_models()
        
        # Add local models
        if settings.USE_LOCAL_MODELS:
            self._add_local_models()
        
        logger.info(f"Initialized {len(self.models)} models")

    def _add_openai_models(self) -> None:
        """Add OpenAI models."""
        # GPT-3.5 Turbo
        self.models["gpt-3.5-turbo"] = LLMModel(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            provider="OpenAI",
            type=ModelType.CLOUD,
            context_length=16385,
            input_cost=0.5,  # $0.0005 per 1K tokens
            output_cost=1.5,  # $0.0015 per 1K tokens
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
            input_cost=10.0,  # $0.01 per 1K tokens
            output_cost=30.0,  # $0.03 per 1K tokens
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
            input_cost=5.0,  # $0.005 per 1K tokens
            output_cost=15.0,  # $0.015 per 1K tokens
            complexity_handling=9.8,
            quality_score=9.8,
            token_processing_speed=900,
            multimodal_capable=True,
        )

    def _add_anthropic_models(self) -> None:
        """Add Anthropic models."""
        # Claude 3 Haiku
        self.models["claude-3-haiku"] = LLMModel(
            id="claude-3-haiku",
            name="Claude 3 Haiku",
            provider="Anthropic",
            type=ModelType.CLOUD,
            context_length=200000,
            input_cost=0.25,  # $0.00025 per 1K tokens
            output_cost=1.25,  # $0.00125 per 1K tokens
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
            input_cost=3.0,  # $0.003 per 1K tokens
            output_cost=15.0,  # $0.015 per 1K tokens
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
            input_cost=15.0,  # $0.015 per 1K tokens
            output_cost=75.0,  # $0.075 per 1K tokens
            complexity_handling=9.9,
            quality_score=9.9,
            token_processing_speed=800,
            multimodal_capable=True,
        )

    def _add_cohere_models(self) -> None:
        """Add Cohere models."""
        # Command R
        self.models["command-r"] = LLMModel(
            id="command-r",
            name="Command R",
            provider="Cohere",
            type=ModelType.CLOUD,
            context_length=128000,
            input_cost=1.0,  # $0.001 per 1K tokens
            output_cost=2.0,  # $0.002 per 1K tokens
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
            input_cost=3.0,  # $0.003 per 1K tokens
            output_cost=15.0,  # $0.015 per 1K tokens
            complexity_handling=9.0,
            quality_score=9.0,
            token_processing_speed=850,
        )

    def _add_local_models(self) -> None:
        """Add local models."""
        # Add models from settings
        for model_name in settings.LOCAL_MODELS:
            model_id = f"local-{model_name}"
            self.models[model_id] = LLMModel(
                id=model_id,
                name=model_name,
                provider="Local",
                type=ModelType.LOCAL,
                context_length=8192,  # Default context length
                input_cost=0.0,  # Local models are free
                output_cost=0.0,  # Local models are free
                complexity_handling=6.0,  # Default complexity handling
                quality_score=7.0,  # Default quality score
                token_processing_speed=500,  # Default token processing speed
            )
        
        # Add some default local models if none are specified
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
        List all available models.

        Args:
            model_type: Optional filter by model type (local or cloud)

        Returns:
            List of models
        """
        if model_type:
            return [model for model in self.models.values() if model.type == model_type]
        return list(self.models.values())

    def get_model(self, model_id: str) -> Optional[LLMModel]:
        """
        Get a model by ID.

        Args:
            model_id: The model ID

        Returns:
            The model if found, None otherwise
        """
        return self.models.get(model_id)

    def analyze_complexity(self, prompt: str) -> ComplexityLevel:
        """
        Analyze the complexity of a prompt.

        Args:
            prompt: The prompt to analyze

        Returns:
            The complexity level
        """
        # Calculate complexity score based on various factors
        scores = {}
        
        # Length score
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
        
        # Token count estimation (rough approximation)
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
        
        # Reasoning complexity
        reasoning_indicators = [
            r"why", r"how", r"explain", r"analyze", r"compare", r"contrast",
            r"evaluate", r"synthesize", r"critique", r"assess", r"reason"
        ]
        reasoning_score = 0
        for indicator in reasoning_indicators:
            if re.search(r"\b" + indicator + r"\b", prompt.lower()):
                reasoning_score += 1
        scores["reasoning"] = min(5, reasoning_score)
        
        # Creativity complexity
        creativity_indicators = [
            r"create", r"generate", r"design", r"imagine", r"story", r"creative",
            r"novel", r"unique", r"original", r"innovative", r"fiction"
        ]
        creativity_score = 0
        for indicator in creativity_indicators:
            if re.search(r"\b" + indicator + r"\b", prompt.lower()):
                creativity_score += 1
        scores["creativity"] = min(5, creativity_score)
        
        # Specialized knowledge complexity
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
        
        # Calculate overall complexity score
        overall_score = (
            scores["length"] * 0.15 +
            scores["tokens"] * 0.15 +
            scores["reasoning"] * 0.3 +
            scores["creativity"] * 0.2 +
            scores["specialized"] * 0.2
        )
        
        # Map overall score to complexity level
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
        Select the appropriate model based on complexity.

        Args:
            complexity: The complexity level

        Returns:
            The selected model ID
        """
        # Define model selection strategy based on complexity
        if complexity == ComplexityLevel.VERY_SIMPLE:
            # For very simple tasks, use local models if available
            local_models = self.list_models(model_type=ModelType.LOCAL)
            if local_models:
                # Sort by quality score and return the best one
                local_models.sort(key=lambda m: m.quality_score, reverse=True)
                return local_models[0].id
            # Fall back to cheapest cloud model
            return "gpt-3.5-turbo" if "gpt-3.5-turbo" in self.models else settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.SIMPLE:
            # For simple tasks, use local models if available, otherwise use basic cloud models
            local_models = self.list_models(model_type=ModelType.LOCAL)
            if local_models:
                # Sort by quality score and return the best one
                local_models.sort(key=lambda m: m.quality_score, reverse=True)
                return local_models[0].id
            # Use basic cloud model
            return "gpt-3.5-turbo" if "gpt-3.5-turbo" in self.models else settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.MEDIUM:
            # For medium complexity, use good cloud models
            if "claude-3-haiku" in self.models:
                return "claude-3-haiku"
            if "gpt-3.5-turbo" in self.models:
                return "gpt-3.5-turbo"
            return settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.COMPLEX:
            # For complex tasks, use better cloud models
            if "claude-3-sonnet" in self.models:
                return "claude-3-sonnet"
            if "gpt-4-turbo" in self.models:
                return "gpt-4-turbo"
            if "command-r-plus" in self.models:
                return "command-r-plus"
            return settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.VERY_COMPLEX:
            # For very complex tasks, use high-quality cloud models
            if "gpt-4o" in self.models:
                return "gpt-4o"
            if "claude-3-sonnet" in self.models:
                return "claude-3-sonnet"
            if "gpt-4-turbo" in self.models:
                return "gpt-4-turbo"
            return settings.DEFAULT_MODEL
        
        elif complexity == ComplexityLevel.EXTREMELY_COMPLEX:
            # For extremely complex tasks, use the best available models
            if "claude-3-opus" in self.models:
                return "claude-3-opus"
            if "gpt-4o" in self.models:
                return "gpt-4o"
            if "gpt-4-turbo" in self.models:
                return "gpt-4-turbo"
            return settings.DEFAULT_MODEL
        
        # Default fallback
        return settings.DEFAULT_MODEL

    async def generate(
        self,
        prompt: str,
        model: str,
        template: Optional[Template] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a response using the specified model.

        Args:
            prompt: The prompt to generate from
            model: The model ID to use
            template: Optional template to use
            context: Optional context for the template

        Returns:
            The generated response
        """
        try:
            # Get model
            model_info = self.get_model(model)
            if not model_info:
                logger.warning(f"Model {model} not found, using default model")
                model = settings.DEFAULT_MODEL
                model_info = self.get_model(model)
            
            # Prepare context
            ctx = context or {}
            ctx["prompt"] = prompt
            
            # Use appropriate client based on model provider
            if model_info.provider == "OpenAI":
                return await self._generate_openai(model, prompt, template, ctx)
            elif model_info.provider == "Anthropic":
                return await self._generate_anthropic(model, prompt, template, ctx)
            elif model_info.provider == "Cohere":
                return await self._generate_cohere(model, prompt, template, ctx)
            elif model_info.provider == "Local":
                return await self._generate_local(model, prompt, template, ctx)
            else:
                raise ValueError(f"Unsupported model provider: {model_info.provider}")
        
        except Exception as e:
            logger.exception(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"

    async def _generate_openai(
        self,
        model: str,
        prompt: str,
        template: Optional[Template],
        context: Dict[str, Any],
    ) -> str:
        """Generate a response using OpenAI."""
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            # Initialize client
            client = ChatOpenAI(
                model=model,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.7,
            )
            
            # Prepare messages
            messages = []
            
            # Add system message if provided
            if "system_prompt" in context:
                messages.append(SystemMessage(content=context["system_prompt"]))
            
            # Add history if provided
            if "history" in context:
                for msg in context["history"]:
                    if msg.role == "user":
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        messages.append(SystemMessage(content=msg.content))
                    elif msg.role == "system":
                        messages.append(SystemMessage(content=msg.content))
            
            # Add current prompt
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            response = await client.ainvoke(messages)
            return response.content
        
        except ImportError:
            logger.error("langchain_openai package not installed")
            return "Error: OpenAI integration not available"
        
        except Exception as e:
            logger.exception(f"Error generating OpenAI response: {e}")
            return f"Error generating response: {str(e)}"

    async def _generate_anthropic(
        self,
        model: str,
        prompt: str,
        template: Optional[Template],
        context: Dict[str, Any],
    ) -> str:
        """Generate a response using Anthropic."""
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain.schema import HumanMessage, SystemMessage
            
            # Initialize client
            client = ChatAnthropic(
                model=model,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.7,
            )
            
            # Prepare messages
            messages = []
            
            # Add system message if provided
            if "system_prompt" in context:
                messages.append(SystemMessage(content=context["system_prompt"]))
            
            # Add history if provided
            if "history" in context:
                for msg in context["history"]:
                    if msg.role == "user":
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        messages.append(SystemMessage(content=msg.content))
                    elif msg.role == "system":
                        messages.append(SystemMessage(content=msg.content))
            
            # Add current prompt
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            response = await client.ainvoke(messages)
            return response.content
        
        except ImportError:
            logger.error("langchain_anthropic package not installed")
            return "Error: Anthropic integration not available"
        
        except Exception as e:
            logger.exception(f"Error generating Anthropic response: {e}")
            return f"Error generating response: {str(e)}"

    async def _generate_cohere(
        self,
        model: str,
        prompt: str,
        template: Optional[Template],
        context: Dict[str, Any],
    ) -> str:
        """Generate a response using Cohere."""
        try:
            from langchain_community.chat_models import ChatCohere
            from langchain.schema import HumanMessage, SystemMessage
            
            # Initialize client
            client = ChatCohere(
                model=model,
                cohere_api_key=settings.COHERE_API_KEY,
                temperature=0.7,
            )
            
            # Prepare messages
            messages = []
            
            # Add system message if provided
            if "system_prompt" in context:
                messages.append(SystemMessage(content=context["system_prompt"]))
            
            # Add history if provided
            if "history" in context:
                for msg in context["history"]:
                    if msg.role == "user":
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        messages.append(SystemMessage(content=msg.content))
                    elif msg.role == "system":
                        messages.append(SystemMessage(content=msg.content))
            
            # Add current prompt
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            response = await client.ainvoke(messages)
            return response.content
        
        except ImportError:
            logger.error("langchain_community package not installed")
            return "Error: Cohere integration not available"
        
        except Exception as e:
            logger.exception(f"Error generating Cohere response: {e}")
            return f"Error generating response: {str(e)}"

    async def _generate_local(
        self,
        model: str,
        prompt: str,
        template: Optional[Template],
        context: Dict[str, Any],
    ) -> str:
        """Generate a response using a local model."""
        try:
            from langchain_community.llms import LlamaCpp
            
            # Extract model name from model ID
            model_name = model.replace("local-", "")
            
            # Initialize client
            client = LlamaCpp(
                model_path=f"/models/{model_name}.gguf",
                temperature=0.7,
                max_tokens=2000,
                n_ctx=8192,
            )
            
            # Prepare prompt
            full_prompt = prompt
            
            # Add system prompt if provided
            if "system_prompt" in context:
                full_prompt = f"{context['system_prompt']}\n\n{full_prompt}"
            
            # Add history if provided
            if "history" in context:
                history_text = ""
                for msg in context["history"]:
                    if msg.role == "user":
                        history_text += f"User: {msg.content}\n"
                    elif msg.role == "assistant":
                        history_text += f"Assistant: {msg.content}\n"
                    elif msg.role == "system":
                        history_text += f"System: {msg.content}\n"
                full_prompt = f"{history_text}\n{full_prompt}"
            
            # Generate response
            response = client.invoke(full_prompt)
            return response
        
        except ImportError:
            logger.error("langchain_community package not installed")
            return "Error: Local model integration not available"
        
        except Exception as e:
            logger.exception(f"Error generating local model response: {e}")
            return f"Error generating response: {str(e)}"