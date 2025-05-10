"""
Base classes for external service connectors.

This module provides base classes for implementing connectors to external services.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

from src.core.error_handling import BaseError, ErrorCategory, ErrorHandler
from src.core.logging import get_logger
from src.core.performance import async_cached, async_profiled, async_timed

# Set up logging
logger = get_logger(__name__)


class ConnectorError(BaseError):
    """Base class for connector errors."""
    def __init__(
        self,
        message: str,
        connector_type: Optional[str] = None,
        service_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.CONNECTOR,
            code="ERR_CONNECTOR",
            details={
                "connector_type": connector_type,
                "service_name": service_name,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.connector_type = connector_type
        self.service_name = service_name


class ConnectorAuthError(ConnectorError):
    """Error raised when authentication fails."""
    def __init__(
        self,
        message: str,
        connector_type: Optional[str] = None,
        service_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            connector_type=connector_type,
            service_name=service_name,
            code="ERR_CONNECTOR_AUTH",
            **kwargs
        )


class ConnectorTimeoutError(ConnectorError):
    """Error raised when a request times out."""
    def __init__(
        self,
        message: str,
        connector_type: Optional[str] = None,
        service_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            connector_type=connector_type,
            service_name=service_name,
            code="ERR_CONNECTOR_TIMEOUT",
            **kwargs
        )


class ConnectorRateLimitError(ConnectorError):
    """Error raised when rate limits are exceeded."""
    def __init__(
        self,
        message: str,
        connector_type: Optional[str] = None,
        service_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            connector_type=connector_type,
            service_name=service_name,
            code="ERR_CONNECTOR_RATE_LIMIT",
            details={
                "retry_after": retry_after,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.retry_after = retry_after


class ConnectorNotFoundError(ConnectorError):
    """Error raised when a resource is not found."""
    def __init__(
        self,
        message: str,
        connector_type: Optional[str] = None,
        service_name: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            connector_type=connector_type,
            service_name=service_name,
            code="ERR_CONNECTOR_NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class ConnectorValidationError(ConnectorError):
    """Error raised when validation fails."""
    def __init__(
        self,
        message: str,
        connector_type: Optional[str] = None,
        service_name: Optional[str] = None,
        validation_errors: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            connector_type=connector_type,
            service_name=service_name,
            code="ERR_CONNECTOR_VALIDATION",
            details={
                "validation_errors": validation_errors,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.validation_errors = validation_errors


class ConnectorStatus(str, Enum):
    """Status of a connector."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ConnectorConfig:
    """Configuration for a connector."""
    service_name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    api_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, str] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """Base class for all connectors."""

    def __init__(self, config: ConnectorConfig):
        """Initialize the connector.

        Args:
            config: Connector configuration.
        """
        self.config = config
        self.status = ConnectorStatus.DISCONNECTED
        self.last_error: Optional[Exception] = None
        self.connected_at: Optional[datetime] = None
        self.disconnected_at: Optional[datetime] = None

    @property
    def service_name(self) -> str:
        """Get the service name."""
        return self.config.service_name

    @property
    def connector_type(self) -> str:
        """Get the connector type."""
        return self.__class__.__name__

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the service.

        Raises:
            ConnectorError: If connection fails.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the service."""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if the connector is connected.

        Returns:
            True if connected, False otherwise.
        """
        pass

    async def reconnect(self) -> None:
        """Reconnect to the service.

        Raises:
            ConnectorError: If reconnection fails.
        """
        await self.disconnect()
        await self.connect()

    def get_status(self) -> Dict[str, Any]:
        """Get the connector status.

        Returns:
            Dictionary with connector status information.
        """
        return {
            "service_name": self.service_name,
            "connector_type": self.connector_type,
            "status": self.status,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "disconnected_at": self.disconnected_at.isoformat() if self.disconnected_at else None,
            "last_error": str(self.last_error) if self.last_error else None,
        }


class HttpConnector(BaseConnector):
    """Base class for HTTP-based connectors."""

    def __init__(self, config: ConnectorConfig):
        """Initialize the HTTP connector.

        Args:
            config: Connector configuration.
        """
        super().__init__(config)
        self._session = None

    async def connect(self) -> None:
        """Connect to the service.

        Raises:
            ConnectorError: If connection fails.
        """
        import aiohttp

        self.status = ConnectorStatus.CONNECTING

        try:
            # Create a new session
            self._session = aiohttp.ClientSession(
                headers=self.config.headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            )

            # Test the connection
            await self._test_connection()

            # Update status
            self.status = ConnectorStatus.CONNECTED
            self.connected_at = datetime.now()
            self.last_error = None

            logger.info(f"Connected to {self.service_name} using {self.connector_type}")

        except Exception as e:
            self.status = ConnectorStatus.ERROR
            self.last_error = e
            self.disconnected_at = datetime.now()

            logger.error(f"Failed to connect to {self.service_name}: {e}")
            raise ConnectorError(
                f"Failed to connect to {self.service_name}: {e}",
                connector_type=self.connector_type,
                service_name=self.service_name,
                cause=e,
            )

    async def disconnect(self) -> None:
        """Disconnect from the service."""
        if self._session:
            await self._session.close()
            self._session = None

        self.status = ConnectorStatus.DISCONNECTED
        self.disconnected_at = datetime.now()

        logger.info(f"Disconnected from {self.service_name}")

    async def is_connected(self) -> bool:
        """Check if the connector is connected.

        Returns:
            True if connected, False otherwise.
        """
        if self.status != ConnectorStatus.CONNECTED or not self._session:
            return False

        try:
            # Test the connection
            await self._test_connection()
            return True
        except Exception:
            return False

    @abstractmethod
    async def _test_connection(self) -> None:
        """Test the connection to the service.

        Raises:
            ConnectorError: If the connection test fails.
        """
        pass

    @async_timed
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request.

        Args:
            method: HTTP method.
            url: URL to request.
            **kwargs: Additional arguments for the request.

        Returns:
            Response data.

        Raises:
            ConnectorError: If the request fails.
        """
        import aiohttp

        # Ensure we're connected
        if not await self.is_connected():
            await self.connect()

        # Prepare the URL
        if self.config.base_url and not url.startswith(("http://", "https://")):
            url = f"{self.config.base_url.rstrip('/')}/{url.lstrip('/')}"

        # Add default parameters
        params = {**self.config.params, **(kwargs.pop("params", {}) or {})}
        if params:
            kwargs["params"] = params

        # Make the request with retries
        retries = 0
        while True:
            try:
                async with self._session.request(method, url, **kwargs) as response:
                    # Check for rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", self.config.retry_delay))
                        raise ConnectorRateLimitError(
                            f"Rate limit exceeded for {self.service_name}",
                            connector_type=self.connector_type,
                            service_name=self.service_name,
                            retry_after=retry_after,
                        )

                    # Check for authentication errors
                    if response.status in (401, 403):
                        raise ConnectorAuthError(
                            f"Authentication failed for {self.service_name}",
                            connector_type=self.connector_type,
                            service_name=self.service_name,
                        )

                    # Check for not found errors
                    if response.status == 404:
                        raise ConnectorNotFoundError(
                            f"Resource not found: {url}",
                            connector_type=self.connector_type,
                            service_name=self.service_name,
                        )

                    # Check for validation errors
                    if response.status == 422:
                        response_json = await response.json()
                        validation_errors = response_json.get("errors", {})
                        raise ConnectorValidationError(
                            f"Validation failed: {validation_errors}",
                            connector_type=self.connector_type,
                            service_name=self.service_name,
                            validation_errors=validation_errors,
                        )

                    # Check for server errors
                    if response.status >= 500:
                        if retries < self.config.max_retries:
                            retries += 1
                            await asyncio.sleep(self.config.retry_delay * (2 ** (retries - 1)))
                            continue

                        raise ConnectorError(
                            f"Server error: {response.status}",
                            connector_type=self.connector_type,
                            service_name=self.service_name,
                            details={"status_code": response.status},
                        )

                    # Check for other errors
                    if response.status >= 400:
                        raise ConnectorError(
                            f"Request failed with status {response.status}",
                            connector_type=self.connector_type,
                            service_name=self.service_name,
                            details={"status_code": response.status},
                        )

                    # Parse the response
                    try:
                        data = await response.json()
                    except:
                        data = await response.text()

                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "data": data,
                    }

            except aiohttp.ClientError as e:
                if isinstance(e, aiohttp.ClientTimeout):
                    raise ConnectorTimeoutError(
                        f"Request timed out: {url}",
                        connector_type=self.connector_type,
                        service_name=self.service_name,
                        cause=e,
                    )

                if retries < self.config.max_retries:
                    retries += 1
                    await asyncio.sleep(self.config.retry_delay * (2 ** (retries - 1)))
                    continue

                raise ConnectorError(
                    f"Request failed: {e}",
                    connector_type=self.connector_type,
                    service_name=self.service_name,
                    cause=e,
                )

            except ConnectorError:
                # Re-raise connector errors
                raise

            except Exception as e:
                if retries < self.config.max_retries:
                    retries += 1
                    await asyncio.sleep(self.config.retry_delay * (2 ** (retries - 1)))
                    continue

                raise ConnectorError(
                    f"Request failed: {e}",
                    connector_type=self.connector_type,
                    service_name=self.service_name,
                    cause=e,
                )


class DatabaseConnector(BaseConnector):
    """Base class for database connectors."""

    def __init__(self, config: ConnectorConfig):
        """Initialize the database connector.

        Args:
            config: Connector configuration.
        """
        super().__init__(config)
        self._connection = None
        self._pool = None

    @abstractmethod
    async def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a database query.

        Args:
            query: SQL query to execute.
            params: Query parameters.

        Returns:
            Query results.

        Raises:
            ConnectorError: If the query fails.
        """
        pass

    @abstractmethod
    async def execute_many(
        self,
        query: str,
        params_list: List[Dict[str, Any]],
    ) -> None:
        """Execute a database query with multiple parameter sets.

        Args:
            query: SQL query to execute.
            params_list: List of parameter dictionaries.

        Raises:
            ConnectorError: If the query fails.
        """
        pass

    @abstractmethod
    async def transaction(self) -> Any:
        """Start a database transaction.

        Returns:
            Transaction object.

        Raises:
            ConnectorError: If starting the transaction fails.
        """
        pass


class MessageQueueConnector(BaseConnector):
    """Base class for message queue connectors."""

    def __init__(self, config: ConnectorConfig):
        """Initialize the message queue connector.

        Args:
            config: Connector configuration.
        """
        super().__init__(config)
        self._connection = None
        self._channel = None

    @abstractmethod
    async def publish(
        self,
        queue: str,
        message: Union[str, bytes, Dict[str, Any]],
        **kwargs
    ) -> None:
        """Publish a message to a queue.

        Args:
            queue: Queue name.
            message: Message to publish.
            **kwargs: Additional options.

        Raises:
            ConnectorError: If publishing fails.
        """
        pass

    @abstractmethod
    async def consume(
        self,
        queue: str,
        callback: callable,
        **kwargs
    ) -> None:
        """Consume messages from a queue.

        Args:
            queue: Queue name.
            callback: Callback function to process messages.
            **kwargs: Additional options.

        Raises:
            ConnectorError: If consuming fails.
        """
        pass

    @abstractmethod
    async def create_queue(
        self,
        queue: str,
        **kwargs
    ) -> None:
        """Create a queue.

        Args:
            queue: Queue name.
            **kwargs: Additional options.

        Raises:
            ConnectorError: If queue creation fails.
        """
        pass

    @abstractmethod
    async def delete_queue(
        self,
        queue: str,
        **kwargs
    ) -> None:
        """Delete a queue.

        Args:
            queue: Queue name.
            **kwargs: Additional options.

        Raises:
            ConnectorError: If queue deletion fails.
        """
        pass


class FileStorageConnector(BaseConnector):
    """Base class for file storage connectors."""

    def __init__(self, config: ConnectorConfig):
        """Initialize the file storage connector.

        Args:
            config: Connector configuration.
        """
        super().__init__(config)
        self._client = None

    @abstractmethod
    async def upload_file(
        self,
        local_path: str,
        remote_path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload a file.

        Args:
            local_path: Local file path.
            remote_path: Remote file path.
            **kwargs: Additional options.

        Returns:
            File metadata.

        Raises:
            ConnectorError: If upload fails.
        """
        pass

    @abstractmethod
    async def download_file(
        self,
        remote_path: str,
        local_path: str,
        **kwargs
    ) -> None:
        """Download a file.

        Args:
            remote_path: Remote file path.
            local_path: Local file path.
            **kwargs: Additional options.

        Raises:
            ConnectorError: If download fails.
        """
        pass

    @abstractmethod
    async def list_files(
        self,
        path: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List files in a directory.

        Args:
            path: Directory path.
            **kwargs: Additional options.

        Returns:
            List of file metadata.

        Raises:
            ConnectorError: If listing fails.
        """
        pass

    @abstractmethod
    async def delete_file(
        self,
        path: str,
        **kwargs
    ) -> None:
        """Delete a file.

        Args:
            path: File path.
            **kwargs: Additional options.

        Raises:
            ConnectorError: If deletion fails.
        """
        pass

    @abstractmethod
    async def file_exists(
        self,
        path: str,
        **kwargs
    ) -> bool:
        """Check if a file exists.

        Args:
            path: File path.
            **kwargs: Additional options.

        Returns:
            True if the file exists, False otherwise.

        Raises:
            ConnectorError: If the check fails.
        """
        pass


class ConnectorRegistry:
    """Registry for connectors."""

    def __init__(self):
        """Initialize the connector registry."""
        self._connectors: Dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector) -> None:
        """Register a connector.

        Args:
            connector: Connector to register.
        """
        key = f"{connector.connector_type}:{connector.service_name}"
        self._connectors[key] = connector
        logger.info(f"Registered connector: {key}")

    def unregister(self, connector_type: str, service_name: str) -> None:
        """Unregister a connector.

        Args:
            connector_type: Type of connector.
            service_name: Service name.
        """
        key = f"{connector_type}:{service_name}"
        if key in self._connectors:
            del self._connectors[key]
            logger.info(f"Unregistered connector: {key}")

    def get(self, connector_type: str, service_name: str) -> BaseConnector:
        """Get a connector.

        Args:
            connector_type: Type of connector.
            service_name: Service name.

        Returns:
            The connector.

        Raises:
            ConnectorError: If the connector is not found.
        """
        key = f"{connector_type}:{service_name}"
        connector = self._connectors.get(key)
        if not connector:
            raise ConnectorError(
                f"Connector not found: {key}",
                connector_type=connector_type,
                service_name=service_name,
            )
        return connector

    def list(self) -> List[Dict[str, Any]]:
        """List all registered connectors.

        Returns:
            List of connector status dictionaries.
        """
        return [connector.get_status() for connector in self._connectors.values()]

    async def connect_all(self) -> None:
        """Connect all registered connectors.

        Raises:
            ConnectorError: If any connection fails.
        """
        errors = []
        for connector in self._connectors.values():
            try:
                await connector.connect()
            except Exception as e:
                errors.append(str(e))

        if errors:
            raise ConnectorError(
                f"Failed to connect all connectors: {', '.join(errors)}",
            )

    async def disconnect_all(self) -> None:
        """Disconnect all registered connectors."""
        for connector in self._connectors.values():
            try:
                await connector.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting connector: {e}")


# Create a global connector registry
registry = ConnectorRegistry()