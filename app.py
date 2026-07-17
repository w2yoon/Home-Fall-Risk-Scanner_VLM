"""Streamlit entry point for the SEVA Home Fall-Risk Scanner MVP."""

import io
import json

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError

from core import profile_store
from core.personalization import personalize
from image_annotator import annotate_image, is_missing_device
from steadi_checklist import DISCLAIMER_TEXT
from vlm_client import VLMError, analyze_image_for_hazards

load_dotenv()

st.set_page_config(page_title="SEVA Home Fall-Risk Scanner", layout="wide")

SEVERITY_BADGE = {
    "high": "🔴 High",
    "medium": "🟠 Medium",
    "low": "🟡 Low",
}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

MOBILITY_OPTIONS = ["ambulatory", "cane", "walker", "wheelchair"]
HAND_FUNCTION_OPTIONS = ["both", "left_only", "right_only", "limited_grip"]
BED_TYPE_OPTIONS = ["standard", "hospital"]
VISION_OPTIONS = ["typical", "low_vision"]
SEX_OPTIONS = ["", "female", "male", "other", "prefer not to say"]


def _load_hazards_kb() -> list[dict]:
    with open("data/knowledge/hazards.json", "r") as f:
        return json.load(f)["hazards"]


def _profile_editor(elder_id: str, profile: dict) -> dict:
    pp = profile["physical_profile"]
    with st.sidebar:
        st.header("Who is this scan for?")
        st.caption(
            "This changes which hazards get flagged and how they're "
            "framed — the same photo can produce a different report for "
            "a different person."
        )
        pp["mobility"] = st.selectbox(
            "Mobility", MOBILITY_OPTIONS, index=MOBILITY_OPTIONS.index(pp["mobility"])
        )
        pp["hand_function"] = st.selectbox(
            "Hand function", HAND_FUNCTION_OPTIONS,
            index=HAND_FUNCTION_OPTIONS.index(pp["hand_function"]),
        )
        pp["bed_type"] = st.selectbox(
            "Bed type", BED_TYPE_OPTIONS, index=BED_TYPE_OPTIONS.index(pp["bed_type"])
        )
        pp["vision"] = st.selectbox(
            "Vision", VISION_OPTIONS, index=VISION_OPTIONS.index(pp["vision"])
        )
        with st.expander("More details (optional)"):
            pp["height_cm"] = st.number_input(
                "Height (cm)", min_value=0, max_value=250, value=int(pp.get("height_cm", 0))
            )
            pp["weight_kg"] = st.number_input(
                "Weight (kg)", min_value=0, max_value=300, value=int(pp.get("weight_kg", 0))
            )
            pp["sex"] = st.selectbox(
                "Sex (optional, record only — does not affect results)",
                SEX_OPTIONS, index=SEX_OPTIONS.index(pp.get("sex", "")),
            )
            st.caption(
                "Height, weight, and sex are stored with this profile but "
                "are not currently used to change hazard results — only "
                "mobility, hand function, bed type, and vision are."
            )
            pp["notes"] = st.text_area("Notes", value=pp.get("notes", ""))

    profile_store.refresh_staleness(profile)
    profile_store.save_profile(elder_id, profile)
    return profile


def main() -> None:
    st.title("🏠 SEVA Home Fall-Risk Scanner")
    st.warning(f"⚠️ **Disclaimer:** {DISCLAIMER_TEXT}")
    st.caption(
        "Hazard identification is grounded in CDC STEADI, NIA, CPSC, "
        "the ADA Standards for Accessible Design, FDA, and NHS guidance, "
        "personalized to the person being scanned for."
    )

    with st.sidebar:
        elder_id = st.text_input("Elder ID", value=st.session_state.get("elder_id", "default"))
        st.session_state["elder_id"] = elder_id

    profile = profile_store.load_profile(elder_id)
    profile = _profile_editor(elder_id, profile)

    if profile["home_safety_scan"]["stale"]:
        st.info(
            "🔄 This person's profile changed since the last scan. "
            "Rescan to get results that match their current needs."
        )

    uploaded_file = st.file_uploader(
        "Upload a photo of a room to scan for fall hazards",
        type=["png", "jpg", "jpeg", "webp"],
    )

    if uploaded_file is None:
        st.info("Upload a room photo above to get started.")
        return

    image_bytes = uploaded_file.getvalue()
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        image = Image.open(io.BytesIO(image_bytes))  # re-open after verify()
    except (UnidentifiedImageError, OSError):
        st.error("That file doesn't look like a valid image. Please upload a JPG, PNG, or WEBP.")
        return

    if st.button("Scan for hazards", type="primary"):
        with st.spinner("Analyzing photo for fall hazards..."):
            try:
                kb = _load_hazards_kb()
                applicable = personalize(kb, profile["physical_profile"])
                mime_type = uploaded_file.type or "image/jpeg"
                result = analyze_image_for_hazards(
                    image_bytes, mime_type, applicable, profile["physical_profile"]
                )
            except VLMError as exc:
                st.error(f"Couldn't analyze this image: {exc}")
                return

        st.session_state["hazards"] = result["hazards"]
        st.session_state["scanned_image"] = image
        profile = profile_store.record_scan(elder_id, profile, result["hazards"])

    hazards = st.session_state.get("hazards")
    scanned_image = st.session_state.get("scanned_image")

    if hazards is None or scanned_image is None:
        return

    col_image, col_list = st.columns([3, 2])

    with col_image:
        st.subheader("Annotated Photo")
        if hazards:
            annotated = annotate_image(scanned_image, hazards)
            st.image(annotated, use_container_width=True)
            st.caption(
                "🟥🟧🟨 Solid box = hazard visible in photo &nbsp;·&nbsp; "
                "🟦 Dashed blue box = recommended device not currently present"
            )
        else:
            st.image(scanned_image, use_container_width=True)

    with col_list:
        st.subheader("Detected Hazards")
        if not hazards:
            st.success("✅ No major hazards detected in this view.")
        else:
            sorted_hazards = sorted(
                hazards,
                key=lambda h: (
                    is_missing_device(h),
                    SEVERITY_ORDER.get(h["severity"], 3),
                ),
            )
            for hazard in sorted_hazards:
                missing = is_missing_device(hazard)
                type_label = "➕ Recommended addition" if missing else "⚠️ Hazard detected"
                severity_badge = SEVERITY_BADGE.get(hazard["severity"], hazard["severity"])
                risk_label = "Why it's recommended" if missing else "Risk"

                with st.expander(
                    f"{type_label} — {severity_badge} — {hazard['label']}",
                    expanded=True,
                ):
                    st.markdown(f"**{risk_label}:** {hazard['description']}")
                    st.markdown(f"**Recommended fix:** {hazard['recommendation']}")

    st.divider()
    st.caption(
        "Reference: CDC STEADI, NIA, CPSC, ADA Standards for Accessible "
        "Design (2010), FDA, and NHS inform (Scotland, OGL v3). This is "
        "a demo/pilot tool, not a medical device. Contains public sector "
        "information licensed under the Open Government Licence v3.0."
    )


if __name__ == "__main__":
    main()
