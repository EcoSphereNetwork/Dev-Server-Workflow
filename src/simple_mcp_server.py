#!/usr/bin/env python3
"""
Simple MCP Server for testing purposes
"""

import logging
import os
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("simple-mcp-server")

# Create FastAPI app
app = FastAPI(
    title="Simple MCP Server",
    description="A simple MCP server for testing purposes",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ToolCall(BaseModel):
    name: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    content: str
    status: str = "success"

# Available tools
TOOLS = {
    "get_date": {
        "description": "Get the current date and time",
        "parameters": {}
    },
    "echo": {
        "description": "Echo back the input",
        "parameters": {
            "text": {
                "type": "string",
                "description": "The text to echo back"
            }
        }
    }
}

@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint that returns basic information about the API."""
    return {
        "name": "Simple MCP Server",
        "version": "0.1.0",
        "description": "A simple MCP server for testing purposes",
    }

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/tools", tags=["Tools"])
async def get_tools() -> Dict[str, Dict[str, Any]]:
    """Get available tools."""
    return TOOLS

@app.post("/tools/{tool_name}", tags=["Tools"])
async def call_tool(tool_name: str, parameters: Dict[str, Any] = None) -> ToolResponse:
    """Call a tool."""
    if parameters is None:
        parameters = {}
    
    if tool_name not in TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    logger.info(f"Calling tool '{tool_name}' with parameters: {parameters}")
    
    if tool_name == "get_date":
        import datetime
        return ToolResponse(content=f"Current date and time: {datetime.datetime.now()}")
    
    elif tool_name == "echo":
        if "text" not in parameters:
            raise HTTPException(status_code=400, detail="Missing required parameter 'text'")
        return ToolResponse(content=f"Echo: {parameters['text']}")
    
    else:
        raise HTTPException(status_code=501, detail=f"Tool '{tool_name}' is not implemented")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3333))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Simple MCP Server on {host}:{port}")
    
    uvicorn.run(
        "simple_mcp_server:app",
        host=host,
        port=port,
        reload=False,
    )