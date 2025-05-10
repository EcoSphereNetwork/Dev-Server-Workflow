"""
Task cost estimator for the Prompt MCP Server.

This module provides functionality to estimate the cost of processing a task with different models.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Union

from ..models.llm import LLMModel, ModelType, ComplexityLevel
from .llm_selector import LLMSelector
from .template_manager import TemplateManager

# Create logger
logger = logging.getLogger(__name__)


class TaskCostEstimator:
    """Task cost estimator class."""

    def __init__(self, llm_selector: LLMSelector, template_manager: TemplateManager):
        """
        Initialize the task cost estimator.

        Args:
            llm_selector: The LLM selector
            template_manager: The template manager
        """
        self.llm_selector = llm_selector
        self.template_manager = template_manager

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.

        Args:
            text: The text to estimate tokens for

        Returns:
            The estimated number of tokens
        """
        # Simple estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    async def estimate_cost(
        self,
        prompt: str,
        model_ids: Optional[List[str]] = None,
        expected_output_length: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Estimate the cost of processing a prompt with different models.

        Args:
            prompt: The prompt to estimate cost for
            model_ids: Optional list of model IDs to estimate cost for
            expected_output_length: Optional expected output length in characters

        Returns:
            A dictionary with cost estimates
        """
        try:
            # Estimate input tokens
            input_tokens = self.estimate_tokens(prompt)
            
            # Estimate output tokens
            if expected_output_length:
                output_tokens = self.estimate_tokens(expected_output_length)
            else:
                # Default: output is roughly 1.5x the input for most tasks
                output_tokens = int(input_tokens * 1.5)
            
            # Get models to estimate cost for
            if model_ids:
                models = [self.llm_selector.get_model(model_id) for model_id in model_ids if self.llm_selector.get_model(model_id)]
            else:
                # Use all available models
                models = self.llm_selector.list_models()
            
            # Calculate cost for each model
            cost_estimates = []
            for model in models:
                input_cost = (input_tokens / 1_000_000) * model.input_cost
                output_cost = (output_tokens / 1_000_000) * model.output_cost
                total_cost = input_cost + output_cost
                
                cost_estimates.append({
                    "model": model.id,
                    "name": model.name,
                    "provider": model.provider,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost": total_cost,
                })
            
            # Sort by total cost
            cost_estimates.sort(key=lambda x: x["total_cost"])
            
            # Analyze complexity
            complexity = self.llm_selector.analyze_complexity(prompt)
            recommended_model_id = self.llm_selector.select_model(complexity)
            recommended_model = self.llm_selector.get_model(recommended_model_id)
            
            # Return results
            return {
                "estimated_input_tokens": input_tokens,
                "estimated_output_tokens": output_tokens,
                "complexity": complexity,
                "recommended_model": {
                    "id": recommended_model.id,
                    "name": recommended_model.name,
                    "provider": recommended_model.provider,
                },
                "cost_estimates": cost_estimates,
            }
        
        except Exception as e:
            logger.exception(f"Error estimating cost: {e}")
            return {
                "error": str(e),
                "estimated_input_tokens": self.estimate_tokens(prompt),
                "estimated_output_tokens": 0,
                "cost_estimates": [],
            }

    async def generate_cost_report(
        self,
        prompt: str,
        model_ids: Optional[List[str]] = None,
        expected_output_length: Optional[int] = None,
    ) -> str:
        """
        Generate a human-readable cost report.

        Args:
            prompt: The prompt to estimate cost for
            model_ids: Optional list of model IDs to estimate cost for
            expected_output_length: Optional expected output length in characters

        Returns:
            A human-readable cost report
        """
        try:
            # Get cost estimates
            estimates = await self.estimate_cost(prompt, model_ids, expected_output_length)
            
            # Generate report
            report = "# Task Cost Estimation Report\n\n"
            
            report += f"## Task Complexity: {estimates['complexity']}\n\n"
            
            report += f"## Token Estimates\n"
            report += f"- Estimated input tokens: {estimates['estimated_input_tokens']}\n"
            report += f"- Estimated output tokens: {estimates['estimated_output_tokens']}\n"
            report += f"- Total tokens: {estimates['estimated_input_tokens'] + estimates['estimated_output_tokens']}\n\n"
            
            report += f"## Recommended Model\n"
            report += f"- Model: {estimates['recommended_model']['name']} ({estimates['recommended_model']['provider']})\n\n"
            
            report += f"## Cost Estimates\n\n"
            report += "| Model | Provider | Input Cost | Output Cost | Total Cost |\n"
            report += "|-------|----------|------------|-------------|------------|\n"
            
            for estimate in estimates["cost_estimates"]:
                report += f"| {estimate['name']} | {estimate['provider']} | ${estimate['input_cost']:.6f} | ${estimate['output_cost']:.6f} | ${estimate['total_cost']:.6f} |\n"
            
            return report
        
        except Exception as e:
            logger.exception(f"Error generating cost report: {e}")
            return f"Error generating cost report: {str(e)}"