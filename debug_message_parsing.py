#!/usr/bin/env python3
"""
Test script to debug the "Unknown function: message" issue
"""
import json
import re

def test_parsing_logic(text):
    """Test the same parsing logic as in handle_message"""
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
                    return func_name
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
    
    # Check for JSON blocks
    if "```json" in text:
        print("Found ```json blocks")
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        for block in json_blocks:
            print(f"JSON block: '{block}'")
            try:
                calls = json.loads(block)
                if isinstance(calls, dict):
                    calls = [calls]
                for call in calls:
                    if 'name' in call and 'parameters' in call:
                        func_name = call['name']
                        print(f"Found function in JSON block: {func_name}")
                        return func_name
            except json.JSONDecodeError as e:
                print(f"JSON block parse error: {e}")
    
    print("No function patterns found - should be treated as regular text")
    return None

# Test cases
test_cases = [
    "cześć",
    "hello world",
    '{"name": "message", "parameters": {}}',
    '<function_calls>{"name": "message", "parameters": {}}</function_calls>',
    "```json\n{\"name\": \"message\", \"parameters\": {}}\n```",
    "Witaj! Jak mogę Ci pomóc?",
]

for test_case in test_cases:
    print(f"\n{'='*50}")
    result = test_parsing_logic(test_case)
    if result:
        print(f"❌ PROBLEM: Would trigger 'Unknown function: {result}'")
    else:
        print("✅ OK: Would be treated as regular text")
