"""
SatQuery AI — Main FastAPI Application
Serves the API endpoints and the frontend.
"""

import os
import json
import uuid
from io import BytesIO
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

if os.path.exists(SAMPLES_DIR):
    app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}

@app.get("/")
@app.get("/app")
async def serve_frontend():
    """Serve the main frontend HTML page with no-cache headers."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html", headers=NO_CACHE_HEADERS)
    return {"error": "Frontend not found"}

@app.get("/style.css")
async def serve_css():
    css_path = os.path.join(FRONTEND_DIR, "style.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css", headers=NO_CACHE_HEADERS)

@app.get("/app.js")
async def serve_js():
    js_path = os.path.join(FRONTEND_DIR, "app.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript", headers=NO_CACHE_HEADERS)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
