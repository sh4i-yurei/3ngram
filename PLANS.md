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

**Phase**: Specification (pre-implementation)
**Current milestone**: M4 (Specification) — in progress
**Last session**: Session 9 — 10-issue sprint across 5 instances, code quality tooling, agent skills, CI improvements
**Next**: Session 10 — Stage 3 specification work (ExecPlan required first)

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
- System Design v0.1.3 (docs/design/system-design.md)
- ADR-007: Embedding adapter (docs/architecture/adr/ADR-007-embedding-adapter.md)
- ADR-008: Expanded agent architecture (docs/architecture/adr/ADR-008-expanded-agent-architecture.md)
- ADR-009: Knowledge graph Phase 2 (docs/architecture/adr/ADR-009-knowledge-graph-phase2.md)
- ADR-010: CLS consolidation (docs/architecture/adr/ADR-010-cls-consolidation.md)
- ADR-011: HippoRAG retrieval (docs/architecture/adr/ADR-011-hipporag-retrieval.md)
- ADR-012: Hybrid Librarian Gate (docs/architecture/adr/ADR-012-hybrid-librarian-gate.md)
- SLI/SLO Targets v0.1.0 (docs/operations/sli-slo.md)
- Risk Register v0.1.0 (docs/governance/risk-register.md)
- Module Design: Memory (docs/design/module-memory.md)
- Module Design: Retrieval (docs/design/module-retrieval.md)
- Module Design: Autonomy (docs/design/module-autonomy.md)
- Module Design: Infrastructure (docs/design/module-infrastructure.md)
- Project Charter v0.2.1 (docs/governance/project-charter.md)

### Stage 3 artifacts (pending)

- Technical Specification (docs/specs/technical-specification.md) — Stage 3
- Schema Definitions (docs/design/schemas/) — Stage 3

### Key decisions (Session 9)

- **10-issue sprint**: First 5-instance concurrent sprint. Closed 3ngram #20, #21, #22 and p&s #24, #28, #29, #38, #47, #48, #49.
- **Code quality tooling** (PR #26): Expanded ruff rules (C90, C4, RET, S, ARG, PLR, PLW), added vulture + pip-audit, created validate-version-refs.sh, check-frontmatter.py, vulture_whitelist.py.
- **M4 agent skills** (PR #25): Created spec-authoring, schema-authoring, and architecture-knowledge skills for Stage 3 work.
- **AGENTS.md updated** (PR #19): Git safety rules, artifact creation rules, problem solving rules added.
- **p&s CI improvements**: Post-merge health check (#50), failure notifications (#53), gate caching (#54), STD-030 optimization section (#52), KB templates and amendments (#51).
- **Merge management lesson**: Multi-agent PRs cause cascading behind-main states. Need dedicated merge manager phase for future sprints. Pattern recorded in MEMORY.md.
- **Branch discipline issues**: Shared local clone across 5 instances caused branch collisions. Per-instance worktrees recommended for future multi-agent sessions.

### Key decisions (Session 8)

- **Cross-project tooling**: Built scripts (branch-status.sh, ci-status.sh, ci-logs.sh, branch-cleanup.sh, session-verify.sh), commands (daily-report, session-start, session-close), and skills in home directory.
- **KB gap analysis**: Identified 5 new p&s issues (#42-#46) from systematic KB audit.
- **Sprint planning**: Created 10-issue sprint plan distributed across 5 instances.

### Key decisions (Session 7)

- **PR #3 merged**: M2 architecture decisions + M3 design artifacts merged to main (squash, commit 7b9854c). Design phase complete.
- **Phase transition**: Design (Stage 2) complete, entering Specification (Stage 3). Governance files updated (PLANS.md, AI_CONTEXT.md, AGENTS.md).
- **Spec phase scope**: Stage 3 requires ~4 technical specifications (one per module: Memory, Retrieval, Autonomy, Infrastructure) per STD-023, and ~7 schema definitions (memory_records, memory_versions, memory_edges, librarian_audit, librarian_queue, agent_registry, outbox) per STD-055.
- **Authoring order**: Schema definitions first (tech specs reference them), then tech specs per module.
- **ExecPlan required**: Stage 3 work is Tier 3 and needs an ExecPlan in `plans/exec_plans/` before starting.
- **Open issues addressed**: #5 (CI gates), #7 (scope disclaimers) worked in parallel by separate instances.
- **Parallel execution**: 3 Claude instances — Instance 1 (governance + orchestration), Instance 2 (docs issues #4/#7), Instance 3 (CI gates #5).

### Key decisions (Session 6)

- **Critical quality review**: 5 parallel review agents audited all 4 module designs + cross-artifact consistency. Memory scored 9.5/10 (clean), others had actionable issues.
- **Retrieval fixes (7)**: Broken system design section refs, PageRank limits corrected, `include_historical` flag added to RetrievalQuery, retry escalation logic fixed, ProcessPoolExecutor → `asyncio.to_thread()`, latency buffer reduced.
- **Autonomy fixes (5)**: Wrong ADR-008 scheduling ref → ADR-001, "symptom table" → "critical failure scenarios", PII cross-ref sharpened.
- **Infrastructure fixes (4)**: EventBus handler typed as async callable, graph rebuild atomic swap documented, outbox worker restart clarified, pending refs → STD-055/STD-023 citations.
- **Charter v0.2.1**: All Qdrant references replaced with Postgres+pgvector per ADR-003 (9 edits across goals, constraints, assumptions, risks, implementation steps).
- **Cross-artifact cleanup**: Deleted garbage template file, added superseded ADR notes to AI_CONTEXT.md, PRD disclaimer added (frozen baseline).
- **Design review re-run**: PASS (45/45 STD-024 checklist items).

### Key decisions (Session 5)

- **3 CRITICALs resolved**: Gate bypass via consolidation (internal write path added), no concurrency control (optimistic locking added), PII regex overclaim (reclassified as best-effort). System design bumped to v0.1.1.
- **Threat model approach**: Embedded in module designs per STD-007, not a standalone document. System design updated to v0.1.2.
- **SLI/SLO targets**: 6 critical paths defined per STD-043 — Gate latency, retrieval latency, embedding latency, uptime, audit completeness, consolidation retention.
- **Risk register**: 20 risks across security (5), reliability (8), delivery (4), compliance (3). RSK-014 (solo developer) accepted.
- **Parallel execution**: M3 work split across 3 Claude instances — Instance 1 (Memory + Retrieval modules), Instance 2 (Autonomy + Infrastructure modules), Instance 3 (SLI/SLO + risk register + governance).

### Key decisions (Session 4)

- **v2 scope expansion**: System design synthesizes v2 feature spec with M1/M2 artifacts. 8 memory types (up from 4), HippoRAG retrieval, CLS consolidation, RL Gate Advisor, 5-phase delivery plan.
- **ADR-004 superseded**: Embedding adapter interface replaces fixed fastembed model (ADR-007).
- **ADR-005 superseded**: Expanded agent architecture with RL components (ADR-008).
- **ADR-006 superseded**: Knowledge graph promoted to Phase 2 scope (ADR-009).
- **New patterns**: CLS dual-path consolidation (ADR-010), HippoRAG retrieval pipeline (ADR-011), hybrid Librarian Gate (ADR-012).

### Key architecture decisions (Session 3)

- **ADR-003 changed from proposal**: Postgres+pgvector replaces Postgres+Qdrant. Unified storage eliminates cross-DB consistency class.
- **Self-healing**: aiobreaker circuit breakers + tenacity retries at module boundaries, component health checks.
- **Agent learning**: Data collection from day one (log all retrievals, results, feedback). Actual learning algorithms are post-MVP.
- **No agent framework**: Python Protocol classes, not LangGraph/CrewAI/Pydantic AI. 1-2 agents don't justify framework overhead.
