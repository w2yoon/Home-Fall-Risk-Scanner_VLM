"""
VLM API client for hazard detection.

Isolates the vision-language model call behind a single function
(`analyze_image_for_hazards`) so the backend can be swapped (e.g. from
Gemini to GPT-4o-mini vision) without touching app.py.
"""

from __future__ import annotations

import json
import os
import re

from google import genai
from google.genai import types

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


def _grounding_text(applicable_hazards: list[dict]) -> str:
    """Flatten a personalized (pre-filtered) subset of hazards.json into
    plain text for prompt injection. Callers must pass only items that
    already apply to this profile — see core/personalization.py. This
    function does not do any filtering itself; applicability is decided
    in code, not by the model.
    """
    lines = []
    for item in applicable_hazards:
        severity = item.get("effective_severity", item.get("severity_default", "low"))
        rooms = ", ".join(item.get("rooms", []))
        lines.append(f"- [{rooms}] {item['label']} (baseline severity: {severity})")
        lines.append(f"  Risk: {item['simple']['risk']}")
        lines.append(f"  Fix: {item['simple']['fix']}")
    return "\n".join(lines)


def _profile_directive(physical_profile: dict | None) -> str:
    if not physical_profile:
        return ""

    parts = []
    hand_function = physical_profile.get("hand_function")
    if hand_function and hand_function != "both":
        side = "left" if "left" in hand_function else "right" if "right" in hand_function else None
        if side:
            parts.append(
                f"This person has {hand_function.replace('_', ' ')}. When recommending "
                f"a grab bar, handle, or rail, specify which side of the fixture it "
                f"should be mounted on so it's reachable with their {side} hand — base "
                f"this on what's visible in the photo, not a guess."
            )
        else:
            parts.append(
                f"This person has {hand_function.replace('_', ' ')}. Account for this "
                f"when recommending anything that needs to be gripped."
            )
    vision = physical_profile.get("vision")
    if vision == "low_vision":
        parts.append(
            "This person has low vision. Weight lighting and color-contrast issues "
            "more heavily in your descriptions."
        )
    if not parts:
        return ""
    return "\nThis scan is personalized for a specific person:\n" + "\n".join(f"- {p}" for p in parts) + "\n"


def _build_system_prompt(applicable_hazards: list[dict], physical_profile: dict | None) -> str:
    grounding_text = _grounding_text(applicable_hazards)
    profile_directive = _profile_directive(physical_profile)
    return f"""You are a home fall-risk safety assistant for a caregiving
app. You analyze a single photo of a room belonging to an elderly person
and identify TWO types of fall-risk signals, grounded strictly in the
reference list below — a knowledge base of hazards sourced from CDC
STEADI, NIA, CPSC, the ADA Standards for Accessible Design, FDA, and NHS
guidance, already filtered to what's relevant for this specific person:

1. VISIBLE HAZARDS: Objects or conditions in the photo that pose a fall
   risk (e.g., loose rugs, clutter, poor lighting, narrow walkways).
2. MISSING ASSISTIVE DEVICES: Safety equipment that is commonly needed
   in this type of space for an elderly person, but is NOT visible in
   the photo (e.g., no grab bar near the toilet, no non-slip mat in the
   shower).

For missing assistive devices, draw the bounding box around the AREA
where the device would typically be installed (e.g., the wall next to
the toilet), not around an object that doesn't exist. Set the "label"
field to clearly indicate this is a missing item, e.g. "Missing: Grab
bar". Only flag a missing item if it appears in the reference list below
— do not suggest devices that aren't in the list, even if they seem
reasonable, because applicability to this person has already been
decided before this prompt was built.

Do not diagnose medical conditions. Do not invent visible hazards that
are not actually present in the image.
{profile_directive}
Reference list — hazards and missing devices relevant to this person:
{grounding_text}

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


def analyze_image_for_hazards(
    image_bytes: bytes,
    mime_type: str,
    applicable_hazards: list[dict],
    physical_profile: dict | None = None,
) -> dict:
    """
    Send an image to the VLM and return a validated hazards dict:
    {"hazards": [ {label, severity, description, recommendation,
    bounding_box}, ... ]}

    `applicable_hazards` must already be filtered for this person — see
    core/personalization.py. This function does not filter; it only
    grounds the prompt in what's passed to it.

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
                _build_system_prompt(applicable_hazards, physical_profile),
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
