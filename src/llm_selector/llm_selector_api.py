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
LLM Selector API

A FastAPI server that exposes the LLM selector functionality via REST API.
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from llm_selector import LLMSelector, TaskComplexityAnalyzer, ModelCostEstimator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llm_selector_api")

# Create FastAPI app
app = FastAPI(
    title="LLM Selector API",
    description="API for automatically selecting the optimal LLM based on task complexity",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM selector
selector = LLMSelector()
task_analyzer = TaskComplexityAnalyzer()
cost_estimator = ModelCostEstimator()

# Pydantic models for request/response validation
class TaskAnalysisRequest(BaseModel):
    task_description: str
    task_type: str = "general"
    context_length: Optional[int] = None
    expected_output_length: Optional[int] = None
    require_multimodal: bool = False
    quality_threshold: float = 7.0
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)

class ModelSelectionRequest(BaseModel):
    task_description: str
    task_type: str = "general"
    context_length: Optional[int] = None
    expected_output_length: Optional[int] = None
    require_multimodal: bool = False
    quality_threshold: float = 7.0
    selection_strategy: str = "balanced"
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)

class TaskCostEstimationRequest(BaseModel):
    task_complexity: str = "medium"
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    context_length: Optional[int] = None
    models_to_evaluate: Optional[List[str]] = None
    require_multimodal: bool = False
    quality_threshold: float = 7.0
    energy_cost_per_kwh: float = 0.30
    hardware_amortization_months: int = 36
    include_hardware_costs: bool = True
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "LLM Selector API",
        "version": "1.0.0",
        "description": "API for automatically selecting the optimal LLM based on task complexity",
        "endpoints": [
            {"path": "/analyze-task", "method": "POST", "description": "Analyze task complexity"},
            {"path": "/select-model", "method": "POST", "description": "Select optimal LLM for a task"},
            {"path": "/estimate-task-cost", "method": "POST", "description": "Estimate costs for different LLMs"},
            {"path": "/complexity-categories", "method": "GET", "description": "Get complexity categories"},
            {"path": "/available-models", "method": "GET", "description": "Get available models"},
            {"path": "/task-types", "method": "GET", "description": "Get task types"}
        ]
    }

@app.post("/analyze-task")
async def analyze_task(request: TaskAnalysisRequest):
    """Analyze task complexity"""
    try:
        result = task_analyzer.analyze_task(
            task_description=request.task_description,
            task_type=request.task_type,
            context_length=request.context_length,
            expected_output_length=request.expected_output_length,
            require_multimodal=request.require_multimodal,
            quality_threshold=request.quality_threshold,
            custom_parameters=request.custom_parameters
        )
        return result
    except Exception as e:
        logger.exception("Error analyzing task")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/select-model")
async def select_model(request: ModelSelectionRequest):
    """Select optimal LLM for a task"""
    try:
        result = selector.select_model(
            task_description=request.task_description,
            task_type=request.task_type,
            context_length=request.context_length,
            expected_output_length=request.expected_output_length,
            require_multimodal=request.require_multimodal,
            quality_threshold=request.quality_threshold,
            selection_strategy=request.selection_strategy,
            custom_parameters=request.custom_parameters
        )
        return result
    except Exception as e:
        logger.exception("Error selecting model")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/estimate-task-cost")
async def estimate_task_cost(request: TaskCostEstimationRequest):
    """Estimate costs for different LLMs"""
    try:
        # Create a new cost estimator with the provided parameters
        estimator = ModelCostEstimator(
            energy_cost_per_kwh=request.energy_cost_per_kwh,
            hardware_amortization_months=request.hardware_amortization_months,
            include_hardware_costs=request.include_hardware_costs
        )
        
        # Estimate costs
        result = estimator.estimate_task_costs(
            task_complexity=request.task_complexity,
            input_tokens=request.input_tokens,
            output_tokens=request.output_tokens,
            context_length=request.context_length,
            models_to_evaluate=request.models_to_evaluate,
            require_multimodal=request.require_multimodal,
            quality_threshold=request.quality_threshold,
            **request.custom_parameters
        )
        
        # Convert to dict for JSON serialization
        return {
            "task": result.task,
            "model_results": {model: vars(cost) for model, cost in result.model_results.items()},
            "recommendations": {key: vars(rec) for key, rec in result.recommendations.items()},
            "timestamp": result.timestamp
        }
    except Exception as e:
        logger.exception("Error estimating task cost")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/complexity-categories")
async def get_complexity_categories():
    """Get complexity categories"""
    from llm_selector import COMPLEXITY_CATEGORIES
    return COMPLEXITY_CATEGORIES

@app.get("/available-models")
async def get_available_models():
    """Get available models"""
    from llm_selector import MODEL_DATABASE
    return MODEL_DATABASE

@app.get("/task-types")
async def get_task_types():
    """Get task types"""
    from llm_selector import TASK_TYPES
    return TASK_TYPES

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests"""
    start_time = time.time()
    
    # Get request body
    body = await request.body()
    body_str = body.decode() if body else ""
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    if body_str and len(body_str) < 1000:  # Only log small request bodies
        logger.debug(f"Request body: {body_str}")
    
    # Process request
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} (took {process_time:.4f}s)")
    
    return response

def main():
    """Run the API server"""
    # Get port from environment or use default
    port = int(os.environ.get("LLM_SELECTOR_API_PORT", 5000))
    
    # Run server
    uvicorn.run(
        "llm_selector_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()