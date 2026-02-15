---
name: spec-authoring
description: Write technical specifications per STD-023. Use when creating or reviewing specs that authorize implementation work.
---

# Overview

Guide the authoring of Technical Specifications aligned to STD-023 and
the TPL-PRJ-TECH-SPEC template. Specs translate approved Module Designs
into explicit implementation instructions and are the gate that
authorizes code.

# Instructions

## Before writing

1. Confirm a Module Design exists and is approved for the scope being
   specified. Specs without a parent design are non-compliant (STD-020).
2. Establish the traceability chain:
   - PRD requirement(s) being addressed
   - System Design component(s) being refined
   - Module Design section(s) being implemented
   - ADR(s) constraining the implementation
3. Read the existing system design at `docs/design/system-design.md`
   and relevant module design(s) under `docs/design/`.

## Required sections (STD-023)

Every spec MUST include all 10 sections. Empty sections must state
"Not applicable" with justification.

1. **Scope and intent** -- What behavior is added/changed/removed and
   which Module Design section this implements.
2. **Implementation boundaries** -- Files, modules, or components that
   may be modified. Forbidden areas explicitly listed.
3. **Interfaces and contracts** -- Public interfaces, inputs/outputs,
   payloads, error shapes, compatibility considerations.
4. **Data structures and models** -- Data models, schemas, migrations,
   ownership changes. Link schema definitions per STD-055.
5. **Algorithms and control flow** -- Core logic, edge cases, pseudocode
   where needed to remove ambiguity.
6. **Error handling behavior** -- Expected errors, retry/backoff rules,
   failure surfacing.
7. **Configuration and dependencies** -- Config keys, defaults, new
   dependencies with approval status.
8. **Testing requirements** -- Test cases (unit, integration, e2e),
   coverage goals, how to run tests.
9. **Success metrics and instrumentation** -- Metrics tied to design,
   telemetry required to measure them.
10. **Non-functional constraints** -- Performance, scalability, security,
    observability, privacy requirements.

## Additional required content

- **Explicit exclusions** -- What is intentionally NOT being changed,
  including deferred work.
- **Validation and rollout** -- Migration/rollback steps, feature flags,
  monitoring, rollback triggers.
- **Links** -- Module Design, ADRs, Issues/PRs.

## Template reference (TPL-PRJ-TECH-SPEC)

The canonical template lives in the KB at:
`06_Projects/Templates/design/technical_specification_tpl.md`

Fetch it with:

```bash
gh api repos/sh4i-yurei/policies-and-standards/contents/06_Projects/Templates/design/technical_specification_tpl.md --jq '.content' | base64 -d
```

## Pre-submission checklist

Before requesting review, verify:

- [ ] All 10 required sections present and non-empty
- [ ] Traceability chain complete (PRD -> System Design -> Module Design -> Spec)
- [ ] ADR references for every architectural constraint
- [ ] Schema definitions linked per STD-055
- [ ] Implementation boundaries explicit (allowed + forbidden)
- [ ] Test cases cover happy path, error paths, and edge cases
- [ ] Non-functional constraints have measurable targets
- [ ] Exclusions section prevents scope creep
- [ ] No implementation code in the spec (pseudocode is acceptable)
- [ ] Frontmatter includes: title, version, status, owner, last_updated

## 3ngram-specific guidance

- All specs live under `docs/specs/`
- Naming convention: `<module>-<component>-spec.md`
- Module boundaries defined in system design must be respected --
  specs cannot cross module boundaries without ADR justification
- Applicable rule packs: STD-050 (API), STD-051 (data), STD-053 (security)
- Librarian Gate invariant: any spec involving memory writes MUST
  route through the Gate (ADR-012)
- Self-healing pattern: specs for infrastructure modules MUST include
  aiobreaker circuit breaker and tenacity retry configuration

# Safety / Limits

- Read-only: do not create spec files without explicit user request.
- Do not fabricate requirements -- if the Module Design is unclear,
  flag the ambiguity rather than guessing.
- Do not skip sections. "Not applicable" with justification is
  acceptable; blank sections are not.
