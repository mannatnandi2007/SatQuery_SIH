"""
SatQuery AI — Report Generator
Assembles query results into downloadable JSON reports.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional


# Directory to save reports
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_report(
    query: str,
    image_filenames: List[str],
    answer: str,
    confidence: Dict,
    trace: List[Dict],
    evidence_type: str,
    overlay_filename: Optional[str] = None
) -> Dict:
    """
    Generate a JSON report and save it to disk.

    Returns:
        {"report_id": str, "report_url": str}
    """
    report_id = uuid.uuid4().hex[:16]
    timestamp = datetime.now(timezone.utc).isoformat()

    report_data = {
        "report_id": report_id,
        "generated_at": timestamp,
        "query": {
            "text": query,
            "images": image_filenames,
        },
        "result": {
            "answer": answer,
            "confidence": confidence,
            "evidence": {
                "type": evidence_type,
                "overlay_file": overlay_filename
            }
        },
        "execution_trace": trace,
        "total_duration_ms": sum(t.get("duration_ms", 0) for t in trace),
        "system": {
            "version": "SatQuery AI v0.1.0-prototype",
            "model": "RS-VLM (Gemini-backed)",
            "pipeline": "compatibility → routing → specialist → evidence → report"
        }
    }

    # Save to disk
    report_filename = f"report_{report_id}.json"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    return {
        "report_id": report_id,
        "report_url": f"/report/{report_id}"
    }
