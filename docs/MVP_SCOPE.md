# MVP Scope

This document defines what the current prototype is intended to do. It describes committed product behavior, not the background requirements or the implementation rationale.

## In Scope

- Single-label verification from one uploaded image
- Manual entry of expected values for:
  - brand name
  - class or type
  - alcohol content
  - net contents
- OCR-based text extraction
- Deterministic field comparison in the backend
- Per-field results with:
  - expected value
  - detected value
  - status
  - notes
- Result states:
  - `Match`
  - `Mismatch`
  - `Needs Review`
- Batch mode that accepts:
  - one selected image folder
  - one manifest JSON file
- Sequential batch review with navigation between result items
- Plain-language error handling for bad manifests, missing files, and request failures

## Verification Rules In Scope

- General fields are normalized before comparison where reasonable.
- Brand and class or type may return `Needs Review` for close OCR matches.
- Alcohol content and net contents use OCR-oriented normalization.
- Government warning is treated more strictly than other fields.
- The government warning is treated as a fixed required value in the product.

## Explicitly Out Of Scope

- COLA integration
- User authentication
- Database or long-term persistence
- Permanent file storage
- Full federal compliance coverage beyond the chosen prototype fields
- Advanced image correction for glare, skew, or poor photography
- Model training or tuning
- Backend-native parallel or asynchronous batch processing

## Deferred Candidates

- AI vision fallback for hard OCR cases
- Upstream ingestion from a real submission system
- Dedicated backend batch API
- Deployment hardening for production use

## Success Standard

The MVP is successful if a reviewer can run the app, verify a label, understand the outcome, and see honest limits when the OCR or comparison logic is uncertain.
