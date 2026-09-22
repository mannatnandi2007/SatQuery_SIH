"""
SatQuery AI — Multi-Box Visual Grounding & Overlay Renderer (Node N11)
Renders multi-layer, color-coded bounding boxes on normalized satellite imagery.
Features:
- Separate visual layers per reasoning type (count, change, grounding, SAR anomaly)
- Sequential box numbering per layer (e.g., #1, #2...)
- High-contrast legend strip displaying layer summaries (e.g. '🔵 Count — 14 buildings')
- Metric scale bar calibrated to GSD
- Preserves raw AnnotationSet for client-side interactive toggling
"""

import os
import uuid
import base64
from io import BytesIO
from typing import Optional, List, Dict, Tuple, Any
from PIL import Image, ImageDraw, ImageFont

from annotation_schema import AnnotationSet, AnnotationLayer, GroundingBox
from gsd_normalizer import gsd_normalizer

OVERLAYS_DIR = os.path.join(os.path.dirname(__file__), "static", "overlays")
os.makedirs(OVERLAYS_DIR, exist_ok=True)


def _get_font(size: int = 12):
    """Retrieve font with fallback."""
    for font_name in ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf", "consola.ttf"]:
        try:
            return ImageFont.truetype(font_name, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Convert HEX color string to RGB tuple."""
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join(c * 2 for c in hex_code)
    try:
        return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return (0, 229, 255)


class MultiBoxOverlayRenderer:
    """
    Renders standardized AnnotationSet onto satellite imagery.
    """

    def __init__(self, overlays_dir: str = OVERLAYS_DIR):
        self.overlays_dir = overlays_dir

    def render(
        self,
        image_bytes: bytes,
        annotation_set: AnnotationSet,
        gsd_m: float = 10.0,
        draw_legend: bool = True
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Renders multi-layer bounding boxes with distinct colors, numbered labels,
        and an industrial legend strip.
        Returns: (filename, base64_str, metric_info)
        """
        base_img = Image.open(BytesIO(image_bytes)).convert("RGB")
        w, h = base_img.size

        # If annotation_set is empty, save base image without overlays
        if annotation_set.is_empty():
            filename = f"scene_{uuid.uuid4().hex[:12]}.png"
            filepath = os.path.join(self.overlays_dir, filename)
            base_img.save(filepath, "PNG")

            buf = BytesIO()
            base_img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return filename, b64, {"gsd_m": gsd_m, "box_count": 0}

        # Create semi-transparent overlay for box fills
        fill_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        fill_draw = ImageDraw.Draw(fill_overlay)

        # Primary drawing canvas
        img_out = base_img.copy()

        # Step 1: Draw box fills and borders
        for layer in annotation_set.layers:
            color_rgb = _hex_to_rgb(layer.color)

            for box in layer.boxes:
                c1, c2, c3, c4 = box.bbox
                x1 = int(min(c1, c3) / 100.0 * w)
                y1 = int(min(c2, c4) / 100.0 * h)
                x2 = int(max(c1, c3) / 100.0 * w)
                y2 = int(max(c2, c4) / 100.0 * h)

                x1, y1 = max(0, min(x1, x2)), max(0, min(y1, y2))
                x2, y2 = min(w, max(x1, x2)), min(h, max(y1, y2))

                # Fill with transparent tint (alpha = 35)
                fill_draw.rectangle([x1, y1, x2, y2], fill=(*color_rgb, 35))

        # Alpha composite fills
        img_out = Image.alpha_composite(img_out.convert("RGBA"), fill_overlay).convert("RGB")
        draw = ImageDraw.Draw(img_out)

        font_label = _get_font(max(10, min(w, h) // 40))

        # Step 2: Draw crisp borders, corner reticles, and numbered tags
        for layer in annotation_set.layers:
            color_rgb = _hex_to_rgb(layer.color)

            for box in layer.boxes:
                c1, c2, c3, c4 = box.bbox
                x1 = int(min(c1, c3) / 100.0 * w)
                y1 = int(min(c2, c4) / 100.0 * h)
                x2 = int(max(c1, c3) / 100.0 * w)
                y2 = int(max(c2, c4) / 100.0 * h)

                x1, y1 = max(0, min(x1, x2)), max(0, min(y1, y2))
                x2, y2 = min(w, max(x1, x2)), min(h, max(y1, y2))

                # Double-line border for high contrast
                draw.rectangle([x1, y1, x2, y2], outline=color_rgb, width=2)

                # Corner reticle ticks
                tick_len = min(12, max(4, (x2 - x1) // 5))
                draw.line([(x1, y1), (x1 + tick_len, y1)], fill=(255, 255, 255), width=2)
                draw.line([(x1, y1), (x1, y1 + tick_len)], fill=(255, 255, 255), width=2)
                draw.line([(x2, y2), (x2 - tick_len, y2)], fill=(255, 255, 255), width=2)
                draw.line([(x2, y2), (x2, y2 - tick_len)], fill=(255, 255, 255), width=2)

                # Numbered Tag Label: e.g. "#1 0.94" or "Building 1"
                box_title = f"#{box.id} {box.label}" if box.label else f"#{box.id}"
                if box.confidence and box.confidence < 1.0:
                    box_title += f" ({box.confidence:.2f})"

                tag_bbox = draw.textbbox((x1, max(0, y1 - 18)), box_title, font=font_label)
                tw = tag_bbox[2] - tag_bbox[0] + 6
                th = tag_bbox[3] - tag_bbox[1] + 4

                # Dark backdrop pill
                draw.rectangle([x1, max(0, y1 - th), x1 + tw, max(0, y1)], fill=(14, 18, 26))
                draw.rectangle([x1, max(0, y1 - th), x1 + tw, max(0, y1)], outline=color_rgb, width=1)
                draw.text((x1 + 3, max(0, y1 - th) + 1), box_title, fill=color_rgb, font=font_label)

        # Step 3: Draw Calibrated Metric Scale Bar
        from evidence import draw_metric_scale_bar
        draw_metric_scale_bar(draw, w, h, gsd_m)

        # Step 4: Draw Legend Strip if multiple layers or requested
        if draw_legend and len(annotation_set.layers) > 0:
            legend_h = 32
            legend_canvas = Image.new("RGB", (w, h + legend_h), (14, 18, 26))
            legend_canvas.paste(img_out, (0, 0))
            legend_draw = ImageDraw.Draw(legend_canvas)

            font_legend = _get_font(11)
            offset_x = 16
            legend_y = h + 8

            for layer in annotation_set.layers:
                color_rgb = _hex_to_rgb(layer.color)
                count = len(layer.boxes)
                reason_label = layer.reasoning.replace("_", " ").title()
                legend_text = f"{reason_label} ({count})"

                # Color bullet dot
                legend_draw.ellipse([offset_x, legend_y + 2, offset_x + 10, legend_y + 12], fill=color_rgb)
                legend_draw.text((offset_x + 16, legend_y), legend_text, fill=(240, 245, 255), font=font_legend)

                bbox_t = legend_draw.textbbox((offset_x + 16, legend_y), legend_text, font=font_legend)
                offset_x += (bbox_t[2] - bbox_t[0]) + 36

            final_img = legend_canvas
        else:
            final_img = img_out

        filename = f"overlay_{uuid.uuid4().hex[:12]}.png"
        filepath = os.path.join(self.overlays_dir, filename)
        final_img.save(filepath, "PNG")

        buf = BytesIO()
        final_img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        metric_info = {
            "gsd_m": gsd_m,
            "total_layers": len(annotation_set.layers),
            "total_boxes": annotation_set.total_boxes_count()
        }

        return filename, b64, metric_info


# Singleton instance
multi_box_renderer = MultiBoxOverlayRenderer()
