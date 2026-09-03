"""
SatQuery AI — Confidence Score
Maps raw model confidence to High/Medium/Low labels.
"""

from typing import Dict


def compute_confidence(raw_score: float) -> Dict:
    """
    Map a raw confidence score (0.0 - 1.0) to a labeled confidence result.

    Thresholds:
        High:   > 0.8
        Medium: 0.5 - 0.8
        Low:    < 0.5
    """
    # Clamp to valid range
    score = max(0.0, min(1.0, raw_score))

    if score > 0.8:
        label = "High"
    elif score >= 0.5:
        label = "Medium"
    else:
        label = "Low"

    return {
        "label": label,
        "score": round(score, 3)
    }
