"""
Test FastAPI + DDD Implementation
Verify the new architecture works correctly
"""
import asyncio
import sys
import os
import logging

# Add project root to path
sys.path.append('/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt')

# Configure logging for test
logging.basicConfig(level=logging.INFO)

async def test_ddd_architecture():
    """Test the new DDD architecture implementation"""
    print("🏗️  Testing TTKi FastAPI + DDD Architecture...")
    
    try:
        # Test 1: Import all DDD components
        print("\n📦 Test 1: Importing DDD Components")
        
        from src.domain.entities import TaskEntity, AgentEntity, ExecutionPlanEntity
        from src.domain.value_objects import TaskId, AgentId, TaskType, TaskPriority
        from src.domain.services.agent_orchestrator import AgentOrchestrator
        from src.application.services.ttki_application_service import TTKiApplicationService
        from src.infrastructure.config.settings import get_settings
        
        print("   ✅ All DDD components imported successfully")
        
        # Test 2: Configuration
        print("\n⚙️  Test 2: Configuration System")
        settings = get_settings()
        print(f"   📊 App: {settings.app_name} v{settings.version}")
        print(f"   🌐 Server: {settings.host}:{settings.port}")
        print(f"   🔄 Legacy support: {settings.enable_legacy_support}")
        
        # Test 3: Domain Objects Creation
        print("\n🎯 Test 3: Domain Objects")
        
        # Create value objects
        task_id = TaskId.generate()
        agent_id = AgentId.generate("TestAgent")
        print(f"   🆔 Task ID: {task_id}")
        print(f"   🤖 Agent ID: {agent_id}")
        
        # Create entities
        task_entity = TaskEntity(
            id=task_id,
            description="Test DDD task creation",
            task_type=TaskType.PLANNING,
            priority=TaskPriority.HIGH,
            estimated_duration=2.0
        )
        
        agent_entity = AgentEntity(
            id=agent_id,
            agent_type="TestAgent",
            capabilities=["testing", "validation"],
            performance_metrics={"success_rate": 1.0}
        )
        
        print(f"   📋 Task entity: {task_entity.description}")
        print(f"   🤖 Agent entity: {agent_entity.agent_type}")
        
        # Test 4: Domain Services
        print("\n🔧 Test 4: Domain Services")
        
        orchestrator = AgentOrchestrator()
        await orchestrator.register_agent(agent_entity)
        
        status = orchestrator.get_system_status()
        print(f"   🎛️  Orchestrator: {status['active_agents']} active agents")
        
        # Test 5: Application Service
        print("\n🚀 Test 5: Application Service")
        
        app_service = TTKiApplicationService(orchestrator)
        await app_service.initialize()
        
        system_status = await app_service.get_system_status()
        print(f"   ✅ Initialized: {system_status['initialized']}")
        print(f"   🏗️  Architecture: {system_status['architecture']}")
        print(f"   🔄 Legacy support: {system_status['legacy_support']}")
        
        # Test 6: Task Execution Simulation
        print("\n⚡ Test 6: Task Execution")
        
        result = await app_service.execute_task(
            task="Create a test file and analyze its content",
            context={"test_mode": True},
            priority="high"
        )
        
        print(f"   🎯 Execution success: {result['success']}")
        print(f"   ⏱️  Duration: {result.get('duration', 0):.2f}s")
        print(f"   🤖 Agent type: {result.get('agent_type')}")
        
        if result.get('execution_plan'):
            plan = result['execution_plan']
            print(f"   📋 Plan: {plan['task_count']} tasks, complexity: {plan['complexity_score']:.2f}")
        
        # Test 7: System Status
        print("\n📊 Test 7: System Status")
        final_status = await app_service.get_system_status()
        print(f"   📈 Active plans: {final_status['active_plans']}")
        print(f"   🎛️  Orchestrator agents: {len(final_status['orchestrator_status']['agent_details'])}")
        
        await app_service.shutdown()
        
        print("\n🎉 All DDD architecture tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ DDD architecture test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_ddd_architecture())
