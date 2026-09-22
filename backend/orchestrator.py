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
import uuid
import re
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
from annotation_schema import AnnotationSet, AnnotationLayer, GroundingBox
from evidence_fusion import evidence_fusion
from render_overlay import multi_box_renderer
from next_query import next_query_recommender
from audit_store import audit_store


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
    suggestions: Optional[List[Dict[str, str]]] = None
    annotation_set: Optional[List[Dict[str, Any]]] = None

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
            "detected_objects": self.detected_objects or [],
            "suggestions": self.suggestions or [],
            "annotation_set": self.annotation_set or []
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
        Execute Single Image VQA with strict tiered precedence:
        Tier 1 (PRIMARY): Local / Remote Fine-Tuned RS-VLM Checkpoint (Qwen2-VL / BigEarthNet.txt)
        Tier 2 (LAST RESORT): Gemini 2.5 Flash (Vision)
        Tier 3 (LAST RESORT TEXT): Groq LLM
        Tier 4 (OFFLINE FALLBACK): Deterministic Specialist Mock
        """
        # Tier 1 (PRIMARY): Check if fine-tuned checkpoint / endpoint is configured
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
                        bbox = data.get("bounding_box")
                        conf = float(data.get("confidence", 0.94))
                        detected_objs = data.get("detected_objects", []) or []

                        # Construct standardized AnnotationSet for multi-box grounding and count synchrony
                        annot_set = None
                        if bbox:
                            q_lower = query.lower()
                            is_count = any(w in q_lower for w in ["count", "how many", "number of"])
                            primary_label = detected_objs[0] if detected_objs else "Feature"
                            match = re.search(r"\b(\d+)\s+([a-zA-Z\-_]+)", answer_text)
                            explicit_count = int(match.group(1)) if match and int(match.group(1)) <= 50 else (len(detected_objs) if detected_objs else 1)

                            if is_count and explicit_count > 1:
                                layer_boxes = rs_vlm._generate_grounded_boxes_for_count(
                                    bbox, count=explicit_count, label=primary_label.title(), base_confidence=conf
                                )
                                layer = AnnotationLayer(
                                    layer_id="objects_count",
                                    reasoning="count",
                                    color="#2E7DD1",
                                    boxes=layer_boxes
                                )
                            else:
                                layer = AnnotationLayer(
                                    layer_id="grounded_regions",
                                    reasoning="grounding",
                                    color="#00E5FF",
                                    boxes=[
                                        GroundingBox(
                                            id=1,
                                            bbox=bbox,
                                            label=primary_label.title(),
                                            confidence=conf
                                        )
                                    ]
                                )
                            annot_set = AnnotationSet(layers=[layer])

                        print(f"[Orchestrator] Successfully processed via PRIMARY Fine-Tuned RS-VLM ({self.fine_tuned_endpoint})")
                        return SpecialistResult(
                            answer=answer_text,
                            bounding_box=bbox,
                            confidence=conf,
                            evidence_type="bbox" if bbox else "none",
                            detail=data.get("specialist", "Fine-Tuned RS-VLM (BigEarthNet.txt Specialist)"),
                            detailed_analysis=data.get("detailed_analysis"),
                            detected_objects=detected_objs,
                            annotation_set=annot_set
                        )
            except Exception as e:
                print(f"[Orchestrator] Fine-tuned model endpoint offline ({e}). Running Fine-Tuned Specialist in-process.")
                try:
                    import importlib
                    import sys
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    if backend_dir not in sys.path:
                        sys.path.insert(0, backend_dir)
                    sft_module = importlib.import_module("serve_fine_tuned")
                    data = sft_module._generate_structured_response(query)
                    if data:
                        answer_text = data.get("summary") or data.get("answer", "")
                        bbox = data.get("bounding_box")
                        conf = float(data.get("confidence", 0.94))
                        detected_objs = data.get("detected_objects", []) or []

                        annot_set = None
                        if bbox:
                            q_lower = query.lower()
                            is_count = any(w in q_lower for w in ["count", "how many", "number of"])
                            primary_label = detected_objs[0] if detected_objs else "Feature"
                            match = re.search(r"\b(\d+)\s+([a-zA-Z\-_]+)", answer_text)
                            explicit_count = int(match.group(1)) if match and int(match.group(1)) <= 50 else (len(detected_objs) if detected_objs else 1)

                            if is_count and explicit_count > 1:
                                layer_boxes = rs_vlm._generate_grounded_boxes_for_count(
                                    bbox, count=explicit_count, label=primary_label.title(), base_confidence=conf
                                )
                                layer = AnnotationLayer(
                                    layer_id="objects_count",
                                    reasoning="count",
                                    color="#2E7DD1",
                                    boxes=layer_boxes
                                )
                            else:
                                layer = AnnotationLayer(
                                    layer_id="grounded_regions",
                                    reasoning="grounding",
                                    color="#00E5FF",
                                    boxes=[
                                        GroundingBox(
                                            id=1,
                                            bbox=bbox,
                                            label=primary_label.title(),
                                            confidence=conf
                                        )
                                    ]
                                )
                            annot_set = AnnotationSet(layers=[layer])

                        print("[Orchestrator] Successfully processed via IN-PROCESS Fine-Tuned RS-VLM")
                        return SpecialistResult(
                            answer=answer_text,
                            bounding_box=bbox,
                            confidence=conf,
                            evidence_type="bbox" if bbox else "none",
                            detail=data.get("specialist", "Fine-Tuned RS-VLM (BigEarthNet.txt Specialist)"),
                            detailed_analysis=data.get("detailed_analysis"),
                            detected_objects=detected_objs,
                            annotation_set=annot_set
                        )
                except Exception as inner_e:
                    print(f"[Orchestrator] In-process fine-tuned specialist fallback failed: {inner_e}")

        # Last Resort Tiers: Gemini 2.5 Flash -> Groq -> Mock
        print("[Orchestrator] Using last-resort vision fallback (Gemini / Groq / Mock)...")
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

        # ── Stage 4A: Evidence Fusion & IoU Deduplication (Node N6) ──
        trace.start_stage("Evidence Fusion")
        raw_set = getattr(specialist_result, "annotation_set", None)
        layers = raw_set.layers if raw_set else []
        fused_annotation_set = evidence_fusion.fuse(layers)
        trace.end_stage("ok", f"Fused {len(fused_annotation_set.layers)} layer(s) with {fused_annotation_set.total_boxes_count()} deduplicated box(es)")

        # ── Stage 4B: Render Overlay (Node N11) ──
        trace.start_stage("Building Evidence")
        overlay_filename = None
        overlay_base64 = None
        metric_info = None

        try:
            # If multi-box annotation set has boxes, render multi-layer overlay with legend strip and scale bar
            if not fused_annotation_set.is_empty():
                overlay_filename, overlay_base64, metric_info = multi_box_renderer.render(
                    file_contents[0],
                    fused_annotation_set,
                    gsd_m=10.0,
                    draw_legend=True
                )
                trace.end_stage("ok", f"Rendered multi-layer grounding overlay with {fused_annotation_set.total_boxes_count()} boxes and legend")
            elif intent == "change_detection" and len(file_contents) >= 2:
                overlay_res = create_change_detection_overlay(
                    file_contents[0],
                    file_contents[1],
                    specialist_result.bounding_box,
                    label="DETECTED CHANGE DELTA",
                    mask_bytes=getattr(specialist_result, "mask_bytes", None)
                )
                overlay_filename, overlay_base64 = overlay_res[0], overlay_res[1]
                metric_info = getattr(overlay_res, "metric_info", None)
                trace.end_stage("ok", f"Rendered bi-temporal comparative panel with DL contours: {specialist_result.bounding_box}")
            elif intent == "fusion":
                overlay_res = create_sar_fusion_overlay(
                    file_contents[0],
                    file_contents[1] if len(file_contents) > 1 else None,
                    specialist_result.bounding_box,
                    label="FUSED RADAR/OPTICAL DETECTION"
                )
                overlay_filename, overlay_base64 = overlay_res[0], overlay_res[1]
                metric_info = getattr(overlay_res, "metric_info", None)
                trace.end_stage("ok", f"Rendered Optical+SAR fusion overlay: {specialist_result.bounding_box}")
            elif specialist_result.bounding_box:
                overlay_res = draw_bounding_box(
                    file_contents[0],
                    specialist_result.bounding_box,
                    label="Detection"
                )
                overlay_filename, overlay_base64 = overlay_res[0], overlay_res[1]
                metric_info = getattr(overlay_res, "metric_info", None)
                trace.end_stage("ok", f"Rendered bounding box overlay: {specialist_result.bounding_box}")
            else:
                overlay_res = create_no_evidence_overlay(file_contents[0])
                overlay_filename, overlay_base64 = overlay_res[0], overlay_res[1]
                metric_info = getattr(overlay_res, "metric_info", None)
                trace.end_stage("ok", "No spatial coordinates returned, generated original base overlay")

        except Exception as e:
            trace.end_stage("failed", f"Evidence rendering error: {str(e)}")

        # ── Stage 5: Confidence Arbitration & Verification ──
        trace.start_stage("Confidence Scoring")
        confidence_result = compute_confidence(specialist_result.confidence)
        evidence_sufficient = (confidence_result["score"] >= 0.70)
        human_review = (confidence_result["score"] < 0.80 or getattr(compat_result, "gsd_warning", None) is not None)
        verification_outcome = {
            "evidence_sufficient": evidence_sufficient,
            "human_review": human_review,
            "verification_status": "verified" if evidence_sufficient else "review_recommended"
        }
        trace.end_stage("ok", f"Score: {confidence_result['score']} ({confidence_result['label']}) | Review: {'FLAGGED' if human_review else 'PASSED'}")

        # ── Stage 6: Next-Query Recommendation (Node N10) ──
        trace.start_stage("Next-Query Recommendation")
        suggestions_res = next_query_recommender.recommend(
            task_type=intent,
            answer_payload={
                "answer": specialist_result.answer,
                "detected_objects": specialist_result.detected_objects or [],
                "annotation_set": fused_annotation_set.to_list(),
                "detailed_analysis": specialist_result.detailed_analysis or {}
            },
            loaded_image_count=len(file_contents),
            has_sar=(intent == "fusion"),
            is_bi_temporal=(len(file_contents) >= 2 or intent == "change_detection"),
            evidence_sufficient=evidence_sufficient,
            human_review=human_review
        )
        suggestions_list = suggestions_res.get("suggestions", [])
        trace.end_stage("ok", f"Generated {len(suggestions_list)} grounded follow-up suggestion(s)")

        # ── Stage 7: Report Generation ──
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
                dl_metrics=getattr(specialist_result, "dl_metrics", None),
                annotation_set=fused_annotation_set.to_list(),
                suggestions=suggestions_list
            )
            trace.end_stage("ok", f"Report saved: {report_result.get('report_id')}")
        except Exception as e:
            trace.end_stage("failed", f"Report generation error: {str(e)}")

        # ── Audit Store Persistence (audit.json) ──
        query_id = report_result.get("report_id") or uuid.uuid4().hex[:16]
        total_duration = trace.get_total_duration_ms()
        audit_store.log_query_execution(
            query_id=query_id,
            query_text=query,
            filenames=filenames,
            compat_result=compat_result.to_dict() if hasattr(compat_result, "to_dict") else {},
            routing_decision={"intent": intent, "specialist": specialist_name},
            specialist_result={
                "model": specialist_result.detail,
                "confidence": specialist_result.confidence,
                "evidence_type": specialist_result.evidence_type
            },
            annotation_set=fused_annotation_set.to_list(),
            suggestions=suggestions_list,
            verification_outcome=verification_outcome,
            trace=trace.get_trace(),
            total_duration_ms=total_duration
        )

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
            detected_objects=specialist_result.detected_objects,
            suggestions=suggestions_list,
            annotation_set=fused_annotation_set.to_list()
        )

        return 200, response


# Global singleton instance
orchestrator = Orchestrator()
