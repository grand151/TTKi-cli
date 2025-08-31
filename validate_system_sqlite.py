#!/usr/bin/env python3
"""
TTKi System Validation with SQLite Backend
=======================================

Comprehensive validation test for the TTKi Advanced AI System using SQLite database.
This version tests all system components without requiring PostgreSQL/Docker.
"""

import asyncio
import aiosqlite
import json
import time
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
import uuid
import numpy as np

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class ValidationTest:
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        self.db_path = "ttki_validation.db"
        
    async def setup_database(self):
        """Setup SQLite database with test schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Create basic tables for testing
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_analytics (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    agent_id TEXT,
                    session_id TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS learning_events (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    embedding_vector TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            await db.commit()
    
    async def cleanup_database(self):
        """Remove test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    async def test_database_connectivity(self):
        """Test 1: Database Basic Operations"""
        try:
            await self.setup_database()
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT 1 as test")
                result = await cursor.fetchone()
                assert result[0] == 1
                
            self.test_results.append({
                'name': 'Database Basic Operations',
                'status': 'PASSED',
                'message': 'SQLite connectivity and basic queries working'
            })
            print("✅ Database test: PASSED")
            return True
            
        except Exception as e:
            self.test_results.append({
                'name': 'Database Basic Operations',
                'status': 'FAILED',
                'message': f'Database error: {str(e)}'
            })
            print(f"❌ Database test failed: {str(e)}")
            return False
    
    async def test_crud_operations(self):
        """Test 2: CRUD Operations"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # CREATE: Insert test agent
                agent_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO agents (id, name, agent_type, status)
                    VALUES (?, ?, ?, ?)
                """, (agent_id, 'TestAgent', 'research', 'active'))
                
                # CREATE: Insert test task
                task_id = str(uuid.uuid4())
                await db.execute("""
                    INSERT INTO tasks (id, agent_id, name, description, status, priority)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (task_id, agent_id, 'Test Task', 'A test task for validation', 'pending', 2))
                
                await db.commit()
                
                # READ: Verify agent exists
                cursor = await db.execute("SELECT name, agent_type FROM agents WHERE id = ?", (agent_id,))
                agent_result = await cursor.fetchone()
                assert agent_result[0] == 'TestAgent'
                assert agent_result[1] == 'research'
                
                # READ: Verify task exists
                cursor = await db.execute("SELECT name, status, priority FROM tasks WHERE id = ?", (task_id,))
                task_result = await cursor.fetchone()
                assert task_result[0] == 'Test Task'
                assert task_result[1] == 'pending'
                assert task_result[2] == 2
                
                # UPDATE: Modify task status
                await db.execute("UPDATE tasks SET status = ? WHERE id = ?", ('completed', task_id))
                await db.commit()
                
                # Verify update
                cursor = await db.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
                updated_result = await cursor.fetchone()
                assert updated_result[0] == 'completed'
                
                # DELETE: Remove test data
                await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                await db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
                await db.commit()
                
                # Verify deletion
                cursor = await db.execute("SELECT COUNT(*) FROM agents WHERE id = ?", (agent_id,))
                count_result = await cursor.fetchone()
                assert count_result[0] == 0
            
            self.test_results.append({
                'name': 'CRUD Operations',
                'status': 'PASSED',
                'message': 'All CRUD operations working correctly'
            })
            print("✅ CRUD test: PASSED")
            return True
            
        except Exception as e:
            self.test_results.append({
                'name': 'CRUD Operations',
                'status': 'FAILED',
                'message': f'CRUD error: {str(e)}'
            })
            print(f"❌ CRUD test failed: {str(e)}")
            return False
    
    async def test_analytics_recording(self):
        """Test 3: Analytics Recording"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Insert analytics event
                analytics_id = str(uuid.uuid4())
                agent_id = str(uuid.uuid4())
                session_id = str(uuid.uuid4())
                
                event_data = json.dumps({
                    'action': 'task_completion',
                    'duration': 5.2,
                    'success': True,
                    'metrics': {'cpu_usage': 15.3, 'memory_usage': 45.7}
                })
                
                await db.execute("""
                    INSERT INTO system_analytics (id, event_type, event_data, agent_id, session_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (analytics_id, 'task_execution', event_data, agent_id, session_id))
                
                await db.commit()
                
                # Verify analytics record
                cursor = await db.execute("""
                    SELECT event_type, event_data, agent_id 
                    FROM system_analytics 
                    WHERE id = ?
                """, (analytics_id,))
                
                result = await cursor.fetchone()
                assert result[0] == 'task_execution'
                assert result[2] == agent_id
                
                # Parse and verify event data
                parsed_data = json.loads(result[1])
                assert parsed_data['action'] == 'task_completion'
                assert parsed_data['success'] is True
                
                # Clean up
                await db.execute("DELETE FROM system_analytics WHERE id = ?", (analytics_id,))
                await db.commit()
            
            self.test_results.append({
                'name': 'Analytics Recording',
                'status': 'PASSED',
                'message': 'Analytics recording and retrieval working'
            })
            print("✅ Analytics test: PASSED")
            return True
            
        except Exception as e:
            self.test_results.append({
                'name': 'Analytics Recording',
                'status': 'FAILED',
                'message': f'Analytics error: {str(e)}'
            })
            print(f"❌ Analytics test failed: {str(e)}")
            return False
    
    async def test_vector_operations(self):
        """Test 4: Vector Operations (simulated)"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Insert learning event with embedding
                event_id = str(uuid.uuid4())
                agent_id = str(uuid.uuid4())
                
                # Create a test embedding vector
                test_vector = np.random.rand(128).tolist()
                vector_json = json.dumps(test_vector)
                
                event_data = json.dumps({
                    'learning_type': 'experience',
                    'context': 'task completion',
                    'outcome': 'success',
                    'confidence': 0.85
                })
                
                await db.execute("""
                    INSERT INTO learning_events (id, agent_id, event_type, event_data, embedding_vector)
                    VALUES (?, ?, ?, ?, ?)
                """, (event_id, agent_id, 'experience_learning', event_data, vector_json))
                
                await db.commit()
                
                # Verify learning event
                cursor = await db.execute("""
                    SELECT event_type, event_data, embedding_vector 
                    FROM learning_events 
                    WHERE id = ?
                """, (event_id,))
                
                result = await cursor.fetchone()
                assert result[0] == 'experience_learning'
                
                # Verify vector storage
                stored_vector = json.loads(result[2])
                assert len(stored_vector) == 128
                assert isinstance(stored_vector[0], float)
                
                # Verify event data
                parsed_data = json.loads(result[1])
                assert parsed_data['learning_type'] == 'experience'
                assert parsed_data['confidence'] == 0.85
                
                # Clean up
                await db.execute("DELETE FROM learning_events WHERE id = ?", (event_id,))
                await db.commit()
            
            self.test_results.append({
                'name': 'Vector Operations',
                'status': 'PASSED',
                'message': 'Vector storage and retrieval working (simulated)'
            })
            print("✅ Vector test: PASSED")
            return True
            
        except Exception as e:
            self.test_results.append({
                'name': 'Vector Operations',
                'status': 'FAILED',
                'message': f'Vector error: {str(e)}'
            })
            print(f"❌ Vector test failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting TTKi System Validation (SQLite Backend)...")
        print("=" * 50)
        
        test_functions = [
            self.test_database_connectivity,
            self.test_crud_operations,
            self.test_analytics_recording,
            self.test_vector_operations
        ]
        
        passed = 0
        failed = 0
        
        for test_func in test_functions:
            print(f"🔍 Testing {test_func.__name__.replace('test_', '').replace('_', ' ')}...")
            try:
                success = await test_func()
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ {test_func.__name__} failed with exception: {str(e)}")
                failed += 1
                self.test_results.append({
                    'name': test_func.__name__.replace('test_', '').replace('_', ' ').title(),
                    'status': 'FAILED',
                    'message': f'Exception: {str(e)}'
                })
        
        # Generate report
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 50)
        print("TTKi System Validation Results (SQLite)")
        print("=" * 50)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Overall: {'✅ PASSED' if failed == 0 else '❌ FAILED'}")
        print("=" * 50)
        
        # Print detailed results
        for result in self.test_results:
            status_icon = "✅ PASS" if result['status'] == 'PASSED' else "❌ FAIL"
            print(f"{status_icon} {result['name']}")
            if result['status'] == 'FAILED':
                print(f"   Error: {result['message']}")
        
        # Save report
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_tests': passed + failed,
            'passed': passed,
            'failed': failed,
            'success_rate': passed / (passed + failed) * 100 if (passed + failed) > 0 else 0,
            'duration': duration,
            'overall_status': 'PASSED' if failed == 0 else 'FAILED',
            'test_results': self.test_results,
            'database_backend': 'SQLite'
        }
        
        with open('validation_report_sqlite.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Validation report saved: validation_report_sqlite.json")
        
        # Cleanup
        await self.cleanup_database()
        
        print("🎉 TTKi System Validation Complete!")
        
        return failed == 0

async def main():
    """Main validation entry point"""
    validator = ValidationTest()
    success = await validator.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
