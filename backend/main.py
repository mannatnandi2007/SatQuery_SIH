"""
SatQuery AI — Main FastAPI Application
Serves the API endpoints and the frontend.
"""

import os
import json
import uuid
from io import BytesIO
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from audit_store import audit_store
from memory_store import memory_store


from compatibility import run_compatibility_check
from router import route_query, classify_intent
from specialists import rs_vlm, change_detection, fusion
from evidence import draw_bounding_box, create_no_evidence_overlay, OVERLAYS_DIR
from confidence import compute_confidence
from trace import TraceBuilder
from report import generate_report, REPORTS_DIR


app = FastAPI(
    title="SatQuery AI",
    description="Satellite Image Visual Question Answering System",
    version="0.1.0"
)

# CORS — allow frontend to call from any origin in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static overlay images
os.makedirs(OVERLAYS_DIR, exist_ok=True)
app.mount("/static/overlays", StaticFiles(directory=OVERLAYS_DIR), name="overlays")

# Serve reports
os.makedirs(REPORTS_DIR, exist_ok=True)


@app.get("/health")
async def health_check():
    return {
        "message": "SatQuery AI API v0.1.0",
        "status": "running",
        "gemini_ready": bool(rs_vlm.gemini_model),
        "groq_ready": bool(rs_vlm.groq_client)
    }


from orchestrator import orchestrator


@app.post("/compatibility-check")
async def compatibility_check(
    images: List[UploadFile] = File(...),
    query: str = Form(...)
):
    """
    Run compatibility checks before any model inference via Orchestrator.
    Returns structured pass/fail with specific reason.
    """
    filenames = [img.filename for img in images]
    file_contents = [await img.read() for img in images]

    for img in images:
        await img.seek(0)

    result = orchestrator.check_compatibility(filenames, file_contents, query)
    return {
        "valid": result.valid,
        "reason": result.reason,
        "detected_intent": result.detected_intent
    }


@app.post("/query")
async def process_query(
    images: List[UploadFile] = File(...),
    query: str = Form(...)
):
    """
    Full analysis pipeline handled by the Orchestrator:
    1. Pre-flight compatibility
    2. Intent routing & specialist dispatch
    3. Multi-tier execution (Fine-Tuned Checkpoint -> Gemini Vision -> Groq -> Mock)
    4. Evidence rendering & bounding box normalization
    5. Confidence arbitration
    6. Observable execution trace telemetry & report generation
    """
    filenames = [img.filename for img in images]
    file_contents = [await img.read() for img in images]

    status_code, response = await orchestrator.process_query(filenames, file_contents, query)

    if status_code != 200:
        return JSONResponse(status_code=status_code, content=response.to_dict())

    return response.to_dict()


@app.get("/report/{report_id}")
@app.get("/report/{report_id}.{ext}")
async def get_report(report_id: str, format: Optional[str] = None, ext: Optional[str] = None):
    """Download a generated report in JSON, Markdown, PDF, or Word DOCX format."""
    fmt = (ext or format or "json").lower().strip()
    if "." in report_id:
        base, ext_part = report_id.rsplit(".", 1)
        if ext_part.lower() in ["json", "md", "pdf", "docx"]:
            report_id = base
            fmt = ext_part.lower()

    media_types = {
        "json": "application/json",
        "md": "text/markdown; charset=utf-8",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    if fmt not in media_types:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{fmt}'. Supported formats: json, md, pdf, docx")

    filename = f"report_{report_id}.{fmt}"
    report_path = os.path.join(REPORTS_DIR, filename)

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail=f"Report file '{filename}' not found")

    download_name = f"satquery_report_{report_id}.{fmt}"
    return FileResponse(
        report_path,
        media_type=media_types[fmt],
        filename=download_name
    )


# ─── Operator Feedback & Telemetry Endpoints ──────────────────────

class FeedbackRequest(BaseModel):
    query_id: str
    rating: str  # "accept" | "flag_inaccurate" | "corrected"
    notes: Optional[str] = None
    corrected_bbox: Optional[List[float]] = None

    def validate_rating(self):
        valid_ratings = {"accept", "flag_inaccurate", "corrected"}
        if self.rating not in valid_ratings:
            raise ValueError(f"Invalid rating '{self.rating}'. Must be one of: {valid_ratings}")

class SuggestionClickRequest(BaseModel):
    query_id: str
    suggestion_text: str
    task_type: str


@app.post("/feedback")
async def record_feedback(payload: FeedbackRequest):
    """
    Operator feedback endpoint (Task 3.3).
    Captures human-in-the-loop ratings, notes, and corrected coordinates.
    """
    try:
        payload.validate_rating()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    audit_store.log_operator_feedback(
        query_id=payload.query_id,
        rating=payload.rating,
        notes=payload.notes,
        corrected_bbox=payload.corrected_bbox
    )

    # Automatically record into Exemplar Memory Store to aid future queries and Colab retraining
    records = audit_store.get_latest_records(limit=30)
    matched_query = ""
    for r in records:
        if r.get("query_id") == payload.query_id:
            matched_query = r.get("query", {}).get("text", "")
            break

    memory_store.record_exemplar(
        image_bytes=None,
        query=matched_query or payload.query_id,
        rating=payload.rating,
        notes=payload.notes,
        corrected_bbox=payload.corrected_bbox
    )

    return {
        "status": "success",
        "message": f"Feedback '{payload.rating}' logged for query {payload.query_id} (exemplar memory updated)"
    }


@app.post("/suggestion/click")
async def record_suggestion_click(payload: SuggestionClickRequest):
    """
    Asynchronous telemetry endpoint for suggestion chip taps (Feature 1).
    Logs suggestion interaction without entering promotion-gate signal.
    """
    audit_store.log_suggestion_click(
        query_id=payload.query_id,
        suggestion_text=payload.suggestion_text,
        task_type=payload.task_type
    )
    return {
        "status": "recorded",
        "query_id": payload.query_id
    }


@app.get("/audit")
async def get_audit_trail(limit: int = 15):
    """Retrieve the latest records from audit.json."""
    records = audit_store.get_latest_records(limit=limit)
    return {
        "count": len(records),
        "records": records
    }


@app.get("/active-learning/queue")
async def get_active_learning_queue(limit: int = 25):
    """
    Active Learning & Uncertainty Triage Endpoint (Task 3.4).
    Returns prioritized high-entropy and operator-flagged queries for fine-tuning triage.
    """
    queue = audit_store.get_active_learning_queue(limit=limit)
    return {
        "status": "ready",
        "count": len(queue),
        "queue": queue
    }


@app.get("/active-learning/export-dataset")
async def export_active_learning_dataset():
    """
    Exports queued active learning exemplars as a Colab-ready BigEarthNet JSON dataset.
    One-click export directly loadable into training/finetune_rsvlm_colab.ipynb!
    """
    export_path = memory_store.export_colab_dataset()
    if not os.path.exists(export_path):
        raise HTTPException(status_code=404, detail="Dataset not ready")
    return FileResponse(
        export_path,
        media_type="application/json",
        filename="active_learning_colab_dataset.json"
    )


@app.get("/memory/stats")
async def get_memory_stats():
    """Returns instant exemplar memory cache statistics."""
    return {
        "status": "ready",
        "stats": memory_store.get_stats()
    }


@app.get("/self-adapt/status")
async def get_self_adaptation_status():
    """
    Returns current self-adapting calibration profile and operator metrics.
    """
    profile = audit_store.get_adaptation_profile()
    mem_stats = memory_store.get_stats()
    return {
        "status": "active",
        "profile": profile,
        "exemplar_memory": mem_stats
    }


@app.post("/compare-baseline")
async def compare_baseline(
    image: UploadFile = File(...),
    query: str = Form(...)
):
    """
    Optional baseline comparison endpoint:
    Runs external Gemini Vision strictly for comparing against local SatQuery output.
    Does NOT affect normal /query execution.
    """
    image_bytes = await image.read()
    baseline_result = await rs_vlm.compare_with_baseline(image_bytes, query)
    if not baseline_result:
        return {
            "available": False,
            "message": "Baseline Gemini API is not configured or reached quota."
        }
    return {
        "available": True,
        "baseline_model": "Gemini 2.5 Flash",
        "result": baseline_result
    }


# ─── Startup ──────────────────────────────────────────────────────


@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("  SatQuery AI - Satellite Image VQA System")
    print("  Version: 0.1.0-prototype")
    print("=" * 60)
    print(f"  Gemini API: {'[OK] Ready' if rs_vlm.gemini_model else '[X] Not configured'}")
    print(f"  Groq API:   {'[OK] Ready' if rs_vlm.groq_client else '[X] Not configured'}")
    print(f"  Overlays:   {OVERLAYS_DIR}")
    print(f"  Reports:    {REPORTS_DIR}")
    print("=" * 60)


# ─── Serve Frontend & Static Assets ──────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
SAMPLES_DIR = os.path.join(FRONTEND_DIR, "samples")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")
DIST_ASSETS_DIR = os.path.join(DIST_DIR, "assets")

if os.path.exists(SAMPLES_DIR):
    app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

if os.path.exists(DIST_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=DIST_ASSETS_DIR), name="assets")

NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}

@app.get("/")
@app.get("/app")
async def serve_frontend():
    """Serve the main frontend HTML page with no-cache headers."""
    # Check if compiled React SPA exists in dist/
    dist_index = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index, media_type="text/html", headers=NO_CACHE_HEADERS)

    # Fallback to frontend/index.html
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html", headers=NO_CACHE_HEADERS)
    return {"error": "Frontend not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
