# Treasury Requirements

This document captures the problem the prototype is meant to solve and the external constraints it should respect

## Problem Statement

Build a prototype that helps TTB compliance agents verify alcohol label artwork against submitted application values.

## Primary User

TTB compliance agents reviewing label submissions.

## Core Workflow

1. The reviewer provides a label image.
2. The reviewer provides the expected submission values.
3. The app extracts or identifies relevant label text.
4. The app compares detected values against expected values.
5. The app presents clear results for review.

## Required Verification Areas

- Brand name
- Class or type
- Alcohol content
- Net contents
- Government warning

## Product Expectations

- The interface should be simple enough for non-technical reviewers.
- Results should be returned quickly enough to be practical in a review workflow.
- Mismatches and uncertain cases should be obvious.
- Batch processing is valuable if feasible within prototype scope.

## Constraints

- Treat this as a standalone proof of concept.
- Do not integrate with COLA for this build.
- Avoid unnecessary storage of uploaded files or sensitive data.
- Expect restricted network environments where outbound ML endpoints may be blocked.
- Apply stricter handling to the government warning than to general fields.
- Allow reasonable normalization for fields like brand name when differences are cosmetic.

## Deliverables

- Source repository
- Runnable application
- README with setup and run instructions
- Documentation for scope, assumptions, and architecture
- Public deployment URL if deployment is completed
