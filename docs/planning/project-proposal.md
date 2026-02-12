---
id: 3NGRAM-PROP-001
title: "3ngram: Agentic RAG Memory System — Project Proposal"
version: 0.1.0
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-032, STD-033, STD-054]
tags: [proposal, planning, 3ngram, memory, rag, a2a, architecture]
---

# Purpose

Propose the 3ngram project — an agentic RAG memory system that treats
AI memory as a kernel-governed operating system — for entry into the
Tier 3 SDLC pipeline.

# Scope

This proposal captures intent, constraints, and architectural direction
before PRD, charter, and design artifacts are produced. It gates all
downstream Tier 3 work.

# Standard

## Project proposal

### Metadata

- Project name: 3ngram
- Owner/decision maker: Mark (sh4i-yurei)
- Stakeholders: Mark (sole stakeholder)
- Target change tier: Tier 3
- Status: active
- Source links:
  - Intake: [project-intake.md](project-intake.md)
  - Predecessor: [ai_tech_stack](https://github.com/sh4i-yurei/ai_tech_stack) (deprecated)
  - Obsidian vault design notes: /mnt/d/ai_knowledge/

### Purpose / concept summary

3ngram is a kernel-governed memory OS for AI agents. It replaces the
pattern of "RAG as a library" with "memory as a first-class runtime
substrate" enforced by mandatory invariants.

**Primary use cases:**

1. **Persistent agent memory**: An AI agent (Claude Code, custom A2A
   agent) stores decisions, beliefs, episodes, and skills as typed,
   versioned records that survive across sessions.
2. **Agentic retrieval**: Rather than naive top-k vector search, the
   system runs a 6-stage retrieval pipeline: plan, hybrid retrieve,
   rerank, validate (provenance, contradictions, temporal validity),
   bounded retry, and assemble.
3. **Policy-gated durability**: The Librarian gate ensures no memory
   becomes durable without authorization — preventing memory poisoning,
   hallucination persistence, and unreviewed knowledge drift.
4. **Agent-to-agent delegation**: Via A2A protocol, external agents can
   discover 3ngram's capabilities (Agent Card), delegate research tasks,
   and receive streamed results.
5. **Tool integration**: Via MCP, agents like Claude Code can call
   memory operations (store, retrieve, search, validate) as standard
   tool calls.

**Key outcomes:**

- A running local memory system that Claude Code can use as an MCP
  server for persistent, validated memory.
- A2A-compatible endpoint that other agents can discover and delegate
  to.
- Operational governance — not aspirational governance. Every invariant
  is enforced in code, not just documented.

### Landscape and limitations

**Current state**: The `ai_tech_stack` repository attempted to build a
unified agentic AI platform. It is deprecated as of 2026-01-10 due to:

1. **Over-architecture**: 7 Docker services (Qdrant, Meilisearch,
   Postgres, Redis, n8n, RAG service, agent service) from day one.
   Complexity grew faster than value.
2. **Fragile embedding layer**: SentenceTransformers crashed silently,
   forcing an emergency migration to fastembed.
3. **Untested integrations**: No integration tests. UMC (Unified Memory
   Context) was wired everywhere but reliable nowhere — silent failures,
   null-object fallbacks.
4. **Aspirational governance**: A governance agent directory existed but
   barely worked. Standards were documented but not enforced in code.
5. **Documentation drift**: Docs described features that didn't exist
   (Raspberry Pi cluster, Phase III hardware).

**Known constraints:**

- WSL2 Ubuntu environment (no native Linux).
- RTX 3070 GPU available. Default to fastembed (CPU) for simplicity;
  GPU-accelerated models are an option if retrieval quality demands it.
- Solo developer — no team review capacity.
- A2A protocol is pre-1.0 (v0.3), evolving rapidly.

**Existing alternatives considered:**

- **Mem0**: Service-centric, no kernel-level invariants, self-healing
  not mandatory. Useful algorithms to port as adapters.
- **Supermemory**: Infrastructure service, doesn't enforce system-wide
  retrieval validation or agent role coherence.
- **LangChain memory**: Too tightly coupled to LangChain abstractions.
  Not protocol-native.

All share the same limitation: memory as a library bolt-on, not a
governed runtime.

### Proposed architecture (high level)

**Design principle**: Monolith-first. One Python FastAPI service with
clear internal module boundaries. Extract to services only when
justified by real bottlenecks.

**Core subsystems:**

1. **Memory Kernel** — Typed records (Decision, Belief, Episode, Skill)
   with temporal awareness, versioning, and supersession tracking.
   Postgres for durable state, Qdrant for vector representations.

2. **Retrieval Engine** — 6-stage agentic retrieval: Plan, Hybrid
   Retrieve (vector + keyword), Rerank, Validate (provenance, temporal,
   contradictions), Bounded Retry, Assemble. Fastembed for embeddings.

3. **Librarian Gate** — Policy enforcement layer. All durable memory
   writes require Librarian authorization. Audit trail for every
   decision. Configurable auto-approval policies for low-risk writes.

4. **MCP Endpoint** — Exposes memory operations (store, retrieve,
   search, validate, list) as MCP tools. Compatible with Claude Code
   and any MCP client.

5. **A2A Endpoint** — Agent Card served at
   `/.well-known/agent-card.json`. Task lifecycle (send, stream, get,
   cancel). Skills declared for research, memory storage, and retrieval.
   JSON-RPC 2.0 + SSE transport per A2A v0.3 spec.

6. **Researcher Agent Role** — First implemented agent role. Receives
   research queries, executes retrieval pipeline, validates results,
   returns cited responses. Demonstrates end-to-end system capability.

**Key integrations:**

- A2A Python SDK (`a2a-sdk`) for protocol compliance.
- MCP SDK for tool serving.
- Postgres 16 for relational state.
- Qdrant for vector search.
- fastembed for embeddings (CPU default; GPU models available via RTX 3070).
- Docker Compose for local development.

**Decisions requiring options analysis and ADRs:**

- ADR-001: Monolith-first vs microservices architecture.
- ADR-002: Dual protocol strategy (MCP + A2A coexistence).
- ADR-003: Storage backend selection (Postgres + Qdrant).
- ADR-004: Embedding model selection (fastembed).
- ADR-005: Agent role architecture (internal modules vs services).
- ADR-006: Knowledge graph approach (defer vs integrate).

### Deliverables (required before implementation)

Per Tier 3 ceremony (STD-032):

- [x] Project intake: [project-intake.md](project-intake.md)
- [x] Project proposal: this document
- [x] PRD: [requirements-prd.md](requirements-prd.md)
- [x] Project charter: [project-charter.md](../governance/project-charter.md)
- [x] Project roadmap: [project-roadmap.md](project-roadmap.md)
- [x] Backlog/milestones: [backlog-milestones.md](backlog-milestones.md)
- [ ] Architecture options analyses: [docs/architecture/](../architecture/)
- [ ] ADRs (001-006): [docs/architecture/adr/](../architecture/adr/)
- [ ] System design: [system-design.md](../design/system-design.md)
- [ ] Module designs: docs/design/module-*.md
- [ ] Threat model: [threat-model.md](../operations/threat-model.md)
- [ ] SLI/SLO targets: [sli-slo.md](../operations/sli-slo.md)
- [ ] Risk register: [risk-register.md](../governance/risk-register.md)
- [ ] Technical specification: [technical-specification.md](../specs/technical-specification.md)
- [ ] Schema definitions: [docs/design/schemas/](../design/schemas/)
- [ ] Design review (red-team pass)

### Risks and dependencies

**Risks:**

- A2A protocol instability: Pre-1.0 spec may introduce breaking changes.
  Mitigation: Adapter pattern, pinned SDK version, version negotiation.
- Scope creep: The vision (from Obsidian vault notes) is expansive —
  5 agent roles, knowledge graph, workspace adapter, CLI gateway.
  Mitigation: Strict MVP boundary. This proposal explicitly defers
  everything beyond the 6 core subsystems listed above.
- Solo developer bottleneck: No peer review capacity. All design and
  code review is self + AI-assisted.
  Mitigation: AI red-team pass on designs. Quint decision tracking for
  auditability. KB governance for consistency.
- Embedding model risk: fastembed is lightweight but may lack accuracy
  for domain-specific retrieval.
  Mitigation: Adapter interface allows swapping models. Evaluation
  metrics in retrieval pipeline.

**Dependencies:**

- policies-and-standards KB (v2.0.0) for templates and CI workflows.
- Docker Desktop with WSL2 integration.
- GitHub (repository hosting, CI/CD via Actions).
- PyPI packages: a2a-sdk, fastapi, qdrant-client, fastembed.

### Success criteria and metrics

**Success criteria:**

1. A Claude Code session can connect to 3ngram via MCP and store/retrieve
   memories that persist across sessions.
2. An external A2A client can discover 3ngram's Agent Card, send a
   research task, and receive a streamed response with citations.
3. The Librarian gate demonstrably prevents unauthorized durable writes
   (tested with both approved and rejected write attempts).
4. Retrieval results include provenance metadata and confidence scores.
5. All design artifacts pass KB compliance checks (frontmatter, links,
   sections, spelling).

**Metrics:**

- Retrieval latency: p95 under 2 seconds for hybrid search.
- Memory durability: Zero data loss on clean shutdown/restart.
- Librarian gate accuracy: 100% enforcement (no bypass paths).
- A2A protocol compliance: Pass TCK (Test Compatibility Kit) from
  a2a-sdk.

**SLI/SLO alignment:** To be defined in docs/operations/sli-slo.md
during design phase.

### Next steps

1. Draft PRD with detailed functional and non-functional requirements.
2. Draft project charter establishing design governance.
3. Draft project roadmap with milestones.
4. Conduct architecture options analyses for major decisions.
5. Record ADRs for each architectural decision.
6. Proceed through system design, module designs, and specification.
7. Coordinate AI-assisted red-team review on system design.
8. Track decisions in Quint (FPF lifecycle).

# Implementation Notes

- This proposal is deliberately high-level. Detailed architecture lives
  in the system design document.
- The deliverables checklist should be updated as artifacts are completed.

# Continuous Improvement and Compliance Metrics

- Track whether all listed deliverables are completed before
  implementation begins.
- Capture feedback on missing sections to improve the template.

# Compliance

Proposals that omit required sections, links, or metadata are
non-compliant until corrected. This proposal satisfies TPL-PRJ-PROP
(v0.1.7).

# Changelog

- 0.1.0 — Initial proposal for 3ngram project.
