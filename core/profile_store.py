"""JSON-per-elder profile storage.

Self-contained for this repo — mirrors the JSON-per-elder pattern used in
the sibling SEVA_Care project's core/storage.py, but is its own
independent copy so this app keeps deploying standalone (no cross-repo
dependency). No caching, no ORM: this is a demo-scale store.

Profiles contain physical_profile data (mobility, hand_function, etc.)
which is personal/health-adjacent — data/elders/ is gitignored so no real
profile ever gets committed to the public repo.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

ELDERS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "elders")

DEFAULT_PHYSICAL_PROFILE = {
    "height_cm": 0,
    "weight_kg": 0,
    # Record-only. Deliberately NOT a personalization driver — see build
    # spec 2.1: "Do not add sex/gender as a personalization driver. It
    # has little bearing on which hazards apply, and inventing
    # differentiation on that basis would be exactly the kind of
    # unfounded specificity this project has already had to correct
    # once." core/personalization.py must never read this field.
    "sex": "",
    "mobility": "ambulatory",
    "hand_function": "both",
    "bed_type": "standard",
    "vision": "typical",
    "notes": "",
}


def _profile_path(elder_id: str) -> str:
    return os.path.join(ELDERS_DIR, f"{elder_id}.json")


def _default_profile(elder_id: str) -> dict:
    return {
        "elder_id": elder_id,
        "physical_profile": dict(DEFAULT_PHYSICAL_PROFILE),
        "home_safety_scan": {
            "history": [],
            "stale": False,
            "profile_snapshot_hash": None,
        },
    }


def load_profile(elder_id: str) -> dict:
    path = _profile_path(elder_id)
    if not os.path.exists(path):
        return _default_profile(elder_id)
    with open(path, "r") as f:
        profile = json.load(f)
    # Backfill any fields added to the schema after this profile was created.
    for key, value in DEFAULT_PHYSICAL_PROFILE.items():
        profile.setdefault("physical_profile", {}).setdefault(key, value)
    profile.setdefault("home_safety_scan", {"history": [], "stale": False, "profile_snapshot_hash": None})
    return profile


def save_profile(elder_id: str, profile: dict) -> None:
    os.makedirs(ELDERS_DIR, exist_ok=True)
    path = _profile_path(elder_id)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(profile, f, indent=2)
    os.replace(tmp, path)


def list_elder_ids() -> list[str]:
    if not os.path.isdir(ELDERS_DIR):
        return []
    return sorted(fn[:-5] for fn in os.listdir(ELDERS_DIR) if fn.endswith(".json"))


def profile_snapshot_hash(physical_profile: dict) -> str:
    """A stable hash of the physical_profile, used to detect changes
    that should mark prior home_safety_scan results as stale (spec 2.4).
    """
    canonical = json.dumps(physical_profile, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def record_scan(elder_id: str, profile: dict, hazards: list[dict]) -> dict:
    """Append a scan result to home_safety_scan.history, clear staleness,
    and persist. Returns the updated profile.
    """
    snapshot_hash = profile_snapshot_hash(profile["physical_profile"])
    entry = {
        "scan_id": f"{elder_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "profile_snapshot": dict(profile["physical_profile"]),
        "hazards": hazards,
    }
    profile["home_safety_scan"]["history"].append(entry)
    profile["home_safety_scan"]["stale"] = False
    profile["home_safety_scan"]["profile_snapshot_hash"] = snapshot_hash
    save_profile(elder_id, profile)
    return profile


def refresh_staleness(profile: dict) -> dict:
    """Call after any physical_profile edit: if it no longer matches the
    hash recorded at the last scan, mark home_safety_scan.stale = True
    so the caregiver view can prompt a rescan (spec 2.4).
    """
    scan = profile["home_safety_scan"]
    if not scan["history"]:
        scan["stale"] = False
        return profile
    current_hash = profile_snapshot_hash(profile["physical_profile"])
    scan["stale"] = current_hash != scan["profile_snapshot_hash"]
    return profile
