"""
Hardcoded reference content derived from the CDC STEADI
"Check for Safety: A Home Fall Prevention Checklist for Older Adults".

This is embedded as static grounding context that gets injected into the
VLM system prompt (prompt-based grounding, not a retrieval/vector-DB step).
Source: CDC STEADI initiative, https://www.cdc.gov/steadi (paraphrased,
not fetched live).
"""

STEADI_CHECKLIST = [
    {
        "room": "Floors & Walkways",
        "items": [
            {
                "hazard": "Loose rugs or throw rugs",
                "fix": "Remove the rug entirely, or use double-sided tape "
                       "or a non-slip rug pad to secure it flat to the floor.",
            },
            {
                "hazard": "Clutter, boxes, papers, or cords in walking paths",
                "fix": "Clear walkways completely; route cords along walls "
                       "or use cord covers.",
            },
            {
                "hazard": "Uneven, cracked, or damaged flooring/thresholds",
                "fix": "Repair or replace damaged flooring; add a beveled "
                       "threshold ramp for any raised transitions.",
            },
            {
                "hazard": "Furniture placed in a way that narrows walking paths",
                "fix": "Rearrange furniture to keep a clear, wide path "
                       "through frequently used rooms.",
            },
        ],
    },
    {
        "room": "Stairs & Steps",
        "items": [
            {
                "hazard": "Missing handrail on one or both sides of stairs",
                "fix": "Install a sturdy, graspable handrail that runs the "
                       "full length of the stairs on at least one side, "
                       "ideally both.",
            },
            {
                "hazard": "Loose, damaged, or uneven steps",
                "fix": "Repair broken steps and secure any loose stair "
                       "treads or carpeting.",
            },
            {
                "hazard": "Poor lighting on stairways",
                "fix": "Add bright lighting with switches at both the top "
                       "and bottom of the stairs.",
            },
            {
                "hazard": "No contrasting edge marking on steps",
                "fix": "Apply high-contrast, non-slip tape to the edge of "
                       "each step to improve visibility.",
            },
        ],
    },
    {
        "room": "Kitchen",
        "items": [
            {
                "hazard": "Frequently used items stored on high shelves",
                "fix": "Move commonly used dishes, food, and supplies to "
                       "waist- or shoulder-height shelves so a step stool "
                       "isn't needed.",
            },
            {
                "hazard": "Unstable step stool or use of a chair to reach "
                          "high places",
                "fix": "Provide a sturdy step stool with a handrail, or "
                       "better yet, eliminate the need to climb by "
                       "relocating items.",
            },
            {
                "hazard": "Slippery kitchen floor (wax, spills)",
                "fix": "Use non-slip floor wax or mats, and clean spills "
                       "immediately.",
            },
        ],
    },
    {
        "room": "Bedroom",
        "items": [
            {
                "hazard": "No lamp or light switch within reach of the bed",
                "fix": "Place a lamp or install a touch light within easy "
                       "arm's reach of the bed.",
            },
            {
                "hazard": "No clear, unobstructed path from bed to bathroom",
                "fix": "Install nightlights or motion-sensor lighting along "
                       "the path from the bed to the bathroom.",
            },
            {
                "hazard": "Bed height too high or too low",
                "fix": "Adjust bed height so feet rest flat on the floor "
                       "when sitting on the edge.",
            },
            {
                "hazard": "Clutter on the floor near the bed",
                "fix": "Keep the floor around the bed clear of shoes, "
                       "clothing, and other objects.",
            },
        ],
    },
    {
        "room": "Bathroom",
        "items": [
            {
                "hazard": "No grab bars near the toilet",
                "fix": "Install a securely mounted grab bar next to the "
                       "toilet.",
            },
            {
                "hazard": "No grab bars inside or beside the tub/shower",
                "fix": "Install grab bars inside the tub/shower and at the "
                       "entry point, mounted into wall studs or blocking.",
            },
            {
                "hazard": "No non-slip mat or strips in the tub or shower "
                          "floor",
                "fix": "Add a rubber non-slip mat or adhesive non-slip "
                       "strips to the tub/shower floor.",
            },
            {
                "hazard": "Toilet seat too low",
                "fix": "Consider a raised toilet seat or a toilet safety "
                       "frame with armrests.",
            },
            {
                "hazard": "Slippery bathroom floor when wet",
                "fix": "Use a non-slip bath mat outside the tub/shower and "
                       "wipe up water promptly.",
            },
            {
                "hazard": "Poor lighting in the bathroom, especially at "
                          "night",
                "fix": "Add a nightlight or motion-sensor light for "
                       "nighttime bathroom use.",
            },
        ],
    },
]


def checklist_as_prompt_text() -> str:
    """Flatten the STEADI checklist into plain text for prompt injection."""
    lines = []
    for room in STEADI_CHECKLIST:
        lines.append(f"\n{room['room']}:")
        for item in room["items"]:
            lines.append(f"- Hazard: {item['hazard']}")
            lines.append(f"  Recommended fix: {item['fix']}")
    return "\n".join(lines)


DISCLAIMER_TEXT = (
    "This tool provides general safety observations based on CDC STEADI "
    "guidelines and is not a substitute for a professional in-home "
    "assessment or medical advice."
)
