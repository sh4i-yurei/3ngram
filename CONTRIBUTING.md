---
id: TPL-PRJ-CONTRIBUTING
title: Contributing template
version: 0.1.4
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-003, STD-005, STD-008, STD-031, STD-032]
tags: [template, contributing, workflow, project]
---
# Purpose

Provide a consistent contributing guide template for governed projects.

# Scope

Use for any repository governed by this knowledgebase.

# Standard

## Template

### Contributing

Set expectations for proposing work, opening PRs, and using AI
assistance.

#### How to propose work

- Open an issue describing the problem, scope, and change tier.
- Link to governing standards and the relevant design or spec.

#### Branch and pull request flow

- Branch naming: <feature|fix|chore|docs>/<short-name>.
- PR requirements: passing CI, links to issue and decision record,
  updated docs and tests, adherence to review checklist.

#### Commit style

- Use Conventional Commit prefixes (e.g., feat:, fix:, docs:).
- Keep commits small and scoped; avoid mixing concerns.

#### Coding and testing expectations

- Follow [Coding_Standards_and_Conventions](../../../03_Engineering_Standards/Coding_Standards_and_Conventions.md) and
  [Testing_and_Quality_Standard](../../../03_Engineering_Standards/Testing_and_Quality_Standard.md).
- Write or update tests with each change; no failing tests on merge.

#### Documentation expectations

- Update README, design, specs, and runbooks when behavior or intent
  changes.
- Keep changelogs current where used.

#### AI-assisted work

- Provide the approved spec and standards in the prompt context.
- Follow [KB_Integration_Standard](../../../03_Engineering_Standards/KB_Integration_Standard.md) and `AGENTS.md` for KB retrieval and
  pointer artifact requirements.
- Summarize AI-generated changes in the PR description.
- Do not bypass reviews or required gates.

#### Getting help

- Maintainer contact: <name/email/handle>.
- Discuss larger changes in an issue before opening a PR.
- Code of conduct: [CODE_OF_CONDUCT](./CODE_OF_CONDUCT.md).

# Implementation Notes

- Adapt the template to project-specific workflows as needed.
- Keep links up to date with the project structure.

# Continuous Improvement and Compliance Metrics

Track contribution friction, review turnaround time, and rework rates.

# Compliance

Repositories without a contributing guide are non-compliant.

# Changelog
- 0.1.4 - Updated links for renamed engineering standards.

- 0.1.3 - Set owner/reviewer/approver values.
- 0.1.2 - Added owner/reviewer/approver frontmatter fields.

- 0.1.1 — Linked KB integration standard for AI-assisted work.
- 0.1.0 — Initial draft.
