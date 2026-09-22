# SatQuery AI — Prototype Engineering Tasks & Phase Roadmap

**Version:** 2.0  
**Status:** In Progress  
**Track Owners:**
- **JEV-JEPA Representation Engine**: Khushal & Aryan
- **UI / UX & Hallmark Frontend**: Aryan
- **GSD Normalisation Engine**: Madhura & Dipesh
- **Fine-Tuning & Self-Adapting Loop**: Aakansha & Mannat

---

## 1. Team Assignment Matrix & Track Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               TRACK RESPONSIBILITY MATRIX                              │
├─────────────────────────┬────────────────────────────┬─────────────────────────────────┤
│ Track                   │ Assignees                  │ Core Deliverables               │
├─────────────────────────┼────────────────────────────┼─────────────────────────────────┤
│ JEV-JEPA Representation │ Khushal & Aryan            │ EO Latent Encoder, Masked Patch │
│                         │                            │ Predictor, Latent Change Metric │
├─────────────────────────┼────────────────────────────┼─────────────────────────────────┤
│ UI / UX Workbench       │ Aryan                      │ Hallmark Telemetry Interface,   │
│                         │                            │ Dual Canvas, 8-State Components │
├─────────────────────────┼────────────────────────────┼─────────────────────────────────┤
│ GSD Normalisation       │ Madhura & Dipesh           │ Scale Detection, Anti-Aliased   │
│                         │                            │ Resampling, Metric Scale Bar    │
├─────────────────────────┼────────────────────────────┼─────────────────────────────────┤
│ Fine-Tuning & Adaptive  │ Aakansha & Mannat          │ RS-VLM QLoRA Checkpoint,        │
│ Loop                    │                            │ Feedback Ingestion, AL Queue    │
└─────────────────────────┴────────────────────────────┴─────────────────────────────────┘
```

---

## 2. Chronological Phase Breakdown

### Phase 1: Foundations, Preprocessing & Baseline Normalisation Setup
*Objective: Prepare datasets, implement spatial resolution normalization baselines, scaffold JEV-JEPA encoder, and configure the Hallmark design tokens.*

#### Track A: GSD Normalisation (Madhura & Dipesh)
- [x] **Task 1.1: GSD Metadata Extractor (`backend/gsd_normalizer.py`)**
  - **Inputs:** GeoTIFF raster bytes, PNG/JPG with optional EXIF/XML header tags.
  - **Outputs:** Structured metadata dictionary: `{detected_gsd_m: float, sensor: str, crs: str, dimensions: (int, int)}`.
  - **Criteria:** Correctly reads pixel resolution for Sentinel-2 (10m/20m/60m), Landsat 8 (15m/30m), and falls back gracefully to manual input for plain JPG/PNG.
- [x] **Task 1.2: Spatial Resolution Resampling Engine**
  - **Inputs:** Image tensor or PIL image, source GSD, target canonical GSD (default: $10.0\text{m/px}$).
  - **Outputs:** Resampled raster preserving spatial aspect ratio and high-frequency edge gradients (bicubic or Lanczos anti-aliased).
  - **Criteria:** Eliminates scale-induced artifacts without introducing ringing along water/land or runway boundaries.

#### Track B: Fine-Tuning & Self-Adapting Setup (Aakansha & Mannat)
- [x] **Task 1.3: Remote Sensing VQA Dataset Curation (`training/data/`)**
  - **Inputs:** BigEarthNet, RSIVQA, or curated GeoTIFF scenes.
  - **Outputs:** Formatted instruction-tuning dataset `bigearthnet_vqa_grounding.json` with $(N=500)$ curated pairs containing spatial bounding tags `[ymin, xmin, ymax, xmax]`.
  - **Criteria:** Validated schema, balanced distribution across water bodies, urban ports, airports, agricultural parcels, and industrial facilities.
- [x] **Task 1.4: Evaluation Baseline & ECE Harness**
  - **Inputs:** Base vision-language model (Qwen2-VL-7B or LLaVA-1.5-7B).
  - **Outputs:** Evaluation script computing Grounding IoU, VQA Accuracy, and Expected Calibration Error (ECE).
  - **Criteria:** Generates reproducible zero-shot baseline metrics before LoRA fine-tuning.

#### Track C: JEV-JEPA Representation Engine (Khushal & Aryan)
- [x] **Task 1.5: JEV-JEPA Architecture Definition (`backend/jepa_engine.py`)**
  - **Inputs:** Pre-processed multispectral/optical scene patches ($16 \times 16$ or $14 \times 14$).
  - **Outputs:** Vision Transformer (ViT) latent encoder producing patch representations $z \in \mathbb{R}^{B \times N \times D}$ ($D=768$).
  - **Criteria:** Non-generative architecture without pixel decoders; verifies forward pass execution under $< 100\text{ms}$ on GPU.
- [x] **Task 1.6: Spatial Masking Strategy**
  - **Inputs:** Input scene patch grid.
  - **Outputs:** Multi-block context and target masks (4 context blocks, 2 target blocks).
  - **Criteria:** Context patches pass to encoder; target patches predicted purely in latent feature space.

#### Track D: UI / UX Hallmark Architecture (Aryan)
- [x] **Task 1.7: Hallmark Design System Setup (`frontend/style.css`)**
  - **Inputs:** `UIrules.md` requirements and color token specifications.
  - **Outputs:** Pure CSS design token system implementing high-contrast industrial dark mode (`--color-paper`, `--color-rule`, `--color-accent`, `--font-display`, `--font-mono`).
  - **Criteria:** Completely purge all 20 banned patterns (no purple/blue gradients, no Inter-everywhere, no Space Grotesk/Instrument Serif, no glassmorphism).
- [x] **Task 1.8: Telemetry Workbench Shell (`frontend/index.html`)**
  - **Inputs:** Wireframe for dual-canvas workspace (Scene view + Evidence overlay view).
  - **Outputs:** Responsive semantic HTML layout with header status bar, stage telemetry drawer, and inspector sidebar.
  - **Criteria:** Passes initial Hallmark anti-slop visual check; zero emojis in headings, zero decorative badge clutter.

---

### Phase 2: Core Engineering & Specialist Model Tracks
*Objective: Train the specialist model, implement JEPA latent change detection, integrate GSD scale-aware pre-flight checks, and build interactive workbench controls.*

#### Track A: GSD Normalisation (Madhura & Dipesh)
- [x] **Task 2.1: Pre-flight Compatibility GSD Arbitration (`backend/compatibility.py`)**
  - **Inputs:** Dual-image uploads for change detection or multi-sensor comparison.
  - **Outputs:** Cross-image GSD ratio and compatibility status (flags warning if GSD ratio $> 3.5\times$, rejects if $> 6.0\times$).
  - **Criteria:** Prevents invalid change detection across incompatible scales (e.g. 60m Sentinel vs 0.3m Drone) without automated decimation.
- [x] **Task 2.2: Metric Scale Bar & Real-World Dimensions (`backend/evidence.py`)**
  - **Inputs:** Bounding box pixel dimensions $[w, h]$, normalized image GSD.
  - **Outputs:** Physical metric calculation ($L = w \times \text{GSD}$, $\text{Area} = w \times h \times \text{GSD}^2$) and visual scale bar rendering.
  - **Criteria:** Overlays metric scale bar (e.g., "$100\text{ m}$") accurately calibrated to the image's coordinate reference.

#### Track B: Fine-Tuning & Self-Adapting Loop (Aakansha & Mannat)
- [x] **Task 2.3: RS-VLM QLoRA Fine-Tuning Execution (`training/finetune_rsvlm_colab.ipynb`)**
  - **Inputs:** Base model checkpoint + curated instruction dataset (`training/data/`).
  - **Outputs:** Optimized LoRA adapter pipeline & export notebook (`training/finetune_rsvlm_colab.ipynb`), target weight path (`backend/weights/satquery_rsvlm_lora/`).
  - **Criteria:** 4-bit NF4 quantization setup, rank $r=32$, $\alpha=64$, training pipeline with grounding validation loss calculation.
- [x] **Task 2.4: Local Inference Server Integration (`backend/serve_fine_tuned.py`)**
  - **Inputs:** LoRA adapter and base model loaded via `peft` and `transformers`.
  - **Outputs:** FastAPI endpoint serving structured VQA predictions with bounding box tags (`/v1/rsvlm/predict`).
  - **Criteria:** Standalone server with fallback detection when offline or weights not yet generated.

#### Track C: JEV-JEPA Representation Engine (Khushal & Aryan)
- [x] **Task 2.5: JEV-JEPA Masked Predictor Pipeline (`backend/jepa_engine.py`)**
  - **Inputs:** Context latent vectors and target spatial positional encodings.
  - **Outputs:** Predicted target latent vectors $\hat{z}_{\text{target}}$ via `JEVJEPAPredictor`.
  - **Criteria:** Smooth cosine distance loss in latent embedding space; spatial mixture of context with positional guidance.
- [x] **Task 2.6: Latent-Space Change Detection Specialist (`backend/dl_models.py`)**
  - **Inputs:** Aligned bi-temporal scene embeddings $z_{T1}$ and $z_{T2}$.
  - **Outputs:** Spatial feature distance heatmap matrix $D(i, j) = 1 - \cos(z_{T1}^{(i,j)}, z_{T2}^{(i,j)})$ and clustered change polygons fused with Siamese CD.
  - **Criteria:** Successfully isolates significant ground changes while filtering illumination/shadow noise.

#### Track D: UI / UX Hallmark Architecture (Aryan)
- [x] **Task 2.7: 8-State Interactive Components (`frontend/app.js`, `frontend/style.css`)**
  - **Inputs:** Design tokens and component specifications.
  - **Outputs:** Complete 8-state styling for: `default`/`idle`, `hover`, `focus-visible`, `active`, `disabled`, `loading`, `error`, and `success`/`dirty`.
  - **Criteria:** Zero button fade animations; crisp 1px offset `:active` state; high-contrast focus rings.
- [x] **Task 2.8: Dual-Canvas Geospatial Inspector (`frontend/index.html`, `frontend/app.js`)**
  - **Inputs:** Uploaded raw scene + rendered evidence overlay.
  - **Outputs:** Multi-mode canvas (`evidence`, `raw`, `split`), real-time reticle coordinates tracker, and GSD ground-meter calculator.
  - **Criteria:** Clean monospace reticle telemetry, tactical crosshair reticles, zero cursor-following glow beams.

#### Pending Manual Action Items (Phase 2)
- [ ] **Task 2.M1: Execute QLoRA Training Job on Colab GPU (Aakansha & Mannat)**
  - **Inputs:** [`training/finetune_rsvlm_colab.ipynb`](file:///c:/Users/nandi/Desktop/SATQuery/training/finetune_rsvlm_colab.ipynb) and [`training/data/bigearthnet_vqa_grounding.json`](file:///c:/Users/nandi/Desktop/SATQuery/training/data/bigearthnet_vqa_grounding.json).
  - **Action:** Open notebook in Google Colab (T4 or A100 GPU runtime), upload dataset, execute 4-bit NF4 quantized training loop with LoRA ($r=32, \alpha=64$).
  - **Agent Step-by-Step Run Guide (for Aakansha's Agent):**
    1. *Colab Session Setup*: Open Google Colab (`https://colab.research.google.com`), select `File` > `Upload notebook`, and choose `training/finetune_rsvlm_colab.ipynb`.
    2. *GPU Hardware Selection*: Navigate to `Runtime` > `Change runtime type` > choose **T4 GPU** (or A100 if Colab Pro is available) > click Save.
    3. *Data File Ingestion*: Open Colab left-side File drawer (folder icon), and upload `training/data/bigearthnet_vqa_grounding.json` to `/content/bigearthnet_vqa_grounding.json`.
    4. *Dependency Installation*: Execute Cell 1 (`!pip install -q transformers peft bitsandbytes accelerate datasets`). Verify CUDA is detected with `torch.cuda.is_available()`.
    5. *Execute Training Loop*: Run the cells in sequence:
       - 4-bit NF4 Quantization loading (`Qwen/Qwen2-VL-7B-Instruct` or `Qwen/Qwen2-VL-2B-Instruct`)
       - LoRA configuration setup ($r=32, \alpha=64$, targeting `q_proj`, `v_proj`, `k_proj`, `o_proj`)
       - Dataset mapping and tokenization
       - SFT / Training execution (monitor loss dropping from ~2.6 down to < 0.6)
    6. *Export Artifacts*: Ensure the final export cell completes:
       - Output directory created: `/content/satquery_rsvlm_lora/`
       - Contains `adapter_model.safetensors` and `adapter_config.json`.
    7. *Download Artifacts*: Download `adapter_model.safetensors` and `adapter_config.json` to your local machine.
  - **Criteria:** Loss converges, validation IoU evaluates, and exports `adapter_model.safetensors` and `adapter_config.json`.
- [ ] **Task 2.M2: Deploy Trained LoRA Weights to Local Backend (Aakansha & Mannat)**
  - **Inputs:** Exported weights from Colab run.
  - **Action:** Place `adapter_model.safetensors` and `adapter_config.json` inside [`backend/weights/satquery_rsvlm_lora/`](file:///c:/Users/nandi/Desktop/SATQuery/backend/weights/satquery_rsvlm_lora/).
  - **Agent Step-by-Step Deployment Guide (for Aakansha's Agent):**
    1. *Create Directory*: Ensure directory exists: `mkdir -p backend/weights/satquery_rsvlm_lora`
    2. *Place Weight Files*: Move the two downloaded files into the repository:
       - `backend/weights/satquery_rsvlm_lora/adapter_model.safetensors`
       - `backend/weights/satquery_rsvlm_lora/adapter_config.json`
    3. *Start Serving Microservice*: In a terminal window from `backend/`:
       ```bash
       python serve_fine_tuned.py
       ```
       (The service will start on port 8001).
    4. *Verify Weight Health Endpoint*: Open browser or run curl:
       ```bash
       curl http://localhost:8001/health
       ```
       Verify the JSON response has:
       - `"status": "ready"`
       - `"weights_loaded": true`
       - `"adapter_path": ".../backend/weights/satquery_rsvlm_lora"`
    5. *End-to-End Test*: Trigger a test query to verify live inference:
       ```bash
       python -c "import requests; r = requests.post('http://localhost:8001/query', data={'query': 'Detect all port facilities'}); print(r.json())"
       ```
  - **Criteria:** `backend/serve_fine_tuned.py` successfully initializes the live PEFT adapter on startup without falling back to mock mode.
- [ ] **Task 2.M3: Remote Vision Cloud API Keys Configuration (Optional) (All / User)**
  - **Inputs:** User API credentials for Gemini and Groq.
  - **Action:** Set `GEMINI_API_KEY` and/or `GROQ_API_KEY` in [`backend/.env`](file:///c:/Users/nandi/Desktop/SATQuery/backend/.env).
  - **Criteria:** Remote cloud vision specialist activates for secondary multi-tier arbitration.
- [ ] **Task 2.M4: Dual-Canvas Geospatial Inspector Visual QA (Aryan)**
  - **Inputs:** Web browser pointing to [`frontend/index.html`](file:///c:/Users/nandi/Desktop/SATQuery/frontend/index.html) with running backend (`localhost:8000`).
  - **Action:** Test preset scenes, toggle between Evidence / Raw / Split dual-view, hover over canvas to verify coordinate (`COORD`), ground distance (`GROUND`), and GSD meter readouts, and verify all 8 button states.
  - **Criteria:** Reticle tracks smoothly at 60fps; no visual glitches or banned UI patterns.

---

### Phase 3: Integration, Spatial Calibration, Multi-Box Grounding & Recommendation
*Objective: Wire all components into the central orchestrator, implement multi-box visual grounding (N11), next-query recommendation (N10), closed-loop feedback pipeline, and generate rich multi-format telemetry reports.*

#### Track A: Cross-Pipeline Orchestration & Recommendation (Khushal, Aryan, Madhura, Dipesh, Aakansha, Mannat)
- [x] **Task 3.1: Orchestrator Pipeline Integration (`backend/orchestrator.py`)**
  - **Inputs:** Raw multipart request from `/query`.
  - **Outputs:** Unified execution pipeline executing:
    $$\text{Compatibility} \to \text{GSD Normalizer} \to \text{JEV-JEPA Latents} \to \text{Specialist Exec} \to \text{Evidence Fusion (N6)} \to \text{Verify Decision (N7)} \to \text{Final Answer (N9)} \parallel \text{Render Overlay (N11)} \to \text{Suggest Next Query (N10)}$$
  - **Criteria:** Total synchronous pipeline latency $< 2000\text{ms}$ on GPU; structured error fallback on any sub-component failure.
- [x] **Task 3.2: Multi-Sensor Alignment Specialist (`backend/specialists.py`)**
  - **Inputs:** Heterogeneous inputs (e.g. Optical RGB + Sentinel-1 SAR).
  - **Outputs:** Coregistered dual-band visualization and cross-modal reasoning.
  - **Criteria:** Returns pseudo-color SAR fusion overlay highlighting high-dielectric/metallic structures (ships, bridges).
- [x] **Task 3.8: Next-Query Recommendation Engine Node N10 (`backend/next_query.py`)**
  - **Inputs:** `task_type` (T1–T6), structured answer payload (entities, counts, boxes), `evidence_sufficient` / `human_review` flags, loaded imagery context, rolling history.
  - **Outputs:** Structured JSON payload with 2–4 ranked suggestions: `{"suggestions": [{"text": "...", "task_type": "..."}]}`.
  - **Criteria:** Grounded task-transition table, sensor-context gating (no temporal queries if 1 image), entity/numeric template filler, evidence-priority ranking.
- [x] **Task 3.9: Extended Annotation Set Schema & Specialist Adoption (`backend/annotation_schema.py`, `backend/specialists.py`)**
  - **Inputs:** Multi-specialist detections from T1, T3, T4/T5, T6.
  - **Outputs:** Standardized `AnnotationSet` containing distinct `AnnotationLayer` objects with reasoning tags (`count`, `change`, `grounding`, `sar_anomaly`), unique colors, and sequential box numbering.
  - **Criteria:** Synchronized count (text count and box count derived from identical detections), ChangeFormer/Siamese connected components, Grounding DINO wrapping.
- [x] **Task 3.10: Evidence Fusion IoU Deduplication & Layer Aggregation (`backend/evidence_fusion.py`)**
  - **Inputs:** Candidate annotation layers from specialists.
  - **Outputs:** Fused `AnnotationSet` with IoU deduplication ($\text{IoU} \ge 0.50$), retaining higher-confidence boxes and sequential 1-based indexing per layer.
  - **Criteria:** Clean cross-specialist arbitration without duplicate box clutter.

#### Track B: Self-Adapting Feedback & Audit Trail (Aakansha & Mannat)
- [x] **Task 3.3: Operator Feedback Endpoint (`backend/main.py`, `backend/audit_store.py`)**
  - **Inputs:** `POST /feedback` with query ID, rating (`accept` / `flag_inaccurate` / `corrected`), operator notes, corrected bounding box.
  - **Outputs:** Persistent `audit.json` log with namespaced operator feedback ledger.
  - **Criteria:** Real-time feedback ingestion with zero impact on query endpoint throughput.
- [x] **Task 3.4: Active Learning & Uncertainty Triage (`backend/audit_store.py`)**
  - **Inputs:** Model token probabilities, grounding confidence, and operator feedback logs.
  - **Outputs:** Prioritized queue of hard-negative or high-entropy queries in `audit.json` for retraining triage.
  - **Criteria:** Successfully filters and ranks the top 10% most ambiguous queries for model refinement.
- [x] **Task 3.12: Dual Audit Schema (`audit.json` / `backend/audit_store.py`)**
  - **Inputs:** Full query telemetry, validation outcome, routing decision, specialist metrics, `annotation_set`, and `suggestion_log`.
  - **Outputs:** Append-only structured JSON log with namespaced suggestion tracking (`POST /suggestion/click`) and reproducibility trails.
  - **Criteria:** Non-gating telemetry: suggestions and thumbs feedback never contaminate dual-gate model promotion checks.

#### Track C: Evidence, Scale Calibration & Multi-Box Overlay (Madhura, Dipesh & Aryan)
- [x] **Task 3.5: GSD-Calibrated Evidence Overlays (`backend/evidence.py`)**
  - **Inputs:** Specialist bounding box predictions + normalized GSD metadata.
  - **Outputs:** Rendered overlay image with highlighted target regions, category label pills, and verified metric dimensions.
  - **Criteria:** Crisp high-resolution PNG overlay without blurred borders or low-contrast text.
- [x] **Task 3.11: Multi-Layer Overlay Rendering Node N11 (`backend/render_overlay.py`)**
  - **Inputs:** Base GSD-normalized raster, fused `AnnotationSet`.
  - **Outputs:** Color-coded multi-layer box overlay, numbered labels, metric scale bar, and industrial legend strip (e.g. `🔵 Count — 14 buildings   🔴 Likely new — 3 structures`).
  - **Criteria:** Conditional trigger (skips if zero boxes), single flattened PNG output + preserved raw structured payload for client-side toggling.

#### Track D: UI Telemetry, Suggestion Chips & Chat Surface (Aryan)
- [x] **Task 3.6: Step-by-Step Observable Telemetry Drawer (`frontend/app.js`)**
  - **Inputs:** Structured `trace` array returned by backend.
  - **Outputs:** Collapsible real-time timeline displaying stage duration (ms), status chip (`OK` / `WARN` / `FAIL`), and diagnostic parameters.
  - **Criteria:** Stage-by-stage progression rendered without generic spinners or fade-in scroll animations.
- [x] **Task 3.7: In-UI Operator Feedback Modal / Drawer (`frontend/index.html`, `frontend/app.js`)**
  - **Inputs:** Displayed query result.
  - **Outputs:** Inline feedback controls: "Accept Verification", "Flag Inaccurate" with instant confirmation chip.
  - **Criteria:** Submits to `POST /feedback` and displays instant confirmation chip.
- [x] **Task 3.13: Tappable Suggestion Chips & Gradio Chat QA (`frontend/app.js`, `frontend/index.html`, `backend/gradio_app.py`)**
  - **Inputs:** `data.suggestions` array returned by Node N10.
  - **Outputs:** Hallmark-compliant suggestion chips rendered under Executive Summary; clicking re-submits text as a new user query through N1 and logs click asynchronously to `POST /suggestion/click`. Standalone Gradio interface for conversational QA.
  - **Criteria:** Instant query re-population and execution with zero page refresh; tactile 1px active displacement.

---

### Phase 4: Telemetry Polish, System Evaluation & Demo Readiness
*Objective: Conduct anti-slop design audit, execute golden demo rehearsals, generate evaluation reports, and finalize repository documentation.*

#### All Tracks
- [x] **Task 4.1: Hallmark Anti-AI-Slop Comprehensive Audit (Aryan)**
  - **Check:** Verify all 20 banned UI patterns are completely absent across all CSS, HTML, and JS files.
  - **Check:** Responsive testing across 320px, 375px, 768px, and 1440px viewports (zero horizontal scroll, `overflow-x: clip`).
  - **Deliverable:** UI audit checklist signed off. Zero purple/blue gradients, zero unstyled libraries, strictly roman headings, monospace tabular numbers.
- [x] **Task 4.2: Automated Integration & Scene Verification Suite (`backend/tests/test_pipeline_e2e.py`)**
  - **Check:** Test automated pipeline across canonical satellite scenes:
    1. *Airport Runway Inspection* (High-res optical, object counting & length estimation).
    2. *Urban Harbor & Cargo Vessel Grounding* (Sentinel-2 10m, vessel localization).
    3. *Agricultural Parcel Vegetation Health* (Multi-spectral NDVI analysis).
    4. *Bi-Temporal Port Infrastructure Change* (T1 vs T2 change detection via JEPA latents).
    5. *Maritime Vessel Detection via SAR Fusion* (Sentinel-1 SAR + Optical coregistration).
  - **Deliverable:** 13/13 unit and integration tests passing with 100% success rate (`Ran 13 tests in 1.324s - OK`).
- [x] **Task 4.3: Multi-Format Report Generator Verification (Madhura & Dipesh)**
  - **Check:** Verify `/report/{id}` outputs accurate JSON, Markdown, PDF, and Word DOCX reports containing GSD metadata, annotation set layers, suggestions, and complete telemetry traces.
  - **Deliverable:** Verified multi-format export with embedded visual evidence and metric scale tables.
- [x] **Task 4.4: Self-Adapting Loop Validation (Aakansha & Mannat)**
  - **Check:** Verified feedback logging to `audit.json` (`POST /feedback`), async suggestion click tracking (`POST /suggestion/click`), and query history preservation.
  - **Deliverable:** Validated audit ledger schema version 2.1 in `backend/audit.json`.
- [x] **Task 4.5: Final Documentation & Presentation Walkthrough (Khushal & Aryan)**
  - **Check:** Updated `WALKTHROUGH.md` with complete 11-stage pipeline architecture diagram (Mermaid), N10/N11 data contracts, and quick-start instructions.

---

## 3. Pending Manual Action Items (Human Verification & Deployment)

The following tasks cannot be completed fully autonomously inside the IDE and require manual operator action:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               MANUAL ACTION ITEMS INVENTORY                            │
├─────────┬──────────────────────┬────────────────────────────┬──────────────────────────┤
│ Task ID │ Category             │ Owner                      │ Required Action          │
├─────────┼──────────────────────┼────────────────────────────┼──────────────────────────┤
│ 2.M1    │ Model Training       │ Aakansha & Mannat          │ Run Colab QLoRA GPU Job  │
│ 2.M2    │ Weights Deployment   │ Aakansha & Mannat          │ Copy weights to backend  │
│ 2.M3    │ Cloud API Keys       │ User / All                 │ Set GEMINI / GROQ keys   │
│ 2.M4    │ Visual QA Inspection │ Aryan                      │ Browser UX Inspection    │
│ 4.M1    │ Golden Demo Live Run │ All Team Members           │ Rehearse live demo talk  │
└─────────┴──────────────────────┴────────────────────────────┴──────────────────────────┤
```

### Detailed Manual Instructions:

1. **Task 2.M1: Execute QLoRA Training Job on Colab GPU (Aakansha & Mannat)**
   - **File:** [`training/finetune_rsvlm_colab.ipynb`](file:///c:/Users/nandi/Desktop/SATQuery/training/finetune_rsvlm_colab.ipynb)
   - **Action:** Open notebook in Google Colab with T4/A100 GPU runtime, upload `training/data/bigearthnet_vqa_grounding.json`, and run cells 1–7 to export trained adapter weights (`adapter_model.safetensors`, `adapter_config.json`).

2. **Task 2.M2: Deploy Trained LoRA Weights to Local Backend (Aakansha & Mannat)**
   - **Action:** Download the Colab output files and place them into:
     - `backend/weights/satquery_rsvlm_lora/adapter_model.safetensors`
     - `backend/weights/satquery_rsvlm_lora/adapter_config.json`
   - Start the serving microservice: `python backend/serve_fine_tuned.py` on port 8001.

3. **Task 2.M3: Remote Vision Cloud API Keys Configuration (Optional) (User)**
   - **Action:** Add your API key to [`backend/.env`](file:///c:/Users/nandi/Desktop/SATQuery/backend/.env):
     ```env
     GEMINI_API_KEY=your_actual_key_here
     GROQ_API_KEY=your_actual_key_here
     ```
   - *Note:* The system automatically operates with high-precision offline heuristic and deep learning fallback engines (ONNX Siamese CD + synthetic grounding) when keys are absent.

4. **Task 2.M4: Dual-Canvas Geospatial Inspector Visual QA (Aryan)**
   - **Action:** Start backend server: `python backend/main.py`, open `http://localhost:8000/app` in Chrome/Edge, load sample presets, and verify:
     - Reticle coordinates (`COORD: X px, Y px`) and ground distance (`GROUND: ~X m, ~Y m`) track at 60fps.
     - Suggestion chips render under Executive Summary and re-trigger query on click.
     - Multi-layer color legend displays on the canvas overlay.
     - Operator feedback buttons ("Accept Verification", "Flag Inaccurate") log successfully.

5. **Task 4.M1: Live Golden Demo Rehearsal (All Team Members)**
   - **Action:** Execute the 5 canonical presentation scenes in sequence to prepare for the live SIH evaluation presentation.

