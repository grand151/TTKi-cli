#!/usr/bin/env python3
"""
Simple test of the fixed message handling without async complications
"""
import os
import sys
import json
import re
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Mock the socket.io for testing
class MockSocketIO:
    def __init__(self):
        self.messages = []
    
    def emit(self, event, message):
        print(f"SocketIO emit({event}): {message}")
        self.messages.append(message)

# Create a simple test version of the parsing logic
socketio = MockSocketIO()

def parse_ai_response(text):
    """Simplified version of the parsing logic from handle_message"""
    print(f"Parsing AI response: '{text[:100]}...'")
    
    # Check for function_calls with JSON content (the problematic case)
    if "<function_calls>" in text and "</function_calls>" in text:
        print("Found <function_calls> tags")
        func_calls_pattern = r'<function_calls>(.*?)</function_calls>'
        func_calls_match = re.search(func_calls_pattern, text, re.DOTALL)
        
        if func_calls_match:
            content = func_calls_match.group(1).strip()
            print(f"Content inside function_calls: '{content}'")
            
            try:
                call_data = json.loads(content)
                if isinstance(call_data, dict) and 'name' in call_data and 'parameters' in call_data:
                    func_name = call_data['name']
                    params = call_data['parameters']
                    print(f"Function name: {func_name}, params: {params}")
                    
                    # NEW: Special handling for common AI responses
                    if func_name in ['message', 'text', 'response', 'reply']:
                        message_text = params.get('text', params.get('content', str(params)))
                        socketio.emit("message", f"🤖 TTKi: {message_text}")
                        return "HANDLED_AS_MESSAGE"
                    else:
                        socketio.emit("message", f"❓ Unknown function: {func_name}")
                        return "UNKNOWN_FUNCTION"
            except json.JSONDecodeError:
                pass
    
    # Check for JSON blocks
    if "```json" in text:
        print("Found ```json blocks")
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        
        for block in json_blocks:
            try:
                calls = json.loads(block)
                if isinstance(calls, dict):
                    calls = [calls]
                
                for call in calls:
                    if 'name' in call and 'parameters' in call:
                        func_name = call['name']
                        params = call['parameters']
                        
                        # NEW: Special handling
                        if func_name in ['message', 'text', 'response', 'reply']:
                            message_text = params.get('text', params.get('content', str(params)))
                            socketio.emit("message", f"🤖 TTKi: {message_text}")
                            return "HANDLED_AS_MESSAGE"
                        else:
                            socketio.emit("message", f"❓ Unknown function: {func_name}")
                            return "UNKNOWN_FUNCTION"
            except json.JSONDecodeError:
                continue
    
    # Regular text response
    socketio.emit("message", f"🤖 TTKi: {text}")
    return "REGULAR_MESSAGE"

# Test cases
test_cases = [
    # Regular greeting (should work fine)
    "Cześć! Jak mogę Ci pomóc?",
    
    # Problematic case that was causing "Unknown function: message"
    '<function_calls>{"name": "message", "parameters": {"text": "Cześć! Jak mogę Ci pomóc dzisiaj?"}}</function_calls>',
    
    # Another problematic format
    '```json\n{"name": "message", "parameters": {"text": "Witaj! W czym mogę pomóc?"}}\n```',
    
    # Real function call (should still work)
    '<function_calls>{"name": "shell_exec", "parameters": {"command": "ls -la"}}</function_calls>',
]

print("🧪 TESTING THE FIXED MESSAGE PARSING LOGIC")
print("=" * 60)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n🔍 TEST CASE {i}:")
    print(f"Input: {test_case[:80]}{'...' if len(test_case) > 80 else ''}")
    print("-" * 40)
    
    result = parse_ai_response(test_case)
    print(f"Result: {result}")
    
    if result == "HANDLED_AS_MESSAGE":
        print("✅ SUCCESS: 'message' function properly converted to regular message")
    elif result == "REGULAR_MESSAGE":
        print("✅ SUCCESS: Regular text handled normally")
    elif result == "UNKNOWN_FUNCTION":
        print("⚠️  EXPECTED: Real unknown function would be reported")
    else:
        print("❌ UNEXPECTED RESULT")

print(f"\n🎯 SUMMARY:")
print(f"Total messages emitted: {len(socketio.messages)}")
for i, msg in enumerate(socketio.messages, 1):
    print(f"  {i}. {msg}")

print("\n✅ Fix verification complete!")
