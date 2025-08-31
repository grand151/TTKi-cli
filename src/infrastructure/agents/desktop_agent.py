"""
Desktop Agent - Hybrid implementation with Legacy Bridge
Handles desktop operations via DDD architecture + Legacy TTKi Bridge
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from ...domain.entities import AgentEntity
from ...domain.value_objects import TaskType, TaskResult, AgentId
from .legacy_bridge import LegacyTTKiBridge

logger = logging.getLogger(__name__)

class DesktopAgent:
    """
    Real Desktop Agent Implementation
    Integrates with TTKi desktop functions and Docker containers
    """
    
    def __init__(self, agent_id: str = "desktop_agent_001"):
        self.agent_id = AgentId.from_string(agent_id)
        self.capabilities = [
            "desktop_operations", "file_operations", "folder_creation",
            "desktop_navigation", "window_management"
        ]
        
        # Import TTKi functions
        try:
            import sys
            import os
            # Add app.py path for imports
            app_path = "/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt"
            if app_path not in sys.path:
                sys.path.append(app_path)
                
            from app import (
                desktop_create_folder, desktop_list_files, desktop_navigate,
                get_screenshot, take_screenshot
            )
            
            self.desktop_create_folder = desktop_create_folder
            self.desktop_list_files = desktop_list_files
            self.desktop_navigate = desktop_navigate
            self.get_screenshot = get_screenshot
            self.take_screenshot = take_screenshot
            
            self.functions_available = True
            logger.info("Desktop Agent: TTKi functions loaded successfully")
            
        except ImportError as e:
            logger.error(f"Desktop Agent: Failed to import TTKi functions: {str(e)}")
            self.functions_available = False
    
    def can_handle_task(self, task_type: TaskType) -> bool:
        """Check if agent can handle task type"""
        return task_type in [
            TaskType.FILE_OPERATIONS,
            TaskType.VISION_ANALYSIS  # For desktop screenshots
        ]
    
    async def execute_task(self, task_description: str, parameters: Dict[str, Any] = None) -> TaskResult:
        """Execute desktop task using real TTKi functions"""
        start_time = datetime.now()
        
        if not self.functions_available:
            return TaskResult(
                success=False,
                error_message="TTKi desktop functions not available",
                duration=0.0
            )
        
        try:
            # Parse task description to determine action
            task_lower = task_description.lower()
            
            if "create folder" in task_lower or "mkdir" in task_lower:
                return await self._create_folder(task_description, parameters)
            
            elif "screenshot" in task_lower or "capture" in task_lower:
                return await self._take_screenshot(parameters)
            
            elif "list files" in task_lower or "ls" in task_lower:
                return await self._list_files(parameters)
            
            elif "navigate" in task_lower or "cd" in task_lower:
                return await self._navigate(task_description, parameters)
            
            else:
                return TaskResult(
                    success=False,
                    error_message=f"Unknown desktop task: {task_description}",
                    duration=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Desktop Agent error: {str(e)}")
            
            return TaskResult(
                success=False,
                error_message=str(e),
                duration=duration
            )
    
    async def _create_folder(self, task_description: str, parameters: Dict[str, Any] = None) -> TaskResult:
        """Create folder on desktop"""
        start_time = datetime.now()
        
        try:
            # Extract folder name from description or parameters
            folder_name = None
            
            if parameters and "folder_name" in parameters:
                folder_name = parameters["folder_name"]
            elif parameters and "name" in parameters:
                folder_name = parameters["name"]
            else:
                # Try to extract from description
                import re
                # Look for quoted strings or words after "folder"
                match = re.search(r'(?:folder|directory)\s+["\']?([^"\']+)["\']?', task_description, re.IGNORECASE)
                if match:
                    folder_name = match.group(1).strip()
                else:
                    folder_name = "NewFolder"
            
            logger.info(f"Creating folder: {folder_name}")
            
            # Call TTKi function
            result = self.desktop_create_folder(folder_name)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                success=True,
                data={
                    "folder_name": folder_name,
                    "result": result,
                    "action": "folder_created"
                },
                duration=duration,
                metrics={"folder_name": folder_name}
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                success=False,
                error_message=f"Failed to create folder: {str(e)}",
                duration=duration
            )
    
    async def _take_screenshot(self, parameters: Dict[str, Any] = None) -> TaskResult:
        """Take desktop screenshot"""
        start_time = datetime.now()
        
        try:
            logger.info("Taking desktop screenshot")
            
            # Call TTKi screenshot function
            result = self.take_screenshot()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                success=True,
                data={
                    "screenshot_result": result,
                    "action": "screenshot_taken"
                },
                duration=duration,
                metrics={"screenshot_size": len(str(result)) if result else 0}
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                success=False,
                error_message=f"Failed to take screenshot: {str(e)}",
                duration=duration
            )
    
    async def _list_files(self, parameters: Dict[str, Any] = None) -> TaskResult:
        """List desktop files"""
        start_time = datetime.now()
        
        try:
            logger.info("Listing desktop files")
            
            # Call TTKi function
            result = self.desktop_list_files()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                success=True,
                data={
                    "files": result,
                    "action": "files_listed"
                },
                duration=duration,
                metrics={"file_count": len(result) if isinstance(result, list) else 0}
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                success=False,
                error_message=f"Failed to list files: {str(e)}",
                duration=duration
            )
    
    async def _navigate(self, task_description: str, parameters: Dict[str, Any] = None) -> TaskResult:
        """Navigate desktop"""
        start_time = datetime.now()
        
        try:
            # Extract path from description or parameters
            path = parameters.get("path", "/headless/Desktop") if parameters else "/headless/Desktop"
            
            logger.info(f"Navigating to: {path}")
            
            # Call TTKi function
            result = self.desktop_navigate(path)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                success=True,
                data={
                    "path": path,
                    "result": result,
                    "action": "navigation_completed"
                },
                duration=duration,
                metrics={"path": path}
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                success=False,
                error_message=f"Failed to navigate: {str(e)}",
                duration=duration
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": str(self.agent_id),
            "agent_type": "DesktopAgent",
            "functions_available": self.functions_available,
            "capabilities": self.capabilities,
            "status": "ready"
        }
