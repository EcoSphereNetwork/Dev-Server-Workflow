"""
Structured logging module for the Dev-Server-Workflow application.
This module provides utilities for consistent logging across the application.
"""

import json
import logging
import logging.config
import logging.handlers
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional, Union, List

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# JSON log format
JSON_LOG_FORMAT = {
    "timestamp": "%(asctime)s",
    "level": "%(levelname)s",
    "logger": "%(name)s",
    "message": "%(message)s",
    "module": "%(module)s",
    "function": "%(funcName)s",
    "line": "%(lineno)d",
    "process": "%(process)d",
    "thread": "%(thread)d"
}

class JSONFormatter(logging.Formatter):
    """Formatter for JSON-structured logs."""
    
    def __init__(self, fmt_dict: Optional[Dict[str, str]] = None):
        """
        Initialize a new JSONFormatter.
        
        Args:
            fmt_dict: Dictionary of format strings for log record attributes
        """
        self.fmt_dict = fmt_dict or JSON_LOG_FORMAT
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record: Log record to format
        
        Returns:
            JSON-formatted log record
        """
        log_dict = {}
        
        # Add standard fields from format dictionary
        for key, fmt in self.fmt_dict.items():
            log_dict[key] = self._format_field(record, fmt)
        
        # Add exception info if present
        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename",
                          "funcName", "id", "levelname", "levelno", "lineno", "module",
                          "msecs", "message", "msg", "name", "pathname", "process",
                          "processName", "relativeCreated", "stack_info", "thread", "threadName"]:
                log_dict[key] = value
        
        # Convert to JSON
        return json.dumps(log_dict)
    
    def _format_field(self, record: logging.LogRecord, fmt: str) -> str:
        """
        Format a single field of a log record.
        
        Args:
            record: Log record to format
            fmt: Format string for the field
        
        Returns:
            Formatted field value
        """
        # Create a temporary formatter for this field
        formatter = logging.Formatter(fmt)
        return formatter.format(record)

class ContextAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context to log records."""
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process the log message by adding context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments for the logger
        
        Returns:
            Tuple of (message, kwargs)
        """
        # Add extra context to the log record
        kwargs.setdefault("extra", {}).update(self.extra)
        return msg, kwargs

def configure_logging(
    log_level: str = "INFO",
    log_format: str = "text",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    max_bytes: int = 10485760,  # 10 MB
    backup_count: int = 5,
    enable_console: bool = True
) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (text or json)
        log_file: Log file name
        log_dir: Directory for log files
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        enable_console: Whether to enable console logging
    """
    # Convert log level string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create log directory if it doesn't exist
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure handlers
    handlers = []
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        if log_format.lower() == "json":
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        handlers.append(console_handler)
    
    # File handler
    if log_file:
        if log_dir:
            log_file = os.path.join(log_dir, log_file)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        if log_format.lower() == "json":
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers
    )

def get_logger(
    name: str,
    context: Optional[Dict[str, Any]] = None
) -> Union[logging.Logger, ContextAdapter]:
    """
    Get a logger with optional context.
    
    Args:
        name: Logger name
        context: Context to add to log records
    
    Returns:
        Logger or ContextAdapter
    """
    logger = logging.getLogger(name)
    
    if context:
        return ContextAdapter(logger, context)
    
    return logger

class LogContext:
    """Context manager for adding context to logs."""
    
    def __init__(
        self,
        logger: Union[logging.Logger, ContextAdapter],
        context: Dict[str, Any]
    ):
        """
        Initialize a new LogContext.
        
        Args:
            logger: Logger to add context to
            context: Context to add to log records
        """
        self.logger = logger
        self.context = context
        self.original_logger = None
    
    def __enter__(self) -> Union[logging.Logger, ContextAdapter]:
        """
        Enter the context.
        
        Returns:
            Logger with context
        """
        if isinstance(self.logger, ContextAdapter):
            # If already an adapter, update the context
            self.original_logger = self.logger
            new_context = {**self.logger.extra, **self.context}
            self.logger = ContextAdapter(self.logger.logger, new_context)
        else:
            # Create a new adapter
            self.original_logger = self.logger
            self.logger = ContextAdapter(self.logger, self.context)
        
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context."""
        self.logger = self.original_logger

def log_execution_time(logger: Union[logging.Logger, ContextAdapter], level: int = logging.INFO):
    """
    Decorator to log the execution time of a function.
    
    Args:
        logger: Logger to use
        level: Logging level
    
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.log(
                level,
                f"Function '{func.__name__}' executed in {execution_time:.4f} seconds",
                extra={"execution_time": execution_time}
            )
            
            return result
        
        return wrapper
    
    return decorator