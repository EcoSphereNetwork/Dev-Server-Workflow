"""
Docker utilities for the Dev-Server-Workflow project.

This module provides utilities for working with Docker containers and Docker Compose.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Union

from ..core.logger import get_logger

logger = get_logger("docker_utils")

class DockerUtils:
    """
    Utilities for Docker operations.
    """
    
    @staticmethod
    def check_docker_installed() -> bool:
        """
        Check if Docker is installed.
        
        Returns:
            bool: True if Docker is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Docker installation: {e}")
            return False
    
    @staticmethod
    def check_docker_running() -> bool:
        """
        Check if Docker is running.
        
        Returns:
            bool: True if Docker is running, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Docker status: {e}")
            return False
    
    @staticmethod
    def check_docker_compose_installed() -> bool:
        """
        Check if Docker Compose is installed.
        
        Returns:
            bool: True if Docker Compose is installed, False otherwise
        """
        try:
            # Try the new Docker Compose plugin first
            result = subprocess.run(
                ["docker", "compose", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode == 0:
                return True
            
            # Try the old docker-compose command
            result = subprocess.run(
                ["docker-compose", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Docker Compose installation: {e}")
            return False
    
    @staticmethod
    def get_docker_compose_command() -> List[str]:
        """
        Get the Docker Compose command.
        
        Returns:
            List[str]: Docker Compose command
        """
        # Check if the new Docker Compose plugin is available
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if result.returncode == 0:
                return ["docker", "compose"]
        except Exception:
            pass
        
        # Fall back to the old docker-compose command
        return ["docker-compose"]
    
    @staticmethod
    def start_docker_compose(compose_file: Union[str, Path], env_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Start Docker Compose.
        
        Args:
            compose_file: Path to the Docker Compose file
            env_file: Path to the environment file
            
        Returns:
            bool: True if successful, False otherwise
        """
        compose_file = Path(compose_file)
        if not compose_file.exists():
            logger.error(f"Docker Compose file not found: {compose_file}")
            return False
        
        # Get the Docker Compose command
        compose_cmd = DockerUtils.get_docker_compose_command()
        
        # Build the command
        cmd = compose_cmd + ["-f", str(compose_file), "up", "-d"]
        
        # Add environment file if specified
        if env_file:
            env_file = Path(env_file)
            if not env_file.exists():
                logger.warning(f"Environment file not found: {env_file}")
            else:
                cmd.extend(["--env-file", str(env_file)])
        
        # Run the command
        try:
            logger.info(f"Starting Docker Compose with file: {compose_file}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.info("Docker Compose started successfully")
                return True
            else:
                logger.error(f"Error starting Docker Compose: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Error running Docker Compose: {e}")
            return False
    
    @staticmethod
    def stop_docker_compose(compose_file: Union[str, Path]) -> bool:
        """
        Stop Docker Compose.
        
        Args:
            compose_file: Path to the Docker Compose file
            
        Returns:
            bool: True if successful, False otherwise
        """
        compose_file = Path(compose_file)
        if not compose_file.exists():
            logger.error(f"Docker Compose file not found: {compose_file}")
            return False
        
        # Get the Docker Compose command
        compose_cmd = DockerUtils.get_docker_compose_command()
        
        # Build the command
        cmd = compose_cmd + ["-f", str(compose_file), "down"]
        
        # Run the command
        try:
            logger.info(f"Stopping Docker Compose with file: {compose_file}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.info("Docker Compose stopped successfully")
                return True
            else:
                logger.error(f"Error stopping Docker Compose: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Error running Docker Compose: {e}")
            return False
    
    @staticmethod
    def get_docker_container_id(container_name: str) -> Optional[str]:
        """
        Get the ID of a Docker container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Optional[str]: Container ID or None if not found
        """
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                container_id = result.stdout.decode().strip()
                if container_id:
                    return container_id
            
            return None
        except Exception as e:
            logger.error(f"Error getting container ID: {e}")
            return None
    
    @staticmethod
    def is_docker_container_running(container_name: str) -> bool:
        """
        Check if a Docker container is running.
        
        Args:
            container_name: Name of the container
            
        Returns:
            bool: True if the container is running, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                container_id = result.stdout.decode().strip()
                return bool(container_id)
            
            return False
        except Exception as e:
            logger.error(f"Error checking if container is running: {e}")
            return False
    
    @staticmethod
    def get_docker_container_logs(container_name: str, tail: int = 100) -> Optional[str]:
        """
        Get the logs of a Docker container.
        
        Args:
            container_name: Name of the container
            tail: Number of lines to return from the end of the logs
            
        Returns:
            Optional[str]: Container logs or None if an error occurred
        """
        try:
            result = subprocess.run(
                ["docker", "logs", f"--tail={tail}", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                return result.stdout.decode()
            else:
                logger.error(f"Error getting container logs: {result.stderr.decode()}")
                return None
        except Exception as e:
            logger.error(f"Error getting container logs: {e}")
            return None
    
    @staticmethod
    def start_docker_container(container_name: str) -> bool:
        """
        Start a Docker container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "start", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"Container {container_name} started successfully")
                return True
            else:
                logger.error(f"Error starting container: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Error starting container: {e}")
            return False
    
    @staticmethod
    def stop_docker_container(container_name: str) -> bool:
        """
        Stop a Docker container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "stop", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"Container {container_name} stopped successfully")
                return True
            else:
                logger.error(f"Error stopping container: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return False
    
    @staticmethod
    def remove_docker_container(container_name: str, force: bool = False) -> bool:
        """
        Remove a Docker container.
        
        Args:
            container_name: Name of the container
            force: Force removal
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = ["docker", "rm"]
            if force:
                cmd.append("-f")
            cmd.append(container_name)
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"Container {container_name} removed successfully")
                return True
            else:
                logger.error(f"Error removing container: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Error removing container: {e}")
            return False
    
    @staticmethod
    def create_docker_network(network_name: str) -> bool:
        """
        Create a Docker network.
        
        Args:
            network_name: Name of the network
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the network already exists
            result = subprocess.run(
                ["docker", "network", "inspect", network_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"Network {network_name} already exists")
                return True
            
            # Create the network
            result = subprocess.run(
                ["docker", "network", "create", network_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"Network {network_name} created successfully")
                return True
            else:
                logger.error(f"Error creating network: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Error creating network: {e}")
            return False
    
    @staticmethod
    def run_docker_container(
        image: str,
        name: Optional[str] = None,
        ports: Optional[List[str]] = None,
        volumes: Optional[List[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        network: Optional[str] = None,
        command: Optional[List[str]] = None,
        detach: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Run a Docker container.
        
        Args:
            image: Docker image
            name: Container name
            ports: Port mappings (format: "host:container")
            volumes: Volume mappings (format: "host:container")
            environment: Environment variables
            network: Docker network
            command: Command to run
            detach: Run in detached mode
            
        Returns:
            Tuple[bool, Optional[str]]: (Success, Container ID or output)
        """
        try:
            cmd = ["docker", "run"]
            
            if detach:
                cmd.append("-d")
            
            if name:
                cmd.extend(["--name", name])
            
            if ports:
                for port in ports:
                    cmd.extend(["-p", port])
            
            if volumes:
                for volume in volumes:
                    cmd.extend(["-v", volume])
            
            if environment:
                for key, value in environment.items():
                    cmd.extend(["-e", f"{key}={value}"])
            
            if network:
                cmd.extend(["--network", network])
            
            cmd.append(image)
            
            if command:
                cmd.extend(command)
            
            logger.info(f"Running Docker container: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                output = result.stdout.decode().strip()
                logger.info(f"Container started successfully: {output}")
                return True, output
            else:
                logger.error(f"Error running container: {result.stderr.decode()}")
                return False, None
        except Exception as e:
            logger.error(f"Error running container: {e}")
            return False, None