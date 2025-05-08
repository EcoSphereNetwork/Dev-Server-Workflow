"""
Docker executor module.

This module provides classes for executing Docker and Docker Compose commands.
"""

from typing import Tuple, Protocol, List, Optional
import asyncio
import os
import platform
import shutil
from abc import ABC, abstractmethod


class CommandExecutor(Protocol):
    """Protocol for command executors."""
    
    async def execute(self, cmd: str | List[str]) -> Tuple[int, str, str]:
        """Execute a command and return the exit code, stdout, and stderr."""
        pass


class WindowsExecutor:
    """Command executor for Windows."""
    
    async def execute(self, cmd: str) -> Tuple[int, str, str]:
        """Execute a command on Windows using shell."""
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()


class UnixExecutor:
    """Command executor for Unix-like systems."""
    
    async def execute(self, cmd: List[str]) -> Tuple[int, str, str]:
        """Execute a command on Unix-like systems using exec."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()


class DockerExecutorBase(ABC):
    """Base class for Docker executors."""
    
    def __init__(self):
        """Initialize the Docker executor."""
        self.docker_cmd = self._initialize_docker_cmd()
        self.executor = WindowsExecutor() if platform.system() == 'Windows' else UnixExecutor()

    @abstractmethod
    async def run_command(self, command: str, *args) -> Tuple[int, str, str]:
        """Run a Docker command."""
        pass

    def _initialize_docker_cmd(self) -> str:
        """Initialize the Docker command path."""
        if platform.system() == 'Windows':
            docker_dir = r"C:\Program Files\Docker\Docker\resources\bin"
            docker_paths = [
                os.path.join(docker_dir, "docker-compose.exe"),
                os.path.join(docker_dir, "docker.exe")
            ]
            for path in docker_paths:
                if os.path.exists(path):
                    return path

        docker_cmd = shutil.which('docker')
        if not docker_cmd:
            raise RuntimeError("Docker executable not found")
        return docker_cmd


class DockerComposeExecutor(DockerExecutorBase):
    """Executor for Docker Compose commands."""
    
    def __init__(self, compose_file: str, project_name: str):
        """Initialize the Docker Compose executor.
        
        Args:
            compose_file: Path to the Docker Compose file
            project_name: Name of the Docker Compose project
        """
        super().__init__()
        self.compose_file = os.path.abspath(compose_file)
        self.project_name = project_name

    async def run_command(self, command: str, *args) -> Tuple[int, str, str]:
        """Run a Docker Compose command.
        
        Args:
            command: The Docker Compose command to run
            args: Additional arguments for the command
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if platform.system() == 'Windows':
            cmd = self._build_windows_command(command, *args)
        else:
            cmd = self._build_unix_command(command, *args)
        return await self.executor.execute(cmd)

    def _build_windows_command(self, command: str, *args) -> str:
        """Build a Docker Compose command for Windows.
        
        Args:
            command: The Docker Compose command
            args: Additional arguments
            
        Returns:
            The full command string for Windows
        """
        compose_file = self.compose_file.replace('\\', '/')
        return (f'cd "{os.path.dirname(compose_file)}" && docker compose '
                f'-f "{os.path.basename(compose_file)}" '
                f'-p {self.project_name} {command} {" ".join(args)}')

    def _build_unix_command(self, command: str, *args) -> list[str]:
        """Build a Docker Compose command for Unix-like systems.
        
        Args:
            command: The Docker Compose command
            args: Additional arguments
            
        Returns:
            The command list for Unix-like systems
        """
        return [
            self.docker_cmd,
            "compose",
            "-f", self.compose_file,
            "-p", self.project_name,
            command,
            *args
        ]

    async def down(self) -> Tuple[int, str, str]:
        """Stop and remove containers, networks, volumes, and images created by up."""
        return await self.run_command("down", "--volumes")

    async def pull(self) -> Tuple[int, str, str]:
        """Pull service images."""
        return await self.run_command("pull")

    async def up(self) -> Tuple[int, str, str]:
        """Create and start containers."""
        return await self.run_command("up", "-d")

    async def ps(self) -> Tuple[int, str, str]:
        """List containers."""
        return await self.run_command("ps")
        
    async def logs(self, service: Optional[str] = None) -> Tuple[int, str, str]:
        """View output from containers."""
        if service:
            return await self.run_command("logs", service)
        return await self.run_command("logs")
        
    async def restart(self, service: Optional[str] = None) -> Tuple[int, str, str]:
        """Restart services."""
        if service:
            return await self.run_command("restart", service)
        return await self.run_command("restart")
        
    async def stop(self, service: Optional[str] = None) -> Tuple[int, str, str]:
        """Stop services."""
        if service:
            return await self.run_command("stop", service)
        return await self.run_command("stop")
        
    async def start(self, service: Optional[str] = None) -> Tuple[int, str, str]:
        """Start services."""
        if service:
            return await self.run_command("start", service)
        return await self.run_command("start")


class DockerExecutor(DockerExecutorBase):
    """Executor for Docker commands."""
    
    async def run_command(self, command: str, *args) -> Tuple[int, str, str]:
        """Run a Docker command.
        
        Args:
            command: The Docker command to run
            args: Additional arguments for the command
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if platform.system() == 'Windows':
            cmd = f'docker {command} {" ".join(args)}'
        else:
            cmd = [self.docker_cmd, command, *args]
        return await self.executor.execute(cmd)
        
    async def ps(self, all: bool = False) -> Tuple[int, str, str]:
        """List containers."""
        if all:
            return await self.run_command("ps", "--all")
        return await self.run_command("ps")
        
    async def logs(self, container: str, tail: int = 100) -> Tuple[int, str, str]:
        """View output from a container."""
        return await self.run_command("logs", f"--tail={tail}", container)
        
    async def restart(self, container: str) -> Tuple[int, str, str]:
        """Restart a container."""
        return await self.run_command("restart", container)
        
    async def stop(self, container: str) -> Tuple[int, str, str]:
        """Stop a container."""
        return await self.run_command("stop", container)
        
    async def start(self, container: str) -> Tuple[int, str, str]:
        """Start a container."""
        return await self.run_command("start", container)
        
    async def rm(self, container: str, force: bool = False) -> Tuple[int, str, str]:
        """Remove a container."""
        if force:
            return await self.run_command("rm", "--force", container)
        return await self.run_command("rm", container)
        
    async def pull(self, image: str) -> Tuple[int, str, str]:
        """Pull an image."""
        return await self.run_command("pull", image)
        
    async def run(self, image: str, name: Optional[str] = None, 
                 ports: Optional[List[str]] = None, 
                 envs: Optional[List[str]] = None,
                 volumes: Optional[List[str]] = None,
                 networks: Optional[List[str]] = None,
                 health_cmd: Optional[str] = None,
                 health_interval: Optional[str] = None,
                 health_retries: Optional[int] = None,
                 health_timeout: Optional[str] = None,
                 health_start_period: Optional[str] = None,
                 cpu_limit: Optional[str] = None,
                 memory_limit: Optional[str] = None,
                 restart_policy: Optional[str] = None,
                 detach: bool = True) -> Tuple[int, str, str]:
        """Run a container with advanced options.
        
        Args:
            image: Docker image name
            name: Container name
            ports: List of port mappings (host:container)
            envs: List of environment variables (KEY=VALUE)
            volumes: List of volume mappings (host:container)
            networks: List of networks to connect to
            health_cmd: Command to check container health
            health_interval: Interval between health checks (e.g., "30s")
            health_retries: Number of retries before considering unhealthy
            health_timeout: Timeout for health check (e.g., "10s")
            health_start_period: Start period for health check (e.g., "30s")
            cpu_limit: CPU limit (e.g., "0.5")
            memory_limit: Memory limit (e.g., "512m")
            restart_policy: Restart policy (e.g., "always", "unless-stopped")
            detach: Run container in background
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        args = []
        
        if detach:
            args.append("--detach")
            
        if name:
            args.extend(["--name", name])
            
        if ports:
            for port in ports:
                args.extend(["--publish", port])
                
        if envs:
            for env in envs:
                args.extend(["--env", env])
                
        if volumes:
            for volume in volumes:
                args.extend(["--volume", volume])
                
        if networks:
            for network in networks:
                args.extend(["--network", network])
                
        # Health check options
        if health_cmd:
            args.extend(["--health-cmd", health_cmd])
            
        if health_interval:
            args.extend(["--health-interval", health_interval])
            
        if health_retries:
            args.extend(["--health-retries", str(health_retries)])
            
        if health_timeout:
            args.extend(["--health-timeout", health_timeout])
            
        if health_start_period:
            args.extend(["--health-start-period", health_start_period])
            
        # Resource limits
        if cpu_limit:
            args.extend(["--cpus", cpu_limit])
            
        if memory_limit:
            args.extend(["--memory", memory_limit])
            
        # Restart policy
        if restart_policy:
            args.extend(["--restart", restart_policy])
                
        args.append(image)
        
        return await self.run_command("run", *args)
        
    async def network_create(self, name: str, driver: Optional[str] = None) -> Tuple[int, str, str]:
        """Create a network.
        
        Args:
            name: Network name
            driver: Network driver (e.g., "bridge", "overlay")
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        args = [name]
        
        if driver:
            args.extend(["--driver", driver])
            
        return await self.run_command("network", "create", *args)
        
    async def network_rm(self, name: str) -> Tuple[int, str, str]:
        """Remove a network.
        
        Args:
            name: Network name
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        return await self.run_command("network", "rm", name)
        
    async def network_ls(self) -> Tuple[int, str, str]:
        """List networks.
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        return await self.run_command("network", "ls")
        
    async def network_inspect(self, name: str) -> Tuple[int, str, str]:
        """Inspect a network.
        
        Args:
            name: Network name
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        return await self.run_command("network", "inspect", name)
        
    async def network_connect(self, network: str, container: str) -> Tuple[int, str, str]:
        """Connect a container to a network.
        
        Args:
            network: Network name
            container: Container name
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        return await self.run_command("network", "connect", network, container)
        
    async def network_disconnect(self, network: str, container: str) -> Tuple[int, str, str]:
        """Disconnect a container from a network.
        
        Args:
            network: Network name
            container: Container name
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        return await self.run_command("network", "disconnect", network, container)