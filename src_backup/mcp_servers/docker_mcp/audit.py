"""
Audit logging module for Docker MCP server.

This module provides audit logging functionality for the Docker MCP server.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("docker-mcp-audit")


class AuditLogger:
    """Audit logger for Docker MCP server."""
    
    def __init__(self, log_dir: str = None):
        """Initialize the audit logger.
        
        Args:
            log_dir: Directory to store audit logs
        """
        self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), '../../../logs')
        self.audit_log_path = os.path.join(self.log_dir, 'docker_mcp_audit.log')
        self.json_log_path = os.path.join(self.log_dir, 'docker_mcp_audit.json')
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize JSON log file if it doesn't exist
        if not os.path.exists(self.json_log_path):
            with open(self.json_log_path, 'w') as f:
                json.dump([], f)
                
    def log_event(self, event_type: str, username: str, tool_name: str, 
                 arguments: Dict[str, Any], result: Union[str, Dict[str, Any]], 
                 status: str = "success", error: Optional[str] = None) -> None:
        """Log an audit event.
        
        Args:
            event_type: Type of event (e.g., "tool_execution")
            username: Username
            tool_name: Tool name
            arguments: Tool arguments
            result: Tool result
            status: Event status (e.g., "success", "error")
            error: Error message if status is "error"
        """
        timestamp = datetime.now().isoformat()
        
        # Create event record
        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "username": username,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "status": status
        }
        
        if error:
            event["error"] = error
            
        # Log to text file
        with open(self.audit_log_path, 'a') as f:
            f.write(f"{timestamp} | {event_type} | {username} | {tool_name} | {status}")
            if error:
                f.write(f" | {error}")
            f.write("\n")
            
        # Log to JSON file
        try:
            with open(self.json_log_path, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
            
        logs.append(event)
        
        # Keep only the last 1000 events to prevent the file from growing too large
        if len(logs) > 1000:
            logs = logs[-1000:]
            
        with open(self.json_log_path, 'w') as f:
            json.dump(logs, f, indent=2)
            
        # Also log to standard logger
        log_message = f"{event_type} | {username} | {tool_name} | {status}"
        if error:
            log_message += f" | {error}"
            logger.error(log_message)
        else:
            logger.info(log_message)
            
    def get_logs(self, username: Optional[str] = None, tool_name: Optional[str] = None, 
                event_type: Optional[str] = None, status: Optional[str] = None, 
                start_time: Optional[str] = None, end_time: Optional[str] = None, 
                limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering.
        
        Args:
            username: Filter by username
            tool_name: Filter by tool name
            event_type: Filter by event type
            status: Filter by status
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log entries
        """
        try:
            with open(self.json_log_path, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
            
        # Apply filters
        filtered_logs = logs
        
        if username:
            filtered_logs = [log for log in filtered_logs if log.get("username") == username]
            
        if tool_name:
            filtered_logs = [log for log in filtered_logs if log.get("tool_name") == tool_name]
            
        if event_type:
            filtered_logs = [log for log in filtered_logs if log.get("event_type") == event_type]
            
        if status:
            filtered_logs = [log for log in filtered_logs if log.get("status") == status]
            
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.get("timestamp", "") >= start_time]
            
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.get("timestamp", "") <= end_time]
            
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit
        return filtered_logs[:limit]
        
    def clear_logs(self) -> None:
        """Clear all audit logs."""
        with open(self.audit_log_path, 'w') as f:
            f.write("")
            
        with open(self.json_log_path, 'w') as f:
            json.dump([], f)
            
        logger.info("Audit logs cleared")