"""
Domain Value Objects - Immutable objects without identity
"""
from enum import Enum
from dataclasses import dataclass
from typing import Any
import uuid

class TaskType(Enum):
    """Task types in the TTKi system"""
    VISION_ANALYSIS = "vision_analysis"
    CODE_GENERATION = "code_generation"
    FILE_OPERATIONS = "file_operations"
    TERMINAL_COMMANDS = "terminal_commands"
    BROWSER_AUTOMATION = "browser_automation"
    PLANNING = "planning"
    TESTING = "testing"
    OPTIMIZATION = "optimization"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(frozen=True)
class TaskId:
    """Task identifier value object"""
    value: str
    
    @classmethod
    def generate(cls) -> 'TaskId':
        """Generate new task ID"""
        return cls(f"task_{uuid.uuid4().hex[:8]}")
    
    @classmethod
    def from_string(cls, value: str) -> 'TaskId':
        """Create from string"""
        return cls(value)
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class AgentId:
    """Agent identifier value object"""
    value: str
    
    @classmethod
    def generate(cls, agent_type: str) -> 'AgentId':
        """Generate new agent ID"""
        return cls(f"{agent_type}_{uuid.uuid4().hex[:8]}")
    
    @classmethod
    def from_string(cls, value: str) -> 'AgentId':
        """Create from string"""
        return cls(value)
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class ExecutionPlanId:
    """Execution plan identifier value object"""
    value: str
    
    @classmethod
    def generate(cls) -> 'ExecutionPlanId':
        """Generate new plan ID"""
        return cls(f"plan_{uuid.uuid4().hex[:8]}")
    
    @classmethod
    def from_string(cls, value: str) -> 'ExecutionPlanId':
        """Create from string"""
        return cls(value)
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class TaskResult:
    """Task execution result value object"""
    success: bool
    data: Any = None
    error_message: str = None
    duration: float = 0.0
    metrics: dict = None
    
    def __post_init__(self):
        if self.metrics is None:
            object.__setattr__(self, 'metrics', {})

@dataclass(frozen=True)
class AgentCapability:
    """Agent capability value object"""
    name: str
    description: str
    complexity_factor: float = 1.0
    
    def can_handle_task_type(self, task_type: TaskType) -> bool:
        """Check if capability can handle task type"""
        return self.name == task_type.value

@dataclass(frozen=True)
class PerformanceMetrics:
    """Agent performance metrics value object"""
    success_rate: float = 0.0
    average_duration: float = 0.0
    total_tasks_completed: int = 0
    error_rate: float = 0.0
    efficiency_score: float = 0.0
    
    def calculate_efficiency_score(self) -> float:
        """Calculate overall efficiency score"""
        if self.total_tasks_completed == 0:
            return 0.0
        
        # Weighted score based on success rate and speed
        speed_factor = max(0.1, 1.0 / (self.average_duration + 0.1))
        efficiency = (self.success_rate * 0.7) + (speed_factor * 0.3)
        
        return min(1.0, efficiency)
    
    def update_with_result(self, result: TaskResult) -> 'PerformanceMetrics':
        """Update metrics with new task result"""
        new_total = self.total_tasks_completed + 1
        
        # Update success rate
        current_successes = self.success_rate * self.total_tasks_completed
        new_successes = current_successes + (1 if result.success else 0)
        new_success_rate = new_successes / new_total
        
        # Update average duration
        current_total_duration = self.average_duration * self.total_tasks_completed
        new_total_duration = current_total_duration + result.duration
        new_average_duration = new_total_duration / new_total
        
        # Update error rate
        current_errors = self.error_rate * self.total_tasks_completed
        new_errors = current_errors + (0 if result.success else 1)
        new_error_rate = new_errors / new_total
        
        updated_metrics = PerformanceMetrics(
            success_rate=new_success_rate,
            average_duration=new_average_duration,
            total_tasks_completed=new_total,
            error_rate=new_error_rate,
            efficiency_score=0.0  # Will be calculated
        )
        
        # Calculate new efficiency score
        object.__setattr__(
            updated_metrics, 
            'efficiency_score', 
            updated_metrics.calculate_efficiency_score()
        )
        
        return updated_metrics
