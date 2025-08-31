"""
Simple TTKi System Validation Test
Tests basic system components without complex imports
"""

import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, Any

class SimpleSystemTest:
    """Basic system validation test"""
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'ttki_advanced_db',
            'user': 'ttki_user',
            'password': 'ttki_secure_2024'
        }
        self.test_results = []
    
    async def test_database_basic(self) -> Dict[str, Any]:
        """Test basic database operations"""
        print("🔍 Testing database connectivity...")
        
        result = {
            "test_name": "Database Basic Operations",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Test connection
            conn = await asyncpg.connect(**self.db_config)
            
            # Test basic query
            test_query = await conn.fetchval("SELECT 1")
            result["details"]["basic_query"] = test_query == 1
            
            # Test tables exist
            tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
            table_names = [table['tablename'] for table in tables]
            
            required_tables = ['agents', 'tasks', 'learning_events', 'memory_entries', 'system_analytics']
            tables_exist = all(table in table_names for table in required_tables)
            result["details"]["required_tables"] = tables_exist
            result["details"]["total_tables"] = len(table_names)
            
            # Test vector extension
            try:
                await conn.fetchval("SELECT '[1,2,3]'::vector")
                result["details"]["vector_support"] = True
            except Exception as e:
                result["details"]["vector_support"] = False
                result["errors"].append(f"Vector test: {e}")
            
            await conn.close()
            
            result["success"] = all([
                result["details"]["basic_query"],
                result["details"]["required_tables"],
                result["details"]["vector_support"]
            ])
            
            print(f"✅ Database test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"❌ Database test failed: {e}")
        
        return result
    
    async def test_crud_operations(self) -> Dict[str, Any]:
        """Test basic CRUD operations"""
        print("🔍 Testing CRUD operations...")
        
        result = {
            "test_name": "CRUD Operations",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            # Test agent creation with actual schema
            agent_id = "test_simple_agent"
            await conn.execute("""
                INSERT INTO agents (agent_id, agent_type, agent_name, capabilities, status)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (agent_id) DO UPDATE SET updated_at = now()
            """, agent_id, "test_agent", "Test Agent", ["testing"], "active")
            
            # Verify agent creation
            agent = await conn.fetchrow("SELECT * FROM agents WHERE agent_id = $1", agent_id)
            result["details"]["agent_crud"] = agent is not None
            
            # Test task creation with actual schema
            task_id = "test_simple_task"
            # Get the agent's UUID first
            agent_uuid = await conn.fetchval("SELECT id FROM agents WHERE agent_id = $1", agent_id)
            
            await conn.execute("""
                INSERT INTO tasks (task_id, title, description, task_type, assigned_agent_id, status)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (task_id) DO UPDATE SET updated_at = now()
            """, task_id, "Test Task", "Simple test task", "test", agent_uuid, "completed")
            
            # Verify task creation
            task = await conn.fetchrow("SELECT * FROM tasks WHERE task_id = $1", task_id)
            result["details"]["task_crud"] = task is not None
            
            # Test memory storage with actual schema
            await conn.execute("""
                INSERT INTO memory_entries (bank_id, entry_key, entry_type, content, created_by_agent_id)
                VALUES ((SELECT id FROM memory_banks WHERE bank_name = 'global_patterns' LIMIT 1), 
                        $1, $2, $3, $4)
                ON CONFLICT (bank_id, entry_key) DO UPDATE SET updated_at = now()
            """, "test_key", "test_data", 
                json.dumps({"test": "memory content"}), agent_uuid)
            
            # Verify memory storage
            memory = await conn.fetchrow("""
                SELECT * FROM memory_entries WHERE entry_key = $1
            """, "test_key")
            result["details"]["memory_crud"] = memory is not None
            
            await conn.close()
            
            result["success"] = all([
                result["details"]["agent_crud"],
                result["details"]["task_crud"],
                result["details"]["memory_crud"]
            ])
            
            print(f"✅ CRUD test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"❌ CRUD test failed: {e}")
        
        return result
    
    async def test_analytics_recording(self) -> Dict[str, Any]:
        """Test analytics recording"""
        print("🔍 Testing analytics recording...")
        
        result = {
            "test_name": "Analytics Recording",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            # Get existing agent for analytics
            agent_uuid = await conn.fetchval("SELECT id FROM agents WHERE agent_id = 'test_simple_agent'")
            
            # Record analytics in system_analytics table
            await conn.execute("""
                INSERT INTO system_analytics (
                    metric_type, metric_name, metric_value, 
                    dimensions, related_agent_id, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, "performance", "task_execution_time", 1.5,
                json.dumps({"task_type": "test", "success": True}), 
                agent_uuid, datetime.now())
            
            # Verify analytics
            analytics = await conn.fetchrow("""
                SELECT * FROM system_analytics WHERE metric_name = 'task_execution_time'
            """)
            result["details"]["analytics_recording"] = analytics is not None
            
            # Test performance summary
            summary = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_entries,
                    AVG(metric_value::numeric) as avg_value
                FROM system_analytics 
                WHERE created_at >= NOW() - INTERVAL '1 hour'
                  AND metric_type = 'performance'
            """)
            result["details"]["analytics_summary"] = summary is not None
            
            await conn.close()
            
            result["success"] = all([
                result["details"]["analytics_recording"],
                result["details"]["analytics_summary"]
            ])
            
            print(f"✅ Analytics test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"❌ Analytics test failed: {e}")
        
        return result
    
    async def test_vector_operations(self) -> Dict[str, Any]:
        """Test vector operations for AI features"""
        print("🔍 Testing vector operations...")
        
        result = {
            "test_name": "Vector Operations",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            conn = await asyncpg.connect(**self.db_config)
            
            # Get agent UUIDs
            source_agent = await conn.fetchval("SELECT id FROM agents WHERE agent_id = 'test_simple_agent'")
            target_agent = source_agent  # Use same agent for simplicity
            
            # Test vector storage in learning events
            test_vector = [0.1, 0.2, 0.3, 0.4, 0.5]  # 5D vector
            
            await conn.execute("""
                INSERT INTO learning_events (
                    source_agent_id, target_agent_id, event_type, 
                    content, outcome, embedding_vector, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, source_agent, target_agent, "test_learning", 
                json.dumps({"input": "test", "output": "result"}), "success",
                test_vector, datetime.now())
            
            # Test vector similarity search
            similar = await conn.fetch("""
                SELECT event_type, content,
                       embedding_vector <-> $1::vector as distance
                FROM learning_events 
                WHERE embedding_vector IS NOT NULL
                ORDER BY embedding_vector <-> $1::vector
                LIMIT 3
            """, test_vector)
            
            result["details"]["vector_storage"] = len(similar) > 0
            result["details"]["similarity_search"] = True
            
            # Test knowledge base vector search
            await conn.execute("""
                INSERT INTO knowledge_base (
                    source_agent_id, knowledge_type, content, 
                    embedding_vector, created_at
                ) VALUES ($1, $2, $3, $4, $5)
            """, source_agent, "pattern", 
                json.dumps({"pattern": "test_pattern", "success_rate": 0.95}),
                test_vector, datetime.now())
            
            knowledge = await conn.fetchrow("""
                SELECT * FROM knowledge_base WHERE knowledge_type = 'pattern'
            """)
            result["details"]["knowledge_storage"] = knowledge is not None
            
            await conn.close()
            
            result["success"] = all([
                result["details"]["vector_storage"],
                result["details"]["similarity_search"],
                result["details"]["knowledge_storage"]
            ])
            
            print(f"✅ Vector test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"❌ Vector test failed: {e}")
        
        return result
    
    async def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting TTKi System Validation...")
        print("=" * 50)
        
        start_time = datetime.now()
        
        # Run tests
        tests = [
            self.test_database_basic(),
            self.test_crud_operations(),
            self.test_analytics_recording(),
            self.test_vector_operations()
        ]
        
        results = []
        for test_coro in tests:
            try:
                result = await test_coro
                results.append(result)
                self.test_results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append({
                    "test_name": "Unknown Test",
                    "success": False,
                    "errors": [str(e)]
                })
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["success"])
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print results
        print("\n" + "=" * 50)
        print("TTKi System Validation Results")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Overall: {'✅ PASSED' if passed_tests == total_tests else '❌ FAILED'}")
        print("=" * 50)
        
        # Print individual results
        for result in results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test_name']}")
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"   Error: {error}")
        
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests,
                "duration_seconds": duration
            },
            "test_results": results
        }
        
        with open("validation_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📊 Validation report saved: validation_report.json")
        print("🎉 TTKi System Validation Complete!")
        
        return report

async def main():
    """Main validation execution"""
    validator = SimpleSystemTest()
    await validator.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
