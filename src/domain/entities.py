"""
Domain Entities - Core business objects with identity
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import uuid

from .value_objects import TaskId, AgentId, TaskPriority, TaskStatus, TaskType

@dataclass
class TaskEntity:
    """
    Task Domain Entity
    Represents a single task in the TTKi system
    """
    id: TaskId
    description: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    parameters: Dict[str, Any] = field(default_factory=dict)
    parent_task_id: Optional[TaskId] = None
    dependencies: List[TaskId] = field(default_factory=list)
    estimated_duration: float = 0.0
    actual_duration: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_agent_id: Optional[AgentId] = None
    result: Any = None
    error: Optional[str] = None
    
    def start(self, agent_id: AgentId):
        """Start task execution"""
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"Cannot start task in status: {self.status}")
        
        self.status = TaskStatus.RUNNING
        self.assigned_agent_id = agent_id
        self.started_at = datetime.now()
    
    def complete(self, result: Any, duration: float):
        """Complete task successfully"""
        if self.status != TaskStatus.RUNNING:
            raise ValueError(f"Cannot complete task in status: {self.status}")
        
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.actual_duration = duration
        self.completed_at = datetime.now()
    
    def fail(self, error: str, duration: float):
        """Mark task as failed"""
        if self.status != TaskStatus.RUNNING:
            raise ValueError(f"Cannot fail task in status: {self.status}")
        
        self.status = TaskStatus.FAILED
        self.error = error
        self.actual_duration = duration
        self.completed_at = datetime.now()
    
    def can_start(self, completed_tasks: List[TaskId]) -> bool:
        """Check if task can start (dependencies satisfied)"""
        return all(dep in completed_tasks for dep in self.dependencies)

@dataclass
class AgentEntity:
    """
    Agent Domain Entity
    Represents an AI agent in the system
    """
    id: AgentId
    agent_type: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "available"
    current_task_id: Optional[TaskId] = None
    task_queue: List[TaskId] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def assign_task(self, task_id: TaskId):
        """Assign task to agent"""
        if self.status != "available":
            raise ValueError(f"Agent {self.id} is not available (status: {self.status})")
        
        self.current_task_id = task_id
        self.status = "busy"
        self.last_activity = datetime.now()
    
    def complete_task(self):
        """Mark current task as completed"""
        self.current_task_id = None
        self.status = "available"
        self.last_activity = datetime.now()
    
    def add_to_queue(self, task_id: TaskId):
        """Add task to agent's queue"""
        self.task_queue.append(task_id)
    
    def get_next_queued_task(self) -> Optional[TaskId]:
        """Get next task from queue"""
        if self.task_queue:
            return self.task_queue.pop(0)
        return None
    
    def can_handle_task(self, task_type: TaskType) -> bool:
        """Check if agent can handle task type"""
        return task_type.value in self.capabilities
    
    def update_performance(self, metric: str, value: float):
        """Update performance metric"""
        self.performance_metrics[metric] = value
        self.last_activity = datetime.now()

@dataclass
class ExecutionPlanEntity:
    """
    Execution Plan Domain Entity
    Represents a plan for executing multiple tasks
    """
    id: str
    original_request: str
    tasks: List[TaskEntity] = field(default_factory=list)
    status: str = "pending"
    estimated_total_duration: float = 0.0
    actual_duration: Optional[float] = None
    complexity_score: float = 0.0
    parallel_groups: List[List[TaskId]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success_rate: float = 0.0
    
    def start_execution(self):
        """Start plan execution"""
        if self.status != "pending":
            raise ValueError(f"Cannot start plan in status: {self.status}")
        
        self.status = "running"
        self.started_at = datetime.now()
    
    def complete_execution(self, success_rate: float, duration: float):
        """Complete plan execution"""
        if self.status != "running":
            raise ValueError(f"Cannot complete plan in status: {self.status}")
        
        self.status = "completed"
        self.success_rate = success_rate
        self.actual_duration = duration
        self.completed_at = datetime.now()
    
    def add_task(self, task: TaskEntity):
        """Add task to execution plan"""
        self.tasks.append(task)
        self.estimated_total_duration += task.estimated_duration
    
    def get_ready_tasks(self, completed_task_ids: List[TaskId]) -> List[TaskEntity]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        
        for task in self.tasks:
            if (task.status == TaskStatus.PENDING and 
                task.can_start(completed_task_ids)):
                ready_tasks.append(task)
        
        return ready_tasks
    
    def get_completion_percentage(self) -> float:
        """Get plan completion percentage"""
        if not self.tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in self.tasks 
                             if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED])
        return (completed_tasks / len(self.tasks)) * 100.0
