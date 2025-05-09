#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Konfiguriere Logging
logger = setup_logging("INFO")

# Lade Konfiguration
config_manager = ConfigManager()
config = config_manager.load_env_file(".env")

# -*- coding: utf-8 -*-

"""
Test script for the LLM selector
"""

import sys
import json
from llm_selector import LLMSelector

def main():
    """Test the LLM selector with different tasks"""
    selector = LLMSelector()
    
    # Test tasks
    tasks = [
        {
            "description": "Klassifiziere den folgenden Text als positiv oder negativ.",
            "type": "general",
            "name": "Simple Classification"
        },
        {
            "description": "Erstelle eine Zusammenfassung des folgenden Textes: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "type": "summarization",
            "name": "Text Summarization"
        },
        {
            "description": "Analysiere die folgenden Verkaufsdaten und erstelle eine Zusammenfassung der wichtigsten Trends und Muster.",
            "type": "data_analysis",
            "name": "Data Analysis"
        },
        {
            "description": "Schreibe eine kreative Kurzgeschichte über einen Roboter, der Gefühle entwickelt.",
            "type": "creative_writing",
            "name": "Creative Writing"
        },
        {
            "description": "Entwickle eine komplexe Systemarchitektur für ein verteiltes Microservice-System mit Kubernetes, das Skalierbarkeit, Fehlertoleranz und hohe Verfügbarkeit bietet. Berücksichtige dabei Aspekte wie Service Discovery, Load Balancing, Circuit Breaking und Monitoring.",
            "type": "code_generation",
            "name": "Complex System Architecture"
        }
    ]
    
    # Selection strategies
    strategies = ["cost_effective", "balanced", "high_quality", "fastest"]
    
    # Test each task with each strategy
    for task in tasks:
        print(f"\n=== Task: {task['name']} ===")
        
        # Get task complexity
        result = selector.select_model(
            task_description=task["description"],
            task_type=task["type"]
        )
        complexity = result["task_analysis"]["complexity_result"]["complexity"]
        print(f"Task Complexity: {complexity}")
        
        # Test each strategy
        logger.info("\nModel Selection by Strategy:")
        for strategy in strategies:
            result = selector.select_model(
                task_description=task["description"],
                task_type=task["type"],
                selection_strategy=strategy
            )
            selected_model = result["summary"]["selected_model"]
            model_type = result["summary"]["model_type"]
            provider = result["summary"]["provider"]
            cost = result["summary"]["estimated_cost"]
            print(f"  {strategy}: {selected_model} ({model_type}/{provider}) - Cost: €{cost:.6f}")
        
        # Show all recommendations for balanced strategy
        result = selector.select_model(
            task_description=task["description"],
            task_type=task["type"]
        )
        logger.info("\nAll Recommendations:")
        for strategy_name, recommendation in result["all_recommendations"].items():
            print(f"  {strategy_name}: {recommendation['model']} (Cost: €{recommendation['cost']:.6f}, Latency: {recommendation['latency']:.2f}s, Quality: {recommendation['quality_score']}/10)")

if __name__ == "__main__":
    main()