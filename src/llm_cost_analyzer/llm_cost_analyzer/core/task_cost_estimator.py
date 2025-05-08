"""
Aufgabenkostenrechner für den LLM Cost Analyzer.

Dieses Modul bietet Funktionalität zur Berechnung der Kosten für die Verarbeitung einer Aufgabe mit verschiedenen Modellen.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Union

from ..models.llm import LLMModel, ModelType, ComplexityLevel
from .llm_selector import LLMSelector

# Erstelle Logger
logger = logging.getLogger(__name__)


class TaskCostEstimator:
    """Aufgabenkostenrechner-Klasse."""

    def __init__(self, llm_selector: LLMSelector):
        """
        Initialisiere den Aufgabenkostenrechner.

        Args:
            llm_selector: Der LLM-Selektor
        """
        self.llm_selector = llm_selector

    def estimate_tokens(self, text: str) -> int:
        """
        Schätze die Anzahl der Tokens in einem Text.

        Args:
            text: Der Text, für den Tokens geschätzt werden sollen

        Returns:
            Die geschätzte Anzahl der Tokens
        """
        # Einfache Schätzung: 1 Token ≈ 4 Zeichen für englischen Text
        return len(text) // 4

    async def estimate_cost(
        self,
        prompt: str,
        model_ids: Optional[List[str]] = None,
        expected_output_length: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Schätze die Kosten für die Verarbeitung eines Prompts mit verschiedenen Modellen.

        Args:
            prompt: Der Prompt, für den die Kosten geschätzt werden sollen
            model_ids: Optionale Liste von Modell-IDs, für die die Kosten geschätzt werden sollen
            expected_output_length: Optionale erwartete Ausgabelänge in Zeichen

        Returns:
            Ein Dictionary mit Kostenschätzungen
        """
        try:
            # Schätze Input-Tokens
            input_tokens = self.estimate_tokens(prompt)
            
            # Schätze Output-Tokens
            if expected_output_length:
                output_tokens = self.estimate_tokens(expected_output_length)
            else:
                # Standard: Ausgabe ist etwa 1,5x der Eingabe für die meisten Aufgaben
                output_tokens = int(input_tokens * 1.5)
            
            # Hole Modelle, für die Kosten geschätzt werden sollen
            if model_ids:
                models = [self.llm_selector.get_model(model_id) for model_id in model_ids if self.llm_selector.get_model(model_id)]
            else:
                # Verwende alle verfügbaren Modelle
                models = self.llm_selector.list_models()
            
            # Berechne Kosten für jedes Modell
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
            
            # Sortiere nach Gesamtkosten
            cost_estimates.sort(key=lambda x: x["total_cost"])
            
            # Analysiere Komplexität
            complexity = self.llm_selector.analyze_complexity(prompt)
            recommended_model_id = self.llm_selector.select_model(complexity)
            recommended_model = self.llm_selector.get_model(recommended_model_id)
            
            # Gib Ergebnisse zurück
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
            logger.exception(f"Fehler bei der Kostenschätzung: {e}")
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
        Generiere einen menschenlesbaren Kostenbericht.

        Args:
            prompt: Der Prompt, für den die Kosten geschätzt werden sollen
            model_ids: Optionale Liste von Modell-IDs, für die die Kosten geschätzt werden sollen
            expected_output_length: Optionale erwartete Ausgabelänge in Zeichen

        Returns:
            Ein menschenlesbarer Kostenbericht
        """
        try:
            # Hole Kostenschätzungen
            estimates = await self.estimate_cost(prompt, model_ids, expected_output_length)
            
            # Generiere Bericht
            report = "# Aufgabenkostenschätzungsbericht\n\n"
            
            report += f"## Aufgabenkomplexität: {estimates['complexity']}\n\n"
            
            report += f"## Token-Schätzungen\n"
            report += f"- Geschätzte Input-Tokens: {estimates['estimated_input_tokens']}\n"
            report += f"- Geschätzte Output-Tokens: {estimates['estimated_output_tokens']}\n"
            report += f"- Gesamttokens: {estimates['estimated_input_tokens'] + estimates['estimated_output_tokens']}\n\n"
            
            report += f"## Empfohlenes Modell\n"
            report += f"- Modell: {estimates['recommended_model']['name']} ({estimates['recommended_model']['provider']})\n\n"
            
            report += f"## Kostenschätzungen\n\n"
            report += "| Modell | Anbieter | Input-Kosten | Output-Kosten | Gesamtkosten |\n"
            report += "|-------|----------|------------|-------------|------------|\n"
            
            for estimate in estimates["cost_estimates"]:
                report += f"| {estimate['name']} | {estimate['provider']} | ${estimate['input_cost']:.6f} | ${estimate['output_cost']:.6f} | ${estimate['total_cost']:.6f} |\n"
            
            return report
        
        except Exception as e:
            logger.exception(f"Fehler bei der Generierung des Kostenberichts: {e}")
            return f"Fehler bei der Generierung des Kostenberichts: {str(e)}"