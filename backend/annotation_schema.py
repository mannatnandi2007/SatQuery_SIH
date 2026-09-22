"""
SatQuery AI — Standardized Multi-Layer Annotation Schema
Defines the unified data contract for visual grounding across specialists (T1–T6).
Each layer corresponds to a distinct kind of reasoning (e.g., count, change, grounding, radar anomaly),
carrying its own color and sequential box numbering.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class GroundingBox:
    """
    Standardized bounding box detection.
    bbox format: [x1, y1, x2, y2] as percentages (0.0 to 100.0) of image dimensions.
    """
    id: int
    bbox: List[float]  # [x1, y1, x2, y2]
    label: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bbox": [round(c, 2) for c in self.bbox],
            "label": self.label,
            "confidence": round(self.confidence, 3)
        }


@dataclass
class AnnotationLayer:
    """
    Distinct visual reasoning layer (e.g. 'buildings_count', 'likely_new_construction').
    """
    layer_id: str
    reasoning: str  # "count" | "change" | "grounding" | "sar_anomaly" | "infrastructure"
    color: str      # High-contrast HEX code e.g. "#2E7DD1", "#D14545"
    boxes: List[GroundingBox] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "reasoning": self.reasoning,
            "color": self.color,
            "boxes": [box.to_dict() for box in self.boxes]
        }


@dataclass
class AnnotationSet:
    """
    Collection of annotation layers for a given scene evaluation.
    """
    layers: List[AnnotationLayer] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Returns True if there are no layers or all layers have zero boxes."""
        return len(self.layers) == 0 or all(len(layer.boxes) == 0 for layer in self.layers)

    def total_boxes_count(self) -> int:
        return sum(len(layer.boxes) for layer in self.layers)

    def get_layer(self, layer_id: str) -> Optional[AnnotationLayer]:
        for layer in self.layers:
            if layer.layer_id == layer_id:
                return layer
        return None

    def add_layer(self, layer: AnnotationLayer):
        self.layers.append(layer)

    def to_list(self) -> List[Dict[str, Any]]:
        return [layer.to_dict() for layer in self.layers]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "annotation_set": self.to_list()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnnotationSet":
        layers_data = data.get("annotation_set", []) if isinstance(data, dict) else data
        layers = []
        for l_data in layers_data:
            boxes = [
                GroundingBox(
                    id=b.get("id", i + 1),
                    bbox=b.get("bbox", [0, 0, 0, 0]),
                    label=b.get("label", ""),
                    confidence=float(b.get("confidence", 1.0))
                )
                for i, b in enumerate(l_data.get("boxes", []))
            ]
            layers.append(AnnotationLayer(
                layer_id=l_data.get("layer_id", "default"),
                reasoning=l_data.get("reasoning", "general"),
                color=l_data.get("color", "#2E7DD1"),
                boxes=boxes
            ))
        return cls(layers=layers)
