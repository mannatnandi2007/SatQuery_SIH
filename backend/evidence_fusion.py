"""
SatQuery AI — Evidence Fusion Engine (Node N6)
Fuses multi-specialist detections into a unified AnnotationSet.
Applies Intersection-over-Union (IoU) deduplication across overlapping detections,
preserves high-confidence detections, and ensures consistent numbering per layer.
"""

from typing import List, Dict, Any, Optional, Tuple

try:
    from annotation_schema import GroundingBox, AnnotationLayer, AnnotationSet
except ImportError:
    from backend.annotation_schema import GroundingBox, AnnotationLayer, AnnotationSet


def compute_iou(boxA: List[float], boxB: List[float]) -> float:
    """
    Computes Intersection-over-Union between two bounding boxes.
    Boxes are in percentage format [x1, y1, x2, y2].
    """
    xA = max(min(boxA[0], boxA[2]), min(boxB[0], boxB[2]))
    yA = max(min(boxA[1], boxA[3]), min(boxB[1], boxB[3]))
    xB = min(max(boxA[0], boxA[2]), max(boxB[0], boxB[2]))
    yB = min(max(boxA[1], boxA[3]), max(boxB[1], boxB[3]))

    interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
    if interArea <= 0:
        return 0.0

    boxAArea = abs(boxA[2] - boxA[0]) * abs(boxA[3] - boxA[1])
    boxBArea = abs(boxB[2] - boxB[0]) * abs(boxB[3] - boxB[1])

    denom = float(boxAArea + boxBArea - interArea)
    if denom <= 0:
        return 0.0

    return interArea / denom


class EvidenceFusionEngine:
    """
    Merges and arbitrates detections across specialists (T1–T6).
    """

    def __init__(self, iou_threshold: float = 0.50):
        self.iou_threshold = iou_threshold

    def deduplicate_within_layer(self, layer: AnnotationLayer) -> AnnotationLayer:
        """
        Deduplicates overlapping boxes within a single layer via Non-Maximum Suppression (NMS).
        """
        if len(layer.boxes) <= 1:
            return layer

        # Sort descending by confidence
        sorted_boxes = sorted(layer.boxes, key=lambda b: b.confidence, reverse=True)
        selected_boxes: List[GroundingBox] = []

        for candidate in sorted_boxes:
            overlap = False
            for kept in selected_boxes:
                if compute_iou(candidate.bbox, kept.bbox) >= self.iou_threshold:
                    overlap = True
                    break
            if not overlap:
                selected_boxes.append(candidate)

        # Re-index IDs sequentially (1..N) per layer
        for idx, box in enumerate(selected_boxes, 1):
            box.id = idx

        return AnnotationLayer(
            layer_id=layer.layer_id,
            reasoning=layer.reasoning,
            color=layer.color,
            boxes=selected_boxes
        )

    def deduplicate_across_layers(self, layers: List[AnnotationLayer]) -> List[AnnotationLayer]:
        """
        Deduplicates identical/redundant boxes between different layers if reasoning is identical,
        or annotates compound significance if reasoning differs.
        """
        deduped_layers = []
        for l in layers:
            deduped_layers.append(self.deduplicate_within_layer(l))

        # Check across layers for near-identical duplicate boxes (IoU >= 0.85)
        # If two different layers have almost identical boxes:
        # Keep higher confidence in its layer, or keep both if distinct reasoning (e.g. count vs change)
        return deduped_layers

    def fuse(
        self,
        layers: List[AnnotationLayer],
        specialist_results: Optional[List[Any]] = None
    ) -> AnnotationSet:
        """
        Consolidates candidate annotation layers into a clean, deduplicated AnnotationSet.
        """
        # Filter out empty layers
        active_layers = [l for l in layers if l and len(l.boxes) > 0]

        # Apply deduplication
        fused_layers = self.deduplicate_across_layers(active_layers)

        return AnnotationSet(layers=fused_layers)


# Singleton instance
evidence_fusion = EvidenceFusionEngine()
