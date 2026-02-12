---
id: TPL-PRJ-PLANS
title: PLANS.md template
version: 0.1.4
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-004, STD-032]
tags: [template, ai, plans, execplan]
---
# Purpose

Provide a repo-local PLANS.md file that defines how ExecPlans are
written and maintained for complex AI-assisted work.

# Scope

Use in all governed repositories. Save as `PLANS.md` at the repo root.

# Standard

## PLANS.md template

PLANS.md defines the rules for ExecPlans used in this repository.
ExecPlans are living execution plans for complex tasks and MUST follow
`[exec_plan_tpl](../ai/exec_plan_tpl.md)`.

### When an ExecPlan is required

- Tier 3 work (always).
- Tier 2 work that is cross-module, multi-day, high-risk, or has
  unresolved requirements or unclear technical approach after initial
  scoping.
- Any change introducing new dependencies, data contracts, or critical
  workflows.

### ExecPlan requirements

- ExecPlans MUST be self-contained; a new contributor can implement the
  task using only the ExecPlan and the repo, with links and excerpts for
  required standards and artifacts.
- ExecPlans MUST define the user-visible outcome and how to verify it.
- ExecPlans MUST include and maintain the required sections in
  `[exec_plan_tpl](../ai/exec_plan_tpl.md)`.
- Progress, Surprises & Discoveries, Decision Log, and Outcomes &
  Retrospective MUST be updated as work proceeds.

### Review and optimization

- Review the ExecPlan at each milestone and before handoffs.
- Update PLANS.md if recurring issues or gaps appear in ExecPlans.

### Usage note

Create one ExecPlan file per complex task and keep it up to date
throughout implementation. Store ExecPlans under
`plans/exec_plans/<YYYY-MM-DD>_<short_slug>.md`.

# Implementation Notes

- Keep PLANS.md concise; put execution detail in ExecPlans.
- Reference `PLANS.md` from AGENTS.md so agents know when to use it.

# Continuous Improvement and Compliance Metrics

- Track ExecPlan usage and missed-plan incidents in reviews.

# Compliance

Complex tasks executed without an ExecPlan are non-compliant.

# Changelog

- 0.1.4 - Replaced subjective "ambiguous" criterion with objective scoping language.
- 0.1.3 - Set owner/reviewer/approver values.
- 0.1.2 - Added owner/reviewer/approver frontmatter fields.

- 0.1.1 - Clarified self-contained expectations and storage location.
- 0.1.0 - Initial draft.
