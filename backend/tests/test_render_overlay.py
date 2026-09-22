"""
SatQuery AI — Unit Tests for Visual Multi-Box Grounding & Overlay Renderer (Node N11)
Tests standardized AnnotationSet schema, IoU deduplication, multi-layer rendering,
and scale bar integration in isolation.
"""

import unittest
import sys
import os
from io import BytesIO
from PIL import Image

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from annotation_schema import AnnotationSet, AnnotationLayer, GroundingBox
from evidence_fusion import compute_iou, evidence_fusion
from render_overlay import multi_box_renderer


class TestRenderOverlayAndFusion(unittest.TestCase):
    """Unit tests for Node N11 and Evidence Fusion in isolation."""

    def setUp(self):
        # Create a synthetic 512x512 RGB satellite scene
        img = Image.new("RGB", (512, 512), color=(25, 45, 65))
        buf = BytesIO()
        img.save(buf, format="PNG")
        self.synthetic_image_bytes = buf.getvalue()

    def test_iou_calculation_exact(self):
        """Test IoU computation on known overlapping coordinates."""
        # Identical boxes -> IoU = 1.0
        box1 = [10.0, 10.0, 30.0, 30.0]
        box2 = [10.0, 10.0, 30.0, 30.0]
        self.assertAlmostEqual(compute_iou(box1, box2), 1.0, places=3)

        # Disjoint boxes -> IoU = 0.0
        box3 = [50.0, 50.0, 70.0, 70.0]
        self.assertEqual(compute_iou(box1, box3), 0.0)

        # Partial overlap (50% overlap on 20x20 box)
        box4 = [20.0, 10.0, 40.0, 30.0]
        iou = compute_iou(box1, box4)
        self.assertTrue(0.2 < iou < 0.5)

    def test_evidence_fusion_iou_deduplication(self):
        """Verify overlapping boxes within a layer are deduplicated keeping higher confidence."""
        layer = AnnotationLayer(
            layer_id="buildings_count",
            reasoning="count",
            color="#2E7DD1",
            boxes=[
                GroundingBox(id=1, bbox=[10.0, 10.0, 30.0, 30.0], label="Building A", confidence=0.75),
                GroundingBox(id=2, bbox=[11.0, 11.0, 31.0, 31.0], label="Building A (Dup)", confidence=0.94),
                GroundingBox(id=3, bbox=[60.0, 60.0, 80.0, 80.0], label="Building B", confidence=0.88),
            ]
        )

        fused_set = evidence_fusion.fuse([layer])
        self.assertEqual(len(fused_set.layers), 1)
        fused_layer = fused_set.layers[0]

        # 3 candidate boxes with 2 overlapping -> exactly 2 deduplicated boxes
        self.assertEqual(len(fused_layer.boxes), 2)
        # Verify higher confidence box (0.94) was retained
        confidences = [b.confidence for b in fused_layer.boxes]
        self.assertIn(0.94, confidences)
        self.assertIn(0.88, confidences)
        self.assertNotIn(0.75, confidences)

        # Verify sequential 1-based indexing
        ids = [b.id for b in fused_layer.boxes]
        self.assertEqual(ids, [1, 2])

    def test_empty_annotation_set_rendering(self):
        """Verify renderer gracefully handles empty annotation set without error."""
        empty_set = AnnotationSet(layers=[])
        filename, b64, metric_info = multi_box_renderer.render(
            self.synthetic_image_bytes,
            empty_set,
            gsd_m=10.0
        )
        self.assertTrue(filename.endswith(".png"))
        self.assertIsNotNone(b64)
        self.assertEqual(metric_info.get("box_count"), 0)

    def test_multi_layer_rendering_with_legend(self):
        """Verify multi-layer rendering with distinct colors, labels, and legend strip."""
        layer1 = AnnotationLayer(
            layer_id="buildings_count",
            reasoning="count",
            color="#2E7DD1",
            boxes=[
                GroundingBox(id=1, bbox=[10.0, 10.0, 30.0, 30.0], label="Building 1", confidence=0.92),
                GroundingBox(id=2, bbox=[35.0, 10.0, 55.0, 30.0], label="Building 2", confidence=0.89)
            ]
        )

        layer2 = AnnotationLayer(
            layer_id="likely_new_construction",
            reasoning="change",
            color="#D14545",
            boxes=[
                GroundingBox(id=1, bbox=[60.0, 60.0, 85.0, 85.0], label="New Construction", confidence=0.81)
            ]
        )

        annotation_set = AnnotationSet(layers=[layer1, layer2])
        self.assertEqual(annotation_set.total_boxes_count(), 3)

        filename, b64, metric_info = multi_box_renderer.render(
            self.synthetic_image_bytes,
            annotation_set,
            gsd_m=10.0,
            draw_legend=True
        )

        self.assertTrue(filename.startswith("overlay_"))
        self.assertTrue(filename.endswith(".png"))
        self.assertGreater(len(b64), 100)
        self.assertEqual(metric_info["total_layers"], 2)
        self.assertEqual(metric_info["total_boxes"], 3)

    def test_annotation_set_serialization(self):
        """Verify AnnotationSet to_dict and from_dict contracts."""
        box = GroundingBox(id=1, bbox=[5.0, 5.0, 25.0, 25.0], label="Target", confidence=0.95)
        layer = AnnotationLayer(layer_id="radar_targets", reasoning="sar_anomaly", color="#10B981", boxes=[box])
        anno_set = AnnotationSet(layers=[layer])

        data = anno_set.to_dict()
        self.assertIn("annotation_set", data)
        self.assertEqual(len(data["annotation_set"]), 1)

        restored = AnnotationSet.from_dict(data)
        self.assertEqual(len(restored.layers), 1)
        self.assertEqual(restored.layers[0].layer_id, "radar_targets")
        self.assertEqual(restored.layers[0].boxes[0].confidence, 0.95)


if __name__ == "__main__":
    unittest.main()
