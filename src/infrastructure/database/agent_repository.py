"""
Agent Repository - Database operations for Agent entities
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.entities import AgentEntity
from ...domain.value_objects import AgentId
from .database_manager import get_database_manager

class AgentRepository:
    """Repository for Agent database operations"""
    
    async def save(self, agent: AgentEntity) -> bool:
        """Save agent to database"""
        db = await get_database_manager()
        
        try:
            await db.execute_command("""
                INSERT INTO agents (
                    id, agent_id, agent_type, agent_name, capabilities, 
                    status, version, architecture_type, performance_score
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO UPDATE SET
                    agent_type = EXCLUDED.agent_type,
                    capabilities = EXCLUDED.capabilities,
                    status = EXCLUDED.status,
                    performance_score = EXCLUDED.performance_score,
                    updated_at = NOW()
            """, 
                str(agent.id.value) if hasattr(agent.id, 'value') else str(agent.id),
                str(agent.id),
                agent.agent_type,
                f"{agent.agent_type}_agent",  # agent_name
                agent.capabilities,
                agent.status,
                "1.0.0",  # version
                "hybrid",  # architecture_type
                0.85  # default performance_score
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Agent save failed: {e}")
            return False
    
    async def find_by_id(self, agent_id: AgentId) -> Optional[AgentEntity]:
        """Find agent by ID"""
        db = await get_database_manager()
        
        result = await db.execute_single(
            "SELECT * FROM agents WHERE agent_id = $1",
            str(agent_id),
            readonly=True
        )
        
        if result:
            return AgentEntity(
                id=AgentId(result['agent_id']),
                agent_type=result['agent_type'],
                capabilities=result['capabilities'] or []
            )
        
        return None
    
    async def find_by_type(self, agent_type: str) -> List[AgentEntity]:
        """Find agents by type"""
        db = await get_database_manager()
        
        results = await db.execute_query(
            "SELECT * FROM agents WHERE agent_type = $1 AND status = 'active'",
            agent_type,
            readonly=True
        )
        
        return [
            AgentEntity(
                id=AgentId(result['agent_id']),
                agent_type=result['agent_type'],
                capabilities=result['capabilities'] or []
            )
            for result in results
        ]
    
    async def get_all_active(self) -> List[AgentEntity]:
        """Get all active agents"""
        db = await get_database_manager()
        
        results = await db.execute_query(
            "SELECT * FROM agents WHERE status = 'active' ORDER BY created_at",
            readonly=True
        )
        
        return [
            AgentEntity(
                id=AgentId(result['agent_id']),
                agent_type=result['agent_type'],
                capabilities=result['capabilities'] or []
            )
            for result in results
        ]
    
    async def update_performance(self, agent_id: AgentId, score: float) -> bool:
        """Update agent performance score"""
        db = await get_database_manager()
        
        try:
            await db.execute_command(
                "UPDATE agents SET performance_score = $1, updated_at = NOW() WHERE agent_id = $2",
                score,
                str(agent_id)
            )
            return True
            
        except Exception as e:
            print(f"❌ Performance update failed: {e}")
            return False
    
    async def record_activity(self, agent_id: AgentId) -> bool:
        """Record agent activity"""
        db = await get_database_manager()
        
        try:
            await db.execute_command(
                "UPDATE agents SET last_activity = NOW() WHERE agent_id = $1",
                str(agent_id)
            )
            return True
            
        except Exception as e:
            print(f"❌ Activity update failed: {e}")
            return False
