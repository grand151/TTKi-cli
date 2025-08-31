"""
Direct Bridge Test - Test Legacy Bridge without full system
"""
import asyncio
import sys
import os

# Add project root to path
project_root = "/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt"
sys.path.insert(0, project_root)

async def test_bridge_direct():
    """Test bridge functionality directly"""
    
    print("🌉 Testing Legacy Bridge Direct")
    print("=" * 40)
    
    try:
        # Test bridge import
        from src.infrastructure.agents.legacy_bridge import LegacyTTKiBridge
        print("✅ Bridge imported successfully")
        
        # Initialize bridge
        bridge = LegacyTTKiBridge()
        print(f"✅ Bridge initialized: {bridge.available}")
        
        # Test folder creation
        result = await bridge.execute_desktop_operation(
            "create folder TestFolder", 
            {"folder_name": "TestFolder"}
        )
        
        print(f"✅ Bridge operation success: {result.success}")
        print(f"   Data: {result.data}")
        print(f"   Duration: {result.duration}s")
        
        # Test status
        status = bridge.get_status()
        print(f"✅ Bridge status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bridge test failed: {str(e)}")
        return False

async def test_desktop_agent_direct():
    """Test desktop agent directly"""
    
    print("\n🖥️  Testing Desktop Agent Direct")
    print("=" * 40)
    
    try:
        # Test desktop agent import
        from src.infrastructure.agents.desktop_agent_hybrid import DesktopAgent
        print("✅ Desktop Agent imported successfully")
        
        # Initialize agent
        agent = DesktopAgent()
        print("✅ Desktop Agent initialized")
        
        # Test folder creation task
        result = await agent.execute_task(
            "create folder on desktop", 
            {"folder_name": "DirectTestFolder"}
        )
        
        print(f"✅ Desktop operation success: {result.success}")
        print(f"   Data: {result.data}")
        print(f"   Duration: {result.duration}s")
        
        # Test agent status
        status = agent.get_status()
        print(f"✅ Agent status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Desktop agent test failed: {str(e)}")
        return False

async def test_legacy_ttki_connection():
    """Test legacy TTKi connection"""
    
    print("\n🔧 Testing Legacy TTKi Connection")
    print("=" * 40)
    
    try:
        import requests
        
        response = requests.get("http://localhost:4001", timeout=5)
        if response.status_code == 200:
            print("✅ Legacy TTKi accessible: 200")
            return True
        else:
            print(f"❌ Legacy TTKi error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Legacy TTKi connection failed: {str(e)}")
        return False

async def main():
    """Run direct tests"""
    
    print("🧪 Direct Bridge & Desktop Agent Test")
    print("=" * 50)
    
    # Test individual components
    legacy_ok = await test_legacy_ttki_connection()
    bridge_ok = await test_bridge_direct()
    desktop_ok = await test_desktop_agent_direct()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 DIRECT TEST SUMMARY")
    print("=" * 50)
    
    total_tests = 3
    passed_tests = sum([legacy_ok, bridge_ok, desktop_ok])
    
    print(f"Legacy TTKi:       {'✅ PASS' if legacy_ok else '❌ FAIL'}")
    print(f"Legacy Bridge:     {'✅ PASS' if bridge_ok else '❌ FAIL'}")
    print(f"Desktop Agent:     {'✅ PASS' if desktop_ok else '❌ FAIL'}")
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 BRIDGE SYSTEM WORKING!")
        print("🚀 Ready for desktop operations!")
    else:
        print("⚠️  Some issues detected")

if __name__ == "__main__":
    asyncio.run(main())
