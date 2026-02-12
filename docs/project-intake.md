---
id: TPL-PRJ-INTAKE
title: Project intake template
version: 0.1.4
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-003, STD-032]
tags: [template, intake, planning, project]
---
# Purpose

Provide a pre-repo intake record so new projects have an issue-like
artifact before a repository exists.

# Scope

Use when initiating a new project that does not yet have a repository or
issue tracker.

# Standard

## Summary

One-paragraph description of the project and why it matters.

## Requestor and owner

- Requestor: <name>
- Proposed owner/maintainer: <name>
- Date opened: <YYYY-MM-DD>

## Problem statement

What problem are we solving and why now?

## Goals and success criteria

- Goal 1:
- Goal 2:

## Non-goals

- Out of scope item 1:
- Out of scope item 2:

## Users and stakeholders

- Primary users:
- Stakeholders:

## Constraints and assumptions

- Technical:
- Timeline:
- Budget/compliance:

## Initial change tier

Tier 3 (new system) unless justified otherwise. Reference
[SDLC_With_AI](../../../05_Dev_Workflows/SDLC_With_AI.md) for tiering.

## Risks and dependencies

- Risk:
- Dependency:

## Proposed next steps

- Create repository.
- Draft a Tier 3 project proposal using [project-proposal_tpl](project-proposal_tpl.md) before
  design.
- Draft PRD using [requirements-prd_tpl](requirements-prd_tpl.md).
- Draft project charter using [project_charter_tpl](../project_root/project_charter_tpl.md).
- Open an issue in the new repo and link back to this intake record.

## Links

- Governing standards: [Issue_and_Change_Management_Policy](../../../01_Governance/Issue_and_Change_Management_Policy.md), [SDLC_With_AI](../../../05_Dev_Workflows/SDLC_With_AI.md)
- Related notes: <links>

# Implementation Notes

- Store this intake record in the KB until the repo exists.
- After repo creation, migrate key details into the repo issue tracker
  and keep this record as the origin link.

# Continuous Improvement and Compliance Metrics

- Track time from intake to repo creation.
- Review intake completeness during retrospectives.

# Compliance

New projects without an intake record or equivalent are non-compliant.

# Changelog

- 0.1.4 - Set owner/reviewer/approver values.
- 0.1.3 - Added owner/reviewer/approver frontmatter fields.

- 0.1.2 — Replaced template paths with KB links.
- 0.1.1 — Added project proposal requirement for Tier 3.
- 0.1.0 — Initial draft.
