"""
SatQuery AI — Compatibility Checker with GSD Spatial Arbitration
Track A: Madhura & Dipesh

Rule-based input validator that runs BEFORE any model call.
Checks file types, image decodability, query-image count compatibility,
and Ground Sampling Distance (GSD) cross-image resolution arbitration.
"""

import os
import re
from PIL import Image
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, asdict

from gsd_normalizer import gsd_normalizer, GSDMetadata


SUPPORTED_EXTENSIONS = {".tif", ".tiff", ".jpg", ".jpeg", ".png"}

# Keywords indicating change detection intent (needs 2 images)
CHANGE_DETECTION_KEYWORDS = [
    r"\bchange[ds]?\b", r"\bcompare[ds]?\b", r"\bbefore\b.*\bafter\b",
    r"\bafter\b.*\bbefore\b", r"\bdifferen\w+\b", r"\bbetween\b",
    r"\btransform\w*\b", r"\bevol\w+\b", r"\bover\s+time\b",
    r"\bprogress\w*\b", r"\btemporal\b"
]

MAX_IMAGE_SIZE_MB = 50  # Max upload size in MB
MAX_GSD_RATIO_REJECT = 6.0  # Disallow comparisons beyond 6x scale disparity without warning
MAX_GSD_RATIO_WARN = 3.5    # Warn user about resolution discrepancy


@dataclass
class CompatibilityResult:
    valid: bool
    reason: Optional[str]
    detected_intent: str  # "single_image_vqa" | "change_detection" | "fusion" | "unsupported"
    gsd_metadata: Optional[List[Dict[str, Any]]] = None
    gsd_ratio: Optional[float] = None
    gsd_warning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def detect_query_intent(query: str, image_count: int = 1) -> str:
    """Classify query intent based on router patterns and image count."""
    from router import classify_intent
    intent = classify_intent(query)
    # If user uploads 2 images and intent was single_image_vqa, upgrade to change detection
    if image_count >= 2 and intent == "single_image_vqa":
        return "change_detection"
    return intent


def check_file_extension(filename: str) -> Tuple[bool, Optional[str]]:
    """Check if the file has a supported extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Supported formats: GeoTIFF (.tif, .tiff), JPEG (.jpg, .jpeg), PNG (.png)."
    return True, None


def check_image_decodable(image_bytes: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """Check if the image can be opened and decoded."""
    try:
        from io import BytesIO
        img = Image.open(BytesIO(image_bytes))
        img.verify()  # Verify it's not corrupt
        return True, None
    except Exception as e:
        return False, f"Image '{filename}' appears to be corrupt or unreadable: {str(e)}"


def check_image_size(image_bytes: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """Check if the image is within size limits."""
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        return False, f"Image '{filename}' is too large ({size_mb:.1f} MB). Maximum allowed size is {MAX_IMAGE_SIZE_MB} MB."
    return True, None


def run_compatibility_check(
    filenames: List[str],
    file_contents: List[bytes],
    query: str
) -> CompatibilityResult:
    """
    Run all compatibility checks on uploaded imagery and query,
    including GSD spatial scale arbitration.
    """
    # Check 1: Query is not empty
    if not query or not query.strip():
        return CompatibilityResult(
            valid=False,
            reason="Please enter a question about the satellite image.",
            detected_intent="unsupported"
        )

    # Check 2: At least one image uploaded
    if not filenames or len(filenames) == 0:
        return CompatibilityResult(
            valid=False,
            reason="Please upload at least one satellite image to analyze.",
            detected_intent="unsupported"
        )

    # Detect query intent
    detected_intent = detect_query_intent(query, len(filenames))

    # Check 3: Image count matches intent
    if detected_intent == "change_detection" and len(filenames) < 2:
        return CompatibilityResult(
            valid=False,
            reason=f"Your query suggests bi-temporal change detection, which requires 2 scenes. You provided {len(filenames)} scene(s). Please upload both baseline (T1) and monitoring (T2) scenes.",
            detected_intent=detected_intent
        )

    # Check 4: Individual image integrity checks
    for filename, content in zip(filenames, file_contents):
        ext_ok, ext_reason = check_file_extension(filename)
        if not ext_ok:
            return CompatibilityResult(valid=False, reason=ext_reason, detected_intent=detected_intent)

        size_ok, size_reason = check_image_size(content, filename)
        if not size_ok:
            return CompatibilityResult(valid=False, reason=size_reason, detected_intent=detected_intent)

        decode_ok, decode_reason = check_image_decodable(content, filename)
        if not decode_ok:
            return CompatibilityResult(valid=False, reason=decode_reason, detected_intent=detected_intent)

    # Check 5: GSD Spatial Scale Arbitration (Madhura & Dipesh)
    gsd_metas = []
    for filename, content in zip(filenames, file_contents):
        meta = gsd_normalizer.detect_gsd(content, filename)
        gsd_metas.append(meta.to_dict())

    gsd_ratio = None
    gsd_warning = None

    if len(gsd_metas) >= 2:
        gsd1 = gsd_metas[0]["detected_gsd_m"]
        gsd2 = gsd_metas[1]["detected_gsd_m"]
        ratio = max(gsd1 / max(gsd2, 1e-4), gsd2 / max(gsd1, 1e-4))
        gsd_ratio = round(ratio, 2)

        if ratio > MAX_GSD_RATIO_REJECT:
            return CompatibilityResult(
                valid=False,
                reason=f"Severe spatial resolution mismatch ({ratio:.1f}x difference): Scene 1 has {gsd1}m GSD while Scene 2 has {gsd2}m GSD. Comparing disparate scales without coregistered decimation will cause false positive change artifacts.",
                detected_intent=detected_intent,
                gsd_metadata=gsd_metas,
                gsd_ratio=gsd_ratio
            )
        elif ratio > MAX_GSD_RATIO_WARN:
            gsd_warning = f"Noticeable scale difference ({ratio:.1f}x ratio between {gsd1}m and {gsd2}m). Automated anti-aliased Lanczos resampling will normalize spatial ground scale."

    return CompatibilityResult(
        valid=True,
        reason=None,
        detected_intent=detected_intent,
        gsd_metadata=gsd_metas,
        gsd_ratio=gsd_ratio,
        gsd_warning=gsd_warning
    )
