"""
Task Router - Intelligent task routing and decomposition
Core component of TTKi multi-agent system
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .base_agent import Task, TaskType, TaskPriority

logger = logging.getLogger(__name__)

@dataclass
class RoutingRule:
    """Reguła routingu zadań"""
    pattern: str
    task_type: TaskType
    priority: TaskPriority
    keywords: List[str]
    complexity_factor: float = 1.0

class TaskRouter:
    """
    Intelligent Task Router
    Analizuje zadania użytkownika i kieruje je do odpowiednich agentów
    """
    
    def __init__(self):
        self.routing_rules = self._initialize_routing_rules()
        self.task_counter = 0
    
    def _initialize_routing_rules(self) -> List[RoutingRule]:
        """Inicjalizuje reguły routingu zadań"""
        return [
            # Vision Analysis Rules
            RoutingRule(
                pattern=r"(screenshot|capture|analyze.*screen|what.*see|visual|image)",
                task_type=TaskType.VISION_ANALYSIS,
                priority=TaskPriority.HIGH,
                keywords=["screenshot", "analyze", "visual", "see", "screen", "image", "detect"],
                complexity_factor=0.8
            ),
            
            # Code Generation Rules
            RoutingRule(
                pattern=r"(write.*code|create.*function|implement|generate.*script|code.*for)",
                task_type=TaskType.CODE_GENERATION,
                priority=TaskPriority.HIGH,
                keywords=["write", "create", "implement", "generate", "code", "function", "script"],
                complexity_factor=1.2
            ),
            
            # File Operations Rules
            RoutingRule(
                pattern=r"(create.*file|edit.*file|delete.*file|move.*file|copy.*file|read.*file)",
                task_type=TaskType.FILE_OPERATIONS,
                priority=TaskPriority.MEDIUM,
                keywords=["create", "edit", "delete", "move", "copy", "read", "file"],
                complexity_factor=0.6
            ),
            
            # Terminal Commands Rules
            RoutingRule(
                pattern=r"(run.*command|execute|terminal|bash|shell|install|pip|npm)",
                task_type=TaskType.TERMINAL_COMMANDS,
                priority=TaskPriority.MEDIUM,
                keywords=["run", "execute", "terminal", "command", "bash", "shell", "install"],
                complexity_factor=0.7
            ),
            
            # Browser Automation Rules
            RoutingRule(
                pattern=r"(open.*browser|navigate.*to|click.*button|fill.*form|scrape|web)",
                task_type=TaskType.BROWSER_AUTOMATION,
                priority=TaskPriority.MEDIUM,
                keywords=["browser", "navigate", "click", "fill", "scrape", "web", "url"],
                complexity_factor=1.0
            ),
            
            # Planning Rules
            RoutingRule(
                pattern=r"(plan|strategy|how.*to|steps.*for|break.*down|analyze.*task)",
                task_type=TaskType.PLANNING,
                priority=TaskPriority.HIGH,
                keywords=["plan", "strategy", "how", "steps", "break", "analyze", "approach"],
                complexity_factor=1.5
            ),
            
            # Testing Rules
            RoutingRule(
                pattern=r"(test|verify|check|validate|debug|error|fix)",
                task_type=TaskType.TESTING,
                priority=TaskPriority.HIGH,
                keywords=["test", "verify", "check", "validate", "debug", "error", "fix"],
                complexity_factor=1.1
            ),
            
            # Optimization Rules
            RoutingRule(
                pattern=r"(optimize|improve|performance|faster|efficient|reduce)",
                task_type=TaskType.OPTIMIZATION,
                priority=TaskPriority.LOW,
                keywords=["optimize", "improve", "performance", "faster", "efficient", "reduce"],
                complexity_factor=1.8
            )
        ]
    
    def analyze_task(self, user_input: str) -> Tuple[TaskType, TaskPriority, float]:
        """
        Analizuje zadanie użytkownika i określa typ, priorytet i złożoność
        """
        user_input_lower = user_input.lower()
        
        best_match = None
        best_score = 0.0
        
        for rule in self.routing_rules:
            score = 0.0
            
            # Sprawdź dopasowanie wzorca regex
            if re.search(rule.pattern, user_input_lower):
                score += 3.0
            
            # Sprawdź słowa kluczowe
            keyword_matches = sum(1 for keyword in rule.keywords if keyword in user_input_lower)
            score += keyword_matches * 0.5
            
            # Uwzględnij długość zadania (dłuższe = bardziej złożone)
            if len(user_input.split()) > 10:
                score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = rule
        
        if best_match:
            return best_match.task_type, best_match.priority, best_match.complexity_factor
        
        # Domyślnie - planowanie dla nierozpoznanych zadań
        return TaskType.PLANNING, TaskPriority.MEDIUM, 1.0
    
    def decompose_complex_task(self, user_input: str) -> List[Task]:
        """
        Dekompozycja złożonych zadań na prostsze subtasks
        """
        tasks = []
        
        # Sprawdź czy zadanie zawiera wiele działań
        if self._is_complex_task(user_input):
            subtasks = self._extract_subtasks(user_input)
            
            for i, subtask_description in enumerate(subtasks):
                task_type, priority, complexity = self.analyze_task(subtask_description)
                
                task = Task(
                    id=self._generate_task_id(),
                    type=task_type,
                    description=subtask_description.strip(),
                    priority=priority,
                    estimated_duration=self._estimate_duration(complexity),
                    dependencies=[] if i == 0 else [tasks[i-1].id]
                )
                tasks.append(task)
        else:
            # Pojedyncze zadanie
            task_type, priority, complexity = self.analyze_task(user_input)
            
            task = Task(
                id=self._generate_task_id(),
                type=task_type,
                description=user_input.strip(),
                priority=priority,
                estimated_duration=self._estimate_duration(complexity)
            )
            tasks.append(task)
        
        return tasks
    
    def _is_complex_task(self, user_input: str) -> bool:
        """Sprawdza czy zadanie jest złożone"""
        complexity_indicators = [
            " and then ", " after ", " before ", " first ", " next ", " finally ",
            " step 1", " step 2", " then ", " afterwards ", " subsequently "
        ]
        
        user_input_lower = user_input.lower()
        return any(indicator in user_input_lower for indicator in complexity_indicators)
    
    def _extract_subtasks(self, user_input: str) -> List[str]:
        """Wyodrębnia subtasks z złożonego zadania"""
        # Proste rozdzielenie na podstawie słów kluczowych
        separators = [
            r"\band then\b", r"\bafter\b", r"\bnext\b", r"\bthen\b",
            r"\bstep \d+", r"\bfinally\b", r"\bafterwards\b"
        ]
        
        parts = [user_input]
        for separator in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(re.split(separator, part, flags=re.IGNORECASE))
            parts = new_parts
        
        # Usuń puste części i oczyść
        subtasks = [part.strip() for part in parts if part.strip()]
        
        return subtasks if len(subtasks) > 1 else [user_input]
    
    def _estimate_duration(self, complexity_factor: float) -> float:
        """Estymuje czas wykonania zadania na podstawie złożoności"""
        base_duration = 3.0  # 3 sekundy jako base
        return base_duration * complexity_factor
    
    def _generate_task_id(self) -> str:
        """Generuje unikalny ID zadania"""
        self.task_counter += 1
        return f"task_{self.task_counter:06d}"
    
    def get_routing_stats(self) -> Dict[str, any]:
        """Zwraca statystyki routingu"""
        return {
            'total_rules': len(self.routing_rules),
            'tasks_processed': self.task_counter,
            'rule_types': [rule.task_type.value for rule in self.routing_rules]
        }
