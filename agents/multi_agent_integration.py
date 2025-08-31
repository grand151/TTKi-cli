"""
TTKi Multi-Agent System Integration
Integrates PlannerAgent with existing TTKi infrastructure
"""
import asyncio
import logging
from typing import Dict, Any, Optional

# Import existing TTKi components
from agent_service import TTKiAgent
from agents.planner_agent import PlannerAgent
from agents.base_agent import Task, TaskType, TaskPriority

# Import Vision System if available
try:
    from ttki_vision import ttki_vision
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

logger = logging.getLogger(__name__)

class TTKiMultiAgentSystem:
    """
    TTKi Multi-Agent System
    Integruje PlannerAgent z istniejącą infrastrukturą TTKi
    """
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.legacy_agent = TTKiAgent()  # Zachowaj kompatybilność
        self.initialized = False
        
        # Initialize system
        asyncio.create_task(self._initialize_system())
    
    async def _initialize_system(self):
        """Inicjalizuje system multi-agent"""
        try:
            # Register legacy agent as specialized agent
            # self.planner.register_agent(self.legacy_agent)  # TODO: Adapter needed
            
            self.initialized = True
            logger.info("TTKi Multi-Agent System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Multi-Agent System: {str(e)}")
    
    async def process_user_request(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Główny punkt wejściowy dla żądań użytkownika
        Używa PlannerAgent jako intelligent entry point
        """
        if not self.initialized:
            # Fallback to legacy system
            logger.warning("Multi-Agent System not initialized, using legacy mode")
            return await self._legacy_process(user_input, context)
        
        try:
            # Create task from user input
            task = Task(
                id="user_request_001",
                type=TaskType.PLANNING,
                description=user_input,
                priority=TaskPriority.HIGH,
                parameters=context or {}
            )
            
            # Execute through PlannerAgent
            result = await self.planner.execute_task(task)
            
            return {
                'success': result.success,
                'result': result.result,
                'error': result.error,
                'duration': result.duration,
                'agent_type': 'multi_agent_system',
                'execution_plan': result.result.get('plan') if result.success else None
            }
            
        except Exception as e:
            logger.error(f"Error in multi-agent processing: {str(e)}")
            # Fallback to legacy system
            return await self._legacy_process(user_input, context)
    
    async def _legacy_process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Fallback do legacy systemu"""
        try:
            result = await self.legacy_agent.execute_task(user_input, context)
            return result
        except Exception as e:
            logger.error(f"Legacy system also failed: {str(e)}")
            return {
                'success': False,
                'error': f"Both multi-agent and legacy systems failed: {str(e)}",
                'result': None
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Zwraca status systemu"""
        if self.initialized:
            return self.planner.get_system_status()
        else:
            return {
                'status': 'legacy_mode',
                'multi_agent_initialized': False,
                'legacy_agent_available': True
            }
    
    async def analyze_task_complexity(self, user_input: str) -> Dict[str, Any]:
        """Analizuje złożoność zadania użytkownika"""
        tasks = self.planner.task_router.decompose_complex_task(user_input)
        
        return {
            'original_request': user_input,
            'subtasks_count': len(tasks),
            'estimated_duration': sum(task.estimated_duration for task in tasks),
            'task_types': [task.type.value for task in tasks],
            'complexity_indicators': {
                'multi_step': len(tasks) > 1,
                'requires_planning': any(task.type == TaskType.PLANNING for task in tasks),
                'requires_vision': any(task.type == TaskType.VISION_ANALYSIS for task in tasks),
                'requires_coding': any(task.type == TaskType.CODE_GENERATION for task in tasks)
            }
        }

# Global instance for backward compatibility
multi_agent_system = TTKiMultiAgentSystem()

# Compatibility functions for existing code
async def process_user_request(user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Compatibility function for existing TTKi code"""
    return await multi_agent_system.process_user_request(user_input, context)

def get_agent_status() -> Dict[str, Any]:
    """Compatibility function for agent status"""
    return multi_agent_system.get_system_status()
