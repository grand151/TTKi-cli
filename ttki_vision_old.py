#!/usr/bin/env python3
"""
TTKi Vision System - Inteligentne widzenie dla agenta TTKi
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
    UNKNOWN = "unknown"

@dataclass
class InteractiveElement:
    """Reprezentuje interaktywny element GUI wykryty przez Vision System"""
    id: str
    element_type: ElementType
    label: Optional[str]
    x: int
    y: int
    width: int
    height: int
    confidence: float
    center_x: int
    center_y: int
    clickable: bool = True
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        if self.center_x == 0 and self.center_y == 0:
            self.center_x = self.x + self.width // 2
            self.center_y = self.y + self.height // 2

class TTKiVisionSystem:
    """
    TTKi Vision System - Inteligentny system percepcji GUI
    Zapewnia agentowi "oczy" do analizy interfejsu graficznego
    """
    
    def __init__(self):
        self.last_screenshot = None
        self.detected_elements: List[InteractiveElement] = []
        self.action_patterns: Dict[str, Dict] = {}
        self.screenshot_cache = {}
        
    def take_desktop_screenshot(self) -> np.ndarray:
        """
        Pobiera screenshot aktualnego stanu desktop z VNC
        """
        try:
            # Use VNC bridge to take screenshot
            from app import vnc_shell_exec
            
            # Take screenshot and save to temporary file
            screenshot_path = "/headless/Desktop/ttki_vision_screenshot.png"
            result = vnc_shell_exec(f'DISPLAY=:1 scrot {screenshot_path}')
            
            if "Error" in str(result):
                logger.warning("Scrot failed, trying alternative method")
                # Alternative: use xwd
                result = vnc_shell_exec(f'DISPLAY=:1 xwd -root -out {screenshot_path}.xwd && convert {screenshot_path}.xwd {screenshot_path}')
            
            # Copy screenshot from VNC container to AI container
            copy_result = subprocess.run([
                'docker', 'cp', f'ttki-vnc:{screenshot_path}', '/tmp/ttki_screenshot.png'
            ], capture_output=True, text=True)
            
            if copy_result.returncode == 0:
                # Load image with OpenCV
                image = cv2.imread('/tmp/ttki_screenshot.png')
                if image is not None:
                    self.last_screenshot = image
                    logger.info(f"Screenshot captured: {image.shape}")
                    return image
                else:
                    logger.error("Failed to load screenshot image")
            else:
                logger.error(f"Failed to copy screenshot: {copy_result.stderr}")
                
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            
        # Fallback: create dummy image if screenshot fails
        dummy_image = np.zeros((800, 1024, 3), dtype=np.uint8)
        self.last_screenshot = dummy_image
        return dummy_image
    
    def perceive_interactive_elements(self) -> List[InteractiveElement]:
        """
        Główna funkcja percepcji - zwraca listę interaktywnych elementów
        Odpowiednik funkcji z perspektywy agenta
        """
        logger.info("🔍 TTKi Vision: Perceiving interactive elements...")
        
        # Pobierz aktualny screenshot
        screenshot = self.take_desktop_screenshot()
        
        # Wykryj elementy GUI
        elements = []
        elements.extend(self._detect_buttons(screenshot))
        elements.extend(self._detect_windows(screenshot))
        elements.extend(self._detect_menu_items(screenshot))
        elements.extend(self._detect_desktop_icons(screenshot))
        
        # Zapisz wykryte elementy
        self.detected_elements = elements
        
        logger.info(f"🎯 TTKi Vision: Detected {len(elements)} interactive elements")
        return elements
    
    def _detect_buttons(self, image: np.ndarray) -> List[InteractiveElement]:
        """Wykrywa przyciski w interfejsie"""
        elements = []
        
        try:
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours (potential button boundaries)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size - buttons are usually medium-sized rectangles
                if 20 <= w <= 200 and 15 <= h <= 80:
                    area = cv2.contourArea(contour)
                    rect_area = w * h
                    
                    # Check if contour is roughly rectangular
                    if area > 0.6 * rect_area:
                        element = InteractiveElement(
                            id=f"button_{i}",
                            element_type=ElementType.BUTTON,
                            label=None,  # TODO: Add OCR for label detection
                            x=x, y=y, width=w, height=h,
                            confidence=0.7,
                            center_x=x + w//2,
                            center_y=y + h//2
                        )
                        elements.append(element)
                        
        except Exception as e:
            logger.warning(f"Button detection failed: {e}")
            
        return elements[:10]  # Limit to top 10 candidates
    
    def _detect_windows(self, image: np.ndarray) -> List[InteractiveElement]:
        """Wykrywa okna aplikacji"""
        elements = []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect larger rectangular areas (windows)
            edges = cv2.Canny(gray, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Windows are large rectangles
                if w > 300 and h > 200:
                    element = InteractiveElement(
                        id=f"window_{i}",
                        element_type=ElementType.WINDOW,
                        label="Window",
                        x=x, y=y, width=w, height=h,
                        confidence=0.8,
                        center_x=x + w//2,
                        center_y=y + h//2
                    )
                    elements.append(element)
                    
        except Exception as e:
            logger.warning(f"Window detection failed: {e}")
            
        return elements[:5]  # Limit to top 5 windows
    
    def _detect_menu_items(self, image: np.ndarray) -> List[InteractiveElement]:
        """Wykrywa elementy menu"""
        elements = []
        
        try:
            # Look for horizontal strips that could be menu bars
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect horizontal lines (potential menu bars)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Menu bars are wide and thin
                if w > 100 and h < 40:
                    element = InteractiveElement(
                        id=f"menu_{i}",
                        element_type=ElementType.MENU_ITEM,
                        label="Menu",
                        x=x, y=y, width=w, height=h,
                        confidence=0.6,
                        center_x=x + w//2,
                        center_y=y + h//2
                    )
                    elements.append(element)
                    
        except Exception as e:
            logger.warning(f"Menu detection failed: {e}")
            
        return elements[:8]  # Limit to top 8 menu items
    
    def _detect_desktop_icons(self, image: np.ndarray) -> List[InteractiveElement]:
        """Wykrywa ikony na pulpicie"""
        elements = []
        
        try:
            # Desktop icons are usually small square elements
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Icons are small and roughly square
                if 20 <= w <= 100 and 20 <= h <= 100:
                    aspect_ratio = w / h
                    if 0.7 <= aspect_ratio <= 1.4:  # Roughly square
                        element = InteractiveElement(
                            id=f"icon_{i}",
                            element_type=ElementType.ICON,
                            label="Icon",
                            x=x, y=y, width=w, height=h,
                            confidence=0.5,
                            center_x=x + w//2,
                            center_y=y + h//2
                        )
                        elements.append(element)
                        
        except Exception as e:
            logger.warning(f"Icon detection failed: {e}")
            
        return elements[:15]  # Limit to top 15 icons
    
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
        if any(keyword in task_lower for keyword in ['save', 'zapisz', 'save as']):
            return self._find_save_element(elements)
        elif any(keyword in task_lower for keyword in ['open', 'otwórz', 'load']):
            return self._find_open_element(elements)
        elif any(keyword in task_lower for keyword in ['new', 'nowy', 'create', 'utwórz']):
            return self._find_new_element(elements)
        elif any(keyword in task_lower for keyword in ['close', 'zamknij', 'exit']):
            return self._find_close_element(elements)
        elif any(keyword in task_lower for keyword in ['folder', 'katalog', 'directory']):
            return self._find_folder_related_element(elements)
        else:
            # Fallback: return most prominent clickable element
            return self._find_most_prominent_element(elements)
    
    def _find_save_element(self, elements: List[InteractiveElement]) -> Optional[InteractiveElement]:
        """Znajduje element związany z zapisywaniem"""
        for element in elements:
            if element.element_type == ElementType.BUTTON:
                # Prefer buttons that might be save buttons
                if element.width < 150 and element.height < 50:
                    return element
        return None
    
    def _find_folder_related_element(self, elements: List[InteractiveElement]) -> Optional[InteractiveElement]:
        """Znajduje element związany z folderami/katalogami"""
        # Look for right-click context or desktop area
        for element in elements:
            if element.element_type == ElementType.WINDOW:
                # Click in empty desktop area for context menu
                return InteractiveElement(
                    id="desktop_area",
                    element_type=ElementType.UNKNOWN,
                    label="Desktop",
                    x=400, y=300, width=100, height=100,
                    confidence=0.9,
                    center_x=400, center_y=300
                )
        return None
    
    def _find_most_prominent_element(self, elements: List[InteractiveElement]) -> Optional[InteractiveElement]:
        """Znajduje najbardziej prominent element (fallback)"""
        if not elements:
            return None
            
        # Sort by confidence and size
        sorted_elements = sorted(elements, 
                               key=lambda e: e.confidence * (e.width * e.height), 
                               reverse=True)
        return sorted_elements[0] if sorted_elements else None
    
    def _find_open_element(self, elements: List[InteractiveElement]) -> Optional[InteractiveElement]:
        """Znajduje element do otwierania"""
        for element in elements:
            if element.element_type == ElementType.BUTTON and element.width < 100:
                return element
        return None
    
    def _find_new_element(self, elements: List[InteractiveElement]) -> Optional[InteractiveElement]:
        """Znajduje element do tworzenia nowego"""
        for element in elements:
            if element.element_type in [ElementType.BUTTON, ElementType.MENU_ITEM]:
                return element
        return None
    
    def _find_close_element(self, elements: List[InteractiveElement]) -> Optional[InteractiveElement]:
        """Znajduje element do zamykania"""
        for element in elements:
            if element.element_type == ElementType.BUTTON:
                # Look for buttons in top-right area (typical close button location)
                if element.x > 800 and element.y < 100:
                    return element
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
            
            # Look for specific changes based on action type
            success_indicators = []
            
            if "create folder" in action_description.lower():
                # Look for new folder or dialog
                new_dialogs = [e for e in current_elements if e.element_type == ElementType.WINDOW]
                if new_dialogs:
                    success_indicators.append("Dialog appeared")
                    changes_detected = True
            
            if "save" in action_description.lower():
                # Look for save dialog or file confirmation
                new_windows = [e for e in current_elements if e.element_type == ElementType.WINDOW]
                if len(new_windows) > len([e for e in before_elements if e.element_type == ElementType.WINDOW]):
                    success_indicators.append("New window/dialog opened")
                    changes_detected = True
            
            # Basic screenshot difference if available
            confidence = 0.5  # Default confidence
            if self.last_screenshot is not None:
                diff = cv2.absdiff(self.last_screenshot, current_screenshot)
                diff_score = np.mean(diff) / 255.0  # Normalize to 0-1
                confidence = min(diff_score * 2, 1.0)  # Scale confidence
                
                if diff_score > 0.1:
                    changes_detected = True
                    success_indicators.append(f"Visual change detected (score: {diff_score:.2f})")
            
            result = {
                "success": changes_detected,
                "confidence": confidence,
                "before_elements_count": len(before_elements),
                "after_elements_count": len(current_elements),
                "changes_detected": changes_detected,
                "success_indicators": success_indicators,
                "verification_method": "basic_cv",
                "timestamp": time.time()
            }
            
            logger.info(f"✅ Action verification: {'SUCCESS' if changes_detected else 'NO CHANGE'}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Basic verification failed: {e}")
            return {"success": False, "confidence": 0.0, "error": str(e)}
    
    def get_elements_as_json(self) -> List[Dict]:
        """
        Zwraca wykryte elementy w formacie JSON
        Zgodny z formatem z perspektywy agenta
        """
        return [
            {
                "id": element.id,
                "type": element.element_type.value,
                "label": element.label,
                "x": element.x,
                "y": element.y,
                "width": element.width,
                "height": element.height,
                "center_x": element.center_x,
                "center_y": element.center_y,
                "confidence": element.confidence,
                "clickable": element.clickable
            }
            for element in self.detected_elements
        ]
    
    def save_debug_screenshot(self, elements: List[InteractiveElement] = None) -> str:
        """Zapisuje screenshot z zaznaczonymi elementami dla debugowania"""
        if self.last_screenshot is None:
            return "No screenshot available"
            
        debug_image = self.last_screenshot.copy()
        elements_to_draw = elements or self.detected_elements
        
        # Draw bounding boxes around detected elements
        for element in elements_to_draw:
            color = (0, 255, 0)  # Green for normal elements
            if element.element_type == ElementType.BUTTON:
                color = (255, 0, 0)  # Red for buttons
            elif element.element_type == ElementType.WINDOW:
                color = (0, 0, 255)  # Blue for windows
                
            cv2.rectangle(debug_image, 
                         (element.x, element.y), 
                         (element.x + element.width, element.y + element.height), 
                         color, 2)
            
            # Draw center point
            cv2.circle(debug_image, (element.center_x, element.center_y), 5, color, -1)
            
            # Add label if available
            if element.label:
                cv2.putText(debug_image, element.label, 
                           (element.x, element.y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        debug_path = "/tmp/ttki_vision_debug.png"
        cv2.imwrite(debug_path, debug_image)
        logger.info(f"Debug screenshot saved: {debug_path}")
        return debug_path

# Global Vision System instance
ttki_vision = TTKiVisionSystem()
