# Acceptance Criteria

Tester-facing checklist for deciding whether the prototype is working as intended.

## Setup And Run

- A tester can follow the README and start the backend locally.
- A tester can follow the README and start the frontend locally.
- The frontend can reach the backend health endpoint during local testing.

## Single-Label Verification

- A user can upload one label image.
- A user can enter the expected values required by the UI.
- Submitting the form returns a per-field verification result.
- Each result row shows the field, expected value, detected value, status, and notes.
- The app distinguishes among `Match`, `Mismatch`, and `Needs Review`.
- The government warning is evaluated more strictly than the other fields.

## Batch Verification

- A user can enable batch mode.
- A user can select one image folder and one manifest JSON file.
- The app validates the manifest before running requests.
- Missing files referenced by the manifest are reported clearly.
- Request failures are reported clearly.
- Verified items and error items can be reviewed one at a time.

## UX

- Result states are readable without technical knowledge.
- Error messages use plain language.
- Loading state is visible while verification is running.
- A reviewer can tell which items passed, failed, or need follow-up.

## Engineering

- The app runs without requiring committed secrets.
- Uploaded files are not stored permanently by default.
- Documentation explains setup, scope, assumptions, and architecture.
- The repo includes sample assets that let a tester exercise both single and batch flows.

## Test Assets

- The automated fixture manifest at `test-assets/labels/manifest.json` is present for backend-oriented validation.
- The sample batch manifest at `test-assets/labels/baseline/manifest.json` is present for tester-facing batch flow validation.
