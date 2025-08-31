"""
Planner Agent - Intelligent task planning and coordination
Entry point for TTKi multi-agent system
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .base_agent import BaseAgent, Task, TaskType, TaskPriority, AgentResult
from .task_router import TaskRouter

logger = logging.getLogger(__name__)

@dataclass
class ExecutionPlan:
    """Plan wykonania zadań"""
    plan_id: str
    original_request: str
    tasks: List[Task]
    estimated_total_duration: float
    complexity_score: float
    parallel_groups: List[List[str]] = None  # Grupy zadań do równoległego wykonania
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class PlannerAgent(BaseAgent):
    """
    Planner Agent - Intelligent Task Planning and Coordination
    
    Główny punkt wejściowy dla systemu TTKi multi-agent.
    Odpowiedzialny za:
    - Analizę zadań użytkownika
    - Dekompozycję złożonych zadań
    - Routing do odpowiednich agentów
    - Koordinację wykonania
    - Optymalizację przepływu pracy
    """
    
    def __init__(self, agent_id: str = "planner_001"):
        super().__init__(
            agent_id=agent_id,
            agent_type="PlannerAgent",
            capabilities=[
                "task_analysis", "task_decomposition", "agent_routing",
                "execution_planning", "workflow_optimization", "coordination"
            ]
        )
        self.task_router = TaskRouter()
        self.execution_plans: Dict[str, ExecutionPlan] = {}
        self.available_agents: Dict[str, BaseAgent] = {}
        self.plan_counter = 0
    
    def register_agent(self, agent: BaseAgent):
        """Rejestruje agenta w systemie"""
        self.available_agents[agent.state.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.state.agent_type} ({agent.state.agent_id})")
    
    def can_handle_task(self, task: Task) -> bool:
        """PlannerAgent może obsłużyć wszystkie typy zadań jako entry point"""
        return True
    
    async def execute_task(self, task: Task) -> AgentResult:
        """Wykonuje zadanie planowania"""
        start_time = datetime.now()
        
        try:
            if task.type == TaskType.PLANNING:
                result = await self._plan_execution(task.description)
            else:
                # Dla innych typów zadań - utwórz plan i wykonaj
                result = await self._create_and_execute_plan(task.description)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            agent_result = AgentResult(
                success=True,
                result=result,
                duration=duration,
                metrics={'plans_created': 1}
            )
            
            self.update_performance_metrics(task, agent_result)
            return agent_result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Error in PlannerAgent: {str(e)}")
            
            return AgentResult(
                success=False,
                result=None,
                error=str(e),
                duration=duration
            )
    
    async def _plan_execution(self, user_request: str) -> ExecutionPlan:
        """Tworzy plan wykonania dla zadania użytkownika"""
        self.logger.info(f"Creating execution plan for: {user_request}")
        
        # Dekompozycja zadania
        tasks = self.task_router.decompose_complex_task(user_request)
        
        # Oblicz złożoność i estymowany czas
        total_duration = sum(task.estimated_duration for task in tasks)
        complexity_score = self._calculate_complexity_score(tasks)
        
        # Identyfikuj grupy równoległe
        parallel_groups = self._identify_parallel_groups(tasks)
        
        # Utwórz plan
        plan = ExecutionPlan(
            plan_id=self._generate_plan_id(),
            original_request=user_request,
            tasks=tasks,
            estimated_total_duration=total_duration,
            complexity_score=complexity_score,
            parallel_groups=parallel_groups
        )
        
        self.execution_plans[plan.plan_id] = plan
        
        self.logger.info(f"Created plan {plan.plan_id} with {len(tasks)} tasks")
        return plan
    
    async def _create_and_execute_plan(self, user_request: str) -> Dict[str, Any]:
        """Tworzy plan i koordynuje jego wykonanie"""
        # Utwórz plan
        plan = await self._plan_execution(user_request)
        
        # Wykonaj plan
        execution_result = await self._execute_plan(plan)
        
        return {
            'plan': plan,
            'execution_result': execution_result
        }
    
    async def _execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Wykonuje plan zadań"""
        self.logger.info(f"Executing plan {plan.plan_id}")
        
        results = {}
        completed_tasks = []
        failed_tasks = []
        
        try:
            for task in plan.tasks:
                # Sprawdź zależności
                if self._dependencies_satisfied(task, completed_tasks):
                    # Znajdź odpowiedniego agenta
                    agent = self._select_agent_for_task(task)
                    
                    if agent:
                        self.logger.info(f"Executing task {task.id} with {agent.state.agent_type}")
                        result = await agent.execute_task(task)
                        
                        results[task.id] = result
                        
                        if result.success:
                            completed_tasks.append(task.id)
                        else:
                            failed_tasks.append(task.id)
                            self.logger.error(f"Task {task.id} failed: {result.error}")
                    else:
                        self.logger.warning(f"No suitable agent found for task {task.id}")
                        failed_tasks.append(task.id)
                else:
                    self.logger.warning(f"Dependencies not satisfied for task {task.id}")
                    failed_tasks.append(task.id)
            
            return {
                'plan_id': plan.plan_id,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'task_results': results,
                'success_rate': len(completed_tasks) / len(plan.tasks) if plan.tasks else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error executing plan {plan.plan_id}: {str(e)}")
            return {
                'plan_id': plan.plan_id,
                'error': str(e),
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks
            }
    
    def _select_agent_for_task(self, task: Task) -> Optional[BaseAgent]:
        """Wybiera najlepszego agenta dla zadania"""
        suitable_agents = []
        
        for agent in self.available_agents.values():
            if agent.can_handle_task(task):
                # Oblicz score agenta
                score = self._calculate_agent_score(agent, task)
                suitable_agents.append((agent, score))
        
        if suitable_agents:
            # Wybierz agenta z najwyższym score
            suitable_agents.sort(key=lambda x: x[1], reverse=True)
            return suitable_agents[0][0]
        
        return None
    
    def _calculate_agent_score(self, agent: BaseAgent, task: Task) -> float:
        """Oblicza score agenta dla zadania"""
        score = 0.0
        
        # Performance metrics
        success_rate = agent.state.performance_metrics.get('success_rate', 0.5)
        score += success_rate * 50
        
        # Queue size (preferuj agentów z mniejszą kolejką)
        queue_size = len(agent.state.task_queue)
        score -= queue_size * 5
        
        # Specialized capability match
        task_type_match = task.type.value in agent.state.capabilities
        if task_type_match:
            score += 30
        
        return score
    
    def _dependencies_satisfied(self, task: Task, completed_tasks: List[str]) -> bool:
        """Sprawdza czy zależności zadania są spełnione"""
        return all(dep_id in completed_tasks for dep_id in task.dependencies)
    
    def _calculate_complexity_score(self, tasks: List[Task]) -> float:
        """Oblicza score złożoności planu"""
        if not tasks:
            return 0.0
        
        base_score = len(tasks) * 0.2
        dependency_score = sum(len(task.dependencies) for task in tasks) * 0.1
        duration_score = sum(task.estimated_duration for task in tasks) * 0.05
        
        return base_score + dependency_score + duration_score
    
    def _identify_parallel_groups(self, tasks: List[Task]) -> List[List[str]]:
        """Identyfikuje grupy zadań do równoległego wykonania"""
        # Prosty algorytm - zadania bez zależności mogą być wykonywane równolegle
        parallel_groups = []
        independent_tasks = []
        
        for task in tasks:
            if not task.dependencies:
                independent_tasks.append(task.id)
        
        if len(independent_tasks) > 1:
            parallel_groups.append(independent_tasks)
        
        return parallel_groups
    
    def _generate_plan_id(self) -> str:
        """Generuje unikalny ID planu"""
        self.plan_counter += 1
        return f"plan_{self.plan_counter:06d}"
    
    def get_plan_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Zwraca status planu"""
        if plan_id in self.execution_plans:
            plan = self.execution_plans[plan_id]
            return {
                'plan_id': plan.plan_id,
                'original_request': plan.original_request,
                'task_count': len(plan.tasks),
                'estimated_duration': plan.estimated_total_duration,
                'complexity_score': plan.complexity_score,
                'created_at': plan.created_at.isoformat()
            }
        return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Zwraca status całego systemu multi-agent"""
        return {
            'planner_agent': self.get_status(),
            'registered_agents': {
                agent_id: agent.get_status() 
                for agent_id, agent in self.available_agents.items()
            },
            'active_plans': len(self.execution_plans),
            'routing_stats': self.task_router.get_routing_stats()
        }
