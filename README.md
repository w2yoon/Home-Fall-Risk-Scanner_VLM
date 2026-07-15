# SEVA Home Fall-Risk Scanner

A web demo that analyzes a photo of an elderly person's room using a vision-language model, flags potential fall hazards grounded in the CDC STEADI home safety checklist, and returns an annotated photo plus a prioritized list of hazards with plain-language explanations and
recommended fixes.

**Disclaimer:** This tool provides general safety observations and is not a substitute for a professional in-home safety assessment or medical advice.

## Setup

1. Clone this repository and `cd` into it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set your API key:
   ```bash
   cp .env.example .env
   # then edit .env and set GEMINI_API_KEY=<your key>
   ```
   Get a free Gemini API key at https://aistudio.google.com/apikey.
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Project structure

- `app.py` — Streamlit UI and application flow
- `vlm_client.py` — VLM API call and defensive JSON parsing (swappable backend)
- `steadi_checklist.py` — hardcoded CDC STEADI reference checklist
- `image_annotator.py` — Pillow-based bounding box drawing

