---
id: TPL-PRJ-PR-TEMPLATE
title: Pull request template
version: 0.1.2
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-031, STD-056]
tags: [template, pull_request, workflow]
---
# Purpose

Provide a pull request template that enforces KB citations and required
artifact links.

# Scope

Use in all governed repositories. Save as
`.github/pull_request_template.md`.

# Standard

## Template

### Summary

<short summary>

### KB standards consulted

- <STD-xxx> - <link or note>
- <STD-xxx> - <link or note>

### Decision records

- Issue: <link>
- ADR or decision log: <link>

### Artifacts updated

- PRD: <link or N/A>
- Design: <link or N/A>
- Spec: <link or N/A>
- Schema definition: <link or N/A>

### Tests and validation

- <tests run, commands, or N/A>

### Risk and operations

- Release impact: <text>
- Operational readiness review: <planned|complete|N/A>
- Security considerations: <text or N/A>

### AI assistance

- Tools used: <list>
- Validation performed: <tests, review, checks>
- AI-generated scope: <files or summary>

### Checklist

- [ ] CI gates passed
- [ ] Required docs updated
- [ ] KB citations included
- [ ] Rollback or recovery plan documented (if required)

# Implementation Notes

- Keep the template concise; link to artifacts instead of copying text.

# Continuous Improvement and Compliance Metrics

- Track PRs missing KB citations or decision records.

# Compliance

Pull requests without the required sections are non-compliant.

# Changelog

- 0.1.2 - Set owner/reviewer/approver values.
- 0.1.1 - Added owner/reviewer/approver frontmatter fields.

- 0.1.0 - Initial draft.
