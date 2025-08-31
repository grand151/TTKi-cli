"""
Test Real Desktop Agent Integration
"""
import asyncio
import requests
import json

async def test_desktop_operations():
    """Test desktop operations through both systems"""
    print("🖥️  Testing Desktop Operations Integration...")
    
    # Test 1: Legacy TTKi (port 4001) 
    print("\n🔗 Test 1: Legacy TTKi System")
    try:
        # Test legacy system
        legacy_url = "http://localhost:4001"
        response = requests.get(legacy_url, timeout=5)
        print(f"   ✅ Legacy TTKi accessible: {response.status_code}")
        
        # Test desktop function via legacy
        print("   🖥️  Testing desktop folder creation via legacy...")
        
        # This would normally go through WebSocket or direct function call
        print("   📁 Would create folder via legacy TTKi container")
        
    except Exception as e:
        print(f"   ❌ Legacy TTKi not accessible: {str(e)}")
    
    # Test 2: New FastAPI system (port 8000)
    print("\n🚀 Test 2: New FastAPI + DDD System")
    try:
        # Test FastAPI system
        fastapi_url = "http://localhost:8000"
        
        # Health check
        health_response = requests.get(f"{fastapi_url}/api/v1/health", timeout=5)
        print(f"   ✅ FastAPI accessible: {health_response.status_code}")
        
        # Test task execution
        task_data = {
            "task": "create folder named 'DDD_Test' on desktop",
            "context": {"folder_name": "DDD_Test"},
            "priority": "high"
        }
        
        print("   📋 Executing task via FastAPI...")
        task_response = requests.post(
            f"{fastapi_url}/api/v1/execute",
            json=task_data,
            timeout=30
        )
        
        if task_response.status_code == 200:
            result = task_response.json()
            print(f"   🎯 Task success: {result.get('success')}")
            print(f"   ⏱️  Duration: {result.get('duration', 0):.2f}s")
            print(f"   🤖 Agent: {result.get('agent_type')}")
            
            if result.get('execution_plan'):
                plan = result['execution_plan']
                print(f"   📊 Plan: {plan.get('task_count')} tasks")
        else:
            print(f"   ❌ Task failed: {task_response.status_code}")
            print(f"   Error: {task_response.text}")
        
    except Exception as e:
        print(f"   ❌ FastAPI system error: {str(e)}")
    
    # Test 3: System integration recommendation
    print("\n💡 Integration Strategy:")
    print("   🔄 FastAPI system should delegate desktop ops to legacy TTKi")
    print("   🖥️  Legacy TTKi has direct Docker container access")
    print("   🚀 FastAPI provides modern API + DDD architecture")
    print("   🌉 Bridge between systems needed for seamless operation")

if __name__ == "__main__":
    asyncio.run(test_desktop_operations())
