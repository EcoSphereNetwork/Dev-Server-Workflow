"""
Docker MCP handlers module.

This module provides handlers for Docker MCP server operations.
"""

from typing import List, Dict, Any, Optional, Tuple
import asyncio
import os
import yaml
import platform
import json
import logging
from datetime import datetime
from mcp.types import TextContent

from .docker_executor import DockerComposeExecutor, DockerExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '../../../logs/docker_mcp.log'))
    ]
)
logger = logging.getLogger("docker-mcp")


async def parse_port_mapping(host_key: str, container_port: str | int) -> tuple[str, str] | tuple[str, str, str]:
    """Parse port mapping from host to container.
    
    Args:
        host_key: Host port or port/protocol
        container_port: Container port or port/protocol
        
    Returns:
        Tuple of (host_port, container_port) or (host_port, container_port, protocol)
    """
    if '/' in str(host_key):
        host_port, protocol = host_key.split('/')
        if protocol.lower() == 'udp':
            return (str(host_port), str(container_port), 'udp')
        return (str(host_port), str(container_port))

    if isinstance(container_port, str) and '/' in container_port:
        port, protocol = container_port.split('/')
        if protocol.lower() == 'udp':
            return (str(host_key), port, 'udp')
        return (str(host_key), port)

    return (str(host_key), str(container_port))


class DockerHandlers:
    """Handlers for Docker MCP server operations."""
    
    TIMEOUT_AMOUNT = 200
    
    @staticmethod
    async def handle_create_container(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle create-container tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        try:
            image = arguments["image"]
            container_name = arguments.get("name")
            ports_dict = arguments.get("ports", {})
            environment = arguments.get("environment", {})
            volumes_dict = arguments.get("volumes", {})
            networks = arguments.get("networks", [])
            
            # Health check options
            health_check = arguments.get("health_check", {})
            health_cmd = health_check.get("cmd")
            health_interval = health_check.get("interval")
            health_retries = health_check.get("retries")
            health_timeout = health_check.get("timeout")
            health_start_period = health_check.get("start_period")
            
            # Resource limits
            resources = arguments.get("resources", {})
            cpu_limit = resources.get("cpu")
            memory_limit = resources.get("memory")
            
            # Restart policy
            restart_policy = arguments.get("restart_policy")

            if not image:
                raise ValueError("Image name cannot be empty")

            # Convert ports dictionary to list of port mappings
            port_mappings = []
            for host_key, container_port in ports_dict.items():
                port_mappings.append(f"{host_key}:{container_port}")
                
            # Convert environment dictionary to list of environment variables
            env_list = [f"{key}={value}" for key, value in environment.items()]
            
            # Convert volumes dictionary to list of volume mappings
            volume_mappings = [f"{host_path}:{container_path}" for host_path, container_path in volumes_dict.items()]

            # Create Docker executor
            docker = DockerExecutor()

            async def pull_and_run():
                # Pull image if it doesn't exist
                code, out, err = await docker.ps(all=True)
                if code != 0:
                    logger.error(f"Error listing containers: {err}")
                    
                # Pull the image
                logger.info(f"Pulling image {image}")
                code, out, err = await docker.pull(image)
                if code != 0:
                    logger.error(f"Error pulling image: {err}")
                    raise RuntimeError(f"Error pulling image: {err}")

                # Create networks if they don't exist
                for network in networks:
                    # Check if network exists
                    code, out, err = await docker.network_ls()
                    if code != 0:
                        logger.error(f"Error listing networks: {err}")
                        raise RuntimeError(f"Error listing networks: {err}")
                        
                    if network not in out:
                        logger.info(f"Creating network {network}")
                        code, out, err = await docker.network_create(network)
                        if code != 0:
                            logger.error(f"Error creating network: {err}")
                            raise RuntimeError(f"Error creating network: {err}")

                # Run the container
                logger.info(f"Running container {container_name} from image {image}")
                code, out, err = await docker.run(
                    image,
                    name=container_name,
                    ports=port_mappings,
                    envs=env_list,
                    volumes=volume_mappings,
                    networks=networks,
                    health_cmd=health_cmd,
                    health_interval=health_interval,
                    health_retries=health_retries,
                    health_timeout=health_timeout,
                    health_start_period=health_start_period,
                    cpu_limit=cpu_limit,
                    memory_limit=memory_limit,
                    restart_policy=restart_policy,
                    detach=True
                )
                
                if code != 0:
                    logger.error(f"Error running container: {err}")
                    raise RuntimeError(f"Error running container: {err}")
                    
                return out.strip()

            container_id = await asyncio.wait_for(pull_and_run(), timeout=DockerHandlers.TIMEOUT_AMOUNT)
            
            # Get container details
            code, out, err = await docker.ps()
            container_details = out if code == 0 else "Unable to get container details"
            
            return [TextContent(
                type="text", 
                text=f"Created container '{container_name}' (ID: {container_id})\n\nContainer details:\n{container_details}"
            )]
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {DockerHandlers.TIMEOUT_AMOUNT} seconds")
            return [TextContent(
                type="text", 
                text=f"Operation timed out after {DockerHandlers.TIMEOUT_AMOUNT} seconds"
            )]
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error creating container: {str(e)} | Arguments: {arguments}"
            )]

    @staticmethod
    async def handle_deploy_compose(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle deploy-compose tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            compose_yaml = arguments.get("compose_yaml")
            project_name = arguments.get("project_name")

            if not compose_yaml or not project_name:
                raise ValueError("Missing required compose_yaml or project_name")

            yaml_content = DockerHandlers._process_yaml(compose_yaml, debug_info)
            compose_path = DockerHandlers._save_compose_file(yaml_content, project_name)

            try:
                result = await DockerHandlers._deploy_stack(compose_path, project_name, debug_info)
                return [TextContent(type="text", text=result)]
            finally:
                DockerHandlers._cleanup_files(compose_path)

        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error deploying compose stack: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error deploying compose stack: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]

    @staticmethod
    def _process_yaml(compose_yaml: str, debug_info: List[str]) -> dict:
        """Process YAML content.
        
        Args:
            compose_yaml: YAML content as string
            debug_info: List to append debug information
            
        Returns:
            Parsed YAML content as dictionary
        """
        debug_info.append("=== Original YAML ===")
        debug_info.append(compose_yaml)

        try:
            yaml_content = yaml.safe_load(compose_yaml)
            debug_info.append("\n=== Loaded YAML Structure ===")
            debug_info.append(str(yaml_content))
            return yaml_content
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")

    @staticmethod
    def _save_compose_file(yaml_content: dict, project_name: str) -> str:
        """Save compose file to disk.
        
        Args:
            yaml_content: YAML content as dictionary
            project_name: Project name
            
        Returns:
            Path to the saved compose file
        """
        compose_dir = os.path.join(os.getcwd(), "docker_compose_files")
        os.makedirs(compose_dir, exist_ok=True)

        compose_yaml = yaml.safe_dump(yaml_content, default_flow_style=False, sort_keys=False)
        compose_path = os.path.join(compose_dir, f"{project_name}-docker-compose.yml")

        with open(compose_path, 'w', encoding='utf-8') as f:
            f.write(compose_yaml)
            f.flush()
            if platform.system() != 'Windows':
                os.fsync(f.fileno())

        return compose_path

    @staticmethod
    async def _deploy_stack(compose_path: str, project_name: str, debug_info: List[str]) -> str:
        """Deploy Docker Compose stack.
        
        Args:
            compose_path: Path to the compose file
            project_name: Project name
            debug_info: List to append debug information
            
        Returns:
            Result message
        """
        compose = DockerComposeExecutor(compose_path, project_name)

        for command in [compose.down, compose.up]:
            try:
                code, out, err = await command()
                debug_info.extend([
                    f"\n=== {command.__name__.capitalize()} Command ===",
                    f"Return Code: {code}",
                    f"Stdout: {out}",
                    f"Stderr: {err}"
                ])

                if code != 0 and command == compose.up:
                    raise Exception(f"Deploy failed with code {code}: {err}")
            except Exception as e:
                if command != compose.down:
                    raise e
                debug_info.append(f"Warning during {command.__name__}: {str(e)}")

        code, out, err = await compose.ps()
        service_info = out if code == 0 else "Unable to list services"

        return (f"Successfully deployed compose stack '{project_name}'\n"
                f"Running services:\n{service_info}\n\n"
                f"Debug Info:\n{chr(10).join(debug_info)}")

    @staticmethod
    def _cleanup_files(compose_path: str) -> None:
        """Clean up temporary files.
        
        Args:
            compose_path: Path to the compose file
        """
        try:
            if os.path.exists(compose_path):
                os.remove(compose_path)
            compose_dir = os.path.dirname(compose_path)
            if os.path.exists(compose_dir) and not os.listdir(compose_dir):
                os.rmdir(compose_dir)
        except Exception as e:
            logger.error(f"Warning during cleanup: {str(e)}")

    @staticmethod
    async def handle_get_logs(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get-logs tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            container_name = arguments.get("container_name")
            tail = int(arguments.get("tail", 100))
            
            if not container_name:
                raise ValueError("Missing required container_name")

            debug_info.append(f"Fetching logs for container '{container_name}'")
            
            docker = DockerExecutor()
            code, logs, err = await docker.logs(container_name, tail=tail)
            
            if code != 0:
                raise RuntimeError(f"Error retrieving logs: {err}")

            return [TextContent(
                type="text", 
                text=f"Logs for container '{container_name}':\n{logs}\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error retrieving logs: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error retrieving logs: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]

    @staticmethod
    async def handle_list_containers(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle list-containers tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            all_containers = arguments.get("all", True)
            debug_info.append(f"Listing {'all' if all_containers else 'running'} Docker containers")
            
            docker = DockerExecutor()
            code, out, err = await docker.ps(all=all_containers)
            
            if code != 0:
                raise RuntimeError(f"Error listing containers: {err}")

            return [TextContent(
                type="text", 
                text=f"Docker Containers:\n{out}\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error listing containers: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error listing containers: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_stop_container(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle stop-container tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            container_name = arguments.get("container_name")
            if not container_name:
                raise ValueError("Missing required container_name")

            debug_info.append(f"Stopping container '{container_name}'")
            
            docker = DockerExecutor()
            code, out, err = await docker.stop(container_name)
            
            if code != 0:
                raise RuntimeError(f"Error stopping container: {err}")

            return [TextContent(
                type="text", 
                text=f"Container '{container_name}' stopped successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error stopping container: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error stopping container: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_start_container(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle start-container tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            container_name = arguments.get("container_name")
            if not container_name:
                raise ValueError("Missing required container_name")

            debug_info.append(f"Starting container '{container_name}'")
            
            docker = DockerExecutor()
            code, out, err = await docker.start(container_name)
            
            if code != 0:
                raise RuntimeError(f"Error starting container: {err}")

            return [TextContent(
                type="text", 
                text=f"Container '{container_name}' started successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error starting container: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error starting container: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_restart_container(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle restart-container tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            container_name = arguments.get("container_name")
            if not container_name:
                raise ValueError("Missing required container_name")

            debug_info.append(f"Restarting container '{container_name}'")
            
            docker = DockerExecutor()
            code, out, err = await docker.restart(container_name)
            
            if code != 0:
                raise RuntimeError(f"Error restarting container: {err}")

            return [TextContent(
                type="text", 
                text=f"Container '{container_name}' restarted successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error restarting container: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error restarting container: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_remove_container(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle remove-container tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            container_name = arguments.get("container_name")
            force = arguments.get("force", False)
            
            if not container_name:
                raise ValueError("Missing required container_name")

            debug_info.append(f"Removing container '{container_name}' (force: {force})")
            
            docker = DockerExecutor()
            code, out, err = await docker.rm(container_name, force=force)
            
            if code != 0:
                raise RuntimeError(f"Error removing container: {err}")

            return [TextContent(
                type="text", 
                text=f"Container '{container_name}' removed successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error removing container: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error removing container: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_network_create(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle network-create tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            network_name = arguments.get("name")
            driver = arguments.get("driver")
            
            if not network_name:
                raise ValueError("Missing required network name")

            debug_info.append(f"Creating network '{network_name}' (driver: {driver})")
            
            docker = DockerExecutor()
            code, out, err = await docker.network_create(network_name, driver)
            
            if code != 0:
                raise RuntimeError(f"Error creating network: {err}")

            return [TextContent(
                type="text", 
                text=f"Network '{network_name}' created successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error creating network: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error creating network: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_network_remove(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle network-remove tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            network_name = arguments.get("name")
            
            if not network_name:
                raise ValueError("Missing required network name")

            debug_info.append(f"Removing network '{network_name}'")
            
            docker = DockerExecutor()
            code, out, err = await docker.network_rm(network_name)
            
            if code != 0:
                raise RuntimeError(f"Error removing network: {err}")

            return [TextContent(
                type="text", 
                text=f"Network '{network_name}' removed successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error removing network: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error removing network: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_network_list(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle network-list tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            debug_info.append("Listing networks")
            
            docker = DockerExecutor()
            code, out, err = await docker.network_ls()
            
            if code != 0:
                raise RuntimeError(f"Error listing networks: {err}")

            return [TextContent(
                type="text", 
                text=f"Docker Networks:\n{out}\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error listing networks: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error listing networks: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_network_connect(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle network-connect tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            network_name = arguments.get("network")
            container_name = arguments.get("container")
            
            if not network_name or not container_name:
                raise ValueError("Missing required network or container name")

            debug_info.append(f"Connecting container '{container_name}' to network '{network_name}'")
            
            docker = DockerExecutor()
            code, out, err = await docker.network_connect(network_name, container_name)
            
            if code != 0:
                raise RuntimeError(f"Error connecting container to network: {err}")

            return [TextContent(
                type="text", 
                text=f"Container '{container_name}' connected to network '{network_name}' successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error connecting container to network: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error connecting container to network: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_network_disconnect(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle network-disconnect tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            network_name = arguments.get("network")
            container_name = arguments.get("container")
            
            if not network_name or not container_name:
                raise ValueError("Missing required network or container name")

            debug_info.append(f"Disconnecting container '{container_name}' from network '{network_name}'")
            
            docker = DockerExecutor()
            code, out, err = await docker.network_disconnect(network_name, container_name)
            
            if code != 0:
                raise RuntimeError(f"Error disconnecting container from network: {err}")

            return [TextContent(
                type="text", 
                text=f"Container '{container_name}' disconnected from network '{network_name}' successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error disconnecting container from network: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error disconnecting container from network: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_network_inspect(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle network-inspect tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            network_name = arguments.get("name")
            
            if not network_name:
                raise ValueError("Missing required network name")

            debug_info.append(f"Inspecting network '{network_name}'")
            
            docker = DockerExecutor()
            code, out, err = await docker.network_inspect(network_name)
            
            if code != 0:
                raise RuntimeError(f"Error inspecting network: {err}")

            return [TextContent(
                type="text", 
                text=f"Network '{network_name}' details:\n{out}\n\nDebug Info:\n{chr(10).join(debug_info)}"
            )]
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error inspecting network: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error inspecting network: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_compose_logs(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle compose-logs tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            project_name = arguments.get("project_name")
            service = arguments.get("service")
            compose_file = arguments.get("compose_file")
            
            if not project_name or not compose_file:
                raise ValueError("Missing required project_name or compose_file")

            debug_info.append(f"Fetching logs for compose project '{project_name}'")
            
            # Save compose file if it's provided as YAML content
            if not os.path.exists(compose_file) and compose_file.strip().startswith(('version:', 'services:')):
                yaml_content = DockerHandlers._process_yaml(compose_file, debug_info)
                compose_file = DockerHandlers._save_compose_file(yaml_content, project_name)
                cleanup_needed = True
            else:
                cleanup_needed = False
                
            try:
                compose = DockerComposeExecutor(compose_file, project_name)
                code, logs, err = await compose.logs(service)
                
                if code != 0:
                    raise RuntimeError(f"Error retrieving logs: {err}")

                return [TextContent(
                    type="text", 
                    text=f"Logs for compose project '{project_name}'{f' service {service}' if service else ''}:\n{logs}\n\nDebug Info:\n{chr(10).join(debug_info)}"
                )]
            finally:
                if cleanup_needed:
                    DockerHandlers._cleanup_files(compose_file)
                    
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error retrieving compose logs: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error retrieving compose logs: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_compose_ps(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle compose-ps tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            project_name = arguments.get("project_name")
            compose_file = arguments.get("compose_file")
            
            if not project_name or not compose_file:
                raise ValueError("Missing required project_name or compose_file")

            debug_info.append(f"Listing services for compose project '{project_name}'")
            
            # Save compose file if it's provided as YAML content
            if not os.path.exists(compose_file) and compose_file.strip().startswith(('version:', 'services:')):
                yaml_content = DockerHandlers._process_yaml(compose_file, debug_info)
                compose_file = DockerHandlers._save_compose_file(yaml_content, project_name)
                cleanup_needed = True
            else:
                cleanup_needed = False
                
            try:
                compose = DockerComposeExecutor(compose_file, project_name)
                code, out, err = await compose.ps()
                
                if code != 0:
                    raise RuntimeError(f"Error listing services: {err}")

                return [TextContent(
                    type="text", 
                    text=f"Services for compose project '{project_name}':\n{out}\n\nDebug Info:\n{chr(10).join(debug_info)}"
                )]
            finally:
                if cleanup_needed:
                    DockerHandlers._cleanup_files(compose_file)
                    
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error listing compose services: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error listing compose services: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_compose_stop(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle compose-stop tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            project_name = arguments.get("project_name")
            service = arguments.get("service")
            compose_file = arguments.get("compose_file")
            
            if not project_name or not compose_file:
                raise ValueError("Missing required project_name or compose_file")

            debug_info.append(f"Stopping compose project '{project_name}'")
            
            # Save compose file if it's provided as YAML content
            if not os.path.exists(compose_file) and compose_file.strip().startswith(('version:', 'services:')):
                yaml_content = DockerHandlers._process_yaml(compose_file, debug_info)
                compose_file = DockerHandlers._save_compose_file(yaml_content, project_name)
                cleanup_needed = True
            else:
                cleanup_needed = False
                
            try:
                compose = DockerComposeExecutor(compose_file, project_name)
                code, out, err = await compose.stop(service)
                
                if code != 0:
                    raise RuntimeError(f"Error stopping services: {err}")

                return [TextContent(
                    type="text", 
                    text=f"Compose project '{project_name}'{f' service {service}' if service else ''} stopped successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
                )]
            finally:
                if cleanup_needed:
                    DockerHandlers._cleanup_files(compose_file)
                    
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error stopping compose services: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error stopping compose services: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_compose_start(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle compose-start tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            project_name = arguments.get("project_name")
            service = arguments.get("service")
            compose_file = arguments.get("compose_file")
            
            if not project_name or not compose_file:
                raise ValueError("Missing required project_name or compose_file")

            debug_info.append(f"Starting compose project '{project_name}'")
            
            # Save compose file if it's provided as YAML content
            if not os.path.exists(compose_file) and compose_file.strip().startswith(('version:', 'services:')):
                yaml_content = DockerHandlers._process_yaml(compose_file, debug_info)
                compose_file = DockerHandlers._save_compose_file(yaml_content, project_name)
                cleanup_needed = True
            else:
                cleanup_needed = False
                
            try:
                compose = DockerComposeExecutor(compose_file, project_name)
                code, out, err = await compose.start(service)
                
                if code != 0:
                    raise RuntimeError(f"Error starting services: {err}")

                return [TextContent(
                    type="text", 
                    text=f"Compose project '{project_name}'{f' service {service}' if service else ''} started successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
                )]
            finally:
                if cleanup_needed:
                    DockerHandlers._cleanup_files(compose_file)
                    
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error starting compose services: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error starting compose services: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]
            
    @staticmethod
    async def handle_compose_restart(arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle compose-restart tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the result
        """
        debug_info = []
        try:
            project_name = arguments.get("project_name")
            service = arguments.get("service")
            compose_file = arguments.get("compose_file")
            
            if not project_name or not compose_file:
                raise ValueError("Missing required project_name or compose_file")

            debug_info.append(f"Restarting compose project '{project_name}'")
            
            # Save compose file if it's provided as YAML content
            if not os.path.exists(compose_file) and compose_file.strip().startswith(('version:', 'services:')):
                yaml_content = DockerHandlers._process_yaml(compose_file, debug_info)
                compose_file = DockerHandlers._save_compose_file(yaml_content, project_name)
                cleanup_needed = True
            else:
                cleanup_needed = False
                
            try:
                compose = DockerComposeExecutor(compose_file, project_name)
                code, out, err = await compose.restart(service)
                
                if code != 0:
                    raise RuntimeError(f"Error restarting services: {err}")

                return [TextContent(
                    type="text", 
                    text=f"Compose project '{project_name}'{f' service {service}' if service else ''} restarted successfully\n\nDebug Info:\n{chr(10).join(debug_info)}"
                )]
            finally:
                if cleanup_needed:
                    DockerHandlers._cleanup_files(compose_file)
                    
        except Exception as e:
            debug_output = "\n".join(debug_info)
            logger.error(f"Error restarting compose services: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error restarting compose services: {str(e)}\n\nDebug Information:\n{debug_output}"
            )]