"""
Execution Planning Service - Domain service for creating execution plans
"""
import logging
from typing import List, Dict, Any
from datetime import datetime

from ..entities import TaskEntity, ExecutionPlanEntity
from ..value_objects import TaskId, TaskType, TaskPriority, ExecutionPlanId
from .task_analysis_service import TaskAnalysisService

logger = logging.getLogger(__name__)

class ExecutionPlanningService:
    """
    Domain service for creating and optimizing execution plans
    """
    
    def __init__(self):
        self.task_analyzer = TaskAnalysisService()
        self.plan_counter = 0
    
    def create_execution_plan(
        self, 
        user_request: str, 
        context: Dict[str, Any] = None
    ) -> ExecutionPlanEntity:
        """
        Create an execution plan from user request
        """
        # Analyze if task needs decomposition
        if self.task_analyzer.is_complex_task(user_request):
            subtask_descriptions = self.task_analyzer.extract_subtasks(user_request)
            tasks = self._create_task_entities(subtask_descriptions, context)
        else:
            # Single task
            analysis = self.task_analyzer.analyze_task(user_request)
            task = TaskEntity(
                id=TaskId.generate(),
                description=user_request,
                task_type=analysis.task_type,
                priority=analysis.priority,
                estimated_duration=analysis.estimated_duration,
                parameters=context or {}
            )
            tasks = [task]
        
        # Create execution plan
        plan_id = ExecutionPlanId.generate()
        plan = ExecutionPlanEntity(
            id=str(plan_id),
            original_request=user_request,
            tasks=tasks,
            estimated_total_duration=sum(task.estimated_duration for task in tasks),
            complexity_score=self._calculate_complexity_score(tasks),
            parallel_groups=self._identify_parallel_groups(tasks)
        )
        
        self.plan_counter += 1
        return plan
    
    def _create_task_entities(
        self, 
        task_descriptions: List[str], 
        context: Dict[str, Any] = None
    ) -> List[TaskEntity]:
        """Create task entities from descriptions"""
        tasks = []
        
        for i, description in enumerate(task_descriptions):
            analysis = self.task_analyzer.analyze_task(description)
            
            # Set up dependencies (sequential by default)
            dependencies = []
            if i > 0:
                dependencies = [tasks[i-1].id]
            
            task = TaskEntity(
                id=TaskId.generate(),
                description=description.strip(),
                task_type=analysis.task_type,
                priority=analysis.priority,
                estimated_duration=analysis.estimated_duration,
                parameters=context or {},
                dependencies=dependencies
            )
            tasks.append(task)
        
        return tasks
    
    def _calculate_complexity_score(self, tasks: List[TaskEntity]) -> float:
        """Calculate complexity score for the plan"""
        if not tasks:
            return 0.0
        
        base_score = len(tasks) * 0.3
        dependency_score = sum(len(task.dependencies) for task in tasks) * 0.2
        duration_score = sum(task.estimated_duration for task in tasks) * 0.1
        
        # Task type complexity bonuses
        type_complexity = {
            TaskType.VISION_ANALYSIS: 0.8,
            TaskType.CODE_GENERATION: 1.2,
            TaskType.FILE_OPERATIONS: 0.6,
            TaskType.TERMINAL_COMMANDS: 0.7,
            TaskType.BROWSER_AUTOMATION: 1.0,
            TaskType.PLANNING: 1.5,
            TaskType.TESTING: 1.1,
            TaskType.OPTIMIZATION: 1.8
        }
        
        type_score = sum(type_complexity.get(task.task_type, 1.0) 
                        for task in tasks) * 0.1
        
        return base_score + dependency_score + duration_score + type_score
    
    def _identify_parallel_groups(self, tasks: List[TaskEntity]) -> List[List[str]]:
        """Identify groups of tasks that can run in parallel"""
        parallel_groups = []
        
        # Simple approach: tasks without dependencies can run in parallel
        independent_tasks = []
        for task in tasks:
            if not task.dependencies:
                independent_tasks.append(str(task.id))
        
        if len(independent_tasks) > 1:
            parallel_groups.append(independent_tasks)
        
        return parallel_groups
    
    def optimize_plan(self, plan: ExecutionPlanEntity) -> ExecutionPlanEntity:
        """Optimize execution plan for better performance"""
        # TODO: Implement plan optimization algorithms
        # - Dependency optimization
        # - Resource allocation optimization
        # - Critical path analysis
        
        return plan
