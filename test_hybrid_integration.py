"""
Integration Test - Hybrid DDD + Legacy Bridge System
Tests the complete integration between FastAPI DDD and Legacy TTKi
"""
import asyncio
import logging
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemIntegrationTest:
    """Complete system integration testing"""
    
    def __init__(self):
        self.legacy_url = "http://localhost:4001"
        self.fastapi_url = "http://localhost:8000"
        
    async def test_complete_integration(self):
        """Test full system integration"""
        
        print("🧪 Starting Complete System Integration Test")
        print("=" * 60)
        
        # Test 1: Legacy TTKi availability
        legacy_available = await self.test_legacy_system()
        
        # Test 2: FastAPI system startup
        fastapi_available = await self.test_fastapi_system()
        
        # Test 3: Bridge functionality
        bridge_working = await self.test_bridge_functionality()
        
        # Test 4: Desktop operations via hybrid system
        desktop_operations = await self.test_desktop_operations()
        
        # Summary
        await self.print_summary(legacy_available, fastapi_available, bridge_working, desktop_operations)
    
    async def test_legacy_system(self):
        """Test Legacy TTKi system"""
        print("\n🔧 Testing Legacy TTKi System...")
        
        try:
            response = requests.get(self.legacy_url, timeout=5)
            if response.status_code == 200:
                print("✅ Legacy TTKi accessible: 200")
                return True
            else:
                print(f"❌ Legacy TTKi error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Legacy TTKi connection failed: {str(e)}")
            return False
    
    async def test_fastapi_system(self):
        """Test FastAPI DDD system"""
        print("\n🚀 Testing FastAPI DDD System...")
        
        try:
            response = requests.get(f"{self.fastapi_url}/api/v1/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ FastAPI DDD accessible: 200")
                print(f"   Agents: {len(data.get('agents', []))}")
                return True
            else:
                print(f"❌ FastAPI DDD error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ FastAPI DDD connection failed: {str(e)}")
            return False
    
    async def test_bridge_functionality(self):
        """Test Legacy Bridge functionality"""
        print("\n🌉 Testing Legacy Bridge...")
        
        try:
            # Test bridge via direct import
            from src.infrastructure.agents.legacy_bridge import LegacyTTKiBridge
            
            bridge = LegacyTTKiBridge()
            print(f"✅ Bridge initialized: {bridge.available}")
            
            # Test bridge operation
            result = await bridge.execute_desktop_operation("create folder test")
            print(f"✅ Bridge operation: {result.success}")
            
            return bridge.available and result.success
            
        except Exception as e:
            print(f"❌ Bridge test failed: {str(e)}")
            return False
    
    async def test_desktop_operations(self):
        """Test desktop operations via hybrid system"""
        print("\n🖥️  Testing Desktop Operations...")
        
        try:
            # Test hybrid desktop agent
            from src.infrastructure.agents.desktop_agent_hybrid import DesktopAgent
            
            agent = DesktopAgent()
            print(f"✅ Hybrid Desktop Agent initialized")
            
            # Test folder creation
            result = await agent.execute_task(
                "create folder on desktop", 
                {"folder_name": "HybridTest"}
            )
            
            print(f"✅ Desktop operation: {result.success}")
            if result.success:
                print(f"   Result: {result.data}")
            
            return result.success
            
        except Exception as e:
            print(f"❌ Desktop operations failed: {str(e)}")
            return False
    
    async def test_fastapi_desktop_endpoint(self):
        """Test desktop operations via FastAPI endpoint"""
        print("\n🔌 Testing FastAPI Desktop Endpoint...")
        
        try:
            payload = {
                "task_description": "create folder NewFolderTest",
                "agent_type": "desktop",
                "context": {"folder_name": "NewFolderTest"}
            }
            
            response = requests.post(
                f"{self.fastapi_url}/api/v1/execute",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FastAPI Desktop endpoint: {data.get('success', False)}")
                return data.get('success', False)
            else:
                print(f"❌ FastAPI Desktop endpoint error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ FastAPI Desktop endpoint failed: {str(e)}")
            return False
    
    async def print_summary(self, legacy, fastapi, bridge, desktop):
        """Print integration test summary"""
        print("\n" + "=" * 60)
        print("🎯 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 4
        passed_tests = sum([legacy, fastapi, bridge, desktop])
        
        print(f"Legacy TTKi System:      {'✅ PASS' if legacy else '❌ FAIL'}")
        print(f"FastAPI DDD System:      {'✅ PASS' if fastapi else '❌ FAIL'}")
        print(f"Legacy Bridge:           {'✅ PASS' if bridge else '❌ FAIL'}")
        print(f"Desktop Operations:      {'✅ PASS' if desktop else '❌ FAIL'}")
        
        print(f"\nResults: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL SYSTEMS INTEGRATED SUCCESSFULLY!")
            print("🚀 Ready for desktop operations via hybrid architecture")
        else:
            print("⚠️  Some integration issues detected")
            print("💡 Check individual test results above")

async def main():
    """Run integration tests"""
    tester = SystemIntegrationTest()
    await tester.test_complete_integration()

if __name__ == "__main__":
    asyncio.run(main())
