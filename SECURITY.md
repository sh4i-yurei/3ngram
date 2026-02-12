---
id: TPL-PRJ-SECURITY
title: Security policy template
version: 0.1.2
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-007]
tags: [template, security, policy]
---
# Purpose

Provide a standard security policy template for governed projects.

# Scope

Use for all governed repositories that accept external reports or manage
sensitive data.

# Standard

## Template

### Security policy

State how this project handles security, reporting, and supported
versions.

#### Scope

What systems and artifacts this policy covers.

#### Supported versions

List supported releases or branches and how long they receive fixes.

#### Reporting vulnerabilities

- How to report: <email/form/security.md issue template>
- Information to include: affected version, impact, reproduction steps.
- Expected response time: <SLO>.

#### Handling vulnerabilities

- Triage process and owners.
- Fix and validation expectations (tests, advisories).
- Disclosure plan and timelines.

#### Dependencies and secrets

- Approved dependency sources and update cadence.
- Secret handling rules (no secrets in repo; use vault or CI secrets).

#### Safe behavior expectations

- Follow [Security_and_Threat_Modeling_Standard](../../../03_Engineering_Standards/Security_and_Threat_Modeling_Standard.md).
- Avoid new dependencies or services without approval.
- Require code review and CI for all changes.

#### Contact

Security contact: <name/email/handle>.

# Implementation Notes

- Align vulnerability handling with
  [vulnerability-management-workflow](../../../05_Dev_Workflows/vulnerability-management-workflow.md).
- Keep contact details current.

# Continuous Improvement and Compliance Metrics

Track vulnerability response times and recurrence trends.

# Compliance

Projects without a security policy are non-compliant.

# Changelog

- 0.1.2 - Set owner/reviewer/approver values.
- 0.1.1 - Added owner/reviewer/approver frontmatter fields.

- 0.1.0 — Initial draft.
