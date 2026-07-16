"""
VLM API client for hazard detection.

Isolates the vision-language model call behind a single function
(`analyze_image_for_hazards`) so the backend can be swapped (e.g. from
Gemini to GPT-4o-mini vision) without touching app.py.
"""

import json
import os
import re

from google import genai
from google.genai import types

from steadi_checklist import checklist_as_prompt_text

GEMINI_MODEL = "gemini-3-flash-preview"

RESPONSE_SCHEMA_HINT = """
Return ONLY valid JSON (no markdown fences, no commentary) matching exactly
this schema:

{
  "hazards": [
    {
      "label": "string, short hazard name",
      "severity": "low | medium | high",
      "description": "plain-language explanation of the risk",
      "recommendation": "concrete fix, grounded in the STEADI checklist",
      "bounding_box": {"x_min": 0.0, "y_min": 0.0, "x_max": 0.0, "y_max": 0.0}
    }
  ]
}

Bounding box coordinates must be normalized floats between 0.0 and 1.0,
relative to the image width (x) and height (y). If there are no hazards,
return {"hazards": []}.
"""


class VLMError(Exception):
    """Raised when the VLM call or response parsing fails."""


def _build_system_prompt() -> str:
    checklist_text = checklist_as_prompt_text()
    return f"""You are a home fall-risk safety assistant for a caregiving
app. You analyze a single photo of a room belonging to an elderly person
and identify potential fall hazards, grounded strictly in the CDC STEADI
home safety checklist below. Do not diagnose medical conditions. Do not
invent hazards that are not visible in the image.

CDC STEADI Home Fall Prevention Checklist reference:
{checklist_text}

For each hazard you identify in the image, provide a bounding box drawn
tightly around the specific object or area causing the risk.

{RESPONSE_SCHEMA_HINT}
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text.strip()).strip()
    return json.loads(text)


def _validate_hazards(data: dict) -> dict:
    if not isinstance(data, dict) or "hazards" not in data:
        raise VLMError("Response JSON missing 'hazards' key.")

    hazards = data["hazards"]
    if not isinstance(hazards, list):
        raise VLMError("'hazards' must be a list.")

    valid_severities = {"low", "medium", "high"}
    cleaned = []
    for h in hazards:
        if not isinstance(h, dict):
            continue
        bbox = h.get("bounding_box", {})
        try:
            x_min = float(bbox.get("x_min", 0.0))
            y_min = float(bbox.get("y_min", 0.0))
            x_max = float(bbox.get("x_max", 0.0))
            y_max = float(bbox.get("y_max", 0.0))
        except (TypeError, ValueError):
            continue

        x_min = min(max(x_min, 0.0), 1.0)
        y_min = min(max(y_min, 0.0), 1.0)
        x_max = min(max(x_max, 0.0), 1.0)
        y_max = min(max(y_max, 0.0), 1.0)
        if x_max <= x_min or y_max <= y_min:
            continue

        severity = str(h.get("severity", "low")).strip().lower()
        if severity not in valid_severities:
            severity = "low"

        cleaned.append(
            {
                "label": str(h.get("label", "Unlabeled hazard")).strip(),
                "severity": severity,
                "description": str(h.get("description", "")).strip(),
                "recommendation": str(h.get("recommendation", "")).strip(),
                "bounding_box": {
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                },
            }
        )

    return {"hazards": cleaned}


def analyze_image_for_hazards(image_bytes: bytes, mime_type: str) -> dict:
    """
    Send an image to the VLM and return a validated hazards dict:
    {"hazards": [ {label, severity, description, recommendation,
    bounding_box}, ... ]}

    Raises VLMError on any failure (network, auth, parsing).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise VLMError(
            "GEMINI_API_KEY is not set. Add it to your .env file or "
            "environment variables."
        )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                _build_system_prompt(),
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
    except Exception as exc:  # noqa: BLE001 - surface as a friendly VLMError
        raise VLMError(f"VLM API request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise VLMError("VLM API returned an empty response.")

    try:
        data = _extract_json(text)
    except json.JSONDecodeError as exc:
        raise VLMError(f"Could not parse VLM response as JSON: {exc}") from exc

    return _validate_hazards(data)
