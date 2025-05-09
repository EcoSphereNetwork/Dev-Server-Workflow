"""
Metriken-Modul für den n8n MCP Server.

Dieses Modul bietet Funktionen zur Erfassung und Bereitstellung von Metriken.
"""

import os
import json
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..utils.logger import logger
from ..core.config import settings


class MetricsCollector:
    """Metriken-Sammler-Klasse."""
    
    def __init__(self):
        """Initialisiere den Metriken-Sammler."""
        self.enabled = settings.METRICS_ENABLED
        self.metrics = {
            "requests": {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "by_method": {},
            },
            "response_time": {
                "total": 0,
                "count": 0,
                "min": float("inf"),
                "max": 0,
                "by_method": {},
            },
            "workflows": {
                "total": 0,
                "active": 0,
                "inactive": 0,
                "executions": {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                },
            },
            "uptime": {
                "start_time": time.time(),
                "uptime": 0,
            },
        }
        self.lock = threading.Lock()
    
    def record_request(self, method: str, success: bool, response_time: float) -> None:
        """
        Zeichne eine Anfrage auf.
        
        Args:
            method: Die Methode der Anfrage
            success: Ob die Anfrage erfolgreich war
            response_time: Die Antwortzeit der Anfrage
        """
        if not self.enabled:
            return
        
        with self.lock:
            # Aktualisiere die Anfragemetriken
            self.metrics["requests"]["total"] += 1
            
            if success:
                self.metrics["requests"]["successful"] += 1
            else:
                self.metrics["requests"]["failed"] += 1
            
            # Aktualisiere die Methoden-spezifischen Anfragemetriken
            if method not in self.metrics["requests"]["by_method"]:
                self.metrics["requests"]["by_method"][method] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                }
            
            self.metrics["requests"]["by_method"][method]["total"] += 1
            
            if success:
                self.metrics["requests"]["by_method"][method]["successful"] += 1
            else:
                self.metrics["requests"]["by_method"][method]["failed"] += 1
            
            # Aktualisiere die Antwortzeit-Metriken
            self.metrics["response_time"]["total"] += response_time
            self.metrics["response_time"]["count"] += 1
            self.metrics["response_time"]["min"] = min(self.metrics["response_time"]["min"], response_time)
            self.metrics["response_time"]["max"] = max(self.metrics["response_time"]["max"], response_time)
            
            # Aktualisiere die Methoden-spezifischen Antwortzeit-Metriken
            if method not in self.metrics["response_time"]["by_method"]:
                self.metrics["response_time"]["by_method"][method] = {
                    "total": 0,
                    "count": 0,
                    "min": float("inf"),
                    "max": 0,
                }
            
            self.metrics["response_time"]["by_method"][method]["total"] += response_time
            self.metrics["response_time"]["by_method"][method]["count"] += 1
            self.metrics["response_time"]["by_method"][method]["min"] = min(
                self.metrics["response_time"]["by_method"][method]["min"],
                response_time,
            )
            self.metrics["response_time"]["by_method"][method]["max"] = max(
                self.metrics["response_time"]["by_method"][method]["max"],
                response_time,
            )
    
    def update_workflow_metrics(self, total: int, active: int) -> None:
        """
        Aktualisiere die Workflow-Metriken.
        
        Args:
            total: Gesamtzahl der Workflows
            active: Anzahl der aktiven Workflows
        """
        if not self.enabled:
            return
        
        with self.lock:
            # Aktualisiere die Workflow-Metriken
            self.metrics["workflows"]["total"] = total
            self.metrics["workflows"]["active"] = active
            self.metrics["workflows"]["inactive"] = total - active
    
    def record_workflow_execution(self, success: bool) -> None:
        """
        Zeichne eine Workflow-Ausführung auf.
        
        Args:
            success: Ob die Ausführung erfolgreich war
        """
        if not self.enabled:
            return
        
        with self.lock:
            # Aktualisiere die Workflow-Ausführungsmetriken
            self.metrics["workflows"]["executions"]["total"] += 1
            
            if success:
                self.metrics["workflows"]["executions"]["successful"] += 1
            else:
                self.metrics["workflows"]["executions"]["failed"] += 1
    
    def update_uptime(self) -> None:
        """Aktualisiere die Uptime-Metriken."""
        if not self.enabled:
            return
        
        with self.lock:
            # Aktualisiere die Uptime-Metriken
            self.metrics["uptime"]["uptime"] = time.time() - self.metrics["uptime"]["start_time"]
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Erhalte die Metriken.
        
        Returns:
            Die Metriken
        """
        if not self.enabled:
            return {}
        
        with self.lock:
            # Aktualisiere die Uptime-Metriken
            self.update_uptime()
            
            # Berechne die durchschnittliche Antwortzeit
            if self.metrics["response_time"]["count"] > 0:
                avg_response_time = self.metrics["response_time"]["total"] / self.metrics["response_time"]["count"]
            else:
                avg_response_time = 0
            
            # Berechne die durchschnittliche Antwortzeit pro Methode
            for method in self.metrics["response_time"]["by_method"]:
                if self.metrics["response_time"]["by_method"][method]["count"] > 0:
                    self.metrics["response_time"]["by_method"][method]["avg"] = (
                        self.metrics["response_time"]["by_method"][method]["total"] /
                        self.metrics["response_time"]["by_method"][method]["count"]
                    )
                else:
                    self.metrics["response_time"]["by_method"][method]["avg"] = 0
            
            # Erstelle eine Kopie der Metriken
            metrics_copy = json.loads(json.dumps(self.metrics))
            
            # Füge die durchschnittliche Antwortzeit hinzu
            metrics_copy["response_time"]["avg"] = avg_response_time
            
            return metrics_copy
    
    def get_prometheus_metrics(self) -> str:
        """
        Erhalte die Metriken im Prometheus-Format.
        
        Returns:
            Die Metriken im Prometheus-Format
        """
        if not self.enabled:
            return ""
        
        # Erhalte die Metriken
        metrics = self.get_metrics()
        
        # Erstelle die Prometheus-Metriken
        prometheus_metrics = []
        
        # Anfragemetriken
        prometheus_metrics.append("# HELP n8n_mcp_requests_total Gesamtzahl der Anfragen")
        prometheus_metrics.append("# TYPE n8n_mcp_requests_total counter")
        prometheus_metrics.append(f"n8n_mcp_requests_total {metrics['requests']['total']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_requests_successful Anzahl der erfolgreichen Anfragen")
        prometheus_metrics.append("# TYPE n8n_mcp_requests_successful counter")
        prometheus_metrics.append(f"n8n_mcp_requests_successful {metrics['requests']['successful']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_requests_failed Anzahl der fehlgeschlagenen Anfragen")
        prometheus_metrics.append("# TYPE n8n_mcp_requests_failed counter")
        prometheus_metrics.append(f"n8n_mcp_requests_failed {metrics['requests']['failed']}")
        
        # Antwortzeit-Metriken
        prometheus_metrics.append("# HELP n8n_mcp_response_time_avg Durchschnittliche Antwortzeit in Sekunden")
        prometheus_metrics.append("# TYPE n8n_mcp_response_time_avg gauge")
        prometheus_metrics.append(f"n8n_mcp_response_time_avg {metrics['response_time']['avg']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_response_time_min Minimale Antwortzeit in Sekunden")
        prometheus_metrics.append("# TYPE n8n_mcp_response_time_min gauge")
        prometheus_metrics.append(f"n8n_mcp_response_time_min {metrics['response_time']['min']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_response_time_max Maximale Antwortzeit in Sekunden")
        prometheus_metrics.append("# TYPE n8n_mcp_response_time_max gauge")
        prometheus_metrics.append(f"n8n_mcp_response_time_max {metrics['response_time']['max']}")
        
        # Workflow-Metriken
        prometheus_metrics.append("# HELP n8n_mcp_workflows_total Gesamtzahl der Workflows")
        prometheus_metrics.append("# TYPE n8n_mcp_workflows_total gauge")
        prometheus_metrics.append(f"n8n_mcp_workflows_total {metrics['workflows']['total']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_workflows_active Anzahl der aktiven Workflows")
        prometheus_metrics.append("# TYPE n8n_mcp_workflows_active gauge")
        prometheus_metrics.append(f"n8n_mcp_workflows_active {metrics['workflows']['active']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_workflows_inactive Anzahl der inaktiven Workflows")
        prometheus_metrics.append("# TYPE n8n_mcp_workflows_inactive gauge")
        prometheus_metrics.append(f"n8n_mcp_workflows_inactive {metrics['workflows']['inactive']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_workflow_executions_total Gesamtzahl der Workflow-Ausführungen")
        prometheus_metrics.append("# TYPE n8n_mcp_workflow_executions_total counter")
        prometheus_metrics.append(f"n8n_mcp_workflow_executions_total {metrics['workflows']['executions']['total']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_workflow_executions_successful Anzahl der erfolgreichen Workflow-Ausführungen")
        prometheus_metrics.append("# TYPE n8n_mcp_workflow_executions_successful counter")
        prometheus_metrics.append(f"n8n_mcp_workflow_executions_successful {metrics['workflows']['executions']['successful']}")
        
        prometheus_metrics.append("# HELP n8n_mcp_workflow_executions_failed Anzahl der fehlgeschlagenen Workflow-Ausführungen")
        prometheus_metrics.append("# TYPE n8n_mcp_workflow_executions_failed counter")
        prometheus_metrics.append(f"n8n_mcp_workflow_executions_failed {metrics['workflows']['executions']['failed']}")
        
        # Uptime-Metriken
        prometheus_metrics.append("# HELP n8n_mcp_uptime Uptime in Sekunden")
        prometheus_metrics.append("# TYPE n8n_mcp_uptime gauge")
        prometheus_metrics.append(f"n8n_mcp_uptime {metrics['uptime']['uptime']}")
        
        return "\n".join(prometheus_metrics)