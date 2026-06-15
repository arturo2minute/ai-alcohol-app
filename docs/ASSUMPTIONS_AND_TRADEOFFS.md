# Assumptions And Tradeoffs

This document records product assumptions that fill gaps in the prompt

## Application Data Input

Assumption:
Expected submission data is entered manually for single-label review and provided by a simple JSON manifest for batch review.

Why:
The prompt requires verification against submitted values but does not define a real upstream system contract.

Tradeoff:
The current manifest format is a prototype input, not a Treasury or COLA payload. A real integration would likely need a translation layer.

## Batch Manifest Shape

Assumption:
The batch manifest mirrors the current manual form fields and requires only the fields the backend verifies today.

Why:
Keeping the manifest close to the UI reduces validation complexity and makes it easier for testers to understand.

Tradeoff:
The manifest is intentionally narrow and does not model richer submission metadata that a production workflow would probably need.

## Government Warning Policy

Assumption:
The government warning is treated as a fixed required text block and is checked more strictly than the other fields.

Why:
Stakeholder notes and project requirements both call for stricter handling of the warning statement.

Tradeoff:
OCR output that is nearly correct but not exact can still produce `Mismatch` or `Needs Review`.

## Network Environment

Assumption:
The prototype should remain usable in environments where outbound ML calls may be unreliable or blocked.

Why:
The stakeholder context explicitly warns that network restrictions may block external model endpoints.

Tradeoff:
Local OCR keeps the app easier to run in restricted environments, but it limits recovery options for difficult images.

## Batch Processing Model

Assumption:
Sequential batch processing is acceptable for the prototype.

Why:
It keeps the implementation low-risk and reuses the single-label verification path.

Tradeoff:
Large batches will take longer than a parallelized or backend-managed design.

## Test Fixture Separation

Assumption:
The richer fixture manifest used for automated validation is separate from the simpler manifest used in the batch-upload UI.

Why:
Automated tests need more metadata than an end user should have to provide.

Tradeoff:
There are two manifest formats in the repo, so the documentation must make the distinction explicit.
