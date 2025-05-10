"""
Configuration management module for the Dev-Server-Workflow project.

This module provides a unified configuration management system for all components
of the Dev-Server-Workflow project, supporting JSON, YAML, and environment variables.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .logger import get_logger
from .constants import CONFIG_DIR

logger = get_logger("config_manager")

class ConfigManager:
    """
    Manager for configurations from different sources.
    
    This class provides methods for loading, validating, and saving configurations
    from different sources such as files and environment variables.
    """
    
    def __init__(self, config_dir: Union[str, Path] = CONFIG_DIR):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = Path(config_dir)
        self.configs = {}
        
        # Create the configuration directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
    
    def load_json_config(self, name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load a JSON configuration file.
        
        Args:
            name: Name of the configuration file (without .json extension)
            default: Default configuration if the file doesn't exist
            
        Returns:
            Dict with the configuration
        """
        config_file = self.config_dir / f"{name}.json"
        
        if name in self.configs:
            return self.configs[name]
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                self.configs[name] = config
                return config
            except Exception as e:
                logger.error(f"Error loading configuration file {config_file}: {e}")
                if default is not None:
                    logger.info(f"Using default configuration for {name}")
                    self.configs[name] = default
                    return default
                raise
        else:
            if default is not None:
                logger.info(f"Configuration file {config_file} not found. Using default configuration.")
                self.configs[name] = default
                return default
            else:
                logger.error(f"Configuration file {config_file} not found and no default configuration provided.")
                raise FileNotFoundError(f"Configuration file {config_file} not found")
    
    def load_yaml_config(self, name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load a YAML configuration file.
        
        Args:
            name: Name of the configuration file (without .yaml extension)
            default: Default configuration if the file doesn't exist
            
        Returns:
            Dict with the configuration
        """
        config_file = self.config_dir / f"{name}.yaml"
        
        if name in self.configs:
            return self.configs[name]
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                self.configs[name] = config
                return config
            except Exception as e:
                logger.error(f"Error loading configuration file {config_file}: {e}")
                if default is not None:
                    logger.info(f"Using default configuration for {name}")
                    self.configs[name] = default
                    return default
                raise
        else:
            if default is not None:
                logger.info(f"Configuration file {config_file} not found. Using default configuration.")
                self.configs[name] = default
                return default
            else:
                logger.error(f"Configuration file {config_file} not found and no default configuration provided.")
                raise FileNotFoundError(f"Configuration file {config_file} not found")
    
    def save_json_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Save a configuration as a JSON file.
        
        Args:
            name: Name of the configuration file (without .json extension)
            config: Configuration to save
        """
        config_file = self.config_dir / f"{name}.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.configs[name] = config
            logger.info(f"Configuration {name} saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration file {config_file}: {e}")
            raise
    
    def save_yaml_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Save a configuration as a YAML file.
        
        Args:
            name: Name of the configuration file (without .yaml extension)
            config: Configuration to save
        """
        config_file = self.config_dir / f"{name}.yaml"
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            self.configs[name] = config
            logger.info(f"Configuration {name} saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration file {config_file}: {e}")
            raise
    
    def get_config(self, name: str) -> Dict[str, Any]:
        """
        Get an already loaded configuration.
        
        Args:
            name: Name of the configuration
            
        Returns:
            Dict with the configuration
            
        Raises:
            KeyError: If the configuration hasn't been loaded
        """
        if name not in self.configs:
            raise KeyError(f"Configuration {name} hasn't been loaded")
        
        return self.configs[name]
    
    def update_config(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a configuration.
        
        Args:
            name: Name of the configuration
            updates: Updates for the configuration
            
        Returns:
            Dict with the updated configuration
            
        Raises:
            KeyError: If the configuration hasn't been loaded
        """
        if name not in self.configs:
            raise KeyError(f"Configuration {name} hasn't been loaded")
        
        config = self.configs[name]
        self._deep_update(config, updates)
        self.configs[name] = config
        
        return config
    
    def _deep_update(self, d: Dict[str, Any], u: Dict[str, Any]) -> None:
        """
        Update a dictionary recursively.
        
        Args:
            d: Dictionary to update
            u: Dictionary with updates
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
    
    def load_env_config(self, prefix: str = "", env_vars: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Args:
            prefix: Prefix for environment variables
            env_vars: List of environment variables to load
            
        Returns:
            Dict with the configuration
        """
        config = {}
        
        # If no specific environment variables were provided, load all
        if env_vars is None:
            # Load all environment variables with the specified prefix
            for key, value in os.environ.items():
                if prefix and not key.startswith(prefix):
                    continue
                
                # Remove the prefix
                if prefix:
                    config_key = key[len(prefix):].lower()
                else:
                    config_key = key.lower()
                
                # Convert the value
                config[config_key] = self._convert_env_value(value)
        else:
            # Load only the specified environment variables
            for key in env_vars:
                env_key = f"{prefix}{key}" if prefix else key
                value = os.environ.get(env_key)
                
                if value is not None:
                    config[key.lower()] = self._convert_env_value(value)
        
        return config
    
    def _convert_env_value(self, value: str) -> Any:
        """
        Convert an environment variable value to the corresponding Python type.
        
        Args:
            value: Value of the environment variable
            
        Returns:
            Converted value
        """
        # Try to parse the value as JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # Try to parse the value as a number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Try to parse the value as a boolean
        if value.lower() in ('true', 'yes', '1', 'y'):
            return True
        elif value.lower() in ('false', 'no', '0', 'n'):
            return False
        
        # Otherwise return the value as a string
        return value
    
    def load_env_file(self, env_file: Union[str, Path] = ".env") -> Dict[str, Any]:
        """
        Load environment variables from a .env file.
        
        Args:
            env_file: Path to the .env file
            
        Returns:
            Dict with the loaded environment variables
        """
        env_file = Path(env_file)
        
        if not env_file.exists():
            logger.warning(f".env file not found: {env_file}")
            return {}
        
        config = {}
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key-value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Set environment variable
                        os.environ[key] = value
                        
                        # Add to configuration
                        config[key] = self._convert_env_value(value)
            
            logger.info(f"Environment variables loaded from {env_file}")
        except Exception as e:
            logger.error(f"Error loading .env file {env_file}: {e}")
        
        return config