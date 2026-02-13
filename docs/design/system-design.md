---
id: 3NGRAM-SD-001
title: "3ngram: Agentic RAG Memory System — System Design"
version: 0.1.3
category: project
status: draft
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-021]
tags: [design, system-design, architecture, 3ngram]
---

# 3ngram: Agentic RAG Memory System — System Design

# Purpose

This system design defines the architecture for 3ngram, an always-on
autonomous AI kernel that provides typed, versioned memory with agentic
retrieval, policy-gated writes, and dual-protocol communication for AI
agents. It is the authoritative architectural reference for all
downstream design and specification work.

This document synthesizes the v2 feature specification (the full vision)
with the existing M1/M2 artifacts (PRD, charter, ADRs 001-006) into a
governed system design per STD-021. Where the v2 spec expands scope
beyond the original PRD, this document is the authority.

# Scope

This design covers the complete 3ngram architecture across all five
implementation phases. Phase 1 (core kernel) is the MVP. Later phases
are defined at architecture level to ensure Phase 1 decisions do not
create migration barriers.

**In scope**: All four kernel subsystems (memory, retrieval, autonomy,
dev environment), dual-protocol interfaces (MCP + A2A), communication
layer, and infrastructure layer.

**Out of scope**: Mobile/desktop client apps (Phase 4 delivery
channels), multi-tenant support (Phase 5), source code
self-modification, and production Kubernetes deployment.

# Standard

## Purpose and Objectives

### System purpose

3ngram is a **kernel-governed memory operating system for AI agents**. It
sits between the user and every connected AI agent, tool, and automation,
managing shared memory, orchestrating agent collaboration, learning from
every interaction, and improving itself continuously.

It is not a chatbot, not a RAG pipeline, not a plugin. It is the
operating system layer that makes an entire AI stack behave as a single,
self-aware, self-improving intelligence.

### Objectives

1. **Durable typed memory**: Persist structured knowledge (8 memory
   types) across agent sessions with bi-temporal versioning, provenance
   tracking, and confidence scoring.

2. **Policy-gated writes**: Enforce 100% write authorization through the
   Librarian Gate — a hybrid rule-based + RL-trained gatekeeper with
   zero bypass paths.

3. **Intelligent retrieval**: Provide HippoRAG-inspired hybrid retrieval
   (vector + keyword + knowledge graph) with self-reflective validation,
   adaptive query routing, and bounded retries.

4. **Autonomous operation**: Run continuously with self-evaluation,
   self-healing, CLS-inspired memory consolidation, and research-driven
   self-improvement.

5. **Dev-environment native**: Understand code, projects, CI/CD, and
   development workflows as first-class concepts.

6. **Protocol-native interfaces**: Expose all capabilities through MCP
   (agent-to-kernel) and A2A v0.3 (agent-to-agent).

7. **Proactive communication**: Initiate contact with the user only when
   human judgment is needed, batching low-urgency items into
   digest-style insight cards.

### Success criteria

- User never configures memory infrastructure (zero RAG/embedding config)
- Agents find what they need >90% of the time (retrieval hit rate)
- Conflicts detected within seconds of contradictory writes
- User receives < 3 push notifications per week
- Retrieval quality improves month over month (measured by agent
  feedback)
- New agents reach useful context within minutes (progressive feeding)
- The kernel suggests at least one useful self-improvement per month

## System Scope and Boundaries

### In-scope capabilities

**Phase 1 — Core Kernel (months 1-3)**:

- Memory type system (8 types) with record envelope and PostgreSQL
  storage
- Basic Librarian Gate (rule-based policies, no RL)
- Simple retrieval (vector similarity + keyword via pgvector)
- MCP server (`memory_write`, `memory_query`, `memory_forget`)
- Agent registry with token-based identity
- CLI for status and manual operations
- Confidence scoring (observed: 0.9, told: 0.75, inferred: 0.6)

**Phase 2 — Intelligence Layer (months 3-6)**:

- Knowledge graph index (NetworkX, Neo4j migration path)
- HippoRAG-style hybrid retrieval (graph + vector + BM25)
- Self-RAG reflection in retrieval pipeline
- CLS-inspired dual-path consolidation (fast + slow paths)
- Bi-temporal versioning
- Conflict detection
- Adaptive query routing
- Background scheduler for consolidation and decay scoring
- Notification dispatcher (webhook channel first)

**Phase 3 — Self-Improvement (months 6-9)**:

- Feedback collection infrastructure
- RL training pipeline for Gate Advisor (GRPO on accumulated data)
- Memory-R1-style distillation in retrieval pipeline
- Self-evaluation metrics
- Self-healing (automatic re-indexing, embedding refresh, weight
  adjustment)
- Synthetic self-testing
- Research scanner (periodic search + summarization)

**Phase 4 — Jarvis Mode (months 9-12)**:

- Project Context Engine (git integration, CI/CD monitoring)
- Code awareness (dependency tracking, error memory, review memory)
- Workflow Engine (multi-step orchestrated workflows)
- Automation triggers (git events, CI events, cron, monitoring)
- Delivery channels (mobile, desktop, CLI, webhook, email digest)
- Morning briefing and insight card generation
- A2A agent-to-agent protocol support
- Advanced Research Scanner

**Phase 5 — Evolution (month 12+)**:

- Meta-optimizer (evolutionary search over kernel configurations)
- Non-parametric RL for retrieval optimization
- Multi-user support (activate `user_id` scoping)
- Memory portability (export/import, memory passports)
- Plugin system for custom memory types and automation triggers

### Out-of-scope capabilities

- Source code self-modification (Darwin Godel Machine territory)
- Multi-user/multi-tenant in MVP (Phase 5)
- Mobile/desktop client apps as separate products (Phase 4 defines
  delivery channels; client implementations are separate projects)
- Production Kubernetes deployment
- Custom model training or fine-tuning
- Non-English language support

### External boundaries and interfaces

The kernel presents two external interfaces:

1. **MCP** (agent-to-kernel): Vertical integration for tool invocation,
   memory operations, and state queries.
2. **A2A v0.3** (agent-to-agent): Horizontal interoperability for task
   delegation, capability discovery, and collaborative reasoning.

Both interfaces share a common domain layer. No external caller accesses
the infrastructure layer directly.

## Stakeholders and External Actors

### Stakeholders

| Stakeholder | Role | Interest |
|---|---|---|
| Mark (sh4i-yurei) | Sole developer, decision owner | Working system, clean architecture, governed process |
| Governance framework | policies-and-standards KB | Validates STD-032 Tier 3 workflow in practice |

### External actors and systems

| Actor | Protocol | Interaction |
|---|---|---|
| Claude Code | MCP | Primary AI agent consumer: store, query, recall |
| Cursor / Cline | MCP | Coding agents: project context, error memory |
| CI/CD pipelines | Webhook/A2A | Automation triggers, build status events |
| Monitoring tools | Webhook | Alert ingestion, incident correlation |
| Custom agents | MCP / A2A | Extensible agent ecosystem |
| Human operator | CLI / notification channels | Approval requests, conflict resolution, insight review |

### Trust boundaries

```text
┌─────────────────────────────────────────────┐
│ EXTERNAL (untrusted until authenticated)     │
│  ┌─────────────┐  ┌────────────────────┐    │
│  │ MCP clients │  │ A2A peer agents    │    │
│  └──────┬──────┘  └─────────┬──────────┘    │
│         │                   │               │
├─────────┼───────────────────┼───────────────┤
│ PROTOCOL LAYER (auth + rate limiting)        │
│         │ validated token   │               │
├─────────┼───────────────────┼───────────────┤
│ DOMAIN LAYER (kernel subsystems)             │
│  Memory │ Retrieval │ Autonomy │ Dev Env    │
│         │                   │               │
├─────────┼───────────────────┼───────────────┤
│ INFRASTRUCTURE LAYER (kernel-internal only)  │
│  PostgreSQL + pgvector │ KG │ Event Bus     │
└─────────────────────────────────────────────┘
```

All external actors authenticate with token-based identity. Trust
level is assigned on first connect (user approves) and determines
write permissions, type access, and Gate evaluation strictness.

## High-Level Architecture Overview

### Architectural style

**Monolith-first** (ADR-001): Single Python FastAPI process with clear
subsystem boundaries enforced by import-linter. All kernel subsystems
run in-process. The infrastructure layer (PostgreSQL, knowledge graph)
is accessed via adapter interfaces that allow future extraction.

### Four-layer model

```text
USER LAYER
  CLI / Notification channels / Webhook
  Sees: natural-language messages, approval requests, insight cards
  Never sees: embeddings, vectors, policies, confidence scores

           │ Interrupt / Approval Protocol

AGENT LAYER
  Connected LLMs, coding agents, automation tools
  (Claude Code, Cursor, CI/CD, custom agents, cron triggers)
  Sees: typed memory, system state, other agents
  Never manages: indexing, storage, retrieval config

           │ MCP + A2A

KERNEL LAYER
  ┌─────────────────────────────────────────────────┐
  │ MEMORY SUBSYSTEM                                │
  │   Type Registry, Librarian Gate, RL Gate        │
  │   Advisor, Temporal Engine, Conflict Resolver,  │
  │   CLS Consolidation Engine                      │
  ├─────────────────────────────────────────────────┤
  │ RETRIEVAL SUBSYSTEM                             │
  │   HippoRAG Index, Self-RAG Reflection,          │
  │   Adaptive Query Router                         │
  ├─────────────────────────────────────────────────┤
  │ AUTONOMY SUBSYSTEM                              │
  │   Runtime Loop, Self-Eval & Metrics,            │
  │   Meta-Optimizer, Notification Dispatcher,      │
  │   Scheduler, Research Scanner                   │
  ├─────────────────────────────────────────────────┤
  │ DEV ENVIRONMENT SUBSYSTEM                       │
  │   Project Context, Code Awareness,              │
  │   Workflow Engine                               │
  └─────────────────────────────────────────────────┘

           │ Internal (fully abstracted)

INFRASTRUCTURE LAYER
  PostgreSQL + pgvector │ Knowledge Graph (NetworkX → Neo4j)
  Embedding models (swappable) │ Event bus (asyncio → Kafka)
```

### Major components and responsibilities

| Component | Subsystem | Responsibility |
|---|---|---|
| Type Registry | Memory | Schema definitions for 8 memory types; envelope structure |
| Librarian Gate | Memory | Write authorization: declarative rules (hard) + RL advisor (soft) |
| Temporal Engine | Memory | Bi-temporal versioning, temporal queries, decay scoring |
| Conflict Resolver | Memory | Detect and classify contradictions; escalate unresolvable |
| CLS Consolidation | Memory | Dual-path memory management: fast path (recent) + slow path (durable) |
| HippoRAG Index | Retrieval | Hybrid candidate retrieval: dense vector + sparse BM25 + KG traversal |
| Self-RAG Reflection | Retrieval | Validate relevance of retrieved candidates |
| Adaptive Query Router | Retrieval | Route queries by complexity: simple/multi-hop/exploratory/skip |
| Runtime Loop | Autonomy | Continuous operation across three priority tiers |
| Self-Eval | Autonomy | Metric computation: retrieval quality, memory health, agent satisfaction |
| Self-Healing | Autonomy | Autonomous corrective action when metrics degrade |
| Research Scanner | Autonomy | Periodic search for self-improvement techniques |
| Project Context | Dev Env | First-class project entity tracking (git, CI/CD, team, decisions) |
| Code Awareness | Dev Env | Dependency tracking, pattern memory, error memory, review memory |
| Workflow Engine | Dev Env | Multi-step orchestrated development workflows |

### Key interactions

1. **Write path**: Agent submits record via MCP → Librarian Gate
   evaluates (rules + RL advisor) → approved records persist to
   PostgreSQL → embeddings generated → event emitted on internal bus.

2. **Read path**: Agent submits query via MCP → Adaptive Router
   classifies complexity → HippoRAG retrieves candidates (vector +
   keyword + graph) → Self-RAG validates relevance → results filtered
   (temporal, access, confidence) → assembled response returned.

3. **Consolidation path**: Scheduler triggers consolidation → fast-path
   records evaluated → promoted records abstracted and cross-referenced
   → slow-path storage updated → stale records archived.

4. **Self-healing path**: Self-Eval detects metric degradation →
   diagnosis matched to symptom table → auto-repair action taken
   (re-index, refresh embeddings, adjust weights) → metrics re-checked.

## Project Structure

### Directory layout

```text
src/engram/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── config.py               # Settings (Pydantic BaseSettings)
├── memory/                 # Memory subsystem
│   ├── types.py            # 8 memory type schemas + envelope
│   ├── gate.py             # Librarian Gate (policy engine)
│   ├── gate_advisor.py     # RL Gate Advisor (Phase 3)
│   ├── temporal.py         # Bi-temporal versioning engine
│   ├── conflict.py         # Conflict detection and resolution
│   └── consolidation.py    # CLS dual-path consolidation (Phase 2)
├── retrieval/              # Retrieval subsystem
│   ├── router.py           # Adaptive query router
│   ├── search.py           # Hybrid search (vector + keyword + graph)
│   ├── validation.py       # Self-RAG reflection + result validation
│   └── assembly.py         # Response assembly with citations
├── autonomy/               # Autonomy subsystem
│   ├── loop.py             # Runtime loop (3-tier priority)
│   ├── metrics.py          # Self-evaluation metrics
│   ├── healing.py          # Self-healing actions
│   ├── scheduler.py        # Background task scheduling
│   └── scanner.py          # Research scanner (Phase 3)
├── devenv/                 # Dev environment subsystem (Phase 4)
│   ├── project.py          # Project context engine
│   ├── code.py             # Code awareness
│   └── workflow.py         # Workflow engine
├── protocols/              # External protocol adapters
│   ├── mcp/                # MCP server (tools, resources)
│   │   ├── server.py       # FastMCP server setup
│   │   └── tools.py        # MCP tool definitions
│   └── a2a/                # A2A endpoint (agent card, tasks)
│       ├── handler.py      # A2A message handling
│       └── card.py         # Agent card generation
├── agents/                 # Agent role implementations
│   ├── base.py             # AgentRole Protocol definition
│   ├── researcher.py       # Researcher role (retrieval + assembly)
│   └── librarian.py        # Librarian role (gate orchestration)
├── infra/                  # Infrastructure adapters
│   ├── db.py               # PostgreSQL + pgvector connection
│   ├── embeddings.py       # Embedding adapter (fastembed default)
│   ├── graph.py            # Knowledge graph adapter (Phase 2)
│   └── events.py           # Internal event bus
└── notifications/          # Communication layer
    ├── dispatcher.py       # Notification routing
    └── channels/           # Delivery channel implementations
        ├── cli.py          # CLI output
        └── webhook.py      # Webhook delivery
```

### Module/package mapping

| Kernel Subsystem | Python Package | Phase |
|---|---|---|
| Memory | `engram.memory` | 1 (core), 2 (consolidation), 3 (RL advisor) |
| Retrieval | `engram.retrieval` | 1 (basic), 2 (HippoRAG), 3 (RL distiller) |
| Autonomy | `engram.autonomy` | 1 (stub), 2 (scheduler), 3 (full) |
| Dev Environment | `engram.devenv` | 4 |
| Protocols | `engram.protocols` | 1 |
| Agents | `engram.agents` | 1 |
| Infrastructure | `engram.infra` | 1 |
| Notifications | `engram.notifications` | 2 (webhook), 4 (full) |

Import boundaries are enforced by `import-linter` (ADR-001):

- `protocols` depends on `agents` and domain modules, never on `infra`
- `agents` depends on `memory`, `retrieval`, never on `infra`
- `infra` has no upstream dependencies on domain modules
- `memory`, `retrieval`, `autonomy`, `devenv` depend on each other
  through defined interfaces only (Python Protocols)

## Architecture Options Analysis and Decision Rationale

### Existing ADRs (settled)

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Monolith-first architecture | **Active** — unchanged by v2 |
| ADR-002 | Dual protocol (MCP + A2A) | **Active** — unchanged by v2 |
| ADR-003 | Postgres + pgvector (unified storage) | **Active** — v2 confirms; KG is additive (Phase 2) |

### ADRs superseded by v2 scope expansion

| ADR | Original decision | v2 change | New ADR |
|---|---|---|---|
| ADR-004 | fastembed with fixed model | Embedding adapter interface; model is swappable runtime config | ADR-007 |
| ADR-005 | Agent roles as Protocol classes (2 roles) | Expanded roles + RL components; Protocol pattern still valid | ADR-008 |
| ADR-006 | Knowledge graph deferred (not in scope) | KG in Phase 2 scope (NetworkX → Neo4j path) | ADR-009 |

### New architectural decisions from v2

| ADR | Decision | Rationale |
|---|---|---|
| ADR-007 | Swappable embedding adapter | v2 requires model flexibility; fastembed is Phase 1 default but sentence-transformers, GPU models must be swappable without retrieval changes |
| ADR-008 | Expanded agent architecture | v2 adds RL Gate Advisor, Research Scanner, Meta-Optimizer as agent-like components; AgentRole Protocol extended with lifecycle hooks |
| ADR-009 | Knowledge graph in Phase 2 | v2 promotes KG from deferred to Phase 2; NetworkX for prototyping, Neo4j migration path; `memory_edges` schema designed in Phase 1 |
| ADR-010 | CLS dual-path consolidation | v2 adopts Complementary Learning Systems model; fast path for immediate, slow path for consolidated; consolidation triggers (scheduled, event, pressure) |
| ADR-011 | HippoRAG retrieval architecture | v2 adopts HippoRAG-inspired 6-stage pipeline; adaptive routing by query complexity; RL-trained distiller in Phase 3 |
| ADR-012 | Hybrid Librarian Gate (rules + RL) | v2 splits Gate into hard constraints (declarative rules, never overridden) and soft decisions (RL-trained advisor, Phase 3) |

### Links

- Options analysis (architecture): `docs/architecture/options-analysis-architecture.md`
- Options analysis (protocols): `docs/architecture/options-analysis-protocols.md`
- ADRs: `docs/architecture/adr/`

## Data Ownership and Flow

### Owned data

The kernel owns all persistent state. No external system writes
directly to storage.

### Memory type system

Eight core types aligned with CoALA taxonomy and MIRIX architecture:

| Type | Purpose | Phase |
|---|---|---|
| **Belief** | Current understanding of facts or assumptions | 1 |
| **Decision** | A choice with rationale | 1 |
| **Episode** | A narrative interaction sequence | 1 |
| **Skill** | A learned procedure or pattern | 1 |
| **Entity** | A person, project, or system (first-class) | 1 |
| **Preference** | Behavioral preference | 1 |
| **Reflection** | Self-evaluation record | 1 |
| **Resource** | External reference with metadata | 1 |

### Record envelope

Every record is wrapped in a standard envelope:

```text
MemoryRecord {
    id:                 UUID
    type:               MemoryType          # one of 8 types
    content:            str                  # primary text content
    metadata:           dict                 # arbitrary JSON
    version:            int                  # starts at 1
    superseded_by:      UUID | None

    # Provenance
    source_agent:       str                  # agent that created this
    source_confidence:  float                # observed/told/inferred
    evidence_links:     list[UUID]           # supporting records

    # Bi-temporal versioning
    event_time:         datetime             # when true in real world
    ingestion_time:     datetime             # when kernel learned it

    # Governance
    access_level:       AccessLevel          # public/agent/user/system/sensitive
    classification:     str | None           # security label
    gate_decision_id:   UUID                 # Librarian audit reference
    gate_decision_type: GateDecisionType     # external | consolidation | self_healing

    # Concurrency
    expected_version:   int | None           # optimistic lock (required on UPDATE)

    # Lifecycle
    created_at:         datetime
    updated_at:         datetime
    decay_score:        float                # relevance decay (0.0-1.0)
    consolidation_path: str                  # "fast" or "slow"
}
```

### Data flow: write path

All writes pass through the Librarian Gate — no exceptions. Internal
subsystems (consolidation engine, self-healing) use the same Gate
interface as external agents, distinguished by `gate_decision_type`.

```text
External write (agent-initiated):
  Agent → MCP/A2A → Protocol Adapter
    → Librarian Gate (decision_type = external)
      → Layer 1: Declarative rules (schema, access, PII screen, rate limit)
      → Layer 2: RL Advisor (add/update/noop, conflict, confidence)
    → [Approved] → PostgreSQL transaction (see concurrency model below)
      → Record insert/update
      → Embedding generation (via adapter)
      → pgvector upsert
      → KG edge creation (Phase 2)
    → Event bus: memory.created | memory.updated
    → Audit log entry

Internal write (consolidation engine):
  Consolidation Engine → Librarian Gate (decision_type = consolidation)
    → Layer 1: Schema validation, PII screen, classification enforcement
      (access control and rate limiting skipped for internal origin)
    → Layer 2: Conflict classification, consolidation routing
    → [Approved] → PostgreSQL transaction
      → New consolidated record insert
      → Source records: status → 'consolidated', superseded_by set
      → derived_from edges created
    → Event bus: memory.consolidated
    → Audit log entry (internal origin recorded)
```

### Concurrency model

Writes use optimistic concurrency control to prevent version chain
corruption and consolidation races.

- **UPDATE operations**: Require `expected_version` matching the current
  record version. If the version has changed since the caller read it,
  the write is rejected (conflict error). The caller must re-read and
  retry.
- **Consolidation status transitions**: Use `SELECT ... FOR UPDATE`
  within the transaction to lock source records during status change.
  This prevents an agent update racing with consolidation marking.
- **Version chain atomicity**: Inserting a new version and setting
  `superseded_by` on the old version happen in a single PostgreSQL
  transaction at `READ COMMITTED` isolation.
- **Conflict response**: The Gate returns a conflict indicator when
  `expected_version` does not match. Agents are expected to re-read
  and resubmit — the Gate does not auto-merge.

### Data flow: read path

```text
Agent → MCP/A2A → Protocol Adapter
  → Adaptive Query Router
    → Simple fact: single retrieval pass
    → Complex reasoning: multi-hop pipeline
    → Exploratory: broad graph traversal
    → No retrieval needed: skip
  → Hybrid Candidate Retrieval (parallel)
    → Dense vectors (pgvector cosine similarity)
    → Sparse BM25 (Postgres full-text search)
    → KG traversal (Personalized PageRank, Phase 2)
  → Validation & Filtering
    → Temporal validity check
    → Access control check
    → Confidence threshold
    → Self-RAG relevance reflection
  → Memory Distillation (RL-trained, Phase 3)
  → Conflict Resolution + Assembly
  → Response with provenance metadata
```

### CLS consolidation flow

```text
Fast Path (hippocampal):
  New records land immediately
  High fidelity, episode-specific, queryable immediately
  Subject to rapid decay if not reinforced

Slow Path (neocortical):
  Promoted by consolidation engine over time
  Generalized, abstracted, cross-referenced
  Extremely durable

Consolidation triggers:
  - Scheduled: nightly deep, hourly light
  - Event-driven: related memories accumulate past threshold
  - Pressure-driven: fast path memory pressure elevated
```

### Schema definitions

Full schema definitions are a separate artifact
(`docs/design/schemas/`) per STD-055. Key schemas to define:

- `memory_records` table (all 8 types in one table, discriminated by type)
- `memory_versions` table (append-only version history)
- `memory_edges` table (knowledge graph relationships, designed Phase 1,
  populated Phase 2)
- `librarian_audit` table (gate decisions)
- `librarian_queue` table (pending approvals)
- `agent_registry` table (token-based identity)

## Non-Functional Requirements

### Performance and scalability

**Phase 1 targets (single-node, < 100K records)**:

| Metric | Target | Measurement |
|---|---|---|
| Retrieval latency (p95) | < 2 seconds (10 results, 100K corpus) | Benchmark script |
| Embedding generation | < 500ms per record (CPU) | Benchmark |
| Write latency (Gate approval) | < 200ms (auto-approve path) | Structured logging |
| Memory footprint | < 4GB RSS under normal load | Process monitoring |
| Cold start | < 30 seconds (application + migrations) | Timer |

**Scalability path**:

- Phase 1: pgvector handles up to ~500K records (ADR-003 ceiling
  estimate)
- Phase 2: Knowledge graph on NetworkX (in-memory, up to ~1M edges)
- Phase 3+: If scale exceeds ceilings, migrate to dedicated services
  (Qdrant for vectors, Neo4j for graph) via adapter interfaces
- CPU-bound embedding work bulkheaded via `ProcessPoolExecutor`
  (ADR-001)

### Availability and reliability

- **Target**: Development environment, no formal SLA
- **Durability**: Zero data loss on clean shutdown/restart (PostgreSQL
  WAL)
- **Self-healing**: Autonomous corrective action for metric degradation
  (Phase 3)
- **Circuit breakers**: aiobreaker at module boundaries (ADR-001)
- **Retries**: tenacity with exponential backoff at infrastructure
  adapters (ADR-001)

### Observability expectations

| Layer | Tool | Output |
|---|---|---|
| Application logging | `structlog` (JSON) | Structured logs per ADR-005 |
| Metrics | Prometheus client | Counters, histograms, gauges |
| Tracing | OpenTelemetry (future) | Distributed traces when multi-service |
| Health | `/health` endpoint | Component-level health checks |

Key metrics to instrument from day one:

- Retrieval hit rate, precision, latency (p50/p95/p99)
- Gate approval/rejection rate, queue depth
- Memory record counts by type, consolidation path
- Agent connection count, request rate
- Embedding generation latency

## Security and Risk Considerations

### Threat considerations

Per STD-007, threat analysis is distributed across module designs
(`docs/design/module-*.md`), where each module documents its specific
assets, trust boundaries, attack vectors, and mitigations. Key
system-level threat areas:

- **Prompt injection via memory content**: Stored records could contain
  adversarial content. Mitigation: content sanitization in Gate,
  type-specific validation, agent trust scoping.
- **Gate bypass**: Any path that writes to storage without Gate approval
  is a critical vulnerability. All writes — external (agent) and
  internal (consolidation, self-healing) — route through the Gate with
  decision type tracking. Mitigation: database-level permissions,
  integration tests, static analysis (no raw inserts outside Gate).
- **Token theft/replay**: Agent tokens provide persistent identity.
  Mitigation: token rotation, revocation via CLI, connection auditing.
- **Data exfiltration via A2A**: Malicious agents could query sensitive
  records. Mitigation: access control levels, agent trust tiers,
  rate limiting.

### Authentication and authorization

**Access control levels (5 tiers)**:

| Level | Visibility | Example |
|---|---|---|
| Public | All connected agents | Project architecture decisions |
| Agent-scoped | Specific agents (by token) | Agent-specific preferences |
| User-only | Human operator only | Security-sensitive notes |
| System | Kernel internals only | Health metrics, training data |
| Sensitive | Requires explicit consent | PII, credentials references |

**Agent trust levels (4 tiers)**:

| Level | Write access | Gate evaluation | Example |
|---|---|---|---|
| Trusted | All types, higher confidence floor | Standard | Claude Code (primary agent) |
| Standard | Most types | Standard | Cursor, Cline |
| Restricted | Limited types, stricter policies | Enhanced scrutiny | New/unknown agents |
| Read-only | Cannot write | N/A | Monitoring tools |

**Identity model**: Token-based persistent identity issued on first
agent registration. Trust level assigned by user on first connect.
Default to Restricted if user does not respond within 1 hour.

### Key risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Librarian Gate bypass via bug | Data corruption | Integration tests, static analysis, red-team review |
| A2A spec breaking changes (pre-1.0) | Interface rewrites | Adapter pattern, SDK pinning (ADR-002) |
| Embedding model quality degradation | Poor retrieval | Adapter interface for swaps, evaluation metrics (ADR-007) |
| Solo developer blind spots | Design flaws | AI red-team, Quint tracking, governance framework |
| RL advisor training data poisoning (Phase 3) | Bad gate decisions | Hard constraint layer never overridden by RL |

### PII screening model

PII detection in the Librarian Gate Layer 1 is **best-effort screening,
not a hard constraint**. The distinction matters:

- **Phase 1**: Regex-based pattern matching catches structured PII
  (emails, phone numbers, SSNs, credit card numbers). It will miss
  contextual PII embedded in narrative text (e.g., names in episode
  content, addresses described conversationally).
- **Phase 2+**: Upgrade to NER-based detector (e.g., Presidio, spaCy)
  for improved recall on unstructured content.

**Compensating controls** (all phases):

1. **Quarantine by default**: Records flagged as potentially containing
   PII are stored with `access_level = sensitive` pending review, rather
   than silently approved at a lower access level.
2. **Periodic batch rescan**: Scheduled job re-scans stored records with
   the current PII detector. Records flagged retroactively are promoted
   to `sensitive` access level.
3. **PII propagation tracking**: If a source record is flagged as
   containing PII, all `derived_from` descendants in the consolidation
   chain are also promoted to `sensitive`.
4. **Scoped definition**: For this system (single-user development
   tool), "PII" is scoped to: email addresses, phone numbers,
   government IDs, financial account numbers, and API keys/secrets.
   Names and locations in project context are not treated as PII unless
   the user configures stricter rules.

The Gate's hard constraints (never overridden by RL) are: schema
validation, access control enforcement, rate limiting, and
classification rules. PII screening feeds into classification but is
acknowledged as probabilistic.

## Success Metrics and Instrumentation

### Retrieval quality metrics

| Metric | Definition | Target |
|---|---|---|
| Hit rate | % of queries returning at least one useful result | > 90% |
| Precision | % of returned results rated useful by agents | > 80% |
| Latency (p95) | Time from query to validated results | < 2s |
| Conflict rate | % of queries surfacing contradictions | < 5% |
| Miss rate | How often agents report "missing" expected memories | < 10% |

### Memory health metrics

| Metric | Definition | Target |
|---|---|---|
| Memory pressure | Storage utilization across fast/slow paths | < 80% |
| Staleness index | % of records not accessed in 90 days | < 30% |
| Consolidation ratio | Compression achieved by consolidation | > 2:1 |
| Write quality | % of Gate approvals that lead to retrieved memories | > 60% |
| Gate enforcement | % of write operations with audit trail | 100% |

### Agent satisfaction metrics

| Metric | Definition | Target |
|---|---|---|
| Feedback score | Aggregated useful/partial/miss signals | > 0.8 (1.0 scale) |
| Context relevance | How often retrieved context improves agent output | Trending up |
| Progressive feeding | Time for new agent to reach useful context | < 5 minutes |

### Instrumentation plan

All metrics collected via `structlog` fields and Prometheus client
library. Self-eval metrics computed on Tier 3 background schedule
(Phase 2+). Dashboard delivery via CLI initially, web UI in Phase 4.

### Owners and review window

- **Owner**: Mark (sh4i-yurei)
- **Review window**: Monthly metric review; quarterly threshold
  re-calibration

## Progressive Delivery and Rollback Strategy

### Rollout approach

Five-phase progressive delivery. Each phase is independently valuable
and deployable:

1. **Phase 1**: Core kernel — agents can write and query memories.
   Minimum viable product.
2. **Phase 2**: Intelligence layer — retrieval quality jumps via
   HippoRAG and consolidation. Existing data is preserved.
3. **Phase 3**: Self-improvement — kernel learns from usage. Existing
   heuristics remain as fallback.
4. **Phase 4**: Jarvis mode — dev environment integration. Existing
   memory operations unaffected.
5. **Phase 5**: Evolution — advanced optimization. Existing capabilities
   stable.

### Rollback triggers and plan

| Trigger | Action |
|---|---|
| Database migration failure | Alembic `downgrade` to previous revision |
| RL advisor degrades gate quality (Phase 3) | Disable RL advisor, fall back to heuristic rules |
| Retrieval quality drops below threshold | Revert retrieval weights, rebuild index |
| New component causes instability | Disable via feature flag, revert to previous phase behavior |

### Constraints

- Database migrations must be reversible (Alembic up/down)
- RL components always have a heuristic fallback
- Feature flags gate all Phase 2+ components
- No destructive schema changes; additive only until stable

## Failure Scenarios and Mitigations

### Critical failure scenarios

| Symptom | Diagnosis | Auto-Repair (Phase 3+) | Manual Fallback |
|---|---|---|---|
| Retrieval hit rate dropping | Embedding drift or index fragmentation | Re-embed affected records, rebuild index partitions | Manual re-index via CLI |
| Retrieval latency increasing | Index bloat or inefficient query paths | Prune unused index entries, optimize hot paths | Reduce top-k, disable graph traversal |
| High conflict rate | Contradictory information accumulating | Batch conflict resolution, escalate unresolvable | Manual review via `engram librarian review` |
| Memory pressure elevated | Too much data in fast path | Aggressive consolidation, archive decayed records | Manual archive via CLI |
| Agent feedback declining | Retrieval strategy misaligned with usage | Adjust retrieval path weights, retrain RL distiller | Reset weights to defaults |
| Gate approval rate too high | Policies too permissive | Tighten confidence thresholds | Update policy YAML |
| Gate approval rate too low | Policies too strict | Relax thresholds, escalate for review | Update policy YAML |
| PostgreSQL connection failure | Infrastructure issue | Circuit breaker trips, retry with backoff | Restart database |
| Embedding generation timeout | Model or resource issue | Retry with backoff, skip embedding (degraded mode) | Switch embedding model |

### Escalation policy

1. Auto-repair attempted (Phase 3+)
2. If auto-repair fails, notification sent to user
3. User resolves via CLI or approves suggested fix
4. Resolution logged in audit trail

## Design Governance and Approvals

### Decision owner

**Mark (sh4i-yurei)** — sole approver for all design artifacts,
specifications, and architectural decisions.

### Required approvals

| Artifact | Approver | Gate |
|---|---|---|
| System design (this document) | Mark | Architecture Approval (STD-032) |
| Module designs | Mark | Design Approval |
| Technical specifications | Mark | Specification Approval |
| ADRs | Mark | Quint FPF validation |

### AI red-team review

Required for this system design per STD-032 Tier 3. Focus areas:

- Failure modes: What breaks, when, how?
- Data integrity: Corruption vectors, validation gaps
- Security: Authorization bypass, injection, leakage
- Operational risks: Deadlock, resource exhaustion, cascading failures

Red-team findings recorded in Quint.

### Amendment process

Per STD-020:

- Scope changes require charter amendment (PR + changelog + version bump)
- Design changes require system design amendment (same process)
- All amendments tracked via Quint
- 24-hour cooling period before implementation changes

## Assumptions and Constraints

### Assumptions

| ID | Assumption | Validation |
|---|---|---|
| A1 | PostgreSQL + pgvector sufficient for < 500K records | Benchmark at Phase 1 completion |
| A2 | fastembed (CPU) provides adequate retrieval quality | Evaluation metrics, swap via adapter if not |
| A3 | API key auth acceptable for local development | Revisit at production planning |
| A4 | English-only content | No i18n in scope |
| A5 | A2A v0.3 stable enough for integration | Adapter pattern mitigates breaking changes |
| A6 | NetworkX handles KG at prototype scale | Neo4j migration path if exceeded (Phase 2) |
| A7 | Single user (Mark) for all phases through Phase 4 | Multi-user deferred to Phase 5 |
| A8 | RL training data accumulates sufficiently by Phase 3 | Log all interactions from Phase 1 |

### Constraints

| ID | Constraint | Source |
|---|---|---|
| C1 | Python 3.12 | Charter |
| C2 | WSL2 development environment | Charter |
| C3 | Single-node deployment (Docker Compose) | Charter |
| C4 | Solo developer | Charter |
| C5 | Design-first: no implementation code before approved spec | STD-020, Charter |
| C6 | All architectural decisions tracked in Quint | Charter |
| C7 | KB templates for all governed artifacts | STD-056, Charter |
| C8 | No external API calls for embeddings (local-first) | v2 axiom 1 |

## Out-of-Scope Considerations

### Explicit exclusions

- **Source code self-modification**: The kernel adjusts its own
  hyperparameters and swaps components within its infrastructure layer,
  but does not rewrite its own source code. That is Darwin Godel
  Machine territory and not realistic for this system.

- **Multi-user / multi-tenant**: All Phase 1-4 work assumes single user.
  The `user_id` field is present on records from day one to enable
  Phase 5 multi-user without schema migration, but no isolation,
  quotas, or RBAC are implemented.

- **Mobile / desktop client apps**: Phase 4 defines delivery channels
  (push notifications, desktop notifications), but the client
  applications themselves are separate projects with their own design
  processes.

- **Production Kubernetes deployment**: Docker Compose on localhost is
  the deployment target through Phase 4. Cloud deployment is a Phase 5
  concern.

- **Custom model training**: The kernel uses pre-trained models only. No
  fine-tuning of LLMs or embedding models.

- **Non-English content**: Embedding models and retrieval are optimized
  for English only.

### Extension points

The adapter-based architecture (ADR-001, ADR-007) provides explicit
extension points. Interfaces marked "Designed" have Protocol definitions
in the module designs. Interfaces marked "Candidate" are architecturally
supported by the existing patterns but require design work before
implementation.

| Extension point | Interface | Status | Phase | Notes |
|---|---|---|---|---|
| Embedding model | `EmbeddingAdapter` Protocol | Designed | 1 | ADR-007; FastembedAdapter default |
| Graph backend | `GraphAdapter` Protocol | Designed | 2 | ADR-009; NetworkX default, Neo4j path |
| Vector storage | Via `EmbeddingAdapter` | Seam exists | Future | ADR-003 ceiling triggers migration |
| Event transport | `EventBus` Protocol | Designed | 1 | Outbox default; Kafka/Redis swappable |
| Agent roles | `AgentRole` Protocol | Designed | 1 | ADR-008; new roles implement Protocol |
| Document ingestion | Not yet designed | Candidate | 2+ | Docling, Markitdown, git history import |
| Notification channels | Not yet designed | Candidate | 2+ | Slack, email, desktop beyond webhook |
| Custom memory types | Not yet designed | Candidate | 5 | Plugin system per Phase 5 scope |
| Retrieval strategies | Not yet designed | Candidate | 2+ | Custom search beyond vector/BM25/graph |
| Gate policies | Not yet designed | Candidate | 2+ | Custom approval rules beyond built-in |

All extension points share one invariant: **writes go through the
Librarian Gate**. Any new ingestion source, agent role, or automation
trigger produces records that enter the standard Gate approval flow.

## Links

- **Module designs**: `docs/design/module-*.md` (pending)
- **Technical specification**: `docs/specs/technical-specification.md` (pending)
- **Schema definitions**: `docs/design/schemas/` (pending)
- **Threat analysis**: Distributed across module designs per STD-007
- **SLI/SLO**: `docs/operations/sli-slo.md` (pending)
- **Risk register**: `docs/governance/risk-register.md` (pending)
- **ADRs**: `docs/architecture/adr/ADR-001-monolith-first.md` through
  `ADR-012-hybrid-librarian-gate.md`
- **Options analyses**: `docs/architecture/options-analysis-architecture.md`,
  `docs/architecture/options-analysis-protocols.md`
- **PRD**: `docs/planning/requirements-prd.md`
- **Charter**: `docs/governance/project-charter.md`
- **Roadmap**: `docs/planning/project-roadmap.md`
- **v2 feature specification**: Design input (not a governed artifact);
  synthesized into this system design

# Implementation Notes

- All 15 required sections per STD-021 are present.
- Phase 1 scope is the MVP; later phases are architecturally defined to
  prevent migration barriers.
- The v2 feature specification is raw design input. This system design is
  the governed authority. Where they differ, this document governs.
- Module designs will decompose each subsystem into detailed component
  designs per STD-022.
- Schema definitions will follow STD-055 and are linked from section 7.
- Import boundaries between packages are enforced by `import-linter` and
  defined in section 5.

# Continuous Improvement and Compliance Metrics

## Design quality metrics

- **Section completeness**: All 15 STD-021 sections populated (target:
  100%)
- **Traceability**: Every v2 subsystem maps to a system design component
  (target: 100%)
- **ADR coverage**: Every architectural decision linked to an ADR
  (target: 100%)
- **Review completion**: AI red-team pass recorded in Quint (target: 1)

## Post-approval tracking

- Module designs must reference this system design by section
- Technical specifications must trace to system design components
- Implementation PRs must cite the governing design section
- Quarterly review of assumptions (A1-A8) against observed reality

# Compliance

This document complies with:

- **STD-001** (Documentation Standard): All mandatory sections present
  (Purpose, Scope, Standard, Implementation Notes, Continuous
  Improvement, Compliance, Changelog).
- **STD-021** (System Design Standard): All 15 required sections
  populated per template.
- **STD-020** (Design-First Development): System design precedes module
  design and specification.
- **STD-032** (SDLC With AI, Tier 3): Design phase artifact, AI
  red-team review required before approval.

Downstream standards applicable to implementation:

- **STD-004** (AI Assisted Development): Constrains AI-generated code;
  all implementation requires human review.
- **STD-005** (Coding Standards and Conventions): Python conventions,
  naming, formatting rules for implementation phase.

Verified by: sh4i-yurei (draft — pending review)
Date: 2026-02-13

# Changelog

## 0.1.0 — 2026-02-13

**Added:**

- Initial system design synthesizing v2 feature specification with
  M1/M2 artifacts (PRD, charter, ADRs 001-006)
- All 15 STD-021 required sections populated
- Four-layer architecture model (User, Agent, Kernel, Infrastructure)
- Four kernel subsystems (Memory, Retrieval, Autonomy, Dev Environment)
- 8 memory types with record envelope schema
- Hybrid Librarian Gate architecture (declarative rules + RL advisor)
- HippoRAG-inspired 6-stage retrieval pipeline
- CLS dual-path consolidation model
- 5-phase progressive delivery plan
- Failure scenario table with auto-repair actions
- Success metrics with targets for retrieval, memory health, and agent
  satisfaction
- Security model with 5 access levels and 4 agent trust tiers
- Project structure mapping subsystems to Python packages
- ADR supersession plan (004, 005, 006 → 007, 008, 009) and new ADRs
  (010-012)

**Status**: Draft — pending AI red-team review and approval

## 0.1.1 — 2026-02-13

**Fixed** (AI red-team findings C-1, C-2, C-3):

- C-1: Defined internal write path through Librarian Gate for
  consolidation and self-healing writes. Added `gate_decision_type`
  field to record envelope. Consolidation writes now route through
  Gate Layer 1 (schema, PII screen, classification) with audit trail.
- C-2: Added optimistic concurrency control. UPDATE operations require
  `expected_version`; consolidation status transitions use
  `SELECT ... FOR UPDATE`. Version chain operations are atomic within
  a single PostgreSQL transaction.
- C-3: Reclassified PII detection from hard constraint to best-effort
  screening. Added compensating controls: quarantine-by-default,
  periodic batch rescan, PII propagation tracking through consolidation
  chains. Scoped PII definition for single-user context. Clarified
  that Gate hard constraints are schema validation, access control,
  rate limiting, and classification rules.
- Added downstream standards (STD-004, STD-005) to Compliance section.

## 0.1.3 — 2026-02-13

**Added:**

- Extension points table in Out-of-Scope Considerations documenting
  designed adapter interfaces and candidate extension points for future
  phases (document ingestion, notification channels, custom memory types,
  retrieval strategies, Gate policies).

## 0.1.2 — 2026-02-13

**Changed:**

- Replaced standalone threat model reference
  (`docs/operations/threat-model.md`) with distributed threat analysis
  across module designs per STD-007.
- Updated links section to reflect embedded threat approach.
