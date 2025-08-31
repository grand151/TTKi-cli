"""
Repository Interfaces - Domain layer contracts
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import AgentEntity, TaskEntity, ExecutionPlanEntity
from .value_objects import AgentId, TaskId, ExecutionPlanId

class AgentRepository(ABC):
    """Repository interface for Agent entities"""
    
    @abstractmethod
    async def save(self, agent: AgentEntity) -> None:
        """Save agent entity"""
        pass
    
    @abstractmethod
    async def find_by_id(self, agent_id: AgentId) -> Optional[AgentEntity]:
        """Find agent by ID"""
        pass
    
    @abstractmethod
    async def find_by_type(self, agent_type: str) -> List[AgentEntity]:
        """Find agents by type"""
        pass
    
    @abstractmethod
    async def find_available(self) -> List[AgentEntity]:
        """Find available agents"""
        pass
    
    @abstractmethod
    async def delete(self, agent_id: AgentId) -> None:
        """Delete agent"""
        pass

class TaskRepository(ABC):
    """Repository interface for Task entities"""
    
    @abstractmethod
    async def save(self, task: TaskEntity) -> None:
        """Save task entity"""
        pass
    
    @abstractmethod
    async def find_by_id(self, task_id: TaskId) -> Optional[TaskEntity]:
        """Find task by ID"""
        pass
    
    @abstractmethod
    async def find_pending(self) -> List[TaskEntity]:
        """Find pending tasks"""
        pass
    
    @abstractmethod
    async def find_by_agent(self, agent_id: AgentId) -> List[TaskEntity]:
        """Find tasks assigned to agent"""
        pass
    
    @abstractmethod
    async def delete(self, task_id: TaskId) -> None:
        """Delete task"""
        pass

class ExecutionPlanRepository(ABC):
    """Repository interface for ExecutionPlan entities"""
    
    @abstractmethod
    async def save(self, plan: ExecutionPlanEntity) -> None:
        """Save execution plan"""
        pass
    
    @abstractmethod
    async def find_by_id(self, plan_id: ExecutionPlanId) -> Optional[ExecutionPlanEntity]:
        """Find plan by ID"""
        pass
    
    @abstractmethod
    async def find_active(self) -> List[ExecutionPlanEntity]:
        """Find active execution plans"""
        pass
    
    @abstractmethod
    async def delete(self, plan_id: ExecutionPlanId) -> None:
        """Delete execution plan"""
        pass
