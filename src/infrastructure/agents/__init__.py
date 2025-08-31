"""
Real Agent Implementations - Bridge between DDD and TTKi functions
"""

from .desktop_agent import DesktopAgent
from .vision_agent import VisionAgent  
from .coding_agent import CodingAgent
from .file_agent import FileAgent
from .terminal_agent import TerminalAgent

__all__ = [
    'DesktopAgent', 'VisionAgent', 'CodingAgent', 
    'FileAgent', 'TerminalAgent'
]
