"""
TTKi Agent Service - inspirowane architekturą Manus
Zapewnia trwały kontekst i pamięć między działaniami agenta
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Import TTKi Vision System
try:
    from ttki_vision import ttki_vision, InteractiveElement
    VISION_SYSTEM_AVAILABLE = True
except ImportError:
    VISION_SYSTEM_AVAILABLE = False
    print("TTKi Vision System not available - using basic mode")

logger = logging.getLogger(__name__)

class ActionType(Enum):
    BROWSER = "browser"
    DESKTOP = "desktop"
    FILE = "file"
    TERMINAL = "terminal"

@dataclass
class AgentState:
    """Trwały stan agenta - pamięta wszystko między akcjami"""
    current_url: Optional[str] = None
    current_tab_id: Optional[str] = None
    cursor_position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    active_context: ActionType = ActionType.DESKTOP
    desktop_focus: Optional[str] = None
    last_action: Optional[str] = None
    session_start: datetime = field(default_factory=datetime.now)
    # TTKi Vision System state
    last_detected_elements: List[Dict] = field(default_factory=list)
    vision_enabled: bool = VISION_SYSTEM_AVAILABLE

@dataclass
class ActionHistory:
    """Historia pojedynczej akcji"""
    timestamp: datetime
    action_type: ActionType
    action_name: str
    parameters: Dict[str, Any]
    result: Any
    success: bool
    context_before: Dict[str, Any]
    context_after: Dict[str, Any]

class TTKiAgent:
    """
    Główny Agent Service dla TTKi
    Inspirowany architekturą Manus Agent class
    """
    
    def __init__(self):
        self.state = AgentState()
        self.history: List[ActionHistory] = []
        self.memory: Dict[str, Any] = {}
        
    async def execute_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Główna metoda wykonywania zadań
        Zachowuje kontekst między akcjami jak w Manus
        """
        logger.info(f"Agent executing task: {task}")
        
        # Zachowaj kontekst przed akcją
        context_before = self._capture_context()
        
        try:
            # Analiza zadania i wybór kontekstu
            action_type = self._determine_action_type(task)
            self.state.active_context = action_type
            
            # Wykonanie zadania w odpowiednim kontekście
            if action_type == ActionType.BROWSER:
                result = await self._execute_browser_task(task, context)
            elif action_type == ActionType.DESKTOP:
                result = await self._execute_desktop_task(task, context)
            elif action_type == ActionType.FILE:
                result = await self._execute_file_task(task, context)
            elif action_type == ActionType.TERMINAL:
                result = await self._execute_terminal_task(task, context)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
            
            # Zachowaj historię
            context_after = self._capture_context()
            self._record_action(action_type, task, context or {}, result, True, context_before, context_after)
            
            return {
                "success": True,
                "result": result,
                "context": context_after,
                "history_id": len(self.history) - 1
            }
            
        except Exception as e:
            logger.error(f"Agent task failed: {str(e)}")
            context_after = self._capture_context()
            self._record_action(action_type, task, context or {}, str(e), False, context_before, context_after)
            
            return {
                "success": False,
                "error": str(e),
                "context": context_after
            }
    
    def _determine_action_type(self, task: str) -> ActionType:
        """Inteligentne określanie typu akcji na podstawie zadania"""
        task_lower = task.lower()
        
        # Browser keywords
        if any(keyword in task_lower for keyword in ['http', 'www', 'website', 'browser', 'navigate', 'click button', 'fill form']):
            return ActionType.BROWSER
            
        # File operations
        if any(keyword in task_lower for keyword in ['file', 'read', 'write', 'create file', 'edit', 'save']):
            return ActionType.FILE
            
        # Terminal operations  
        if any(keyword in task_lower for keyword in ['command', 'terminal', 'shell', 'run', 'execute']):
            return ActionType.TERMINAL
            
        # Default to desktop for everything else
        return ActionType.DESKTOP
    
    async def _execute_desktop_task(self, task: str, context: Optional[Dict]) -> Any:
        """Wykonanie zadania na pulpicie z TTKi Vision System"""
        
        logger.info(f"🖥️ TTKi Agent: Executing desktop task with vision: {task}")
        
        # Use TTKi Vision System if available
        if VISION_SYSTEM_AVAILABLE and self.state.vision_enabled:
            return await self._execute_desktop_task_with_vision(task, context)
        else:
            return await self._execute_desktop_task_legacy(task, context)
    
    async def _execute_desktop_task_with_vision(self, task: str, context: Optional[Dict]) -> Any:
        """
        Wykonanie zadania z TTKi Vision System
        Implementuje inteligentną percepcję jak w opisanej perspektywie agenta
        """
        logger.info("👁️ Using TTKi Vision System for task execution")
        
        try:
            # KROK 1: Percepcja - "otwarcie oczu" agenta
            logger.info("🔍 Phase 1: Perceiving interactive elements...")
            elements_before = ttki_vision.perceive_interactive_elements(task)
            
            # Zapisz wykryte elementy w stanie agenta
            self.state.last_detected_elements = ttki_vision.get_elements_as_json()
            
            logger.info(f"📋 Detected {len(elements_before)} interactive elements")
            
            # KROK 2: Heurystyka decyzyjna - znajdź cel
            logger.info("🎯 Phase 2: Finding target element for task...")
            target_element = ttki_vision.find_target_for_task(task, elements_before)
            
            if target_element is None:
                logger.warning("❌ No suitable target element found")
                return await self._execute_desktop_task_legacy(task, context)
            
            logger.info(f"🎪 Found target: {target_element.element_type.value} at ({target_element.center_x}, {target_element.center_y})")
            
            # KROK 3: Wykonanie akcji
            logger.info("⚡ Phase 3: Executing action on target...")
            action_result = await self._execute_vision_action(target_element, task)
            
            # KROK 4: Pętla sprzężenia zwrotnego - weryfikacja
            logger.info("🔄 Phase 4: Verifying action success...")
            verification_result = ttki_vision.verify_action_success(elements_before, task)
            
            # Update agent cursor position
            self.state.cursor_position = {
                "x": target_element.center_x,
                "y": target_element.center_y
            }
            
            # Store successful patterns
            if verification_result["success"]:
                self.store_memory("last_successful_action", {
                    "task": task,
                    "target_type": target_element.element_type.value,
                    "coordinates": (target_element.center_x, target_element.center_y),
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "action": "vision_guided_action",
                "task": task,
                "target_element": {
                    "type": target_element.element_type.value,
                    "position": (target_element.center_x, target_element.center_y),
                    "size": (target_element.width, target_element.height),
                    "confidence": target_element.confidence
                },
                "action_result": action_result,
                "verification": verification_result,
                "elements_detected": len(elements_before),
                "cursor_position": self.state.cursor_position,
                "success": verification_result["success"]
            }
            
        except Exception as e:
            logger.error(f"❌ TTKi Vision System failed: {e}")
            logger.info("🔄 Falling back to legacy method...")
            return await self._execute_desktop_task_legacy(task, context)
    
    async def _execute_vision_action(self, target: InteractiveElement, task: str) -> Dict:
        """Wykonuje akcję na znalezionym elemencie"""
        from app import vnc_shell_exec
        
        if "create folder" in task.lower() or "utwórz folder" in task.lower():
            # For folder creation, right-click on desktop area
            logger.info(f"🖱️ Right-clicking at ({target.center_x}, {target.center_y}) for context menu")
            
            # Right-click to open context menu
            right_click_cmd = f'DISPLAY=:1 xdotool mousemove {target.center_x} {target.center_y} && xdotool click 3'
            result = vnc_shell_exec(right_click_cmd)
            
            # Wait for context menu to appear
            import time
            time.sleep(1)
            
            # Try to click on "Create Folder" or similar option
            # This is simplified - in real implementation we'd detect the menu
            folder_option_cmd = f'DISPLAY=:1 xdotool key alt+f && xdotool key n'
            menu_result = vnc_shell_exec(folder_option_cmd)
            
            return {
                "right_click": result,
                "menu_action": menu_result,
                "coordinates": (target.center_x, target.center_y)
            }
        else:
            # Standard left-click action
            logger.info(f"🖱️ Left-clicking at ({target.center_x}, {target.center_y})")
            
            click_cmd = f'DISPLAY=:1 xdotool mousemove {target.center_x} {target.center_y} && xdotool click 1'
            result = vnc_shell_exec(click_cmd)
            
            return {
                "click": result,
                "coordinates": (target.center_x, target.center_y)
            }
    
    async def _execute_desktop_task_legacy(self, task: str, context: Optional[Dict]) -> Any:
        """Wykonanie zadania bez Vision System (legacy mode)"""
        logger.info("🔧 Using legacy desktop execution")
        
        # Agent ma własny pointer na pulpicie
        if "create folder" in task.lower() or "utwórz folder" in task.lower():
            folder_name = self._extract_folder_name(task)
            path = self._extract_path(task) or "/headless/Desktop"
            
            # Update internal pointer position
            self.state.cursor_position = {"x": 400, "y": 300}  # Center of desktop
            
            # Import and use existing VNC function
            from app import vnc_shell_exec
            command = f'mkdir -p "{path}/{folder_name}"'
            result = vnc_shell_exec(command)
            
            # Store in memory for future reference
            self.store_memory("last_created_folder", folder_name)
            self.store_memory("last_folder_path", f"{path}/{folder_name}")
            
            return {
                "action": "create_folder",
                "folder_name": folder_name,
                "path": path,
                "full_path": f"{path}/{folder_name}",
                "cursor_position": self.state.cursor_position,
                "result": result,
                "method": "legacy"
            }
        else:
            # Fallback to VNC command
            from app import vnc_shell_exec
            return vnc_shell_exec(task)
    
    async def _execute_file_task(self, task: str, context: Optional[Dict]) -> Any:
        """Wykonanie operacji na plikach"""
        if "read" in task.lower():
            filepath = self._extract_filepath(task)
            from app import file_read
            return file_read(filepath)
        elif "write" in task.lower():
            filepath = self._extract_filepath(task)
            content = self._extract_content(task)
            from app import file_write
            return file_write(filepath, content)
        return "File operation not recognized"
    
    async def _execute_terminal_task(self, task: str, context: Optional[Dict]) -> Any:
        """Wykonanie komendy w terminalu"""
        command = self._extract_command(task)
        from app import vnc_shell_exec
        return vnc_shell_exec(command)
    
    async def _execute_browser_task(self, task: str, context: Optional[Dict]) -> Any:
        """Placeholder for browser tasks - to be implemented with Playwright"""
        return "Browser functionality to be implemented with Playwright"
    
    def _capture_context(self) -> Dict[str, Any]:
        """Capture current state for history"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cursor_position": self.state.cursor_position.copy(),
            "active_context": self.state.active_context.value,
            "current_url": self.state.current_url,
            "desktop_focus": self.state.desktop_focus,
            "memory_size": len(self.memory)
        }
    
    def _record_action(self, action_type: ActionType, action_name: str, 
                      parameters: Dict, result: Any, success: bool,
                      context_before: Dict, context_after: Dict):
        """Record action in history"""
        history_item = ActionHistory(
            timestamp=datetime.now(),
            action_type=action_type,
            action_name=action_name,
            parameters=parameters,
            result=result,
            success=success,
            context_before=context_before,
            context_after=context_after
        )
        self.history.append(history_item)
        
        # Keep only last 50 actions to prevent memory issues
        if len(self.history) > 50:
            self.history = self.history[-50:]
    
    def get_memory(self, key: str) -> Any:
        """Retrieve from agent memory"""
        return self.memory.get(key)
    
    def store_memory(self, key: str, value: Any):
        """Store in agent memory"""
        self.memory[key] = value
    
    def get_recent_actions(self, count: int = 5) -> List[ActionHistory]:
        """Get recent actions for context"""
        return self.history[-count:] if self.history else []
    
    def get_cursor_position(self) -> Dict[str, int]:
        """Get current agent cursor position"""
        return self.state.cursor_position.copy()
    
    def set_cursor_position(self, x: int, y: int):
        """Update agent cursor position"""
        self.state.cursor_position = {"x": x, "y": y}
    
    def get_context_summary(self) -> str:
        """Get summary of current context for LLM"""
        recent_actions = self.get_recent_actions(3)
        summary = f"Agent context:\n"
        summary += f"- Cursor position: {self.state.cursor_position}\n"
        summary += f"- Active context: {self.state.active_context.value}\n"
        summary += f"- Recent actions:\n"
        
        for action in recent_actions:
            summary += f"  • {action.action_name} ({action.action_type.value}) - {'✓' if action.success else '✗'}\n"
        
        if self.memory:
            summary += f"- Memory: {list(self.memory.keys())}\n"
        
        return summary
    
    # Helper methods for extracting information from tasks
    def _extract_folder_name(self, task: str) -> str:
        """Extract folder name from task"""
        words = task.split()
        for i, word in enumerate(words):
            if word.lower() in ['folder', 'katalog'] and i + 1 < len(words):
                return words[i + 1]
        return "NewFolder"
    
    def _extract_path(self, task: str) -> Optional[str]:
        """Extract path from task"""
        if "desktop" in task.lower() or "pulpit" in task.lower():
            return "/headless/Desktop"
        return None
    
    def _extract_filepath(self, task: str) -> str:
        """Extract filepath from task"""
        words = task.split()
        for word in words:
            if '/' in word or '.' in word:
                return word
        return ""
    
    def _extract_content(self, task: str) -> str:
        """Extract content to write"""
        if '"' in task:
            return task.split('"')[1]
        return ""
    
    def _extract_command(self, task: str) -> str:
        """Extract command from task"""
        return task.replace("run command", "").replace("execute", "").strip()

# Global agent instance
ttki_agent = TTKiAgent()

def get_global_agent() -> TTKiAgent:
    """
    Zwraca globalną instancję agenta TTKi
    Używane przez inne moduły do dostępu do agenta
    """
    return ttki_agent
