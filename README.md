---
id: TPL-PRJ-README
title: README template
version: 0.1.4
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001]
tags: [template, readme, project]
---
# Purpose

Provide a standard README structure for governed projects.

# Scope

Use for all governed repositories.

# Standard

## Template

### <project name>

Short summary of what the project does and who it is for.

#### Motivation

Why this project exists and the problem it solves.

#### Quick start

- Prerequisites: <tools, versions>
- Install/setup: <commands>
- Run: <command>
- Sample usage: <cli/api snippet>

#### Architecture overview

Brief description plus links to architecture, design, and ADRs.

#### Development workflow

- Branch strategy: <link or summary>
- How to use AI assistance in this repo (see [KB_Integration_Standard](../../../03_Engineering_Standards/KB_Integration_Standard.md)
  and `AGENTS.md`).
- Required checks before PR merge.

#### Testing

How to run tests locally and in CI. Note required coverage or gates.

#### Configuration

Where config lives, key environment variables, and secrets handling.

#### Documentation

Links to project docs (architecture, specs, testing, style guide,
runbooks).

#### License

Link to `LICENSE`.

#### Contributing

Link to [CONTRIBUTING](./CONTRIBUTING.md) and
[CODE_OF_CONDUCT](./CODE_OF_CONDUCT.md).

# Implementation Notes

- Keep README links current with repo structure.
- Prefer concise sections; link out for deep detail.

# Continuous Improvement and Compliance Metrics

Track README accuracy during release readiness reviews.

# Compliance

Repositories without a README are non-compliant.

# Changelog
- 0.1.4 - Updated links for renamed engineering standards.

- 0.1.3 - Set owner/reviewer/approver values.
- 0.1.2 - Added owner/reviewer/approver frontmatter fields.

- 0.1.1 - Linked KB integration standard in development workflow.
- 0.1.0 — Initial draft.
