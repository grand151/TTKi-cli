"""
Analytics Repository - Advanced Analytics & Self-Improvement System
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...domain.value_objects import AgentId
from .database_manager import get_database_manager

class AnalyticsRepository:
    """Repository for analytics and self-improvement operations"""
    
    async def record_system_metric(
        self,
        metric_category: str,
        metric_name: str,
        metric_value: float,
        measurement_unit: str = "",
        time_window: str = "real_time",
        aggregation_type: str = "value",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record system performance metric"""
        db = await get_database_manager()
        
        try:
            await db.execute_command("""
                INSERT INTO system_analytics (
                    metric_category, metric_name, metric_value, measurement_unit,
                    time_window, aggregation_type, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                metric_category,
                metric_name,
                metric_value,
                measurement_unit,
                time_window,
                aggregation_type,
                metadata or {}
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Metric recording failed: {e}")
            return False
    
    async def record_agent_metric(
        self,
        agent_id: AgentId,
        metric_type: str,
        metric_value: float,
        measurement_unit: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record agent performance metric"""
        db = await get_database_manager()
        
        try:
            await db.execute_command("""
                INSERT INTO agent_metrics (
                    agent_id, metric_type, metric_value, measurement_unit, context
                ) 
                SELECT a.id, $2, $3, $4, $5
                FROM agents a WHERE a.agent_id = $1
            """,
                str(agent_id),
                metric_type,
                metric_value,
                measurement_unit,
                context or {}
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Agent metric recording failed: {e}")
            return False
    
    async def record_resource_usage(
        self,
        resource_type: str,
        component_id: str,
        component_type: str,
        usage_value: float,
        max_capacity: Optional[float] = None,
        measurement_unit: str = ""
    ) -> bool:
        """Record resource usage metrics"""
        db = await get_database_manager()
        
        try:
            usage_percentage = None
            if max_capacity and max_capacity > 0:
                usage_percentage = (usage_value / max_capacity) * 100
            
            await db.execute_command("""
                INSERT INTO resource_usage (
                    resource_type, component_id, component_type, usage_value,
                    max_capacity, usage_percentage, measurement_unit
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                resource_type,
                component_id,
                component_type,
                usage_value,
                max_capacity,
                usage_percentage,
                measurement_unit
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Resource usage recording failed: {e}")
            return False
    
    async def get_system_performance_summary(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get system performance summary"""
        db = await get_database_manager()
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        result = await db.execute_single("""
            SELECT 
                COUNT(*) as total_metrics,
                COUNT(DISTINCT metric_category) as categories_count,
                AVG(CASE WHEN metric_category = 'performance' THEN metric_value END) as avg_performance,
                MAX(CASE WHEN metric_category = 'error_rates' THEN metric_value END) as max_error_rate,
                MIN(recorded_at) as oldest_metric,
                MAX(recorded_at) as latest_metric
            FROM system_analytics
            WHERE recorded_at > $1
        """, cutoff_time, readonly=True)
        
        return dict(result) if result else {}
    
    async def get_agent_performance_analysis(
        self,
        agent_id: AgentId,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """Get detailed agent performance analysis"""
        db = await get_database_manager()
        
        cutoff_time = datetime.now() - timedelta(days=days_back)
        
        # Get overall metrics
        overall = await db.execute_single("""
            SELECT 
                COUNT(*) as total_measurements,
                AVG(CASE WHEN metric_type = 'execution_time' THEN metric_value END) as avg_execution_time,
                AVG(CASE WHEN metric_type = 'success_rate' THEN metric_value END) as avg_success_rate,
                MAX(CASE WHEN metric_type = 'resource_usage' THEN metric_value END) as max_resource_usage
            FROM agent_metrics am
            JOIN agents a ON am.agent_id = a.id
            WHERE a.agent_id = $1 AND am.measured_at > $2
        """, str(agent_id), cutoff_time, readonly=True)
        
        # Get trend data
        trends = await db.execute_query("""
            SELECT 
                DATE(measured_at) as measurement_date,
                metric_type,
                AVG(metric_value) as avg_value,
                COUNT(*) as measurement_count
            FROM agent_metrics am
            JOIN agents a ON am.agent_id = a.id
            WHERE a.agent_id = $1 AND am.measured_at > $2
            GROUP BY DATE(measured_at), metric_type
            ORDER BY measurement_date DESC
        """, str(agent_id), cutoff_time, readonly=True)
        
        return {
            "overall": dict(overall) if overall else {},
            "trends": trends,
            "analysis_period": f"{days_back} days"
        }
    
    async def create_optimization_recommendation(
        self,
        recommendation_type: str,
        target_component: str,
        recommendation_text: str,
        technical_details: Dict[str, Any],
        priority_level: int = 3,
        estimated_impact: float = 0.5,
        implementation_effort: str = "medium"
    ) -> str:
        """Create optimization recommendation"""
        db = await get_database_manager()
        
        rec_id = str(uuid.uuid4())
        
        try:
            await db.execute_command("""
                INSERT INTO optimization_recommendations (
                    id, recommendation_type, target_component, recommendation_text,
                    technical_details, priority_level, estimated_impact, implementation_effort
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                rec_id,
                recommendation_type,
                target_component,
                recommendation_text,
                technical_details,
                priority_level,
                estimated_impact,
                implementation_effort
            )
            
            return rec_id
            
        except Exception as e:
            print(f"❌ Recommendation creation failed: {e}")
            return ""
    
    async def record_feedback_event(
        self,
        feedback_type: str,
        source_type: str,
        source_id: str,
        target_component: str,
        feedback_content: Dict[str, Any],
        sentiment_score: Optional[float] = None
    ) -> str:
        """Record feedback event"""
        db = await get_database_manager()
        
        event_id = str(uuid.uuid4())
        
        try:
            await db.execute_command("""
                INSERT INTO feedback_events (
                    id, feedback_type, source_type, source_id, target_component,
                    feedback_content, sentiment_score
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                event_id,
                feedback_type,
                source_type,
                source_id,
                target_component,
                feedback_content,
                sentiment_score
            )
            
            return event_id
            
        except Exception as e:
            print(f"❌ Feedback recording failed: {e}")
            return ""
    
    async def create_improvement_action(
        self,
        action_type: str,
        target_component: str,
        description: str,
        implementation_details: Dict[str, Any],
        triggered_by_feedback_id: Optional[str] = None,
        expected_improvement: float = 0.1,
        risk_level: str = "low"
    ) -> str:
        """Create self-improvement action"""
        db = await get_database_manager()
        
        action_id = str(uuid.uuid4())
        
        try:
            await db.execute_command("""
                INSERT INTO improvement_actions (
                    id, action_type, target_component, description,
                    implementation_details, triggered_by_feedback_id,
                    expected_improvement, risk_level
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                action_id,
                action_type,
                target_component,
                description,
                implementation_details,
                triggered_by_feedback_id,
                expected_improvement,
                risk_level
            )
            
            return action_id
            
        except Exception as e:
            print(f"❌ Improvement action creation failed: {e}")
            return ""
    
    async def get_pending_recommendations(
        self,
        component_type: Optional[str] = None,
        priority_threshold: int = 3
    ) -> List[Dict[str, Any]]:
        """Get pending optimization recommendations"""
        db = await get_database_manager()
        
        where_clause = "WHERE status = 'pending' AND priority_level <= $1"
        params = [priority_threshold]
        
        if component_type:
            where_clause += " AND target_component LIKE $2"
            params.append(f"%{component_type}%")
        
        return await db.execute_query(f"""
            SELECT id, recommendation_type, target_component, recommendation_text,
                   priority_level, estimated_impact, implementation_effort, created_at
            FROM optimization_recommendations
            {where_clause}
            ORDER BY priority_level ASC, estimated_impact DESC
        """, *params, readonly=True)
    
    async def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        db = await get_database_manager()
        
        # Get recent system metrics
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        health_data = await db.execute_single("""
            SELECT 
                COUNT(DISTINCT CASE WHEN sa.metric_category = 'performance' THEN sa.id END) as performance_metrics,
                AVG(CASE WHEN sa.metric_category = 'performance' THEN sa.metric_value END) as avg_performance,
                COUNT(DISTINCT CASE WHEN sa.metric_category = 'error_rates' THEN sa.id END) as error_metrics,
                MAX(CASE WHEN sa.metric_category = 'error_rates' THEN sa.metric_value END) as max_error_rate,
                COUNT(DISTINCT a.id) as active_agents,
                AVG(a.performance_score) as avg_agent_performance
            FROM system_analytics sa
            CROSS JOIN agents a
            WHERE sa.recorded_at > $1 AND a.status = 'active'
        """, cutoff_time, readonly=True)
        
        return dict(health_data) if health_data else {}
