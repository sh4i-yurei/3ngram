# 3ngram

A kernel-governed memory OS for AI agents. Typed, versioned memory with
agentic retrieval, policy-gated durable writes, and dual-protocol
communication (MCP + A2A).

## Motivation

LLMs are fundamentally amnesic — fixed context windows, no durable state,
hallucinations when retrieval fails. Existing RAG solutions treat memory
as a library concern. 3ngram treats memory as an OS-level kernel with
mandatory invariants, typed memory, and self-healing mechanisms.

This project replaces the deprecated `ai_tech_stack` repository, applying
lessons learned from that attempt.

## Status

**Design phase complete (M1–M3).** Next milestone: M4 (Specification) —
technical specs and schema definitions.

- M1 (Planning): intake, proposal, PRD, charter, roadmap, backlog
- M2 (Architecture): 2 options analyses, 12 ADRs
- M3 (Design): system design v0.1.3, 4 module designs, SLI/SLO, risk
  register. Design review 45/45 PASS.

See [PLANS.md](PLANS.md) for session history and
[docs/](docs/) for all artifacts.

## Architecture overview

See [system design v0.1.3](docs/design/system-design.md) for the full
architecture. Core concepts:

- **Memory Kernel**: 8 typed records (Belief, Decision, Entity, Episode,
  Preference, Reflection, Resource, Skill) with temporal awareness and
  versioning
- **HippoRAG Retrieval**: 6-stage pipeline with adaptive routing, hybrid
  search, validation, and bounded retries
  ([ADR-011](docs/architecture/adr/ADR-011-hipporag-retrieval.md))
- **Librarian Gate**: No durable memory write without policy authorization —
  hybrid declarative rules + RL-trained advisor
  ([ADR-012](docs/architecture/adr/ADR-012-hybrid-librarian-gate.md))
- **Dual Protocol**: MCP (agent-to-tools) + A2A v0.3 (agent-to-agent)
  ([ADR-002](docs/architecture/adr/ADR-002-dual-protocol.md))
- **Monolith-first**: Single Python service with clear module boundaries
  ([ADR-001](docs/architecture/adr/ADR-001-monolith-first.md))
- **Postgres+pgvector**: Unified storage
  ([ADR-003](docs/architecture/adr/ADR-003-storage-backend.md))
- **Self-healing**: Circuit breakers + retries at module boundaries

## Quick start

Prerequisites and setup instructions will be added after the specification
phase completes.

## Development workflow

- Branch strategy: `<type>/<short-name>`, squash merge, PR-based
- AI assistance governed by `AGENTS.md` and `.kb/ai-context.yaml`
- CI gates A-F per STD-030

## Testing

Testing strategy and commands will be added after specification phase.

## Documentation

### Planning (M1)

- [Project Intake](docs/planning/project-intake.md)
- [Project Proposal](docs/planning/project-proposal.md)
- [PRD](docs/planning/requirements-prd.md)
- [Project Charter](docs/governance/project-charter.md)
- [Project Roadmap](docs/planning/project-roadmap.md)
- [Backlog and Milestones](docs/planning/backlog-milestones.md)

### Architecture (M2)

- [Options Analysis: Architecture Style](docs/architecture/options-analysis-architecture.md)
- [Options Analysis: Protocol Strategy](docs/architecture/options-analysis-protocols.md)
- ADRs 001–012 in [docs/architecture/adr/](docs/architecture/adr/)

### Design (M3)

- [System Design v0.1.3](docs/design/system-design.md)
- [Module: Memory](docs/design/module-memory.md)
- [Module: Retrieval](docs/design/module-retrieval.md)
- [Module: Autonomy](docs/design/module-autonomy.md)
- [Module: Infrastructure](docs/design/module-infrastructure.md)
- [SLI/SLO Targets](docs/operations/sli-slo.md)
- [Risk Register](docs/governance/risk-register.md)

### Governance

- [AGENTS.md](AGENTS.md) — AI agent behavior rules
- [PLANS.md](PLANS.md) — ExecPlan requirements and progress

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
