"""
System Dashboard Service - Real-time monitoring and analytics for TTKi AI System
Provides comprehensive system health, performance metrics, and cross-agent insights.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# Database imports
from src.infrastructure.database.database_manager import DatabaseManager
from src.infrastructure.database.repositories.agent_repository import AgentRepository
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.infrastructure.database.repositories.learning_repository import LearningRepository
from src.infrastructure.database.repositories.memory_repository import MemoryRepository
from src.infrastructure.database.repositories.analytics_repository import AnalyticsRepository

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    average_execution_time: float
    active_agents: int
    system_uptime: float
    memory_usage: Dict[str, Any]
    cpu_usage: float
    database_status: str

@dataclass
class AgentPerformanceMetrics:
    """Agent-specific performance metrics"""
    agent_id: str
    agent_type: str
    total_tasks: int
    success_rate: float
    average_execution_time: float
    last_activity: datetime
    specialization_score: float

class SystemDashboardService:
    """
    Comprehensive system monitoring and analytics service
    """
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        agent_repo: Optional[AgentRepository] = None,
        task_repo: Optional[TaskRepository] = None,
        learning_repo: Optional[LearningRepository] = None,
        memory_repo: Optional[MemoryRepository] = None,
        analytics_repo: Optional[AnalyticsRepository] = None
    ):
        self.db_manager = db_manager
        self.agent_repo = agent_repo
        self.task_repo = task_repo
        self.learning_repo = learning_repo
        self.memory_repo = memory_repo
        self.analytics_repo = analytics_repo
        
        self.start_time = datetime.now()
        
        logger.info("🔧 System Dashboard Service initialized")
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive real-time system dashboard
        """
        logger.info("📊 Generating real-time dashboard...")
        
        try:
            # Get all dashboard components in parallel
            system_health, performance_metrics, agent_metrics, learning_insights, memory_status = await asyncio.gather(
                self._get_system_health(),
                self._get_performance_metrics(),
                self._get_agent_performance_metrics(),
                self._get_learning_insights(),
                self._get_memory_status(),
                return_exceptions=True
            )
            
            dashboard = {
                "timestamp": datetime.now().isoformat(),
                "system_health": system_health if not isinstance(system_health, Exception) else {"status": "error", "error": str(system_health)},
                "performance_metrics": performance_metrics if not isinstance(performance_metrics, Exception) else {"status": "error"},
                "agent_metrics": agent_metrics if not isinstance(agent_metrics, Exception) else [],
                "learning_insights": learning_insights if not isinstance(learning_insights, Exception) else {"status": "error"},
                "memory_status": memory_status if not isinstance(memory_status, Exception) else {"status": "error"},
                "uptime": self._get_uptime(),
                "recommendations": await self._generate_recommendations()
            }
            
            logger.info("✅ Real-time dashboard generated successfully")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Dashboard generation failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "uptime": self._get_uptime()
            }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        
        health = {
            "overall_status": "unknown",
            "database": {"status": "unknown"},
            "agents": {"status": "unknown", "count": 0},
            "tasks": {"status": "unknown"},
            "memory": {"status": "unknown"},
            "learning": {"status": "unknown"}
        }
        
        try:
            # Database health
            if self.db_manager:
                db_healthy = await self.db_manager.health_check()
                health["database"] = {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "last_check": datetime.now().isoformat()
                }
            
            # Agent registry health
            if self.agent_repo:
                try:
                    agents = await self.agent_repo.get_all_agents()
                    active_agents = len([a for a in agents if a.get('status') == 'active'])
                    health["agents"] = {
                        "status": "healthy" if active_agents > 0 else "no_active_agents",
                        "count": active_agents,
                        "total": len(agents)
                    }
                except Exception as e:
                    health["agents"] = {"status": "error", "error": str(e)}
            
            # Task execution health
            if self.task_repo:
                try:
                    recent_tasks = await self.task_repo.get_recent_tasks(limit=10)
                    if recent_tasks:
                        success_rate = len([t for t in recent_tasks if t.get('status') == 'completed']) / len(recent_tasks)
                        health["tasks"] = {
                            "status": "healthy" if success_rate > 0.7 else "degraded" if success_rate > 0.3 else "unhealthy",
                            "recent_success_rate": success_rate,
                            "recent_count": len(recent_tasks)
                        }
                    else:
                        health["tasks"] = {"status": "no_recent_activity"}
                except Exception as e:
                    health["tasks"] = {"status": "error", "error": str(e)}
            
            # Memory system health
            if self.memory_repo:
                try:
                    memory_stats = await self.memory_repo.get_memory_stats()
                    health["memory"] = {
                        "status": "healthy",
                        "banks": memory_stats.get("total_banks", 0),
                        "entries": memory_stats.get("total_entries", 0)
                    }
                except Exception as e:
                    health["memory"] = {"status": "error", "error": str(e)}
            
            # Learning system health
            if self.learning_repo:
                try:
                    learning_stats = await self.learning_repo.get_learning_stats()
                    health["learning"] = {
                        "status": "healthy",
                        "total_events": learning_stats.get("total_events", 0),
                        "recent_events": learning_stats.get("recent_events", 0)
                    }
                except Exception as e:
                    health["learning"] = {"status": "error", "error": str(e)}
            
            # Calculate overall status
            component_statuses = [
                health["database"]["status"],
                health["agents"]["status"],
                health["tasks"]["status"],
                health["memory"]["status"],
                health["learning"]["status"]
            ]
            
            healthy_count = sum(1 for status in component_statuses if status == "healthy")
            total_count = len(component_statuses)
            
            if healthy_count == total_count:
                health["overall_status"] = "healthy"
            elif healthy_count >= total_count * 0.6:
                health["overall_status"] = "degraded"
            else:
                health["overall_status"] = "unhealthy"
                
        except Exception as e:
            health["overall_status"] = "error"
            health["error"] = str(e)
        
        return health
    
    async def _get_performance_metrics(self) -> SystemMetrics:
        """Get system performance metrics"""
        
        try:
            # Get task statistics
            if self.analytics_repo:
                task_stats = await self.analytics_repo.get_performance_summary(time_window_hours=24)
            else:
                task_stats = {
                    "total_tasks": 0,
                    "successful_tasks": 0,
                    "failed_tasks": 0,
                    "average_execution_time": 0.0
                }
            
            # Get agent count
            active_agents = 0
            if self.agent_repo:
                agents = await self.agent_repo.get_all_agents()
                active_agents = len([a for a in agents if a.get('status') == 'active'])
            
            # Get system metrics
            system_metrics = await self._get_system_resource_metrics()
            
            # Get memory usage
            memory_usage = {}
            if self.memory_repo:
                memory_usage = await self.memory_repo.get_memory_usage_stats()
            
            return SystemMetrics(
                total_tasks=task_stats.get("total_tasks", 0),
                successful_tasks=task_stats.get("successful_tasks", 0),
                failed_tasks=task_stats.get("failed_tasks", 0),
                average_execution_time=task_stats.get("average_execution_time", 0.0),
                active_agents=active_agents,
                system_uptime=self._get_uptime(),
                memory_usage=memory_usage,
                cpu_usage=system_metrics.get("cpu_percent", 0),
                database_status="healthy" if self.db_manager and await self.db_manager.health_check() else "unhealthy"
            )
            
        except Exception as e:
            logger.error(f"❌ Performance metrics error: {e}")
            return SystemMetrics(
                total_tasks=0, successful_tasks=0, failed_tasks=0,
                average_execution_time=0.0, active_agents=0,
                system_uptime=self._get_uptime(), memory_usage={},
                cpu_usage=0, database_status="unknown"
            )
    
    async def _get_agent_performance_metrics(self) -> List[AgentPerformanceMetrics]:
        """Get performance metrics for each agent"""
        
        agent_metrics = []
        
        try:
            if not self.analytics_repo:
                return agent_metrics
            
            # Get agent performance data
            agent_performance = await self.analytics_repo.get_agent_performance_comparison(time_window_hours=24)
            
            for agent_data in agent_performance:
                try:
                    metrics = AgentPerformanceMetrics(
                        agent_id=agent_data.get("agent_id", "unknown"),
                        agent_type=agent_data.get("agent_type", "unknown"),
                        total_tasks=agent_data.get("total_tasks", 0),
                        success_rate=agent_data.get("success_rate", 0.0),
                        average_execution_time=agent_data.get("average_execution_time", 0.0),
                        last_activity=datetime.fromisoformat(agent_data.get("last_activity", datetime.now().isoformat())),
                        specialization_score=agent_data.get("specialization_score", 0.0)
                    )
                    agent_metrics.append(metrics)
                except Exception as e:
                    logger.warning(f"⚠️ Could not process agent data: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Agent metrics error: {e}")
        
        return agent_metrics
    
    async def _get_learning_insights(self) -> Dict[str, Any]:
        """Get cross-agent learning insights"""
        
        insights = {
            "total_learning_events": 0,
            "recent_improvements": [],
            "knowledge_sharing": {"active": False, "shared_patterns": 0},
            "adaptation_rate": 0.0,
            "top_learning_agents": []
        }
        
        try:
            if not self.learning_repo:
                return insights
            
            # Get learning statistics
            learning_stats = await self.learning_repo.get_learning_stats()
            insights["total_learning_events"] = learning_stats.get("total_events", 0)
            
            # Get recent improvements
            recent_events = await self.learning_repo.get_recent_learning_events(limit=5)
            insights["recent_improvements"] = [
                {
                    "agent_id": event.get("agent_id"),
                    "event_type": event.get("event_type"),
                    "improvement": event.get("feedback_score", 0),
                    "timestamp": event.get("created_at")
                }
                for event in recent_events if event.get("feedback_score", 0) > 0.8
            ]
            
            # Get knowledge sharing stats
            if self.memory_repo:
                shared_patterns = await self.memory_repo.get_entries_count(bank_name="successful_patterns")
                insights["knowledge_sharing"] = {
                    "active": shared_patterns > 0,
                    "shared_patterns": shared_patterns
                }
            
            # Calculate adaptation rate (learning events per hour)
            if learning_stats.get("recent_events", 0) > 0:
                insights["adaptation_rate"] = learning_stats.get("recent_events", 0) / 24.0  # per hour
            
            # Get top learning agents
            top_agents = await self.learning_repo.get_top_learning_agents(limit=3)
            insights["top_learning_agents"] = [
                {
                    "agent_id": agent.get("agent_id"),
                    "learning_score": agent.get("learning_score", 0),
                    "total_events": agent.get("total_events", 0)
                }
                for agent in top_agents
            ]
            
        except Exception as e:
            logger.error(f"❌ Learning insights error: {e}")
            insights["error"] = str(e)
        
        return insights
    
    async def _get_memory_status(self) -> Dict[str, Any]:
        """Get shared memory system status"""
        
        memory_status = {
            "total_banks": 0,
            "total_entries": 0,
            "active_banks": [],
            "memory_efficiency": 0.0,
            "oldest_entry": None,
            "newest_entry": None
        }
        
        try:
            if not self.memory_repo:
                return memory_status
            
            # Get memory statistics
            stats = await self.memory_repo.get_memory_stats()
            memory_status.update(stats)
            
            # Get active banks
            banks = await self.memory_repo.get_all_banks()
            memory_status["active_banks"] = [
                {
                    "name": bank.get("name"),
                    "entry_count": bank.get("entry_count", 0),
                    "last_updated": bank.get("last_updated")
                }
                for bank in banks
            ]
            
            # Calculate memory efficiency (ratio of successful patterns to total entries)
            successful_patterns = await self.memory_repo.get_entries_count(bank_name="successful_patterns")
            total_entries = memory_status.get("total_entries", 1)
            memory_status["memory_efficiency"] = successful_patterns / max(total_entries, 1)
            
        except Exception as e:
            logger.error(f"❌ Memory status error: {e}")
            memory_status["error"] = str(e)
        
        return memory_status
    
    async def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate system optimization recommendations"""
        
        recommendations = []
        
        try:
            if self.analytics_repo:
                optimization_recs = await self.analytics_repo.get_optimization_recommendations()
                recommendations.extend(optimization_recs)
            
            # Add system-level recommendations
            performance_metrics = await self._get_performance_metrics()
            
            # Task success rate recommendation
            if performance_metrics.total_tasks > 0:
                success_rate = performance_metrics.successful_tasks / performance_metrics.total_tasks
                if success_rate < 0.8:
                    recommendations.append({
                        "type": "performance",
                        "priority": "high" if success_rate < 0.5 else "medium",
                        "title": "Improve Task Success Rate",
                        "description": f"Current success rate is {success_rate:.2%}. Consider agent retraining or task optimization.",
                        "action": "analyze_failed_tasks"
                    })
            
            # Agent utilization recommendation
            if performance_metrics.active_agents == 0:
                recommendations.append({
                    "type": "agents",
                    "priority": "critical",
                    "title": "No Active Agents",
                    "description": "No agents are currently active. System functionality is limited.",
                    "action": "register_agents"
                })
            elif performance_metrics.active_agents < 3:
                recommendations.append({
                    "type": "agents",
                    "priority": "medium",
                    "title": "Low Agent Diversity",
                    "description": f"Only {performance_metrics.active_agents} agents active. Consider registering specialized agents.",
                    "action": "expand_agent_pool"
                })
            
            # Performance recommendation
            if performance_metrics.average_execution_time > 30.0:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "title": "High Average Execution Time",
                    "description": f"Average task time is {performance_metrics.average_execution_time:.1f}s. Consider optimization.",
                    "action": "optimize_task_execution"
                })
            
        except Exception as e:
            logger.error(f"❌ Recommendation generation error: {e}")
            recommendations.append({
                "type": "system",
                "priority": "low",
                "title": "Recommendation System Error",
                "description": f"Could not generate recommendations: {str(e)}",
                "action": "check_analytics_system"
            })
        
        return recommendations
    
    async def _get_system_resource_metrics(self) -> Dict[str, Any]:
        """Get system resource usage metrics"""
        
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_io": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                }
            }
        except ImportError:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_usage": 0,
                "status": "psutil_unavailable"
            }
        except Exception as e:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_usage": 0,
                "error": str(e)
            }
    
    def _get_uptime(self) -> float:
        """Get system uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    async def export_dashboard_data(self, format_type: str = "json") -> str:
        """Export dashboard data in specified format"""
        
        try:
            dashboard_data = await self.get_real_time_dashboard()
            
            if format_type.lower() == "json":
                return json.dumps(dashboard_data, indent=2, default=str)
            elif format_type.lower() == "csv":
                # Simple CSV export for metrics
                metrics = dashboard_data.get("performance_metrics", {})
                csv_data = "metric,value\n"
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        csv_data += f"{key},{value}\n"
                return csv_data
            else:
                return json.dumps(dashboard_data, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Dashboard export failed: {e}")
            return f"Export failed: {str(e)}"
