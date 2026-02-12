---
id: TPL-PRJ-LW-DESIGN
title: Lightweight design template
version: 0.1.3
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-032]
tags: [template, design, lightweight]
---
# Purpose

Provide a Tier 2 lightweight design template that captures essential
intent without full system or module design artifacts.

# Scope

Use for Tier 2 changes as defined in [SDLC_With_AI](../../../05_Dev_Workflows/SDLC_With_AI.md).

# Standard

## Problem statement

Describe the problem, scope, and why it matters now.

## Approach summary

Summarize the proposed approach and key constraints.

## Interfaces and data impacts

List interfaces, data structures, or schema changes affected.

## Testing plan

Define test cases and validation needed before release.

## Success metrics and instrumentation

List metrics that confirm success and any telemetry additions required.

## Progressive delivery and rollback

Describe feature flags, rollout phases, and rollback triggers.

## Rollback plan

Describe rollback steps and risks.

## Failure scenarios and mitigations

Summarize critical failure modes and how the system degrades safely.

## Risks and mitigations

List top risks and planned mitigations.

## Links

- Issue or request: <link>
- Relevant standards: <links>
- Related specs or ADRs: <links>

# Implementation Notes

- Keep the design concise and avoid implementation details.
- Link to this design from the related issue or PR.

# Continuous Improvement and Compliance Metrics

- Track rework caused by incomplete Tier 2 designs.

# Compliance

Tier 2 changes without an approved lightweight design are non-compliant.

# Changelog

- 0.1.3 - Set owner/reviewer/approver values.
- 0.1.2 - Added owner/reviewer/approver frontmatter fields.

- 0.1.1 — Added success metrics, progressive delivery, and failure
  scenarios sections.
- 0.1.0 — Initial draft.
