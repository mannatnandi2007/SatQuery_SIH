# 🛰️ SatQuery AI — VLM Fine-Tuning & BigEarthNet.txt

This folder contains the dataset preparation tools and the fine-tuning recipe for training the **Remote Sensing Vision-Language Model (RS-VLM)** on the **BigEarthNet.txt** benchmark.

---

## 1. Dataset: BigEarthNet.txt

- **Paper**: *"BigEarthNet.txt: A Large-Scale Multi-Sensor Image-Text Dataset and Benchmark for Earth Observation"* ([arXiv:2603.29630](https://arxiv.org/abs/2603.29630))
- **Hugging Face Repository**: `BIFOLD-BigEarthNetv2-0/BigEarthNet.txt`
- **Modality**: Co-registered Sentinel-1 (SAR) and Sentinel-2 (Multispectral Optical) imagery.
- **Annotations**: 9.6M instruction annotations including:
  - **VQA Pairs**: Task-specific question-answering triples.
  - **Referring Expression Detection**: Bounding boxes `<box>[y1, x1, y2, x2]</box>` for spatial visual grounding.

To generate a curated local instruction dataset:
```bash
cd training
python prepare_bigearthnet.py --num_samples 300 --output_dir data
```
This produces `data/bigearthnet_vqa_grounding.json`.

---

## 2. Fine-Tuning in Google Colab (Free T4 GPU)

Because local machines without dedicated NVIDIA CUDA GPUs cannot train 7B models in memory, use the pre-built notebook:

1. Open [Google Colab](https://colab.research.google.com).
2. Click **Upload** and upload `training/finetune_rsvlm_colab.ipynb`.
3. Set the runtime: **Runtime** → **Change runtime type** → **T4 GPU**.
4. Click **Run All** (takes ~25 minutes for 300 curated BigEarthNet instruction samples).
5. At the final cell, Colab will automatically package and prompt you to download `satquery_rsvlm_lora.zip`.

---

## 3. Connecting the Fine-Tuned Model to SatQuery AI

Once your fine-tuned weights are ready, you can point the SatQuery Orchestrator to them in `backend/.env`:

```env
# Enable the fine-tuned specialist
USE_FINE_TUNED_MODEL=true

# Option A: Local / vLLM / Ollama serving endpoint
FINE_TUNED_ENDPOINT_URL=http://localhost:8001/v1/chat/completions

# Option B: Local weights directory
FINE_TUNED_WEIGHTS_PATH=./weights/satquery_rsvlm_lora
```

The **Orchestrator** automatically checks this first:
- If configured and responding, it routes to your fine-tuned RS-VLM.
- If unavailable, it smoothly falls back to **Gemini 2.5 Flash Vision**, then **Groq**, and finally offline deterministic mock.
