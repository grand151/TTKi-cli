"""TTKi AI application module.

This file loads the prompt and function definitions for the TTKi AI system.
"""

from __future__ import annotations

import os
import sys
import json
import re
import subprocess
import shlex
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Callable

from flask import Flask, render_template, make_response

# Import Multi-Agent System with fallback to legacy
try:
    from agents.multi_agent_integration import multi_agent_system, process_user_request
    MULTI_AGENT_AVAILABLE = True
    print("TTKi Multi-Agent System initialized")
except ImportError:
    MULTI_AGENT_AVAILABLE = False
    # Fallback to legacy agent service
    try:
        from agent_service import ttki_agent
        AGENT_SERVICE_AVAILABLE = True
        print("Using legacy agent service")
    except ImportError:
        AGENT_SERVICE_AVAILABLE = False
        print("No agent system available - running in basic mode")
from flask_socketio import SocketIO

ROOT = Path(__file__).parent


def load_text_file(filename: str, fallback: str = "Plik niedostępny") -> str:
    # Sprawdź w folderze config/ 
    config_path = ROOT / "config" / filename
    if config_path.exists():
        try:
            return config_path.read_text(encoding="utf-8")
        except Exception:
            pass
    
    # Fallback do root folder (backward compatibility)
    root_path = ROOT / filename
    if root_path.exists():
        try:
            return root_path.read_text(encoding="utf-8")
        except Exception:
            pass
    
    return fallback


PROMPT_TEXT = load_text_file("prompt.txt", "# TTKi prompt not found.")
FUNCTIONS_TEXT = load_text_file("functions.txt", "{}")


def extract_json_objects(text: str) -> List[Dict]:
    """Extract JSON objects from text that may contain markdown and other content."""
    objs: List[Dict] = []
    
    # Szukamy JSON bloków w markdown
    import re
    json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    
    for block in json_blocks:
        # Szukamy obiektów JSON w bloku - każdy może być w osobnej linii
        lines = block.strip().split('\n')
        current_obj = ""
        brace_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            current_obj += line
            brace_count += line.count('{') - line.count('}')
            
            # Gdy nawiasy się zrównoważą, mamy kompletny obiekt
            if brace_count == 0 and current_obj.strip():
                try:
                    obj = json.loads(current_obj.strip())
                    if isinstance(obj, dict):
                        objs.append(obj)
                except json.JSONDecodeError:
                    pass
                current_obj = ""
    
    return objs


def ttki_shell_exec(id: str = "", exec_dir: str = "", command: str = "") -> str:
    if not command:
        return ""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        return (result.stdout or "") + (result.stderr or "")
    except Exception as e:
        return f"shell_exec error: {e}"


def ttki_message_notify_user(text: str, attachments: Optional[List[str]] = None) -> str:
    if attachments:
        return f"Notify user: {text} (attachments: {attachments})"
    return f"Notify user: {text}"


def shell_exec(command: str, exec_dir: str = "/tmp") -> str:
    """Execute shell command and return result"""
    try:
        import os
        original_dir = os.getcwd()
        if exec_dir and os.path.exists(exec_dir):
            os.chdir(exec_dir)
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        
        os.chdir(original_dir)
        
        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        if result.stderr:
            output += f"Errors:\n{result.stderr}\n"
        
        return output
    except Exception as e:
        return f"Shell execution error: {e}"


def message_notify_user(text: str, attachments=None) -> str:
    """Notify user with message"""
    return f"Notification: {text}"


# =============================================================================
# FILE OPERATIONS - Core AI Agent functionality
# =============================================================================

def file_read(file: str, start_line: int = None, end_line: int = None, sudo: bool = False) -> str:
    """Read file content with optional line range"""
    try:
        if not os.path.exists(file):
            return f"Error: File {file} does not exist"
        
        if sudo:
            # For sudo operations, use shell command
            cmd = f"sudo cat '{file}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return f"Error reading file with sudo: {result.stderr}"
            content = result.stdout
        else:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        
        lines = content.splitlines()
        
        # Handle line range
        if start_line is not None or end_line is not None:
            start = start_line if start_line is not None else 0
            end = end_line if end_line is not None else len(lines)
            
            # Handle negative indices (from end)
            if start < 0:
                start = max(0, len(lines) + start)
            if end < 0:
                end = max(0, len(lines) + end)
                
            lines = lines[start:end]
        
        return '\n'.join(lines)
        
    except Exception as e:
        return f"Error reading file {file}: {e}"


def file_write(file: str, content: str, append: bool = False, leading_newline: bool = None, 
               trailing_newline: bool = True, sudo: bool = False) -> str:
    """Write content to file with various options"""
    try:
        # Handle newlines
        if leading_newline is None:
            leading_newline = append  # Default: add leading newline in append mode
            
        final_content = content
        if leading_newline:
            final_content = '\n' + final_content
        if trailing_newline:
            final_content = final_content + '\n'
        
        if sudo:
            # For sudo operations, use shell command
            mode = '>>' if append else '>'
            cmd = f"echo {shlex.quote(final_content)} {mode} '{file}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return f"Error writing file with sudo: {result.stderr}"
            return f"Successfully wrote to {file} (sudo)"
        else:
            mode = 'a' if append else 'w'
            with open(file, mode, encoding='utf-8') as f:
                f.write(final_content)
            return f"Successfully wrote to {file}"
            
    except Exception as e:
        return f"Error writing file {file}: {e}"


def file_str_replace(file: str, old_str: str, new_str: str, sudo: bool = False) -> str:
    """Replace string in file"""
    try:
        if not os.path.exists(file):
            return f"Error: File {file} does not exist"
        
        # Read current content
        if sudo:
            cmd = f"sudo cat '{file}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return f"Error reading file with sudo: {result.stderr}"
            content = result.stdout
        else:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Check if old_str exists
        if old_str not in content:
            return f"Error: String not found in {file}"
        
        # Replace content
        new_content = content.replace(old_str, new_str)
        
        # Write back
        if sudo:
            cmd = f"echo {shlex.quote(new_content)} > '{file}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return f"Error writing file with sudo: {result.stderr}"
            return f"Successfully replaced string in {file} (sudo)"
        else:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f"Successfully replaced string in {file}"
            
    except Exception as e:
        return f"Error replacing string in {file}: {e}"


def message_ask_user(text: str, attachments=None, suggest_user_takeover: str = "none") -> str:
    """Ask user a question and wait for response"""
    # In this implementation, we'll just return the question
    # Real implementation would wait for user response via Socket.IO
    return f"Question for user: {text}"


def idle() -> str:
    """Indicate completion of all tasks"""
    return "All tasks completed. Entering idle state."


# =============================================================================
# VNC BRIDGE - Execute commands in VNC Desktop
# =============================================================================

def vnc_shell_exec(command: str, working_dir: str = "/home/kali/Desktop") -> str:
    """Execute command in VNC desktop environment via Docker exec"""
    try:
        print(f"Executing VNC command: {command}")
        
        # Use docker exec to run command in VNC container
        docker_cmd = [
            "docker", "exec", 
            "-w", "/headless",  # VNC container working directory  
            "-e", "DISPLAY=:1",  # Set display for GUI apps
            "ttki-vnc",  # Container name
            "bash", "-c", command
        ]
        
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = f"🖥️ VNC Desktop Command: {command}\n"
        output += f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        if result.stderr:
            output += f"Errors:\n{result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"VNC command timeout: {command}"
    except Exception as e:
        return f"VNC command error: {e}"


def desktop_create_folder(folder_name: str, path: str = "/headless/Desktop") -> str:
    """Create folder on VNC desktop"""
    folder_path = f"{path}/{folder_name}"
    return vnc_shell_exec(f"mkdir -p '{folder_path}' && ls -la '{path}'")


def desktop_create_file(file_name: str, content: str = "", path: str = "/headless/Desktop") -> str:
    """Create file on VNC desktop"""
    file_path = f"{path}/{file_name}"
    if content:
        return vnc_shell_exec(f"echo {shlex.quote(content)} > '{file_path}' && ls -la '{path}'")
    else:
        return vnc_shell_exec(f"touch '{file_path}' && ls -la '{path}'")


def desktop_list_files(path: str = "/headless/Desktop") -> str:
    """List files on VNC desktop"""
    return vnc_shell_exec(f"ls -la '{path}'")


def desktop_open_app(app_name: str) -> str:
    """Open application on VNC desktop"""
    return vnc_shell_exec(f"DISPLAY=:1 nohup {app_name} > /dev/null 2>&1 & sleep 1 && echo 'Application {app_name} started'")


# Tool functions mapping
TOOL_FUNCTIONS = {
    # Core functions
    "shell_exec": shell_exec,
    "message_notify_user": message_notify_user,
    
    # File operations - NOWE!
    "file_read": file_read,
    "file_write": file_write, 
    "file_str_replace": file_str_replace,
    
    # Messaging
    "message_ask_user": message_ask_user,
    "idle": idle,
    
    # VNC Desktop Integration - NOWE!
    "vnc_shell_exec": vnc_shell_exec,
    "desktop_create_folder": desktop_create_folder,
    "desktop_create_file": desktop_create_file,
    "desktop_list_files": desktop_list_files,
    "desktop_open_app": desktop_open_app,
}


def safe_configure_gemini() -> Tuple[Any, Optional[str]]:
    try:
        import google.generativeai as genai
    except Exception:
        return None, "google.generativeai not installed"

    # Domyślny klucz API jeśli nie ma zmiennej środowiskowej
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDIiTijoYVlpAMgTjvR4VTRgfguHGo5SVE")
    if not api_key:
        return None, "GEMINI_API_KEY not set"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model, None
    except Exception as e:
        return None, str(e)


MODEL, MODEL_ERR = safe_configure_gemini()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET", "dev-secret")
socketio = SocketIO(app)


@app.route("/")
def index():
    response = app.make_response(render_template("ai_interface.html"))
    response.headers['Permissions-Policy'] = 'fullscreen=*, clipboard-read=*, clipboard-write=*'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.route("/landing")
def landing():
    response = app.make_response(render_template("index.html"))
    response.headers['Permissions-Policy'] = 'fullscreen=*, clipboard-read=*, clipboard-write=*'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.route("/health")
def health():
    """Health check endpoint for Docker"""
    status = {
        "status": "healthy",
        "version": "0.2.1",
        "model_available": MODEL is not None,
        "api_key_configured": bool(os.environ.get("GEMINI_API_KEY"))
    }
    return status


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@socketio.on("message")
def handle_message(message):
    print(f"Received message: {message}")
    
    if MODEL is None:
        print(f"Model not available: {MODEL_ERR}")
        socketio.emit("message", f"Gemini model not available: {MODEL_ERR}")
        return
    
    # Sprawdzenie klucza API
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No GEMINI_API_KEY found")
        socketio.emit("message", "Error: GEMINI_API_KEY not set. Please set your API key first.")
        return
        
    try:
        # Build enhanced prompt with VNC functions
        vnc_functions_docs = """
        
## VNC Desktop Integration Functions

You have special functions to interact with the VNC desktop environment:

```json
{"name": "desktop_create_folder", "parameters": {"folder_name": "MyFolder", "path": "/headless/Desktop"}}
```
Creates a folder on the VNC desktop. User will see it in the right panel.

```json  
{"name": "desktop_create_file", "parameters": {"file_name": "test.txt", "content": "Hello World", "path": "/headless/Desktop"}}
```
Creates a file on the VNC desktop with content.

```json
{"name": "desktop_list_files", "parameters": {"path": "/headless/Desktop"}}
```  
Lists files on the VNC desktop.

```json
{"name": "vnc_shell_exec", "parameters": {"command": "firefox", "working_dir": "/headless"}}
```
Executes commands directly in the VNC desktop environment.

```json
{"name": "desktop_open_app", "parameters": {"app_name": "firefox"}}
```
Opens applications in the VNC desktop.

IMPORTANT: When user asks to create folders/files "on desktop" or "na pulpicie", use these VNC functions instead of regular shell_exec!
The user has a VNC desktop in the right panel - use desktop_* functions to interact with it.

Example responses for desktop operations:
- "Create folder X" → use desktop_create_folder
- "Make file Y" → use desktop_create_file  
- "Open browser" → use desktop_open_app
- "List desktop" → use desktop_list_files

"""
        
        enhanced_prompt = PROMPT_TEXT + vnc_functions_docs + "\n\nUser message: " + str(message)
        print("Generating response with VNC functions...")
        response = MODEL.generate_content(enhanced_prompt)
        print(f"Response received: {response}")
        
        # Sprawdzenie czy odpowiedź jest poprawna
        if not response.candidates:
            print("No response candidates")
            socketio.emit("message", "No response candidates from model")
            return
            
        candidate = response.candidates[0]
        finish_reason = getattr(candidate, 'finish_reason', None)
        print(f"Finish reason: {finish_reason}")
        
        # Sprawdzenie finish_reason
        if finish_reason and finish_reason != 1:  # 1 = STOP (normal completion)
            reason_map = {
                2: "MAX_TOKENS", 3: "SAFETY", 4: "RECITATION", 
                5: "OTHER", 12: "BLOCKED_SAFETY_FILTER"
            }
            reason_name = reason_map.get(finish_reason, f"UNKNOWN({finish_reason})")
            print(f"Response blocked: {reason_name}")
            socketio.emit("message", f"Response blocked by Gemini: {reason_name}. Try rephrasing your message.")
            return
        
        # Pobieranie tekstu odpowiedzi
        text = ""
        if hasattr(response, 'text') and response.text:
            text = response.text.strip()
        elif candidate.content and candidate.content.parts:
            text = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text')).strip()
        
        print(f"Response text: {text[:100]}...")
        
        if not text:
            print("Empty response text")
            socketio.emit("message", "Empty response from model")
            return
            
        # Parse function calls - handle multiple formats
        try:
            # NEW: Try JSON inside function_calls tags
            if "<function_calls>" in text and "</function_calls>" in text:
                print("Parsing function_calls with potential JSON inside")
                func_calls_pattern = r'<function_calls>(.*?)</function_calls>'
                func_calls_match = re.search(func_calls_pattern, text, re.DOTALL)
                
                if func_calls_match:
                    content = func_calls_match.group(1).strip()
                    
                    # Try to parse as JSON first
                    try:
                        call_data = json.loads(content)
                        if isinstance(call_data, dict) and 'name' in call_data and 'parameters' in call_data:
                            func_name = call_data['name']
                            params = call_data['parameters']
                            
                            func = TOOL_FUNCTIONS.get(func_name)
                            if func:
                                try:
                                    print(f"Calling VNC function: {func_name} with params: {params}")
                                    result = func(**params)
                                    socketio.emit("message", f"🔧 {func_name}: {result}")
                                    return
                                except Exception as e:
                                    socketio.emit("message", f"❌ Error in {func_name}: {e}")
                                    return
                            else:
                                socketio.emit("message", f"❓ Unknown function: {func_name}")
                                return
                    except json.JSONDecodeError:
                        # Not JSON, continue to XML parsing
                        pass
            
            # Try JSON blocks format
            if "```json" in text:
                print("Parsing JSON function calls")
                json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                
                for block in json_blocks:
                    try:
                        calls = json.loads(block)
                        if isinstance(calls, dict):
                            calls = [calls]  # Single call
                        
                        for call in calls:
                            if 'name' in call and 'parameters' in call:
                                func_name = call['name']
                                params = call['parameters']
                                
                                func = TOOL_FUNCTIONS.get(func_name)
                                if func:
                                    try:
                                        print(f"Calling function: {func_name} with params: {params}")
                                        result = func(**params)
                                        socketio.emit("message", f"🔧 {func_name}: {result}")
                                    except Exception as e:
                                        socketio.emit("message", f"❌ Error in {func_name}: {e}")
                                else:
                                    socketio.emit("message", f"❓ Unknown function: {func_name}")
                    except json.JSONDecodeError as e:
                        print(f"JSON parse error: {e}")
                        continue
                
                # If we processed JSON calls, return
                if json_blocks:
                    return
            
            # Try XML format: <function_calls><invoke name="..."><parameter>...</parameter></invoke></function_calls>
            if "<function_calls>" in text and "<invoke" in text:
                print("Parsing XML function calls")
                try:
                    # Extract function_calls section
                    func_calls_pattern = r'<function_calls>(.*?)</function_calls>'
                    func_calls_match = re.search(func_calls_pattern, text, re.DOTALL)
                    
                    if func_calls_match:
                        xml_content = f"<function_calls>{func_calls_match.group(1)}</function_calls>"
                        root = ET.fromstring(xml_content)
                        
                        for invoke_tag in root.findall("invoke"):
                            func_name = invoke_tag.get("name")
                            if not func_name:
                                continue
                                
                            params = {}
                            for param_tag in invoke_tag.findall("parameter"):
                                param_name = param_tag.get("name")
                                param_value = param_tag.text or ""
                                if param_name:
                                    params[param_name] = param_value
                            
                            func = TOOL_FUNCTIONS.get(func_name)
                            if func:
                                try:
                                    print(f"Calling function: {func_name} with params: {params}")
                                    result = func(**params)
                                    socketio.emit("message", f"🔧 {func_name}: {result}")
                                except Exception as e:
                                    socketio.emit("message", f"❌ Error in {func_name}: {e}")
                            else:
                                socketio.emit("message", f"❓ Unknown function: {func_name}")
                        return
                except ET.ParseError as e:
                    print(f"XML parse error: {e}")
            
            # LEGACY: Try old format: <function_calls><call><tool_code>...</tool_code></call></function_calls>
            if "<function_calls>" in text and "<call>" in text:
                print("Parsing legacy tool_code format")
                
                # Extract tool_code content
                tool_code_pattern = r'<tool_code>(.*?)</tool_code>'
                matches = re.findall(tool_code_pattern, text, re.DOTALL)
                
                for code in matches:
                    code = code.strip()
                    print(f"Executing tool code: {code}")
                    
                    # Parse different function call patterns
                    if 'shell_exec(' in code:
                        # Extract command from shell_exec(command="...")
                        cmd_pattern = r'shell_exec\(\s*command\s*=\s*["\']([^"\']+)["\']'
                        cmd_match = re.search(cmd_pattern, code)
                        if cmd_match:
                            command = cmd_match.group(1)
                            result = shell_exec(command)
                            socketio.emit("message", f"Shell: {command}\n{result}")
                            continue
                    
                    if 'shell(' in code:
                        # Handle simple shell(command="...") format
                        cmd_pattern = r'shell\(\s*(?:command\s*=\s*)?["\']([^"\']+)["\']'
                        cmd_match = re.search(cmd_pattern, code)
                        if cmd_match:
                            command = cmd_match.group(1)
                            result = shell_exec(command)
                            socketio.emit("message", f"Shell: {command}\n{result}")
                            continue
                    
                    if 'message_notify_user(' in code:
                        # Extract message from message_notify_user(text="...")
                        msg_pattern = r'message_notify_user\(\s*(?:text\s*=\s*)?["\']([^"\']+)["\']'
                        msg_match = re.search(msg_pattern, code)
                        if msg_match:
                            message = msg_match.group(1)
                            socketio.emit("message", f"AI: {message}")
                            continue
                    
                    # Try to execute as Python code (for print statements etc.)
                    if code.startswith('print('):
                        try:
                            # Create safe environment for execution
                            safe_globals = {
                                'shell_exec': shell_exec,
                                'message_notify_user': message_notify_user,
                                'file_read': file_read,
                                'file_write': file_write,
                                'file_str_replace': file_str_replace,
                                'shell': lambda command: shell_exec(command),
                                'print': lambda *args: socketio.emit("message", " ".join(str(arg) for arg in args))
                            }
                            exec(code, safe_globals)
                        except Exception as e:
                            socketio.emit("message", f"Execution error: {e}")
                        continue
                    
                    # Default: treat as regular message
                    socketio.emit("message", f"AI: {code}")
                return
            
            # If no function calls found, treat as regular text response
            socketio.emit("message", f"🤖 TTKi: {text}")
        except Exception as e:
            print(f"Function parsing error: {e}")
            socketio.emit("message", f"Model: {text}")
            
    except Exception as e:
        print(f"Exception in handle_message: {e}")
        import traceback
        traceback.print_exc()
        socketio.emit("message", f"Error: {e}")

# ============ AGENT CONTEXT FUNCTIONS ============

def agent_execute_task(task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute task using Multi-Agent System with intelligent routing
    Enhanced with PlannerAgent as entry point
    """
    # Try Multi-Agent System first
    if MULTI_AGENT_AVAILABLE:
        try:
            import asyncio
            
            # Check if there's already an event loop
            try:
                loop = asyncio.get_running_loop()
                task_result = loop.run_until_complete(process_user_request(task, context))
            except RuntimeError:
                # No event loop, create one
                task_result = asyncio.run(process_user_request(task, context))
            
            return task_result
            
        except Exception as e:
            print(f"Multi-Agent system failed, falling back to legacy: {str(e)}")
    
    # Fallback to legacy agent service
    if AGENT_SERVICE_AVAILABLE:
        try:
            import asyncio
            
            try:
                loop = asyncio.get_running_loop()
                task_result = loop.run_until_complete(ttki_agent.execute_task(task, context))
            except RuntimeError:
                task_result = asyncio.run(ttki_agent.execute_task(task, context))
            
            return task_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Legacy agent execution failed: {str(e)}",
                "task": task
            }
    
    # No agent system available
    return {
        "success": False,
        "error": "No agent system available",
        "fallback": "Using basic functions only"
    }

def agent_get_context() -> Dict[str, Any]:
    """
    Get current agent context and state from Multi-Agent System
    Enhanced with system-wide status
    """
    # Try Multi-Agent System first
    if MULTI_AGENT_AVAILABLE:
        try:
            return {
                "success": True,
                "system_type": "multi_agent",
                "status": multi_agent_system.get_system_status(),
                "capabilities": ["intelligent_routing", "task_decomposition", "agent_coordination"]
            }
        except Exception as e:
            print(f"Multi-Agent context failed: {str(e)}")
    
    # Fallback to legacy agent
    if AGENT_SERVICE_AVAILABLE:
        try:
            return {
                "success": True,
                "system_type": "legacy_agent",
                "cursor_position": ttki_agent.get_cursor_position(),
                "recent_actions": [
                    {
                        "timestamp": action.timestamp.isoformat(),
                        "type": action.action_type.value,
                        "name": action.action_name,
                        "success": action.success
                    }
                    for action in ttki_agent.history[-5:]  # Last 5 actions
                ],
                "current_context": ttki_agent.state.active_context.value,
                "session_duration": (datetime.now() - ttki_agent.state.session_start).total_seconds()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get agent context: {str(e)}"
            }
    
    # No agent system available
    return {
        "success": False,
        "error": "No agent system available",
        "system_type": "basic_mode"
    }
                for action in ttki_agent.get_recent_actions(5)
            ],
            "memory_keys": list(ttki_agent.memory.keys()),
            "state": {
                "active_context": ttki_agent.state.active_context.value,
                "session_start": ttki_agent.state.session_start.isoformat()
            },
            "context_summary": ttki_agent.get_context_summary()
        }
    except Exception as e:
        return {"error": f"Failed to get context: {str(e)}"}

def agent_store_memory(key: str, value: str) -> Dict[str, Any]:
    """
    Store information in agent memory
    Pozwala agentowi zapamiętać ważne informacje
    """
    if not AGENT_SERVICE_AVAILABLE:
        return {"error": "Agent service not available"}
    
    try:
        ttki_agent.store_memory(key, value)
        return {
            "success": True,
            "message": f"Stored '{key}' in agent memory",
            "memory_size": len(ttki_agent.memory)
        }
    except Exception as e:
        return {"error": f"Failed to store memory: {str(e)}"}

def agent_get_memory(key: str) -> Dict[str, Any]:
    """
    Retrieve information from agent memory
    Pozwala agentowi odzyskać zapamiętane informacje
    """
    if not AGENT_SERVICE_AVAILABLE:
        return {"error": "Agent service not available"}
    
    try:
        value = ttki_agent.get_memory(key)
        return {
            "success": True,
            "key": key,
            "value": value,
            "found": value is not None
        }
    except Exception as e:
        return {"error": f"Failed to get memory: {str(e)}"}

def desktop_create_folder_with_context(folder_name: str, path: str = "/headless/Desktop") -> Dict[str, Any]:
    """
    Create folder with agent context (enhanced version)
    Używa agent service dla lepszego kontekstu
    """
    if AGENT_SERVICE_AVAILABLE:
        task = f"create folder {folder_name} on desktop at {path}"
        return agent_execute_task(task)
    else:
        # Fallback to legacy function
        return desktop_create_folder(folder_name, path)

# ============ GLOBAL AGENT INSTANCE ============
# Global agent instance that persists across function calls
_global_agent = None

def get_global_agent():
    """Get or create global agent instance"""
    global _global_agent
    if _global_agent is None and AGENT_SERVICE_AVAILABLE:
        from agent_service import TTKiAgent
        _global_agent = TTKiAgent()
    return _global_agent

def agent_execute_task_persistent(task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute task using persistent global agent instance
    Rozwiązuje problem z utratą kontekstu między wywołaniami
    """
    agent = get_global_agent()
    if agent is None:
        return {
            "success": False,
            "error": "Agent service not available",
            "fallback": "Using legacy functions"
        }
    
    try:
        # Use async event loop for agent execution
        import asyncio
        
        # Check if there's already an event loop
        try:
            loop = asyncio.get_running_loop()
            # If there is, use create_task - but for socket context, create new loop
            task_result = asyncio.new_event_loop().run_until_complete(agent.execute_task(task, context))
        except RuntimeError:
            # No event loop, create one
            task_result = asyncio.run(agent.execute_task(task, context))
        
        return task_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Agent execution failed: {str(e)}",
            "task": task
        }

def agent_get_persistent_context() -> Dict[str, Any]:
    """Get context from persistent global agent"""
    agent = get_global_agent()
    if agent is None:
        return {"error": "Agent service not available"}
    
    try:
        return {
            "success": True,
            "cursor_position": agent.get_cursor_position(),
            "recent_actions": [
                {
                    "timestamp": action.timestamp.isoformat(),
                    "type": action.action_type.value,
                    "name": action.action_name,
                    "success": action.success
                }
                for action in agent.get_recent_actions(5)
            ],
            "memory_keys": list(agent.memory.keys()),
            "state": {
                "active_context": agent.state.active_context.value,
                "session_start": agent.state.session_start.isoformat()
            },
            "context_summary": agent.get_context_summary()
        }
    except Exception as e:
        return {"error": f"Failed to get context: {str(e)}"}


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=4001, debug=True, allow_unsafe_werkzeug=True)
