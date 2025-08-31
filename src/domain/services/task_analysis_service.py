"""
Task Analysis Service - Domain service for analyzing user tasks
"""
import re
import logging
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

from ..value_objects import TaskType, TaskPriority
from ..entities import TaskEntity

logger = logging.getLogger(__name__)

@dataclass
class TaskAnalysisResult:
    """Result of task analysis"""
    task_type: TaskType
    priority: TaskPriority
    complexity_factor: float
    keywords: List[str]
    estimated_duration: float

class TaskAnalysisService:
    """
    Domain service for analyzing and categorizing user tasks
    """
    
    def __init__(self):
        self.analysis_rules = self._initialize_analysis_rules()
    
    def _initialize_analysis_rules(self) -> List[Dict[str, Any]]:
        """Initialize task analysis rules"""
        return [
            {
                'pattern': r'(screenshot|capture|analyze.*screen|what.*see|visual|image)',
                'task_type': TaskType.VISION_ANALYSIS,
                'priority': TaskPriority.HIGH,
                'keywords': ['screenshot', 'analyze', 'visual', 'see', 'screen', 'image'],
                'complexity_factor': 0.8,
                'base_duration': 2.0
            },
            {
                'pattern': r'(write.*code|create.*function|implement|generate.*script)',
                'task_type': TaskType.CODE_GENERATION,
                'priority': TaskPriority.HIGH,
                'keywords': ['write', 'create', 'implement', 'generate', 'code', 'function'],
                'complexity_factor': 1.2,
                'base_duration': 5.0
            },
            {
                'pattern': r'(create.*file|edit.*file|delete.*file|move.*file|copy.*file)',
                'task_type': TaskType.FILE_OPERATIONS,
                'priority': TaskPriority.MEDIUM,
                'keywords': ['create', 'edit', 'delete', 'move', 'copy', 'file'],
                'complexity_factor': 0.6,
                'base_duration': 1.0
            },
            {
                'pattern': r'(run.*command|execute|terminal|bash|shell|install)',
                'task_type': TaskType.TERMINAL_COMMANDS,
                'priority': TaskPriority.MEDIUM,
                'keywords': ['run', 'execute', 'terminal', 'command', 'bash', 'shell'],
                'complexity_factor': 0.7,
                'base_duration': 3.0
            },
            {
                'pattern': r'(open.*browser|navigate.*to|click.*button|fill.*form|web)',
                'task_type': TaskType.BROWSER_AUTOMATION,
                'priority': TaskPriority.MEDIUM,
                'keywords': ['browser', 'navigate', 'click', 'fill', 'web', 'url'],
                'complexity_factor': 1.0,
                'base_duration': 4.0
            },
            {
                'pattern': r'(plan|strategy|how.*to|steps.*for|break.*down)',
                'task_type': TaskType.PLANNING,
                'priority': TaskPriority.HIGH,
                'keywords': ['plan', 'strategy', 'how', 'steps', 'break', 'analyze'],
                'complexity_factor': 1.5,
                'base_duration': 3.0
            },
            {
                'pattern': r'(test|verify|check|validate|debug|error)',
                'task_type': TaskType.TESTING,
                'priority': TaskPriority.HIGH,
                'keywords': ['test', 'verify', 'check', 'validate', 'debug', 'error'],
                'complexity_factor': 1.1,
                'base_duration': 6.0
            },
            {
                'pattern': r'(optimize|improve|performance|faster|efficient)',
                'task_type': TaskType.OPTIMIZATION,
                'priority': TaskPriority.LOW,
                'keywords': ['optimize', 'improve', 'performance', 'faster', 'efficient'],
                'complexity_factor': 1.8,
                'base_duration': 8.0
            }
        ]
    
    def analyze_task(self, user_input: str) -> TaskAnalysisResult:
        """
        Analyze user input and determine task characteristics
        """
        user_input_lower = user_input.lower()
        
        best_match = None
        best_score = 0.0
        
        for rule in self.analysis_rules:
            score = 0.0
            
            # Pattern matching
            if re.search(rule['pattern'], user_input_lower):
                score += 3.0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in rule['keywords'] 
                                 if keyword in user_input_lower)
            score += keyword_matches * 0.5
            
            # Length factor (longer descriptions = more complex)
            if len(user_input.split()) > 10:
                score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = rule
        
        if best_match:
            return TaskAnalysisResult(
                task_type=best_match['task_type'],
                priority=best_match['priority'],
                complexity_factor=best_match['complexity_factor'],
                keywords=best_match['keywords'],
                estimated_duration=best_match['base_duration'] * best_match['complexity_factor']
            )
        
        # Default fallback
        return TaskAnalysisResult(
            task_type=TaskType.PLANNING,
            priority=TaskPriority.MEDIUM,
            complexity_factor=1.0,
            keywords=[],
            estimated_duration=3.0
        )
    
    def is_complex_task(self, user_input: str) -> bool:
        """Check if task requires decomposition"""
        complexity_indicators = [
            " and then ", " after ", " before ", " first ", " next ", 
            " finally ", " step 1", " step 2", " then ", " afterwards "
        ]
        
        user_input_lower = user_input.lower()
        return any(indicator in user_input_lower for indicator in complexity_indicators)
    
    def extract_subtasks(self, user_input: str) -> List[str]:
        """Extract subtasks from complex user input"""
        if not self.is_complex_task(user_input):
            return [user_input]
        
        # Split on common separators
        separators = [
            r'\band then\b', r'\bafter\b', r'\bnext\b', r'\bthen\b',
            r'\bstep \d+', r'\bfinally\b', r'\bafterwards\b'
        ]
        
        parts = [user_input]
        for separator in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(re.split(separator, part, flags=re.IGNORECASE))
            parts = new_parts
        
        # Clean and filter
        subtasks = [part.strip() for part in parts if part.strip()]
        return subtasks if len(subtasks) > 1 else [user_input]
