"""
SatQuery AI — Orchestrator Engine
Manages the end-to-end processing pipeline:
1. Compatibility validation
2. Dynamic intent routing
3. Tiered specialist execution (Fine-Tuned Checkpoint -> Gemini 2.5 Flash -> Groq -> Mock)
4. Evidence bounding-box normalization & rendering
5. Confidence evaluation & arbitration
6. Execution trace telemetry & report generation
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from compatibility import run_compatibility_check, CompatibilityResult
from router import route_query
from specialists import rs_vlm, change_detection, fusion, SpecialistResult
from evidence import (
    draw_bounding_box,
    create_no_evidence_overlay,
    create_change_detection_overlay,
    create_sar_fusion_overlay
)
from confidence import compute_confidence
from trace import TraceBuilder
from report import generate_report


@dataclass
class OrchestratorResponse:
    error: bool
    answer: str
    confidence: Dict[str, Any]
    evidence: Dict[str, Any]
    trace: List[Dict[str, Any]]
    report_url: Optional[str]
    report_id: Optional[str]
    detailed_analysis: Optional[Dict[str, Any]] = None
    detected_objects: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.error,
            "answer": self.answer,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "trace": self.trace,
            "report_url": self.report_url,
            "report_id": self.report_id,
            "detailed_analysis": self.detailed_analysis,
            "detected_objects": self.detected_objects or []
        }


class Orchestrator:
    """
    Central orchestration engine for SatQuery AI.
    Provides pluggable specialist execution and structured telemetry.
    """

    def __init__(self):
        # Configuration for fine-tuned model checkpoint
        self.fine_tuned_enabled = os.environ.get("USE_FINE_TUNED_MODEL", "false").lower() in ("true", "1", "yes")
        self.fine_tuned_endpoint = os.environ.get("FINE_TUNED_ENDPOINT_URL", "").strip()
        self.fine_tuned_weights_path = os.environ.get("FINE_TUNED_WEIGHTS_PATH", "").strip()

    def check_compatibility(self, filenames: List[str], file_contents: List[bytes], query: str) -> CompatibilityResult:
        """Run pre-flight compatibility check before model execution."""
        return run_compatibility_check(filenames, file_contents, query)

    async def _execute_single_image_vqa(self, image_bytes: bytes, query: str) -> SpecialistResult:
        """
        Execute Single Image VQA with tiered fallback chain:
        1. Local / Remote fine-tuned model (if configured)
        2. Gemini 2.5 Flash (Vision)
        3. Groq LLM (Text fallback with metadata)
        4. Offline Mock
        """
        # Tier 1: Check if fine-tuned checkpoint / endpoint is configured
        if self.fine_tuned_enabled and (self.fine_tuned_endpoint or self.fine_tuned_weights_path):
            try:
                import requests
                import asyncio
                if self.fine_tuned_endpoint:
                    def _call_endpoint():
                        files = {"image": ("scene.png", image_bytes, "image/png")}
                        data = {"query": query}
                        res = requests.post(
                            self.fine_tuned_endpoint,
                            files=files,
                            data=data,
                            timeout=10
                        )
                        return res.json() if res.status_code == 200 else None

                    data = await asyncio.to_thread(_call_endpoint)
                    if data:
                        answer_text = data.get("summary") or data.get("answer", "")
                        return SpecialistResult(
                            answer=answer_text,
                            bounding_box=data.get("bounding_box"),
                            confidence=float(data.get("confidence", 0.94)),
                            evidence_type="bbox" if data.get("bounding_box") else "none",
                            detail=data.get("specialist", "Processed by Fine-Tuned RS-VLM Checkpoint"),
                            detailed_analysis=data.get("detailed_analysis")
                        )
            except Exception as e:
                print(f"[Orchestrator] Fine-tuned model call failed, falling back to Gemini: {e}")

        # Tier 2 -> 3 -> 4: RS-VLM specialist fallback chain
        return await rs_vlm.analyze(image_bytes, query)

    async def process_query(
        self,
        filenames: List[str],
        file_contents: List[bytes],
        query: str
    ) -> Tuple[int, OrchestratorResponse]:
        """
        Execute the complete orchestrator pipeline with fine-grained trace timing.
        Returns: (http_status_code, OrchestratorResponse)
        """
        trace = TraceBuilder()

        # ── Stage 1: Compatibility Check ──
        trace.start_stage("Compatibility Check")
        compat_result = self.check_compatibility(filenames, file_contents, query)

        if not compat_result.valid:
            trace.end_stage("failed", compat_result.reason)
            response = OrchestratorResponse(
                error=True,
                answer=compat_result.reason,
                confidence={"label": "N/A", "score": 0.0},
                evidence={"type": "none", "overlay_image_base64": None, "overlay_image_url": None},
                trace=trace.get_trace(),
                report_url=None,
                report_id=None
            )
            return 400, response

        trace.end_stage("ok", f"Validated {len(filenames)} image(s) for intent: {compat_result.detected_intent}")

        # ── Stage 2: Routing & Intent Classification ──
        trace.start_stage("Routing")
        intent, specialist_name = route_query(query)
        if len(file_contents) >= 2 and intent == "single_image_vqa":
            intent = "change_detection"
            specialist_name = "Bi-Temporal Change Detection"
        trace.end_stage("ok", f"Intent: {intent} → Selected Specialist: {specialist_name}")

        # ── Stage 3: Specialist Execution ──
        trace.start_stage("Analyzing")
        try:
            if intent == "single_image_vqa":
                specialist_result = await self._execute_single_image_vqa(file_contents[0], query)
            elif intent == "change_detection":
                specialist_result = await change_detection.analyze(
                    file_contents[0],
                    file_contents[1] if len(file_contents) > 1 else file_contents[0],
                    query
                )
            elif intent == "fusion":
                specialist_result = await fusion.analyze(
                    file_contents[0],
                    query,
                    sar_bytes=file_contents[1] if len(file_contents) > 1 else None
                )
            else:
                specialist_result = await self._execute_single_image_vqa(file_contents[0], query)

            trace.end_stage("ok", specialist_result.detail)

        except Exception as e:
            trace.end_stage("failed", f"Specialist inference error: {str(e)}")
            response = OrchestratorResponse(
                error=True,
                answer="Analysis failed during specialist model inference. Please try again.",
                confidence={"label": "N/A", "score": 0.0},
                evidence={"type": "none", "overlay_image_base64": None, "overlay_image_url": None},
                trace=trace.get_trace(),
                report_url=None,
                report_id=None
            )
            return 500, response

        # ── Stage 4: Evidence Normalization & Overlay Rendering ──
        trace.start_stage("Building Evidence")
        overlay_filename = None
        overlay_base64 = None
        metric_info = None

        try:
            if intent == "change_detection" and len(file_contents) >= 2:
                overlay_res = create_change_detection_overlay(
                    file_contents[0],
                    file_contents[1],
                    specialist_result.bounding_box,
                    label="DETECTED CHANGE DELTA",
                    mask_bytes=getattr(specialist_result, "mask_bytes", None)
                )
                trace.end_stage("ok", f"Rendered bi-temporal comparative panel with DL contours: {specialist_result.bounding_box}")
            elif intent == "fusion":
                overlay_res = create_sar_fusion_overlay(
                    file_contents[0],
                    file_contents[1] if len(file_contents) > 1 else None,
                    specialist_result.bounding_box,
                    label="FUSED RADAR/OPTICAL DETECTION"
                )
                trace.end_stage("ok", f"Rendered Optical+SAR fusion overlay: {specialist_result.bounding_box}")
            elif specialist_result.bounding_box:
                overlay_res = draw_bounding_box(
                    file_contents[0],
                    specialist_result.bounding_box,
                    label="Detection"
                )
                trace.end_stage("ok", f"Rendered bounding box overlay: {specialist_result.bounding_box}")
            else:
                overlay_res = create_no_evidence_overlay(file_contents[0])
                trace.end_stage("ok", "No spatial coordinates returned, generated original base overlay")

            overlay_filename, overlay_base64 = overlay_res[0], overlay_res[1]
            metric_info = getattr(overlay_res, "metric_info", None)

        except Exception as e:
            trace.end_stage("failed", f"Evidence rendering error: {str(e)}")

        # ── Stage 5: Confidence Arbitration ──
        trace.start_stage("Confidence Scoring")
        confidence_result = compute_confidence(specialist_result.confidence)
        trace.end_stage("ok", f"Raw: {specialist_result.confidence:.2f} → {confidence_result['label']} ({confidence_result['score']})")

        # ── Stage 6: Report Generation ──
        trace.start_stage("Report Generation")
        report_result = {"report_id": None, "report_url": None}
        try:
            report_result = generate_report(
                query=query,
                image_filenames=filenames,
                answer=specialist_result.answer,
                confidence=confidence_result,
                trace=trace.get_trace(),
                evidence_type=specialist_result.evidence_type,
                overlay_filename=overlay_filename,
                detailed_analysis=specialist_result.detailed_analysis,
                model=specialist_result.detail,
                dl_metrics=getattr(specialist_result, "dl_metrics", None)
            )
            trace.end_stage("ok", f"Report saved: {report_result.get('report_id')}")
        except Exception as e:
            trace.end_stage("failed", f"Report generation error: {str(e)}")

        # ── Compile Response ──
        response = OrchestratorResponse(
            error=False,
            answer=specialist_result.answer,
            confidence=confidence_result,
            evidence={
                "type": specialist_result.evidence_type,
                "overlay_image_base64": overlay_base64,
                "overlay_image_url": f"/static/overlays/{overlay_filename}" if overlay_filename else None,
                "metric_info": metric_info
            },
            trace=trace.get_trace(),
            report_url=report_result.get("report_url"),
            report_id=report_result.get("report_id"),
            detailed_analysis=specialist_result.detailed_analysis,
            detected_objects=specialist_result.detected_objects
        )

        return 200, response


# Global singleton instance
orchestrator = Orchestrator()
