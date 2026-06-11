# MVP Scope

## Build First
A simple web app that allows a user to:
1. Upload one or more alcohol label images.
2. Enter expected application values manually.
3. Run label verification.
4. View a clear result table:
   - Field
   - Expected value
   - Detected value
   - Status: Match / Mismatch / Needs Review
   - Notes

## Verification Logic
### Primary Path
- Use OCR to detect text from the label.
- Normalize general fields for comparison:
  - Case-insensitive brand match
  - Ignore extra whitespace
  - Normalize punctuation where reasonable
- Use stricter matching for government warning:
  - Required text must be present.
  - “GOVERNMENT WARNING:” must be uppercase.
  - Flag warning as mismatch if wording is incomplete or materially changed.
### AI Fallback Path
- Trigger AI-powered extraction when:
  - OCR misses required fields
  - OCR confidence is low
  - OCR result produces mismatches
  - government warning is incomplete or unclear
### Verification Rule
- AI does not make the compliance decision. AI only extracts candidate values. The backend comparison service determines Match, Mismatch, or Needs Review.

## Batch Upload
- Support multiple images if practical.
- If full async batch processing is too much, process files sequentially and show per-file results.

## Defer
- No COLA integration.
- No user authentication unless deployment requires it.
- No database unless needed.
- No long-term file storage.
- No complex federal compliance implementation.
- No perfect image correction for glare/skew.
- No advanced model training.

## Success Definition
Working, deployed, understandable prototype with clean code and honest documentation.