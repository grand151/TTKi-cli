"""
Agent Orchestrator Domain Service
Core business logic for managing multi-agent coordination
"""
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from ..entities import AgentEntity, TaskEntity, ExecutionPlanEntity
from ..value_objects import TaskId, AgentId, TaskStatus, TaskType, TaskResult, PerformanceMetrics
from ..repositories import AgentRepository, TaskRepository, ExecutionPlanRepository

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Domain service for orchestrating multi-agent task execution
    Core business logic for TTKi multi-agent system
    """
    
    def __init__(
        self,
        agent_repository: Optional[AgentRepository] = None,
        task_repository: Optional[TaskRepository] = None,
        plan_repository: Optional[ExecutionPlanRepository] = None
    ):
        # Repositories will be injected via DI container
        self._agent_repository = agent_repository
        self._task_repository = task_repository
        self._plan_repository = plan_repository
        
        # In-memory cache for active agents (for performance)
        self._active_agents: Dict[AgentId, AgentEntity] = {}
        self._execution_lock = asyncio.Lock()
    
    async def register_agent(self, agent: AgentEntity) -> None:
        """Register new agent in the system"""
        self._active_agents[agent.id] = agent
        
        if self._agent_repository:
            await self._agent_repository.save(agent)
        
        logger.info(f"Registered agent: {agent.agent_type} ({agent.id})")
    
    async def execute_plan(self, plan: ExecutionPlanEntity) -> Dict[str, any]:
        """
        Execute an execution plan with multi-agent coordination
        Core business logic for plan execution
        """
        async with self._execution_lock:
            logger.info(f"Starting execution of plan {plan.id}")
            
            plan.start_execution()
            completed_task_ids: List[TaskId] = []
            failed_task_ids: List[TaskId] = []
            task_results: Dict[TaskId, TaskResult] = {}
            
            try:
                while True:
                    # Get tasks ready for execution
                    ready_tasks = plan.get_ready_tasks(completed_task_ids)
                    
                    if not ready_tasks:
                        # No more ready tasks - check if we're done
                        pending_tasks = [t for t in plan.tasks if t.status == TaskStatus.PENDING]
                        if not pending_tasks:
                            break  # All tasks processed
                        
                        # Check for deadlock (dependencies can't be satisfied)
                        if self._has_circular_dependencies(pending_tasks):
                            logger.error(f"Circular dependencies detected in plan {plan.id}")
                            break
                        
                        # Wait a bit and try again
                        await asyncio.sleep(0.1)
                        continue
                    
                    # Execute ready tasks
                    execution_tasks = []
                    for task in ready_tasks:
                        agent = await self._select_best_agent(task)
                        if agent:
                            execution_task = self._execute_task_with_agent(task, agent)
                            execution_tasks.append(execution_task)
                    
                    # Wait for task completion
                    if execution_tasks:
                        results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                        
                        for i, result in enumerate(results):
                            task = ready_tasks[i]
                            
                            if isinstance(result, Exception):
                                # Task failed with exception
                                task.fail(str(result), 0.0)
                                failed_task_ids.append(task.id)
                                task_results[task.id] = TaskResult(
                                    success=False,
                                    error_message=str(result)
                                )
                            else:
                                # Task completed
                                if result.success:
                                    completed_task_ids.append(task.id)
                                else:
                                    failed_task_ids.append(task.id)
                                
                                task_results[task.id] = result
                
                # Calculate final results
                success_rate = len(completed_task_ids) / len(plan.tasks) if plan.tasks else 0
                total_duration = (datetime.now() - plan.started_at).total_seconds()
                
                plan.complete_execution(success_rate, total_duration)
                
                return {
                    'plan_id': str(plan.id),
                    'success': success_rate > 0.5,  # Consider successful if >50% tasks completed
                    'completed_tasks': [str(tid) for tid in completed_task_ids],
                    'failed_tasks': [str(tid) for tid in failed_task_ids],
                    'task_results': {str(k): v for k, v in task_results.items()},
                    'success_rate': success_rate,
                    'duration': total_duration,
                    'completion_percentage': plan.get_completion_percentage()
                }
                
            except Exception as e:
                logger.error(f"Error executing plan {plan.id}: {str(e)}")
                return {
                    'plan_id': str(plan.id),
                    'success': False,
                    'error': str(e),
                    'completed_tasks': [str(tid) for tid in completed_task_ids],
                    'failed_tasks': [str(tid) for tid in failed_task_ids]
                }
    
    async def _select_best_agent(self, task: TaskEntity) -> Optional[AgentEntity]:
        """
        Select the best agent for a task based on business rules
        """
        suitable_agents = []
        
        for agent in self._active_agents.values():
            if agent.status == "available" and agent.can_handle_task(task.task_type):
                score = self._calculate_agent_score(agent, task)
                suitable_agents.append((agent, score))
        
        if not suitable_agents:
            logger.warning(f"No suitable agent found for task {task.id} (type: {task.task_type})")
            return None
        
        # Select agent with highest score
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        best_agent = suitable_agents[0][0]
        
        logger.info(f"Selected agent {best_agent.id} for task {task.id}")
        return best_agent
    
    def _calculate_agent_score(self, agent: AgentEntity, task: TaskEntity) -> float:
        """
        Calculate agent suitability score for a task
        Business logic for agent selection
        """
        score = 0.0
        
        # Performance-based scoring
        if 'success_rate' in agent.performance_metrics:
            score += agent.performance_metrics['success_rate'] * 50
        
        # Queue size penalty (prefer less busy agents)
        queue_penalty = len(agent.task_queue) * 10
        score -= queue_penalty
        
        # Task type specialization bonus
        task_type_capability = task.task_type.value in agent.capabilities
        if task_type_capability:
            score += 30
        
        # Priority boost for high-priority tasks
        if task.priority.value >= 3:  # HIGH or CRITICAL
            score += 20
        
        # Recent activity bonus (prefer active agents)
        time_since_activity = (datetime.now() - agent.last_activity).total_seconds()
        if time_since_activity < 60:  # Active in last minute
            score += 10
        
        return max(0.0, score)
    
    async def _execute_task_with_agent(self, task: TaskEntity, agent: AgentEntity) -> TaskResult:
        """
        Execute a task with a specific agent using real implementations
        """
        start_time = datetime.now()
        
        try:
            # Assign task to agent
            agent.assign_task(task.id)
            task.start(agent.id)
            
            # Get real agent implementation
            real_agent = await self._get_real_agent_implementation(agent)
            
            if real_agent:
                # Execute with real agent
                result = await real_agent.execute_task(task.description, task.parameters)
            else:
                # Fallback to simulation
                result = await self._simulate_task_execution(task, agent)
            
            # Update task and agent
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.success:
                task.complete(result.data, duration)
            else:
                task.fail(result.error_message, duration)
            
            agent.complete_task()
            
            # Update agent performance metrics
            if 'success_rate' in agent.performance_metrics:
                current_metrics = PerformanceMetrics(
                    success_rate=agent.performance_metrics.get('success_rate', 0.0),
                    average_duration=agent.performance_metrics.get('average_duration', 0.0),
                    total_tasks_completed=agent.performance_metrics.get('total_tasks_completed', 0),
                    error_rate=agent.performance_metrics.get('error_rate', 0.0)
                )
                updated_metrics = current_metrics.update_with_result(result)
                
                agent.performance_metrics.update({
                    'success_rate': updated_metrics.success_rate,
                    'average_duration': updated_metrics.average_duration,
                    'total_tasks_completed': updated_metrics.total_tasks_completed,
                    'error_rate': updated_metrics.error_rate,
                    'efficiency_score': updated_metrics.efficiency_score
                })
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            task.fail(str(e), duration)
            agent.complete_task()
            
            return TaskResult(
                success=False,
                error_message=str(e),
                duration=duration
            )
    
    def _get_real_agent_implementation(self, agent_type: str):
        """Get real agent implementation based on type"""
        
        if agent_type == "desktop":
            from ...infrastructure.agents.desktop_agent_hybrid import DesktopAgent
            return DesktopAgent()
        
        elif agent_type == "vision":
            from ...infrastructure.agents.vision_agent import VisionAgent
            return VisionAgent()
        
        elif agent_type == "coding":
            from ...infrastructure.agents.coding_agent import CodingAgent
            return CodingAgent()
        
        elif agent_type == "file":
            from ...infrastructure.agents.file_agent import FileAgent
            return FileAgent()
        
        elif agent_type == "terminal":
            from ...infrastructure.agents.terminal_agent import TerminalAgent
            return TerminalAgent()
        
        elif agent_type == "browser":
            from ...infrastructure.agents.browser_agent import BrowserAgent
            return BrowserAgent()
        
        else:
            logger.warning(f"No real implementation found for agent type: {agent_type}")
            return None
    
    async def _simulate_task_execution(self, task: TaskEntity, agent: AgentEntity) -> TaskResult:
        """
        Simulate task execution for testing
        TODO: Replace with actual agent integration
        """
        # Simulate processing time based on task complexity
        base_duration = {
            TaskType.VISION_ANALYSIS: 2.0,
            TaskType.CODE_GENERATION: 5.0,
            TaskType.FILE_OPERATIONS: 1.0,
            TaskType.TERMINAL_COMMANDS: 3.0,
            TaskType.BROWSER_AUTOMATION: 4.0,
            TaskType.PLANNING: 3.0,
            TaskType.TESTING: 6.0,
            TaskType.OPTIMIZATION: 8.0
        }.get(task.task_type, 3.0)
        
        await asyncio.sleep(min(base_duration, 0.5))  # Cap simulation time
        
        # Simulate success based on agent performance
        success_rate = agent.performance_metrics.get('success_rate', 0.8)
        import random
        success = random.random() < success_rate
        
        if success:
            return TaskResult(
                success=True,
                data=f"Task {task.id} completed successfully by {agent.id}",
                duration=base_duration
            )
        else:
            return TaskResult(
                success=False,
                error_message=f"Simulated failure for task {task.id}",
                duration=base_duration
            )
    
    def _has_circular_dependencies(self, tasks: List[TaskEntity]) -> bool:
        """
        Check for circular dependencies in task list
        """
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: TaskId, task_map: Dict[TaskId, TaskEntity]) -> bool:
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            if task_id in task_map:
                task = task_map[task_id]
                for dep_id in task.dependencies:
                    if has_cycle(dep_id, task_map):
                        return True
            
            rec_stack.remove(task_id)
            return False
        
        task_map = {task.id: task for task in tasks}
        
        for task in tasks:
            if task.id not in visited:
                if has_cycle(task.id, task_map):
                    return True
        
        return False
    
    def get_system_status(self) -> Dict[str, any]:
        """Get orchestrator system status"""
        return {
            'active_agents': len(self._active_agents),
            'agent_details': {
                str(agent_id): {
                    'type': agent.agent_type,
                    'status': agent.status,
                    'queue_size': len(agent.task_queue),
                    'performance': agent.performance_metrics
                }
                for agent_id, agent in self._active_agents.items()
            }
        }
