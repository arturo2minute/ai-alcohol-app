## Application Data Format

The assignment does not specify the format of the submitted application data. For the prototype, application data is represented as manually entered structured fields in the UI.

The app may optionally support JSON input to preload those fields, but JSON is treated as a prototype convenience rather than an assumed Treasury/COLA format.

In a production integration, these expected values would likely come from COLA or an internal application API.

## Government Warning Matching

For this prototype, the full government warning statement is treated as an exact string match, including case.
The warning text is also treated as a fixed standard value in the product rather than a user-entered field.

Why this assumption was made:
- The project requirements say the government warning must be checked more strictly than general fields.
- The stakeholder notes explicitly require the `GOVERNMENT WARNING:` prefix to be uppercase.
- The warning statement itself is a standard required block of text rather than a case-by-case freeform value.
- To avoid false passes in a compliance-oriented workflow, the prototype uses the stricter rule for the entire warning statement, not just the prefix.

Tradeoff:
- This may produce `Needs Review` or `Mismatch` results for OCR output that is textually correct but differs in letter case from the expected warning body.
