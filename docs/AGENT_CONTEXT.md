# Agent Context

You are helping build a take-home coding assessment for the U.S. Treasury IT Specialist (AI) role.

The project is an AI-powered alcohol label verification prototype.

Read these files before making changes:
1. README.md
2. docs/TREASURY_REQUIREMENTS.md
3. docs/MVP_SCOPE.md
4. docs/ACCEPTANCE_CRITERIA.md
5. docs/ARCHITECTURE_DECISION.md

## Operating Rules
- Prioritize a working prototype over ambitious incomplete features.
- Keep the UI simple, obvious, and usable by non-technical compliance agents.
- Do not overbuild authentication, databases, or enterprise integrations.
- Do not integrate with COLA.
- Avoid storing uploaded files permanently unless clearly documented.
- Keep code organized and easy to review.
- Add comments only where they clarify non-obvious logic.
- Maintain a clean README with setup, run, test, and deployment instructions.

## Product Priorities
1. Correct field verification.
2. Simple UX.
3. Fast response time.
4. Clear mismatch reporting.
5. Batch upload support if feasible.
6. Honest limitations and assumptions.

## Before Coding
Produce a short implementation plan and identify the files you intend to create or modify.

## After Coding
Run the app locally if possible.
Run tests if available.
Update README and assumptions/tradeoffs.

## Current Implementation Status
- Frontend runs locally with Vite on `127.0.0.1:5173`.
- Backend runs locally with FastAPI on `127.0.0.1:3001`.
- VS Code debugging is configured in `.vscode/launch.json` for the backend.
- `backend/app/main.py` is the FastAPI entry point and should stay thin.
- Placeholder verification logic lives in `backend/app/verifier.py`.
- OCR is not implemented yet.
