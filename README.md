# AI Alcohol App

OCR-based prototype for verifying alcohol label text against expected submission values.

Current implementation:

- Frontend: Vite + vanilla JavaScript
- Backend: FastAPI + Python
- Extraction: local OCR with `rapidocr-onnxruntime`
- Verification: deterministic backend rules
- Batch mode: sequential review from a selected image folder plus manifest JSON

## Tester Docs

Use these docs for the project assumptions, scope, and architecture:

- [Treasury requirements summary](docs/TREASURY_REQUIREMENTS.md)
- [MVP scope](docs/MVP_SCOPE.md)
- [Architecture decision](docs/ARCHITECTURE_DECISION.md)
- [Assumptions and tradeoffs](docs/ASSUMPTIONS_AND_TRADEOFFS.md)
- [Acceptance criteria](docs/ACCEPTANCE_CRITERIA.md)

## Prerequisites

Tested locally with:

- Python `3.13.14`
- Node `v24.14.1`
- npm `11.11.0`

You will also need:

- PowerShell on Windows
- Internet access during setup to install Python and npm dependencies

## Setup From Scratch

From the repo root:

### 1. Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Frontend setup

Open a second terminal from the repo root:

```powershell
cd frontend
npm install
```

## Run Locally

### 1. Start the backend

From `backend/` with the virtual environment activated:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 3001
```

The backend health endpoint is:

`http://127.0.0.1:3001/health`

### 2. Start the frontend

From `frontend/`:

```powershell
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

`http://127.0.0.1:5173`

## Environment Notes

The app runs locally without cloud APIs.

Optional environment variables:

- Backend: `FRONTEND_ORIGIN`
  Default: `http://localhost:5173,http://127.0.0.1:5173`
- Frontend: `VITE_API_BASE_URL`
  Default: `http://localhost:3001`

If you change the frontend or backend host/port, update these values to match.



## How To Test

### Single label flow

Note: You can find test files and their expected fields in test-assets\labels

1. Start backend and frontend.
2. Open the app in the browser.
3. Leave `Batch Upload` turned off.
4. Upload one label image.
5. Enter expected values for:
   - Brand Name
   - Class/Type
   - Alcohol Content
   - Net Contents
6. Submit the form and review the results table.

### Batch flow

1. Turn on `Batch Upload`.
2. Select an image folder.
3. Select one manifest JSON file.
4. Run verification.
5. Review results one label at a time with the Previous/Next controls.

Sample batch assets live here:

- Images: [`test-assets/labels/baseline/`](test-assets/labels/baseline/)
- Sample user batch manifest: [`test-assets/labels/baseline/manifest.json`](test-assets/labels/baseline/manifest.json)

## Batch Manifest Format

The end-user batch manifest is intentionally simple:

```json
{
  "manifestVersion": 1,
  "entries": [
    {
      "submissionId": "BASELINE-001",
      "displayName": "Valid Bourbon Label",
      "file": "bourbon-valid-01.png",
      "fields": {
        "brandName": "OLD TOM DISTILLERY",
        "classType": "Kentucky Straight Bourbon Whiskey",
        "alcoholContent": "45% Alc./Vol. (90 Proof)",
        "netContents": "750 mL"
      }
    }
  ]
}
```

Rules:

- `manifestVersion` must be `1`
- `entries` must be a non-empty array
- Each entry must include:
  - `file`
  - `fields.brandName`
  - `fields.classType`
  - `fields.alcoholContent`
  - `fields.netContents`
- `submissionId` and `displayName` are optional
- Manifest `file` values must be exact relative paths from the selected folder root
- Use forward slashes in manifest paths

Example:

- If you select `test-assets/labels/baseline`, the manifest should reference `bourbon-valid-01.png`
- If you select `test-assets/labels`, the manifest should reference `baseline/bourbon-valid-01.png`

## Tests

After backend dependencies are installed:

```powershell
cd backend
.\.venv\Scripts\python -m unittest discover -s tests -v
```

Test assets and the richer fixture manifest used by automated tests live under:

- [`test-assets/labels/`](test-assets/labels/)
- [`test-assets/labels/manifest.json`](test-assets/labels/manifest.json)

## Current Behavior

- Brand name and class/type use normalized comparisons with a `Needs Review` path for close OCR matches
- Alcohol content and net contents use OCR-oriented normalization
- Government warning uses stricter matching than the other fields
- The full government warning is treated as a fixed required value in the product
- Results are reported as `Match`, `Mismatch`, or `Needs Review`
- Batch requests are processed sequentially in the frontend
