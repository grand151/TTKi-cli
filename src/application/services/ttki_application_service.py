"""
TTKi Application Service - Enhanced with Database Integration and Cross-Agent Learning
Main orchestration service that coordinates between DDD components and legacy systems.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Domain imports
from src.domain.entities.task import Task, TaskId
from src.domain.entities.agent import Agent, AgentId
from src.domain.value_objects.task_result import TaskResult
from src.domain.services.orchestration_service import OrchestrationService
from src.infrastructure.agent_registry import AgentRegistry
from src.infrastructure.hybrid_bridge import HybridBridge

# Database imports
from src.infrastructure.database.database_manager import DatabaseManager
from src.infrastructure.database.repositories.agent_repository import AgentRepository
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.infrastructure.database.repositories.learning_repository import LearningRepository
from src.infrastructure.database.repositories.memory_repository import MemoryRepository
from src.infrastructure.database.repositories.analytics_repository import AnalyticsRepository
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...domain.services.agent_orchestrator import AgentOrchestrator
from ...domain.value_objects import TaskId, AgentId, TaskResult
from ...infrastructure.legacy.planner_agent import PlannerAgent
from ...infrastructure.database.database_manager import get_database_manager, close_database_manager
from ...infrastructure.database.agent_repository import AgentRepository
from ...infrastructure.database.task_repository import TaskRepository
from ...infrastructure.database.learning_repository import LearningRepository
from ...infrastructure.database.memory_repository import MemoryRepository
from ...infrastructure.database.analytics_repository import AnalyticsRepository

logger = logging.getLogger(__name__)
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...domain.entities import TaskEntity, AgentEntity, ExecutionPlanEntity
from ...domain.value_objects import (
    TaskId, AgentId, TaskType, TaskPriority, TaskStatus, 
    ExecutionPlanId, AgentCapability
)
from ...domain.services.agent_orchestrator import AgentOrchestrator

# Import legacy components for gradual migration
try:
    from agents.planner_agent import PlannerAgent
    from agents.task_router import TaskRouter
    LEGACY_AGENTS_AVAILABLE = True
except ImportError:
    LEGACY_AGENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class TTKiApplicationService:
    """
    Main application service implementing TTKi use cases
    Enhanced with database integration and advanced analytics
    """
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.legacy_agent = PlannerAgent()
        
        # Database repositories
        self.agent_repo: Optional[AgentRepository] = None
        self.task_repo: Optional[TaskRepository] = None
        self.learning_repo: Optional[LearningRepository] = None
        self.memory_repo: Optional[MemoryRepository] = None
        self.analytics_repo: Optional[AnalyticsRepository] = None
        
        self._initialized = False
        
        logger.info("TTKi Application Service created")
    
    async def initialize(self):
        """Initialize application service with database connection"""
        try:
            # Initialize database manager
            await get_database_manager()
            
            # Initialize repositories
            self.agent_repo = AgentRepository()
            self.task_repo = TaskRepository()
            self.learning_repo = LearningRepository()
            self.memory_repo = MemoryRepository()
            self.analytics_repo = AnalyticsRepository()
            
            # Register default agents
            await self._register_default_agents()
            
            # Initialize system analytics
            await self._initialize_system_analytics()
            
            self._initialized = True
            logger.info("✅ TTKi Application Service initialized with database integration")
            
        except Exception as e:
            logger.error(f"❌ Application service initialization failed: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown application service"""
        try:
            if self._initialized:
                # Record shutdown metrics
                if self.analytics_repo:
                    await self.analytics_repo.record_system_metric(
                        "system", "shutdown_event", 1.0, "count"
                    )
                
                # Close database connections
                await close_database_manager()
                
                self._initialized = False
                logger.info("✅ TTKi Application Service shutdown complete")
                
        except Exception as e:
            logger.error(f"❌ Application service shutdown failed: {e}")
    
    async def _initialize_system_analytics(self):
        """Initialize system analytics and metrics"""
        try:
            await self.analytics_repo.record_system_metric(
                "system", "startup_event", 1.0, "count", "real_time", "count"
            )
            
            await self.analytics_repo.record_system_metric(
                "system", "database_integration", 1.0, "boolean", "real_time", "value"
            )
            
            logger.info("📊 System analytics initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Analytics initialization failed: {e}")
    
    async def _register_default_agents(self):
        """Register default agents in database"""
        try:
            default_agents = await self.orchestrator.get_registered_agents()
            
            for agent_data in default_agents:
                agent_id = AgentId(agent_data["agent_id"])
                
                # Save to database
                await self.agent_repo.save(agent_data["agent"])
                
                # Record agent registration
                await self.analytics_repo.record_system_metric(
                    "agents", "agent_registered", 1.0, "count"
                )
                
                logger.info(f"🤖 Registered agent: {agent_data['agent_type']}")
            
            logger.info("Legacy agents initialized for DDD integration")
            
        except Exception as e:
            logger.warning(f"⚠️ Agent registration failed: {e}")
    
    async def execute_task(
        self, 
        task_description: str, 
        agent_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """
        Execute task with full database integration and analytics
        """
        start_time = datetime.now()
        task_id = TaskId.generate()
        context = context or {}
        
        logger.info(f"🎯 Executing task: {task_description}")
        
        try:
            # Store task in memory for cross-agent access
            if self.memory_repo:
                await self.memory_repo.store_memory(
                    bank_name="global_patterns",
                    entry_key=f"task_{task_id}",
                    entry_type="active_task",
                    content={
                        "description": task_description,
                        "agent_type": agent_type,
                        "context": context,
                        "started_at": start_time.isoformat()
                    }
                )
            
            # Create execution plan
            plan = await self._create_execution_plan(task_description, agent_type, context)
            
            # Execute task
            if plan["use_orchestrator"]:
                # Use DDD orchestrator with database integration
                result = await self._execute_with_orchestrator(
                    task_id, task_description, agent_type, context, plan
                )
            else:
                # Use legacy agent for compatibility
                result = await self._execute_with_legacy_agent(
                    task_id, task_description, context
                )
            
            # Record analytics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_task_analytics(
                task_id, agent_type, execution_time, result.success
            )
            
            # Update cross-agent learning
            if result.success:
                await self._record_learning_event(
                    task_id, task_description, agent_type, result, context
                )
            
            logger.info(f"✅ Task completed: {result.success}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Task execution failed: {e}")
            
            # Record failure analytics
            await self._record_task_analytics(
                task_id, agent_type, execution_time, False, str(e)
            )
            
            return TaskResult(
                success=False,
                error_message=f"Task execution failed: {str(e)}",
                duration=execution_time
            )
    
    async def _create_execution_plan(
        self, 
        task_description: str, 
        agent_type: Optional[str], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create execution plan based on task complexity and requirements"""
        
        # Analyze task complexity
        requires_ai = any(keyword in task_description.lower() for keyword in [
            'analyze', 'generate', 'create', 'design', 'optimize', 'recommend'
        ])
        
        requires_orchestration = any(keyword in task_description.lower() for keyword in [
            'multiple', 'sequence', 'workflow', 'complex', 'coordinate'
        ])
        
        # Check for similar tasks in learning database
        similar_tasks = []
        if self.learning_repo:
            try:
                similar_tasks = await self.learning_repo.find_similar_tasks(
                    task_description, limit=3, threshold=0.7
                )
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve similar tasks: {e}")
        
        plan = {
            "use_orchestrator": requires_ai or requires_orchestration or agent_type,
            "recommended_agent": agent_type or self._recommend_agent(task_description),
            "complexity_score": self._calculate_complexity(task_description),
            "similar_tasks": similar_tasks,
            "requires_ai": requires_ai,
            "estimated_duration": self._estimate_duration(task_description, similar_tasks)
        }
        
        logger.info(f"📋 Execution plan: {plan}")
        return plan
    
    async def _execute_with_orchestrator(
        self,
        task_id: str,
        task_description: str,
        agent_type: Optional[str],
        context: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> TaskResult:
        """Execute task using DDD orchestrator with database integration"""
        
        # Store task in database
        if self.task_repo:
            await self.task_repo.create_task(
                task_id=task_id,
                description=task_description,
                agent_type=plan["recommended_agent"],
                status="in_progress",
                metadata={
                    "plan": plan,
                    "context": context,
                    "complexity_score": plan["complexity_score"]
                }
            )
        
        start_time = datetime.now()
        
        try:
            # Select appropriate orchestrator component
            orchestrator = self.orchestration_service.get_orchestrator()
            
            # Execute task
            result = await orchestrator.execute_task(
                task_description=task_description,
                agent_type=plan["recommended_agent"],
                context=context
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update task status
            if self.task_repo:
                await self.task_repo.update_task_status(
                    task_id=task_id,
                    status="completed" if result.success else "failed",
                    result_data={
                        "success": result.success,
                        "output": result.output,
                        "error": result.error_message,
                        "duration": execution_time
                    }
                )
            
            return TaskResult(
                success=result.success,
                output=result.output,
                error_message=result.error_message,
                duration=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update task status as failed
            if self.task_repo:
                await self.task_repo.update_task_status(
                    task_id=task_id,
                    status="failed",
                    result_data={
                        "success": False,
                        "error": str(e),
                        "duration": execution_time
                    }
                )
            
            raise e
    
    async def _execute_with_legacy_agent(
        self,
        task_id: str,
        task_description: str,
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute task using legacy agent for compatibility"""
        
        start_time = datetime.now()
        
        try:
            # Use hybrid bridge for legacy operations
            result = await self.hybrid_bridge.execute_legacy_task(
                task_description, context
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                success=result.get("success", False),
                output=result.get("output", ""),
                error_message=result.get("error", ""),
                duration=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                success=False,
                error_message=f"Legacy execution failed: {str(e)}",
                duration=execution_time
            )
    
    async def _record_task_analytics(
        self,
        task_id: str,
        agent_type: Optional[str],
        execution_time: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Record task analytics for system optimization"""
        
        if not self.analytics_repo:
            return
        
        try:
            await self.analytics_repo.record_task_analytics(
                task_id=task_id,
                agent_type=agent_type or "unknown",
                execution_time=execution_time,
                success=success,
                error_message=error_message,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "system_load": await self._get_system_metrics()
                }
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not record analytics: {e}")
    
    async def _record_learning_event(
        self,
        task_id: str,
        task_description: str,
        agent_type: Optional[str],
        result: TaskResult,
        context: Dict[str, Any]
    ):
        """Record successful task execution for cross-agent learning"""
        
        if not self.learning_repo:
            return
        
        try:
            await self.learning_repo.record_learning_event(
                agent_id=agent_type or "system",
                event_type="task_completion",
                input_data={
                    "task_description": task_description,
                    "context": context
                },
                output_data={
                    "success": result.success,
                    "output": result.output,
                    "duration": result.duration
                },
                feedback_score=1.0 if result.success else 0.0,
                metadata={
                    "task_id": task_id,
                    "agent_type": agent_type,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Store in shared memory for other agents
            if self.memory_repo:
                await self.memory_repo.store_memory(
                    bank_name="successful_patterns",
                    entry_key=f"pattern_{task_id}",
                    entry_type="success_pattern",
                    content={
                        "task_description": task_description,
                        "agent_type": agent_type,
                        "success_factors": {
                            "execution_time": result.duration,
                            "context_keys": list(context.keys()),
                            "output_length": len(str(result.output))
                        }
                    }
                )
                
        except Exception as e:
            logger.warning(f"⚠️ Could not record learning event: {e}")
    
    def _recommend_agent(self, task_description: str) -> str:
        """Recommend best agent type based on task description"""
        
        task_lower = task_description.lower()
        
        if any(keyword in task_lower for keyword in ['file', 'directory', 'path', 'folder']):
            return "file_agent"
        elif any(keyword in task_lower for keyword in ['network', 'http', 'api', 'request']):
            return "network_agent"
        elif any(keyword in task_lower for keyword in ['analyze', 'data', 'report', 'statistics']):
            return "analysis_agent"
        elif any(keyword in task_lower for keyword in ['generate', 'create', 'write', 'compose']):
            return "generation_agent"
        else:
            return "general_agent"
    
    def _calculate_complexity(self, task_description: str) -> float:
        """Calculate task complexity score (0.0 - 1.0)"""
        
        complexity_indicators = [
            ('multiple', 0.2), ('complex', 0.3), ('analyze', 0.2),
            ('generate', 0.2), ('optimize', 0.3), ('coordinate', 0.3),
            ('workflow', 0.2), ('sequence', 0.2), ('advanced', 0.3)
        ]
        
        score = 0.1  # Base complexity
        task_lower = task_description.lower()
        
        for indicator, weight in complexity_indicators:
            if indicator in task_lower:
                score += weight
        
        # Length-based complexity
        if len(task_description) > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_duration(self, task_description: str, similar_tasks: List[Dict]) -> float:
        """Estimate task duration based on historical data"""
        
        if similar_tasks:
            # Use average duration from similar tasks
            durations = [task.get('avg_duration', 30.0) for task in similar_tasks]
            return sum(durations) / len(durations)
        
        # Fallback estimation based on complexity
        base_duration = 10.0  # seconds
        complexity = self._calculate_complexity(task_description)
        
        return base_duration * (1 + complexity * 5)
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except ImportError:
            return {"status": "metrics_unavailable"}
    
    async def get_cross_agent_insights(self, task_description: str) -> Dict[str, Any]:
        """Get insights from other agents for similar tasks"""
        
        if not self.learning_repo:
            return {"insights": [], "recommendations": []}
        
        try:
            # Find similar successful tasks
            similar_tasks = await self.learning_repo.find_similar_tasks(
                task_description, limit=5, threshold=0.6
            )
            
            # Get performance patterns
            patterns = await self.analytics_repo.get_performance_patterns(
                task_type=self._recommend_agent(task_description),
                time_window_hours=24
            ) if self.analytics_repo else []
            
            insights = []
            recommendations = []
            
            # Analyze similar tasks
            for task in similar_tasks:
                if task.get('success_rate', 0) > 0.8:
                    insights.append({
                        "type": "success_pattern",
                        "description": task.get('task_description', ''),
                        "success_rate": task.get('success_rate', 0),
                        "avg_duration": task.get('avg_duration', 0),
                        "agent_type": task.get('agent_type', 'unknown')
                    })
            
            # Generate recommendations
            if patterns:
                best_performing_agent = max(patterns, key=lambda x: x.get('success_rate', 0))
                recommendations.append({
                    "type": "agent_recommendation",
                    "agent_type": best_performing_agent.get('agent_type'),
                    "reason": f"Best success rate: {best_performing_agent.get('success_rate', 0):.2%}"
                })
            
            if similar_tasks and len(similar_tasks) > 2:
                avg_duration = sum(t.get('avg_duration', 0) for t in similar_tasks) / len(similar_tasks)
                recommendations.append({
                    "type": "timing_recommendation",
                    "estimated_duration": avg_duration,
                    "confidence": min(len(similar_tasks) / 5.0, 1.0)
                })
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "similar_tasks_count": len(similar_tasks)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Could not get cross-agent insights: {e}")
            return {"insights": [], "recommendations": [], "error": str(e)}
    
    async def share_learning_with_agents(self, learning_data: Dict[str, Any]) -> bool:
        """Share learning data with other agents via shared memory"""
        
        if not self.memory_repo:
            return False
        
        try:
            # Store in shared learning bank
            await self.memory_repo.store_memory(
                bank_name="cross_agent_learning",
                entry_key=f"shared_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                entry_type="shared_learning",
                content=learning_data
            )
            
            # Also store in global patterns for quick access
            if learning_data.get('success', False):
                await self.memory_repo.store_memory(
                    bank_name="global_patterns",
                    entry_key=f"pattern_{learning_data.get('task_id', 'unknown')}",
                    entry_type="success_pattern",
                    content={
                        "task_type": learning_data.get('task_type'),
                        "success_factors": learning_data.get('success_factors', {}),
                        "performance_metrics": learning_data.get('performance_metrics', {}),
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            logger.info("🤝 Learning data shared with agents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to share learning data: {e}")
            return False
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics and performance metrics"""
        
        if not self.analytics_repo:
            return {"status": "analytics_unavailable"}
        
        try:
            # Get performance summary
            performance = await self.analytics_repo.get_performance_summary(
                time_window_hours=24
            )
            
            # Get agent performance comparison
            agent_performance = await self.analytics_repo.get_agent_performance_comparison(
                time_window_hours=24
            )
            
            # Get optimization recommendations
            optimizations = await self.analytics_repo.get_optimization_recommendations()
            
            # Get system health metrics
            health = await self._get_system_health()
            
            return {
                "performance_summary": performance,
                "agent_performance": agent_performance,
                "optimization_recommendations": optimizations,
                "system_health": health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Could not get system analytics: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health indicators"""
        
        health = {
            "database_status": "unknown",
            "memory_usage": "unknown",
            "agent_registry": "unknown",
            "overall_status": "unknown"
        }
        
        try:
            # Check database connectivity
            if self.db_manager:
                db_healthy = await self.db_manager.health_check()
                health["database_status"] = "healthy" if db_healthy else "unhealthy"
            
            # Check memory usage
            if self.memory_repo:
                try:
                    memory_stats = await self.memory_repo.get_memory_stats()
                    health["memory_usage"] = {
                        "total_banks": memory_stats.get("total_banks", 0),
                        "total_entries": memory_stats.get("total_entries", 0),
                        "oldest_entry": memory_stats.get("oldest_entry")
                    }
                except:
                    health["memory_usage"] = "unavailable"
            
            # Check agent registry
            if self.agent_registry:
                registered_agents = len(self.agent_registry.get_all_agents())
                health["agent_registry"] = {
                    "registered_agents": registered_agents,
                    "status": "healthy" if registered_agents > 0 else "no_agents"
                }
            
            # Calculate overall status
            statuses = [
                health["database_status"],
                "healthy" if health["memory_usage"] != "unknown" else "unhealthy",
                health["agent_registry"].get("status", "unknown") if isinstance(health["agent_registry"], dict) else "unknown"
            ]
            
            healthy_count = sum(1 for status in statuses if status == "healthy")
            if healthy_count == len(statuses):
                health["overall_status"] = "healthy"
            elif healthy_count > 0:
                health["overall_status"] = "degraded"
            else:
                health["overall_status"] = "unhealthy"
                
        except Exception as e:
            health["overall_status"] = "error"
            health["error"] = str(e)
        
        return health
