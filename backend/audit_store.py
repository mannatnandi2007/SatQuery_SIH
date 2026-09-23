"""
SatQuery AI — Audit Store & Telemetry Logger
Maintains a persistent, append-only JSON ledger (audit.json) recording:
- Input pre-flight validation and GSD ratio
- Routing decisions and latency
- Specialist execution traces and model sources
- Full structured AnnotationSet (multi-box grounding layers)
- Namespaced Suggestion Log (N10 recommendations and click tracking)
- Verification outcomes (evidence sufficiency, human review flags)
- Operator feedback logs (accept, reject, corrections)
"""

import os
import json
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

AUDIT_FILE_PATH = os.path.join(os.path.dirname(__file__), "audit.json")


class AuditStore:
    """
    Thread-safe audit trail logger for SatQuery AI.
    """

    def __init__(self, file_path: str = AUDIT_FILE_PATH):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        """Ensure audit.json exists with valid structure."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "system": "SatQuery AI",
                    "schema_version": "2.1",
                    "records": [],
                    "operator_feedback": [],
                    "suggestion_clicks": []
                }, f, indent=2)

    def log_query_execution(
        self,
        query_id: str,
        query_text: str,
        filenames: List[str],
        compat_result: Dict[str, Any],
        routing_decision: Dict[str, Any],
        specialist_result: Dict[str, Any],
        annotation_set: List[Dict[str, Any]],
        suggestions: List[Dict[str, str]],
        verification_outcome: Dict[str, Any],
        trace: List[Dict[str, Any]],
        total_duration_ms: int
    ):
        """Append a complete, structured query audit record."""
        record = {
            "query_id": query_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": {
                "text": query_text,
                "images": filenames
            },
            "compatibility": compat_result,
            "routing": routing_decision,
            "specialist": specialist_result,
            "annotation_set": annotation_set,
            "suggestion_log": {
                "suggestions_offered": suggestions,
                "clicked_at": None,
                "clicked_suggestion": None
            },
            "verification_outcome": verification_outcome,
            "trace": trace,
            "total_duration_ms": total_duration_ms
        }

        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.setdefault("records", []).append(record)
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[AuditStore] Failed to write query record: {e}")

    def log_suggestion_click(self, query_id: str, suggestion_text: str, task_type: str):
        """Log that a user clicked a suggestion chip (namespaced, UX-only)."""
        click_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_id": query_id,
            "clicked_suggestion": suggestion_text,
            "task_type": task_type
        }

        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.setdefault("suggestion_clicks", []).append(click_event)

                # Also annotate matching record in records array
                for r in reversed(data.get("records", [])):
                    if r.get("query_id") == query_id:
                        s_log = r.setdefault("suggestion_log", {})
                        s_log["clicked_at"] = click_event["timestamp"]
                        s_log["clicked_suggestion"] = suggestion_text
                        break

                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[AuditStore] Failed to log suggestion click: {e}")

    def log_operator_feedback(
        self,
        query_id: str,
        rating: str,
        notes: Optional[str] = None,
        corrected_bbox: Optional[List[float]] = None
    ):
        """Log human-in-the-loop operator feedback (Task 3.3)."""
        feedback_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_id": query_id,
            "rating": rating,  # "accept" | "flag_inaccurate" | "corrected"
            "notes": notes,
            "corrected_bbox": corrected_bbox
        }

        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.setdefault("operator_feedback", []).append(feedback_entry)
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[AuditStore] Failed to log operator feedback: {e}")

    def get_latest_records(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return the latest query audit records."""
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("records", [])[-limit:]
            except Exception:
                return []

    def get_active_learning_queue(self, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Active Learning & Uncertainty Triage (Task 3.4).
        Ranks queries by epistemic uncertainty, low confidence, and human operator flags
        to curate a prioritized queue for downstream model fine-tuning.
        """
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                records = data.get("records", [])
                feedbacks = data.get("operator_feedback", [])
            except Exception as e:
                print(f"[AuditStore] Failed to read for active learning queue: {e}")
                return []

        # Map feedbacks by query_id
        feedback_map = {}
        for fb in feedbacks:
            qid = fb.get("query_id")
            if qid:
                feedback_map[qid] = fb

        triage_candidates = []
        for r in records:
            qid = r.get("query_id", "")
            query_obj = r.get("query", {})
            query_text = query_obj.get("text", "")
            images = query_obj.get("images", [])
            spec = r.get("specialist", {})
            raw_conf = float(spec.get("confidence", 0.85))
            fb = feedback_map.get(qid)

            is_flagged = fb is not None and fb.get("rating") == "flag_inaccurate"
            is_corrected = fb is not None and fb.get("rating") == "corrected"
            is_accepted = fb is not None and fb.get("rating") == "accept"

            # Compute composite uncertainty entropy (0.0 to 1.0)
            # High uncertainty if model had low confidence or operator flagged as inaccurate
            uncertainty = round((1.0 - raw_conf) * 0.6 + (0.4 if (is_flagged or is_corrected) else (0.0 if is_accepted else 0.1)), 3)

            priority = "HIGH" if uncertainty >= 0.50 else ("MEDIUM" if uncertainty >= 0.30 else "LOW")
            triage_reason = []
            if is_flagged:
                triage_reason.append(f"Operator flagged inaccurate: {fb.get('notes') or 'Detection discrepancy'}")
            if is_corrected:
                triage_reason.append("Operator submitted spatial coordinate corrections")
            if raw_conf < 0.75:
                triage_reason.append(f"Low model confidence ({raw_conf:.2f})")
            if not triage_reason:
                triage_reason.append(f"Standard telemetry sample (conf: {raw_conf:.2f})")

            triage_candidates.append({
                "query_id": qid,
                "timestamp": r.get("timestamp"),
                "query_text": query_text,
                "images": images,
                "model": spec.get("model", "Local RS Vision Engine"),
                "confidence": raw_conf,
                "uncertainty_score": min(1.0, uncertainty),
                "priority": priority,
                "reason": " | ".join(triage_reason),
                "operator_status": fb.get("rating") if fb else "unverified",
                "training_candidate": uncertainty >= 0.35
            })

        # Sort highest uncertainty first
        triage_candidates.sort(key=lambda x: x["uncertainty_score"], reverse=True)
        return triage_candidates[:limit]

    def get_adaptation_profile(self) -> Dict[str, Any]:
        """
        Returns dynamic self-adaptation parameters derived from human feedback ledger.
        Used to calibrate detection sensitivity, confidence scaling, and verification bias.
        """
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                feedbacks = data.get("operator_feedback", [])
                records = data.get("records", [])
            except Exception:
                feedbacks = []
                records = []

        total_feedback = len(feedbacks)
        accepts = sum(1 for f in feedbacks if f.get("rating") == "accept")
        flags = sum(1 for f in feedbacks if f.get("rating") == "flag_inaccurate")
        corrections = sum(1 for f in feedbacks if f.get("rating") == "corrected")

        acceptance_rate = round(accepts / total_feedback, 3) if total_feedback > 0 else 1.0

        # Self-adapting calibration bias:
        # If operator has flagged multiple inaccuracies, increase threshold conservatism
        # and slightly dampen overconfident scores by calibration offset
        calibration_offset = 0.0
        if flags > accepts and total_feedback >= 2:
            calibration_offset = -0.06
        elif accepts > flags and total_feedback >= 3:
            calibration_offset = 0.03

        # Sensitivity threshold adjustment for contour filtering
        sensitivity_multiplier = 1.0
        if flags > 0:
            sensitivity_multiplier = max(0.7, 1.0 - (flags * 0.04))

        return {
            "total_queries_recorded": len(records),
            "total_feedback_logged": total_feedback,
            "accepts": accepts,
            "flags": flags,
            "corrections": corrections,
            "acceptance_rate": acceptance_rate,
            "calibration_offset": calibration_offset,
            "sensitivity_multiplier": sensitivity_multiplier,
            "status": "active" if total_feedback > 0 else "calibrating",
            "last_feedback_timestamp": feedbacks[-1].get("timestamp") if feedbacks else None
        }


# Global singleton instance
audit_store = AuditStore()
