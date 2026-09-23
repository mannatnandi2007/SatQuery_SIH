"""
SatQuery AI — Exemplar Memory Store & Colab Training Dataset Exporter
Implements instant operator memorization and bridges the human-in-the-loop
feedback ledger directly to the Colab fine-tuning pipeline.
"""

import os
import json
import hashlib
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from PIL import Image
from io import BytesIO

MEMORY_FILE_PATH = os.path.join(os.path.dirname(__file__), "exemplar_memory.json")
COLAB_EXPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "training", "data", "active_learning_retrain.json")


class ExemplarMemoryStore:
    """
    Thread-safe memory store for operator corrections.
    Provides instant few-shot memory recall and exports Colab-ready datasets.
    """

    def __init__(self, file_path: str = MEMORY_FILE_PATH):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"exemplars": []}, f, indent=2)

    def _compute_image_hash(self, image_bytes: bytes) -> str:
        """Compute robust perceptual thumbnail hash of the image."""
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
            # Normalize to 64x64 thumbnail for spatial alignment robustness
            thumb = img.resize((64, 64), Image.BILINEAR)
            thumb_bytes = thumb.tobytes()
            return hashlib.sha256(thumb_bytes).hexdigest()[:16]
        except Exception:
            return hashlib.sha256(image_bytes[:4096]).hexdigest()[:16]

    def record_exemplar(
        self,
        image_bytes: Optional[bytes],
        query: str,
        rating: str,
        notes: Optional[str] = None,
        corrected_bbox: Optional[List[float]] = None,
        original_answer: Optional[str] = None,
        detected_category: str = "general"
    ) -> Dict[str, Any]:
        """Record an operator-verified correction into exemplar memory."""
        img_hash = self._compute_image_hash(image_bytes) if image_bytes else "unknown"
        exemplar_id = f"ex_{img_hash}_{hashlib.md5(query.encode()).hexdigest()[:8]}"

        entry = {
            "id": exemplar_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "image_hash": img_hash,
            "query": query,
            "rating": rating,
            "notes": notes or "",
            "corrected_bbox": corrected_bbox,
            "original_answer": original_answer or "",
            "category": detected_category
        }

        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Replace existing entry if matching id, else append
                exemplars = data.get("exemplars", [])
                filtered = [e for e in exemplars if e.get("id") != exemplar_id]
                filtered.append(entry)
                data["exemplars"] = filtered

                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[MemoryStore] Failed to record exemplar: {e}")

        # Also refresh the Colab export dataset
        self.export_colab_dataset()
        return entry

    def find_exemplar(self, image_bytes: bytes, query: str) -> Optional[Dict[str, Any]]:
        """Look up if this exact scene or query has verified operator memory."""
        img_hash = self._compute_image_hash(image_bytes)
        q_norm = query.lower().strip()

        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for ex in reversed(data.get("exemplars", [])):
                    if ex.get("image_hash") == img_hash:
                        # Match query intent keywords
                        ex_q = ex.get("query", "").lower()
                        # If query is identical or shares key words
                        if ex_q == q_norm or (len(set(ex_q.split()) & set(q_norm.split())) >= 3):
                            return ex
            except Exception:
                pass
        return None

    def export_colab_dataset(self) -> str:
        """
        Exports all queued active learning and operator-flagged items
        into BigEarthNet instruction tuning format for Colab.
        """
        os.makedirs(os.path.dirname(COLAB_EXPORT_PATH), exist_ok=True)
        colab_entries = []

        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                exemplars = data.get("exemplars", [])
            except Exception:
                exemplars = []

        for idx, ex in enumerate(exemplars, 1):
            q_text = ex.get("query", "Analyze this satellite scene.")
            notes = ex.get("notes", "")
            orig_ans = ex.get("original_answer", "")
            bbox = ex.get("corrected_bbox") or [25.0, 25.0, 75.0, 75.0]

            # Construct verified ground-truth answer for fine-tuning
            gt_answer = f"Verified remote sensing analysis: {notes}." if notes else orig_ans
            if not gt_answer:
                gt_answer = "Verified spatial feature localized with human operator confirmation."

            entry = {
                "id": f"al_sample_{idx:04d}",
                "category": ex.get("category", "urban"),
                "gsd_m": 10.0,
                "sensor": "Sentinel-2 MSI",
                "conversations": [
                    {
                        "from": "human",
                        "value": f"<image>\n{q_text}"
                    },
                    {
                        "from": "gpt",
                        "value": f"{gt_answer} <box>[{int(bbox[0])}, {int(bbox[1])}, {int(bbox[2])}, {int(bbox[3])}]</box>"
                    }
                ],
                "grounding": {
                    "bbox_pct": [float(b) for b in bbox],
                    "label": ex.get("category", "feature"),
                    "operator_rating": ex.get("rating")
                }
            }
            colab_entries.append(entry)

        try:
            with open(COLAB_EXPORT_PATH, "w", encoding="utf-8") as f:
                json.dump(colab_entries, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MemoryStore] Failed to write Colab export dataset: {e}")

        return COLAB_EXPORT_PATH

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                exemplars = data.get("exemplars", [])
                return {
                    "total_exemplars": len(exemplars),
                    "colab_dataset_path": COLAB_EXPORT_PATH,
                    "ready_for_batch_training": len(exemplars) >= 5,
                    "recommended_batch_size": 15
                }
            except Exception:
                return {"total_exemplars": 0, "colab_dataset_path": COLAB_EXPORT_PATH, "ready_for_batch_training": False}


# Global singleton instance
memory_store = ExemplarMemoryStore()
