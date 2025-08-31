#!/usr/bin/env python3
"""
VNC Bridge - allows AI container to execute commands in VNC container
via shared volume communication
"""

import os
import json
import time
import subprocess
import threading
from pathlib import Path

BRIDGE_DIR = Path("/shared/bridge")
COMMANDS_DIR = BRIDGE_DIR / "commands"
RESULTS_DIR = BRIDGE_DIR / "results"

def ensure_bridge_dirs():
    """Create bridge directories if they don't exist"""
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Bridge directories ready: {BRIDGE_DIR}")

def execute_command_in_vnc(command_file: Path):
    """Execute command from AI in VNC container context"""
    try:
        with open(command_file, 'r') as f:
            cmd_data = json.load(f)
        
        command_id = cmd_data['id']
        command = cmd_data['command']
        working_dir = cmd_data.get('working_dir', '/home/kali/Desktop')
        
        print(f"Executing VNC command {command_id}: {command}")
        
        # Set up environment for desktop user
        env = os.environ.copy()
        env['DISPLAY'] = ':1'
        env['HOME'] = '/home/kali'
        env['USER'] = 'kali'
        
        # Execute command in VNC context
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        # Save result
        result_data = {
            'id': command_id,
            'command': command,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
        
        result_file = RESULTS_DIR / f"{command_id}.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        # Remove processed command
        command_file.unlink()
        
        print(f"Command {command_id} completed with exit code {result.returncode}")
        
    except Exception as e:
        print(f"Error executing command: {e}")
        # Save error result
        error_data = {
            'id': command_id if 'command_id' in locals() else 'unknown',
            'command': command if 'command' in locals() else 'unknown',
            'return_code': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }
        
        error_file = RESULTS_DIR / f"{error_data['id']}_error.json"
        with open(error_file, 'w') as f:
            json.dump(error_data, f, indent=2)

def monitor_commands():
    """Monitor for new commands from AI container"""
    print("Starting VNC bridge monitor...")
    
    while True:
        try:
            # Check for new command files
            for cmd_file in COMMANDS_DIR.glob("*.json"):
                execute_command_in_vnc(cmd_file)
            
            time.sleep(0.5)  # Check every 500ms
            
        except KeyboardInterrupt:
            print("VNC bridge stopping...")
            break
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    ensure_bridge_dirs()
    monitor_commands()
