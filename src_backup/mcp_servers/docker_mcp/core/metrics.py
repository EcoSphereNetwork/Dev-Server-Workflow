"""
Metriken-Modul für den Docker MCP Server.

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
            "docker": {
                "containers": {
                    "total": 0,
                    "running": 0,
                    "stopped": 0,
                },
                "images": {
                    "total": 0,
                },
                "networks": {
                    "total": 0,
                },
                "volumes": {
                    "total": 0,
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
    
    def update_docker_metrics(self, containers_total: int, containers_running: int, images_total: int, networks_total: int, volumes_total: int) -> None:
        """
        Aktualisiere die Docker-Metriken.
        
        Args:
            containers_total: Gesamtzahl der Container
            containers_running: Anzahl der laufenden Container
            images_total: Gesamtzahl der Images
            networks_total: Gesamtzahl der Netzwerke
            volumes_total: Gesamtzahl der Volumes
        """
        if not self.enabled:
            return
        
        with self.lock:
            # Aktualisiere die Container-Metriken
            self.metrics["docker"]["containers"]["total"] = containers_total
            self.metrics["docker"]["containers"]["running"] = containers_running
            self.metrics["docker"]["containers"]["stopped"] = containers_total - containers_running
            
            # Aktualisiere die Image-Metriken
            self.metrics["docker"]["images"]["total"] = images_total
            
            # Aktualisiere die Netzwerk-Metriken
            self.metrics["docker"]["networks"]["total"] = networks_total
            
            # Aktualisiere die Volume-Metriken
            self.metrics["docker"]["volumes"]["total"] = volumes_total
    
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
        prometheus_metrics.append("# HELP docker_mcp_requests_total Gesamtzahl der Anfragen")
        prometheus_metrics.append("# TYPE docker_mcp_requests_total counter")
        prometheus_metrics.append(f"docker_mcp_requests_total {metrics['requests']['total']}")
        
        prometheus_metrics.append("# HELP docker_mcp_requests_successful Anzahl der erfolgreichen Anfragen")
        prometheus_metrics.append("# TYPE docker_mcp_requests_successful counter")
        prometheus_metrics.append(f"docker_mcp_requests_successful {metrics['requests']['successful']}")
        
        prometheus_metrics.append("# HELP docker_mcp_requests_failed Anzahl der fehlgeschlagenen Anfragen")
        prometheus_metrics.append("# TYPE docker_mcp_requests_failed counter")
        prometheus_metrics.append(f"docker_mcp_requests_failed {metrics['requests']['failed']}")
        
        # Antwortzeit-Metriken
        prometheus_metrics.append("# HELP docker_mcp_response_time_avg Durchschnittliche Antwortzeit in Sekunden")
        prometheus_metrics.append("# TYPE docker_mcp_response_time_avg gauge")
        prometheus_metrics.append(f"docker_mcp_response_time_avg {metrics['response_time']['avg']}")
        
        prometheus_metrics.append("# HELP docker_mcp_response_time_min Minimale Antwortzeit in Sekunden")
        prometheus_metrics.append("# TYPE docker_mcp_response_time_min gauge")
        prometheus_metrics.append(f"docker_mcp_response_time_min {metrics['response_time']['min']}")
        
        prometheus_metrics.append("# HELP docker_mcp_response_time_max Maximale Antwortzeit in Sekunden")
        prometheus_metrics.append("# TYPE docker_mcp_response_time_max gauge")
        prometheus_metrics.append(f"docker_mcp_response_time_max {metrics['response_time']['max']}")
        
        # Docker-Metriken
        prometheus_metrics.append("# HELP docker_mcp_containers_total Gesamtzahl der Container")
        prometheus_metrics.append("# TYPE docker_mcp_containers_total gauge")
        prometheus_metrics.append(f"docker_mcp_containers_total {metrics['docker']['containers']['total']}")
        
        prometheus_metrics.append("# HELP docker_mcp_containers_running Anzahl der laufenden Container")
        prometheus_metrics.append("# TYPE docker_mcp_containers_running gauge")
        prometheus_metrics.append(f"docker_mcp_containers_running {metrics['docker']['containers']['running']}")
        
        prometheus_metrics.append("# HELP docker_mcp_containers_stopped Anzahl der gestoppten Container")
        prometheus_metrics.append("# TYPE docker_mcp_containers_stopped gauge")
        prometheus_metrics.append(f"docker_mcp_containers_stopped {metrics['docker']['containers']['stopped']}")
        
        prometheus_metrics.append("# HELP docker_mcp_images_total Gesamtzahl der Images")
        prometheus_metrics.append("# TYPE docker_mcp_images_total gauge")
        prometheus_metrics.append(f"docker_mcp_images_total {metrics['docker']['images']['total']}")
        
        prometheus_metrics.append("# HELP docker_mcp_networks_total Gesamtzahl der Netzwerke")
        prometheus_metrics.append("# TYPE docker_mcp_networks_total gauge")
        prometheus_metrics.append(f"docker_mcp_networks_total {metrics['docker']['networks']['total']}")
        
        prometheus_metrics.append("# HELP docker_mcp_volumes_total Gesamtzahl der Volumes")
        prometheus_metrics.append("# TYPE docker_mcp_volumes_total gauge")
        prometheus_metrics.append(f"docker_mcp_volumes_total {metrics['docker']['volumes']['total']}")
        
        # Uptime-Metriken
        prometheus_metrics.append("# HELP docker_mcp_uptime Uptime in Sekunden")
        prometheus_metrics.append("# TYPE docker_mcp_uptime gauge")
        prometheus_metrics.append(f"docker_mcp_uptime {metrics['uptime']['uptime']}")
        
        return "\n".join(prometheus_metrics)