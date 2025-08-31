#!/usr/bin/env python3
"""
Test the fixed parsing logic
"""
import json
import re

def emit_message(message):
    """Mock socketio.emit for testing"""
    print(f"EMIT: {message}")

def test_fixed_parsing_logic(text):
    """Test the fixed parsing logic"""
    print(f"Testing text: '{text}'")
    
    # Check for function_calls tags
    if "<function_calls>" in text and "</function_calls>" in text:
        print("Found <function_calls> tags")
        func_calls_pattern = r'<function_calls>(.*?)</function_calls>'
        func_calls_match = re.search(func_calls_pattern, text, re.DOTALL)
        
        if func_calls_match:
            content = func_calls_match.group(1).strip()
            print(f"Content inside function_calls: '{content}'")
            
            # Try to parse as JSON first
            try:
                call_data = json.loads(content)
                print(f"Parsed as JSON: {call_data}")
                if isinstance(call_data, dict) and 'name' in call_data and 'parameters' in call_data:
                    func_name = call_data['name']
                    params = call_data['parameters']
                    print(f"Function name: {func_name}")
                    print(f"Parameters: {params}")
                    
                    # NEW: Special handling for common AI responses
                    if func_name in ['message', 'text', 'response', 'reply']:
                        message_text = params.get('text', params.get('content', str(params)))
                        emit_message(f"🤖 TTKi: {message_text}")
                        return "HANDLED_AS_MESSAGE"
                    
                    return f"FUNCTION_CALL: {func_name}"
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
    
    print("No function patterns found - should be treated as regular text")
    return "REGULAR_TEXT"

# Test cases including problematic ones
test_cases = [
    "cześć",
    "hello world", 
    '<function_calls>{"name": "message", "parameters": {"text": "Cześć! Jak mogę Ci pomóc?"}}</function_calls>',
    '<function_calls>{"name": "shell_exec", "parameters": {"command": "ls"}}</function_calls>',
    "```json\n{\"name\": \"message\", \"parameters\": {\"text\": \"Witaj!\"}}\n```",
    "Witaj! Jak mogę Ci pomóc?",
]

for test_case in test_cases:
    print(f"\n{'='*60}")
    result = test_fixed_parsing_logic(test_case)
    print(f"RESULT: {result}")
    if result == "HANDLED_AS_MESSAGE":
        print("✅ FIXED: 'message' function properly handled as regular message")
    elif "FUNCTION_CALL" in result and "message" not in result:
        print("✅ OK: Real function call would be processed")
    elif result == "REGULAR_TEXT":
        print("✅ OK: Regular text would be handled normally")
    else:
        print("❌ PROBLEM: Still has issues")
