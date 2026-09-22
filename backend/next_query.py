"""
SatQuery AI — Next-Query Recommendation Engine (Node N10)
Surfaces 2–4 ranked follow-up query suggestions after every answered query,
conditioned on what was just asked, what was found, and what sensor context is loaded.

Philosophical Principle:
Typed structured logic decides what to suggest; generative narration only phrases.
Suggestions are always grounded in available imagery and answer telemetry.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import re


class TaskType(str, Enum):
    SINGLE_VQA = "single_vqa"
    CAPTION_SCENE = "caption_scene"
    GROUND_REGION = "ground_region"
    BI_TEMPORAL_CHANGE = "bi_temporal_change"
    CHANGE_VQA = "change_vqa"
    OPTICAL_SAR_FUSE = "optical_sar_fuse"


# Grounded Task Transition Rules
TASK_TRANSITIONS: Dict[TaskType, List[Dict[str, Any]]] = {
    TaskType.SINGLE_VQA: [
        {
            "target_task": TaskType.GROUND_REGION,
            "template": "Show me where the {entity} are located.",
            "fallback": "Ground and localize the primary objects detected in this scene."
        },
        {
            "target_task": TaskType.CAPTION_SCENE,
            "template": "Describe the surrounding land cover and landscape context.",
            "fallback": "Provide a comprehensive scene overview and LULC description."
        },
        {
            "target_task": TaskType.BI_TEMPORAL_CHANGE,
            "template": "Has this {entity} sector changed compared to baseline imagery?",
            "fallback": "Detect any surface change deltas in this area over time."
        }
    ],
    TaskType.CAPTION_SCENE: [
        {
            "target_task": TaskType.SINGLE_VQA,
            "template": "How many {entity} can be identified in this terrain?",
            "fallback": "Count all prominent industrial or infrastructure facilities."
        },
        {
            "target_task": TaskType.GROUND_REGION,
            "template": "Highlight the boundaries of the {entity}.",
            "fallback": "Pinpoint the primary spatial hotspot identified in the overview."
        },
        {
            "target_task": TaskType.OPTICAL_SAR_FUSE,
            "template": "Cross-verify structural boundaries using SAR radar backscatter.",
            "fallback": "Perform optical and SAR radar fusion on this scene."
        }
    ],
    TaskType.GROUND_REGION: [
        {
            "target_task": TaskType.SINGLE_VQA,
            "template": "What is the structural condition or operational status of {entity}?",
            "fallback": "Analyze the operational condition of these grounded targets."
        },
        {
            "target_task": TaskType.BI_TEMPORAL_CHANGE,
            "template": "Check if these {entity} existed in the earlier acquisition.",
            "fallback": "Evaluate if these localized features represent new additions."
        },
        {
            "target_task": TaskType.CAPTION_SCENE,
            "template": "Describe the environmental risk profile around these {entity}.",
            "fallback": "Assess potential environmental hazards surrounding these objects."
        }
    ],
    TaskType.BI_TEMPORAL_CHANGE: [
        {
            "target_task": TaskType.CHANGE_VQA,
            "template": "What caused the surface alterations across the altered {entity} zone?",
            "fallback": "What specific construction or earthwork caused this change?"
        },
        {
            "target_task": TaskType.GROUND_REGION,
            "template": "Delineate the exact perimeter of new construction or disturbance.",
            "fallback": "Ground the highest-magnitude alteration hotspot with precise boxes."
        },
        {
            "target_task": TaskType.SINGLE_VQA,
            "template": "How many new structures or tracks have been added since baseline?",
            "fallback": "Count the number of new infrastructure additions."
        }
    ],
    TaskType.CHANGE_VQA: [
        {
            "target_task": TaskType.BI_TEMPORAL_CHANGE,
            "template": "Quantify the total surface alteration area in square meters.",
            "fallback": "Calculate metric area footprint of all detected change polygons."
        },
        {
            "target_task": TaskType.GROUND_REGION,
            "template": "Highlight the most altered quadrant or critical infrastructure delta.",
            "fallback": "Isolate the primary disturbance cluster on the map."
        },
        {
            "target_task": TaskType.CAPTION_SCENE,
            "template": "Assess long-term environmental impact of these alterations.",
            "fallback": "Evaluate ecological risks from ongoing land transformation."
        }
    ],
    TaskType.OPTICAL_SAR_FUSE: [
        {
            "target_task": TaskType.GROUND_REGION,
            "template": "Isolate the high-dielectric metallic vessels and radar reflections.",
            "fallback": "Ground the high-intensity radar double-bounce targets."
        },
        {
            "target_task": TaskType.SINGLE_VQA,
            "template": "What types of structures produce the strongest backscatter peaks?",
            "fallback": "Identify specific vessels or metallic installations detected."
        },
        {
            "target_task": TaskType.BI_TEMPORAL_CHANGE,
            "template": "Compare radar backscatter stability across multiple observation dates.",
            "fallback": "Check if these radar signatures remain stationary over time."
        }
    ]
}


class NextQueryRecommender:
    """
    Deterministic rule-and-transition engine for generating grounded follow-up query suggestions.
    """

    def _extract_primary_entity(self, answer_payload: Dict[str, Any]) -> str:
        """Extract the most prominent entity or count from the structured answer."""
        detected_objects = answer_payload.get("detected_objects", [])
        if detected_objects and len(detected_objects) > 0:
            # Pick first clean object label
            return str(detected_objects[0]).lower().strip()

        # Check annotation set box labels
        annotation_set = answer_payload.get("annotation_set", [])
        if annotation_set:
            for layer in annotation_set:
                boxes = layer.get("boxes", [])
                if boxes:
                    return str(boxes[0].get("label", "structures")).lower()

        # Fallback to key objects from detailed analysis
        da = answer_payload.get("detailed_analysis", {}) or {}
        key_objs = da.get("key_objects", [])
        if key_objs:
            words = key_objs[0].split()
            if len(words) >= 2:
                return " ".join(words[:3]).lower()

        return "features"

    def _extract_count_entity(self, answer_payload: Dict[str, Any]) -> Optional[str]:
        """Check if answer mentions a count (e.g. 14 buildings)."""
        answer_text = answer_payload.get("answer", "")
        match = re.search(r"\b(\d+)\s+([a-zA-Z\-_]+)", answer_text)
        if match:
            count = match.group(1)
            noun = match.group(2)
            if noun.lower() not in ["percent", "pct", "m", "px", "meters", "degrees"]:
                return f"{count} {noun}"
        return None

    def recommend(
        self,
        task_type: str,
        answer_payload: Dict[str, Any],
        loaded_image_count: int = 1,
        has_sar: bool = False,
        is_bi_temporal: bool = False,
        evidence_sufficient: bool = True,
        human_review: bool = False,
        rolling_history: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Generate 2–4 ranked follow-up suggestions strictly filtered by loaded sensor context.
        """
        try:
            curr_task = TaskType(task_type.lower())
        except ValueError:
            curr_task = TaskType.SINGLE_VQA

        transitions = TASK_TRANSITIONS.get(curr_task, TASK_TRANSITIONS[TaskType.SINGLE_VQA])

        primary_entity = self._extract_primary_entity(answer_payload)
        count_entity = self._extract_count_entity(answer_payload)

        candidate_suggestions = []

        for trans in transitions:
            target_task = trans["target_task"]

            # Filter 1: Sensor & Context Feasibility
            if target_task in [TaskType.BI_TEMPORAL_CHANGE, TaskType.CHANGE_VQA]:
                if loaded_image_count < 2 and not is_bi_temporal:
                    # Cannot suggest change query if only single image loaded
                    continue

            if target_task == TaskType.OPTICAL_SAR_FUSE:
                if not has_sar and loaded_image_count < 2:
                    continue

            # Template Filling
            entity_fill = count_entity if count_entity and "where the" in trans["template"] else primary_entity
            text = trans["template"].format(entity=entity_fill)

            candidate_suggestions.append({
                "text": text,
                "task_type": target_task.value
            })

        # Ranking logic:
        # If human_review is True or evidence insufficient, prioritize grounding / evidence gathering
        def rank_score(item: Dict[str, str]) -> float:
            score = 1.0
            t = item["task_type"]

            # Prioritize grounding if uncertainty exists
            if human_review or not evidence_sufficient:
                if t == TaskType.GROUND_REGION.value:
                    score += 2.0
                elif t == TaskType.OPTICAL_SAR_FUSE.value:
                    score += 1.5

            # Anti-repetition penalty with rolling history
            if rolling_history:
                recent_occurrences = rolling_history.count(t)
                score -= (recent_occurrences * 0.5)

            return score

        candidate_suggestions.sort(key=rank_score, reverse=True)

        # Ensure between 2 and 4 suggestions
        final_suggestions = candidate_suggestions[:4]
        if len(final_suggestions) < 2:
            # Fallback safe suggestions
            if loaded_image_count >= 2:
                final_suggestions.append({
                    "text": "Detect all temporal alterations between baseline and monitoring scenes.",
                    "task_type": TaskType.BI_TEMPORAL_CHANGE.value
                })
            else:
                final_suggestions.append({
                    "text": "Describe the surrounding land cover and operational environment.",
                    "task_type": TaskType.CAPTION_SCENE.value
                })

        return {
            "suggestions": final_suggestions[:4]
        }


# Global singleton instance
next_query_recommender = NextQueryRecommender()
