"""
Authentication and authorization module for Docker MCP server.

This module provides authentication and authorization functionality for the Docker MCP server.
"""

import os
import json
import logging
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Tuple, Any, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("docker-mcp-auth")

# Default configuration
DEFAULT_CONFIG = {
    "users": {
        "admin": {
            "api_key": "admin_api_key",
            "role": "admin"
        },
        "user": {
            "api_key": "user_api_key",
            "role": "user"
        }
    },
    "roles": {
        "admin": {
            "permissions": ["*"]
        },
        "user": {
            "permissions": [
                "list-containers",
                "get-logs",
                "network-list",
                "network-inspect",
                "compose-ps",
                "compose-logs"
            ]
        }
    },
    "auto_approve": [
        "list-containers",
        "get-logs",
        "network-list",
        "compose-ps",
        "compose-logs"
    ]
}


class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the authentication manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.users = self.config.get("users", {})
        self.roles = self.config.get("roles", {})
        self.auto_approve = set(self.config.get("auto_approve", []))
        self.tokens: Dict[str, Dict[str, Any]] = {}
        
        # Create a secret key for token signing
        self.secret_key = os.environ.get("MCP_AUTH_SECRET", os.urandom(32).hex())
        
    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from file or use default.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_path or not os.path.exists(self.config_path):
            logger.warning("No configuration file found, using default configuration")
            return DEFAULT_CONFIG
            
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return DEFAULT_CONFIG
            
    def _save_config(self) -> bool:
        """Save the configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.config_path:
            logger.warning("No configuration file path specified, cannot save configuration")
            return False
            
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
                logger.info(f"Saved configuration to {self.config_path}")
                return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
            
    def authenticate(self, username: str, api_key: str) -> Optional[str]:
        """Authenticate a user and return a token.
        
        Args:
            username: Username
            api_key: API key
            
        Returns:
            Token if authentication successful, None otherwise
        """
        if username not in self.users:
            logger.warning(f"Authentication failed: User {username} not found")
            return None
            
        user = self.users[username]
        if user.get("api_key") != api_key:
            logger.warning(f"Authentication failed: Invalid API key for user {username}")
            return None
            
        # Generate a token
        token = self._generate_token(username)
        
        # Store token information
        self.tokens[token] = {
            "username": username,
            "role": user.get("role", "user"),
            "created_at": time.time(),
            "expires_at": time.time() + 3600  # 1 hour expiration
        }
        
        logger.info(f"Authentication successful for user {username}")
        return token
        
    def _generate_token(self, username: str) -> str:
        """Generate a token for a user.
        
        Args:
            username: Username
            
        Returns:
            Token
        """
        timestamp = str(int(time.time()))
        message = f"{username}:{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{message}:{signature}"
        
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a token and return user information.
        
        Args:
            token: Token
            
        Returns:
            User information if token is valid, None otherwise
        """
        if token not in self.tokens:
            logger.warning(f"Token validation failed: Token not found")
            return None
            
        token_info = self.tokens[token]
        
        # Check if token has expired
        if token_info.get("expires_at", 0) < time.time():
            logger.warning(f"Token validation failed: Token expired")
            del self.tokens[token]
            return None
            
        return token_info
        
    def is_authorized(self, token: str, tool_name: str) -> bool:
        """Check if a user is authorized to use a tool.
        
        Args:
            token: Token
            tool_name: Tool name
            
        Returns:
            True if authorized, False otherwise
        """
        # Auto-approve tools don't require authorization
        if tool_name in self.auto_approve:
            return True
            
        token_info = self.validate_token(token)
        if not token_info:
            logger.warning(f"Authorization failed: Invalid token")
            return False
            
        role_name = token_info.get("role", "user")
        if role_name not in self.roles:
            logger.warning(f"Authorization failed: Role {role_name} not found")
            return False
            
        role = self.roles[role_name]
        permissions = role.get("permissions", [])
        
        # Check if user has wildcard permission
        if "*" in permissions:
            return True
            
        # Check if user has permission for this tool
        if tool_name in permissions:
            return True
            
        logger.warning(f"Authorization failed: User {token_info.get('username')} does not have permission to use {tool_name}")
        return False
        
    def get_auto_approve_tools(self) -> Set[str]:
        """Get the list of auto-approve tools.
        
        Returns:
            Set of auto-approve tool names
        """
        return self.auto_approve
        
    def add_user(self, username: str, api_key: str, role: str = "user") -> bool:
        """Add a new user.
        
        Args:
            username: Username
            api_key: API key
            role: Role
            
        Returns:
            True if successful, False otherwise
        """
        if username in self.users:
            logger.warning(f"User {username} already exists")
            return False
            
        if role not in self.roles:
            logger.warning(f"Role {role} not found")
            return False
            
        self.users[username] = {
            "api_key": api_key,
            "role": role
        }
        
        self.config["users"] = self.users
        return self._save_config()
        
    def remove_user(self, username: str) -> bool:
        """Remove a user.
        
        Args:
            username: Username
            
        Returns:
            True if successful, False otherwise
        """
        if username not in self.users:
            logger.warning(f"User {username} not found")
            return False
            
        del self.users[username]
        
        # Remove any tokens for this user
        tokens_to_remove = []
        for token, token_info in self.tokens.items():
            if token_info.get("username") == username:
                tokens_to_remove.append(token)
                
        for token in tokens_to_remove:
            del self.tokens[token]
            
        self.config["users"] = self.users
        return self._save_config()
        
    def add_role(self, role_name: str, permissions: List[str]) -> bool:
        """Add a new role.
        
        Args:
            role_name: Role name
            permissions: List of permissions
            
        Returns:
            True if successful, False otherwise
        """
        if role_name in self.roles:
            logger.warning(f"Role {role_name} already exists")
            return False
            
        self.roles[role_name] = {
            "permissions": permissions
        }
        
        self.config["roles"] = self.roles
        return self._save_config()
        
    def remove_role(self, role_name: str) -> bool:
        """Remove a role.
        
        Args:
            role_name: Role name
            
        Returns:
            True if successful, False otherwise
        """
        if role_name not in self.roles:
            logger.warning(f"Role {role_name} not found")
            return False
            
        # Check if any users have this role
        for username, user in self.users.items():
            if user.get("role") == role_name:
                logger.warning(f"Cannot remove role {role_name} because user {username} has this role")
                return False
                
        del self.roles[role_name]
        
        self.config["roles"] = self.roles
        return self._save_config()
        
    def update_auto_approve(self, tools: List[str]) -> bool:
        """Update the list of auto-approve tools.
        
        Args:
            tools: List of tool names
            
        Returns:
            True if successful, False otherwise
        """
        self.auto_approve = set(tools)
        self.config["auto_approve"] = list(self.auto_approve)
        return self._save_config()
        
    def get_audit_log(self, username: Optional[str] = None, tool_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the audit log.
        
        Args:
            username: Filter by username
            tool_name: Filter by tool name
            
        Returns:
            List of audit log entries
        """
        # This is a placeholder for a real audit log implementation
        # In a real implementation, this would query a database or log file
        return []