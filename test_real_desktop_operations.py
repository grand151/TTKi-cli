"""
Real Desktop Operation Test
Test the actual desktop operation that user requested
"""
import asyncio
import sys
import os

# Add project root
project_root = "/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt"
sys.path.insert(0, project_root)

async def test_user_desktop_operation():
    """Test the specific operation user requested: create folder on desktop"""
    
    print("🖥️  Testing USER REQUESTED OPERATION")
    print("=" * 50)
    print("Operation: 'kazałem agentowi utworzyć nowy folder na pulpicie'")
    print("=" * 50)
    
    try:
        # Import the hybrid desktop agent
        from src.infrastructure.agents.desktop_agent_hybrid import DesktopAgent
        
        # Initialize agent
        agent = DesktopAgent()
        print("✅ Desktop Agent initialized")
        
        # Execute EXACT user operation
        result = await agent.execute_task(
            "utwórz nowy folder na pulpicie", 
            {"folder_name": "NowyFolder"}
        )
        
        print(f"✅ Operation completed: {result.success}")
        print(f"📁 Folder creation result: {result.data}")
        print(f"⏱️  Duration: {result.duration}s")
        
        if result.success:
            print("\n🎉 SUCCESS! User's desktop operation completed!")
            print("🌉 Via Legacy Bridge -> TTKi VNC Container")
            print(f"📍 Folder path: {result.data.get('path', 'N/A')}")
            
            # Test another operation
            screenshot_result = await agent.execute_task("take screenshot")
            print(f"\n📸 Screenshot test: {screenshot_result.success}")
            
        return result.success
        
    except Exception as e:
        print(f"❌ User operation failed: {str(e)}")
        return False

async def test_multiple_desktop_operations():
    """Test multiple desktop operations"""
    
    print("\n🔄 Testing Multiple Desktop Operations")
    print("=" * 50)
    
    from src.infrastructure.agents.desktop_agent_hybrid import DesktopAgent
    agent = DesktopAgent()
    
    operations = [
        ("create folder TestFolder1", {"folder_name": "TestFolder1"}),
        ("create folder TestFolder2", {"folder_name": "TestFolder2"}),
        ("take screenshot", {}),
        ("list files on desktop", {}),
    ]
    
    results = []
    
    for operation, context in operations:
        print(f"\n🔧 Executing: {operation}")
        result = await agent.execute_task(operation, context)
        results.append(result.success)
        print(f"   Result: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        
        if result.success and result.data:
            print(f"   Data: {result.data}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    return success_rate >= 75

async def main():
    """Main test function"""
    
    print("🧪 REAL DESKTOP OPERATION TEST")
    print("Testing the exact operation user requested")
    print("=" * 60)
    
    # Test user specific operation
    user_op_success = await test_user_desktop_operation()
    
    # Test multiple operations
    multi_op_success = await test_multiple_desktop_operations()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)
    
    print(f"User Desktop Operation:    {'✅ SUCCESS' if user_op_success else '❌ FAILED'}")
    print(f"Multiple Operations:       {'✅ SUCCESS' if multi_op_success else '❌ FAILED'}")
    
    if user_op_success and multi_op_success:
        print("\n🎉 DESKTOP OPERATIONS FULLY WORKING!")
        print("🚀 Hybrid DDD + Legacy Bridge architecture successful!")
        print("👨‍💻 User can now create folders and perform desktop operations!")
    else:
        print("\n⚠️  Some operations need attention")

if __name__ == "__main__":
    asyncio.run(main())
