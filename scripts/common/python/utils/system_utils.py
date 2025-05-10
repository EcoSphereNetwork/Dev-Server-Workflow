"""
System utilities for the Dev-Server-Workflow project.

This module provides utilities for system operations, including getting system information,
checking commands, and installing packages.
"""

import os
import sys
import platform
import subprocess
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from src.core.logger import get_logger

logger = get_logger("system_utils")

class SystemUtils:
    """
    Utilities for system operations.
    """
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dict[str, Any]: System information
        """
        info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "hostname": platform.node(),
            "username": os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown'),
            "home_directory": os.path.expanduser("~"),
            "current_directory": os.getcwd(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add CPU information if available
        try:
            import psutil
            info["cpu_count"] = psutil.cpu_count()
            info["cpu_percent"] = psutil.cpu_percent(interval=1)
            info["memory_total"] = psutil.virtual_memory().total
            info["memory_available"] = psutil.virtual_memory().available
            info["memory_percent"] = psutil.virtual_memory().percent
            info["disk_total"] = psutil.disk_usage('/').total
            info["disk_free"] = psutil.disk_usage('/').free
            info["disk_percent"] = psutil.disk_usage('/').percent
        except ImportError:
            pass
        
        return info
    
    @staticmethod
    def check_command(command: str) -> bool:
        """
        Check if a command is available.
        
        Args:
            command: Command to check
            
        Returns:
            bool: True if the command is available, False otherwise
        """
        return shutil.which(command) is not None
    
    @staticmethod
    def check_python_package(package: str) -> bool:
        """
        Check if a Python package is installed.
        
        Args:
            package: Package name
            
        Returns:
            bool: True if the package is installed, False otherwise
        """
        try:
            __import__(package)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def install_python_package(package: str) -> bool:
        """
        Install a Python package.
        
        Args:
            package: Package name
            
        Returns:
            bool: True if the package was installed successfully, False otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error installing Python package: {e}")
            return False
    
    @staticmethod
    def create_backup(file_path: Union[str, os.PathLike], suffix: Optional[str] = None) -> Optional[str]:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file
            suffix: Suffix to add to the backup file name (default: timestamp)
            
        Returns:
            Optional[str]: Path to the backup file or None if an error occurred
        """
        try:
            file_path = os.path.abspath(file_path)
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return None
            
            if suffix is None:
                suffix = datetime.now().strftime("%Y%m%d%H%M%S")
            
            backup_path = f"{file_path}.bak.{suffix}"
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    @staticmethod
    def restore_backup(backup_path: Union[str, os.PathLike]) -> bool:
        """
        Restore a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            bool: True if the backup was restored successfully, False otherwise
        """
        try:
            backup_path = os.path.abspath(backup_path)
            
            if not os.path.exists(backup_path):
                logger.warning(f"Backup file not found: {backup_path}")
                return False
            
            # Extract the original file path
            if ".bak." in backup_path:
                original_path = backup_path.split(".bak.")[0]
            else:
                logger.warning(f"Not a valid backup file: {backup_path}")
                return False
            
            # Create a backup of the current file if it exists
            if os.path.exists(original_path):
                SystemUtils.create_backup(original_path, "before_restore")
            
            # Restore the backup
            shutil.copy2(backup_path, original_path)
            
            logger.info(f"Restored backup: {backup_path} to {original_path}")
            return True
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    @staticmethod
    def get_directory_size(directory: Union[str, os.PathLike]) -> int:
        """
        Get the size of a directory in bytes.
        
        Args:
            directory: Path to the directory
            
        Returns:
            int: Size of the directory in bytes
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)
            return total_size
        except Exception as e:
            logger.error(f"Error getting directory size: {e}")
            return 0
    
    @staticmethod
    def get_file_info(file_path: Union[str, os.PathLike]) -> Optional[Dict[str, Any]]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Optional[Dict[str, Any]]: File information or None if an error occurred
        """
        try:
            file_path = os.path.abspath(file_path)
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return None
            
            stat = os.stat(file_path)
            
            return {
                "path": file_path,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_directory": os.path.isdir(file_path),
                "is_file": os.path.isfile(file_path),
                "is_symlink": os.path.islink(file_path),
                "permissions": oct(stat.st_mode)[-3:]
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None