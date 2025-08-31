"""
Terminal Agent - Basic implementation
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from ...domain.entities import AgentEntity
from ...domain.value_objects import TaskType, TaskResult, AgentId

logger = logging.getLogger(__name__)

class TerminalAgent:
    def __init__(self, agent_id: str = "terminal_agent"):
        self.agent_id = AgentId(agent_id)
        self.agent_entity = AgentEntity(
            agent_id=self.agent_id,
            agent_type="terminal",
            capabilities=["terminal_operations", "command_execution", "system_control"]
        )
    
    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> TaskResult:
        start_time = datetime.now()
        await asyncio.sleep(0.4)
        return TaskResult(
            success=True,
            data={"operation": "terminal", "description": task_description},
            duration=(datetime.now() - start_time).total_seconds()
        )
