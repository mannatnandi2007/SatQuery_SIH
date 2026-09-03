"""
SatQuery AI — Evidence Engine
Renders bounding box / mask overlays on satellite images.
"""

import os
import uuid
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64
from typing import Optional, List, Dict, Tuple


# Directory to save overlay images
OVERLAYS_DIR = os.path.join(os.path.dirname(__file__), "static", "overlays")
os.makedirs(OVERLAYS_DIR, exist_ok=True)


def draw_bounding_box(
    image_bytes: bytes,
    bbox: List[float],  # [x1_pct, y1_pct, x2_pct, y2_pct] as percentages (0-100)
    label: Optional[str] = None,
    color: Tuple[int, int, int] = (0, 255, 128),
    thickness: int = 3
) -> Tuple[str, str]:
    """
    Draw a bounding box overlay on the image.

    Args:
        image_bytes: Raw image bytes
        bbox: [x1_pct, y1_pct, x2_pct, y2_pct] as percentages of image dimensions
        label: Optional label text to draw near the box
        color: RGB color tuple for the box
        thickness: Line thickness

    Returns:
        (overlay_filename, overlay_base64)
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Convert percentage coordinates to pixel coordinates
    x1 = int(bbox[0] / 100 * w)
    y1 = int(bbox[1] / 100 * h)
    x2 = int(bbox[2] / 100 * w)
    y2 = int(bbox[3] / 100 * h)

    # Clamp to image bounds
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    # Draw rectangle with multiple passes for thickness
    for i in range(thickness):
        draw.rectangle(
            [x1 - i, y1 - i, x2 + i, y2 + i],
            outline=color
        )

    # Draw semi-transparent fill
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [x1, y1, x2, y2],
        fill=(*color, 40)  # Semi-transparent fill
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # Draw label if provided
    if label:
        draw = ImageDraw.Draw(img)
        # Background for label text
        try:
            font = ImageFont.truetype("arial.ttf", max(14, min(w, h) // 30))
        except (IOError, OSError):
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((x1, y1 - 25), label, font=font)
        draw.rectangle(
            [text_bbox[0] - 2, text_bbox[1] - 2, text_bbox[2] + 2, text_bbox[3] + 2],
            fill=color
        )
        draw.text((x1, y1 - 25), label, fill=(0, 0, 0), font=font)

    # Save to file
    filename = f"{uuid.uuid4().hex[:12]}.png"
    filepath = os.path.join(OVERLAYS_DIR, filename)
    img.save(filepath, "PNG")

    # Also create base64 version
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return filename, img_base64


def create_no_evidence_overlay(image_bytes: bytes) -> Tuple[str, str]:
    """
    Return the original image as the overlay when no bounding box is available.
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGB")

    filename = f"{uuid.uuid4().hex[:12]}.png"
    filepath = os.path.join(OVERLAYS_DIR, filename)
    img.save(filepath, "PNG")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return filename, img_base64
