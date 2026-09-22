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


# Global singleton instance
audit_store = AuditStore()
