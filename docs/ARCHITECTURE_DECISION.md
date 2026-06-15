Synthetic AI-generated labels are stored under:

`test-assets/labels/`

The test-validation manifest file is stored at:

`test-assets/labels/manifest.json`

The test-validation manifest is the source of truth for automated label fixture validation.

- `expectedFields` represents the fake application/COLA submission data.
- `labelGroundTruth` represents what is intentionally printed on the synthetic label.
- `scenarioCategory` classifies the fixture intent:
  `baseline`, `negative_case`, or `ocr_stress`.
- `ocrMustFind` represents text the OCR should ideally extract.
- `acceptableOverallResults` identifies the allowed overall verification result states:
  `pass`, `fail`, or `review_required`.
- `expectedMismatchFields` identifies fields that should fail validation when the verifier can confidently detect them.

This test manifest is not the same thing as the planned end-user batch manifest.

For batch-upload UX, the prototype will use a simpler manifest format that mirrors the manual submission form instead of the richer test-fixture schema. A sample batch manifest is stored at:

`test-assets/labels/baseline/manifest.json`

That sample batch manifest uses:

- `manifestVersion`
- `entries[]`
- `entries[].file`
- `entries[].fields`
- optional `entries[].submissionId`
- optional `entries[].displayName`

Batch `file` values are expected to be exact relative paths from the folder selected by the user. Forward slashes should be used in manifest paths for consistency across environments.

## Extraction Strategy

The app uses a two-stage extraction pipeline.

The primary extraction path uses OCR because it is fast, inexpensive, and appropriate for reading printed label text.

If OCR produces missing fields, mismatches, or low-confidence results, the app can retry extraction using an AI-powered vision extractor. The AI fallback is used only to identify candidate field values from difficult images.

Final verification is not delegated to the AI model. The backend applies deterministic comparison rules to the extracted values so the results remain explainable and auditable.

This design balances speed, cost, usability, and compliance review needs.
