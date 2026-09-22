"""
SatQuery AI — End-to-End Pipeline Integration Test
Verifies end-to-end flow from pre-flight validation through specialist execution,
evidence fusion, multi-box rendering (N11), next-query recommendation (N10),
report generation, and audit trail persistence.
"""

import unittest
import asyncio
import sys
import os
from io import BytesIO
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch
from orchestrator import orchestrator
from audit_store import audit_store
from specialists import SpecialistResult
from annotation_schema import AnnotationSet, AnnotationLayer, GroundingBox


class TestPipelineE2E(unittest.IsolatedAsyncioTestCase):
    """E2E asynchronous integration tests for full pipeline execution."""

    def setUp(self):
        # Generate synthetic satellite test scenes
        img1 = Image.new("RGB", (400, 300), color=(30, 60, 45))
        buf1 = BytesIO()
        img1.save(buf1, format="PNG")
        self.img1_bytes = buf1.getvalue()

        img2 = Image.new("RGB", (400, 300), color=(40, 70, 55))
        buf2 = BytesIO()
        img2.save(buf2, format="PNG")
        self.img2_bytes = buf2.getvalue()

    @patch.object(orchestrator, "_execute_single_image_vqa")
    async def test_single_vqa_e2e(self, mock_vqa):
        """Test Single VQA pipeline returns answer, multi-box annotation_set, and suggestions."""
        mock_vqa.return_value = SpecialistResult(
            answer="Detected 8 buildings across the port facility.",
            bounding_box=[20, 20, 80, 80],
            confidence=0.92,
            evidence_type="bbox",
            detail="Mock RS-VLM for pipeline test",
            detected_objects=["building", "warehouse"],
            annotation_set=AnnotationSet(layers=[
                AnnotationLayer(
                    layer_id="buildings_count",
                    reasoning="count",
                    color="#2E7DD1",
                    boxes=[
                        GroundingBox(id=1, bbox=[22, 22, 45, 45], label="Building 1", confidence=0.92),
                        GroundingBox(id=2, bbox=[50, 22, 75, 45], label="Building 2", confidence=0.90)
                    ]
                )
            ])
        )
        status_code, response = await orchestrator.process_query(
            filenames=["scene.png"],
            file_contents=[self.img1_bytes],
            query="Count how many buildings are in this port complex."
        )

        self.assertEqual(status_code, 200)
        data = response.to_dict()
        self.assertFalse(data["error"])
        self.assertIsNotNone(data["answer"])
        self.assertIn("confidence", data)
        self.assertIn("trace", data)

        # Feature 1: Next-Query Recommendations (N10)
        self.assertIn("suggestions", data)
        suggestions = data["suggestions"]
        self.assertGreaterEqual(len(suggestions), 2)
        for s in suggestions:
            self.assertIn("text", s)
            self.assertIn("task_type", s)

        # Feature 2: Multi-Box Visual Grounding (N11)
        self.assertIn("annotation_set", data)
        annotation_set = data["annotation_set"]
        self.assertIsInstance(annotation_set, list)
        self.assertGreaterEqual(len(annotation_set), 1)

        # Verify overlay image generated
        self.assertIsNotNone(data["evidence"]["overlay_image_url"])
        self.assertIsNotNone(data["evidence"]["overlay_image_base64"])

    async def test_change_detection_e2e(self):
        """Test Bi-Temporal Change Detection returns change overlay and follow-up suggestions."""
        status_code, response = await orchestrator.process_query(
            filenames=["port_t1.png", "port_t2.png"],
            file_contents=[self.img1_bytes, self.img2_bytes],
            query="Detect all bi-temporal change deltas between baseline and monitoring dates."
        )

        self.assertEqual(status_code, 200)
        data = response.to_dict()
        self.assertFalse(data["error"])
        self.assertIn("suggestions", data)
        self.assertIn("annotation_set", data)

    @patch.object(orchestrator, "_execute_single_image_vqa")
    async def test_building_counting_e2e(self, mock_vqa):
        """Test counting number of buildings returns synchronized multi-box layer and count."""
        mock_vqa.return_value = SpecialistResult(
            answer="Detected 6 industrial buildings in this complex.",
            bounding_box=[15, 15, 85, 85],
            confidence=0.93,
            evidence_type="bbox",
            detail="Building Counter Specialist",
            detected_objects=["industrial building", "warehouse"],
            annotation_set=AnnotationSet(layers=[
                AnnotationLayer(
                    layer_id="buildings_count",
                    reasoning="count",
                    color="#2E7DD1",
                    boxes=[
                        GroundingBox(id=i, bbox=[15 + i*10, 15, 22 + i*10, 35], label=f"Building {i}", confidence=0.93)
                        for i in range(1, 7)
                    ]
                )
            ])
        )
        status_code, response = await orchestrator.process_query(
            filenames=["industrial_complex.png"],
            file_contents=[self.img1_bytes],
            query="Count the total number of buildings in this industrial complex."
        )

        self.assertEqual(status_code, 200)
        data = response.to_dict()
        self.assertFalse(data["error"])
        self.assertIn("6", data["answer"])
        self.assertIn("annotation_set", data)
        self.assertEqual(len(data["annotation_set"]), 1)
        count_layer = data["annotation_set"][0]
        self.assertEqual(count_layer["reasoning"], "count")
        self.assertEqual(len(count_layer["boxes"]), 6)

    async def test_zero_change_detection_identical_images(self):
        """Test bi-temporal detection on identical scenes correctly reports zero changes with no boxes."""
        status_code, response = await orchestrator.process_query(
            filenames=["baseline.png", "monitoring_identical.png"],
            file_contents=[self.img1_bytes, self.img1_bytes],
            query="Detect all bi-temporal change deltas between baseline and monitoring dates."
        )

        self.assertEqual(status_code, 200)
        data = response.to_dict()
        self.assertFalse(data["error"])
        # Must confirm no changes in text
        self.assertIn("no significant", data["answer"].lower())
        # Annotation set must have zero boxes
        total_boxes = sum(len(layer.get("boxes", [])) for layer in data.get("annotation_set", []))
        self.assertEqual(total_boxes, 0)

    def test_audit_store_logging_and_feedback(self):
        """Test audit trail logging, suggestion click, and operator feedback."""
        test_qid = "test_e2e_query_123"

        # Log query
        audit_store.log_query_execution(
            query_id=test_qid,
            query_text="Test query text",
            filenames=["test.png"],
            compat_result={"valid": True},
            routing_decision={"intent": "single_image_vqa"},
            specialist_result={"model": "Test", "confidence": 0.9},
            annotation_set=[],
            suggestions=[{"text": "Follow up", "task_type": "ground_region"}],
            verification_outcome={"evidence_sufficient": True, "human_review": False},
            trace=[],
            total_duration_ms=120
        )

        # Log suggestion click
        audit_store.log_suggestion_click(
            query_id=test_qid,
            suggestion_text="Follow up",
            task_type="ground_region"
        )

        # Log operator feedback
        audit_store.log_operator_feedback(
            query_id=test_qid,
            rating="accept",
            notes="Operator verified detection"
        )

        records = audit_store.get_latest_records(limit=5)
        found = any(r.get("query_id") == test_qid for r in records)
        self.assertTrue(found)


if __name__ == "__main__":
    unittest.main()
