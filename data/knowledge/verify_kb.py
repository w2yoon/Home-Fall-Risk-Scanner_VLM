"""
Part 1 verification gate for data/knowledge/hazards.json.

Run this before starting Part 2. Exits non-zero if any gate check fails,
per the build instruction's "Verification gate — do not proceed to Part 2
until all pass."
"""

import json
import sys
from pathlib import Path

KB_PATH = Path(__file__).parent / "hazards.json"
README_PATH = Path(__file__).parent.parent.parent / "README.md"

REQUIRED_ROOMS = {"bedroom", "bathroom", "kitchen", "living_room"}
BANNED_AUTHORITIES = {"who", "aarp", "who (who)", "aarp homefit"}
BANNED_TEXT_MARKERS = ["who.int", "aarp.org/homefit", "aarp homefit guide"]
OGL_ATTRIBUTION_LINE = (
    "Contains public sector information licensed under the "
    "Open Government Licence v3.0."
)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")


def main() -> int:
    data = json.loads(KB_PATH.read_text())
    hazards = data["hazards"]

    ok = True

    # 1. Every item verified_against_source: true, with a real section reference
    unverified = [
        h["id"] for h in hazards
        if not h.get("source", {}).get("verified_against_source")
    ]
    if unverified:
        fail(f"{len(unverified)} item(s) not verified_against_source: {unverified}")
        ok = False
    else:
        print(f"OK: all {len(hazards)} items have verified_against_source: true")

    # section reference required unless SEVA internal (which has no external section)
    missing_section = [
        h["id"] for h in hazards
        if h["source"]["authority"] != "SEVA internal" and not h["source"].get("section")
    ]
    if missing_section:
        fail(f"{len(missing_section)} non-internal item(s) missing a section reference: {missing_section}")
        ok = False

    # 2. Zero WHO- or AARP-derived content anywhere
    raw_text = KB_PATH.read_text().lower()
    banned_hits = [marker for marker in BANNED_TEXT_MARKERS if marker in raw_text]
    authorities = {h["source"]["authority"].lower() for h in hazards}
    banned_authorities_found = authorities & BANNED_AUTHORITIES
    if banned_hits or banned_authorities_found:
        fail(f"WHO/AARP content found: text markers={banned_hits}, authorities={banned_authorities_found}")
        ok = False
    else:
        print("OK: zero WHO/AARP content detected")

    # 3. Count of SEVA internal items, with justification
    internal = [h for h in hazards if h["source"]["authority"] == "SEVA internal"]
    print(f"INFO: {len(internal)} SEVA internal item(s) of {len(hazards)} total "
          f"({100 * len(internal) / len(hazards):.0f}%):")
    for h in internal:
        note = h["detail"]["source_note"]
        justification = note.split(".")[0] + "."
        print(f"  - {h['id']}: {justification}")
        if not note.startswith("SEVA guidance"):
            fail(f"{h['id']} is SEVA internal but source_note doesn't use the required "
                 f"'SEVA guidance — general safety practice...' framing (rule 4.2)")
            ok = False

    # 4. If any ogl_v3 item exists, the attribution line must be present in the app
    ogl_items = [h for h in hazards if h["source"]["license"] == "ogl_v3"]
    if ogl_items:
        print(f"INFO: {len(ogl_items)} OGL v3 item(s) present: {[h['id'] for h in ogl_items]}")
        readme_text = README_PATH.read_text() if README_PATH.exists() else ""
        if OGL_ATTRIBUTION_LINE not in readme_text:
            fail(f"OGL content present but attribution line not found in {README_PATH}")
            ok = False
        else:
            print("OK: OGL attribution line present in README.md")
    else:
        print("INFO: no OGL v3 items present — attribution line not required")

    # 5. Coverage exists for all four rooms
    covered_rooms = set()
    for h in hazards:
        covered_rooms.update(h["rooms"])
    missing_rooms = REQUIRED_ROOMS - covered_rooms
    if missing_rooms:
        fail(f"Missing coverage for room(s): {missing_rooms}")
        ok = False
    else:
        print(f"OK: all required rooms covered ({sorted(REQUIRED_ROOMS)}); "
              f"also covers: {sorted(covered_rooms - REQUIRED_ROOMS)}")

    # 6. Schema sanity: license values, effort values, image_treatment values
    valid_licenses = {"public_domain", "ogl_v3", None}
    valid_efforts = {"immediate", "purchase", "professional"}
    valid_treatments = {"none", "remove", "composite", "illustration"}
    for h in hazards:
        lic = h["source"]["license"]
        if h["source"]["authority"] != "SEVA internal" and lic not in valid_licenses:
            fail(f"{h['id']}: invalid license {lic!r}")
            ok = False
        if h["action"]["effort"] not in valid_efforts:
            fail(f"{h['id']}: invalid effort {h['action']['effort']!r}")
            ok = False
        if h["action"]["image_treatment"] not in valid_treatments:
            fail(f"{h['id']}: invalid image_treatment {h['action']['image_treatment']!r}")
            ok = False

    print()
    if ok:
        print("PART 1 GATE: PASS")
        return 0
    else:
        print("PART 1 GATE: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
