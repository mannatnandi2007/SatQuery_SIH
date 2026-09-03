# SatQuery AI — Prototype PRD
### Team Parallax | SIH 2026 — PS 26167 | Build window: 1 days, 2 people

This PRD scopes the **MVP prototype**, not the full vision in the pitch deck. It's written to be handed section-by-section to an AI coding assistant — each functional requirement below is close to a ready-made prompt.

---

## 1. One-liner

A web app where a user uploads a satellite image, asks a plain-English question about it, and gets back a grounded answer with visual evidence, a confidence score, and a step-by-step trace of how the system got there.

## 2. Goals

- Prove the core loop end-to-end: **upload → validate → route → analyze → grounded answer**.
- Fine-tune and demo **one** working specialist model (RS-VLM: visual question answering + grounding) on a curated subset of the provided dataset.
- Make the two "novelty" claims from the pitch deck visibly real in the UI: **input compatibility checking before execution**, and an **observable execution trace + confidence score** with every answer.

## 3. Non-goals (explicitly cut for this build)

- **Change Detection specialist** and **Optical+SAR Fusion specialist** are NOT fully built. Stub them behind the same UI (see §7.4) — do not spend fine-tuning time here.
- No user accounts/auth, no persistence beyond the current session, no multi-user concurrency handling.
- No cloud deployment required — localhost + tunnel (ngrok/Cloudflare Tunnel) for the live demo is sufficient.
- No production-grade error recovery — handle only the failure modes listed in §8.
- No mobile-responsive polish — desktop demo only.

## 4. Users

Single persona for this prototype: **a judge or evaluator using the live demo**, playing the role of a non-GIS-expert end user. Optimize for a handful of reliable, impressive interactions — not general robustness.

## 5. Core user flow

1. User opens the web app, uploads a satellite image (GeoTIFF/JPG/PNG).
2. User types a natural-language question.
3. **Compatibility Checker** runs instantly (rule-based, no model call) — if the query needs two images (e.g. "what changed") but only one was uploaded, the user gets an immediate, specific error instead of a silent failure.
4. If valid, the UI shows a lightweight live status (`Routing` → `Analyzing` → `Building evidence`).
5. User receives: a direct-language answer, a visual evidence overlay (bounding box/mask on the image), a confidence score, and an expandable execution trace.
6. User can download a JSON/PDF report or ask a follow-up query.

## 6. Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Frontend | React + Next.js (or plain Vite+React if faster to scaffold) | Single-page: upload, query box, results panel |
| Backend | FastAPI (Python) | Async endpoints, serves inference synchronously for MVP |
| Model serving | Local inference via `transformers` + `peft` (no separate serving layer needed for demo scale) | |
| Base model | Qwen2-VL-7B or LLaVA-1.5-7B | Pick whichever has the smoother QLoRA recipe available on the day |
| Fine-tuning | QLoRA (4-bit NF4), via Unsloth or HF `peft`+`bitsandbytes` | Rank 16–32, 2–4 epochs on 200–500 curated examples |
| Image handling | GDAL (for GeoTIFF) + Pillow/OpenCV (for overlay rendering) | |
| Report generation | Basic JSON always; PDF via `weasyprint` if time allows | |

## 7. Functional requirements

### 7.1 Frontend

- Upload widget accepting 1–2 images (toggle or auto-detect based on query intent).
- Text input for the natural-language query.
- Submit triggers `POST /query` (see §9).
- Results panel renders: answer text, image with overlay, confidence badge (e.g. High/Medium/Low + numeric score), collapsible trace list, "Download report" button.
- Error state: if compatibility check fails, show the specific returned reason inline near the upload widget — not a generic error toast.
- Loading state: show named stages (`Routing`, `Analyzing`, `Building evidence`) rather than a bare spinner — this is directly demoing the "observable execution" claim.

### 7.2 Backend — Compatibility Checker

Rule-based, runs before any model call. Checks:
- File type is supported (`.tif`, `.tiff`, `.jpg`, `.png`).
- Image count matches query intent (a "what changed" style query requires 2 images; a "what is this" query requires 1).
- Image is decodable and non-corrupt.
- (If GeoTIFF) has readable geo-metadata via GDAL.

Returns a structured pass/fail with a specific reason string, not a boolean.

### 7.3 Backend — Query Router

Lightweight intent classifier: given the query text, decide `single_image_vqa` vs `change_detection` vs `unsupported`. For the MVP, keyword/regex rules are sufficient (e.g. "changed", "compare", "before/after" → change_detection). Do not spend fine-tuning budget here.

### 7.4 Backend — Specialists

- **RS-VLM (VQA/Grounding)** — the only fully implemented specialist. Loads the fine-tuned checkpoint, takes `(image, question)`, returns `(answer_text, bounding_box_or_mask, raw_confidence)`.
- **Change Detection** — stub. Either return a fixed "feature coming in v2" response, or (stretch goal, Day 2 only) a simple pixel-difference heatmap between the two images with no ML model involved.
- **Optical+SAR Fusion** — stub only, same treatment as above. Do not attempt to build this for the 2-day window.

### 7.5 Backend — Evidence Engine

Takes the specialist's raw output (bounding box or mask coordinates) and renders it as an overlay on the original image (PIL/OpenCV `rectangle`/`polylines`). Returns the overlay as a base64 image or a saved file path the frontend can fetch.

### 7.6 Backend — Confidence Score

Simplest defensible approach for the MVP: average token-level softmax probability from the model's own generation, mapped to a High (>0.8) / Medium (0.5–0.8) / Low (<0.5) label. Don't attempt calibration (ECE tuning) — that's a v2 concern.

### 7.7 Backend — Execution Trace

A list of `{stage, status, duration_ms, detail}` objects built as the request moves through the pipeline (compatibility check → routing → specialist → evidence → answer). Returned alongside the answer, rendered as a collapsible list in the UI.

### 7.8 Backend — Report Generation

Assemble `{query, image_ref, answer, confidence, trace, timestamp}` into a JSON file for download. PDF export is a stretch goal only if time remains on Day 2.

## 8. Error handling (only these cases, no more)

| Case | Behavior |
|---|---|
| Compatibility check fails | Return reason string, no model call made |
| Unsupported/corrupt image | Return clear error, no crash |
| Model inference exceptions | Catch, return a generic "analysis failed" with the exception logged server-side, trace shows the failed stage |
| Oversized image | Resize/tile before inference rather than erroring, if time allows; otherwise cap upload size and reject cleanly |

## 9. API contract

```
POST /compatibility-check
Request:  multipart form { images: File[], query: string }
Response: { valid: boolean, reason: string | null, detected_intent: string }

POST /query
Request:  multipart form { images: File[], query: string }
Response: {
  answer: string,
  confidence: { label: "High"|"Medium"|"Low", score: number },
  evidence: { type: "bbox"|"mask"|"none", overlay_image_url: string },
  trace: [ { stage: string, status: "ok"|"failed"|"skipped", duration_ms: number, detail: string } ],
  report_url: string
}

GET /report/{id}
Response: file download (JSON, PDF if implemented)
```

## 10. Data requirements

- 200–500 curated `(image, question, answer)` triples from the provided dataset, converted to instruction-tuning format:
```json
{"image": "path/to/img.tif", "question": "Is there a body of water in this image?", "answer": "Yes, in the lower left quadrant."}
```
- Include a mix of presence/comparison-style questions and a handful of grounding-style questions (with bounding box annotations) if your source data supports it — grounding is what makes the evidence overlay possible.
- Hold out 10–15 examples as a fixed demo set — these are the ones you rehearse the live demo on (see prior build-plan discussion).

## 11. Success criteria (what "done" means for the demo)

- [ ] 3–5 rehearsed (image, question) pairs return a correct-looking answer with a visible evidence overlay, every time, reliably.
- [ ] Compatibility checker visibly rejects at least one bad input live (e.g. uploading 1 image for a change-detection-style question) with a specific message.
- [ ] Execution trace is visible and expandable in the UI for every successful query.
- [ ] Confidence score is displayed and varies (not hardcoded to one value) across the demo set.
- [ ] Report download works for at least one query.

## 12. Build milestones (maps to the 2-day plan)

- **Day 1 EOD**: fine-tuning running/complete; backend + frontend functional against mocked model output.
- **Day 2, hour 4**: real fine-tuned checkpoint integrated and returning real answers.
- **Day 2, hour 12**: full pipeline integrated, demo set finalized.
- **Day 2, hour 16+**: rehearsal, backup demo video recorded, buffer.

## 13. Out of scope for this prototype (deck-only, not build-only)

Everything else in the pitch deck's architecture and novelty analysis (multi-sensor fusion, bi-temporal change analysis, full calibrated confidence, production compute optimizations, GDAL-based adaptive tiling) remains a **stated roadmap item** — true and defensible to describe to judges, but not something this 1-day build needs to implement.
