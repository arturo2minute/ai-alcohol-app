## Application Data Format

The assignment does not specify the format of the submitted application data. For the prototype, application data is represented as manually entered structured fields in the UI.

The app may optionally support JSON input to preload or batch-submit those fields, but JSON is treated as a prototype convenience rather than an assumed Treasury/COLA format.

In a production integration, these expected values would likely come from COLA or an internal application API.

For the planned batch-upload workflow, the JSON manifest is intentionally simple and mirrors the current manual form fields:

- `manifestVersion`
- `entries[]`
- `entries[].file`
- `entries[].fields.brandName`
- `entries[].fields.classType`
- `entries[].fields.alcoholContent`
- `entries[].fields.netContents`

Optional identifiers may also be included for user-facing status and support workflows:

- `entries[].submissionId`
- `entries[].displayName`

Why this assumption was made:
- The current backend verification contract only needs one image plus the four expected form values.
- A simpler manifest is easier for non-technical users to understand and easier to validate safely.
- This keeps the prototype close to the current app behavior while still emulating the idea of upstream submission metadata.

Tradeoff:
- This manifest format is not a real COLA payload and should not be treated as one.
- Future integration may require a translation layer from external data into the app's simpler verification fields.

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
