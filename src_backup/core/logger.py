"""
Logging module for the Dev-Server-Workflow project.

This module provides a standardized logging setup for all components of the
Dev-Server-Workflow project.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from .constants import LOGS_DIR, DEFAULT_LOG_LEVEL, DEFAULT_LOG_FORMAT

# Global logger registry to avoid duplicate loggers
_loggers: Dict[str, logging.Logger] = {}

def setup_logging(
    level: str = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    logger_name: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the script.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (optional)
        log_format: Format for log messages
        logger_name: Name of the logger (defaults to script name)
        
    Returns:
        Logger instance
    """
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Create logger for the script
    if logger_name is None:
        logger_name = os.path.basename(sys.argv[0])
    
    # Check if logger already exists in registry
    if logger_name in _loggers:
        return _loggers[logger_name]
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(numeric_level)
    
    # Add file handler if specified
    if log_file:
        # Create directory if it doesn't exist
        log_path = Path(log_file)
        os.makedirs(log_path.parent, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    # Store logger in registry
    _loggers[logger_name] = logger
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    if name in _loggers:
        return _loggers[name]
    
    # Create a new logger
    return setup_logging(logger_name=name)