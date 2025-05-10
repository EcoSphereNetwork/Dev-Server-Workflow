"""
Process management utilities for the Dev-Server-Workflow project.

This module provides utilities for managing processes, including starting, stopping,
and checking the status of processes.
"""

import os
import sys
import signal
import subprocess
import time
import psutil
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Union

from ..core.logger import get_logger

logger = get_logger("process_utils")

class ProcessManager:
    """
    Utilities for process management.
    """
    
    @staticmethod
    def is_process_running(pid: int) -> bool:
        """
        Check if a process is running.
        
        Args:
            pid: Process ID
            
        Returns:
            bool: True if the process is running, False otherwise
        """
        try:
            # Check if the process exists
            os.kill(pid, 0)
            return True
        except OSError:
            return False
        except Exception as e:
            logger.error(f"Error checking if process is running: {e}")
            return False
    
    @staticmethod
    def is_process_running_by_name(process_name: str) -> bool:
        """
        Check if a process with the given name is running.
        
        Args:
            process_name: Process name
            
        Returns:
            bool: True if a process with the name is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking if process is running by name: {e}")
            return False
    
    @staticmethod
    def get_process_id_by_name(process_name: str) -> List[int]:
        """
        Get the process IDs of processes with the given name.
        
        Args:
            process_name: Process name
            
        Returns:
            List[int]: List of process IDs
        """
        try:
            pids = []
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    pids.append(proc.info['pid'])
            return pids
        except Exception as e:
            logger.error(f"Error getting process ID by name: {e}")
            return []
    
    @staticmethod
    def kill_process(pid: int, force: bool = False) -> bool:
        """
        Kill a process.
        
        Args:
            pid: Process ID
            force: Force kill (SIGKILL instead of SIGTERM)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not ProcessManager.is_process_running(pid):
                logger.warning(f"Process {pid} is not running")
                return True
            
            # Send SIGTERM or SIGKILL
            os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
            
            # Wait for the process to terminate
            for _ in range(10):
                if not ProcessManager.is_process_running(pid):
                    return True
                time.sleep(0.1)
            
            # If the process is still running and force is True, send SIGKILL
            if force:
                logger.warning(f"Process {pid} did not terminate, sending SIGKILL")
                os.kill(pid, signal.SIGKILL)
                
                # Wait for the process to terminate
                for _ in range(10):
                    if not ProcessManager.is_process_running(pid):
                        return True
                    time.sleep(0.1)
            
            # If we get here, the process is still running
            logger.error(f"Failed to kill process {pid}")
            return False
        except Exception as e:
            logger.error(f"Error killing process: {e}")
            return False
    
    @staticmethod
    def kill_process_by_name(process_name: str, force: bool = False) -> bool:
        """
        Kill processes with the given name.
        
        Args:
            process_name: Process name
            force: Force kill (SIGKILL instead of SIGTERM)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pids = ProcessManager.get_process_id_by_name(process_name)
            
            if not pids:
                logger.warning(f"No processes found with name {process_name}")
                return True
            
            success = True
            for pid in pids:
                if not ProcessManager.kill_process(pid, force):
                    success = False
            
            return success
        except Exception as e:
            logger.error(f"Error killing process by name: {e}")
            return False
    
    @staticmethod
    def start_process(
        command: List[str],
        log_file: Optional[Union[str, Path]] = None,
        pid_file: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[Union[str, Path]] = None
    ) -> Tuple[bool, Optional[int]]:
        """
        Start a process.
        
        Args:
            command: Command to run
            log_file: Path to the log file
            pid_file: Path to the PID file
            env: Environment variables
            cwd: Working directory
            
        Returns:
            Tuple[bool, Optional[int]]: (Success, Process ID)
        """
        try:
            # Open log file if specified
            if log_file:
                log_file = Path(log_file)
                os.makedirs(log_file.parent, exist_ok=True)
                log_fd = open(log_file, 'w')
            else:
                log_fd = subprocess.DEVNULL
            
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Start the process
            process = subprocess.Popen(
                command,
                stdout=log_fd,
                stderr=subprocess.STDOUT,
                env=process_env,
                cwd=cwd,
                start_new_session=True
            )
            
            # Save the PID if specified
            if pid_file:
                pid_file = Path(pid_file)
                os.makedirs(pid_file.parent, exist_ok=True)
                with open(pid_file, 'w') as f:
                    f.write(str(process.pid))
            
            # Wait briefly and check if the process is running
            time.sleep(0.5)
            if ProcessManager.is_process_running(process.pid):
                logger.info(f"Process started successfully with PID {process.pid}")
                return True, process.pid
            
            logger.error(f"Process failed to start")
            return False, None
        except Exception as e:
            logger.error(f"Error starting process: {e}")
            return False, None
    
    @staticmethod
    def get_process_info(pid: int) -> Optional[Dict[str, Any]]:
        """
        Get information about a process.
        
        Args:
            pid: Process ID
            
        Returns:
            Optional[Dict[str, Any]]: Process information or None if not found
        """
        try:
            process = psutil.Process(pid)
            return {
                'pid': process.pid,
                'name': process.name(),
                'status': process.status(),
                'create_time': process.create_time(),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_percent': process.memory_percent(),
                'cmdline': process.cmdline(),
                'exe': process.exe(),
                'cwd': process.cwd()
            }
        except psutil.NoSuchProcess:
            logger.warning(f"Process {pid} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return None
    
    @staticmethod
    def wait_for_process_to_finish(pid: int, timeout: int = 30) -> bool:
        """
        Wait for a process to finish.
        
        Args:
            pid: Process ID
            timeout: Timeout in seconds
            
        Returns:
            bool: True if the process finished, False if it timed out
        """
        try:
            start_time = time.time()
            while ProcessManager.is_process_running(pid):
                if time.time() - start_time > timeout:
                    logger.warning(f"Timeout waiting for process {pid} to finish")
                    return False
                time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Error waiting for process to finish: {e}")
            return False