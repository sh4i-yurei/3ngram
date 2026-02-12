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
**Current milestone**: M2 (Architecture Decisions) — complete
**Last session**: Session 3 — Architecture decisions (options analyses + ADRs)
**Next**: Session 4 — System design, threat model, SLI/SLO, risk register

### Completed artifacts

- Project Intake (docs/planning/project-intake.md)
- Project Proposal (docs/planning/project-proposal.md)
- PRD (docs/planning/requirements-prd.md)
- Project Charter (docs/governance/project-charter.md)
- Project Roadmap (docs/planning/project-roadmap.md)
- Backlog and Milestones (docs/planning/backlog-milestones.md)
- Options Analysis: Architecture Style (docs/architecture/options-analysis-architecture.md)
- Options Analysis: Protocol Strategy (docs/architecture/options-analysis-protocols.md)
- ADR-001: Monolith-first (docs/architecture/adr/ADR-001-monolith-first.md)
- ADR-002: Dual protocol MCP+A2A (docs/architecture/adr/ADR-002-dual-protocol.md)
- ADR-003: Postgres+pgvector (docs/architecture/adr/ADR-003-storage-backend.md)
- ADR-004: fastembed (docs/architecture/adr/ADR-004-embedding-model.md)
- ADR-005: Agent roles as Protocol classes (docs/architecture/adr/ADR-005-agent-roles.md)
- ADR-006: Knowledge graph deferred (docs/architecture/adr/ADR-006-knowledge-graph.md)

### Pending artifacts

- System Design (docs/design/system-design.md)
- Module Designs (docs/design/module-*.md)
- Threat Model (docs/operations/threat-model.md)
- SLI/SLO (docs/operations/sli-slo.md)
- Risk Register (docs/governance/risk-register.md)
- Technical Specification (docs/specs/technical-specification.md)
- Schema Definitions (docs/design/schemas/)

### Key architecture decisions (Session 3)

- **ADR-003 changed from proposal**: Postgres+pgvector replaces Postgres+Qdrant. Unified storage eliminates cross-DB consistency class.
- **Self-healing**: aiobreaker circuit breakers + tenacity retries at module boundaries, component health checks.
- **Agent learning**: Data collection from day one (log all retrievals, results, feedback). Actual learning algorithms are post-MVP.
- **No agent framework**: Python Protocol classes, not LangGraph/CrewAI/Pydantic AI. 1-2 agents don't justify framework overhead.
