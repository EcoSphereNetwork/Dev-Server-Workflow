"""
Comprehensive error handling module for the Dev-Server-Workflow application.
This module provides structured error classes and utilities for consistent error handling.
"""

import logging
import sys
import traceback
from enum import Enum
from typing import Dict, Any, Optional, List, Type, Union

# Configure logger
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Enum representing the severity of an error."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class ErrorCategory(Enum):
    """Enum representing the category of an error."""
    CONFIGURATION = "configuration"
    NETWORK = "network"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    RESOURCE = "resource"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    UNKNOWN = "unknown"

class BaseError(Exception):
    """Base error class for all application errors."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        code: str = "ERR_UNKNOWN",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize a new BaseError.
        
        Args:
            message: Human-readable error message
            category: Category of the error
            severity: Severity level of the error
            code: Error code for programmatic identification
            details: Additional error details
            cause: Original exception that caused this error
        """
        self.message = message
        self.category = category
        self.severity = severity
        self.code = code
        self.details = details or {}
        self.cause = cause
        
        # Capture stack trace
        self.stack_trace = traceback.format_exc()
        
        # Log the error based on severity
        self._log_error()
        
        super().__init__(message)
    
    def _log_error(self) -> None:
        """Log the error based on its severity."""
        log_message = f"{self.code}: {self.message}"
        
        if self.details:
            log_message += f" - Details: {self.details}"
        
        if self.cause:
            log_message += f" - Caused by: {str(self.cause)}"
        
        if self.severity == ErrorSeverity.DEBUG:
            logger.debug(log_message)
        elif self.severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif self.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif self.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary representation.
        
        Returns:
            Dictionary representation of the error
        """
        error_dict = {
            "code": self.code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.name,
        }
        
        if self.details:
            error_dict["details"] = self.details
        
        return error_dict

# Configuration Errors
class ConfigurationError(BaseError):
    """Error raised when there is a configuration issue."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.ERROR,
            code="ERR_CONFIGURATION",
            details=details,
            cause=cause
        )

class MissingConfigurationError(ConfigurationError):
    """Error raised when a required configuration is missing."""
    
    def __init__(
        self,
        config_key: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        message = f"Missing required configuration: {config_key}"
        super().__init__(
            message=message,
            details=details,
            cause=cause
        )
        self.code = "ERR_MISSING_CONFIG"
        self.config_key = config_key

# Network Errors
class NetworkError(BaseError):
    """Error raised when there is a network issue."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.ERROR,
            code="ERR_NETWORK",
            details=details,
            cause=cause
        )

class ConnectionError(NetworkError):
    """Error raised when a connection cannot be established."""
    
    def __init__(
        self,
        host: str,
        port: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        endpoint = host
        if port is not None:
            endpoint = f"{host}:{port}"
        
        message = f"Failed to connect to {endpoint}"
        super().__init__(
            message=message,
            details=details,
            cause=cause
        )
        self.code = "ERR_CONNECTION"
        self.host = host
        self.port = port

class TimeoutError(NetworkError):
    """Error raised when a network operation times out."""
    
    def __init__(
        self,
        operation: str,
        timeout: float,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(
            message=message,
            details=details,
            cause=cause
        )
        self.code = "ERR_TIMEOUT"
        self.operation = operation
        self.timeout = timeout

# Authentication and Authorization Errors
class AuthenticationError(BaseError):
    """Error raised when authentication fails."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.ERROR,
            code="ERR_AUTHENTICATION",
            details=details,
            cause=cause
        )

class AuthorizationError(BaseError):
    """Error raised when authorization fails."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.ERROR,
            code="ERR_AUTHORIZATION",
            details=details,
            cause=cause
        )

# Validation Errors
class ValidationError(BaseError):
    """Error raised when validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            code="ERR_VALIDATION",
            details=details,
            cause=cause
        )
        self.field = field

# Resource Errors
class ResourceError(BaseError):
    """Error raised when there is an issue with a resource."""
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.ERROR,
            code="ERR_RESOURCE",
            details=details,
            cause=cause
        )
        self.resource_type = resource_type
        self.resource_id = resource_id

class ResourceNotFoundError(ResourceError):
    """Error raised when a resource is not found."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(
            message=message,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            cause=cause
        )
        self.code = "ERR_RESOURCE_NOT_FOUND"

# External Service Errors
class ExternalServiceError(BaseError):
    """Error raised when there is an issue with an external service."""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.ERROR,
            code="ERR_EXTERNAL_SERVICE",
            details=details,
            cause=cause
        )
        self.service_name = service_name

# MCP Specific Errors
class MCPError(BaseError):
    """Error raised when there is an issue with an MCP component."""
    
    def __init__(
        self,
        message: str,
        mcp_component: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.ERROR,
            code="ERR_MCP",
            details=details,
            cause=cause
        )
        self.mcp_component = mcp_component

class MCPServerError(MCPError):
    """Error raised when there is an issue with an MCP server."""
    
    def __init__(
        self,
        message: str,
        server_type: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            mcp_component=f"{server_type}_server",
            details=details,
            cause=cause
        )
        self.code = "ERR_MCP_SERVER"
        self.server_type = server_type

# Error Handler
class ErrorHandler:
    """Utility class for handling errors consistently."""
    
    @staticmethod
    def handle_error(
        error: Union[BaseError, Exception],
        default_message: str = "An unexpected error occurred",
        log_error: bool = True,
        raise_error: bool = False,
        error_map: Optional[Dict[Type[Exception], Type[BaseError]]] = None
    ) -> Dict[str, Any]:
        """
        Handle an error consistently.
        
        Args:
            error: The error to handle
            default_message: Default message to use if error is not a BaseError
            log_error: Whether to log the error
            raise_error: Whether to re-raise the error after handling
            error_map: Mapping of exception types to BaseError types
        
        Returns:
            Dictionary representation of the error
        
        Raises:
            The original error if raise_error is True
        """
        # Convert standard exceptions to BaseError if needed
        if not isinstance(error, BaseError):
            if error_map and type(error) in error_map:
                error_class = error_map[type(error)]
                error = error_class(str(error), cause=error)
            else:
                error = BaseError(
                    message=str(error) or default_message,
                    category=ErrorCategory.UNKNOWN,
                    severity=ErrorSeverity.ERROR,
                    code="ERR_UNKNOWN",
                    cause=error
                )
        
        # Log the error if requested
        if log_error:
            logger.error(f"Handled error: {error.code} - {error.message}")
            if error.cause:
                logger.error(f"Caused by: {error.cause}")
        
        # Re-raise the error if requested
        if raise_error:
            raise error
        
        # Return the error as a dictionary
        return error.to_dict()

# Global error handler for uncaught exceptions
def setup_global_error_handler() -> None:
    """Set up a global error handler for uncaught exceptions."""
    
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't handle keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Set the exception hook
    sys.excepthook = global_exception_handler