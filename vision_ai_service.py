#!/usr/bin/env python3
"""
TTKi Vision AI Service - Dedykowany model AI dla systemu widzenia
Niezależny od głównego modelu myślenia dla maksymalnej responsywności
"""

import os
import logging
import json
import base64
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import google.generativeai as genai
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisionAnalysisResult:
    """Wynik analizy wizualnej dedykowanego modelu AI"""
    elements_detected: List[Dict]
    confidence_scores: Dict[str, float]
    recommended_actions: List[Dict]
    analysis_metadata: Dict
    processing_time: float

class TTKiVisionAI:
    """
    Dedykowany model AI dla TTKi Vision System
    Zwiększa responsywność przez odciążenie głównego modelu
    """
    
    def __init__(self):
        self.vision_model = None
        self.vision_api_key = None
        self.is_available = False
        self._initialize_vision_model()
        
    def _initialize_vision_model(self) -> bool:
        """Inicjalizacja dedykowanego modelu wizji"""
        try:
            # Sprawdź czy jest dostępny drugi klucz API
            self.vision_api_key = os.environ.get('GEMINI_API_KEY_2')
            
            if not self.vision_api_key:
                logger.info("🔍 GEMINI_API_KEY_2 not found - TTKi Vision AI will use main model")
                return False
            
            # Konfiguruj dedykowany model dla wizji
            genai.configure(api_key=self.vision_api_key)
            
            # Użyj modelu zoptymalizowanego pod wizję
            self.vision_model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",  # Szybszy model dla wizji
                generation_config={
                    "temperature": 0.1,  # Niska temperatura dla precyzji
                    "top_p": 0.8,
                    "top_k": 20,
                    "max_output_tokens": 2048,
                }
            )
            
            self.is_available = True
            logger.info("🎯 TTKi Vision AI initialized successfully with dedicated model")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize TTKi Vision AI: {e}")
            self.is_available = False
            return False
    
    def analyze_screenshot_for_elements(self, screenshot_data: bytes, task_context: str = "") -> VisionAnalysisResult:
        """
        Analiza zrzutu ekranu w poszukiwaniu elementów interaktywnych
        Dedykowany model AI dla maksymalnej responsywności
        """
        start_time = datetime.now()
        
        if not self.is_available:
            logger.warning("🔄 TTKi Vision AI not available - using fallback analysis")
            return self._fallback_analysis(screenshot_data, task_context)
        
        try:
            # Konwertuj screenshot do base64
            screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')
            
            # Prompt zoptymalizowany dla wykrywania elementów GUI
            vision_prompt = f"""
            Jesteś TTKi Vision AI - dedykowanym systemem wizualnym dla agenta AI.
            
            Analizuj ten zrzut ekranu pod kątem elementów interaktywnych GUI:
            
            ZADANIE KONTEKSTOWE: {task_context}
            
            Zwróć JSON z następującą strukturą:
            {{
                "elements_detected": [
                    {{
                        "type": "button|window|menu|icon|text_field|checkbox|dropdown",
                        "coordinates": {{"x": int, "y": int, "width": int, "height": int}},
                        "text_content": "visible text or description",
                        "confidence": float_0_to_1,
                        "interactable": boolean,
                        "element_id": "unique_identifier",
                        "context_relevance": float_0_to_1
                    }}
                ],
                "recommended_actions": [
                    {{
                        "action_type": "click|type|scroll|drag",
                        "target_element": "element_id",
                        "confidence": float_0_to_1,
                        "reasoning": "why this action is recommended"
                    }}
                ],
                "screen_analysis": {{
                    "layout_type": "desktop|application|dialog|browser",
                    "primary_focus": "main element or area user should focus on",
                    "complexity_score": float_0_to_1,
                    "actionable_elements": int
                }}
            }}
            
            KRYTERIA ANALIZY:
            1. Identyfikuj WSZYSTKIE klikalne elementy
            2. Ocen relevancję dla zadania kontekstowego
            3. Zapisz dokładne współrzędne i rozmiary
            4. Zaproponuj najbardziej prawdopodobne akcje
            5. Oceń pewność detekcji dla każdego elementu
            
            Odpowiedz TYLKO prawidłowym JSON-em bez dodatkowych komentarzy.
            """
            
            # Przygotuj zawartość dla modelu
            image_data = {
                "mime_type": "image/png",
                "data": screenshot_b64
            }
            
            # Wywołaj dedykowany model wizji
            response = self.vision_model.generate_content([
                vision_prompt,
                image_data
            ])
            
            # Parsuj odpowiedź
            analysis_data = self._parse_vision_response(response.text)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return VisionAnalysisResult(
                elements_detected=analysis_data.get("elements_detected", []),
                confidence_scores=self._extract_confidence_scores(analysis_data),
                recommended_actions=analysis_data.get("recommended_actions", []),
                analysis_metadata=analysis_data.get("screen_analysis", {}),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ TTKi Vision AI analysis failed: {e}")
            return self._fallback_analysis(screenshot_data, task_context)
    
    def analyze_action_result(self, before_screenshot: bytes, after_screenshot: bytes, 
                             executed_action: Dict) -> Dict:
        """
        Analiza wyniku akcji porównując stan przed i po
        Wykorzystuje dedykowany model dla weryfikacji
        """
        if not self.is_available:
            return {"success": False, "confidence": 0.0, "analysis": "Vision AI not available"}
        
        try:
            # Konwertuj oba zrzuty ekranu
            before_b64 = base64.b64encode(before_screenshot).decode('utf-8')
            after_b64 = base64.b64encode(after_screenshot).decode('utf-8')
            
            verification_prompt = f"""
            Jesteś TTKi Vision AI weryfikującym powodzenie akcji.
            
            WYKONANA AKCJA: {executed_action}
            
            Porównaj dwa zrzuty ekranu (przed i po akcji) i oceń:
            
            Zwróć JSON:
            {{
                "action_successful": boolean,
                "confidence_score": float_0_to_1,
                "detected_changes": [
                    {{
                        "change_type": "new_window|closed_dialog|state_change|content_change",
                        "location": {{"x": int, "y": int}},
                        "description": "what changed"
                    }}
                ],
                "verification_details": {{
                    "expected_outcome": "what should have happened",
                    "actual_outcome": "what actually happened",
                    "match_quality": float_0_to_1
                }}
            }}
            
            Odpowiedz TYLKO JSON-em.
            """
            
            # Przygotuj obrazy
            before_image = {"mime_type": "image/png", "data": before_b64}
            after_image = {"mime_type": "image/png", "data": after_b64}
            
            response = self.vision_model.generate_content([
                verification_prompt,
                before_image,
                after_image
            ])
            
            return self._parse_vision_response(response.text)
            
        except Exception as e:
            logger.error(f"❌ Action verification failed: {e}")
            return {"success": False, "confidence": 0.0, "error": str(e)}
    
    def get_smart_targeting_suggestions(self, screenshot_data: bytes, user_intent: str) -> List[Dict]:
        """
        Inteligentne sugestie targetowania dla zadania użytkownika
        Wykorzystuje kontekst zadania dla lepszych rekomendacji
        """
        if not self.is_available:
            return []
        
        try:
            screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')
            
            targeting_prompt = f"""
            TTKi Vision AI - Smart Targeting dla zadania: "{user_intent}"
            
            Przeanalizuj ekran i zaproponuj 3-5 najlepszych opcji targetowania:
            
            Zwróć JSON:
            {{
                "targeting_suggestions": [
                    {{
                        "target_id": "unique_id",
                        "element_type": "button|menu|field",
                        "coordinates": {{"x": int, "y": int}},
                        "action_sequence": ["click", "type:text", "etc"],
                        "success_probability": float_0_to_1,
                        "reasoning": "why this target is good for the intent",
                        "alternative_approaches": ["other ways to achieve the same"]
                    }}
                ]
            }}
            
            Priorytetyzuj opcje według prawdopodobieństwa sukcesu.
            """
            
            image_data = {"mime_type": "image/png", "data": screenshot_b64}
            
            response = self.vision_model.generate_content([
                targeting_prompt,
                image_data
            ])
            
            result = self._parse_vision_response(response.text)
            return result.get("targeting_suggestions", [])
            
        except Exception as e:
            logger.error(f"❌ Smart targeting failed: {e}")
            return []
    
    def _parse_vision_response(self, response_text: str) -> Dict:
        """Parsuj odpowiedź modelu wizji"""
        try:
            # Usuń ewentualne markdown formatowanie
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse vision response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            return {}
    
    def _extract_confidence_scores(self, analysis_data: Dict) -> Dict[str, float]:
        """Wyciągnij oceny pewności z analizy"""
        confidence_scores = {}
        
        for element in analysis_data.get("elements_detected", []):
            element_id = element.get("element_id", "unknown")
            confidence = element.get("confidence", 0.0)
            confidence_scores[element_id] = confidence
        
        return confidence_scores
    
    def _fallback_analysis(self, screenshot_data: bytes, task_context: str) -> VisionAnalysisResult:
        """Analiza fallback gdy dedykowany model nie jest dostępny"""
        logger.info("🔄 Using fallback vision analysis")
        
        return VisionAnalysisResult(
            elements_detected=[],
            confidence_scores={},
            recommended_actions=[],
            analysis_metadata={
                "fallback_mode": True,
                "reason": "Dedicated vision model not available"
            },
            processing_time=0.0
        )
    
    def get_model_status(self) -> Dict:
        """Status dedykowanego modelu wizji"""
        return {
            "vision_ai_available": self.is_available,
            "api_key_configured": self.vision_api_key is not None,
            "model_type": "gemini-1.5-flash" if self.is_available else "fallback",
            "optimization": "visual_perception" if self.is_available else "none"
        }

# Globalny singleton instancji TTKi Vision AI
_vision_ai_instance = None

def get_vision_ai() -> TTKiVisionAI:
    """Pobierz globalną instancję TTKi Vision AI"""
    global _vision_ai_instance
    
    if _vision_ai_instance is None:
        _vision_ai_instance = TTKiVisionAI()
    
    return _vision_ai_instance

def is_vision_ai_available() -> bool:
    """Sprawdź czy dedykowany model wizji jest dostępny"""
    return get_vision_ai().is_available

# Przykład użycia
if __name__ == "__main__":
    vision_ai = get_vision_ai()
    status = vision_ai.get_model_status()
    
    print("🎯 TTKi Vision AI Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")
