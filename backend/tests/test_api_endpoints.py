"""
SatQuery AI — Unit Tests for FastAPI Endpoints
Tests /health, /compatibility-check, /query, /feedback, /suggestion/click, /audit.
"""

import unittest
import sys
import os
from io import BytesIO
from PIL import Image
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app


class TestAPIEndpoints(unittest.TestCase):
    """Test suite for FastAPI REST API endpoints."""

    def setUp(self):
        self.client = TestClient(app)

        # Create synthetic test image
        img = Image.new("RGB", (256, 256), color=(40, 80, 120))
        buf = BytesIO()
        img.save(buf, format="PNG")
        self.img_bytes = buf.getvalue()

    def test_health_endpoint(self):
        """Test GET /health returns running status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "running")

    def test_compatibility_check_endpoint(self):
        """Test POST /compatibility-check with valid image and query."""
        response = self.client.post(
            "/compatibility-check",
            files={"images": ("scene.png", self.img_bytes, "image/png")},
            data={"query": "Detect all harbor vessels."}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])

    def test_query_endpoint_with_suggestions_and_annotations(self):
        """Test POST /query returns 200 with suggestions and annotation_set."""
        response = self.client.post(
            "/query",
            files={"images": ("scene.png", self.img_bytes, "image/png")},
            data={"query": "Count how many buildings are located in this industrial complex."}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["error"])
        self.assertIn("answer", data)
        self.assertIn("suggestions", data)
        self.assertIn("annotation_set", data)
        self.assertGreaterEqual(len(data["suggestions"]), 2)

    def test_feedback_endpoint(self):
        """Test POST /feedback logs operator verification."""
        response = self.client.post(
            "/feedback",
            json={
                "query_id": "test_api_query_456",
                "rating": "accept",
                "notes": "Verified bounding coordinates."
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_suggestion_click_endpoint(self):
        """Test POST /suggestion/click records chip click telemetry."""
        response = self.client.post(
            "/suggestion/click",
            json={
                "query_id": "test_api_query_456",
                "suggestion_text": "Show me where the buildings are located.",
                "task_type": "ground_region"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "recorded")

    def test_audit_endpoint(self):
        """Test GET /audit returns latest audit ledger records."""
        response = self.client.get("/audit?limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("records", data)
        self.assertIsInstance(data["records"], list)

    def test_active_learning_queue_endpoint(self):
        """Test GET /active-learning/queue returns prioritized triage queue."""
        response = self.client.get("/active-learning/queue?limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ready")
        self.assertIn("queue", data)
        self.assertIsInstance(data["queue"], list)

    def test_self_adapt_status_endpoint(self):
        """Test GET /self-adapt/status returns calibration profile."""
        response = self.client.get("/self-adapt/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "active")
        self.assertIn("profile", data)
        self.assertIn("acceptance_rate", data["profile"])


if __name__ == "__main__":
    unittest.main()
