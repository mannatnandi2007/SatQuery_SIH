"""
SatQuery AI — Compatibility Checker
Rule-based input validator that runs BEFORE any model call.
Checks file types, image decodability, and query-image count compatibility.
"""

import os
import re
from PIL import Image
from typing import List, Tuple, Optional
from dataclasses import dataclass


SUPPORTED_EXTENSIONS = {".tif", ".tiff", ".jpg", ".jpeg", ".png"}

# Keywords that indicate change detection intent (needs 2 images)
CHANGE_DETECTION_KEYWORDS = [
    r"\bchange[ds]?\b", r"\bcompare[ds]?\b", r"\bbefore\b.*\bafter\b",
    r"\bafter\b.*\bbefore\b", r"\bdifferen\w+\b", r"\bbetween\b",
    r"\btransform\w*\b", r"\bevol\w+\b", r"\bover\s+time\b",
    r"\bprogress\w*\b", r"\btemporal\b"
]

MAX_IMAGE_SIZE_MB = 50  # Max upload size in MB


@dataclass
class CompatibilityResult:
    valid: bool
    reason: Optional[str]
    detected_intent: str  # "single_image_vqa" | "change_detection" | "unsupported"


def detect_query_intent(query: str) -> str:
    """Classify query intent based on keywords/regex patterns."""
    query_lower = query.lower().strip()

    for pattern in CHANGE_DETECTION_KEYWORDS:
        if re.search(pattern, query_lower):
            return "change_detection"

    return "single_image_vqa"


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
    Run all compatibility checks on the uploaded images and query.

    Returns a structured pass/fail with a specific reason string.
    """
    # Check: query is not empty
    if not query or not query.strip():
        return CompatibilityResult(
            valid=False,
            reason="Please enter a question about the satellite image.",
            detected_intent="unsupported"
        )

    # Check: at least one image uploaded
    if not filenames or len(filenames) == 0:
        return CompatibilityResult(
            valid=False,
            reason="Please upload at least one satellite image to analyze.",
            detected_intent="unsupported"
        )

    # Detect query intent
    detected_intent = detect_query_intent(query)

    # Check: image count matches intent
    if detected_intent == "change_detection" and len(filenames) < 2:
        return CompatibilityResult(
            valid=False,
            reason=f"Your question appears to involve change detection or comparison, which requires two images. You uploaded {len(filenames)} image(s). Please upload a second image showing the same area at a different time.",
            detected_intent=detected_intent
        )

    # Check each image
    for i, (filename, content) in enumerate(zip(filenames, file_contents)):
        # Check file extension
        ext_ok, ext_reason = check_file_extension(filename)
        if not ext_ok:
            return CompatibilityResult(
                valid=False,
                reason=ext_reason,
                detected_intent=detected_intent
            )

        # Check file size
        size_ok, size_reason = check_image_size(content, filename)
        if not size_ok:
            return CompatibilityResult(
                valid=False,
                reason=size_reason,
                detected_intent=detected_intent
            )

        # Check image decodability
        decode_ok, decode_reason = check_image_decodable(content, filename)
        if not decode_ok:
            return CompatibilityResult(
                valid=False,
                reason=decode_reason,
                detected_intent=detected_intent
            )

    return CompatibilityResult(
        valid=True,
        reason=None,
        detected_intent=detected_intent
    )
