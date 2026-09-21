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
- [ ] **Task 1.1: GSD Metadata Extractor (`backend/gsd_normalizer.py`)**
  - **Inputs:** GeoTIFF raster bytes, PNG/JPG with optional EXIF/XML header tags.
  - **Outputs:** Structured metadata dictionary: `{detected_gsd_m: float, sensor: str, crs: str, dimensions: (int, int)}`.
  - **Criteria:** Correctly reads pixel resolution for Sentinel-2 (10m/20m/60m), Landsat 8 (15m/30m), and falls back gracefully to manual input for plain JPG/PNG.
- [ ] **Task 1.2: Spatial Resolution Resampling Engine**
  - **Inputs:** Image tensor or PIL image, source GSD, target canonical GSD (default: $10.0\text{m/px}$).
  - **Outputs:** Resampled raster preserving spatial aspect ratio and high-frequency edge gradients (bicubic or Lanczos anti-aliased).
  - **Criteria:** Eliminates scale-induced artifacts without introducing ringing along water/land or runway boundaries.

#### Track B: Fine-Tuning & Self-Adapting Setup (Aakansha & Mannat)
- [ ] **Task 1.3: Remote Sensing VQA Dataset Curation (`training/data/`)**
  - **Inputs:** BigEarthNet, RSIVQA, or curated GeoTIFF scenes.
  - **Outputs:** Formatted instruction-tuning dataset `bigearthnet_vqa_grounding.json` with $(N=500)$ curated pairs containing spatial bounding tags `[ymin, xmin, ymax, xmax]`.
  - **Criteria:** Validated schema, balanced distribution across water bodies, urban ports, airports, agricultural parcels, and industrial facilities.
- [ ] **Task 1.4: Evaluation Baseline & ECE Harness**
  - **Inputs:** Base vision-language model (Qwen2-VL-7B or LLaVA-1.5-7B).
  - **Outputs:** Evaluation script computing Grounding IoU, VQA Accuracy, and Expected Calibration Error (ECE).
  - **Criteria:** Generates reproducible zero-shot baseline metrics before LoRA fine-tuning.

#### Track C: JEV-JEPA Representation Engine (Khushal & Aryan)
- [ ] **Task 1.5: JEV-JEPA Architecture Definition (`backend/jepa_engine.py`)**
  - **Inputs:** Pre-processed multispectral/optical scene patches ($16 \times 16$ or $14 \times 14$).
  - **Outputs:** Vision Transformer (ViT) latent encoder producing patch representations $z \in \mathbb{R}^{B \times N \times D}$ ($D=768$).
  - **Criteria:** Non-generative architecture without pixel decoders; verifies forward pass execution under $< 100\text{ms}$ on GPU.
- [ ] **Task 1.6: Spatial Masking Strategy**
  - **Inputs:** Input scene patch grid.
  - **Outputs:** Multi-block context and target masks (4 context blocks, 2 target blocks).
  - **Criteria:** Context patches pass to encoder; target patches predicted purely in latent feature space.

#### Track D: UI / UX Hallmark Architecture (Aryan)
- [ ] **Task 1.7: Hallmark Design System Setup (`frontend/style.css`)**
  - **Inputs:** `UIrules.md` requirements and color token specifications.
  - **Outputs:** Pure CSS design token system implementing high-contrast industrial dark mode (`--color-paper`, `--color-rule`, `--color-accent`, `--font-display`, `--font-mono`).
  - **Criteria:** Completely purge all 20 banned patterns (no purple/blue gradients, no Inter-everywhere, no Space Grotesk/Instrument Serif, no glassmorphism).
- [ ] **Task 1.8: Telemetry Workbench Shell (`frontend/index.html`)**
  - **Inputs:** Wireframe for dual-canvas workspace (Scene view + Evidence overlay view).
  - **Outputs:** Responsive semantic HTML layout with header status bar, stage telemetry drawer, and inspector sidebar.
  - **Criteria:** Passes initial Hallmark anti-slop visual check; zero emojis in headings, zero decorative badge clutter.

---

### Phase 2: Core Engineering & Specialist Model Tracks
*Objective: Train the specialist model, implement JEPA latent change detection, integrate GSD scale-aware pre-flight checks, and build interactive workbench controls.*

#### Track A: GSD Normalisation (Madhura & Dipesh)
- [ ] **Task 2.1: Pre-flight Compatibility GSD Arbitration (`backend/compatibility.py`)**
  - **Inputs:** Dual-image uploads for change detection or multi-sensor comparison.
  - **Outputs:** Cross-image GSD ratio and compatibility status (e.g., flag warning if GSD difference $> 4\times$).
  - **Criteria:** Prevents invalid change detection across incompatible scales (e.g. 60m Sentinel vs 0.3m Drone) without automated decimation.
- [ ] **Task 2.2: Metric Scale Bar & Real-World Dimensions (`backend/evidence.py`)**
  - **Inputs:** Bounding box pixel dimensions $[w, h]$, normalized image GSD.
  - **Outputs:** Physical metric calculation ($L = w \times \text{GSD}$, $\text{Area} = w \times h \times \text{GSD}^2$) and visual scale bar rendering.
  - **Criteria:** Overlays metric scale bar (e.g., "$100\text{ m}$") accurately calibrated to the image's coordinate reference.

#### Track B: Fine-Tuning & Self-Adapting Loop (Aakansha & Mannat)
- [ ] **Task 2.3: RS-VLM QLoRA Fine-Tuning Execution**
  - **Inputs:** Base model checkpoint + curated instruction dataset (`training/data/`).
  - **Outputs:** Optimized LoRA adapter weights (`backend/weights/satquery_rsvlm_lora/adapter_model.safetensors`).
  - **Criteria:** 4-bit NF4 quantization, rank $r=32$, $\alpha=64$, training loss converges with grounding IoU $> 0.65$ on validation set.
- [ ] **Task 2.4: Local Inference Server Integration (`backend/serve_fine_tuned.py`)**
  - **Inputs:** LoRA adapter and base model loaded via `peft` and `transformers`.
  - **Outputs:** FastAPI endpoint serving structured VQA predictions with bounding box tags.
  - **Criteria:** Inference latency $< 1200\text{ms}$ on single GPU; fallback to API tiers when offline.

#### Track C: JEV-JEPA Representation Engine (Khushal & Aryan)
- [ ] **Task 2.5: JEV-JEPA Masked Predictor Pipeline**
  - **Inputs:** Context latent vectors and target spatial positional encodings.
  - **Outputs:** Predicted target latent vectors $\hat{z}_{\text{target}}$.
  - **Criteria:** Trained on smooth prediction loss (Smooth L1 / cosine loss in latent space); latent representation space shows semantic clustering of terrain types.
- [ ] **Task 2.6: Latent-Space Change Detection Specialist (`backend/dl_models.py`)**
  - **Inputs:** Aligned bi-temporal scene embeddings $z_{T1}$ and $z_{T2}$.
  - **Outputs:** Spatial feature distance heatmap matrix $D(i, j) = 1 - \cos(z_{T1}^{(i,j)}, z_{T2}^{(i,j)})$ and clustered change polygons.
  - **Criteria:** Successfully isolates significant ground changes (vegetation clearing, new building footprint) while ignoring illumination/shadow noise.

#### Track D: UI / UX Hallmark Architecture (Aryan)
- [ ] **Task 2.7: 8-State Interactive Components (`frontend/app.js`, `frontend/style.css`)**
  - **Inputs:** Design tokens and component specifications.
  - **Outputs:** Interactive buttons, input fields, toggles, and sliders with complete styling for: `default`, `hover`, `focus-visible`, `active`, `disabled`, `loading`, `error`, and `success`.
  - **Criteria:** Zero button fade animations; crisp 1px offset `:active` state; high-contrast focus rings.
- [ ] **Task 2.8: Dual-Canvas Geospatial Inspector**
  - **Inputs:** Uploaded raw scene + rendered evidence overlay.
  - **Outputs:** Split-pane or synchronized pan/zoom canvas displaying pixel coordinates, detected object chips, and GSD indicator.
  - **Criteria:** Smooth 60fps rendering, no cursor-following glow beams, clean tactile controls.

---

### Phase 3: Integration, Spatial Calibration & Self-Adapting Feedback
*Objective: Wire all components into the central orchestrator, implement the closed-loop feedback pipeline, and generate rich multi-format telemetry reports.*

#### Track A: Cross-Pipeline Orchestration (Khushal, Aryan, Madhura, Dipesh, Aakansha, Mannat)
- [ ] **Task 3.1: Orchestrator Pipeline Integration (`backend/orchestrator.py`)**
  - **Inputs:** Raw multipart request from `/query`.
  - **Outputs:** Unified execution pipeline executing:
    $$\text{Compatibility} \to \text{GSD Normalizer} \to \text{JEV-JEPA Latents} \to \text{RS-VLM Reasoning} \to \text{Evidence Grounding} \to \text{Telemetry Trace}$$
  - **Criteria:** Total synchronous pipeline latency $< 2000\text{ms}$ on GPU; structured error fallback on any sub-component failure.
- [ ] **Task 3.2: Multi-Sensor Alignment Specialist (`backend/specialists.py`)**
  - **Inputs:** Heterogeneous inputs (e.g. Optical RGB + Sentinel-1 SAR).
  - **Outputs:** Coregistered dual-band visualization and cross-modal reasoning.
  - **Criteria:** Returns pseudo-color SAR fusion overlay highlighting high-dielectric/metallic structures (ships, bridges).

#### Track B: Self-Adapting Feedback Loop (Aakansha & Mannat)
- [ ] **Task 3.3: Operator Feedback Endpoint (`backend/main.py`)**
  - **Inputs:** `POST /feedback` with query ID, rating (`accept` / `reject` / `corrected`), corrected bounding box, operator notes.
  - **Outputs:** In-memory feedback store and persistent JSONL log.
  - **Criteria:** Real-time feedback ingestion with zero impact on query endpoint throughput.
- [ ] **Task 3.4: Active Learning & Uncertainty Triage**
  - **Inputs:** Model token probabilities, grounding confidence, and operator feedback logs.
  - **Outputs:** Prioritized queue of hard-negative or high-entropy queries for automated retraining triage.
  - **Criteria:** Successfully filters and ranks the top 10% most ambiguous queries for model refinement.

#### Track C: Evidence & Scale Calibration (Madhura, Dipesh & Aryan)
- [ ] **Task 3.5: GSD-Calibrated Evidence Overlays (`backend/evidence.py`)**
  - **Inputs:** Specialist bounding box predictions + normalized GSD metadata.
  - **Outputs:** Rendered overlay image with highlighted target regions, category label pills, and verified metric dimensions.
  - **Criteria:** Crisp high-resolution PNG overlay without blurred borders or low-contrast text.

#### Track D: UI Telemetry & Feedback Interface (Aryan)
- [ ] **Task 3.6: Step-by-Step Observable Telemetry Drawer (`frontend/app.js`)**
  - **Inputs:** Structured `trace` array returned by backend.
  - **Outputs:** Collapsible real-time timeline displaying stage duration (ms), status chip (`OK` / `WARN` / `FAIL`), and diagnostic parameters.
  - **Criteria:** Stage-by-stage progression rendered without generic spinners or fade-in scroll animations.
- [ ] **Task 3.7: In-UI Operator Feedback Modal / Drawer**
  - **Inputs:** Displayed query result.
  - **Outputs:** Inline feedback controls: "Accept Evidence", "Flag Inaccurate", and interactive bounding box adjustment tool.
  - **Criteria:** Submits to `POST /feedback` and displays instant confirmation chip.

---

### Phase 4: Telemetry Polish, System Evaluation & Demo Readiness
*Objective: Conduct anti-slop design audit, execute golden demo rehearsals, generate evaluation reports, and finalize repository documentation.*

#### All Tracks
- [ ] **Task 4.1: Hallmark Anti-AI-Slop Comprehensive Audit (Aryan)**
  - **Check:** Verify all 20 banned UI patterns are completely absent across all CSS, HTML, and JS files.
  - **Check:** Responsive testing across 320px, 375px, 768px, and 1440px viewports (zero horizontal scroll, `overflow-x: clip`).
  - **Deliverable:** UI audit checklist signed off.
- [ ] **Task 4.2: Golden Demo Scene Rehearsal (All Team Members)**
  - **Check:** Test and rehearse 5 canonical satellite scenes:
    1. *Airport Runway Inspection* (High-res optical, object counting & length estimation).
    2. *Urban Harbor & Cargo Vessel Grounding* (Sentinel-2 10m, vessel localization).
    3. *Agricultural Parcel Vegetation Health* (Multi-spectral NDVI analysis).
    4. *Bi-Temporal Port Infrastructure Change* (T1 vs T2 change detection via JEPA latents).
    5. *Maritime Vessel Detection via SAR Fusion* (Sentinel-1 SAR + Optical coregistration).
  - **Deliverable:** 100% reliable responses with calibrated confidence and verified overlays.
- [ ] **Task 4.3: Multi-Format Report Generator Verification (Madhura & Dipesh)**
  - **Check:** Verify `/report/{id}` outputs accurate JSON, Markdown, and formatted PDF reports containing GSD metadata and complete telemetry traces.
- [ ] **Task 4.4: Self-Adapting Loop Validation (Aakansha & Mannat)**
  - **Check:** Submit 5 feedback corrections, verify active learning queue captures candidates, and verify dynamic prompt update in RS-VLM.
- [ ] **Task 4.5: Final Documentation & Presentation Walkthrough (Khushal & Aryan)**
  - **Check:** Update `WALKTHROUGH.md` and repository README with launch instructions, API guide, and evaluation results.
