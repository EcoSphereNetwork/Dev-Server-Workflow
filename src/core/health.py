"""
Health monitoring module for the Dev-Server-Workflow application.
This module provides utilities for health checks and monitoring.
"""

import asyncio
import logging
import os
import platform
import psutil
import socket
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Awaitable, Union, Tuple

from src.core.logging import get_logger

# Configure logger
logger = get_logger(__name__)

class HealthStatus(Enum):
    """Enum representing the health status of a component."""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck:
    """Base class for health checks."""
    
    def __init__(
        self,
        name: str,
        description: str,
        check_interval: int = 60,  # seconds
        timeout: int = 5,  # seconds
        critical: bool = False
    ):
        """
        Initialize a new HealthCheck.
        
        Args:
            name: Name of the health check
            description: Description of the health check
            check_interval: Interval between checks in seconds
            timeout: Timeout for the check in seconds
            critical: Whether this check is critical for overall health
        """
        self.name = name
        self.description = description
        self.check_interval = check_interval
        self.timeout = timeout
        self.critical = critical
        self.last_check_time = None
        self.last_status = HealthStatus.UNKNOWN
        self.last_message = "Health check has not run yet"
        self.last_data = {}
    
    async def check(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """
        Run the health check.
        
        Returns:
            Tuple of (status, message, data)
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def run(self) -> Dict[str, Any]:
        """
        Run the health check and update the status.
        
        Returns:
            Health check result
        """
        self.last_check_time = datetime.now()
        
        try:
            # Run the check with a timeout
            status, message, data = await asyncio.wait_for(
                self.check(),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            status = HealthStatus.UNHEALTHY
            message = f"Health check timed out after {self.timeout} seconds"
            data = {}
        except Exception as e:
            logger.exception(f"Error running health check '{self.name}'")
            status = HealthStatus.UNHEALTHY
            message = f"Error running health check: {str(e)}"
            data = {"error": str(e)}
        
        self.last_status = status
        self.last_message = message
        self.last_data = data
        
        return self.get_result()
    
    def get_result(self) -> Dict[str, Any]:
        """
        Get the result of the health check.
        
        Returns:
            Health check result
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.last_status.value,
            "message": self.last_message,
            "critical": self.critical,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "data": self.last_data
        }

class SystemHealthCheck(HealthCheck):
    """Health check for system resources."""
    
    def __init__(
        self,
        cpu_threshold: float = 90.0,  # percent
        memory_threshold: float = 90.0,  # percent
        disk_threshold: float = 90.0,  # percent
        check_interval: int = 60,  # seconds
        critical: bool = True
    ):
        """
        Initialize a new SystemHealthCheck.
        
        Args:
            cpu_threshold: CPU usage threshold in percent
            memory_threshold: Memory usage threshold in percent
            disk_threshold: Disk usage threshold in percent
            check_interval: Interval between checks in seconds
            critical: Whether this check is critical for overall health
        """
        super().__init__(
            name="system",
            description="System resource health check",
            check_interval=check_interval,
            critical=critical
        )
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
    
    async def check(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """
        Run the health check.
        
        Returns:
            Tuple of (status, message, data)
        """
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Get disk usage
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent
        
        # Collect data
        data = {
            "cpu": {
                "percent": cpu_percent,
                "threshold": self.cpu_threshold
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory_percent,
                "threshold": self.memory_threshold
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "used": disk.used,
                "percent": disk_percent,
                "threshold": self.disk_threshold
            },
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "hostname": socket.gethostname()
            }
        }
        
        # Determine status
        if cpu_percent >= self.cpu_threshold or memory_percent >= self.memory_threshold or disk_percent >= self.disk_threshold:
            status = HealthStatus.DEGRADED
            message = "System resources are under pressure"
            
            # If any resource is severely over threshold, mark as unhealthy
            if cpu_percent >= self.cpu_threshold + 5 or memory_percent >= self.memory_threshold + 5 or disk_percent >= self.disk_threshold + 5:
                status = HealthStatus.UNHEALTHY
                message = "System resources are critically low"
        else:
            status = HealthStatus.HEALTHY
            message = "System resources are within normal limits"
        
        return status, message, data

class ServiceHealthCheck(HealthCheck):
    """Health check for a service endpoint."""
    
    def __init__(
        self,
        name: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
        timeout: int = 5,  # seconds
        check_interval: int = 60,  # seconds
        critical: bool = True
    ):
        """
        Initialize a new ServiceHealthCheck.
        
        Args:
            name: Name of the service
            url: URL to check
            method: HTTP method to use
            headers: HTTP headers to include
            expected_status: Expected HTTP status code
            timeout: Timeout for the check in seconds
            check_interval: Interval between checks in seconds
            critical: Whether this check is critical for overall health
        """
        super().__init__(
            name=f"service_{name}",
            description=f"Health check for {name} service",
            check_interval=check_interval,
            timeout=timeout,
            critical=critical
        )
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.expected_status = expected_status
    
    async def check(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """
        Run the health check.
        
        Returns:
            Tuple of (status, message, data)
        """
        import aiohttp
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=self.method,
                    url=self.url,
                    headers=self.headers,
                    timeout=self.timeout
                ) as response:
                    response_time = time.time() - start_time
                    response_text = await response.text()
                    
                    data = {
                        "url": self.url,
                        "method": self.method,
                        "status_code": response.status,
                        "expected_status_code": self.expected_status,
                        "response_time": response_time,
                        "response_size": len(response_text)
                    }
                    
                    if response.status == self.expected_status:
                        status = HealthStatus.HEALTHY
                        message = f"Service {self.name} is healthy"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"Service {self.name} returned unexpected status code: {response.status}"
                    
                    return status, message, data
        except aiohttp.ClientError as e:
            response_time = time.time() - start_time
            status = HealthStatus.UNHEALTHY
            message = f"Service {self.name} is unreachable: {str(e)}"
            data = {
                "url": self.url,
                "method": self.method,
                "error": str(e),
                "response_time": response_time
            }
            return status, message, data

class DatabaseHealthCheck(HealthCheck):
    """Health check for a database connection."""
    
    def __init__(
        self,
        name: str,
        connection_string: str,
        query: str = "SELECT 1",
        timeout: int = 5,  # seconds
        check_interval: int = 60,  # seconds
        critical: bool = True
    ):
        """
        Initialize a new DatabaseHealthCheck.
        
        Args:
            name: Name of the database
            connection_string: Database connection string
            query: Query to execute
            timeout: Timeout for the check in seconds
            check_interval: Interval between checks in seconds
            critical: Whether this check is critical for overall health
        """
        super().__init__(
            name=f"database_{name}",
            description=f"Health check for {name} database",
            check_interval=check_interval,
            timeout=timeout,
            critical=critical
        )
        self.connection_string = connection_string
        self.query = query
    
    async def check(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """
        Run the health check.
        
        Returns:
            Tuple of (status, message, data)
        """
        import asyncpg
        
        start_time = time.time()
        
        try:
            conn = await asyncpg.connect(self.connection_string)
            try:
                await conn.execute(self.query)
                response_time = time.time() - start_time
                
                status = HealthStatus.HEALTHY
                message = f"Database {self.name} is healthy"
                data = {
                    "query": self.query,
                    "response_time": response_time
                }
            finally:
                await conn.close()
        except Exception as e:
            response_time = time.time() - start_time
            status = HealthStatus.UNHEALTHY
            message = f"Database {self.name} is unhealthy: {str(e)}"
            data = {
                "query": self.query,
                "error": str(e),
                "response_time": response_time
            }
        
        return status, message, data

class CustomHealthCheck(HealthCheck):
    """Custom health check with a user-provided check function."""
    
    def __init__(
        self,
        name: str,
        description: str,
        check_func: Callable[[], Awaitable[Tuple[HealthStatus, str, Dict[str, Any]]]],
        check_interval: int = 60,  # seconds
        timeout: int = 5,  # seconds
        critical: bool = False
    ):
        """
        Initialize a new CustomHealthCheck.
        
        Args:
            name: Name of the health check
            description: Description of the health check
            check_func: Async function that performs the health check
            check_interval: Interval between checks in seconds
            timeout: Timeout for the check in seconds
            critical: Whether this check is critical for overall health
        """
        super().__init__(
            name=name,
            description=description,
            check_interval=check_interval,
            timeout=timeout,
            critical=critical
        )
        self.check_func = check_func
    
    async def check(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """
        Run the health check.
        
        Returns:
            Tuple of (status, message, data)
        """
        return await self.check_func()

class HealthMonitor:
    """Health monitor for the application."""
    
    def __init__(self):
        """Initialize a new HealthMonitor."""
        self.checks: Dict[str, HealthCheck] = {}
        self.running = False
        self.task = None
    
    def add_check(self, check: HealthCheck) -> None:
        """
        Add a health check to the monitor.
        
        Args:
            check: Health check to add
        """
        self.checks[check.name] = check
    
    def remove_check(self, name: str) -> None:
        """
        Remove a health check from the monitor.
        
        Args:
            name: Name of the health check to remove
        """
        if name in self.checks:
            del self.checks[name]
    
    async def run_checks(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Health check results
        """
        results = {}
        
        for name, check in self.checks.items():
            # Check if it's time to run this check
            if check.last_check_time is None or (datetime.now() - check.last_check_time).total_seconds() >= check.check_interval:
                results[name] = await check.run()
            else:
                results[name] = check.get_result()
        
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """
        Get the overall health status.
        
        Returns:
            Overall health status
        """
        if not self.checks:
            return HealthStatus.UNKNOWN
        
        # Check if any critical checks are unhealthy
        for check in self.checks.values():
            if check.critical and check.last_status == HealthStatus.UNHEALTHY:
                return HealthStatus.UNHEALTHY
        
        # Check if any critical checks are degraded
        for check in self.checks.values():
            if check.critical and check.last_status == HealthStatus.DEGRADED:
                return HealthStatus.DEGRADED
        
        # Check if any critical checks are unknown
        for check in self.checks.values():
            if check.critical and check.last_status == HealthStatus.UNKNOWN:
                return HealthStatus.UNKNOWN
        
        # If all critical checks are healthy, check non-critical checks
        has_degraded = False
        for check in self.checks.values():
            if not check.critical and check.last_status == HealthStatus.UNHEALTHY:
                return HealthStatus.DEGRADED
            elif not check.critical and check.last_status == HealthStatus.DEGRADED:
                has_degraded = True
        
        if has_degraded:
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    async def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the application.
        
        Returns:
            Health status
        """
        results = await self.run_checks()
        overall_status = self.get_overall_status()
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "checks": results
        }
    
    async def monitor_loop(self) -> None:
        """Run the health monitor loop."""
        self.running = True
        
        while self.running:
            try:
                await self.run_checks()
                
                # Log overall status
                overall_status = self.get_overall_status()
                logger.info(f"Health status: {overall_status.value}")
                
                # Check for unhealthy critical services
                for name, check in self.checks.items():
                    if check.critical and check.last_status == HealthStatus.UNHEALTHY:
                        logger.error(f"Critical service {name} is unhealthy: {check.last_message}")
            except Exception as e:
                logger.exception("Error in health monitor loop")
            
            # Sleep for a short time
            await asyncio.sleep(10)
    
    def start(self) -> None:
        """Start the health monitor."""
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.monitor_loop())
    
    def stop(self) -> None:
        """Stop the health monitor."""
        self.running = False
        if self.task is not None and not self.task.done():
            self.task.cancel()

# Create a global health monitor
health_monitor = HealthMonitor()

# Add system health check by default
health_monitor.add_check(SystemHealthCheck())

def setup_health_monitoring(
    services: Optional[List[Dict[str, Any]]] = None,
    databases: Optional[List[Dict[str, Any]]] = None,
    custom_checks: Optional[List[Dict[str, Any]]] = None
) -> None:
    """
    Set up health monitoring for the application.
    
    Args:
        services: List of service configurations
        databases: List of database configurations
        custom_checks: List of custom check configurations
    """
    # Add service health checks
    if services:
        for service in services:
            health_monitor.add_check(ServiceHealthCheck(**service))
    
    # Add database health checks
    if databases:
        for database in databases:
            health_monitor.add_check(DatabaseHealthCheck(**database))
    
    # Add custom health checks
    if custom_checks:
        for check_config in custom_checks:
            check_func = check_config.pop("check_func")
            health_monitor.add_check(CustomHealthCheck(check_func=check_func, **check_config))
    
    # Start the health monitor
    health_monitor.start()

async def health_check_handler() -> Dict[str, Any]:
    """
    Handle health check requests.
    
    Returns:
        Health status
    """
    return await health_monitor.get_health()