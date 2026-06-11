# Treasury Requirements Summary

## Core Problem
Build a working prototype that helps compliance agents verify alcohol label information against submitted application fields.

## Core User
TTB compliance agents reviewing alcohol label applications.

## Primary Use Case
Agent uploads one or more label images and enters or uploads expected application data. The app extracts or identifies label fields and compares them against expected values.

## Must-Have Features
- Upload alcohol label image.
- Enter expected application fields.
- Extract/check:
  - Brand name
  - Class/type
  - Alcohol content
  - Net contents
  - Government warning
- Show pass/fail/mismatch results clearly.
- Keep UI simple and obvious.
- Return results quickly, target approximately 5 seconds per label where possible.
- Support batch upload if feasible within time.

## Important Stakeholder Constraints
- Standalone proof of concept; no COLA integration.
- Avoid unnecessary sensitive-data storage.
- Cloud APIs may be a risk because government networks can block outbound ML endpoints.
- Warning statement must be checked strictly.
- Brand-name comparison should allow reasonable normalization, such as capitalization differences.

## Deliverables
- Source code repository.
- README with setup/run instructions.
- Brief documentation of approach, tools, assumptions.
- Deployed working prototype URL.