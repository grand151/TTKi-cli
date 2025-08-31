"""
Test PlannerAgent Integration
Quick test to verify PlannerAgent functionality
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append('/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt')

from agents.planner_agent import PlannerAgent
from agents.base_agent import Task, TaskType, TaskPriority

async def test_planner_agent():
    """Test PlannerAgent basic functionality"""
    print("🚀 Testing TTKi PlannerAgent...")
    
    # Initialize PlannerAgent
    planner = PlannerAgent()
    print(f"✅ PlannerAgent initialized: {planner.state.agent_id}")
    
    # Test 1: Simple task analysis
    print("\n📋 Test 1: Task Analysis")
    test_requests = [
        "Take a screenshot and analyze what's on the screen",
        "Create a Python function that calculates fibonacci numbers",
        "Open browser, navigate to google.com and search for 'AI agents'",
        "First take screenshot, then write code to process images, and finally test the code"
    ]
    
    for request in test_requests:
        print(f"\n🔍 Analyzing: '{request}'")
        
        # Analyze task complexity
        tasks = planner.task_router.decompose_complex_task(request)
        print(f"   📊 Decomposed into {len(tasks)} subtasks:")
        
        for i, task in enumerate(tasks, 1):
            print(f"     {i}. {task.type.value}: {task.description[:50]}...")
            print(f"        Priority: {task.priority.value}, Duration: {task.estimated_duration:.1f}s")
    
    # Test 2: Plan execution simulation
    print("\n🎯 Test 2: Plan Creation")
    test_task = Task(
        id="test_001",
        type=TaskType.PLANNING,
        description="Take a screenshot and create a summary of what's visible",
        priority=TaskPriority.HIGH
    )
    
    result = await planner.execute_task(test_task)
    print(f"✅ Plan creation result: {result.success}")
    
    if result.success and result.result:
        plan = result.result
        print(f"   📋 Plan ID: {plan.plan_id}")
        print(f"   📊 Tasks count: {len(plan.tasks)}")
        print(f"   ⏱️  Estimated duration: {plan.estimated_total_duration:.1f}s")
        print(f"   🎛️  Complexity score: {plan.complexity_score:.2f}")
    
    # Test 3: System status
    print("\n📈 Test 3: System Status")
    status = planner.get_system_status()
    print(f"   🤖 Agent type: {status['planner_agent']['agent_type']}")
    print(f"   📊 Performance metrics: {status['planner_agent']['performance_metrics']}")
    print(f"   🎯 Routing stats: {status['routing_stats']}")
    
    print("\n🎉 All tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_planner_agent())
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
