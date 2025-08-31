#!/usr/bin/env python3
"""
Test JSON blocks parsing specifically
"""
import json
import re

def test_json_blocks(text):
    """Test JSON blocks parsing"""
    print(f"Testing JSON blocks in: '{text}'")
    
    if "```json" in text:
        print("Found ```json blocks")
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        print(f"Found {len(json_blocks)} JSON blocks")
        
        for i, block in enumerate(json_blocks):
            print(f"Block {i}: '{block}'")
            try:
                calls = json.loads(block)
                if isinstance(calls, dict):
                    calls = [calls]
                print(f"Parsed calls: {calls}")
                
                for call in calls:
                    if 'name' in call and 'parameters' in call:
                        func_name = call['name']
                        params = call['parameters']
                        print(f"Found function: {func_name} with params: {params}")
                        
                        if func_name in ['message', 'text', 'response', 'reply']:
                            message_text = params.get('text', params.get('content', str(params)))
                            print(f"WOULD EMIT: 🤖 TTKi: {message_text}")
                            return "HANDLED_AS_MESSAGE"
                        else:
                            return f"FUNCTION_CALL: {func_name}"
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
        
        return "JSON_BLOCKS_PROCESSED"
    else:
        print("No JSON blocks found")
        return "NO_JSON_BLOCKS"

# Test the problematic case
test_case = "```json\n{\"name\": \"message\", \"parameters\": {\"text\": \"Witaj!\"}}\n```"
print("="*60)
result = test_json_blocks(test_case)
print(f"Result: {result}")
