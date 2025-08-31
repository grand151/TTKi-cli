"""
Learning Repository - Cross-Agent Learning & Knowledge Management
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.value_objects import AgentId, TaskId
from .database_manager import get_database_manager

class LearningRepository:
    """Repository for cross-agent learning operations"""
    
    async def record_learning_event(
        self,
        event_type: str,
        source_agent_id: AgentId,
        target_agent_id: Optional[AgentId],
        task_id: Optional[TaskId],
        context: Dict[str, Any],
        learning_data: Dict[str, Any],
        confidence_score: float = 0.0
    ) -> str:
        """Record a learning event"""
        db = await get_database_manager()
        
        event_id = str(uuid.uuid4())
        
        try:
            await db.execute_command("""
                INSERT INTO learning_events (
                    id, event_type, source_agent_id, target_agent_id, task_id,
                    context, learning_data, confidence_score
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                event_id,
                event_type,
                str(source_agent_id),
                str(target_agent_id) if target_agent_id else None,
                str(task_id) if task_id else None,
                context,
                learning_data,
                confidence_score
            )
            
            return event_id
            
        except Exception as e:
            print(f"❌ Learning event recording failed: {e}")
            return ""
    
    async def add_knowledge(
        self,
        knowledge_type: str,
        title: str,
        content: str,
        embedding: Optional[List[float]],
        source_agent_id: AgentId,
        tags: List[str] = None,
        confidence_score: float = 0.0
    ) -> str:
        """Add knowledge to knowledge base"""
        db = await get_database_manager()
        
        knowledge_id = str(uuid.uuid4())
        tags = tags or []
        
        try:
            # Convert embedding to proper vector format
            embedding_str = None
            if embedding:
                embedding_str = f"[{','.join(map(str, embedding))}]"
            
            await db.execute_command("""
                INSERT INTO knowledge_base (
                    id, knowledge_type, title, content, embedding,
                    source_agent_id, tags, confidence_score
                ) VALUES ($1, $2, $3, $4, $5::vector, $6, $7, $8)
            """,
                knowledge_id,
                knowledge_type,
                title,
                content,
                embedding_str,
                str(source_agent_id),
                tags,
                confidence_score
            )
            
            return knowledge_id
            
        except Exception as e:
            print(f"❌ Knowledge addition failed: {e}")
            return ""
    
    async def search_similar_knowledge(
        self,
        query_embedding: List[float],
        knowledge_type: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Search for similar knowledge using vector similarity"""
        db = await get_database_manager()
        
        try:
            # Build query with optional type filter
            where_clause = ""
            params = [f"[{','.join(map(str, query_embedding))}]", similarity_threshold, limit]
            
            if knowledge_type:
                where_clause = "AND knowledge_type = $4"
                params.append(knowledge_type)
            
            results = await db.execute_query(f"""
                SELECT 
                    id, knowledge_type, title, content, tags, confidence_score,
                    usage_count, effectiveness_score, created_at,
                    1 - (embedding <=> $1::vector) as similarity_score
                FROM knowledge_base
                WHERE 1 - (embedding <=> $1::vector) > $2
                {where_clause}
                ORDER BY similarity_score DESC
                LIMIT $3
            """, *params, readonly=True)
            
            return results
            
        except Exception as e:
            print(f"❌ Knowledge search failed: {e}")
            return []
    
    async def update_knowledge_usage(self, knowledge_id: str) -> bool:
        """Update knowledge usage statistics"""
        db = await get_database_manager()
        
        try:
            await db.execute_command("""
                UPDATE knowledge_base 
                SET usage_count = usage_count + 1, updated_at = NOW()
                WHERE id = $1
            """, knowledge_id)
            
            return True
            
        except Exception as e:
            print(f"❌ Knowledge usage update failed: {e}")
            return False
    
    async def get_agent_learning_progress(self, agent_id: AgentId) -> List[Dict[str, Any]]:
        """Get learning progress for agent"""
        db = await get_database_manager()
        
        return await db.execute_query("""
            SELECT learning_domain, skill_level, learning_events_count,
                   learning_velocity, last_improvement_date, plateau_indicator
            FROM agent_learning_progress
            WHERE agent_id = (SELECT id FROM agents WHERE agent_id = $1)
            ORDER BY skill_level DESC
        """, str(agent_id), readonly=True)
    
    async def update_learning_progress(
        self,
        agent_id: AgentId,
        learning_domain: str,
        skill_improvement: float
    ) -> bool:
        """Update agent learning progress"""
        db = await get_database_manager()
        
        try:
            await db.execute_command("""
                INSERT INTO agent_learning_progress (
                    agent_id, learning_domain, skill_level, learning_events_count,
                    last_improvement_date, learning_velocity
                ) 
                SELECT 
                    a.id, $2, $3, 1, NOW(), $3
                FROM agents a WHERE a.agent_id = $1
                ON CONFLICT (agent_id, learning_domain) DO UPDATE SET
                    skill_level = LEAST(1.0, agent_learning_progress.skill_level + $3),
                    learning_events_count = agent_learning_progress.learning_events_count + 1,
                    last_improvement_date = NOW(),
                    learning_velocity = $3,
                    updated_at = NOW()
            """,
                str(agent_id),
                learning_domain,
                skill_improvement
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Learning progress update failed: {e}")
            return False
    
    async def get_learning_recommendations(self, agent_id: AgentId) -> List[Dict[str, Any]]:
        """Get learning recommendations for agent"""
        db = await get_database_manager()
        
        return await db.execute_query("""
            SELECT DISTINCT
                kb.knowledge_type,
                kb.title,
                kb.confidence_score,
                kb.effectiveness_score
            FROM knowledge_base kb
            WHERE kb.source_agent_id != (SELECT id FROM agents WHERE agent_id = $1)
            AND kb.effectiveness_score > 0.7
            ORDER BY kb.effectiveness_score DESC, kb.confidence_score DESC
            LIMIT 10
        """, str(agent_id), readonly=True)
