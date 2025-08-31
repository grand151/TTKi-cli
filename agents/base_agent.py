"""
Base Agent Class - Shared functionality for all TTKi agents
Inspired by AI Manus architecture patterns
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Typy zadań w systemie TTKi"""
    VISION_ANALYSIS = "vision_analysis"
    CODE_GENERATION = "code_generation"
    FILE_OPERATIONS = "file_operations"
    TERMINAL_COMMANDS = "terminal_commands"
    BROWSER_AUTOMATION = "browser_automation"
    PLANNING = "planning"
    TESTING = "testing"
    OPTIMIZATION = "optimization"

class TaskPriority(Enum):
    """Priorytet zadań"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Reprezentacja zadania w systemie"""
    id: str
    type: TaskType
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    parent_task_id: Optional[str] = None
    estimated_duration: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"

@dataclass
class AgentState:
    """Stan bazowy agenta"""
    agent_id: str
    agent_type: str
    current_task: Optional[Task] = None
    task_queue: List[Task] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    session_start: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

@dataclass
class AgentResult:
    """Wynik działania agenta"""
    success: bool
    result: Any
    error: Optional[str] = None
    duration: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    next_actions: List[Task] = field(default_factory=list)

class BaseAgent(ABC):
    """
    Bazowa klasa dla wszystkich agentów TTKi
    Implementuje wspólną funkcjonalność i interfejs
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str] = None):
        self.state = AgentState(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities or []
        )
        self.history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"TTKi.{agent_type}.{agent_id}")
    
    @abstractmethod
    async def execute_task(self, task: Task) -> AgentResult:
        """Wykonanie zadania - implementowane przez konkretnych agentów"""
        pass
    
    @abstractmethod
    def can_handle_task(self, task: Task) -> bool:
        """Sprawdza czy agent może obsłużyć dane zadanie"""
        pass
    
    def estimate_task_duration(self, task: Task) -> float:
        """Estymacja czasu wykonania zadania"""
        # Domyślna implementacja - może być przesłonięta
        base_duration = {
            TaskType.VISION_ANALYSIS: 2.0,
            TaskType.CODE_GENERATION: 5.0,
            TaskType.FILE_OPERATIONS: 1.0,
            TaskType.TERMINAL_COMMANDS: 3.0,
            TaskType.BROWSER_AUTOMATION: 4.0,
            TaskType.PLANNING: 3.0,
            TaskType.TESTING: 6.0,
            TaskType.OPTIMIZATION: 8.0
        }.get(task.type, 3.0)
        
        return base_duration
    
    def update_performance_metrics(self, task: Task, result: AgentResult):
        """Aktualizuje metryki wydajności agenta"""
        if 'completed_tasks' not in self.state.performance_metrics:
            self.state.performance_metrics['completed_tasks'] = 0
        if 'success_rate' not in self.state.performance_metrics:
            self.state.performance_metrics['success_rate'] = 1.0
        if 'average_duration' not in self.state.performance_metrics:
            self.state.performance_metrics['average_duration'] = 0.0
        
        self.state.performance_metrics['completed_tasks'] += 1
        
        # Aktualizuj success rate
        total_tasks = self.state.performance_metrics['completed_tasks']
        current_success_rate = self.state.performance_metrics['success_rate']
        new_success_rate = ((current_success_rate * (total_tasks - 1)) + (1 if result.success else 0)) / total_tasks
        self.state.performance_metrics['success_rate'] = new_success_rate
        
        # Aktualizuj średni czas wykonania
        current_avg = self.state.performance_metrics['average_duration']
        new_avg = ((current_avg * (total_tasks - 1)) + result.duration) / total_tasks
        self.state.performance_metrics['average_duration'] = new_avg
        
        self.state.last_activity = datetime.now()
    
    def add_task_to_queue(self, task: Task):
        """Dodaje zadanie do kolejki agenta"""
        self.state.task_queue.append(task)
        # Sortuj według priorytetu
        self.state.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
    
    def get_next_task(self) -> Optional[Task]:
        """Pobiera następne zadanie z kolejki"""
        if self.state.task_queue:
            return self.state.task_queue.pop(0)
        return None
    
    def record_action(self, task: Task, result: AgentResult):
        """Rejestruje wykonaną akcję w historii"""
        action_record = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task.id,
            'task_type': task.type.value,
            'task_description': task.description,
            'success': result.success,
            'duration': result.duration,
            'error': result.error,
            'metrics': result.metrics
        }
        self.history.append(action_record)
        
        # Ogranicz historię do ostatnich 1000 akcji
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca aktualny status agenta"""
        return {
            'agent_id': self.state.agent_id,
            'agent_type': self.state.agent_type,
            'current_task': self.state.current_task.description if self.state.current_task else None,
            'queue_size': len(self.state.task_queue),
            'capabilities': self.state.capabilities,
            'performance_metrics': self.state.performance_metrics,
            'last_activity': self.state.last_activity.isoformat(),
            'uptime': (datetime.now() - self.state.session_start).total_seconds()
        }
