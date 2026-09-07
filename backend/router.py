"""
SatQuery AI — Query Router
Lightweight intent classifier using keyword/regex rules.
Routes queries to the appropriate specialist.
"""

import re
from typing import Tuple


# Pattern groups for intent classification
CHANGE_DETECTION_PATTERNS = [
    r"\bchange[ds]?\b",
    r"\bcompare[ds]?\b",
    r"\bbefore\s+and\s+after\b",
    r"\bafter\b.*\bbefore\b",
    r"\bdifferen\w+\b",
    r"\bbetween\b.*\b(image|photo|time|year|period)\w*\b",
    r"\btransform\w*\b",
    r"\bevol\w+\b",
    r"\bover\s+time\b",
    r"\bprogress\w*\b",
    r"\btemporal\b",
    r"\bgrow[nth]*\b",
    r"\bexpan[dsion]+\b",
    r"\bshrink\w*\b",
    r"\bdeforest\w*\b",
    r"\burbaniz\w*\b",
]

FUSION_PATTERNS = [
    r"\bsar\b",
    r"\bradar\b",
    r"\boptical\s*[\+&]\s*sar\b",
    r"\bfus[eion]+\b.*\b(sar|radar)\b",
    r"\bmulti[\-\s]?sensor\b",
    r"\bbackscatter\b",
    r"\bsentinel[\-\s]?1\b",
    r"\bpolarimetr\w*\b",
    r"\bc[\-\s]?band\b",
]

VQA_PATTERNS = [
    r"\bwhat\b", r"\bwhere\b", r"\bhow\s+many\b", r"\bis\s+there\b",
    r"\bare\s+there\b", r"\bidentif\w+\b", r"\bdetect\w*\b", r"\bfind\b",
    r"\bcount\b", r"\blocate\b", r"\bdescribe\b", r"\bshow\b",
    r"\bclassif\w+\b", r"\bsegment\w*\b", r"\banalyze\b", r"\banalyse\b",
]


def classify_intent(query: str) -> str:
    """
    Classify the query intent based on keyword/regex patterns.

    Returns one of:
        - "single_image_vqa"
        - "change_detection"
        - "fusion"
        - "unsupported"
    """
    query_lower = query.lower().strip()

    if not query_lower:
        return "unsupported"

    # Check for fusion patterns first (most specific)
    for pattern in FUSION_PATTERNS:
        if re.search(pattern, query_lower):
            return "fusion"

    # Check for change detection patterns
    for pattern in CHANGE_DETECTION_PATTERNS:
        if re.search(pattern, query_lower):
            return "change_detection"

    # Default to VQA for any question-like query
    for pattern in VQA_PATTERNS:
        if re.search(pattern, query_lower):
            return "single_image_vqa"

    # If it's a sentence/question but doesn't match specific patterns, still try VQA
    if len(query_lower.split()) >= 2:
        return "single_image_vqa"

    return "unsupported"


def route_query(query: str) -> Tuple[str, str]:
    """
    Route the query to the appropriate specialist.

    Returns:
        (intent, specialist_name)
    """
    intent = classify_intent(query)

    specialist_map = {
        "single_image_vqa": "RS-VLM",
        "change_detection": "Change Detection",
        "fusion": "Optical+SAR Fusion",
        "unsupported": "None",
    }

    return intent, specialist_map[intent]
