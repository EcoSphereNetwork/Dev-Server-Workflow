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
LLM Selector Client

A simple client script that demonstrates how to use the LLM selector.
"""

import sys
import json
import argparse
import requests
from typing import Dict, Any, Optional

def analyze_task(api_url: str, task_description: str, task_type: str = "general",
               require_multimodal: bool = False, quality_threshold: float = 7.0) -> Dict[str, Any]:
    """Analyze task complexity"""
    endpoint = f"{api_url}/analyze-task"
    payload = {
        "task_description": task_description,
        "task_type": task_type,
        "require_multimodal": require_multimodal,
        "quality_threshold": quality_threshold
    }
    
    response = requests.post(endpoint, json=payload)
    response.raise_for_status()
    return response.json()

def select_model(api_url: str, task_description: str, task_type: str = "general",
               require_multimodal: bool = False, quality_threshold: float = 7.0,
               selection_strategy: str = "balanced") -> Dict[str, Any]:
    """Select optimal LLM for a task"""
    endpoint = f"{api_url}/select-model"
    payload = {
        "task_description": task_description,
        "task_type": task_type,
        "require_multimodal": require_multimodal,
        "quality_threshold": quality_threshold,
        "selection_strategy": selection_strategy
    }
    
    response = requests.post(endpoint, json=payload)
    response.raise_for_status()
    return response.json()

def estimate_task_cost(api_url: str, task_complexity: str = "medium",
                     require_multimodal: bool = False, quality_threshold: float = 7.0) -> Dict[str, Any]:
    """Estimate costs for different LLMs"""
    endpoint = f"{api_url}/estimate-task-cost"
    payload = {
        "task_complexity": task_complexity,
        "require_multimodal": require_multimodal,
        "quality_threshold": quality_threshold
    }
    
    response = requests.post(endpoint, json=payload)
    response.raise_for_status()
    return response.json()

def get_complexity_categories(api_url: str) -> Dict[str, Any]:
    """Get complexity categories"""
    endpoint = f"{api_url}/complexity-categories"
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json()

def get_available_models(api_url: str) -> Dict[str, Any]:
    """Get available models"""
    endpoint = f"{api_url}/available-models"
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json()

def get_task_types(api_url: str) -> Dict[str, Any]:
    """Get task types"""
    endpoint = f"{api_url}/task-types"
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json()

def print_model_selection_result(result: Dict[str, Any]) -> None:
    """Print model selection result in a human-readable format"""
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    summary = result["summary"]
    logger.info("\n=== LLM Selection Result ===")
    print(f"Task Type: {summary['task_type']}")
    print(f"Complexity: {summary['task_complexity']}")
    print(f"Selected Model: {summary['selected_model']} ({summary['provider']})")
    print(f"Strategy: {summary['selection_strategy']}")
    print(f"Estimated Cost: €{summary['estimated_cost']:.6f}")
    print(f"Estimated Latency: {summary['estimated_latency']}")
    print(f"Quality Score: {summary['quality_score']}")
    logger.info("===========================\n")
    
    # Print all recommendations
    logger.info("All Recommendations:")
    for strategy, recommendation in result["all_recommendations"].items():
        print(f"  {strategy}: {recommendation['model']} (Cost: €{recommendation['cost']:.6f}, Latency: {recommendation['latency']:.2f}s, Quality: {recommendation['quality_score']}/10)")
    
    logger.info("\nRouting Details:")
    routing = result["routing_details"]
    print(f"  Endpoint: {routing['endpoint']}")
    print(f"  API Key Required: {routing['api_key_required']}")
    print(f"  Provider: {routing['provider']}")
    print(f"  Model Type: {routing['model_type']}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LLM Selector Client")
    parser.add_argument("--api-url", type=str, default="http://localhost:5000",
                      help="URL of the LLM Selector API")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # analyze-task command
    analyze_parser = subparsers.add_parser("analyze-task", help="Analyze task complexity")
    analyze_parser.add_argument("--task", "-t", type=str, required=True, help="Task description")
    analyze_parser.add_argument("--type", type=str, default="general", help="Task type")
    analyze_parser.add_argument("--multimodal", "-m", action="store_true", help="Require multimodal capabilities")
    analyze_parser.add_argument("--quality", "-q", type=float, default=7.0, help="Quality threshold (1-10)")
    
    # select-model command
    select_parser = subparsers.add_parser("select-model", help="Select optimal LLM for a task")
    select_parser.add_argument("--task", "-t", type=str, required=True, help="Task description")
    select_parser.add_argument("--type", type=str, default="general", help="Task type")
    select_parser.add_argument("--multimodal", "-m", action="store_true", help="Require multimodal capabilities")
    select_parser.add_argument("--quality", "-q", type=float, default=7.0, help="Quality threshold (1-10)")
    select_parser.add_argument("--strategy", "-s", type=str, default="balanced", 
                             choices=["cost_effective", "balanced", "high_quality", "fastest"],
                             help="Selection strategy")
    
    # estimate-task-cost command
    estimate_parser = subparsers.add_parser("estimate-task-cost", help="Estimate costs for different LLMs")
    estimate_parser.add_argument("--complexity", "-c", type=str, default="medium",
                               choices=["very_simple", "simple", "medium", "complex", "very_complex", "extremely_complex"],
                               help="Task complexity")
    estimate_parser.add_argument("--multimodal", "-m", action="store_true", help="Require multimodal capabilities")
    estimate_parser.add_argument("--quality", "-q", type=float, default=7.0, help="Quality threshold (1-10)")
    
    # get-complexity-categories command
    subparsers.add_parser("get-complexity-categories", help="Get complexity categories")
    
    # get-available-models command
    subparsers.add_parser("get-available-models", help="Get available models")
    
    # get-task-types command
    subparsers.add_parser("get-task-types", help="Get task types")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    try:
        if args.command == "analyze-task":
            result = analyze_task(
                api_url=args.api_url,
                task_description=args.task,
                task_type=args.type,
                require_multimodal=args.multimodal,
                quality_threshold=args.quality
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == "select-model":
            result = select_model(
                api_url=args.api_url,
                task_description=args.task,
                task_type=args.type,
                require_multimodal=args.multimodal,
                quality_threshold=args.quality,
                selection_strategy=args.strategy
            )
            print_model_selection_result(result)
        
        elif args.command == "estimate-task-cost":
            result = estimate_task_cost(
                api_url=args.api_url,
                task_complexity=args.complexity,
                require_multimodal=args.multimodal,
                quality_threshold=args.quality
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == "get-complexity-categories":
            result = get_complexity_categories(args.api_url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == "get-available-models":
            result = get_available_models(args.api_url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == "get-task-types":
            result = get_task_types(args.api_url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        else:
            parser.print_help()
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()