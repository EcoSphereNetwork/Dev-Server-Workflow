"""
Prometheus metrics for Docker MCP server.

This module provides Prometheus metrics for the Docker MCP server.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from prometheus_client import Counter, Gauge, Histogram, Summary, CollectorRegistry, generate_latest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("docker-mcp-metrics")


class MetricsCollector:
    """Prometheus metrics collector for Docker MCP server."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.registry = CollectorRegistry()
        
        # Tool execution metrics
        self.tool_executions_total = Counter(
            'docker_mcp_tool_executions_total',
            'Total number of tool executions',
            ['tool_name', 'status'],
            registry=self.registry
        )
        
        self.tool_execution_duration = Histogram(
            'docker_mcp_tool_execution_duration_seconds',
            'Duration of tool executions in seconds',
            ['tool_name'],
            registry=self.registry
        )
        
        # Authentication metrics
        self.authentication_attempts_total = Counter(
            'docker_mcp_authentication_attempts_total',
            'Total number of authentication attempts',
            ['status'],
            registry=self.registry
        )
        
        # Container metrics
        self.containers_total = Gauge(
            'docker_mcp_containers_total',
            'Total number of Docker containers',
            ['status'],
            registry=self.registry
        )
        
        # Network metrics
        self.networks_total = Gauge(
            'docker_mcp_networks_total',
            'Total number of Docker networks',
            registry=self.registry
        )
        
        # Compose stack metrics
        self.compose_stacks_total = Gauge(
            'docker_mcp_compose_stacks_total',
            'Total number of Docker Compose stacks',
            registry=self.registry
        )
        
        # Server metrics
        self.server_info = Gauge(
            'docker_mcp_server_info',
            'Docker MCP server information',
            ['version'],
            registry=self.registry
        )
        
        # Set server info
        self.server_info.labels(version='0.1.0').set(1)
        
        # Cache for container counts
        self.container_counts: Dict[str, int] = {
            'running': 0,
            'stopped': 0,
            'total': 0
        }
        
        # Cache for network count
        self.network_count = 0
        
        # Cache for compose stack count
        self.compose_stack_count = 0
        
        # Last update time
        self.last_update_time = 0
        
    def record_tool_execution(self, tool_name: str, duration: float, status: str = 'success') -> None:
        """Record a tool execution.
        
        Args:
            tool_name: Name of the tool
            duration: Duration of the execution in seconds
            status: Status of the execution (success, error)
        """
        self.tool_executions_total.labels(tool_name=tool_name, status=status).inc()
        self.tool_execution_duration.labels(tool_name=tool_name).observe(duration)
        
    def record_authentication_attempt(self, status: str = 'success') -> None:
        """Record an authentication attempt.
        
        Args:
            status: Status of the authentication attempt (success, error)
        """
        self.authentication_attempts_total.labels(status=status).inc()
        
    def update_container_counts(self, running: int, stopped: int, total: int) -> None:
        """Update container counts.
        
        Args:
            running: Number of running containers
            stopped: Number of stopped containers
            total: Total number of containers
        """
        self.container_counts = {
            'running': running,
            'stopped': stopped,
            'total': total
        }
        
        self.containers_total.labels(status='running').set(running)
        self.containers_total.labels(status='stopped').set(stopped)
        self.containers_total.labels(status='total').set(total)
        
        self.last_update_time = time.time()
        
    def update_network_count(self, count: int) -> None:
        """Update network count.
        
        Args:
            count: Number of networks
        """
        self.network_count = count
        self.networks_total.set(count)
        self.last_update_time = time.time()
        
    def update_compose_stack_count(self, count: int) -> None:
        """Update compose stack count.
        
        Args:
            count: Number of compose stacks
        """
        self.compose_stack_count = count
        self.compose_stacks_total.set(count)
        self.last_update_time = time.time()
        
    def get_metrics(self) -> bytes:
        """Get Prometheus metrics.
        
        Returns:
            Prometheus metrics in bytes format
        """
        return generate_latest(self.registry)
        
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as a dictionary.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'tool_stats': {
                # This is a placeholder for real metrics
                # In a real implementation, this would be calculated from Prometheus metrics
                'create-container': {
                    'count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'average_duration': 0
                }
            },
            'container_counts': self.container_counts,
            'network_count': self.network_count,
            'compose_stack_count': self.compose_stack_count,
            'last_update_time': self.last_update_time
        }