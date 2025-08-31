#!/usr/bin/env python3
"""
TTKi Vision Test - Test dedykowanego systemu widzenia AI
Sprawdza responsywność i poprawność integracji
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_vision_system():
    """Test TTKi Vision System with dedicated AI"""
    
    print("🚀 TTKi Vision System Test - Dedicated AI Model")
    print("=" * 60)
    
    try:
        # Test 1: Import and initialize Vision AI
        print("\n📦 Test 1: Importing Vision AI Service...")
        from vision_ai_service import get_vision_ai, is_vision_ai_available
        
        vision_ai = get_vision_ai()
        status = vision_ai.get_model_status()
        
        print(f"   Vision AI Available: {status['vision_ai_available']}")
        print(f"   API Key Configured: {status['api_key_configured']}")
        print(f"   Model Type: {status['model_type']}")
        print(f"   Optimization: {status['optimization']}")
        
        # Test 2: Import TTKi Vision System
        print("\n🎯 Test 2: Importing TTKi Vision System...")
        from ttki_vision import TTKiVisionSystem
        
        vision_system = TTKiVisionSystem()
        print(f"   Vision System AI Enhanced: {vision_system.ai_enhanced}")
        print(f"   Vision AI Instance: {vision_system.vision_ai is not None}")
        
        # Test 3: Agent Service Integration
        print("\n🤖 Test 3: Testing Agent Service Integration...")
        from agent_service import get_global_agent
        
        agent = get_global_agent()
        agent_status = agent.state.__dict__
        
        print(f"   Agent State Vision Enabled: {agent_status.get('vision_enabled', False)}")
        print(f"   Agent Memory: {len(agent.memory)} items")
        
        # Test 4: Environment Configuration
        print("\n🔧 Test 4: Environment Configuration...")
        gemini_key_1 = os.environ.get('GEMINI_API_KEY')
        gemini_key_2 = os.environ.get('GEMINI_API_KEY_2')
        
        print(f"   GEMINI_API_KEY: {'✅ Set' if gemini_key_1 else '❌ Missing'}")
        print(f"   GEMINI_API_KEY_2: {'✅ Set' if gemini_key_2 else '❌ Missing'}")
        
        if gemini_key_2:
            print(f"   Dedicated Vision Model: ✅ Available")
            print(f"   Expected Responsiveness: 🚀 Enhanced")
        else:
            print(f"   Dedicated Vision Model: ⚠️ Not configured")
            print(f"   Expected Responsiveness: 🔧 Standard (shared model)")
        
        # Test 5: Mock Task Execution
        print("\n⚡ Test 5: Mock Task Execution...")
        
        test_task = "create folder TestVision"
        print(f"   Testing task: '{test_task}'")
        
        # Simulate task execution without actual VNC
        result = await agent.execute_task(test_task)
        print(f"   Task execution result: {type(result).__name__}")
        
        if isinstance(result, dict):
            print(f"   Action: {result.get('action', 'N/A')}")
            print(f"   Method: {result.get('method', result.get('verification_method', 'N/A'))}")
            
        # Test Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        vision_score = 0
        total_tests = 5
        
        if status['vision_ai_available']:
            vision_score += 1
            print("✅ Dedicated Vision AI: Working")
        else:
            print("⚠️ Dedicated Vision AI: Fallback mode")
        
        if vision_system.ai_enhanced:
            vision_score += 1
            print("✅ Enhanced Vision System: Active")
        else:
            print("🔧 Enhanced Vision System: Basic mode")
        
        if agent.state.vision_enabled:
            vision_score += 1
            print("✅ Agent Vision Integration: Enabled")
        else:
            print("⚠️ Agent Vision Integration: Disabled")
        
        if gemini_key_2:
            vision_score += 1
            print("✅ Dedicated API Key: Configured")
        else:
            print("⚠️ Dedicated API Key: Missing (using shared)")
        
        if result:
            vision_score += 1
            print("✅ Task Execution: Working")
        else:
            print("❌ Task Execution: Failed")
        
        print(f"\n🎯 Vision System Score: {vision_score}/{total_tests}")
        
        if vision_score >= 4:
            print("🚀 TTKi Vision System: EXCELLENT - Maximum responsiveness expected")
        elif vision_score >= 3:
            print("✅ TTKi Vision System: GOOD - Enhanced responsiveness")
        elif vision_score >= 2:
            print("⚠️ TTKi Vision System: BASIC - Standard functionality")
        else:
            print("❌ TTKi Vision System: ISSUES - Check configuration")
        
        print("\n💡 RECOMMENDATIONS:")
        
        if not gemini_key_2:
            print("   • Add GEMINI_API_KEY_2 to .env for dedicated vision model")
            print("   • This will increase responsiveness by offloading vision tasks")
        
        if not vision_system.ai_enhanced:
            print("   • Check OpenCV installation in container")
            print("   • Verify Vision AI service initialization")
        
        if vision_score == total_tests:
            print("   • System is optimally configured! 🎉")
            print("   • Ready for production use with maximum responsiveness")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("   • Check if all dependencies are installed")
        print("   • Verify environment variables in .env")
        print("   • Ensure containers are running")
        return False
    
    return True

if __name__ == "__main__":
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = asyncio.run(test_vision_system())
    
    if success:
        print(f"\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test completed with errors!")
        sys.exit(1)
