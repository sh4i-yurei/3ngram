---
id: 3NGRAM-ADR-011
title: "ADR-011: HippoRAG-inspired retrieval pipeline"
version: 0.1.0
category: architecture
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-047]
tags: [adr, architecture, retrieval, hipporag, rl, 3ngram]
---

## 1. Purpose

Record the decision to adopt a HippoRAG-inspired 6-stage retrieval pipeline that combines dense vector search, sparse keyword search, knowledge graph traversal, and RL-trained optimization to deliver high-quality multi-hop memory retrieval.

## 2. Scope

This decision applies to the retrieval engine of 3ngram. It governs the full retrieval pipeline from query intake to result delivery, including query routing, candidate retrieval, validation, distillation, conflict resolution, and feedback collection. Phased implementation across three phases.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-011 |
| Status | Accepted |
| Date | 2026-02-13 |
| Deciders | sh4i-yurei |

### 3.2 Context

Standard RAG (retrieve top-k vectors, concatenate, send to LLM) is insufficient for 3ngram's requirements. Multi-hop queries (e.g., "What decisions were influenced by beliefs that later turned out to be wrong?") require traversing relationships between memories, not just finding the closest vectors.

The HippoRAG paper (NeurIPS 2024) demonstrates 20% improvement on multi-hop question answering benchmarks and 10-30x cost reduction compared to iterative LLM-based retrieval (e.g., IRCoT). HippoRAG achieves this by combining Personalized PageRank over a knowledge graph with standard vector retrieval, mimicking hippocampal indexing in the brain.

3ngram's memory type system and knowledge graph (ADR-009) provide the foundation for a HippoRAG-inspired pipeline adapted to the memory domain.

### 3.3 Decision Drivers

- **Multi-hop retrieval** -- standard top-k vector retrieval cannot answer queries that span multiple related memories
- **Retrieval quality** -- HippoRAG shows 20% improvement on multi-hop benchmarks
- **Cost efficiency** -- 10-30x cheaper than iterative LLM-based retrieval approaches
- **Phased delivery** -- the pipeline must be deliverable incrementally (basic retrieval in Phase 1, full pipeline in Phase 2, RL in Phase 3)
- **Bounded execution** -- retrieval must complete within SLO targets; unbounded retries are not acceptable

### 3.4 Options

#### Option A: HippoRAG-inspired 6-stage pipeline with phased delivery

Six stages delivered across three phases. Each stage is a discrete pipeline component with clear inputs and outputs. Stages can be skipped or simplified based on query complexity.

#### Option B: Standard RAG with iterative refinement

Top-k vector retrieval with optional LLM-based query expansion. Simpler but cannot handle multi-hop queries. Quality ceiling is lower.

#### Option C: Full GraphRAG (Microsoft approach)

LLM-based entity extraction at ingestion time, community detection, graph summarization. High quality but extremely expensive at ingestion time and requires LLM calls for every memory write.

### 3.5 Decision

**Option A -- HippoRAG-inspired 6-stage retrieval pipeline.**

#### Stage 1: Adaptive query routing

Classify the incoming query and select the retrieval strategy:

- `simple` -- single-hop, use vector search only
- `multi_hop` -- relationship-spanning, use vector + KG traversal
- `exploratory` -- broad discovery, use vector + keyword + KG
- `skip` -- query can be answered from cache or context

#### Stage 2: Hybrid candidate retrieval

Run retrieval strategies in parallel based on the route:

- Dense vector search via pgvector (cosine similarity)
- Sparse BM25 keyword search via Postgres full-text search
- Knowledge graph traversal via Personalized PageRank (Phase 2+, ADR-009)
- Merge candidates using Reciprocal Rank Fusion (RRF)

#### Stage 3: Validation and filtering

Apply filters to the candidate set:

- Temporal relevance (recent memories weighted higher, configurable decay)
- Access control (memory visibility rules)
- Confidence threshold (minimum confidence score)
- Self-RAG reflection -- lightweight check: "Does this candidate actually answer the query?" (Phase 2+)

#### Stage 4: Memory distillation (Phase 3)

RL-trained component that selects the optimal subset of candidates:

- Trained on outcome data (which retrieved memories were actually useful to the caller)
- GRPO/PPO reward signal from Stage 6 feedback
- Replaces heuristic ranking with learned ranking

#### Stage 5: Conflict resolution and assembly

Detect and resolve conflicts in the result set:

- Identify `contradicts` edges between candidates (ADR-009)
- Apply recency and confidence-based resolution
- Assemble the final result with provenance metadata (source memories, confidence scores, relationships)

#### Stage 6: Delivery and feedback loop (Phase 3)

Deliver results and collect feedback:

- Return results with provenance metadata
- Collect implicit feedback (was the memory used? was it helpful?)
- Feed the training signal to Stage 4 (RL distillation) and the Librarian (storage quality)

**Bounded retries:** Maximum 3 attempts with escalating strategies:

1. Standard retrieval with original query
2. Broaden -- relax filters, expand time window
3. Alternative strategy -- switch from simple to multi-hop (or vice versa)
4. Return partial results with confidence warning

### 3.6 Consequences

**Positive:**

- Multi-hop queries are supported natively, not as an afterthought
- Parallel candidate retrieval keeps latency bounded
- Phased delivery means Phase 1 ships a functional (if basic) retrieval system
- RL optimization in Phase 3 provides continuous quality improvement
- Bounded retries prevent runaway retrieval costs

**Negative:**

- 6-stage pipeline is more complex than standard RAG; mitigated by each stage being an independent, testable component
- Phase 1 retrieval is basic (vector + keyword only); mitigated by the fact that this is still functional and useful
- RL training in Phase 3 requires sufficient interaction data; mitigated by collecting feedback from Phase 1 onward

**Follow-up actions:**

- Define the `RetrievalPipeline` interface with stage composition
- Implement Stages 1-3 (basic) for Phase 1
- Design the feedback collection schema for Stage 6
- Integrate knowledge graph traversal (ADR-009) into Stage 2 for Phase 2

### 3.7 Notes and Links

- Knowledge graph: [ADR-009 Knowledge Graph Phase 2](./ADR-009-knowledge-graph-phase2.md)
- Embedding adapter: [ADR-007 Embedding Adapter](./ADR-007-embedding-adapter.md)
- Storage backend: [ADR-003 Storage Backend](./ADR-003-storage-backend.md)
- Expanded agents: [ADR-008 Expanded Agent Architecture](./ADR-008-expanded-agent-architecture.md)
- HippoRAG paper (NeurIPS 2024)

## 4. Implementation Notes

- The pipeline is implemented as a chain of async functions in `src/engram/retrieval/pipeline.py`
- Each stage is a separate module under `src/engram/retrieval/stages/` (e.g., `routing.py`, `candidates.py`, `validation.py`)
- Stage 2 parallelism uses `asyncio.gather()` for concurrent vector, keyword, and KG retrieval
- RRF fusion: `score = sum(1 / (k + rank_i))` where `k=60` (standard RRF constant)
- Query routing in Phase 1 uses a simple heuristic (keyword detection for multi-hop indicators: "why", "influenced", "related to")
- Self-RAG reflection in Phase 2 uses a lightweight LLM call to validate candidate relevance
- Retry budget is tracked per query; partial results include a `retrieval_confidence` score
- Circuit breakers (aiobreaker) wrap each stage independently; a stage failure degrades gracefully (skipped, not fatal)

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| End-to-end retrieval latency (p95) | < 500ms (Phase 1), < 1s (Phase 2) | Continuous monitoring |
| Retrieval precision at k=10 | > 0.80 (Phase 1), > 0.90 (Phase 2) | Quarterly evaluation |
| Multi-hop query success rate | > 70% (Phase 2) | Quarterly evaluation |
| Retry rate | < 10% of queries | Continuous monitoring |

Review this ADR when any of these signals appear:

- Retrieval latency consistently exceeds SLO targets
- Multi-hop query success rate is below 50% after Phase 2 deployment
- RL training data volume is sufficient to begin Phase 3 distillation
- A new retrieval approach (e.g., improved GraphRAG) shows significant quality gains in benchmarks

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-047 (Architecture Decision Workflow) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted HippoRAG-inspired 6-stage retrieval pipeline with phased delivery
