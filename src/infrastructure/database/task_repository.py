"""
Task Repository - Database operations for Task entities
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.entities import TaskEntity
from ...domain.value_objects import TaskId, AgentId, TaskStatus, TaskType, TaskPriority
from .database_manager import get_database_manager

class TaskRepository:
    """Repository for Task database operations"""
    
    async def save(self, task: TaskEntity) -> bool:
        """Save task to database"""
        db = await get_database_manager()
        
        try:
            await db.execute_command("""
                INSERT INTO tasks (
                    id, task_id, description, task_type, priority, status,
                    assigned_agent_id, parent_task_id, parameters, result,
                    estimated_duration, actual_duration, complexity_score,
                    created_at, started_at, completed_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    result = EXCLUDED.result,
                    actual_duration = EXCLUDED.actual_duration,
                    started_at = EXCLUDED.started_at,
                    completed_at = EXCLUDED.completed_at
            """,
                str(task.id.value) if hasattr(task.id, 'value') else str(task.id),
                str(task.id),
                task.description,
                task.task_type.value if hasattr(task.task_type, 'value') else str(task.task_type),
                task.priority.value if hasattr(task.priority, 'value') else int(task.priority),
                task.status.value if hasattr(task.status, 'value') else str(task.status),
                str(task.assigned_agent_id) if task.assigned_agent_id else None,
                str(task.parent_task_id) if task.parent_task_id else None,
                task.parameters,
                None,  # result - will be updated later
                int(task.estimated_duration),
                int(task.actual_duration) if task.actual_duration else None,
                0.5,  # default complexity_score
                task.created_at,
                task.started_at,
                task.completed_at
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Task save failed: {e}")
            return False
    
    async def find_by_id(self, task_id: TaskId) -> Optional[TaskEntity]:
        """Find task by ID"""
        db = await get_database_manager()
        
        result = await db.execute_single(
            "SELECT * FROM tasks WHERE task_id = $1",
            str(task_id),
            readonly=True
        )
        
        if result:
            return TaskEntity(
                id=TaskId.from_string(result['task_id']),
                description=result['description'],
                task_type=TaskType(result['task_type']),
                priority=TaskPriority(result['priority']),
                status=TaskStatus(result['status']),
                parameters=result['parameters'] or {},
                estimated_duration=result['estimated_duration'] or 0.0,
                actual_duration=result['actual_duration'],
                created_at=result['created_at'],
                started_at=result['started_at'],
                completed_at=result['completed_at'],
                assigned_agent_id=AgentId(result['assigned_agent_id']) if result['assigned_agent_id'] else None
            )
        
        return None
    
    async def find_by_status(self, status: TaskStatus) -> List[TaskEntity]:
        """Find tasks by status"""
        db = await get_database_manager()
        
        results = await db.execute_query(
            "SELECT * FROM tasks WHERE status = $1 ORDER BY priority ASC, created_at ASC",
            status.value if hasattr(status, 'value') else str(status),
            readonly=True
        )
        
        return [self._map_to_entity(result) for result in results]
    
    async def find_by_agent(self, agent_id: AgentId) -> List[TaskEntity]:
        """Find tasks assigned to agent"""
        db = await get_database_manager()
        
        results = await db.execute_query(
            "SELECT * FROM tasks WHERE assigned_agent_id = $1 ORDER BY created_at DESC",
            str(agent_id),
            readonly=True
        )
        
        return [self._map_to_entity(result) for result in results]
    
    async def update_status(self, task_id: TaskId, status: TaskStatus) -> bool:
        """Update task status"""
        db = await get_database_manager()
        
        try:
            timestamp_field = None
            if status == TaskStatus.RUNNING:
                timestamp_field = "started_at = NOW(),"
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                timestamp_field = "completed_at = NOW(),"
            
            query = f"""
                UPDATE tasks SET 
                    status = $1,
                    {timestamp_field or ''}
                WHERE task_id = $2
            """.strip().rstrip(',')
            
            await db.execute_command(query, str(status), str(task_id))
            return True
            
        except Exception as e:
            print(f"❌ Status update failed: {e}")
            return False
    
    async def update_result(self, task_id: TaskId, result: Dict[str, Any]) -> bool:
        """Update task result"""
        db = await get_database_manager()
        
        try:
            await db.execute_command(
                "UPDATE tasks SET result = $1 WHERE task_id = $2",
                result,
                str(task_id)
            )
            return True
            
        except Exception as e:
            print(f"❌ Result update failed: {e}")
            return False
    
    async def assign_to_agent(self, task_id: TaskId, agent_id: AgentId) -> bool:
        """Assign task to agent"""
        db = await get_database_manager()
        
        try:
            await db.execute_command(
                "UPDATE tasks SET assigned_agent_id = $1 WHERE task_id = $2",
                str(agent_id),
                str(task_id)
            )
            return True
            
        except Exception as e:
            print(f"❌ Task assignment failed: {e}")
            return False
    
    def _map_to_entity(self, result: Dict[str, Any]) -> TaskEntity:
        """Map database result to TaskEntity"""
        return TaskEntity(
            id=TaskId.from_string(result['task_id']),
            description=result['description'],
            task_type=TaskType(result['task_type']),
            priority=TaskPriority(result['priority']),
            status=TaskStatus(result['status']),
            parameters=result['parameters'] or {},
            estimated_duration=result['estimated_duration'] or 0.0,
            actual_duration=result['actual_duration'],
            created_at=result['created_at'],
            started_at=result['started_at'],
            completed_at=result['completed_at'],
            assigned_agent_id=AgentId(result['assigned_agent_id']) if result['assigned_agent_id'] else None
        )
