"""
Database Manager for TTKi Advanced AI System
===========================================

Handles database connections, initialization, and migrations.
Supports both PostgreSQL and SQLite backends.
"""

import asyncio
import aiosqlite
import asyncpg
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Centralized database management for TTKi system.
    Handles connections, schema initialization, and maintenance.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ttki_system.db')
        self.is_postgresql = self.database_url.startswith('postgresql')
        self.is_sqlite = self.database_url.startswith('sqlite')
        self._pool = None
        
    async def initialize_database(self):
        """Initialize database schema and connections"""
        try:
            if self.is_postgresql:
                await self._initialize_postgresql()
            elif self.is_sqlite:
                await self._initialize_sqlite()
            else:
                raise ValueError(f"Unsupported database URL: {self.database_url}")
                
            logger.info(f"Database initialized successfully: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL database"""
        # Parse connection string
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(self.database_url)
        
        # Create connection pool
        self._pool = await asyncpg.create_pool(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:],  # Remove leading slash
            min_size=1,
            max_size=10
        )
        
        # Create schema
        await self._create_postgresql_schema()
        
    async def _initialize_sqlite(self):
        """Initialize SQLite database"""
        db_path = self.database_url.replace('sqlite:///', '')
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create schema
        await self._create_sqlite_schema(db_path)
    
    async def _create_postgresql_schema(self):
        """Create PostgreSQL schema"""
        schema_sql = """
        -- Enable pgvector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Agents table
        CREATE TABLE IF NOT EXISTS agents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            agent_type VARCHAR(100) NOT NULL,
            status VARCHAR(50) DEFAULT 'active',
            capabilities JSONB DEFAULT '{}',
            configuration JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tasks table
        CREATE TABLE IF NOT EXISTS tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            priority INTEGER DEFAULT 1,
            input_data JSONB DEFAULT '{}',
            output_data JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP
        );
        
        -- Memory entries table
        CREATE TABLE IF NOT EXISTS memory_entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            memory_type VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            embedding vector(768),
            metadata JSONB DEFAULT '{}',
            importance_score FLOAT DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Learning events table
        CREATE TABLE IF NOT EXISTS learning_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB NOT NULL,
            embedding_vector vector(768),
            confidence FLOAT DEFAULT 0.5,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- System analytics table
        CREATE TABLE IF NOT EXISTS system_analytics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            agent_id UUID REFERENCES agents(id),
            session_id UUID,
            performance_metrics JSONB DEFAULT '{}'
        );
        
        -- Shared memory table
        CREATE TABLE IF NOT EXISTS shared_memory (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            key VARCHAR(255) UNIQUE NOT NULL,
            value JSONB NOT NULL,
            owner_agent_id UUID REFERENCES agents(id),
            access_permissions JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tool usage table
        CREATE TABLE IF NOT EXISTS tool_usage (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            tool_name VARCHAR(255) NOT NULL,
            usage_data JSONB NOT NULL,
            success BOOLEAN DEFAULT true,
            execution_time FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Error logs table
        CREATE TABLE IF NOT EXISTS error_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID REFERENCES agents(id),
            error_type VARCHAR(100) NOT NULL,
            error_message TEXT NOT NULL,
            stack_trace TEXT,
            context_data JSONB DEFAULT '{}',
            severity VARCHAR(20) DEFAULT 'error',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
        CREATE INDEX IF NOT EXISTS idx_tasks_agent_status ON tasks(agent_id, status);
        CREATE INDEX IF NOT EXISTS idx_memory_agent_type ON memory_entries(agent_id, memory_type);
        CREATE INDEX IF NOT EXISTS idx_learning_agent_type ON learning_events(agent_id, event_type);
        CREATE INDEX IF NOT EXISTS idx_analytics_type_time ON system_analytics(event_type, timestamp);
        CREATE INDEX IF NOT EXISTS idx_shared_memory_key ON shared_memory(key);
        CREATE INDEX IF NOT EXISTS idx_tool_usage_agent_tool ON tool_usage(agent_id, tool_name);
        CREATE INDEX IF NOT EXISTS idx_error_logs_agent_type ON error_logs(agent_id, error_type);
        """
        
        async with self._pool.acquire() as conn:
            await conn.execute(schema_sql)
    
    async def _create_sqlite_schema(self, db_path: str):
        """Create SQLite schema"""
        schema_sql = """
        -- Agents table
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            agent_type TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            capabilities TEXT DEFAULT '{}',
            configuration TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tasks table
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 1,
            input_data TEXT DEFAULT '{}',
            output_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        );
        
        -- Memory entries table
        CREATE TABLE IF NOT EXISTS memory_entries (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT,
            metadata TEXT DEFAULT '{}',
            importance_score REAL DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        );
        
        -- Learning events table
        CREATE TABLE IF NOT EXISTS learning_events (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT NOT NULL,
            embedding_vector TEXT,
            confidence REAL DEFAULT 0.5,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        );
        
        -- System analytics table
        CREATE TABLE IF NOT EXISTS system_analytics (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            event_data TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            agent_id TEXT,
            session_id TEXT,
            performance_metrics TEXT DEFAULT '{}'
        );
        
        -- Shared memory table
        CREATE TABLE IF NOT EXISTS shared_memory (
            id TEXT PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            owner_agent_id TEXT,
            access_permissions TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tool usage table
        CREATE TABLE IF NOT EXISTS tool_usage (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            usage_data TEXT NOT NULL,
            success BOOLEAN DEFAULT 1,
            execution_time REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        );
        
        -- Error logs table
        CREATE TABLE IF NOT EXISTS error_logs (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            error_type TEXT NOT NULL,
            error_message TEXT NOT NULL,
            stack_trace TEXT,
            context_data TEXT DEFAULT '{}',
            severity TEXT DEFAULT 'error',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
        CREATE INDEX IF NOT EXISTS idx_tasks_agent_status ON tasks(agent_id, status);
        CREATE INDEX IF NOT EXISTS idx_memory_agent_type ON memory_entries(agent_id, memory_type);
        CREATE INDEX IF NOT EXISTS idx_learning_agent_type ON learning_events(agent_id, event_type);
        CREATE INDEX IF NOT EXISTS idx_analytics_type_time ON system_analytics(event_type, timestamp);
        CREATE INDEX IF NOT EXISTS idx_shared_memory_key ON shared_memory(key);
        CREATE INDEX IF NOT EXISTS idx_tool_usage_agent_tool ON tool_usage(agent_id, tool_name);
        CREATE INDEX IF NOT EXISTS idx_error_logs_agent_type ON error_logs(agent_id, error_type);
        """
        
        async with aiosqlite.connect(db_path) as db:
            await db.executescript(schema_sql)
            await db.commit()
    
    async def get_connection(self):
        """Get database connection"""
        if self.is_postgresql:
            if not self._pool:
                await self.initialize_database()
            return self._pool.acquire()
        elif self.is_sqlite:
            db_path = self.database_url.replace('sqlite:///', '')
            return aiosqlite.connect(db_path)
        else:
            raise ValueError(f"Unsupported database type")
    
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data from analytics and logs"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            if self.is_postgresql:
                async with self._pool.acquire() as conn:
                    await conn.execute(
                        "DELETE FROM system_analytics WHERE timestamp < $1",
                        cutoff_date
                    )
                    await conn.execute(
                        "DELETE FROM error_logs WHERE timestamp < $1 AND severity NOT IN ('critical', 'fatal')",
                        cutoff_date
                    )
            elif self.is_sqlite:
                db_path = self.database_url.replace('sqlite:///', '')
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        "DELETE FROM system_analytics WHERE timestamp < ?",
                        (cutoff_date,)
                    )
                    await db.execute(
                        "DELETE FROM error_logs WHERE timestamp < ? AND severity NOT IN ('critical', 'fatal')",
                        (cutoff_date,)
                    )
                    await db.commit()
                    
            logger.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {str(e)}")
            raise
    
    async def optimize_database(self):
        """Optimize database performance"""
        try:
            if self.is_postgresql:
                async with self._pool.acquire() as conn:
                    await conn.execute("VACUUM ANALYZE;")
            elif self.is_sqlite:
                db_path = self.database_url.replace('sqlite:///', '')
                async with aiosqlite.connect(db_path) as db:
                    await db.execute("VACUUM;")
                    await db.execute("ANALYZE;")
                    await db.commit()
                    
            logger.info("Database optimization completed")
            
        except Exception as e:
            logger.error(f"Database optimization failed: {str(e)}")
            raise
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get database health status"""
        try:
            if self.is_postgresql:
                async with self._pool.acquire() as conn:
                    # Check connection
                    await conn.execute("SELECT 1")
                    
                    # Get database size
                    size_result = await conn.fetchrow(
                        "SELECT pg_size_pretty(pg_database_size(current_database())) as size"
                    )
                    
                    # Get table counts
                    tables_result = await conn.fetch("""
                        SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
                        FROM pg_stat_user_tables
                        ORDER BY tablename
                    """)
                    
                    return {
                        'status': 'healthy',
                        'database_type': 'PostgreSQL',
                        'database_size': size_result['size'],
                        'tables': [dict(row) for row in tables_result],
                        'connection_pool_size': len(self._pool._holders) if self._pool else 0
                    }
                    
            elif self.is_sqlite:
                db_path = self.database_url.replace('sqlite:///', '')
                async with aiosqlite.connect(db_path) as db:
                    # Check connection
                    await db.execute("SELECT 1")
                    
                    # Get database size
                    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
                    
                    # Get table info
                    cursor = await db.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """)
                    tables = await cursor.fetchall()
                    
                    return {
                        'status': 'healthy',
                        'database_type': 'SQLite',
                        'database_size': f"{db_size / (1024*1024):.2f} MB",
                        'tables': [{'name': table[0]} for table in tables],
                        'database_path': db_path
                    }
                    
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'database_type': 'PostgreSQL' if self.is_postgresql else 'SQLite'
            }
    
    async def close(self):
        """Close database connections"""
        try:
            if self._pool:
                await self._pool.close()
                self._pool = None
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
