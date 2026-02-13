---
id: 3NGRAM-ADR-010
title: "ADR-010: CLS-inspired dual-path memory consolidation"
version: 0.1.0
category: architecture
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-047]
tags: [adr, architecture, consolidation, cls, memory, 3ngram]
---

## 1. Purpose

Record the decision to adopt a Complementary Learning Systems (CLS) inspired dual-path architecture for memory consolidation, preventing memory bloat and improving retrieval quality through biological-inspired memory management.

## 2. Scope

This decision applies to the memory lifecycle management layer of 3ngram. It governs how memories transition from fast (high-fidelity, recent) storage to slow (consolidated, durable) storage, including consolidation triggers, actions, and scheduling. Phase 2 implementation.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-010 |
| Status | Accepted |
| Date | 2026-02-13 |
| Deciders | sh4i-yurei |

### 3.2 Context

As 3ngram accumulates memories over time, retrieval quality degrades due to noise -- redundant episodes, outdated beliefs, verbose records that bury key information. Biological memory systems solve this through consolidation: the hippocampus stores recent experiences at high fidelity, while the neocortex gradually integrates them into generalized, durable knowledge.

The Complementary Learning Systems theory (Go-CLS, Nature 2023) provides a well-studied model for this dual-path approach. Applying CLS principles to 3ngram means memories are stored immediately in a fast path and consolidated over time into a slow path, reducing noise and improving retrieval relevance.

Without consolidation, memory stores grow unbounded, retrieval becomes slower, and the signal-to-noise ratio decreases monotonically.

### 3.3 Decision Drivers

- **Memory bloat prevention** -- unbounded memory growth degrades retrieval quality and increases storage costs
- **Retrieval quality** -- consolidated memories are more relevant and less noisy than raw episode logs
- **Biological plausibility** -- CLS is a well-studied model with known benefits for knowledge systems
- **Phased implementation** -- consolidation is complex; it should build on Phase 1 foundations (memory types, edges)
- **Reversibility** -- original memories must be preserved; consolidation produces new records, not in-place mutations

### 3.4 Options

#### Option A: CLS-inspired dual-path consolidation

Two storage paths: fast (hippocampal) for immediate, high-fidelity storage with temporal decay, and slow (neocortical) for consolidated, generalized, durable storage. Consolidation runs on multiple trigger types. Original memories are preserved with a `consolidated_into` edge; consolidated memories reference their sources via `derived_from` edges.

#### Option B: Simple TTL-based expiration

Memories expire after a configurable time-to-live. Simple to implement but loses valuable information. No generalization or knowledge synthesis.

#### Option C: Manual curation only

The Librarian flags memories for review; a human or agent decides what to keep. Does not scale and does not improve retrieval quality automatically.

### 3.5 Decision

**Option A -- CLS-inspired dual-path consolidation.**

**Fast path (hippocampal):**

- Immediate storage of all memory writes at full fidelity
- Subject to temporal decay -- relevance score decreases over time unless reinforced by retrieval
- High recall, low precision (everything is kept initially)

**Slow path (neocortical):**

- Consolidated over time from fast-path memories
- Generalized, compressed, and highly durable
- High precision, lower recall (only validated knowledge persists)

**Consolidation triggers:**

1. **Scheduled** -- nightly deep consolidation (full sweep), hourly light consolidation (recent memories only)
2. **Event-driven** -- when related memories accumulate past a threshold (e.g., 5+ episodes about the same topic)
3. **Pressure-driven** -- when fast-path memory count exceeds a configured limit

**Consolidation actions:**

- Merge related episodes into narrative summaries
- Promote repeated observations to beliefs (with confidence scores)
- Extract skills from episode patterns (e.g., recurring successful approaches)
- Compress verbose records while preserving key information
- Create `derived_from` edges from consolidated memories to their sources
- Create `supersedes` edges when a consolidated memory replaces older versions

**Reversibility:** Original memories are never deleted during consolidation. They are marked with a `consolidated` status and linked via edges. Rollback is possible by following `derived_from` edges back to sources.

### 3.6 Consequences

**Positive:**

- Memory stores remain manageable as usage grows -- consolidation prevents unbounded growth
- Retrieval quality improves over time as noise is reduced and knowledge is generalized
- Biological plausibility means the approach is well-studied with known failure modes
- Reversibility preserves original data for audit and rollback
- Knowledge graph edges (ADR-009) provide the relationship context needed for intelligent consolidation

**Negative:**

- Consolidation logic is complex and requires careful testing to avoid information loss; mitigated by reversibility and phased rollout
- Scheduled jobs add operational complexity; mitigated by running within the monolith (ADR-001) via asyncio scheduling
- Quality of consolidated memories depends on summarization capability; mitigated by starting with simple merge strategies and improving with RL feedback in Phase 3

**Follow-up actions:**

- Define consolidation job interfaces in the Consolidation Engine component (ADR-008)
- Design the `memory_status` enum (active, consolidated, archived) for the memories table
- Implement scheduled consolidation triggers using asyncio task scheduling
- Define quality metrics for consolidated memories (information retention, retrieval hit rate)

### 3.7 Notes and Links

- Knowledge graph: [ADR-009 Knowledge Graph Phase 2](./ADR-009-knowledge-graph-phase2.md)
- Expanded agents: [ADR-008 Expanded Agent Architecture](./ADR-008-expanded-agent-architecture.md)
- HippoRAG retrieval: [ADR-011 HippoRAG Retrieval](./ADR-011-hipporag-retrieval.md)
- Go-CLS (Nature 2023) -- Complementary Learning Systems theory applied to AI

## 4. Implementation Notes

- Consolidation Engine is an agent component (ADR-008) implementing the `AgentRole` Protocol with `on_schedule` for trigger handling
- Fast-path memories use the standard memories table with `status = 'active'`
- Consolidated memories are new records with `status = 'active'` and `derived_from` edges to source memories
- Source memories transition to `status = 'consolidated'` and are excluded from default retrieval (but queryable with explicit flag)
- Temporal decay function: `relevance = base_relevance * exp(-lambda * days_since_last_access)` where `lambda` is configurable per memory type
- Consolidation batch size is configurable (`ENGRAM_CONSOLIDATION_BATCH_SIZE`, default 100)
- Nightly deep consolidation runs at a configurable hour (`ENGRAM_CONSOLIDATION_HOUR`, default 3 AM UTC)

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Fast-path memory count | < 10,000 active | Continuous monitoring |
| Consolidation job duration | < 30 minutes (nightly) | Per run |
| Information retention rate | > 95% (key facts preserved) | Monthly evaluation |
| Retrieval quality improvement post-consolidation | > 10% precision gain | Quarterly evaluation |

Review this ADR when any of these signals appear:

- Consolidation job duration exceeds 1 hour consistently
- Information loss is detected in consolidated memories (user complaints or evaluation metrics)
- RL feedback (Phase 3) suggests different consolidation strategies
- Memory volume exceeds 100k records and consolidation scheduling needs optimization

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-047 (Architecture Decision Workflow) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted CLS-inspired dual-path memory consolidation for Phase 2
