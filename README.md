# 🛰️ SatQuery AI — Self-Adapting Multimodal Satellite Intelligence

> **Ask questions about satellite images in plain English. Get annotated, evidence-grounded answers.**

SatQuery AI transforms satellite imagery analysis from a specialized GIS task into a conversational experience. Upload satellite images, type a natural-language query, and receive structured analytical responses with visual evidence overlays — all processed through a transparent, multi-stage pipeline.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Natural-Language VQA** | Ask questions like *"How many agricultural parcels are here?"* or *"Is this area suitable for construction?"* |
| **Multi-Modal Input** | Supports optical imagery, SAR radar, and bi-temporal scene pairs for change detection |
| **Real-Time Spectral Analysis** | Pixel-level HSV/spectral-index analysis without cloud dependencies |
| **Self-Adapting Feedback Loop** | Operator corrections improve future responses immediately via exemplar memory |
| **Observable Telemetry** | Every pipeline stage is individually timed and logged for full auditability |
| **Multi-Format Reports** | Export analysis as JSON, Markdown, PDF, or DOCX |
| **3D Visualization** | Interactive Earth globe with orbiting satellites on the landing page |
| **Grounded Follow-Up Suggestions** | Context-aware suggestion chips for deeper analysis |

---

## 🏗️ Architecture

SatQuery AI runs an **11-node orchestrated pipeline**:

```
Query + Image → Intent Classification → Compatibility Check → Specialist Execution
→ Evidence Fusion → Verify Decision → Final Answer + Render Overlay
→ Suggest Next Query → Report Generation → Audit Store
```

### Specialist Execution Tiers (Graceful Degradation)
1. **Tier 1**: Live Fine-Tuned RS-VLM (Qwen2-VL + LoRA on GPU, port 8001)
2. **Tier 2**: Operator Exemplar Memory (cached human corrections)
3. **Tier 3**: LocalRSVisionEngine (deterministic OpenCV spectral analysis — always available)

> The system **never fails completely**. It works offline, on CPU, without API keys.

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** + **Uvicorn** | Async API server (ports 8000 + 8001) |
| **OpenCV (cv2)** | Core spectral analysis engine — HSV decomposition, contour extraction, overlay rendering |
| **Pillow (PIL)** | Image I/O and GeoTIFF metadata extraction |
| **NumPy** | Pixel manipulation and spectral index computation |
| **PyTorch** | JEV-JEPA Vision Transformer and Siamese CNN |
| **Transformers** + **PEFT** | Qwen2-VL-7B + LoRA adapter serving |
| **ONNX Runtime** | Siamese Change Detection inference |
| **Google Gemini** | Cloud VLM baseline (optional) |
| **Groq** | Low-latency LLM fallback (optional) |
| **ReportLab** + **python-docx** | PDF and Word report generation |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** + **Vite** | Component-based SPA with hot-reload |
| **Three.js** + **@react-three/fiber** | 3D Earth globe and satellite visualization |
| **@react-three/drei** | 3D helper components (OrbitControls, Text, Stars) |
| **Lucide React** | SVG icon library |
| **Web Speech API** | Voice-to-text query input |

### Training
| Technology | Purpose |
|---|---|
| **BigEarthNet.txt** | 9.6M instruction annotations from Sentinel-1/2 |
| **QLoRA Fine-Tuning** | 4-bit NF4 quantized LoRA (r=32, α=64) on Google Colab |

For the full technology reference, see [`docs/technology_stack.md`](docs/technology_stack.md).

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and **npm**
- A modern browser (Chrome, Edge, Firefox)
- *(Optional)* NVIDIA GPU with CUDA for fine-tuned model inference

### Quick Start (Windows)

```bash
# 1. Clone the repository
git clone https://github.com/mannatnandi2007/SatQuery_SIH.git
cd SatQuery_SIH

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# 3. Install frontend dependencies & build
cd frontend
npm install
npm run build
cd ..

# 4. Configure environment (optional — works without API keys)
copy backend\.env.example backend\.env
# Edit backend\.env to add your API keys if desired

# 5. Launch the platform
run_satquery.bat
```

This opens `http://localhost:8000` with both services running.

### Manual Start (Step-by-Step)

```bash
# Terminal 1: Fine-Tuned RS-VLM Specialist (port 8001)
cd backend
python -m uvicorn serve_fine_tuned:app --host 127.0.0.1 --port 8001 --reload

# Terminal 2: Main Orchestrator + React SPA (port 8000)
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Open http://localhost:8000 in your browser
```

### Frontend Development Mode

```bash
cd frontend
npm install
npm run dev
# Opens Vite dev server at http://localhost:5173
```

### Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Service health check |
| `/query` | POST | Full analysis pipeline (image + query) |
| `/compatibility-check` | POST | Pre-flight validation |
| `/feedback` | POST | Operator feedback (accept/flag/correct) |
| `/suggestion/click` | POST | Suggestion chip telemetry |
| `/audit` | GET | Audit trail retrieval |
| `/active-learning/queue` | GET | Uncertainty triage queue |
| `/active-learning/export-dataset` | GET | Export Colab-ready training dataset |
| `/memory/stats` | GET | Exemplar memory statistics |
| `/self-adapt/status` | GET | Self-adaptation calibration profile |
| `/compare-baseline` | POST | Optional Gemini baseline comparison |
| `/report/{id}` | GET | Download report (JSON/MD/PDF/DOCX) |

Full interactive API documentation available at `http://localhost:8000/docs`.

---

## 📁 Project Structure

```
SATQuery/
├── run_satquery.bat            # One-click platform launcher
├── start.ps1                   # PowerShell alternative launcher
├── stop_satquery.bat           # Graceful shutdown
├── README.md                   # This file
│
├── backend/                    # FastAPI Backend (20 Python files)
│   ├── main.py                # API server (15 endpoints)
│   ├── orchestrator.py        # 11-node pipeline engine
│   ├── specialists.py         # LocalRSVisionEngine + VLM specialists
│   ├── router.py              # NLP intent classifier
│   ├── gsd_normalizer.py      # Ground Sampling Distance engine
│   ├── jepa_engine.py         # JEV-JEPA ViT latent encoder
│   ├── dl_models.py           # Siamese CNN + ONNX runtime
│   ├── serve_fine_tuned.py    # Qwen2-VL LoRA serving (port 8001)
│   ├── render_overlay.py      # Multi-box evidence overlay renderer
│   ├── next_query.py          # Follow-up suggestion engine
│   ├── report.py              # Multi-format report generator
│   ├── audit_store.py         # Audit trail ledger
│   ├── memory_store.py        # Exemplar memory store
│   ├── tests/                 # 23 unit & integration tests
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + Three.js Frontend
│   ├── src/
│   │   ├── App.jsx            # SPA controller
│   │   ├── index.css          # Design system
│   │   └── components/        # 14 React components
│   ├── samples/               # Sample satellite images
│   └── package.json           # Node dependencies
│
├── training/                   # VLM Fine-Tuning Pipeline
│   ├── prepare_bigearthnet.py # Dataset curation
│   ├── finetune_rsvlm_colab.ipynb
│   └── data/                  # Instruction datasets
│
└── docs/                       # Documentation
    ├── ARCHITECTURE.md         # System architecture
    ├── PRD.md                  # Product requirements
    ├── WALKTHROUGH.md          # Developer guide
    ├── working_report.md       # Prototype functioning report
    ├── technology_stack.md     # Complete tech stack reference
    └── final_report.md         # Final project report
```

---

## 🔬 Special Features

### Self-Adapting Intelligence
The system improves with every interaction through a closed-loop feedback mechanism:
1. Operator flags or corrects a result via the UI
2. Correction is stored in exemplar memory
3. Future similar queries automatically use the corrected result
4. Corrected data is exportable for model retraining on Colab

### JEV-JEPA Architecture
A non-generative self-supervised representation learning engine inspired by V-JEPA:
- Predicts in **latent embedding space** (D=768), not pixel space
- Multi-block spatial masking for context/target learning
- Cosine distance for bi-temporal change detection
- More robust to atmospheric and illumination variations

### Observable Pipeline
Every pipeline stage is individually timed:
- Compatibility Check → Routing → Specialist Execution → Evidence Fusion → Overlay Rendering → Confidence Scoring → Suggestion Generation → Report Generation
- All timings visible in the UI's collapsible telemetry drawer
- Complete traces persisted to `audit.json`

---

## 🧪 Sample Queries

Upload a satellite image and try:
- *"What types of land cover are in this scene?"*
- *"How many agricultural parcels can you identify?"*
- *"Is this area suitable for construction?"*
- *"What is the flood risk assessment for this region?"*
- *"Identify all water bodies and estimate their area"*

For change detection, upload two temporal images (T1 and T2):
- *"What changed between these two images?"*
- *"Has urbanization expanded?"*

---

## 📄 Environment Variables

Create `backend/.env` from the example:

```env
# API Keys (optional — system works without them)
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here

# Fine-Tuned Model (requires GPU)
USE_FINE_TUNED_MODEL=false
FINE_TUNED_ENDPOINT_URL=http://localhost:8001/v1/chat/completions
FINE_TUNED_WEIGHTS_PATH=./weights/satquery_rsvlm_lora
```

---

## 📊 Testing

```bash
# Run all backend tests
cd backend
python -m pytest tests/ -v

# Expected output: 23 passed
```

---

## 👥 Team

Developed for the **Smart India Hackathon (SIH)** by:
Khushal, Aryan, Madhura, Dipesh, Aakansha, Mannat

---

## 📝 License

This project is a prototype developed for the Smart India Hackathon.
