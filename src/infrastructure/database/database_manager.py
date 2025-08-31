"""
Database Configuration and Connection Management
Advanced PostgreSQL + Vector Database Integration
"""
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import asynccontextmanager

import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ttki_advanced"
    user: str = ""
    password: str = ""
    readonly_user: str = ""
    readonly_password: str = ""
    pool_min_size: int = 10
    pool_max_size: int = 50
    
    @classmethod
    def from_file(cls, credentials_file: str) -> 'DatabaseConfig':
        """Load configuration from credentials file"""
        config = {}
        
        if os.path.exists(credentials_file):
            with open(credentials_file, 'r') as f:
                for line in f:
                    if line.startswith('#') or '=' not in line:
                        continue
                    key, value = line.strip().split('=', 1)
                    config[key] = value
        
        return cls(
            host=config.get('DB_HOST', 'localhost'),
            port=int(config.get('DB_PORT', 5432)),
            database=config.get('DB_NAME', 'ttki_advanced'),
            user=config.get('DB_USER', ''),
            password=config.get('DB_PASSWORD', ''),
            readonly_user=config.get('DB_READONLY_USER', ''),
            readonly_password=config.get('DB_READONLY_PASSWORD', '')
        )

class DatabaseManager:
    """
    Advanced Database Manager for TTKi System
    Handles connections, pooling, and operations
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.readonly_pool: Optional[asyncpg.Pool] = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize database connections"""
        try:
            # Create main connection pool
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=self.config.pool_min_size,
                max_size=self.config.pool_max_size,
                command_timeout=60
            )
            
            # Create readonly connection pool
            if self.config.readonly_user:
                self.readonly_pool = await asyncpg.create_pool(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.readonly_user,
                    password=self.config.readonly_password,
                    min_size=5,
                    max_size=20,
                    command_timeout=30
                )
            
            self._initialized = True
            logger.info("✅ Database Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
        if self.readonly_pool:
            await self.readonly_pool.close()
        self._initialized = False
        logger.info("🔌 Database connections closed")
    
    @asynccontextmanager
    async def get_connection(self, readonly: bool = False):
        """Get database connection from pool"""
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        
        pool = self.readonly_pool if readonly and self.readonly_pool else self.pool
        
        async with pool.acquire() as connection:
            yield connection
    
    async def execute_query(
        self, 
        query: str, 
        *args, 
        readonly: bool = False
    ) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        async with self.get_connection(readonly=readonly) as conn:
            result = await conn.fetch(query, *args)
            return [dict(record) for record in result]
    
    async def execute_single(
        self, 
        query: str, 
        *args, 
        readonly: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Execute query and return single result"""
        async with self.get_connection(readonly=readonly) as conn:
            result = await conn.fetchrow(query, *args)
            return dict(result) if result else None
    
    async def execute_command(self, query: str, *args) -> str:
        """Execute command (INSERT, UPDATE, DELETE)"""
        async with self.get_connection() as conn:
            result = await conn.execute(query, *args)
            return result
    
    async def vector_search(
        self, 
        table: str, 
        embedding_column: str,
        query_embedding: List[float], 
        limit: int = 10,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        
        # Convert embedding to proper format
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        query = f"""
        SELECT *, 
               1 - ({embedding_column} <=> $1::vector) as similarity_score
        FROM {table}
        WHERE 1 - ({embedding_column} <=> $1::vector) > $2
        ORDER BY similarity_score DESC
        LIMIT $3
        """
        
        return await self.execute_query(
            query, 
            embedding_str, 
            similarity_threshold, 
            limit,
            readonly=True
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Test main connection
            main_status = await self.execute_single(
                "SELECT 1 as status, version() as version",
                readonly=False
            )
            
            # Test readonly connection
            readonly_status = None
            if self.readonly_pool:
                readonly_status = await self.execute_single(
                    "SELECT 1 as status",
                    readonly=True
                )
            
            # Get connection pool stats
            pool_stats = {
                "main_pool_size": self.pool.get_size() if self.pool else 0,
                "main_pool_idle": self.pool.get_idle_size() if self.pool else 0,
                "readonly_pool_size": self.readonly_pool.get_size() if self.readonly_pool else 0,
                "readonly_pool_idle": self.readonly_pool.get_idle_size() if self.readonly_pool else 0
            }
            
            return {
                "status": "healthy",
                "main_connection": bool(main_status),
                "readonly_connection": bool(readonly_status),
                "pool_stats": pool_stats,
                "database_version": main_status.get("version") if main_status else None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global database manager instance
db_manager: Optional[DatabaseManager] = None

async def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global db_manager
    
    if db_manager is None:
        credentials_file = "/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/.db_credentials"
        config = DatabaseConfig.from_file(credentials_file)
        db_manager = DatabaseManager(config)
        await db_manager.initialize()
    
    return db_manager

async def close_database_manager():
    """Close global database manager"""
    global db_manager
    
    if db_manager:
        await db_manager.close()
        db_manager = None
