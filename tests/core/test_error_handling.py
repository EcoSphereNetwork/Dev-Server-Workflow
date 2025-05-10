"""
Unit tests for the error handling module.
"""

import unittest
import logging
from src.core.error_handling import (
    BaseError, ConfigurationError, NetworkError, ValidationError,
    AuthenticationError, AuthorizationError, ResourceError,
    ResourceNotFoundError, ExternalServiceError, MCPError, MCPServerError,
    ErrorHandler, ErrorCategory, ErrorSeverity
)

class TestBaseError(unittest.TestCase):
    """Test cases for the BaseError class."""
    
    def test_base_error_initialization(self):
        """Test that BaseError initializes correctly."""
        error = BaseError("Test error message")
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.category, ErrorCategory.UNKNOWN)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_UNKNOWN")
        self.assertEqual(error.details, {})
        self.assertIsNone(error.cause)
        
    def test_base_error_with_details(self):
        """Test that BaseError handles details correctly."""
        details = {"key": "value", "number": 42}
        error = BaseError("Test error message", details=details)
        self.assertEqual(error.details, details)
        
    def test_base_error_with_cause(self):
        """Test that BaseError handles cause correctly."""
        cause = ValueError("Original error")
        error = BaseError("Test error message", cause=cause)
        self.assertEqual(error.cause, cause)
        
    def test_base_error_to_dict(self):
        """Test that BaseError.to_dict() returns the correct dictionary."""
        error = BaseError(
            message="Test error message",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.WARNING,
            code="TEST_ERROR",
            details={"key": "value"}
        )
        error_dict = error.to_dict()
        self.assertEqual(error_dict["message"], "Test error message")
        self.assertEqual(error_dict["category"], "configuration")
        self.assertEqual(error_dict["severity"], "WARNING")
        self.assertEqual(error_dict["code"], "TEST_ERROR")
        self.assertEqual(error_dict["details"], {"key": "value"})

class TestConfigurationError(unittest.TestCase):
    """Test cases for the ConfigurationError class."""
    
    def test_configuration_error_initialization(self):
        """Test that ConfigurationError initializes correctly."""
        error = ConfigurationError("Missing configuration")
        self.assertEqual(error.message, "Missing configuration")
        self.assertEqual(error.category, ErrorCategory.CONFIGURATION)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_CONFIGURATION")
        
class TestMissingConfigurationError(unittest.TestCase):
    """Test cases for the MissingConfigurationError class."""
    
    def test_missing_configuration_error_initialization(self):
        """Test that MissingConfigurationError initializes correctly."""
        error = ConfigurationError("Missing configuration")
        self.assertEqual(error.message, "Missing configuration")
        self.assertEqual(error.category, ErrorCategory.CONFIGURATION)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_CONFIGURATION")

class TestNetworkError(unittest.TestCase):
    """Test cases for the NetworkError class."""
    
    def test_network_error_initialization(self):
        """Test that NetworkError initializes correctly."""
        error = NetworkError("Connection failed")
        self.assertEqual(error.message, "Connection failed")
        self.assertEqual(error.category, ErrorCategory.NETWORK)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_NETWORK")

class TestConnectionError(unittest.TestCase):
    """Test cases for the ConnectionError class."""
    
    def test_connection_error_initialization(self):
        """Test that ConnectionError initializes correctly."""
        error = NetworkError("Connection failed")
        self.assertEqual(error.message, "Connection failed")
        self.assertEqual(error.category, ErrorCategory.NETWORK)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_NETWORK")

class TestValidationError(unittest.TestCase):
    """Test cases for the ValidationError class."""
    
    def test_validation_error_initialization(self):
        """Test that ValidationError initializes correctly."""
        error = ValidationError("Invalid input")
        self.assertEqual(error.message, "Invalid input")
        self.assertEqual(error.category, ErrorCategory.VALIDATION)
        self.assertEqual(error.severity, ErrorSeverity.WARNING)
        self.assertEqual(error.code, "ERR_VALIDATION")
        
    def test_validation_error_with_field(self):
        """Test that ValidationError handles field correctly."""
        error = ValidationError("Invalid input", field="username")
        self.assertEqual(error.field, "username")

class TestAuthenticationError(unittest.TestCase):
    """Test cases for the AuthenticationError class."""
    
    def test_authentication_error_initialization(self):
        """Test that AuthenticationError initializes correctly."""
        error = AuthenticationError("Authentication failed")
        self.assertEqual(error.message, "Authentication failed")
        self.assertEqual(error.category, ErrorCategory.AUTHENTICATION)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_AUTHENTICATION")

class TestAuthorizationError(unittest.TestCase):
    """Test cases for the AuthorizationError class."""
    
    def test_authorization_error_initialization(self):
        """Test that AuthorizationError initializes correctly."""
        error = AuthorizationError("Authorization failed")
        self.assertEqual(error.message, "Authorization failed")
        self.assertEqual(error.category, ErrorCategory.AUTHORIZATION)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_AUTHORIZATION")

class TestResourceError(unittest.TestCase):
    """Test cases for the ResourceError class."""
    
    def test_resource_error_initialization(self):
        """Test that ResourceError initializes correctly."""
        error = ResourceError("Resource error", resource_type="User")
        self.assertEqual(error.message, "Resource error")
        self.assertEqual(error.category, ErrorCategory.RESOURCE)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_RESOURCE")
        self.assertEqual(error.resource_type, "User")
        self.assertIsNone(error.resource_id)
        
    def test_resource_error_with_id(self):
        """Test that ResourceError handles resource_id correctly."""
        error = ResourceError("Resource error", resource_type="User", resource_id="123")
        self.assertEqual(error.resource_type, "User")
        self.assertEqual(error.resource_id, "123")

class TestResourceNotFoundError(unittest.TestCase):
    """Test cases for the ResourceNotFoundError class."""
    
    def test_resource_not_found_error_initialization(self):
        """Test that ResourceNotFoundError initializes correctly."""
        error = ResourceNotFoundError("User", "123")
        self.assertEqual(error.message, "User with ID '123' not found")
        self.assertEqual(error.category, ErrorCategory.RESOURCE)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_RESOURCE_NOT_FOUND")
        self.assertEqual(error.resource_type, "User")
        self.assertEqual(error.resource_id, "123")

class TestExternalServiceError(unittest.TestCase):
    """Test cases for the ExternalServiceError class."""
    
    def test_external_service_error_initialization(self):
        """Test that ExternalServiceError initializes correctly."""
        error = ExternalServiceError("Service unavailable", service_name="GitHub")
        self.assertEqual(error.message, "Service unavailable")
        self.assertEqual(error.category, ErrorCategory.EXTERNAL_SERVICE)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_EXTERNAL_SERVICE")
        self.assertEqual(error.service_name, "GitHub")

class TestMCPError(unittest.TestCase):
    """Test cases for the MCPError class."""
    
    def test_mcp_error_initialization(self):
        """Test that MCPError initializes correctly."""
        error = MCPError("MCP error", mcp_component="Hub")
        self.assertEqual(error.message, "MCP error")
        self.assertEqual(error.category, ErrorCategory.INTERNAL)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_MCP")
        self.assertEqual(error.mcp_component, "Hub")

class TestMCPServerError(unittest.TestCase):
    """Test cases for the MCPServerError class."""
    
    def test_mcp_server_error_initialization(self):
        """Test that MCPServerError initializes correctly."""
        error = MCPServerError("Server error", server_type="Docker")
        self.assertEqual(error.message, "Server error")
        self.assertEqual(error.category, ErrorCategory.INTERNAL)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.code, "ERR_MCP_SERVER")
        self.assertEqual(error.mcp_component, "Docker_server")
        self.assertEqual(error.server_type, "Docker")

class TestErrorHandler(unittest.TestCase):
    """Test cases for the ErrorHandler class."""
    
    def test_handle_error_with_base_error(self):
        """Test that ErrorHandler.handle_error() handles BaseError correctly."""
        error = BaseError("Test error")
        result = ErrorHandler.handle_error(error, log_error=False, raise_error=False)
        self.assertEqual(result["message"], "Test error")
        self.assertEqual(result["code"], "ERR_UNKNOWN")
        self.assertEqual(result["category"], "unknown")
        
    def test_handle_error_with_standard_exception(self):
        """Test that ErrorHandler.handle_error() handles standard exceptions correctly."""
        error = ValueError("Invalid value")
        result = ErrorHandler.handle_error(error, log_error=False, raise_error=False)
        self.assertEqual(result["message"], "Invalid value")
        self.assertEqual(result["code"], "ERR_UNKNOWN")
        self.assertEqual(result["category"], "unknown")
        
    def test_handle_error_with_error_map(self):
        """Test that ErrorHandler.handle_error() uses error_map correctly."""
        error_map = {ValueError: ConfigurationError}
        error = ValueError("Invalid value")
        result = ErrorHandler.handle_error(error, log_error=False, raise_error=False, error_map=error_map)
        self.assertEqual(result["message"], "Invalid value")
        self.assertEqual(result["code"], "ERR_CONFIGURATION")
        self.assertEqual(result["category"], "configuration")
        
    def test_handle_error_with_raise_error(self):
        """Test that ErrorHandler.handle_error() raises the error when raise_error is True."""
        error = BaseError("Test error")
        with self.assertRaises(BaseError):
            ErrorHandler.handle_error(error, log_error=False, raise_error=True)

if __name__ == '__main__':
    unittest.main()