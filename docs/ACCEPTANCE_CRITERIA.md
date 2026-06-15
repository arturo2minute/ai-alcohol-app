# Acceptance Criteria

## Functional
- User can upload at least one label image.
- User can input expected application values.
- If batch mode is enabled, user can select an image folder and one manifest JSON file.
- App detects or extracts relevant text from the label.
- App compares expected values against detected values.
- App displays results clearly.
- App flags mismatches and uncertain results.
- App checks government warning more strictly than regular fields.
- App can handle multiple labels or documents if implemented.

## UX
- Main action is obvious.
- Results are readable without technical knowledge.
- Error messages are understandable.
- Batch manifest errors are described in plain language.
- Loading state is visible.
- User can tell what passed, failed, or needs review.

## Engineering
- App runs from documented setup instructions.
- Code is organized by responsibility.
- No unnecessary permanent storage of uploaded files.
- Secrets are not committed.
- Environment variables are documented.
- README explains approach, tools, assumptions, and limitations.

## Deployment
- App is deployed to a public URL.
- Deployed version can be tested by Treasury reviewers.

## Test Asset Validation
- App can load or reference `test-assets/labels/manifest.json`.
- Sample user-batch manifests can load or reference `test-assets/labels/baseline/manifest.json`.
- Automated tests can iterate through manifest entries.
- OCR output is checked against `ocrMustFind` where practical.
- Verification output is checked against `acceptableOverallResults`.
- Negative-case labels produce mismatches for fields listed in `expectedMismatchFields` when the verifier can confidently identify a failure.
- OCR-stress labels may return `review_required` when OCR quality is insufficient.
