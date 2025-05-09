#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Selector Module

This module provides functionality to automatically select the most appropriate LLM
(local or cloud) based on task complexity, cost considerations, and quality requirements.
"""

import re
import json
import time
import logging
import argparse
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llm_selector")

# Task complexity categories
COMPLEXITY_CATEGORIES = {
    "very_simple": {
        "description": "Sehr einfache Aufgaben: Klassifikation, kurze Antworten, einfache Fragen",
        "avg_input_tokens": 200,
        "avg_output_tokens": 100,
        "min_complexity_handling": 4.0,
        "required_context_size": 1024,
        "processing_time_multiplier": 1.0
    },
    "simple": {
        "description": "Einfache Aufgaben: Zusammenfassungen, kurze Texte, einfache Faktenrecherche",
        "avg_input_tokens": 1000,
        "avg_output_tokens": 300,
        "min_complexity_handling": 5.0,
        "required_context_size": 2048,
        "processing_time_multiplier": 1.2
    },
    "medium": {
        "description": "Mittlere Komplexität: Standard-Codegeneration, detaillierte Antworten, Analysen",
        "avg_input_tokens": 2000,
        "avg_output_tokens": 800,
        "min_complexity_handling": 6.5,
        "required_context_size": 4096,
        "processing_time_multiplier": 1.5
    },
    "complex": {
        "description": "Komplexe Aufgaben: Tiefe Textanalysen, fortgeschrittene Codegeneration, logisches Reasoning",
        "avg_input_tokens": 4000,
        "avg_output_tokens": 1500,
        "min_complexity_handling": 7.5,
        "required_context_size": 8192,
        "processing_time_multiplier": 2.0
    },
    "very_complex": {
        "description": "Sehr komplexe Aufgaben: Multi-step Reasoning, detaillierte Berichte, komplexe Problemlösung",
        "avg_input_tokens": 8000,
        "avg_output_tokens": 3000,
        "min_complexity_handling": 8.5,
        "required_context_size": 16384,
        "processing_time_multiplier": 3.0
    },
    "extremely_complex": {
        "description": "Extrem komplexe Aufgaben: Forschungssynthesen, hochkomplexe Logikketten, AI-Agenten-Systeme",
        "avg_input_tokens": 15000,
        "avg_output_tokens": 4000,
        "min_complexity_handling": 9.5,
        "required_context_size": 32768,
        "processing_time_multiplier": 4.0
    }
}

# Model database with costs and capabilities
MODEL_DATABASE = {
    # Cloud models
    "claude-3-5-sonnet": {
        "type": "cloud",
        "provider": "anthropic",
        "input_cost": 3.0,     # € per 1M tokens
        "output_cost": 15.0,   # € per 1M tokens
        "max_context": 200000,
        "max_output": 4096,
        "token_processing_speed": 150,  # Tokens per second
        "complexity_handling": 9.5,     # 1-10 scale
        "quality_score": 9.5,           # 1-10 scale
        "multimodal_capable": True
    },
    "claude-3-opus": {
        "type": "cloud",
        "provider": "anthropic",
        "input_cost": 15.0,
        "output_cost": 75.0,
        "max_context": 200000,
        "max_output": 4096,
        "token_processing_speed": 100,
        "complexity_handling": 10.0,
        "quality_score": 10.0,
        "multimodal_capable": True
    },
    "gpt-4o": {
        "type": "cloud",
        "provider": "openai",
        "input_cost": 10.0,
        "output_cost": 30.0,
        "max_context": 128000,
        "max_output": 4096,
        "token_processing_speed": 120,
        "complexity_handling": 9.5,
        "quality_score": 9.5,
        "multimodal_capable": True
    },
    "gpt-4o-mini": {
        "type": "cloud",
        "provider": "openai",
        "input_cost": 5.0,
        "output_cost": 15.0,
        "max_context": 128000,
        "max_output": 4096,
        "token_processing_speed": 150,
        "complexity_handling": 9.0,
        "quality_score": 8.8,
        "multimodal_capable": True
    },
    
    # Local models
    "local-1.5b": {
        "type": "local",
        "hardware_cost": 1500,          # Acquisition costs in €
        "power_consumption_w": 150,     # Watts
        "max_context": 2048,
        "max_output": 2048,
        "token_processing_speed": 100,  # Tokens per second
        "complexity_handling": 4.5,     # 1-10 scale
        "quality_score": 5.0,           # 1-10 scale
        "multimodal_capable": False,
        "maintenance_cost_per_month": 50
    },
    "local-3b": {
        "type": "local",
        "hardware_cost": 2000,
        "power_consumption_w": 200,
        "max_context": 4096,
        "max_output": 2048,
        "token_processing_speed": 80,
        "complexity_handling": 5.5,
        "quality_score": 6.0,
        "multimodal_capable": False,
        "maintenance_cost_per_month": 75
    },
    "local-7b": {
        "type": "local",
        "hardware_cost": 2500,
        "power_consumption_w": 300,
        "max_context": 8192,
        "max_output": 2048,
        "token_processing_speed": 50,
        "complexity_handling": 7.0,
        "quality_score": 7.5,
        "multimodal_capable": False,
        "maintenance_cost_per_month": 100
    },
    "local-13b": {
        "type": "local",
        "hardware_cost": 3000,
        "power_consumption_w": 400,
        "max_context": 8192,
        "max_output": 2048,
        "token_processing_speed": 30,
        "complexity_handling": 7.5,
        "quality_score": 8.0,
        "multimodal_capable": False,
        "maintenance_cost_per_month": 125
    },
    "local-34b": {
        "type": "local",
        "hardware_cost": 7500,
        "power_consumption_w": 800,
        "max_context": 16384,
        "max_output": 4096,
        "token_processing_speed": 15,
        "complexity_handling": 8.5,
        "quality_score": 8.8,
        "multimodal_capable": False,
        "maintenance_cost_per_month": 200
    },
    "local-70b": {
        "type": "local",
        "hardware_cost": 15000,
        "power_consumption_w": 1200,
        "max_context": 32768,
        "max_output": 4096,
        "token_processing_speed": 8,
        "complexity_handling": 9.0,
        "quality_score": 9.2,
        "multimodal_capable": False,
        "maintenance_cost_per_month": 300
    }
}

# Task types with specific requirements
TASK_TYPES = {
    "general": {
        "complexity_multiplier": 1.0,
        "quality_threshold": 7.0,
        "keywords": []
    },
    "code_generation": {
        "complexity_multiplier": 1.2,
        "quality_threshold": 8.0,
        "keywords": ["code", "programmieren", "funktion", "klasse", "implementiere"]
    },
    "creative_writing": {
        "complexity_multiplier": 1.1,
        "quality_threshold": 8.5,
        "keywords": ["kreativ", "geschichte", "artikel", "blog", "schreibe"]
    },
    "data_analysis": {
        "complexity_multiplier": 1.3,
        "quality_threshold": 8.0,
        "keywords": ["daten", "analyse", "statistik", "trend", "auswerten"]
    },
    "translation": {
        "complexity_multiplier": 0.9,
        "quality_threshold": 8.0,
        "keywords": ["übersetze", "übersetzung", "sprache", "von", "nach"]
    },
    "summarization": {
        "complexity_multiplier": 0.8,
        "quality_threshold": 7.5,
        "keywords": ["zusammenfassen", "zusammenfassung", "kurz", "kompakt"]
    }
}

# Complexity patterns with detection features
COMPLEXITY_PATTERNS = {
    "very_simple": {
        "keywords": ["klassifiziere", "kategorisiere", "kurz", "einfach", "ja/nein", "wahr/falsch"],
        "max_token_estimate": 500,
        "requires_reasoning": False,
        "requires_creativity": False,
        "requires_specialization": False
    },
    "simple": {
        "keywords": ["zusammenfassen", "liste", "extrahiere", "finde", "erkläre kurz"],
        "max_token_estimate": 1500,
        "requires_reasoning": False,
        "requires_creativity": False,
        "requires_specialization": False
    },
    "medium": {
        "keywords": ["analysiere", "vergleiche", "erkläre", "generiere code", "schreibe"],
        "max_token_estimate": 3000,
        "requires_reasoning": True,
        "requires_creativity": False,
        "requires_specialization": False
    },
    "complex": {
        "keywords": ["entwickle", "entwerfe", "optimiere", "debugge", "löse", "tiefgehend"],
        "max_token_estimate": 6000,
        "requires_reasoning": True,
        "requires_creativity": True,
        "requires_specialization": False
    },
    "very_complex": {
        "keywords": ["forschung", "komplex", "umfassend", "detailliert", "mehrschrittig"],
        "max_token_estimate": 12000,
        "requires_reasoning": True,
        "requires_creativity": True,
        "requires_specialization": True
    },
    "extremely_complex": {
        "keywords": ["hochkomplex", "KI-Agent", "Forschungssynthese", "Systemarchitektur", "umfangreich"],
        "max_token_estimate": 20000,
        "requires_reasoning": True,
        "requires_creativity": True,
        "requires_specialization": True
    }
}

@dataclass
class TaskAnalysisResult:
    """Result of task complexity analysis"""
    complexity: str
    scores: Dict[str, int]
    estimated_tokens: int
    has_reasoning: bool
    has_creativity: bool
    has_specialization: bool

@dataclass
class ModelCost:
    """Cost calculation for a model"""
    model_name: str
    input_cost: float = 0.0
    output_cost: float = 0.0
    energy_cost: float = 0.0
    hardware_cost: float = 0.0
    maintenance_cost: float = 0.0
    total_cost: float = 0.0
    processing_time: float = 0.0
    latency: float = 0.0
    is_rejected: bool = False
    rejection_reason: Optional[str] = None
    model_type: str = "unknown"
    provider: str = "unknown"
    quality_score: float = 0.0
    max_context: int = 0
    multimodal_capable: bool = False

@dataclass
class ModelRecommendation:
    """Model recommendation with cost and performance metrics"""
    model: str
    cost: float
    latency: float
    quality_score: float
    savings_vs_cloud: Optional[float] = None

@dataclass
class TaskCostEstimation:
    """Complete cost estimation for a task"""
    task: Dict[str, Any]
    model_results: Dict[str, ModelCost]
    recommendations: Dict[str, ModelRecommendation]
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

class TaskComplexityAnalyzer:
    """Analyzes tasks to determine their complexity level"""
    
    @staticmethod
    def estimate_token_count(text: str) -> int:
        """Estimate token count based on text length"""
        # Simple estimation: approx. 4 characters per token (for German/English)
        return max(1, len(text) // 4)
    
    @staticmethod
    def detect_task_type(description: str) -> str:
        """Detect task type based on keywords"""
        # Default type
        detected_type = "general"
        highest_match_count = 0
        
        # Check each task type for keywords
        for task_type, type_info in TASK_TYPES.items():
            if task_type == "general" or not type_info.get("keywords"):
                continue
            
            match_count = sum(1 for keyword in type_info["keywords"] 
                             if keyword.lower() in description.lower())
            
            # Choose the type with the most matches
            if match_count > highest_match_count:
                highest_match_count = match_count
                detected_type = task_type
        
        return detected_type
    
    @classmethod
    def analyze_complexity(cls, description: str, task_type: str) -> TaskAnalysisResult:
        """Analyze task complexity based on description and type"""
        # Estimate token count
        estimated_tokens = cls.estimate_token_count(description)
        
        # Check for indicators of complex reasoning
        reasoning_indicators = ["warum", "wie", "erkläre", "analysiere", "vergleiche", "bewerte"]
        has_reasoning = any(indicator.lower() in description.lower() for indicator in reasoning_indicators)
        
        # Check for indicators of creativity
        creativity_indicators = ["kreativ", "innovativ", "neu", "originell", "entwerfe", "gestalte"]
        has_creativity = any(indicator.lower() in description.lower() for indicator in creativity_indicators)
        
        # Check for indicators of specialization
        specialization_indicators = ["fachlich", "spezialisiert", "expertenwissen", "domänenspezifisch"]
        has_specialization = any(indicator.lower() in description.lower() for indicator in specialization_indicators)
        
        # Count keywords for each complexity level
        complexity_scores = {}
        for complexity, patterns in COMPLEXITY_PATTERNS.items():
            score = 0
            
            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword.lower() in description.lower():
                    score += 1
            
            # Consider reasoning, creativity, and specialization
            if patterns["requires_reasoning"] and has_reasoning:
                score += 2
            if patterns["requires_creativity"] and has_creativity:
                score += 2
            if patterns["requires_specialization"] and has_specialization:
                score += 2
            
            # Consider estimated token count
            if estimated_tokens <= patterns["max_token_estimate"]:
                score += 1
            
            complexity_scores[complexity] = score
        
        # Determine complexity with highest score
        highest_score = -1
        detected_complexity = "medium"  # Default value
        
        for complexity, score in complexity_scores.items():
            if score > highest_score:
                highest_score = score
                detected_complexity = complexity
        
        # Consider task type for final complexity
        type_info = TASK_TYPES.get(task_type, TASK_TYPES["general"])
        complexity_order = ["very_simple", "simple", "medium", "complex", "very_complex", "extremely_complex"]
        complexity_index = complexity_order.index(detected_complexity)
        
        # Adjust complexity based on type
        adjusted_index = complexity_index
        if type_info["complexity_multiplier"] > 1.2:
            # Increase complexity by one level for types with high multiplier
            adjusted_index = min(complexity_index + 1, len(complexity_order) - 1)
        elif type_info["complexity_multiplier"] < 0.8:
            # Decrease complexity by one level for types with low multiplier
            adjusted_index = max(complexity_index - 1, 0)
        
        final_complexity = complexity_order[adjusted_index]
        
        return TaskAnalysisResult(
            complexity=final_complexity,
            scores=complexity_scores,
            estimated_tokens=estimated_tokens,
            has_reasoning=has_reasoning,
            has_creativity=has_creativity,
            has_specialization=has_specialization
        )
    
    @classmethod
    def analyze_task(cls, task_description: str, task_type: str = "general", 
                    context_length: Optional[int] = None, 
                    expected_output_length: Optional[int] = None,
                    require_multimodal: bool = False,
                    quality_threshold: float = 7.0,
                    custom_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main function to analyze a task"""
        if not task_description:
            raise ValueError("No task description provided")
        
        # Detect task type if not explicitly specified
        detected_task_type = task_type if task_type != "general" else cls.detect_task_type(task_description)
        
        # Analyze complexity
        complexity_analysis = cls.analyze_complexity(task_description, detected_task_type)
        
        # Determine quality requirement based on type and custom threshold
        type_quality_threshold = TASK_TYPES.get(detected_task_type, {}).get("quality_threshold", 7.0)
        final_quality_threshold = max(quality_threshold, type_quality_threshold)
        
        # Create requirements parameters for model selection
        requirements_for_model_selection = {
            "task_complexity": complexity_analysis.complexity,
            "task_type": detected_task_type,
            "input_tokens": context_length or complexity_analysis.estimated_tokens,
            "output_tokens": expected_output_length or max(1, complexity_analysis.estimated_tokens // 2),
            "require_multimodal": require_multimodal,
            "quality_threshold": final_quality_threshold,
        }
        
        # Add custom parameters if provided
        if custom_parameters:
            requirements_for_model_selection.update(custom_parameters)
        
        return {
            "task_analysis": {
                "description": (task_description[:100] + "...") if len(task_description) > 100 else task_description,
                "detected_type": detected_task_type,
                "complexity_result": asdict(complexity_analysis),
                "quality_threshold": final_quality_threshold,
                "multimodal_required": require_multimodal
            },
            "model_selection_parameters": requirements_for_model_selection
        }


class ModelCostEstimator:
    """Estimates costs for different LLM models based on task requirements"""
    
    def __init__(self, energy_cost_per_kwh: float = 0.30, 
                hardware_amortization_months: int = 36,
                include_hardware_costs: bool = True):
        self.energy_cost_per_kwh = energy_cost_per_kwh
        self.hardware_amortization_months = hardware_amortization_months
        self.include_hardware_costs = include_hardware_costs
    
    def calculate_cloud_model_cost(self, model: str, input_token_count: int, 
                                 output_token_count: int) -> ModelCost:
        """Calculate tokenization costs for cloud models"""
        model_info = MODEL_DATABASE.get(model)
        if not model_info or model_info["type"] != "cloud":
            raise ValueError(f"Invalid cloud model: {model}")
        
        input_cost = (input_token_count / 1000000) * model_info["input_cost"]
        output_cost = (output_token_count / 1000000) * model_info["output_cost"]
        
        # Rejected requests: If context size > maxContext or required quality > model quality
        is_rejected = False
        rejection_reason = None
        
        if self.context_length and self.context_length > model_info["max_context"]:
            is_rejected = True
            rejection_reason = f"Context size ({self.context_length}) exceeds model's maximum context size ({model_info['max_context']})"
        elif self.quality_threshold and self.quality_threshold > model_info["quality_score"]:
            is_rejected = True
            rejection_reason = f"Required quality ({self.quality_threshold}) exceeds model quality ({model_info['quality_score']})"
        elif self.require_multimodal and not model_info["multimodal_capable"]:
            is_rejected = True
            rejection_reason = "Model does not support multimodal tasks"
        
        # Processing time in seconds
        processing_time = 0 if is_rejected else (input_token_count + output_token_count) / model_info["token_processing_speed"]
        
        # Response latency (simplified)
        latency = 0 if is_rejected else (processing_time + 1.5)  # +1.5s for network latency
        
        return ModelCost(
            model_name=model,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
            processing_time=processing_time,
            latency=latency,
            is_rejected=is_rejected,
            rejection_reason=rejection_reason,
            model_type="cloud",
            provider=model_info["provider"],
            quality_score=model_info["quality_score"],
            max_context=model_info["max_context"],
            multimodal_capable=model_info["multimodal_capable"]
        )
    
    def calculate_local_model_cost(self, model: str, input_token_count: int, 
                                 output_token_count: int) -> ModelCost:
        """Calculate costs for local models"""
        model_info = MODEL_DATABASE.get(model)
        if not model_info or model_info["type"] != "local":
            raise ValueError(f"Invalid local model: {model}")
        
        # Check if the model meets the requirements
        is_rejected = False
        rejection_reason = None
        
        if self.context_length and self.context_length > model_info["max_context"]:
            is_rejected = True
            rejection_reason = f"Context size ({self.context_length}) exceeds model's maximum context size ({model_info['max_context']})"
        elif self.quality_threshold and self.quality_threshold > model_info["quality_score"]:
            is_rejected = True
            rejection_reason = f"Required quality ({self.quality_threshold}) exceeds model quality ({model_info['quality_score']})"
        elif self.require_multimodal and not model_info["multimodal_capable"]:
            is_rejected = True
            rejection_reason = "Model does not support multimodal tasks"
        
        if is_rejected:
            return ModelCost(
                model_name=model,
                is_rejected=True,
                rejection_reason=rejection_reason,
                model_type="local",
                provider="local",
                quality_score=model_info["quality_score"],
                max_context=model_info["max_context"],
                multimodal_capable=model_info["multimodal_capable"]
            )
        
        # Total token count
        total_tokens = input_token_count + output_token_count
        
        # Processing time considering task complexity
        complexity_info = COMPLEXITY_CATEGORIES[self.task_complexity]
        adjusted_processing_time = (total_tokens / model_info["token_processing_speed"] * 
                                   complexity_info["processing_time_multiplier"])
        
        # Energy and hardware costs
        # Energy consumption in kWh
        energy_consumption = (model_info["power_consumption_w"] / 1000) * (adjusted_processing_time / 3600)
        energy_cost = energy_consumption * self.energy_cost_per_kwh
        
        # Hardware depreciation costs
        hardware_cost = 0
        if self.include_hardware_costs:
            # Hourly hardware cost based on depreciation period
            hourly_hardware_cost = model_info["hardware_cost"] / (self.hardware_amortization_months * 30 * 24)
            hardware_cost = hourly_hardware_cost * (adjusted_processing_time / 3600)
        
        # Maintenance costs
        hourly_maintenance_cost = model_info["maintenance_cost_per_month"] / (30 * 24)
        maintenance_cost = hourly_maintenance_cost * (adjusted_processing_time / 3600)
        
        # Total costs
        total_cost = energy_cost + hardware_cost + maintenance_cost
        
        # Latency is equal to processing time for local models
        latency = adjusted_processing_time
        
        return ModelCost(
            model_name=model,
            energy_cost=energy_cost,
            hardware_cost=hardware_cost,
            maintenance_cost=maintenance_cost,
            total_cost=total_cost,
            processing_time=adjusted_processing_time,
            latency=latency,
            is_rejected=False,
            model_type="local",
            provider="local",
            quality_score=model_info["quality_score"],
            max_context=model_info["max_context"],
            multimodal_capable=model_info["multimodal_capable"]
        )
    
    def estimate_task_costs(self, task_complexity: str = "medium",
                          input_tokens: Optional[int] = None,
                          output_tokens: Optional[int] = None,
                          context_length: Optional[int] = None,
                          models_to_evaluate: List[str] = None,
                          require_multimodal: bool = False,
                          quality_threshold: float = 7.0,
                          **kwargs) -> TaskCostEstimation:
        """Main function to calculate costs for different models"""
        # Store parameters as instance variables for use in other methods
        self.task_complexity = task_complexity
        self.context_length = context_length
        self.require_multimodal = require_multimodal
        self.quality_threshold = quality_threshold
        
        # Determine tokens based on complexity or explicit specifications
        if input_tokens is not None and output_tokens is not None:
            # Use explicitly specified token counts
            input_token_count = input_tokens
            output_token_count = output_tokens
        else:
            # Use average token counts based on complexity category
            complexity_info = COMPLEXITY_CATEGORIES.get(task_complexity)
            if not complexity_info:
                raise ValueError(f"Invalid complexity category: {task_complexity}")
            
            input_token_count = complexity_info["avg_input_tokens"]
            output_token_count = complexity_info["avg_output_tokens"]
            required_context = complexity_info["required_context_size"]
        
        # Use explicit context length if specified, otherwise from complexity category
        effective_context_length = context_length or required_context if 'required_context' in locals() else None
        
        # Use all models if none specified
        if not models_to_evaluate:
            models_to_evaluate = list(MODEL_DATABASE.keys())
        
        # Calculate results for each model
        results = {}
        for model in models_to_evaluate:
            try:
                model_info = MODEL_DATABASE.get(model)
                if not model_info:
                    results[model] = {"error": f"Unknown model: {model}"}
                    continue
                
                # Check if the model meets the basic requirements
                complexity_info = COMPLEXITY_CATEGORIES.get(task_complexity)
                if model_info["complexity_handling"] < complexity_info["min_complexity_handling"]:
                    results[model] = {
                        "is_rejected": True,
                        "rejection_reason": f"Model cannot handle the required complexity ({task_complexity})"
                    }
                    continue
                
                # Calculate specific costs depending on model type
                if model_info["type"] == "cloud":
                    model_cost = self.calculate_cloud_model_cost(model, input_token_count, output_token_count)
                else:
                    model_cost = self.calculate_local_model_cost(model, input_token_count, output_token_count)
                
                results[model] = model_cost
                
            except Exception as e:
                results[model] = {"error": str(e)}
        
        # Find the most cost-effective suitable model
        cheapest_model = None
        lowest_cost = float('inf')
        
        for model, result in results.items():
            if isinstance(result, ModelCost) and not result.is_rejected and result.total_cost < lowest_cost:
                cheapest_model = model
                lowest_cost = result.total_cost
        
        # Find the fastest suitable model
        fastest_model = None
        lowest_latency = float('inf')
        
        for model, result in results.items():
            if isinstance(result, ModelCost) and not result.is_rejected and result.latency < lowest_latency:
                fastest_model = model
                lowest_latency = result.latency
        
        # Find the highest quality model
        best_quality_model = None
        highest_quality = -float('inf')
        
        for model, result in results.items():
            if isinstance(result, ModelCost) and not result.is_rejected and result.quality_score > highest_quality:
                best_quality_model = model
                highest_quality = result.quality_score
        
        # Calculate total costs when using cloud model as reference
        cloud_reference_model = "claude-3-5-sonnet"  # Default reference
        cloud_cost = None
        if cloud_reference_model in results and isinstance(results[cloud_reference_model], ModelCost) and not results[cloud_reference_model].is_rejected:
            cloud_cost = results[cloud_reference_model].total_cost
        
        # Create recommendations
        recommendations = {}
        
        if cheapest_model:
            savings_vs_cloud = cloud_cost - results[cheapest_model].total_cost if cloud_cost else None
            recommendations["most_cost_effective"] = ModelRecommendation(
                model=cheapest_model,
                cost=results[cheapest_model].total_cost,
                latency=results[cheapest_model].latency,
                quality_score=results[cheapest_model].quality_score,
                savings_vs_cloud=savings_vs_cloud
            )
        
        if fastest_model:
            recommendations["fastest_response"] = ModelRecommendation(
                model=fastest_model,
                cost=results[fastest_model].total_cost,
                latency=results[fastest_model].latency,
                quality_score=results[fastest_model].quality_score
            )
        
        if best_quality_model:
            recommendations["highest_quality"] = ModelRecommendation(
                model=best_quality_model,
                cost=results[best_quality_model].total_cost,
                latency=results[best_quality_model].latency,
                quality_score=results[best_quality_model].quality_score
            )
        
        # Find balanced model (good compromise between cost, speed, and quality)
        if cheapest_model and fastest_model and best_quality_model:
            # Normalize costs, latency, and quality to 0-1 scale
            models_to_consider = list(set([cheapest_model, fastest_model, best_quality_model]))
            
            # Find min/max values for normalization
            min_cost = min(results[model].total_cost for model in models_to_consider)
            max_cost = max(results[model].total_cost for model in models_to_consider)
            cost_range = max_cost - min_cost
            
            min_latency = min(results[model].latency for model in models_to_consider)
            max_latency = max(results[model].latency for model in models_to_consider)
            latency_range = max_latency - min_latency
            
            min_quality = min(results[model].quality_score for model in models_to_consider)
            max_quality = max(results[model].quality_score for model in models_to_consider)
            quality_range = max_quality - min_quality
            
            # Calculate balanced score for each model
            best_balanced_score = -float('inf')
            balanced_model = None
            
            for model in models_to_consider:
                # Normalize values (0 is best, 1 is worst)
                norm_cost = (results[model].total_cost - min_cost) / cost_range if cost_range else 0
                norm_latency = (results[model].latency - min_latency) / latency_range if latency_range else 0
                # For quality, 1 is best, 0 is worst
                norm_quality = (results[model].quality_score - min_quality) / quality_range if quality_range else 0
                
                # Calculate balanced score (lower is better for cost and latency, higher is better for quality)
                balanced_score = (1 - norm_cost) * 0.4 + (1 - norm_latency) * 0.3 + norm_quality * 0.3
                
                if balanced_score > best_balanced_score:
                    best_balanced_score = balanced_score
                    balanced_model = model
            
            if balanced_model:
                recommendations["balanced"] = ModelRecommendation(
                    model=balanced_model,
                    cost=results[balanced_model].total_cost,
                    latency=results[balanced_model].latency,
                    quality_score=results[balanced_model].quality_score
                )
        
        # Create task cost estimation result
        return TaskCostEstimation(
            task={
                "complexity": task_complexity,
                "input_tokens": input_token_count,
                "output_tokens": output_token_count,
                "total_tokens": input_token_count + output_token_count,
                "context_length": effective_context_length,
                "require_multimodal": require_multimodal,
                "quality_threshold": quality_threshold
            },
            model_results={model: result for model, result in results.items() if isinstance(result, ModelCost)},
            recommendations=recommendations
        )


class LLMSelector:
    """Main class for selecting the optimal LLM based on task complexity"""
    
    def __init__(self):
        self.task_analyzer = TaskComplexityAnalyzer()
        self.cost_estimator = ModelCostEstimator()
    
    def select_model(self, task_description: str, task_type: str = "general",
                   context_length: Optional[int] = None,
                   expected_output_length: Optional[int] = None,
                   require_multimodal: bool = False,
                   quality_threshold: float = 7.0,
                   selection_strategy: str = "balanced",
                   custom_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Select the optimal model for a given task"""
        # Analyze task complexity
        task_analysis = self.task_analyzer.analyze_task(
            task_description=task_description,
            task_type=task_type,
            context_length=context_length,
            expected_output_length=expected_output_length,
            require_multimodal=require_multimodal,
            quality_threshold=quality_threshold,
            custom_parameters=custom_parameters
        )
        
        # Estimate costs for different models
        model_selection_params = task_analysis["model_selection_parameters"]
        cost_estimation = self.cost_estimator.estimate_task_costs(**model_selection_params)
        
        # Selection strategies
        selection_strategies = {
            "cost_effective": {
                "name": "Kosteneffizient",
                "description": "Wählt das kostengünstigste Modell, das die Anforderungen erfüllt",
                "recommendation_key": "most_cost_effective"
            },
            "balanced": {
                "name": "Ausgewogen",
                "description": "Balanciert Kosten, Geschwindigkeit und Qualität",
                "recommendation_key": "balanced"
            },
            "high_quality": {
                "name": "Hohe Qualität",
                "description": "Priorisiert Qualität über Kosten",
                "recommendation_key": "highest_quality"
            },
            "fastest": {
                "name": "Schnellste Antwort",
                "description": "Wählt das Modell mit der geringsten Latenz",
                "recommendation_key": "fastest_response"
            }
        }
        
        # Choose default strategy based on complexity if not specified
        if not selection_strategy or selection_strategy not in selection_strategies:
            complexity = task_analysis["task_analysis"]["complexity_result"]["complexity"]
            
            if complexity in ["very_simple", "simple"]:
                selection_strategy = "cost_effective"
            elif complexity in ["very_complex", "extremely_complex"]:
                selection_strategy = "high_quality"
            else:
                selection_strategy = "balanced"
        
        # Get strategy info
        strategy_info = selection_strategies[selection_strategy]
        
        # Get recommendation based on strategy
        recommendations = cost_estimation.recommendations
        recommendation = recommendations.get(strategy_info["recommendation_key"])
        
        # Fallback to most cost-effective if the chosen strategy doesn't have a recommendation
        if not recommendation and "most_cost_effective" in recommendations:
            recommendation = recommendations["most_cost_effective"]
            strategy_info = selection_strategies["cost_effective"]
        
        # If no recommendations available, return error
        if not recommendation:
            return {
                "error": "No suitable models found for this task",
                "task_analysis": task_analysis["task_analysis"]
            }
        
        # Get model details
        model_results = cost_estimation.model_results
        selected_model = recommendation.model
        model_details = model_results[selected_model]
        
        # Create routing information
        model_type = model_details.model_type
        is_local = model_type == "local"
        
        routing_info = {
            "endpoint": f"http://localhost:8000/models/{selected_model}/generate" if is_local else
                       f"https://api.{model_details.provider}.com/v1/chat/completions",
            "api_key_required": not is_local,
            "provider": model_details.provider,
            "model_type": model_type
        }
        
        # Create model selection result
        model_selection = {
            "selected_model": selected_model,
            "selection_strategy": selection_strategy,
            "strategy_name": strategy_info["name"],
            "strategy_description": strategy_info["description"],
            "estimated_cost": recommendation.cost,
            "estimated_latency": recommendation.latency,
            "quality_score": recommendation.quality_score
        }
        
        # Create summary
        summary = {
            "task_type": task_analysis["task_analysis"]["detected_type"],
            "task_complexity": task_analysis["task_analysis"]["complexity_result"]["complexity"],
            "selected_model": selected_model,
            "selection_strategy": strategy_info["name"],
            "estimated_cost": recommendation.cost,
            "estimated_latency": f"{recommendation.latency:.2f} seconds",
            "quality_score": f"{recommendation.quality_score}/10",
            "model_type": routing_info["model_type"],
            "provider": routing_info["provider"]
        }
        
        return {
            "success": True,
            "summary": summary,
            "routing_details": routing_info,
            "model_selection_details": model_selection,
            "task_analysis": task_analysis["task_analysis"],
            "all_recommendations": {k: asdict(v) for k, v in recommendations.items()},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def main():
    """Command-line interface for the LLM Selector"""
    parser = argparse.ArgumentParser(description="LLM Selector - Automatically select the optimal LLM based on task complexity")
    parser.add_argument("--task", "-t", type=str, help="Task description")
    parser.add_argument("--type", type=str, default="general", help="Task type (general, code_generation, creative_writing, etc.)")
    parser.add_argument("--strategy", "-s", type=str, default="balanced", 
                        choices=["cost_effective", "balanced", "high_quality", "fastest"],
                        help="Selection strategy")
    parser.add_argument("--multimodal", "-m", action="store_true", help="Require multimodal capabilities")
    parser.add_argument("--quality", "-q", type=float, default=7.0, help="Quality threshold (1-10)")
    parser.add_argument("--output", "-o", type=str, default="json", choices=["json", "text"], 
                        help="Output format")
    
    args = parser.parse_args()
    
    # If no task provided, use interactive mode
    if not args.task:
        print("Enter task description (Ctrl+D to finish):")
        task_lines = []
        try:
            while True:
                line = input()
                task_lines.append(line)
        except EOFError:
            pass
        args.task = "\n".join(task_lines)
    
    # Select model
    selector = LLMSelector()
    result = selector.select_model(
        task_description=args.task,
        task_type=args.type,
        require_multimodal=args.multimodal,
        quality_threshold=args.quality,
        selection_strategy=args.strategy
    )
    
    # Output result
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            summary = result["summary"]
            print("\n=== LLM Selection Result ===")
            print(f"Task Type: {summary['task_type']}")
            print(f"Complexity: {summary['task_complexity']}")
            print(f"Selected Model: {summary['selected_model']} ({summary['provider']})")
            print(f"Strategy: {summary['selection_strategy']}")
            print(f"Estimated Cost: €{summary['estimated_cost']:.6f}")
            print(f"Estimated Latency: {summary['estimated_latency']}")
            print(f"Quality Score: {summary['quality_score']}")
            print("===========================\n")


if __name__ == "__main__":
    main()