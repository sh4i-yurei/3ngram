---
id: TPL-PRJ-SYSTEM-DESIGN
title: System design template
version: 0.1.6
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-021]
tags: [template, design, system]
---

# Purpose

Provide a structured System Design template aligned with
[System_Design_Standard](../../../04_Design_Framework/System_Design_Standard.md).

# Scope

Use for Tier 3 work and for any system-level design required before
module design or implementation.

# Standard

## Purpose and Objectives

- System purpose: <one-line summary>
- Objectives: <list>
- Success criteria: <text>

## System Scope and Boundaries

- In-scope capabilities: <list>
- Out-of-scope capabilities: <list>
- External boundaries and interfaces: <text>

## Stakeholders and External Actors

- Stakeholders: <list>
- External actors/systems: <list>
- Trust boundaries: <text>

## High-Level Architecture Overview

- Architectural style: <text>
- Major components and responsibilities: <list>
- Key interactions: <text>

## Project Structure

- Directory layout: <tree or list>
- Key file boundaries: <list>
- Module/package mapping: <text>

## Architecture Options Analysis and Decision Rationale

- Options considered: <list>
- Decision criteria: <text>
- Selected option and rationale: <text>
- ADRs or options analysis link: <links>

## Data Ownership and Flow

- Owned data: <list>
- Data ingress/egress: <text>
- Data lifecycle notes: <text>
- Schema definitions: <links>

## Non-Functional Requirements

- Performance and scalability: <text>
- Availability and reliability: <text>
- Observability expectations: <text>

## Security and Risk Considerations

- Threat considerations: <text>
- Authentication/authorization: <text>
- Key risks and mitigations: <text>

## Success Metrics and Instrumentation

- Metrics: <list>
- Instrumentation changes: <text>
- Owners and review window: <text>

## Progressive Delivery and Rollback Strategy

- Rollout approach: <text>
- Rollback triggers and plan: <text>
- Constraints: <text>

## Failure Scenarios and Mitigations

- Critical failure scenarios: <list>
- Mitigations and fallback behavior: <text>

## Design Governance and Approvals

- Decision owner: <name>
- Required approvers: <list>
- Escalation and amendment process: <text>

## Assumptions and Constraints

- Assumptions: <list>
- Constraints: <list>

## Out-of-Scope Considerations

- Explicit exclusions: <list>

## Links

- Module Design: <link>
- Technical Spec: <link>
- Schema definitions: <links>
- ADRs: <links>
- Options analysis: <link>

# Implementation Notes

- Keep all required sections, even if marked N/A.
- Replace placeholders with project-specific details.

# Continuous Improvement and Compliance Metrics

- Track revision frequency and post-implementation corrections.

# Compliance

System designs that omit required sections are non-compliant.

# Changelog

- 0.1.6 - Added project structure section for directory layout and file boundaries.
- 0.1.5 - Set owner/reviewer/approver values.
- 0.1.4 - Added owner/reviewer/approver frontmatter fields.

- 0.1.3 - Removed project-specific content and aligned to required sections.
- 0.1.2 - Fixed frontmatter and aligned required section headings.
- 0.1.1 - Added success metrics, progressive delivery, governance, and
  failure scenarios sections.
- 0.1.0 - Initial consolidated system design aligned to System_Design_Standard.
