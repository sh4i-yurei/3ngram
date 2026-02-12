---
id: TPL-PRJ-ADR
title: Architecture decision record template
version: 0.1.2
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-021]
tags: [template, adr, decision, architecture]
---

# Purpose

Provide a structured ADR template to capture architectural decisions and
their rationale with traceability to System Design artifacts.

# Scope

Use one ADR per significant architectural decision for Tier 2 and Tier 3
changes.

# Standard

## Architecture decision record template

Use one file per significant decision. Keep entries short and link to
the System Design, options analysis, and related specs.

## Metadata

- Title: <decision title>
- Status: proposed | accepted | rejected | superseded
- Date: <YYYY-MM-DD>
- Related issue or spec: <link>

## Context

What problem are you solving? What constraints apply? Keep this to a few
sentences.

## Decision drivers and evaluation criteria

List the decision rubric or criteria that govern the choice. Link to the
architecture options analysis if it exists.

## Options considered

- <option 1 - summary>
- <option 2 - summary>
- <option 3 - summary>

## Decision

State the chosen option and why it wins given the constraints.

## Consequences

- Positive: <benefits>
- Negative: <costs or risks>
- Follow-up: <tasks, mitigations, or ADRs to create>

## Notes and links

- System Design: <link>
- Options analysis: <link>
- Linked ADRs: <list or \"none\">
- References: <docs, standards, diagrams>

# Implementation Notes

- Keep ADRs short; defer detailed analysis to linked artifacts.
- Update status when superseded or rejected.

# Continuous Improvement and Compliance Metrics

- Track ADR lead time and rework frequency.

# Compliance

Architectural decisions without ADRs are non-compliant.

# Changelog

- 0.1.2 - Set owner/reviewer/approver values.
- 0.1.1 - Added owner/reviewer/approver frontmatter fields.

- 0.1.0 - Initial draft.
