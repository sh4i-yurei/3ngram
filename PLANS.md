# PLANS.md

PLANS.md defines the rules for ExecPlans used in this repository.

## When an ExecPlan is required

- Tier 3 work (always — this project is Tier 3).
- Any change introducing new dependencies, data contracts, or critical
  workflows.
- Cross-module changes or multi-session implementation work.

## ExecPlan requirements

- ExecPlans MUST be self-contained; a new contributor can implement the
  task using only the ExecPlan and the repo.
- ExecPlans MUST define the user-visible outcome and how to verify it.
- Progress, Surprises and Discoveries, Decision Log, and Outcomes and
  Retrospective MUST be updated as work proceeds.

## Storage

Store ExecPlans under `plans/exec_plans/<YYYY-MM-DD>_<short_slug>.md`.

## Current status

**Phase**: Design (pre-implementation)
**Current milestone**: M1 (Planning) — complete
**Last session**: Session 2 — planning artifacts (PRD, Charter, Roadmap, Backlog)
**Next**: Session 3 — Architecture decisions (options analyses + ADRs)

### Completed artifacts

- Project Intake (docs/planning/project-intake.md)
- Project Proposal (docs/planning/project-proposal.md)
- PRD (docs/planning/requirements-prd.md)
- Project Charter (docs/governance/project-charter.md)
- Project Roadmap (docs/planning/project-roadmap.md)
- Backlog and Milestones (docs/planning/backlog-milestones.md)

### Pending artifacts

- Architecture Options Analyses (docs/architecture/)
- ADRs 001-006 (docs/architecture/adr/)
- System Design (docs/design/system-design.md)
- Module Designs (docs/design/module-*.md)
- Threat Model (docs/operations/threat-model.md)
- SLI/SLO (docs/operations/sli-slo.md)
- Risk Register (docs/governance/risk-register.md)
- Technical Specification (docs/specs/technical-specification.md)
- Schema Definitions (docs/design/schemas/)
