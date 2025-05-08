"""
MCP Interface für den LLM Cost Analyzer.

Dieses Modul bietet eine MCP-konforme Schnittstelle für den LLM Cost Analyzer.
"""

import json
import logging
import asyncio
import websockets
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .core.llm_selector import LLMSelector
from .core.task_cost_estimator import TaskCostEstimator

# Erstelle Logger
logger = logging.getLogger(__name__)

# Erstelle Router
router = APIRouter()


class MCPInterface:
    """MCP Interface Klasse für den LLM Cost Analyzer."""

    def __init__(self, llm_selector: LLMSelector, task_cost_estimator: TaskCostEstimator):
        """
        Initialisiere das MCP Interface.

        Args:
            llm_selector: Der LLM Selector
            task_cost_estimator: Der Task Cost Estimator
        """
        self.llm_selector = llm_selector
        self.task_cost_estimator = task_cost_estimator
        self.clients = set()

    async def register(self, websocket: WebSocket) -> None:
        """
        Registriere einen WebSocket-Client.

        Args:
            websocket: Der WebSocket-Client
        """
        await websocket.accept()
        self.clients.add(websocket)
        logger.info(f"Client registriert: {websocket.client}")

    def unregister(self, websocket: WebSocket) -> None:
        """
        Deregistriere einen WebSocket-Client.

        Args:
            websocket: Der WebSocket-Client
        """
        self.clients.remove(websocket)
        logger.info(f"Client deregistriert: {websocket.client}")

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Sende eine Nachricht an alle registrierten Clients.

        Args:
            message: Die zu sendende Nachricht
        """
        if not self.clients:
            return
        
        # Konvertiere die Nachricht in JSON
        message_json = json.dumps(message)
        
        # Sende die Nachricht an alle Clients
        await asyncio.gather(
            *[client.send_text(message_json) for client in self.clients],
            return_exceptions=True
        )

    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """
        Verarbeite eine Nachricht von einem Client.

        Args:
            websocket: Der WebSocket-Client
            message: Die empfangene Nachricht
        """
        try:
            # Extrahiere den Nachrichtentyp
            message_type = message.get("type", "")
            
            # Verarbeite die Nachricht basierend auf dem Typ
            if message_type == "analyze_complexity":
                # Analysiere die Komplexität eines Prompts
                prompt = message.get("prompt", "")
                complexity = self.llm_selector.analyze_complexity(prompt)
                recommended_model = self.llm_selector.select_model(complexity)
                
                # Sende die Antwort
                await websocket.send_json({
                    "type": "complexity_result",
                    "request_id": message.get("request_id"),
                    "complexity": complexity,
                    "recommended_model": recommended_model
                })
            
            elif message_type == "estimate_cost":
                # Schätze die Kosten für einen Prompt
                prompt = message.get("prompt", "")
                model_ids = message.get("model_ids")
                expected_output_length = message.get("expected_output_length")
                
                # Berechne die Kosten
                cost_estimate = await self.task_cost_estimator.estimate_cost(
                    prompt=prompt,
                    model_ids=model_ids,
                    expected_output_length=expected_output_length
                )
                
                # Sende die Antwort
                await websocket.send_json({
                    "type": "cost_estimate_result",
                    "request_id": message.get("request_id"),
                    "cost_estimate": cost_estimate
                })
            
            elif message_type == "generate_report":
                # Generiere einen Kostenbericht
                prompt = message.get("prompt", "")
                model_ids = message.get("model_ids")
                expected_output_length = message.get("expected_output_length")
                
                # Generiere den Bericht
                report = await self.task_cost_estimator.generate_cost_report(
                    prompt=prompt,
                    model_ids=model_ids,
                    expected_output_length=expected_output_length
                )
                
                # Sende die Antwort
                await websocket.send_json({
                    "type": "report_result",
                    "request_id": message.get("request_id"),
                    "report": report
                })
            
            elif message_type == "list_models":
                # Liste alle verfügbaren Modelle auf
                model_type = message.get("model_type")
                models = self.llm_selector.list_models(model_type=model_type)
                
                # Sende die Antwort
                await websocket.send_json({
                    "type": "models_list",
                    "request_id": message.get("request_id"),
                    "models": [model.model_dump() for model in models]
                })
            
            elif message_type == "ping":
                # Ping-Pong für Verbindungstests
                await websocket.send_json({
                    "type": "pong",
                    "request_id": message.get("request_id")
                })
            
            else:
                # Unbekannter Nachrichtentyp
                await websocket.send_json({
                    "type": "error",
                    "request_id": message.get("request_id"),
                    "error": f"Unbekannter Nachrichtentyp: {message_type}"
                })
        
        except Exception as e:
            # Fehler bei der Verarbeitung der Nachricht
            logger.exception(f"Fehler bei der Verarbeitung der Nachricht: {e}")
            await websocket.send_json({
                "type": "error",
                "request_id": message.get("request_id"),
                "error": str(e)
            })

    async def websocket_endpoint(self, websocket: WebSocket) -> None:
        """
        WebSocket-Endpunkt für MCP-Kommunikation.

        Args:
            websocket: Der WebSocket-Client
        """
        await self.register(websocket)
        try:
            while True:
                # Empfange eine Nachricht
                message = await websocket.receive_json()
                
                # Verarbeite die Nachricht
                await self.handle_message(websocket, message)
        
        except WebSocketDisconnect:
            # Client hat die Verbindung getrennt
            self.unregister(websocket)
        
        except Exception as e:
            # Fehler bei der Verarbeitung der WebSocket-Verbindung
            logger.exception(f"Fehler bei der WebSocket-Verbindung: {e}")
            self.unregister(websocket)


# Erstelle eine Instanz des MCP Interface
mcp_interface = None


def get_mcp_interface(
    llm_selector: LLMSelector,
    task_cost_estimator: TaskCostEstimator
) -> MCPInterface:
    """
    Hole das MCP Interface.

    Args:
        llm_selector: Der LLM Selector
        task_cost_estimator: Der Task Cost Estimator

    Returns:
        Das MCP Interface
    """
    global mcp_interface
    if mcp_interface is None:
        mcp_interface = MCPInterface(llm_selector, task_cost_estimator)
    return mcp_interface


@router.websocket("/mcp")
async def websocket_endpoint(
    websocket: WebSocket,
    llm_selector: LLMSelector = None,
    task_cost_estimator: TaskCostEstimator = None
) -> None:
    """
    WebSocket-Endpunkt für MCP-Kommunikation.

    Args:
        websocket: Der WebSocket-Client
        llm_selector: Der LLM Selector
        task_cost_estimator: Der Task Cost Estimator
    """
    # Hole das MCP Interface
    interface = get_mcp_interface(llm_selector, task_cost_estimator)
    
    # Verarbeite die WebSocket-Verbindung
    await interface.websocket_endpoint(websocket)