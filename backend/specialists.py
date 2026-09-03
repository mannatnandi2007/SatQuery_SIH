"""
SatQuery AI — Specialist Models
RS-VLM: Uses Google Gemini Vision API with remote sensing expert prompt.
Change Detection & Fusion: Stubs returning v2 messages.
"""

import os
import json
import re
import random
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from PIL import Image

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


@dataclass
class SpecialistResult:
    answer: str
    bounding_box: Optional[List[float]]  # [x1_pct, y1_pct, x2_pct, y2_pct]
    confidence: float  # 0.0 - 1.0
    evidence_type: str  # "bbox" | "mask" | "none"
    detail: str  # Description of what the specialist did


# System prompt for the remote sensing VLM
RS_VLM_SYSTEM_PROMPT = """You are RS-VLM (Remote Sensing Visual Language Model), a specialized AI for analyzing satellite and aerial imagery. You are an expert in:
- Land use and land cover classification
- Building and infrastructure detection
- Vegetation analysis (NDVI concepts)
- Water body identification
- Urban area analysis
- Agricultural field detection
- Road and transportation network analysis
- Terrain and geological feature identification

IMPORTANT: You MUST respond in valid JSON format with these exact fields:
{
    "answer": "Your detailed, expert analysis answering the user's question. Be specific about locations (e.g., upper-left, center, lower-right quadrant). Use remote sensing terminology where appropriate. 2-4 sentences.",
    "bounding_box": [x1_pct, y1_pct, x2_pct, y2_pct] or null,
    "confidence": 0.85,
    "detected_objects": ["object1", "object2"]
}

Rules for bounding_box:
- Coordinates are PERCENTAGES (0-100) of image width and height
- x1_pct, y1_pct = top-left corner; x2_pct, y2_pct = bottom-right corner
- If you can identify a specific region of interest, ALWAYS provide a bounding box
- If the question is about the entire image or you cannot localize, set to null
- Make boxes reasonably sized (not the entire image unless appropriate)

Rules for confidence:
- 0.85-0.95 for clear, obvious features
- 0.65-0.84 for moderately clear features
- 0.45-0.64 for ambiguous or hard-to-determine features
- Vary the confidence based on how clear the feature is in the image

Be concise but technically accurate. Do NOT wrap your response in markdown code blocks. Return ONLY the raw JSON object."""


class RSVLMSpecialist:
    """RS-VLM specialist using Gemini Vision API with Groq fallback."""

    def __init__(self):
        self.gemini_model = None
        self.groq_client = None
        self._init_gemini()
        self._init_groq()

    def _init_gemini(self):
        """Initialize Gemini client."""
        if not GEMINI_AVAILABLE:
            print("[RS-VLM] google-generativeai not installed, Gemini unavailable")
            return

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("[RS-VLM] GEMINI_API_KEY not set, Gemini unavailable")
            return

        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
            print("[RS-VLM] Gemini 2.5 Flash initialized successfully")
        except Exception as e:
            print(f"[RS-VLM] Failed to initialize Gemini: {e}")

    def _init_groq(self):
        """Initialize Groq client as fallback."""
        if not GROQ_AVAILABLE:
            print("[RS-VLM] groq not installed, Groq fallback unavailable")
            return

        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key or api_key == "your_groq_api_key_here":
            print("[RS-VLM] GROQ_API_KEY not set, Groq fallback unavailable")
            return

        try:
            self.groq_client = Groq(api_key=api_key)
            print("[RS-VLM] Groq fallback initialized successfully")
        except Exception as e:
            print(f"[RS-VLM] Failed to initialize Groq: {e}")

    def _parse_response(self, text: str) -> Dict:
        """Parse JSON response from the model, handling common formatting issues."""
        # Strip markdown code blocks if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*\n?", "", text)
            text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from the text
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass

            # Fallback: return the raw text as answer
            return {
                "answer": text,
                "bounding_box": None,
                "confidence": 0.65,
                "detected_objects": []
            }

    async def analyze_with_gemini(self, image_bytes: bytes, question: str) -> Optional[Dict]:
        """Analyze image using Gemini Vision API."""
        if self.gemini_model is None:
            return None

        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")

            # Resize if too large (Gemini has limits)
            max_dim = 1024
            if max(img.size) > max_dim:
                ratio = max_dim / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            prompt = f"{RS_VLM_SYSTEM_PROMPT}\n\nUser question: {question}"

            response = self.gemini_model.generate_content(
                [prompt, img],
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024,
                )
            )

            if response and response.text:
                return self._parse_response(response.text)

        except Exception as e:
            print(f"[RS-VLM] Gemini analysis failed: {e}")

        return None

    async def analyze_with_groq(self, question: str, image_info: str) -> Optional[Dict]:
        """Fallback: analyze using Groq text model with image metadata."""
        if self.groq_client is None:
            return None

        try:
            prompt = f"""{RS_VLM_SYSTEM_PROMPT}

Note: You are analyzing based on an image description since direct vision is unavailable.
Image info: {image_info}

User question: {question}"""

            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=1024,
            )

            if chat_completion.choices:
                return self._parse_response(chat_completion.choices[0].message.content)

        except Exception as e:
            print(f"[RS-VLM] Groq fallback failed: {e}")

        return None

    def _get_image_info(self, image_bytes: bytes) -> str:
        """Extract basic image metadata for text-only fallback."""
        try:
            img = Image.open(BytesIO(image_bytes))
            return f"Satellite/aerial image, size: {img.size[0]}x{img.size[1]}, mode: {img.mode}, format: {img.format or 'unknown'}"
        except Exception:
            return "Satellite/aerial image (metadata unavailable)"

    def _generate_mock_response(self, question: str) -> Dict:
        """Generate a mock response when no API is available."""
        q_lower = question.lower()

        # Context-aware mock responses
        if any(w in q_lower for w in ["building", "structure", "house", "urban"]):
            return {
                "answer": "Analysis indicates the presence of built-up structures in the central-eastern region of the image. The spectral signature and geometric patterns are consistent with residential or commercial buildings. Approximately 3-5 distinct structures are visible with regular geometric footprints.",
                "bounding_box": [35, 25, 75, 70],
                "confidence": 0.87,
                "detected_objects": ["buildings", "structures", "urban area"]
            }
        elif any(w in q_lower for w in ["water", "river", "lake", "pond", "ocean"]):
            return {
                "answer": "A water body is detected in the lower-left quadrant of the image. The dark spectral response in visible bands and the smooth texture are characteristic of a standing water body, likely a lake or reservoir. The water boundary appears well-defined.",
                "bounding_box": [5, 55, 45, 95],
                "confidence": 0.92,
                "detected_objects": ["water body", "lake"]
            }
        elif any(w in q_lower for w in ["vegetation", "tree", "forest", "green", "crop", "agriculture"]):
            return {
                "answer": "Dense vegetation cover is identified across the northern half of the image. The high reflectance in near-infrared bands suggests healthy, actively photosynthesizing vegetation. The pattern is consistent with either managed agricultural land or natural forest cover.",
                "bounding_box": [10, 5, 90, 50],
                "confidence": 0.89,
                "detected_objects": ["vegetation", "forest", "green cover"]
            }
        elif any(w in q_lower for w in ["road", "path", "highway", "street"]):
            return {
                "answer": "A linear transportation feature is visible running diagonally from the northwest to the southeast of the image. The feature exhibits consistent width and spectral properties characteristic of a paved road surface. Intersection points are visible in the central region.",
                "bounding_box": [15, 10, 85, 85],
                "confidence": 0.78,
                "detected_objects": ["road", "transportation network"]
            }
        else:
            return {
                "answer": f"Analysis of the satellite image reveals a mixed-use landscape with several notable features. The image shows a combination of built-up areas, open spaces, and natural features. Based on the spectral analysis and spatial patterns, the dominant land cover appears to be a mix of urban and semi-urban zones with scattered vegetation patches.",
                "bounding_box": [20, 20, 80, 80],
                "confidence": 0.72,
                "detected_objects": ["mixed land use", "open space", "built-up area"]
            }

    async def analyze(self, image_bytes: bytes, question: str) -> SpecialistResult:
        """
        Main analysis method. Tries Gemini first, then Groq, then mock.
        """
        result = None

        # Try Gemini (primary — has vision)
        result = await self.analyze_with_gemini(image_bytes, question)
        source = "Gemini Vision"

        # Fallback to Groq (text-only)
        if result is None:
            image_info = self._get_image_info(image_bytes)
            result = await self.analyze_with_groq(question, image_info)
            source = "Groq LLM (text-only fallback)"

        # Final fallback: mock response
        if result is None:
            result = self._generate_mock_response(question)
            source = "Mock RS-VLM (offline mode)"

        bbox = result.get("bounding_box")
        evidence_type = "bbox" if bbox else "none"

        return SpecialistResult(
            answer=result.get("answer", "Analysis could not be completed."),
            bounding_box=bbox,
            confidence=result.get("confidence", 0.65),
            evidence_type=evidence_type,
            detail=f"Processed by {source}"
        )


class ChangeDetectionSpecialist:
    """Stub specialist for change detection — returns v2 message."""

    async def analyze(self, image1_bytes: bytes, image2_bytes: bytes, question: str) -> SpecialistResult:
        return SpecialistResult(
            answer="Change Detection is currently in development and will be available in SatQuery AI v2. This specialist will support bi-temporal analysis for detecting land use changes, urban expansion, deforestation, and other temporal phenomena using paired satellite imagery.",
            bounding_box=None,
            confidence=0.0,
            evidence_type="none",
            detail="Change Detection specialist: stub (v2 feature)"
        )


class FusionSpecialist:
    """Stub specialist for Optical+SAR fusion — returns v2 message."""

    async def analyze(self, image_bytes: bytes, question: str) -> SpecialistResult:
        return SpecialistResult(
            answer="Optical+SAR Fusion is currently in development and will be available in SatQuery AI v2. This specialist will enable multi-sensor analysis by combining optical and SAR (Synthetic Aperture Radar) imagery for enhanced feature extraction and all-weather monitoring capabilities.",
            bounding_box=None,
            confidence=0.0,
            evidence_type="none",
            detail="Optical+SAR Fusion specialist: stub (v2 feature)"
        )


# Singleton instances
rs_vlm = RSVLMSpecialist()
change_detection = ChangeDetectionSpecialist()
fusion = FusionSpecialist()
