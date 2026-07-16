"""Pillow-based drawing of hazard bounding boxes onto a copy of the image."""

from PIL import Image, ImageDraw, ImageFont

SEVERITY_COLORS = {
    "high": (220, 38, 38),      # red
    "medium": (245, 158, 11),   # orange
    "low": (234, 179, 8),       # yellow
}
DEFAULT_COLOR = (107, 114, 128)  # gray fallback
MISSING_DEVICE_COLOR = (37, 99, 235)  # blue


def is_missing_device(hazard: dict) -> bool:
    """True if this entry represents a recommended-but-absent safety
    device rather than a hazard actually visible in the photo, per the
    "Missing: <device>" label convention set in vlm_client.py's prompt.
    """
    return hazard.get("label", "").strip().lower().startswith("missing")


def _load_font(size: int):
    try:
        return ImageFont.truetype("Arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _draw_dashed_rectangle(draw, bbox, color, width, dash=12, gap=8):
    x_min, y_min, x_max, y_max = bbox
    edges = [
        ((x_min, y_min), (x_max, y_min)),
        ((x_max, y_min), (x_max, y_max)),
        ((x_max, y_max), (x_min, y_max)),
        ((x_min, y_max), (x_min, y_min)),
    ]
    for (sx, sy), (ex, ey) in edges:
        length = ((ex - sx) ** 2 + (ey - sy) ** 2) ** 0.5
        if length == 0:
            continue
        dx, dy = (ex - sx) / length, (ey - sy) / length
        pos = 0.0
        while pos < length:
            seg_end = min(pos + dash, length)
            draw.line(
                [
                    (sx + dx * pos, sy + dy * pos),
                    (sx + dx * seg_end, sy + dy * seg_end),
                ],
                fill=color,
                width=width,
            )
            pos += dash + gap


def annotate_image(image: Image.Image, hazards: list[dict]) -> Image.Image:
    """Return a copy of `image` with hazard bounding boxes drawn on it."""
    annotated = image.convert("RGB").copy()
    draw = ImageDraw.Draw(annotated)
    width, height = annotated.size

    box_width = max(2, round(min(width, height) * 0.004))
    font_size = max(12, round(min(width, height) * 0.02))
    font = _load_font(font_size)

    for hazard in hazards:
        bbox = hazard.get("bounding_box", {})
        x_min = bbox.get("x_min", 0.0) * width
        y_min = bbox.get("y_min", 0.0) * height
        x_max = bbox.get("x_max", 0.0) * width
        y_max = bbox.get("y_max", 0.0) * height

        missing = is_missing_device(hazard)
        if missing:
            color = MISSING_DEVICE_COLOR
            _draw_dashed_rectangle(draw, (x_min, y_min, x_max, y_max), color, box_width)
        else:
            color = SEVERITY_COLORS.get(hazard.get("severity", "low"), DEFAULT_COLOR)
            draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=box_width)

        label = hazard.get("label", "")
        if label:
            text_bbox = draw.textbbox((0, 0), label, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            pad = 4
            label_y = max(0, y_min - text_h - 2 * pad)
            draw.rectangle(
                [x_min, label_y, x_min + text_w + 2 * pad, label_y + text_h + 2 * pad],
                fill=color,
            )
            draw.text(
                (x_min + pad, label_y + pad),
                label,
                fill=(255, 255, 255),
                font=font,
            )

    return annotated
