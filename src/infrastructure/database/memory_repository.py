"""
Memory Repository - Shared Memory System for Cross-Agent Communication
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...domain.value_objects import AgentId
from .database_manager import get_database_manager

class MemoryRepository:
    """Repository for shared memory operations"""
    
    async def create_memory_bank(
        self,
        bank_name: str,
        bank_type: str = "global",
        access_level: str = "public",
        retention_policy: str = "permanent",
        max_size_mb: int = 1024
    ) -> str:
        """Create a new memory bank"""
        db = await get_database_manager()
        
        bank_id = str(uuid.uuid4())
        
        try:
            await db.execute_command("""
                INSERT INTO memory_banks (
                    id, bank_name, bank_type, access_level, 
                    retention_policy, max_size_mb
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """,
                bank_id,
                bank_name,
                bank_type,
                access_level,
                retention_policy,
                max_size_mb
            )
            
            return bank_id
            
        except Exception as e:
            print(f"❌ Memory bank creation failed: {e}")
            return ""
    
    async def store_memory(
        self,
        bank_name: str,
        entry_key: str,
        entry_type: str,
        content: Dict[str, Any],
        embedding: Optional[List[float]] = None,
        created_by_agent_id: Optional[AgentId] = None,
        expires_in_hours: Optional[int] = None
    ) -> bool:
        """Store memory entry"""
        db = await get_database_manager()
        
        try:
            # Get memory bank ID
            bank = await db.execute_single(
                "SELECT id FROM memory_banks WHERE bank_name = $1",
                bank_name,
                readonly=True
            )
            
            if not bank:
                print(f"❌ Memory bank '{bank_name}' not found")
                return False
            
            # Calculate expiration
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            
            # Convert embedding
            embedding_str = None
            if embedding:
                embedding_str = f"[{','.join(map(str, embedding))}]"
            
            await db.execute_command("""
                INSERT INTO memory_entries (
                    memory_bank_id, entry_key, entry_type, content,
                    embedding, created_by_agent_id, expires_at
                ) VALUES ($1, $2, $3, $4, $5::vector, $6, $7)
                ON CONFLICT (memory_bank_id, entry_key) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    created_at = NOW()
            """,
                bank['id'],
                entry_key,
                entry_type,
                content,
                embedding_str,
                str(created_by_agent_id) if created_by_agent_id else None,
                expires_at
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Memory storage failed: {e}")
            return False
    
    async def retrieve_memory(
        self,
        bank_name: str,
        entry_key: str,
        accessing_agent_id: Optional[AgentId] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve memory entry"""
        db = await get_database_manager()
        
        try:
            result = await db.execute_single("""
                SELECT me.*, mb.bank_name
                FROM memory_entries me
                JOIN memory_banks mb ON me.memory_bank_id = mb.id
                WHERE mb.bank_name = $1 AND me.entry_key = $2
                AND (me.expires_at IS NULL OR me.expires_at > NOW())
            """, bank_name, entry_key, readonly=True)
            
            if result:
                # Log access
                if accessing_agent_id:
                    await self._log_memory_access(
                        result['id'], 
                        accessing_agent_id, 
                        "read"
                    )
                
                return {
                    "entry_key": result['entry_key'],
                    "entry_type": result['entry_type'],
                    "content": result['content'],
                    "relevance_score": result['relevance_score'],
                    "access_count": result['access_count'],
                    "created_at": result['created_at']
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Memory retrieval failed: {e}")
            return None
    
    async def search_memories(
        self,
        bank_name: str,
        query_embedding: List[float],
        entry_type: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Search memories using vector similarity"""
        db = await get_database_manager()
        
        try:
            where_clause = ""
            params = [bank_name, f"[{','.join(map(str, query_embedding))}]", similarity_threshold, limit]
            
            if entry_type:
                where_clause = "AND me.entry_type = $5"
                params.append(entry_type)
            
            results = await db.execute_query(f"""
                SELECT 
                    me.entry_key, me.entry_type, me.content, me.relevance_score,
                    me.access_count, me.created_at,
                    1 - (me.embedding <=> $2::vector) as similarity_score
                FROM memory_entries me
                JOIN memory_banks mb ON me.memory_bank_id = mb.id
                WHERE mb.bank_name = $1
                AND me.embedding IS NOT NULL
                AND 1 - (me.embedding <=> $2::vector) > $3
                AND (me.expires_at IS NULL OR me.expires_at > NOW())
                {where_clause}
                ORDER BY similarity_score DESC
                LIMIT $4
            """, *params, readonly=True)
            
            return results
            
        except Exception as e:
            print(f"❌ Memory search failed: {e}")
            return []
    
    async def get_memory_bank_stats(self, bank_name: str) -> Dict[str, Any]:
        """Get memory bank statistics"""
        db = await get_database_manager()
        
        result = await db.execute_single("""
            SELECT 
                mb.bank_type, mb.access_level, mb.max_size_mb, mb.current_size_mb,
                COUNT(me.id) as entry_count,
                COUNT(CASE WHEN me.expires_at > NOW() OR me.expires_at IS NULL THEN 1 END) as active_entries,
                AVG(me.relevance_score) as avg_relevance,
                SUM(me.access_count) as total_accesses
            FROM memory_banks mb
            LEFT JOIN memory_entries me ON mb.id = me.memory_bank_id
            WHERE mb.bank_name = $1
            GROUP BY mb.id, mb.bank_type, mb.access_level, mb.max_size_mb, mb.current_size_mb
        """, bank_name, readonly=True)
        
        return dict(result) if result else {}
    
    async def cleanup_expired_memories(self) -> int:
        """Clean up expired memory entries"""
        db = await get_database_manager()
        
        try:
            result = await db.execute_command(
                "DELETE FROM memory_entries WHERE expires_at < NOW()"
            )
            
            # Extract count from result string (e.g., "DELETE 5")
            count = int(result.split()[-1]) if result.split()[-1].isdigit() else 0
            return count
            
        except Exception as e:
            print(f"❌ Memory cleanup failed: {e}")
            return 0
    
    async def _log_memory_access(
        self,
        memory_entry_id: str,
        accessing_agent_id: AgentId,
        access_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log memory access for analytics"""
        db = await get_database_manager()
        
        try:
            await db.execute_command("""
                INSERT INTO memory_access_log (
                    memory_entry_id, accessing_agent_id, access_type, context
                ) VALUES ($1, $2, $3, $4)
            """,
                memory_entry_id,
                str(accessing_agent_id),
                access_type,
                context or {}
            )
            
            # Update access count
            await db.execute_command(
                "UPDATE memory_entries SET access_count = access_count + 1, last_accessed = NOW() WHERE id = $1",
                memory_entry_id
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Memory access logging failed: {e}")
            return False
