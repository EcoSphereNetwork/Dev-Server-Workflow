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

# Prometheus Exporter for Dev-Server-Workflow
# This script collects metrics from the MCP servers and exports them to Prometheus

import time
import argparse
import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import psutil
    import docker
    from prometheus_client import start_http_server, Gauge, Counter, Summary
except ImportError:
    logger.info("Required packages not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "docker", "prometheus_client"])
    import psutil
    import docker
    from prometheus_client import start_http_server, Gauge, Counter, Summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'monitoring.log'))
    ]
)
logger = logging.getLogger("prometheus_exporter")

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs'), exist_ok=True)

# Define metrics
# System metrics
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage', 'System CPU usage percentage')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage', 'System memory usage percentage')
SYSTEM_DISK_USAGE = Gauge('system_disk_usage', 'System disk usage percentage')
SYSTEM_NETWORK_SENT = Gauge('system_network_sent', 'System network bytes sent')
SYSTEM_NETWORK_RECEIVED = Gauge('system_network_received', 'System network bytes received')

# Docker metrics
DOCKER_CONTAINER_COUNT = Gauge('docker_container_count', 'Number of running Docker containers')
DOCKER_CONTAINER_CPU = Gauge('docker_container_cpu', 'Container CPU usage percentage', ['container'])
DOCKER_CONTAINER_MEMORY = Gauge('docker_container_memory', 'Container memory usage in bytes', ['container'])
DOCKER_CONTAINER_NETWORK_IN = Gauge('docker_container_network_in', 'Container network bytes received', ['container'])
DOCKER_CONTAINER_NETWORK_OUT = Gauge('docker_container_network_out', 'Container network bytes sent', ['container'])
DOCKER_CONTAINER_STATUS = Gauge('docker_container_status', 'Container status (1=running, 0=stopped)', ['container'])

# MCP server metrics
MCP_SERVER_REQUEST_COUNT = Counter('mcp_server_request_count', 'Number of requests to MCP server', ['server', 'endpoint'])
MCP_SERVER_ERROR_COUNT = Counter('mcp_server_error_count', 'Number of errors from MCP server', ['server', 'endpoint'])
MCP_SERVER_RESPONSE_TIME = Summary('mcp_server_response_time', 'Response time of MCP server in seconds', ['server', 'endpoint'])
MCP_SERVER_TOOL_CALLS = Counter('mcp_server_tool_calls', 'Number of tool calls to MCP server', ['server', 'tool'])
MCP_SERVER_HEALTH = Gauge('mcp_server_health', 'Health status of MCP server (1=healthy, 0=unhealthy)', ['server'])

# n8n metrics
N8N_WORKFLOW_EXECUTIONS = Counter('n8n_workflow_executions', 'Number of n8n workflow executions', ['workflow'])
N8N_WORKFLOW_ERRORS = Counter('n8n_workflow_errors', 'Number of n8n workflow errors', ['workflow'])
N8N_WORKFLOW_EXECUTION_TIME = Summary('n8n_workflow_execution_time', 'Execution time of n8n workflow in seconds', ['workflow'])

class PrometheusExporter:
    def __init__(self, port: int = 9090, interval: int = 15):
        """
        Initialize the Prometheus exporter
        
        Args:
            port: Port to expose metrics on
            interval: Interval in seconds between metric collections
        """
        self.port = port
        self.interval = interval
        self.docker_client = None
        self.mcp_servers = []
        
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
    
    def collect_system_metrics(self) -> None:
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY_USAGE.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            SYSTEM_DISK_USAGE.set(disk.percent)
            
            # Network usage
            net_io = psutil.net_io_counters()
            SYSTEM_NETWORK_SENT.set(net_io.bytes_sent)
            SYSTEM_NETWORK_RECEIVED.set(net_io.bytes_recv)
            
            logger.debug(f"System metrics collected: CPU={cpu_percent}%, Memory={memory.percent}%, Disk={disk.percent}%")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def collect_docker_metrics(self) -> None:
        """Collect Docker metrics"""
        if not self.docker_client:
            logger.warning("Docker client not available, skipping Docker metrics")
            return
        
        try:
            # Get running containers
            containers = self.docker_client.containers.list()
            DOCKER_CONTAINER_COUNT.set(len(containers))
            
            # Collect metrics for each container
            for container in containers:
                try:
                    # Get container stats
                    stats = container.stats(stream=False)
                    
                    # Container name
                    container_name = container.name
                    
                    # CPU usage
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                    cpu_percent = 0.0
                    if system_delta > 0 and cpu_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * 100.0
                    DOCKER_CONTAINER_CPU.labels(container=container_name).set(cpu_percent)
                    
                    # Memory usage
                    memory_usage = stats['memory_stats'].get('usage', 0)
                    DOCKER_CONTAINER_MEMORY.labels(container=container_name).set(memory_usage)
                    
                    # Network usage
                    if 'networks' in stats:
                        network_in = sum(network['rx_bytes'] for network in stats['networks'].values())
                        network_out = sum(network['tx_bytes'] for network in stats['networks'].values())
                        DOCKER_CONTAINER_NETWORK_IN.labels(container=container_name).set(network_in)
                        DOCKER_CONTAINER_NETWORK_OUT.labels(container=container_name).set(network_out)
                    
                    # Container status
                    DOCKER_CONTAINER_STATUS.labels(container=container_name).set(1)  # 1 = running
                    
                    # Check if this is an MCP server
                    if container_name.endswith('-mcp') or container_name.endswith('-mcp-bridge'):
                        if container_name not in self.mcp_servers:
                            self.mcp_servers.append(container_name)
                    
                    logger.debug(f"Docker metrics collected for container {container_name}")
                except Exception as e:
                    logger.error(f"Error collecting metrics for container {container.name}: {e}")
            
            # Update status for stopped containers
            all_containers = self.docker_client.containers.list(all=True)
            for container in all_containers:
                if container.status != 'running':
                    DOCKER_CONTAINER_STATUS.labels(container=container.name).set(0)  # 0 = stopped
        except Exception as e:
            logger.error(f"Error collecting Docker metrics: {e}")
    
    def collect_mcp_server_metrics(self) -> None:
        """Collect MCP server metrics"""
        if not self.docker_client:
            logger.warning("Docker client not available, skipping MCP server metrics")
            return
        
        for server_name in self.mcp_servers:
            try:
                # Check if server is running
                try:
                    container = self.docker_client.containers.get(server_name)
                    if container.status != 'running':
                        MCP_SERVER_HEALTH.labels(server=server_name).set(0)  # 0 = unhealthy
                        continue
                except docker.errors.NotFound:
                    MCP_SERVER_HEALTH.labels(server=server_name).set(0)  # 0 = unhealthy
                    continue
                
                # Get container IP
                container_ip = container.attrs['NetworkSettings']['IPAddress']
                if not container_ip:
                    # Try to get IP from networks
                    networks = container.attrs['NetworkSettings']['Networks']
                    if networks:
                        container_ip = next(iter(networks.values()))['IPAddress']
                
                if not container_ip:
                    logger.warning(f"Could not determine IP for container {server_name}")
                    MCP_SERVER_HEALTH.labels(server=server_name).set(0)  # 0 = unhealthy
                    continue
                
                # Check health endpoint
                try:
                    # Execute curl command inside the container
                    exit_code, output = container.exec_run(
                        cmd=f"curl -s http://localhost:3333/health",
                        stdout=True,
                        stderr=True
                    )
                    
                    if exit_code == 0 and "ok" in output.decode('utf-8'):
                        MCP_SERVER_HEALTH.labels(server=server_name).set(1)  # 1 = healthy
                    else:
                        MCP_SERVER_HEALTH.labels(server=server_name).set(0)  # 0 = unhealthy
                except Exception as e:
                    logger.error(f"Error checking health for MCP server {server_name}: {e}")
                    MCP_SERVER_HEALTH.labels(server=server_name).set(0)  # 0 = unhealthy
                
                logger.debug(f"MCP server metrics collected for {server_name}")
            except Exception as e:
                logger.error(f"Error collecting metrics for MCP server {server_name}: {e}")
    
    def collect_n8n_metrics(self) -> None:
        """Collect n8n metrics"""
        try:
            # Check if n8n container is running
            if not self.docker_client:
                logger.warning("Docker client not available, skipping n8n metrics")
                return
            
            try:
                n8n_container = self.docker_client.containers.get('n8n')
                if n8n_container.status != 'running':
                    logger.warning("n8n container is not running")
                    return
            except docker.errors.NotFound:
                logger.warning("n8n container not found")
                return
            
            # Collect n8n metrics using the n8n API
            import requests
            import json
            import os
            
            # Get n8n API credentials from environment
            n8n_host = os.environ.get('N8N_HOST', 'localhost')
            n8n_port = os.environ.get('N8N_PORT', '5678')
            n8n_api_key = os.environ.get('N8N_API_KEY', '')
            
            # Skip if no API key is available
            if not n8n_api_key:
                logger.warning("N8N_API_KEY not set, skipping n8n metrics collection")
                return
                
            # Base URL for n8n API
            base_url = f"http://{n8n_host}:{n8n_port}/api/v1"
            
            # Headers for authentication
            headers = {
                "X-N8N-API-KEY": n8n_api_key,
                "Content-Type": "application/json"
            }
            
            # Get workflow executions
            try:
                response = requests.get(f"{base_url}/executions", headers=headers)
                if response.status_code == 200:
                    executions = response.json()
                    
                    # Process executions by workflow
                    workflow_executions = {}
                    workflow_errors = {}
                    workflow_times = {}
                    
                    for execution in executions.get('data', []):
                        workflow_id = execution.get('workflowId', 'unknown')
                        workflow_name = execution.get('workflowName', 'unknown')
                        
                        # Use workflow name as label
                        if workflow_name not in workflow_executions:
                            workflow_executions[workflow_name] = 0
                            workflow_errors[workflow_name] = 0
                            workflow_times[workflow_name] = []
                            
                        # Count executions
                        workflow_executions[workflow_name] += 1
                        
                        # Count errors
                        if execution.get('status') == 'failed':
                            workflow_errors[workflow_name] += 1
                            
                        # Track execution times
                        if execution.get('startedAt') and execution.get('stoppedAt'):
                            start_time = execution.get('startedAt')
                            stop_time = execution.get('stoppedAt')
                            
                            # Convert to datetime objects
                            from datetime import datetime
                            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            stop_dt = datetime.fromisoformat(stop_time.replace('Z', '+00:00'))
                            
                            # Calculate duration in seconds
                            duration = (stop_dt - start_dt).total_seconds()
                            workflow_times[workflow_name].append(duration)
                    
                    # Update metrics
                    for workflow_name, count in workflow_executions.items():
                        N8N_WORKFLOW_EXECUTIONS.labels(workflow=workflow_name).inc(count)
                        
                    for workflow_name, count in workflow_errors.items():
                        N8N_WORKFLOW_ERRORS.labels(workflow=workflow_name).inc(count)
                        
                    for workflow_name, times in workflow_times.items():
                        if times:
                            for time_value in times:
                                N8N_WORKFLOW_EXECUTION_TIME.labels(workflow=workflow_name).observe(time_value)
                    
                    logger.debug(f"Collected metrics for {len(workflow_executions)} n8n workflows")
                else:
                    logger.warning(f"Failed to get n8n executions: {response.status_code} {response.text}")
            except requests.RequestException as e:
                logger.error(f"Error connecting to n8n API: {e}")
                
            logger.debug("n8n metrics collected")
        except Exception as e:
            logger.error(f"Error collecting n8n metrics: {e}")
    
    def run(self) -> None:
        """Start the Prometheus exporter"""
        # Start the HTTP server to expose metrics
        start_http_server(self.port)
        logger.info(f"Prometheus exporter started on port {self.port}")
        
        # Collect metrics in a loop
        while True:
            try:
                logger.info("Collecting metrics...")
                
                # Collect system metrics
                self.collect_system_metrics()
                
                # Collect Docker metrics
                self.collect_docker_metrics()
                
                # Collect MCP server metrics
                self.collect_mcp_server_metrics()
                
                # Collect n8n metrics
                self.collect_n8n_metrics()
                
                logger.info(f"Metrics collected successfully. Next collection in {self.interval} seconds.")
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
            
            # Wait for the next collection
            time.sleep(self.interval)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Prometheus Exporter for Dev-Server-Workflow')
    parser.add_argument('--port', type=int, default=9090, help='Port to expose metrics on')
    parser.add_argument('--interval', type=int, default=15, help='Interval in seconds between metric collections')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Start the exporter
    exporter = PrometheusExporter(port=args.port, interval=args.interval)
    exporter.run()

if __name__ == '__main__':
    main()