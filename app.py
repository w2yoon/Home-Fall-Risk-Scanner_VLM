"""Streamlit entry point for the SEVA Home Fall-Risk Scanner MVP."""

import io

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError

from image_annotator import annotate_image
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


def main() -> None:
    st.title("🏠 SEVA Home Fall-Risk Scanner")
    st.warning(f"⚠️ **Disclaimer:** {DISCLAIMER_TEXT}")
    st.caption(
        "Hazard identification is grounded in the CDC STEADI "
        "\"Check for Safety\" home fall prevention checklist."
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
                mime_type = uploaded_file.type or "image/jpeg"
                result = analyze_image_for_hazards(image_bytes, mime_type)
            except VLMError as exc:
                st.error(f"Couldn't analyze this image: {exc}")
                return

        st.session_state["hazards"] = result["hazards"]
        st.session_state["scanned_image"] = image

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
        else:
            st.image(scanned_image, use_container_width=True)

    with col_list:
        st.subheader("Detected Hazards")
        if not hazards:
            st.success("✅ No major hazards detected in this view.")
        else:
            sorted_hazards = sorted(
                hazards, key=lambda h: SEVERITY_ORDER.get(h["severity"], 3)
            )
            for hazard in sorted_hazards:
                badge = SEVERITY_BADGE.get(hazard["severity"], hazard["severity"])
                with st.expander(f"{badge} — {hazard['label']}", expanded=True):
                    st.markdown(f"**Risk:** {hazard['description']}")
                    st.markdown(f"**Recommended fix:** {hazard['recommendation']}")

    st.divider()
    st.caption(
        "Reference: CDC STEADI (Stopping Elderly Accidents, Deaths & "
        "Injuries) Initiative — 'Check for Safety: A Home Fall Prevention "
        "Checklist for Older Adults'. This is a demo/pilot tool, not a "
        "medical device."
    )


if __name__ == "__main__":
    main()
