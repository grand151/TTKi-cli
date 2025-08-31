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
    Desktop Agent with Legacy Bridge Integration
    
    This agent provides desktop operations via:
    1. DDD architecture for coordination and planning
    2. Legacy TTKi bridge for actual container operations
    """
    
    def __init__(self, agent_id: str = "desktop_agent"):
        self.agent_id = AgentId(agent_id)
        
        # Create agent entity correctly - AgentEntity expects specific parameters
        self.agent_entity = AgentEntity(
            id=self.agent_id,
            agent_type="desktop",
            capabilities=["folder_operations", "screenshots", "navigation", "window_management"]
        )
        
        # Initialize legacy bridge
        self.legacy_bridge = LegacyTTKiBridge()
        
        logger.info(f"✅ Desktop Agent initialized with bridge status: {self.legacy_bridge.available}")
    
    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> TaskResult:
        """
        Execute desktop task via intelligent delegation
        """
        start_time = datetime.now()
        context = context or {}
        
        logger.info(f"🖥️  Desktop Agent executing: {task_description}")
        
        try:
            # Priority 1: Use Legacy Bridge for container operations
            if self.legacy_bridge.available and self._needs_container_access(task_description):
                logger.info("🌉 Delegating to Legacy TTKi Bridge")
                return await self.legacy_bridge.execute_desktop_operation(
                    task_description, 
                    context
                )
            
            # Priority 2: Local fallback operations
            else:
                logger.info("🔧 Using local fallback operations")
                return await self._execute_local_fallback(task_description, context)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Desktop Agent execution failed: {str(e)}")
            
            return TaskResult(
                success=False,
                error_message=f"Desktop operation failed: {str(e)}",
                duration=duration
            )
    
    def _needs_container_access(self, task_description: str) -> bool:
        """Determine if task needs Docker container access"""
        container_keywords = [
            "create folder", "folder", "desktop", "screenshot", 
            "window", "vnc", "display", "gui"
        ]
        
        return any(keyword in task_description.lower() for keyword in container_keywords)
    
    async def _execute_local_fallback(
        self, 
        task_description: str, 
        context: Dict[str, Any]
    ) -> TaskResult:
        """Local fallback operations (non-container)"""
        
        start_time = datetime.now()
        
        try:
            if "create folder" in task_description.lower():
                return await self._create_folder_local(context)
            
            elif "list files" in task_description.lower():
                return await self._list_files_local(context)
            
            else:
                # Generic success for coordination/planning tasks
                return TaskResult(
                    success=True,
                    data={
                        "operation": "desktop_coordination",
                        "description": task_description,
                        "mode": "local_fallback",
                        "note": "Operation coordinated locally"
                    },
                    duration=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as e:
            return TaskResult(
                success=False,
                error_message=f"Local fallback failed: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds()
            )
    
    async def _create_folder_local(self, context: Dict[str, Any]) -> TaskResult:
        """Create folder locally (fallback)"""
        
        start_time = datetime.now()
        folder_name = context.get("folder_name", "NewFolder")
        
        try:
            import os
            local_path = f"/tmp/ttki_fallback/{folder_name}"
            os.makedirs(local_path, exist_ok=True)
            
            return TaskResult(
                success=True,
                data={
                    "folder_created": folder_name,
                    "path": local_path,
                    "mode": "local_fallback"
                },
                duration=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                error_message=f"Local folder creation failed: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds()
            )
    
    async def _list_files_local(self, context: Dict[str, Any]) -> TaskResult:
        """List files locally (fallback)"""
        
        start_time = datetime.now()
        
        try:
            import os
            path = context.get("path", "/tmp/ttki_fallback")
            
            if os.path.exists(path):
                files = os.listdir(path)
            else:
                files = []
            
            return TaskResult(
                success=True,
                data={
                    "files": files,
                    "path": path,
                    "mode": "local_fallback"
                },
                duration=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                error_message=f"Local file listing failed: {str(e)}",
                duration=(datetime.now() - start_time).total_seconds()
            )
    
    def get_capabilities(self) -> list:
        """Get agent capabilities"""
        return self.agent_entity.capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": str(self.agent_id),
            "agent_type": "desktop",
            "capabilities": self.get_capabilities(),
            "legacy_bridge": self.legacy_bridge.get_status(),
            "status": "active"
        }
