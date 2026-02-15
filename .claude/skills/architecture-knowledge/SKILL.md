---
name: architecture-knowledge
description: 3ngram architecture reference — ADRs, module boundaries, invariants, design locations. Use when making design or implementation decisions.
---

# Overview

Authoritative quick-reference for 3ngram's architecture. Summarizes all
12 ADRs, module boundaries, settled decisions, and key invariants.
Consult this before proposing any architectural change.

# Instructions

## ADR Index

All ADRs live in `docs/architecture/adr/`. Every numbered ADR listed
below (ADR-001 through ADR-012) currently has status **Accepted**.

| ADR | Title | Supersedes | Phase |
|-----|-------|------------|-------|
| 001 | Monolith-first architecture | -- | Foundational |
| 002 | Dual protocol (MCP + A2A v0.3) | -- | Foundational |
| 003 | Storage backend (Postgres + pgvector) | Original Qdrant plan | Foundational |
| 004 | Embedding model (fastembed, bge-small-en-v1.5) | -- | Superseded by 007 |
| 005 | Agent roles (Python Protocol classes) | -- | Superseded by 008 |
| 006 | Knowledge graph deferred | -- | Superseded by 009 |
| 007 | Embedding adapter (swappable interface) | ADR-004 scope | Phase 1 |
| 008 | Expanded agent architecture (RL components) | ADR-005 scope | Phase 1-3 |
| 009 | Knowledge graph Phase 2 (NetworkX, Neo4j path) | ADR-006 timeline | Phase 2 |
| 010 | CLS consolidation (dual-path fast/slow) | -- | Phase 2 |
| 011 | HippoRAG retrieval (6-stage pipeline) | -- | Phase 1-3 |
| 012 | Hybrid Librarian Gate (rules + RL advisor) | -- | Phase 1-3 |

### ADR summaries

**ADR-001 Monolith-first**: Single Python FastAPI service with module
boundaries enforced by import-linter. CPU-bound work (embeddings)
bulkheaded via ProcessPoolExecutor. Self-healing via aiobreaker circuit
breakers and tenacity retries.

**ADR-002 Dual protocol**: MCP (vertical, agent-to-tools) at `/mcp/`
and A2A v0.3 (horizontal, agent-to-agent) at `/` with agent card at
`/.well-known/agent-card.json`. Shared authentication middleware, shared
domain layer.

**ADR-003 Storage backend**: Postgres+pgvector replaces Postgres+Qdrant.
Unified storage eliminates cross-database consistency bugs. HNSW
indexing, hybrid search via RRF in SQL. Scaling ceiling ~1M vectors.

**ADR-004 Embedding model** (superseded by ADR-007): Selected fastembed
with BAAI/bge-small-en-v1.5 (384 dims). CPU-first, GPU optional via
RTX 3070. ONNX Runtime avoids PyTorch dependency.

**ADR-005 Agent roles** (superseded by ADR-008): Agent roles as Python
Protocol classes (Researcher for MVP). No framework dependency
(LangGraph, CrewAI avoided). AgentRole Protocol with `execute()`,
`cancel()`, `health_check()`.

**ADR-006 Knowledge graph** (superseded by ADR-009): Lightweight
`memory_edges` table designed but implementation deferred to post-MVP.
Edge types: supersedes, supports, contradicts, relates_to, derived_from.

**ADR-007 Embedding adapter**: EmbeddingAdapter Protocol
(`embed_one`, `embed_batch`, `dimension`, `model_name`). fastembed
default (BAAI/bge-small-en-v1.5, 384 dims). `model_version` column
tracks provenance. Re-embedding queued on model swap.

**ADR-008 Expanded agents**: AgentRole Protocol with lifecycle hooks
(`on_start`, `on_stop`, `on_health_check`, `on_schedule`). Phase 1:
Researcher + Librarian. Phase 2: Consolidation Engine + Conflict
Resolver. Phase 3: RL Gate Advisor + Research Scanner + Meta-Optimizer.

**ADR-009 KG Phase 2**: `memory_edges` table (source_id, target_id,
edge_type, weight, metadata). Edge types: supersedes, supports,
contradicts, relates_to, derived_from, similar_to. NetworkX for
in-memory traversal (PageRank alpha=0.85). Graph rebuild every 300s.

**ADR-010 CLS consolidation**: Fast path (hippocampal) = immediate,
full fidelity, temporal decay. Slow path (neocortical) = consolidated,
generalized, durable. Consolidation triggers: scheduled (nightly deep,
hourly light), event-driven, pressure-driven. Original records never
deleted, marked `consolidated`.

**ADR-011 HippoRAG retrieval**: 6 stages: (1) adaptive query routing
(simple/multi_hop/exploratory/skip), (2) hybrid retrieval (dense +
sparse BM25 + KG traversal via RRF k=60), (3) validation (temporal
decay, access control, confidence), (4) RL distillation (Phase 3),
(5) conflict resolution, (6) delivery + feedback. SLO: p95 < 500ms
Phase 1.

**ADR-012 Hybrid Librarian Gate**: Layer 1 = hard constraints (schema
validation, access control, PII detection, rate limiting) -- never
overridden. Layer 2 = soft decisions (ADD/UPDATE/NOOP, conflict
classification, confidence calibration) -- heuristic Phase 1, RL Phase
3. Full auditability: every decision logged with rationale and source.

## Module boundaries

| Module | Package | Subsystem | Phase |
|--------|---------|-----------|-------|
| Type Registry | `engram.memory` | Memory | 1 |
| Librarian Gate | `engram.memory` | Memory | 1/3 |
| Temporal Engine | `engram.memory` | Memory | 1 |
| Conflict Resolver | `engram.memory` | Memory | 2 |
| CLS Consolidation | `engram.memory` | Memory | 2 |
| HippoRAG Index | `engram.retrieval` | Retrieval | 2 |
| Self-RAG Reflection | `engram.retrieval` | Retrieval | 2 |
| Adaptive Query Router | `engram.retrieval` | Retrieval | 1 |
| Runtime Loop | `engram.autonomy` | Autonomy | 1 |
| Self-Eval and Metrics | `engram.autonomy` | Autonomy | 2 |
| Self-Healing | `engram.autonomy` | Autonomy | 3 |
| Research Scanner | `engram.autonomy` | Autonomy | 3 |
| MCP Server | `engram.protocols.mcp` | Protocols | 1 |
| A2A Handler | `engram.protocols.a2a` | Protocols | 4 |
| Researcher Agent | `engram.agents` | Agents | 1 |
| Librarian Agent | `engram.agents` | Agents | 1 |
| PostgreSQL Adapter | `engram.infra` | Infrastructure | 1 |
| Embedding Adapter | `engram.infra` | Infrastructure | 1 |
| KG Adapter | `engram.infra` | Infrastructure | 2 |
| Event Bus | `engram.infra` | Infrastructure | 1 |

### Import rules (enforced by import-linter)

- Protocols layer depends on Agents and domain modules, NOT Infrastructure
- Agents depend on Memory/Retrieval, NOT Infrastructure
- Infrastructure has NO upstream domain dependencies
- All modules accessed through adapter interfaces

## Settled decisions -- do NOT reopen without new ADR

1. **Monolith-first** (ADR-001) -- Single process, no microservices.
   Service extraction via adapters if scale demands it.
2. **Postgres+pgvector unified storage** (ADR-003) -- No separate
   vector database. Revisit only if >1M vectors with measured perf
   degradation.
3. **Dual protocol MCP+A2A** (ADR-002) -- Both protocols on same
   FastAPI app. MCP is the primary agent interface.
4. **Hybrid Librarian Gate** (ADR-012) -- All durable writes route
   through the Gate. No bypass paths. Hard constraints never overridden
   by RL.
5. **CLS dual-path consolidation** (ADR-010) -- Fast/slow memory paths.
   Original records never deleted; consolidation creates new records
   with derived_from edges.

## Key invariants

1. **No durable write without Gate authorization** -- Every write
   (external, consolidation, self-healing) routes through the
   Librarian Gate. Gate bypass is a critical vulnerability.
2. **Hard constraints never overridden** -- Layer 1 rules (schema
   validation, access control, rate limiting, PII detection) are
   immutable regardless of RL advisor output.
3. **Bi-temporal version chains are atomic** -- Version operations
   within single PostgreSQL transactions (READ COMMITTED). Optimistic
   concurrency via `expected_version`.
4. **Module boundaries enforced at import level** -- import-linter
   rules prevent cross-boundary violations. Violations fail CI.
5. **Extension points share Gate invariant** -- Custom memory types,
   new agent roles, embedding models, graph backends all produce
   records through the standard Gate flow.

## Design document locations

| Artifact | Path |
|----------|------|
| System Design | `docs/design/system-design.md` |
| Module: Memory | `docs/design/module-memory.md` |
| Module: Retrieval | `docs/design/module-retrieval.md` |
| Module: Autonomy | `docs/design/module-autonomy.md` |
| Module: Infrastructure | `docs/design/module-infrastructure.md` |
| ADRs (12) | `docs/architecture/adr/ADR-{001..012}-*.md` |
| Options Analyses | `docs/architecture/options-analysis-*.md` |
| PRD | `docs/planning/requirements-prd.md` |
| Charter | `docs/governance/project-charter.md` |
| Roadmap | `docs/planning/project-roadmap.md` |
| SLI/SLO | `docs/operations/sli-slo.md` |
| Risk Register | `docs/governance/risk-register.md` |
| Schemas | `docs/design/schemas/` (pending) |
| Specs | `docs/specs/` (template exists; project specs pending) |

## Key interfaces

### Write path

```text
Agent -> MCP/A2A -> Librarian Gate
  -> Layer 1: Schema, PII, ACL, rate limit
  -> Layer 2: ADD/UPDATE/NOOP decision
  -> PostgreSQL transaction (record + embedding + edges)
  -> Event bus notification
  -> Audit log entry
```

### Read path

```text
Agent -> MCP/A2A -> Query Router
  -> Classify: simple | multi_hop | exploratory | skip
  -> Parallel retrieval: dense + sparse + KG
  -> Merge via RRF (k=60)
  -> Validate: temporal, ACL, confidence
  -> Conflict resolution
  -> Response with provenance
```

# Safety / Limits

- This skill is read-only reference material.
- Do not re-open settled decisions without explicit user approval and
  a new ADR.
- If a proposed change conflicts with an invariant listed above, flag
  it immediately -- do not proceed.
- Architecture changes require an options analysis (STD-047) before
  implementation.
