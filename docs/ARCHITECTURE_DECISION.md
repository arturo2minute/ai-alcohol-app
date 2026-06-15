# Architecture Decision

This document explains how the prototype is built and why the main technical boundaries were chosen.

## System Shape

- `frontend/` contains the browser UI built with Vite and vanilla JavaScript.
- `backend/` contains the FastAPI service.
- `backend/app/ocr.py` handles OCR extraction.
- `backend/app/verifier.py` handles field extraction and deterministic comparison rules.
- `backend/app/main.py` exposes the API endpoints and keeps request wiring thin.

## Request Flow

### Single Label

1. The browser submits one image and the expected field values to `POST /verify`.
2. The backend runs OCR on the image.
3. The backend extracts candidate field values from OCR output.
4. The backend applies deterministic comparison rules.
5. The backend returns per-field results and a summary.

### Batch Review

1. The browser reads the selected manifest file.
2. The browser matches manifest paths against the selected image folder.
3. The browser sends one `/verify` request per matched entry.
4. The browser keeps the review state, including missing-file and request-error items.

## Major Decisions

### Split Frontend And Backend

Decision:
Use a separate browser client and API service.

Reason:
This keeps UI concerns, OCR work, and verification logic separated and easy to inspect.

### Local OCR In The Backend

Decision:
Run OCR locally inside the backend process using `rapidocr-onnxruntime`.

Reason:
Local OCR avoids dependence on external model services and keeps extraction close to the verification pipeline.

### Deterministic Verification

Decision:
Make the backend comparison rules the source of truth for `Match`, `Mismatch`, and `Needs Review`.

Reason:
The verification outcome needs to stay explainable and auditable even when OCR is noisy.

### Frontend-Orchestrated Batch Processing

Decision:
Keep batch orchestration in the frontend and reuse the single-label backend endpoint.

Reason:
This reduces backend surface area and keeps the prototype implementation smaller.

## Data Artifacts

- End-user batch manifest example:
  `test-assets/labels/baseline/manifest.json`
- Automated test fixture manifest:
  `test-assets/labels/manifest.json`

These files serve different purposes and should not be treated as interchangeable.
