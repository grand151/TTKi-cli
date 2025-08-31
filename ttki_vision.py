#!/usr/bin/env python3
"""
TTKi Vision System - Inteligentne widzenie dla agenta TTKi z dedykowanym AI
Enhanced with dedicated Vision AI model for maximum responsiveness
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import subprocess
import json
from datetime import datetime

# Import dedykowanego Vision AI
try:
    from vision_ai_service import get_vision_ai, is_vision_ai_available
    VISION_AI_AVAILABLE = True
except ImportError:
    VISION_AI_AVAILABLE = False
    logging.warning("⚠️ Vision AI Service not available - using basic computer vision")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElementType(Enum):
    BUTTON = "button"
    WINDOW = "window" 
    MENU = "menu"
    ICON = "icon"
    TEXT_FIELD = "text_field"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    UNKNOWN = "unknown"

@dataclass
class InteractiveElement:
    element_type: ElementType
    center_x: int
    center_y: int
    width: int
    height: int
    confidence: float
    text_content: Optional[str] = None
    element_id: Optional[str] = None
    context_relevance: float = 0.0

class TTKiVisionSystem:
    """
    Inteligentny system widzenia TTKi z dedykowanym AI
    Zwiększona responsywność przez odciążenie głównego modelu
    """
    
    def __init__(self):
        self.last_screenshot = None
        self.last_elements = []
        self.vision_ai = None
        self.ai_enhanced = False
        
        # Inicjalizacja dedykowanego Vision AI
        if VISION_AI_AVAILABLE:
            self.vision_ai = get_vision_ai()
            self.ai_enhanced = self.vision_ai.is_available
            
            if self.ai_enhanced:
                logger.info("🎯 TTKi Vision System enhanced with dedicated AI model")
            else:
                logger.info("🔍 TTKi Vision System using computer vision + main AI")
        else:
            logger.info("🖥️ TTKi Vision System using basic computer vision")
    
    def capture_screenshot(self) -> np.ndarray:
        """Capture screenshot from VNC display"""
        try:
            # Use scrot to capture screenshot
            result = subprocess.run([
                'scrot', '-z', '/tmp/ttki_screenshot.png'
            ], capture_output=True, text=True, env={'DISPLAY': ':1'})
            
            if result.returncode != 0:
                logger.error(f"Screenshot capture failed: {result.stderr}")
                return None
            
            # Load screenshot with OpenCV
            screenshot = cv2.imread('/tmp/ttki_screenshot.png')
            if screenshot is None:
                logger.error("Failed to load screenshot")
                return None
            
            self.last_screenshot = screenshot
            return screenshot
            
        except Exception as e:
            logger.error(f"Screenshot capture exception: {e}")
            return None
    
    def perceive_interactive_elements(self, task_context: str = "") -> List[InteractiveElement]:
        """
        Perceive interactive elements using enhanced AI vision
        Wykorzystuje dedykowany Vision AI dla maksymalnej responsywności
        """
        logger.info("👁️ TTKi Vision: Perceiving interactive elements...")
        
        # Capture fresh screenshot
        screenshot = self.capture_screenshot()
        if screenshot is None:
            logger.error("❌ Cannot perceive - screenshot capture failed")
            return []
        
        # Use enhanced AI vision if available
        if self.ai_enhanced and self.vision_ai:
            return self._perceive_with_ai_vision(screenshot, task_context)
        else:
            return self._perceive_with_computer_vision(screenshot, task_context)
    
    def _perceive_with_ai_vision(self, screenshot: np.ndarray, task_context: str) -> List[InteractiveElement]:
        """Percepcja z dedykowanym AI modelem wizji"""
        try:
            logger.info("🎯 Using dedicated Vision AI for element detection")
            
            # Convert screenshot to bytes
            _, buffer = cv2.imencode('.png', screenshot)
            screenshot_bytes = buffer.tobytes()
            
            # Analyze with dedicated Vision AI
            analysis_result = self.vision_ai.analyze_screenshot_for_elements(
                screenshot_bytes, 
                task_context
            )
            
            # Convert AI analysis to InteractiveElement objects
            elements = []
            for element_data in analysis_result.elements_detected:
                coords = element_data.get("coordinates", {})
                
                element = InteractiveElement(
                    element_type=self._parse_element_type(element_data.get("type", "unknown")),
                    center_x=coords.get("x", 0) + coords.get("width", 0) // 2,
                    center_y=coords.get("y", 0) + coords.get("height", 0) // 2,
                    width=coords.get("width", 0),
                    height=coords.get("height", 0),
                    confidence=element_data.get("confidence", 0.0),
                    text_content=element_data.get("text_content"),
                    element_id=element_data.get("element_id"),
                    context_relevance=element_data.get("context_relevance", 0.0)
                )
                elements.append(element)
            
            self.last_elements = elements
            
            logger.info(f"🎪 AI Vision detected {len(elements)} elements in {analysis_result.processing_time:.2f}s")
            return elements
            
        except Exception as e:
            logger.error(f"❌ AI vision perception failed: {e}")
            logger.info("🔄 Falling back to computer vision...")
            return self._perceive_with_computer_vision(screenshot, task_context)
    
    def _perceive_with_computer_vision(self, screenshot: np.ndarray, task_context: str) -> List[InteractiveElement]:
        """Percepcja z podstawowym computer vision"""
        logger.info("🖥️ Using computer vision for element detection")
        
        elements = []
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Detect potential buttons using contours
        elements.extend(self._detect_buttons(gray))
        
        # Detect windows/rectangles
        elements.extend(self._detect_windows(gray))
        
        # Detect text fields
        elements.extend(self._detect_text_fields(gray))
        
        self.last_elements = elements
        logger.info(f"🔍 Computer vision detected {len(elements)} elements")
        
        return elements
    
    def _parse_element_type(self, type_str: str) -> ElementType:
        """Convert string to ElementType enum"""
        type_mapping = {
            "button": ElementType.BUTTON,
            "window": ElementType.WINDOW,
            "menu": ElementType.MENU,
            "icon": ElementType.ICON,
            "text_field": ElementType.TEXT_FIELD,
            "checkbox": ElementType.CHECKBOX,
            "dropdown": ElementType.DROPDOWN
        }
        return type_mapping.get(type_str.lower(), ElementType.UNKNOWN)
    
    def _detect_buttons(self, gray: np.ndarray) -> List[InteractiveElement]:
        """Basic button detection using computer vision"""
        elements = []
        
        try:
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size - buttons are usually medium-sized rectangles
                if 20 <= w <= 200 and 15 <= h <= 80:
                    area = cv2.contourArea(contour)
                    rect_area = w * h
                    
                    # Check if contour is roughly rectangular
                    if area > 0.6 * rect_area:
                        element = InteractiveElement(
                            element_type=ElementType.BUTTON,
                            center_x=x + w//2,
                            center_y=y + h//2,
                            width=w,
                            height=h,
                            confidence=0.7,
                            element_id=f"button_{i}"
                        )
                        elements.append(element)
                        
        except Exception as e:
            logger.warning(f"Button detection failed: {e}")
            
        return elements[:10]  # Limit to top 10 candidates
    
    def _detect_windows(self, gray: np.ndarray) -> List[InteractiveElement]:
        """Basic window detection"""
        elements = []
        
        try:
            edges = cv2.Canny(gray, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Windows are large rectangles
                if w > 300 and h > 200:
                    element = InteractiveElement(
                        element_type=ElementType.WINDOW,
                        center_x=x + w//2,
                        center_y=y + h//2,
                        width=w,
                        height=h,
                        confidence=0.8,
                        element_id=f"window_{i}"
                    )
                    elements.append(element)
                    
        except Exception as e:
            logger.warning(f"Window detection failed: {e}")
            
        return elements[:5]
    
    def _detect_text_fields(self, gray: np.ndarray) -> List[InteractiveElement]:
        """Basic text field detection"""
        elements = []
        
        try:
            # Simple rectangular detection for text fields
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Text fields are usually wide and short
                if 50 <= w <= 300 and 15 <= h <= 40:
                    element = InteractiveElement(
                        element_type=ElementType.TEXT_FIELD,
                        center_x=x + w//2,
                        center_y=y + h//2,
                        width=w,
                        height=h,
                        confidence=0.6,
                        element_id=f"textfield_{i}"
                    )
                    elements.append(element)
                    
        except Exception as e:
            logger.warning(f"Text field detection failed: {e}")
            
        return elements[:8]
    
    def find_target_for_task(self, task: str, elements: List[InteractiveElement] = None) -> Optional[InteractiveElement]:
        """
        Enhanced target finding with AI recommendations
        Wykorzystuje dedykowany Vision AI dla inteligentnego targetowania
        """
        if elements is None:
            elements = self.last_elements
            
        logger.info(f"🎯 Finding target for task: {task}")
        
        if not elements:
            logger.warning("⚠️ No elements provided for targeting")
            return None
        
        # Use AI-enhanced targeting if available
        if self.ai_enhanced and self.vision_ai and self.last_screenshot is not None:
            try:
                # Get AI targeting suggestions
                _, buffer = cv2.imencode('.png', self.last_screenshot)
                screenshot_bytes = buffer.tobytes()
                
                suggestions = self.vision_ai.get_smart_targeting_suggestions(
                    screenshot_bytes, 
                    task
                )
                
                if suggestions:
                    # Find best matching element from suggestions
                    best_suggestion = max(suggestions, key=lambda x: x.get('success_probability', 0))
                    target_coords = best_suggestion.get('coordinates', {})
                    
                    # Find closest element to AI suggestion
                    best_element = self._find_closest_element(
                        elements, 
                        target_coords.get('x', 0), 
                        target_coords.get('y', 0)
                    )
                    
                    if best_element:
                        logger.info(f"🎪 AI targeting selected: {best_element.element_type.value} (confidence: {best_suggestion.get('success_probability', 0):.2f})")
                        return best_element
                
            except Exception as e:
                logger.error(f"❌ AI targeting failed: {e}")
                logger.info("🔄 Falling back to heuristic targeting...")
        
        # Fallback to heuristic targeting
        return self._find_target_with_heuristics(task, elements)
    
    def _find_closest_element(self, elements: List[InteractiveElement], x: int, y: int) -> Optional[InteractiveElement]:
        """Find element closest to given coordinates"""
        if not elements:
            return None
        
        def distance(element):
            return ((element.center_x - x) ** 2 + (element.center_y - y) ** 2) ** 0.5
        
        return min(elements, key=distance)
    
    def _find_target_with_heuristics(self, task: str, elements: List[InteractiveElement]) -> Optional[InteractiveElement]:
        """Fallback heuristic targeting"""
        logger.info("🔧 Using heuristic targeting")
        
        task_lower = task.lower()
        
        # Task-specific heuristics
        if "create folder" in task_lower or "utwórz folder" in task_lower:
            # Look for desktop area or file manager
            desktop_elements = [e for e in elements if e.element_type in [ElementType.WINDOW, ElementType.ICON]]
            if desktop_elements:
                return max(desktop_elements, key=lambda e: e.width * e.height)  # Largest area
        
        elif "open" in task_lower or "otwórz" in task_lower:
            # Look for buttons or menu items
            interactive_elements = [e for e in elements if e.element_type == ElementType.BUTTON]
            if interactive_elements:
                return max(interactive_elements, key=lambda e: e.confidence)
        
        # Generic fallback - highest confidence element
        if elements:
            return max(elements, key=lambda e: e.confidence)
        
        return None
    
    def verify_action_success(self, before_elements: List[InteractiveElement], 
                            action_description: str) -> Dict[str, Any]:
        """
        Enhanced action verification with AI comparison
        Wykorzystuje dedykowany Vision AI dla weryfikacji powodzenia
        """
        logger.info("🔄 Verifying action success...")
        
        # Wait a moment for interface to update
        import time
        time.sleep(1)
        
        # Capture new screenshot for comparison
        current_screenshot = self.capture_screenshot()
        if current_screenshot is None:
            return {"success": False, "confidence": 0.0, "error": "Cannot capture verification screenshot"}
        
        # Use AI verification if available
        if self.ai_enhanced and self.vision_ai and self.last_screenshot is not None:
            try:
                # Convert both screenshots to bytes
                _, before_buffer = cv2.imencode('.png', self.last_screenshot)
                _, after_buffer = cv2.imencode('.png', current_screenshot)
                
                before_bytes = before_buffer.tobytes()
                after_bytes = after_buffer.tobytes()
                
                # Analyze with dedicated Vision AI
                verification_result = self.vision_ai.analyze_action_result(
                    before_bytes,
                    after_bytes,
                    {"task": action_description, "timestamp": datetime.now().isoformat()}
                )
                
                if verification_result:
                    logger.info(f"🎯 AI verification: {verification_result.get('action_successful', False)} (confidence: {verification_result.get('confidence_score', 0):.2f})")
                    return {
                        "success": verification_result.get("action_successful", False),
                        "confidence": verification_result.get("confidence_score", 0.0),
                        "changes_detected": verification_result.get("detected_changes", []),
                        "verification_method": "ai_vision",
                        "analysis": verification_result.get("verification_details", {})
                    }
                
            except Exception as e:
                logger.error(f"❌ AI verification failed: {e}")
                logger.info("🔄 Falling back to basic verification...")
        
        # Fallback to basic comparison
        return self._verify_with_basic_comparison(before_elements, current_screenshot, action_description)
    
    def _verify_with_basic_comparison(self, before_elements: List[InteractiveElement], 
                                    current_screenshot: np.ndarray, action_description: str) -> Dict[str, Any]:
        """Basic verification using computer vision comparison"""
        logger.info("🔧 Using basic verification method")
        
        try:
            # Detect elements in current state
            current_elements = self._perceive_with_computer_vision(current_screenshot, action_description)
            
            # Compare before and after states
            changes_detected = len(current_elements) != len(before_elements)
            
            # Basic screenshot difference if available
            confidence = 0.5  # Default confidence
            if self.last_screenshot is not None:
                diff = cv2.absdiff(self.last_screenshot, current_screenshot)
                diff_score = np.mean(diff) / 255.0  # Normalize to 0-1
                confidence = min(diff_score * 2, 1.0)  # Scale confidence
                
                if diff_score > 0.1:
                    changes_detected = True
            
            result = {
                "success": changes_detected,
                "confidence": confidence,
                "before_elements_count": len(before_elements),
                "after_elements_count": len(current_elements),
                "changes_detected": changes_detected,
                "verification_method": "basic_cv",
                "timestamp": time.time()
            }
            
            logger.info(f"✅ Action verification: {'SUCCESS' if changes_detected else 'NO CHANGE'}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Basic verification failed: {e}")
            return {"success": False, "confidence": 0.0, "error": str(e)}
    
    def get_elements_as_json(self) -> List[Dict]:
        """Return detected elements as JSON"""
        elements_json = []
        
        for element in self.last_elements:
            element_dict = {
                "element_id": element.element_id,
                "type": element.element_type.value,
                "position": {
                    "center_x": element.center_x,
                    "center_y": element.center_y,
                    "width": element.width,
                    "height": element.height
                },
                "confidence": element.confidence,
                "text_content": element.text_content,
                "context_relevance": element.context_relevance
            }
            elements_json.append(element_dict)
        
        return elements_json

# Globalna instancja TTKi Vision System
_vision_system_instance = None

def get_ttki_vision() -> TTKiVisionSystem:
    """Pobierz globalną instancję TTKi Vision System"""
    global _vision_system_instance
    
    if _vision_system_instance is None:
        _vision_system_instance = TTKiVisionSystem()
    
    return _vision_system_instance

# Główna instancja systemu wizji
ttki_vision = get_ttki_vision()

# Legacy compatibility functions
def perceive_interactive_elements() -> List[InteractiveElement]:
    """Legacy function for backward compatibility"""
    return ttki_vision.perceive_interactive_elements()

def find_target_for_task(task: str, elements: List[InteractiveElement] = None) -> Optional[InteractiveElement]:
    """Legacy function for backward compatibility"""
    return ttki_vision.find_target_for_task(task, elements)

def verify_action_success(elements_before: List[InteractiveElement], task: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    return ttki_vision.verify_action_success(elements_before, task)
