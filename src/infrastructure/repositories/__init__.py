"""
Repository Layer for TTKi Advanced AI System
===========================================

Implements the repository pattern for data access.
Provides a clean interface between domain logic and data storage.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..domain.entities import Agent, Task, MemoryEntry, LearningEvent, SystemAnalytics


class BaseRepository(ABC):
    """Base repository interface"""
    
    @abstractmethod
    async def create(self, entity: Any) -> Any:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def update(self, entity: Any) -> Any:
        """Update an entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[Any]:
        """List all entities"""
        pass


class AgentRepository(BaseRepository):
    """Repository for managing agents"""
    
    async def find_by_type(self, agent_type: str) -> List[Agent]:
        """Find agents by type"""
        # Implementation would be in concrete classes
        raise NotImplementedError
    
    async def find_active_agents(self) -> List[Agent]:
        """Find all active agents"""
        raise NotImplementedError


class TaskRepository(BaseRepository):
    """Repository for managing tasks"""
    
    async def find_by_agent(self, agent_id: str) -> List[Task]:
        """Find tasks for a specific agent"""
        raise NotImplementedError
    
    async def find_by_status(self, status: str) -> List[Task]:
        """Find tasks by status"""
        raise NotImplementedError
    
    async def find_pending_tasks(self) -> List[Task]:
        """Find all pending tasks"""
        raise NotImplementedError


class MemoryRepository(BaseRepository):
    """Repository for managing memory entries"""
    
    async def find_by_agent(self, agent_id: str) -> List[MemoryEntry]:
        """Find memory entries for a specific agent"""
        raise NotImplementedError
    
    async def search_by_similarity(self, query_vector: List[float], limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries by vector similarity"""
        raise NotImplementedError
    
    async def find_by_type(self, memory_type: str) -> List[MemoryEntry]:
        """Find memory entries by type"""
        raise NotImplementedError


class LearningEventRepository(BaseRepository):
    """Repository for managing learning events"""
    
    async def find_by_agent(self, agent_id: str) -> List[LearningEvent]:
        """Find learning events for a specific agent"""
        raise NotImplementedError
    
    async def find_by_type(self, event_type: str) -> List[LearningEvent]:
        """Find learning events by type"""
        raise NotImplementedError
    
    async def find_recent_events(self, limit: int = 50) -> List[LearningEvent]:
        """Find recent learning events"""
        raise NotImplementedError


class AnalyticsRepository(BaseRepository):
    """Repository for managing system analytics"""
    
    async def find_by_type(self, event_type: str) -> List[SystemAnalytics]:
        """Find analytics by event type"""
        raise NotImplementedError
    
    async def find_by_agent(self, agent_id: str) -> List[SystemAnalytics]:
        """Find analytics for a specific agent"""
        raise NotImplementedError
    
    async def get_performance_metrics(self, time_range: Dict[str, Any]) -> List[SystemAnalytics]:
        """Get performance metrics for a time range"""
        raise NotImplementedError
