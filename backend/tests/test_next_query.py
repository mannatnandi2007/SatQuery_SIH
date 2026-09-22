"""
SatQuery AI — Unit Tests for Next-Query Recommendation Engine (Node N10)
Tests task-transition rules, sensor context filtering, entity template filling,
ranking logic under uncertainty/human-review, and rolling history anti-repetition.
"""

import unittest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from next_query import next_query_recommender, TaskType


class TestNextQueryRecommender(unittest.TestCase):
    """Unit tests for Node N10 in complete isolation using synthetic state dicts."""

    def setUp(self):
        self.recommender = next_query_recommender

    def test_single_vqa_transitions_with_entities(self):
        """Verify single_vqa generates grounded suggestions with detected entities."""
        synthetic_payload = {
            "answer": "Detected 14 buildings in the northern commercial complex.",
            "detected_objects": ["buildings", "roadway"],
            "annotation_set": [
                {
                    "layer_id": "buildings_count",
                    "reasoning": "count",
                    "color": "#2E7DD1",
                    "boxes": [{"id": i, "bbox": [10, 10, 20, 20], "label": f"Building {i}", "confidence": 0.9} for i in range(14)]
                }
            ],
            "detailed_analysis": {"key_objects": ["14 commercial warehouse buildings"]}
        }

        result = self.recommender.recommend(
            task_type="single_vqa",
            answer_payload=synthetic_payload,
            loaded_image_count=1,
            has_sar=False,
            is_bi_temporal=False,
            evidence_sufficient=True,
            human_review=False
        )

        self.assertIn("suggestions", result)
        suggestions = result["suggestions"]
        self.assertGreaterEqual(len(suggestions), 2)
        self.assertLessEqual(len(suggestions), 4)

        # Ensure ground_region is suggested
        task_types = [s["task_type"] for s in suggestions]
        self.assertIn(TaskType.GROUND_REGION.value, task_types)

        # Verify template filled with count/entity
        ground_suggestion = next(s for s in suggestions if s["task_type"] == TaskType.GROUND_REGION.value)
        self.assertTrue("14 buildings" in ground_suggestion["text"] or "buildings" in ground_suggestion["text"])

    def test_sensor_context_filtering_single_image(self):
        """Verify bi_temporal_change is NOT suggested when only 1 image is loaded."""
        synthetic_payload = {
            "answer": "Runway 09/27 observed with asphalt surfacing.",
            "detected_objects": ["runway"]
        }

        result = self.recommender.recommend(
            task_type="single_vqa",
            answer_payload=synthetic_payload,
            loaded_image_count=1,
            has_sar=False,
            is_bi_temporal=False
        )

        task_types = [s["task_type"] for s in result["suggestions"]]
        self.assertNotIn(TaskType.BI_TEMPORAL_CHANGE.value, task_types)
        self.assertNotIn(TaskType.CHANGE_VQA.value, task_types)

    def test_sensor_context_filtering_dual_images(self):
        """Verify bi_temporal_change IS allowed when 2 images are loaded."""
        synthetic_payload = {
            "answer": "Surface disturbance observed between acquisition dates.",
            "detected_objects": ["construction ground"]
        }

        result = self.recommender.recommend(
            task_type="bi_temporal_change",
            answer_payload=synthetic_payload,
            loaded_image_count=2,
            has_sar=False,
            is_bi_temporal=True
        )

        task_types = [s["task_type"] for s in result["suggestions"]]
        self.assertTrue(
            TaskType.CHANGE_VQA.value in task_types or TaskType.GROUND_REGION.value in task_types
        )

    def test_ranking_under_human_review(self):
        """Verify evidence-gathering tasks are ranked highest when human_review=True."""
        synthetic_payload = {
            "answer": "Potential vessel anomaly detected under cloud cover.",
            "detected_objects": ["vessel"]
        }

        result = self.recommender.recommend(
            task_type="caption_scene",
            answer_payload=synthetic_payload,
            loaded_image_count=1,
            evidence_sufficient=False,
            human_review=True
        )

        suggestions = result["suggestions"]
        self.assertGreaterEqual(len(suggestions), 2)
        # First suggestion should be grounding/evidence gathering
        first_task = suggestions[0]["task_type"]
        self.assertIn(first_task, [TaskType.GROUND_REGION.value, TaskType.SINGLE_VQA.value])

    def test_rolling_history_anti_repetition(self):
        """Verify recently asked tasks in rolling history are penalized in ranking."""
        synthetic_payload = {
            "answer": "Port docks and container yards.",
            "detected_objects": ["port"]
        }

        # User has already asked ground_region twice recently
        rolling_history = ["ground_region", "ground_region", "single_vqa"]

        result = self.recommender.recommend(
            task_type="caption_scene",
            answer_payload=synthetic_payload,
            loaded_image_count=1,
            rolling_history=rolling_history
        )

        suggestions = result["suggestions"]
        # The first suggestion should NOT be ground_region due to repetition penalty
        self.assertNotEqual(suggestions[0]["task_type"], "ground_region")


if __name__ == "__main__":
    unittest.main()
