"""
Unit tests for the logging module.
"""

import unittest
import logging
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from src.core.logging import (
    configure_logging, get_logger, set_correlation_id, set_request_id,
    set_user_id, set_component, clear_context, with_context, log_function_call,
    JSONFormatter, ContextAdapter, LogContext
)

class TestLoggingConfiguration(unittest.TestCase):
    """Test cases for logging configuration."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset logging configuration before each test
        logging.root.handlers = []
        logging.root.setLevel(logging.INFO)
        
    def test_configure_logging_default(self):
        """Test that configure_logging() works with default parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "app.log")
            configure_logging(log_file=log_file, log_level="INFO")
            
            # Check that the root logger has the correct level
            self.assertEqual(logging.root.level, logging.INFO)
            
            # Check that the log file was created
            self.assertTrue(os.path.exists(log_file))
            
            # Log a message and check that it was written to the file
            logger = logging.getLogger("test")
            logger.info("Test message")
            
            with open(log_file, "r") as f:
                log_content = f.read()
                self.assertIn("Test message", log_content)
    
    def test_configure_logging_json(self):
        """Test that configure_logging() works with JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "app.log")
            configure_logging(log_file=log_file, log_level="INFO", log_format="json")
            
            # Log a message and check that it was written to the file as JSON
            logger = logging.getLogger("test")
            logger.info("Test message")
            
            with open(log_file, "r") as f:
                log_content = f.read()
                # Check that the log content is valid JSON
                try:
                    log_data = json.loads(log_content)
                    self.assertIn("message", log_data)
                    self.assertEqual(log_data["message"], "Test message")
                except json.JSONDecodeError:
                    self.fail("Log content is not valid JSON")
    
    def test_configure_logging_console_only(self):
        """Test that configure_logging() works with console output only."""
        with patch("sys.stdout") as mock_stdout:
            configure_logging(log_file=None, log_level="INFO", console_output=True)
            
            # Check that the root logger has a console handler
            self.assertEqual(len(logging.root.handlers), 1)
            self.assertIsInstance(logging.root.handlers[0], logging.StreamHandler)
            
            # Log a message and check that it was written to stdout
            logger = logging.getLogger("test")
            logger.info("Test message")
            
            # Check that the message was written to stdout
            mock_stdout.write.assert_called()

class TestJSONFormatter(unittest.TestCase):
    """Test cases for the JSONFormatter class."""
    
    def test_json_formatter(self):
        """Test that JSONFormatter formats log records correctly."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Check that the formatted record is valid JSON
        try:
            log_data = json.loads(formatted)
            self.assertEqual(log_data["logger"], "test")
            self.assertEqual(log_data["level"], "INFO")
            self.assertEqual(log_data["message"], "Test message")
            self.assertEqual(log_data["line"], 42)
        except json.JSONDecodeError:
            self.fail("Formatted record is not valid JSON")
    
    def test_json_formatter_with_exception(self):
        """Test that JSONFormatter handles exceptions correctly."""
        formatter = JSONFormatter()
        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=True
            )
            
            formatted = formatter.format(record)
            
            # Check that the formatted record is valid JSON
            try:
                log_data = json.loads(formatted)
                self.assertEqual(log_data["logger"], "test")
                self.assertEqual(log_data["level"], "ERROR")
                self.assertEqual(log_data["message"], "Test message")
                self.assertIn("exception", log_data)
                self.assertEqual(log_data["exception"]["type"], "ValueError")
                self.assertEqual(log_data["exception"]["message"], "Test exception")
            except json.JSONDecodeError:
                self.fail("Formatted record is not valid JSON")

class TestContextAdapter(unittest.TestCase):
    """Test cases for the ContextAdapter class."""
    
    def test_context_adapter(self):
        """Test that ContextAdapter adds context to log records."""
        logger = logging.getLogger("test")
        context = {"user_id": "123", "request_id": "456"}
        adapter = ContextAdapter(logger, context)
        
        with patch.object(logger, "info") as mock_info:
            adapter.info("Test message")
            
            # Check that the context was added to the log record
            args, kwargs = mock_info.call_args
            self.assertEqual(args[0], "Test message")
            self.assertIn("extra", kwargs)
            self.assertEqual(kwargs["extra"]["user_id"], "123")
            self.assertEqual(kwargs["extra"]["request_id"], "456")

class TestLogContext(unittest.TestCase):
    """Test cases for the LogContext class."""
    
    def test_log_context(self):
        """Test that LogContext adds context to log records."""
        logger = logging.getLogger("test")
        context = {"user_id": "123", "request_id": "456"}
        
        with patch.object(logger, "info") as mock_info:
            with LogContext(logger, context) as ctx_logger:
                ctx_logger.info("Test message")
                
                # Check that the context was added to the log record
                args, kwargs = mock_info.call_args
                self.assertEqual(args[0], "Test message")
                self.assertIn("extra", kwargs)
                self.assertEqual(kwargs["extra"]["user_id"], "123")
                self.assertEqual(kwargs["extra"]["request_id"], "456")

class TestThreadContext(unittest.TestCase):
    """Test cases for thread context functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear thread context before each test
        clear_context()
        
    def test_set_correlation_id(self):
        """Test that set_correlation_id() sets the correlation ID."""
        set_correlation_id("123")
        self.assertEqual(logging.getThreadContext().correlation_id, "123")
        
    def test_set_request_id(self):
        """Test that set_request_id() sets the request ID."""
        set_request_id("456")
        self.assertEqual(logging.getThreadContext().request_id, "456")
        
    def test_set_user_id(self):
        """Test that set_user_id() sets the user ID."""
        set_user_id("789")
        self.assertEqual(logging.getThreadContext().user_id, "789")
        
    def test_set_component(self):
        """Test that set_component() sets the component."""
        set_component("test")
        self.assertEqual(logging.getThreadContext().component, "test")
        
    def test_clear_context(self):
        """Test that clear_context() clears the thread context."""
        set_correlation_id("123")
        set_request_id("456")
        set_user_id("789")
        set_component("test")
        
        clear_context()
        
        self.assertIsNone(logging.getThreadContext().correlation_id)
        self.assertIsNone(logging.getThreadContext().request_id)
        self.assertIsNone(logging.getThreadContext().user_id)
        self.assertIsNone(logging.getThreadContext().component)
        
    def test_with_context_decorator(self):
        """Test that with_context decorator sets and restores context."""
        set_correlation_id("original")
        
        @with_context(correlation_id="123")
        def test_function():
            self.assertEqual(logging.getThreadContext().correlation_id, "123")
            
        test_function()
        
        # Check that the original context was restored
        self.assertEqual(logging.getThreadContext().correlation_id, "original")

class TestLogFunctionCall(unittest.TestCase):
    """Test cases for the log_function_call decorator."""
    
    def test_log_function_call(self):
        """Test that log_function_call decorator logs function calls."""
        logger = logging.getLogger("test")
        
        @log_function_call(logger=logger)
        def test_function(arg1, arg2=None):
            return arg1 + (arg2 or 0)
            
        with patch.object(logger, "debug") as mock_debug:
            result = test_function(1, arg2=2)
            
            # Check that the function call was logged
            self.assertEqual(mock_debug.call_count, 2)
            
            # Check the first log message (function call)
            args1, _ = mock_debug.call_args_list[0]
            self.assertIn("Calling test_function", args1[0])
            self.assertIn("arg1=1", args1[0])
            self.assertIn("arg2=2", args1[0])
            
            # Check the second log message (function return)
            args2, _ = mock_debug.call_args_list[1]
            self.assertIn("test_function returned: 3", args2[0])
            
            # Check that the function returned the correct result
            self.assertEqual(result, 3)
    
    def test_log_function_call_exception(self):
        """Test that log_function_call decorator logs exceptions."""
        logger = logging.getLogger("test")
        
        @log_function_call(logger=logger)
        def test_function():
            raise ValueError("Test exception")
            
        with patch.object(logger, "debug") as mock_debug:
            with patch.object(logger, "exception") as mock_exception:
                with self.assertRaises(ValueError):
                    test_function()
                
                # Check that the function call was logged
                self.assertEqual(mock_debug.call_count, 1)
                
                # Check the log message (function call)
                args, _ = mock_debug.call_args
                self.assertIn("Calling test_function", args[0])
                
                # Check that the exception was logged
                self.assertEqual(mock_exception.call_count, 1)
                args, _ = mock_exception.call_args
                self.assertIn("test_function raised an exception", args[0])
                self.assertIn("Test exception", args[0])

if __name__ == '__main__':
    unittest.main()