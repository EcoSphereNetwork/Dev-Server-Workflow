"""
Network utilities for the Dev-Server-Workflow project.

This module provides utilities for network operations, including checking port availability,
finding free ports, and waiting for ports to become available.
"""

import socket
import time
import requests
from typing import Optional, List, Dict, Any, Union

from ..core.logger import get_logger

logger = get_logger("network_utils")

class NetworkUtils:
    """
    Utilities for network operations.
    """
    
    @staticmethod
    def is_port_in_use(port: int, host: str = "localhost") -> bool:
        """
        Check if a port is already in use.
        
        Args:
            port: Port number
            host: Hostname or IP address
            
        Returns:
            bool: True if the port is in use, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                return result == 0
        except Exception as e:
            logger.error(f"Error checking if port is in use: {e}")
            return False
    
    @staticmethod
    def find_free_port(start_port: int = 8000, end_port: int = 9000, host: str = "localhost") -> Optional[int]:
        """
        Find a free port.
        
        Args:
            start_port: Start port
            end_port: End port
            host: Hostname or IP address
            
        Returns:
            Optional[int]: Free port or None if no free port was found
        """
        for port in range(start_port, end_port + 1):
            if not NetworkUtils.is_port_in_use(port, host):
                return port
        
        logger.warning(f"No free port found in range {start_port}-{end_port}")
        return None
    
    @staticmethod
    def wait_for_port(port: int, host: str = "localhost", timeout: int = 30) -> bool:
        """
        Wait for a port to become available.
        
        Args:
            port: Port number
            host: Hostname or IP address
            timeout: Timeout in seconds
            
        Returns:
            bool: True if the port became available, False if it timed out
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if NetworkUtils.is_port_in_use(port, host):
                return True
            
            time.sleep(0.5)
        
        logger.warning(f"Timeout waiting for port {port} to become available")
        return False
    
    @staticmethod
    def wait_for_http_server(url: str, timeout: int = 30, check_interval: float = 0.5) -> bool:
        """
        Wait for an HTTP server to become available.
        
        Args:
            url: URL of the server
            timeout: Timeout in seconds
            check_interval: Interval between checks in seconds
            
        Returns:
            bool: True if the server became available, False if it timed out
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=1)
                if response.status_code < 500:  # Accept any non-server error
                    logger.info(f"HTTP server at {url} is available")
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(check_interval)
        
        logger.warning(f"Timeout waiting for HTTP server at {url} to become available")
        return False
    
    @staticmethod
    def check_url_availability(url: str, timeout: int = 5) -> bool:
        """
        Check if a URL is available.
        
        Args:
            url: URL to check
            timeout: Timeout in seconds
            
        Returns:
            bool: True if the URL is available, False otherwise
        """
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code < 500  # Accept any non-server error
        except requests.RequestException as e:
            logger.error(f"Error checking URL availability: {e}")
            return False
    
    @staticmethod
    def get_local_ip() -> str:
        """
        Get the local IP address.
        
        Returns:
            str: Local IP address
        """
        try:
            # Create a socket to determine the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            logger.error(f"Error getting local IP address: {e}")
            return "127.0.0.1"
    
    @staticmethod
    def get_hostname() -> str:
        """
        Get the hostname.
        
        Returns:
            str: Hostname
        """
        try:
            return socket.gethostname()
        except Exception as e:
            logger.error(f"Error getting hostname: {e}")
            return "localhost"