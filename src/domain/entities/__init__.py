"""
Domain Entities for TTKi Advanced AI System
==========================================

Core domain objects that represent the business logic and data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class AgentType(Enum):
    """Types of AI agents in the system"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    COORDINATOR = "coordinator"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class Agent:
    """
    Represents an AI agent in the TTKi system.
    Each agent has specific capabilities and can execute tasks.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    agent_type: AgentType = AgentType.RESEARCH
    status: str = "active"
    capabilities: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


# Aliases for backward compatibility
AgentEntity = Agent
    
    def update_status(self, new_status: str):
        """Update agent status"""
        self.status = new_status
        self.updated_at = datetime.now()
    
    def add_capability(self, capability: str, details: Any):
        """Add a new capability to the agent"""
        self.capabilities[capability] = details
        self.updated_at = datetime.now()


@dataclass
class Task:
    """
    Represents a task that can be executed by an agent.
    Contains all necessary information for task execution.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    name: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Aliases for backward compatibility
TaskEntity = Task
TaskId = str
ExecutionPlanEntity = Dict[str, Any]  # Placeholder for execution plan
    
    def start_execution(self):
        """Mark task as started"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete_execution(self, output_data: Dict[str, Any]):
        """Mark task as completed with output data"""
        self.status = TaskStatus.COMPLETED
        self.output_data = output_data
        self.completed_at = datetime.now()
    
    def fail_execution(self, error_message: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.output_data = {"error": error_message}
        self.completed_at = datetime.now()


@dataclass
class MemoryEntry:
    """
    Represents a memory entry for an agent.
    Can store various types of information with embeddings for similarity search.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    memory_type: str = "general"
    content: str = ""
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance_score: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    
    def access(self):
        """Update access timestamp"""
        self.accessed_at = datetime.now()
    
    def update_importance(self, score: float):
        """Update importance score"""
        self.importance_score = max(0.0, min(1.0, score))


@dataclass
class LearningEvent:
    """
    Represents a learning event that can be shared between agents.
    Contains knowledge that agents can learn from each other.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    event_type: str = "experience"
    event_data: Dict[str, Any] = field(default_factory=dict)
    embedding_vector: Optional[List[float]] = None
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    
    def update_confidence(self, new_confidence: float):
        """Update confidence score"""
        self.confidence = max(0.0, min(1.0, new_confidence))


@dataclass
class SystemAnalytics:
    """
    Represents system analytics and performance metrics.
    Used for monitoring and optimization.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedMemory:
    """
    Represents shared memory accessible by multiple agents.
    Contains data that can be shared across the system.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key: str = ""
    value: Dict[str, Any] = field(default_factory=dict)
    owner_agent_id: Optional[str] = None
    access_permissions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update_value(self, new_value: Dict[str, Any]):
        """Update shared memory value"""
        self.value = new_value
        self.updated_at = datetime.now()


@dataclass
class ToolUsage:
    """
    Represents tool usage by an agent.
    Tracks which tools are used and their effectiveness.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    tool_name: str = ""
    usage_data: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    execution_time: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ErrorLog:
    """
    Represents an error log entry.
    Used for tracking and debugging system issues.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: Optional[str] = None
    error_type: str = ""
    error_message: str = ""
    stack_trace: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "error"
    timestamp: datetime = field(default_factory=datetime.now)
