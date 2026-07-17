"""Deterministic, code-side personalization of the hazards.json knowledge
base against an elder's physical_profile.

Per build spec 2.2: "Filter the KB by applies_when against the profile in
Python, before the VLM call... The VLM's job is what is visible in this
photo. Applicability is deterministic and belongs in code." This module
is that boundary — nothing here calls the model.

Field semantics (spec 2.3):
  - mobility, bed_type: hard gates. An item with applies_when.mobility
    set only applies to profiles whose mobility is in that list (null =
    everyone). This is how bed_type: "hospital" suppresses the bedside
    mobility-aid item, and how mobility gates the ambulatory-vs-wheelchair
    rug variants.
  - hand_function: not filtered here. Which side a grab bar or handle
    should go on depends on room geometry visible only in the photo, so
    it's passed to the VLM as a directive (see vlm_client.py) rather than
    used to include/exclude KB items.
  - vision: a severity modifier, not a gate. Spec 2.3 says low_vision
    "raises severity on lighting and contrast items" — it does not say
    those items stop applying to everyone else. Items tagged
    applies_when.vision get bumped one severity level when the profile
    matches; they are never excluded on vision grounds.
"""
from __future__ import annotations

SEVERITY_ORDER = ["low", "medium", "high"]


def _gate_matches(constraint, profile_value) -> bool:
    if constraint is None:
        return True
    allowed = constraint if isinstance(constraint, list) else [constraint]
    return profile_value in allowed


def applicable_hazards(hazards: list[dict], physical_profile: dict) -> list[dict]:
    """Return only the KB items that apply to this profile, per the hard
    gates (mobility, bed_type). Order preserved from the source list.
    """
    mobility = physical_profile.get("mobility")
    bed_type = physical_profile.get("bed_type")

    result = []
    for hazard in hazards:
        aw = hazard.get("applies_when", {})
        if not _gate_matches(aw.get("mobility"), mobility):
            continue
        if not _gate_matches(aw.get("bed_type"), bed_type):
            continue
        result.append(hazard)
    return result


def effective_severity(hazard: dict, physical_profile: dict) -> str:
    """The severity to use for this item given the profile: the KB's
    severity_default, bumped one level if this is a vision-sensitive item
    and the profile has low_vision.
    """
    base = hazard.get("severity_default", "low")
    vision_constraint = hazard.get("applies_when", {}).get("vision")
    if vision_constraint and _gate_matches(vision_constraint, physical_profile.get("vision")):
        idx = min(SEVERITY_ORDER.index(base) + 1, len(SEVERITY_ORDER) - 1)
        return SEVERITY_ORDER[idx]
    return base


def personalize(hazards: list[dict], physical_profile: dict) -> list[dict]:
    """Convenience wrapper: filter, then attach each item's effective
    severity for this profile as `effective_severity`.
    """
    applicable = applicable_hazards(hazards, physical_profile)
    personalized = []
    for hazard in applicable:
        item = dict(hazard)
        item["effective_severity"] = effective_severity(hazard, physical_profile)
        personalized.append(item)
    return personalized
