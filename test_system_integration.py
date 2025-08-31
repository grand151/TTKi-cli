"""
TTKi Advanced AI System - Comprehensive Integration Test
Tests all system components: database, DDD architecture, cross-agent learning, analytics
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Test imports
try:
    from src.infrastructure.database.database_manager import DatabaseManager
    from src.infrastructure.database.repositories.agent_repository import AgentRepository
    from src.infrastructure.database.repositories.task_repository import TaskRepository
    from src.infrastructure.database.repositories.learning_repository import LearningRepository
    from src.infrastructure.database.repositories.memory_repository import MemoryRepository
    from src.infrastructure.database.repositories.analytics_repository import AnalyticsRepository
    from src.application.services.ttki_application_service import TTKiApplicationService
    from src.application.services.system_dashboard_service import SystemDashboardService
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TTKiSystemTest:
    """Comprehensive system integration test"""
    
    def __init__(self):
        self.db_manager = None
        self.repositories = {}
        self.services = {}
        self.test_results = []
        
    async def setup(self):
        """Initialize all system components"""
        logger.info("🔧 Setting up TTKi system test environment...")
        
        try:
            # Initialize database manager
            self.db_manager = DatabaseManager(
                host="localhost",
                port=5432,
                database="ttki_advanced_db",
                user="ttki_user",
                password="ttki_secure_2024"
            )
            
            await self.db_manager.initialize()
            logger.info("✅ Database manager initialized")
            
            # Initialize repositories
            self.repositories = {
                'agent': AgentRepository(self.db_manager),
                'task': TaskRepository(self.db_manager),
                'learning': LearningRepository(self.db_manager),
                'memory': MemoryRepository(self.db_manager),
                'analytics': AnalyticsRepository(self.db_manager)
            }
            logger.info("✅ All repositories initialized")
            
            # Initialize services
            self.services = {
                'application': TTKiApplicationService(
                    db_manager=self.db_manager,
                    agent_repo=self.repositories['agent'],
                    task_repo=self.repositories['task'],
                    learning_repo=self.repositories['learning'],
                    memory_repo=self.repositories['memory'],
                    analytics_repo=self.repositories['analytics']
                ),
                'dashboard': SystemDashboardService(
                    db_manager=self.db_manager,
                    **self.repositories
                )
            }
            
            await self.services['application'].initialize()
            logger.info("✅ All services initialized")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            raise e
    
    async def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity and basic operations"""
        logger.info("🔍 Testing database connectivity...")
        
        result = {
            "test_name": "Database Connectivity",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Test health check
            health_check = await self.db_manager.health_check()
            result["details"]["health_check"] = health_check
            
            # Test read connection
            async with self.db_manager.get_read_connection() as conn:
                test_query = await conn.fetchval("SELECT 1")
                result["details"]["read_connection"] = test_query == 1
            
            # Test write connection
            async with self.db_manager.get_write_connection() as conn:
                test_query = await conn.fetchval("SELECT COUNT(*) FROM agents")
                result["details"]["write_connection"] = isinstance(test_query, int)
                result["details"]["agent_count"] = test_query
            
            # Test vector search capability
            try:
                async with self.db_manager.get_read_connection() as conn:
                    vector_test = await conn.fetchval("SELECT '[1,2,3]'::vector")
                    result["details"]["vector_support"] = vector_test is not None
            except Exception as e:
                result["details"]["vector_support"] = False
                result["errors"].append(f"Vector test failed: {e}")
            
            result["success"] = all([
                health_check,
                result["details"]["read_connection"],
                result["details"]["write_connection"]
            ])
            
            logger.info(f"✅ Database connectivity test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"❌ Database connectivity test failed: {e}")
        
        return result
    
    async def test_repository_operations(self) -> Dict[str, Any]:
        """Test CRUD operations for all repositories"""
        logger.info("🔍 Testing repository operations...")
        
        result = {
            "test_name": "Repository Operations",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Test agent repository
            logger.info("Testing agent repository...")
            test_agent_id = "test_agent_001"
            
            # Create agent
            await self.repositories['agent'].create_agent(
                agent_id=test_agent_id,
                agent_type="test_agent",
                capabilities=["testing", "validation"],
                metadata={"test": True, "created_at": datetime.now().isoformat()}
            )
            
            # Get agent
            agent = await self.repositories['agent'].get_agent(test_agent_id)
            result["details"]["agent_operations"] = agent is not None
            
            # Test task repository
            logger.info("Testing task repository...")
            test_task_id = "test_task_001"
            
            await self.repositories['task'].create_task(
                task_id=test_task_id,
                description="Test task for validation",
                agent_type="test_agent",
                status="completed",
                metadata={"test": True}
            )
            
            task = await self.repositories['task'].get_task(test_task_id)
            result["details"]["task_operations"] = task is not None
            
            # Test learning repository
            logger.info("Testing learning repository...")
            
            await self.repositories['learning'].record_learning_event(
                agent_id=test_agent_id,
                event_type="test_completion",
                input_data={"test_input": "sample"},
                output_data={"test_output": "result"},
                feedback_score=0.95,
                metadata={"test": True}
            )
            
            learning_events = await self.repositories['learning'].get_recent_learning_events(limit=1)
            result["details"]["learning_operations"] = len(learning_events) > 0
            
            # Test memory repository
            logger.info("Testing memory repository...")
            
            await self.repositories['memory'].store_memory(
                bank_name="test_bank",
                entry_key="test_entry",
                entry_type="test_data",
                content={"test": "memory content", "timestamp": datetime.now().isoformat()}
            )
            
            memory_entry = await self.repositories['memory'].retrieve_memory("test_bank", "test_entry")
            result["details"]["memory_operations"] = memory_entry is not None
            
            # Test analytics repository
            logger.info("Testing analytics repository...")
            
            await self.repositories['analytics'].record_task_analytics(
                task_id=test_task_id,
                agent_type="test_agent",
                execution_time=1.5,
                success=True,
                metadata={"test": True}
            )
            
            analytics = await self.repositories['analytics'].get_performance_summary(time_window_hours=1)
            result["details"]["analytics_operations"] = analytics.get("total_tasks", 0) > 0
            
            result["success"] = all([
                result["details"]["agent_operations"],
                result["details"]["task_operations"],
                result["details"]["learning_operations"],
                result["details"]["memory_operations"],
                result["details"]["analytics_operations"]
            ])
            
            logger.info(f"✅ Repository operations test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"❌ Repository operations test failed: {e}")
        
        return result
    
    async def test_cross_agent_learning(self) -> Dict[str, Any]:
        """Test cross-agent learning capabilities"""
        logger.info("🔍 Testing cross-agent learning system...")
        
        result = {
            "test_name": "Cross-Agent Learning",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Create multiple agents
            agents = ["agent_001", "agent_002", "agent_003"]
            for agent_id in agents:
                await self.repositories['agent'].create_agent(
                    agent_id=agent_id,
                    agent_type=f"specialized_agent_{agent_id[-1]}",
                    capabilities=["learning", "sharing"],
                    metadata={"learning_test": True}
                )
            
            # Record learning events for each agent
            learning_tasks = [
                ("file_operation", {"files": ["test.txt"]}, {"success": True, "processed": 1}),
                ("data_analysis", {"dataset": "sample.csv"}, {"insights": ["trend1", "trend2"]}),
                ("network_request", {"url": "api.test.com"}, {"status": 200, "data": "response"})
            ]
            
            for i, (task_type, input_data, output_data) in enumerate(learning_tasks):
                await self.repositories['learning'].record_learning_event(
                    agent_id=agents[i],
                    event_type=task_type,
                    input_data=input_data,
                    output_data=output_data,
                    feedback_score=0.9,
                    metadata={"cross_learning_test": True}
                )
            
            # Test similarity search
            similar_tasks = await self.repositories['learning'].find_similar_tasks(
                "file processing operation", limit=3, threshold=0.5
            )
            result["details"]["similarity_search"] = len(similar_tasks) > 0
            
            # Test shared memory
            await self.repositories['memory'].store_memory(
                bank_name="cross_agent_learning",
                entry_key="shared_pattern_001",
                entry_type="success_pattern",
                content={
                    "pattern_type": "file_processing",
                    "success_factors": ["proper_validation", "error_handling"],
                    "applicable_agents": agents
                }
            )
            
            shared_patterns = await self.repositories['memory'].get_bank_entries("cross_agent_learning")
            result["details"]["shared_memory"] = len(shared_patterns) > 0
            
            # Test learning statistics
            learning_stats = await self.repositories['learning'].get_learning_stats()
            result["details"]["learning_stats"] = learning_stats.get("total_events", 0) >= len(learning_tasks)
            
            # Test top learning agents
            top_agents = await self.repositories['learning'].get_top_learning_agents(limit=3)
            result["details"]["top_agents"] = len(top_agents) > 0
            
            result["success"] = all([
                result["details"]["similarity_search"],
                result["details"]["shared_memory"],
                result["details"]["learning_stats"],
                result["details"]["top_agents"]
            ])
            
            logger.info(f"✅ Cross-agent learning test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"❌ Cross-agent learning test failed: {e}")
        
        return result
    
    async def test_system_dashboard(self) -> Dict[str, Any]:
        """Test system dashboard and analytics"""
        logger.info("🔍 Testing system dashboard...")
        
        result = {
            "test_name": "System Dashboard",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Get real-time dashboard
            dashboard = await self.services['dashboard'].get_real_time_dashboard()
            result["details"]["dashboard_generation"] = "timestamp" in dashboard
            
            # Check dashboard components
            required_components = [
                "system_health", "performance_metrics", "agent_metrics",
                "learning_insights", "memory_status", "recommendations"
            ]
            
            for component in required_components:
                result["details"][f"has_{component}"] = component in dashboard
            
            # Test dashboard export
            export_data = await self.services['dashboard'].export_dashboard_data("json")
            result["details"]["export_functionality"] = len(export_data) > 0
            
            result["success"] = all([
                result["details"]["dashboard_generation"],
                *[result["details"][f"has_{comp}"] for comp in required_components],
                result["details"]["export_functionality"]
            ])
            
            logger.info(f"✅ System dashboard test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"❌ System dashboard test failed: {e}")
        
        return result
    
    async def test_application_service(self) -> Dict[str, Any]:
        """Test main application service functionality"""
        logger.info("🔍 Testing application service...")
        
        result = {
            "test_name": "Application Service",
            "success": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Test task execution
            task_result = await self.services['application'].execute_task(
                "Analyze test data and generate report",
                agent_type="analysis_agent",
                context={"test_mode": True, "data_source": "test_dataset"}
            )
            
            result["details"]["task_execution"] = hasattr(task_result, 'success')
            
            # Test cross-agent insights
            insights = await self.services['application'].get_cross_agent_insights(
                "Process file data"
            )
            result["details"]["cross_agent_insights"] = "insights" in insights
            
            # Test system analytics
            analytics = await self.services['application'].get_system_analytics()
            result["details"]["system_analytics"] = "performance_summary" in analytics or "status" in analytics
            
            result["success"] = all([
                result["details"]["task_execution"],
                result["details"]["cross_agent_insights"],
                result["details"]["system_analytics"]
            ])
            
            logger.info(f"✅ Application service test: {'PASSED' if result['success'] else 'FAILED'}")
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"❌ Application service test failed: {e}")
        
        return result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all system tests"""
        logger.info("🚀 Starting comprehensive TTKi system test...")
        
        start_time = datetime.now()
        
        # Run all tests
        tests = [
            self.test_database_connectivity(),
            self.test_repository_operations(),
            self.test_cross_agent_learning(),
            self.test_system_dashboard(),
            self.test_application_service()
        ]
        
        test_results = []
        for test in tests:
            try:
                result = await test
                test_results.append(result)
                self.test_results.append(result)
            except Exception as e:
                error_result = {
                    "test_name": "Unknown Test",
                    "success": False,
                    "details": {},
                    "errors": [str(e)]
                }
                test_results.append(error_result)
                self.test_results.append(error_result)
        
        # Calculate overall results
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result["success"])
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "test_results": test_results,
            "overall_success": passed_tests == total_tests
        }
        
        return summary
    
    async def cleanup(self):
        """Clean up test data and connections"""
        logger.info("🧹 Cleaning up test environment...")
        
        try:
            # Clean up test data
            if self.db_manager:
                async with self.db_manager.get_write_connection() as conn:
                    # Remove test agents
                    await conn.execute("DELETE FROM agents WHERE agent_id LIKE 'test_%' OR agent_id LIKE 'agent_%'")
                    
                    # Remove test tasks
                    await conn.execute("DELETE FROM tasks WHERE task_id LIKE 'test_%'")
                    
                    # Remove test learning events
                    await conn.execute("DELETE FROM learning_events WHERE metadata->>'test' = 'true' OR metadata->>'cross_learning_test' = 'true' OR metadata->>'learning_test' = 'true'")
                    
                    # Remove test memory entries
                    await conn.execute("DELETE FROM shared_memory WHERE bank_name = 'test_bank' OR bank_name = 'cross_agent_learning'")
                    
                    # Remove test analytics
                    await conn.execute("DELETE FROM task_analytics WHERE metadata->>'test' = 'true'")
            
            # Close database connections
            if self.services.get('application'):
                await self.services['application'].shutdown()
            
            if self.db_manager:
                await self.db_manager.close()
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")

async def main():
    """Main test execution"""
    test_runner = TTKiSystemTest()
    
    try:
        # Setup
        await test_runner.setup()
        
        # Run tests
        results = await test_runner.run_all_tests()
        
        # Generate test report
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        summary = results["test_summary"]
        print("\n" + "="*50)
        print("TTKi System Test Results")
        print("="*50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"Overall: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
        print(f"Report: {report_filename}")
        print("="*50)
        
        # Print individual test results
        for result in results["test_results"]:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test_name']}")
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"   Error: {error}")
        
        print("\n🎉 TTKi System Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        await test_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
