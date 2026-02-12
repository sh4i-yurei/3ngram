---
id: TPL-PRJ-TESTING
title: Testing template
version: 0.2.2
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-008]
tags: [template, testing, quality]
---

# Purpose

Document how this project validates behavior.

# Scope

Use for project-specific testing expectations aligned to
[Testing_and_Quality_Standard](../../../03_Engineering_Standards/Testing_and_Quality_Standard.md).

# Standard

## Testing strategy template

Align with [Testing_and_Quality_Standard](../../../03_Engineering_Standards/Testing_and_Quality_Standard.md) and project requirements.

## Test strategy

- Levels: unit, integration, end-to-end, contract
- Tooling/frameworks: <list>
- Coverage expectations: <targets or rationale>

## Test execution

- Local commands: <commands>
- CI commands and required gates: <list>
- Data/fixtures: <location and setup>

## Validation evidence

What evidence is required before merge/release (reports, screenshots,
logs). Handling of flaky or quarantined tests.

## Responsibilities

Who owns maintaining tests and triaging failures.

## Definition of done

- Tests defined for each spec behavior and edge case.
- CI passing with required coverage.
- New failures triaged and tracked.

## Links

- Specs and designs: <links>
- Runbooks for test infrastructure: <links>

# Implementation Notes

- Validate test commands locally before release.

# Continuous Improvement and Compliance Metrics

- Track flaky test rates and coverage drift.

# Compliance

Projects without documented testing strategy are non-compliant.

# Changelog

- 0.2.2 - Set owner/reviewer/approver values.
- 0.2.1 - Added owner/reviewer/approver frontmatter fields.

- 0.2.0 - Added responsibilities and evidence expectations.
- 0.1.0 - Initial draft.
