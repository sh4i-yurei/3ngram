---
id: 3NGRAM-ADR-009
title: "ADR-009: Knowledge graph in Phase 2 scope"
version: 0.1.0
category: architecture
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-047]
tags: [adr, architecture, knowledge-graph, hipporag, 3ngram]
---

## 1. Purpose

Record the decision to bring the knowledge graph into Phase 2 scope rather than deferring it indefinitely. This supersedes ADR-006, which deferred KG implementation to post-MVP. The v2 retrieval pipeline (HippoRAG-inspired) requires relationship-aware search, making KG a Phase 2 dependency rather than an optional enhancement.

## 2. Scope

This decision applies to the data model, retrieval pipeline, and memory relationship management in 3ngram. It governs the `memory_edges` table schema, edge type taxonomy, in-memory graph operations, and the migration path to a dedicated graph engine.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-009 |
| Status | Accepted |
| Date | 2026-02-13 |
| Deciders | sh4i-yurei |
| Supersedes | ADR-006 |

### 3.2 Context

ADR-006 designed the `memory_edges` schema but deferred implementation to post-MVP. The v2 system design introduces HippoRAG-inspired retrieval (ADR-011), which uses Personalized PageRank over a knowledge graph for multi-hop queries. This makes the knowledge graph a prerequisite for the full retrieval pipeline, not an optional enhancement.

Phase 1 still focuses on schema design and basic edge creation. Phase 2 brings the graph online for retrieval. This is a schedule change, not a design change -- ADR-006's schema was designed for exactly this path.

### 3.3 Decision Drivers

- **HippoRAG dependency** -- multi-hop retrieval (ADR-011) requires graph traversal via Personalized PageRank
- **Consolidation dependency** -- the Consolidation Engine (ADR-008) needs relationship context to merge related memories
- **Conflict detection** -- the `contradicts` edge type is essential for the Librarian's conflict resolution logic
- **ADR-006 readiness** -- the schema is already designed; what changes is the implementation timeline
- **Phase 2 feasibility** -- NetworkX for in-memory graph operations is lightweight and well-understood

### 3.4 Options

#### Option A: Phase 2 implementation with NetworkX prototyping

Phase 1: Design `memory_edges` table schema and include in initial migration. Create edges during Librarian write operations (basic: `supersedes`, `relates_to`). Phase 2: Load edges into NetworkX for in-memory graph operations (PageRank, shortest path, community detection). Future: Neo4j migration via adapter interface when scale demands it.

#### Option B: Keep ADR-006 timeline (post-MVP, indefinite)

Defer as originally planned. HippoRAG retrieval operates without graph traversal in Phase 2, using only vector and keyword search. Reduces Phase 2 scope but limits retrieval quality.

#### Option C: Full Neo4j integration in Phase 2

Skip the NetworkX prototyping step and go directly to Neo4j. Higher quality but adds operational complexity (separate database to manage).

### 3.5 Decision

**Option A -- Phase 2 implementation with NetworkX prototyping.**

The `memory_edges` table schema from ADR-006 is implemented in Phase 1 migrations:

- `id` -- UUID primary key
- `source_id` -- FK to memories table
- `target_id` -- FK to memories table
- `edge_type` -- enum: `supersedes`, `supports`, `contradicts`, `relates_to`, `derived_from`, `similar_to`
- `weight` -- float, edge strength (0.0 to 1.0)
- `metadata` -- JSONB for edge-specific attributes
- `created_at` -- timestamp

Edge type `similar_to` is added to the ADR-006 taxonomy to support embedding-similarity-based edges discovered during retrieval.

Phase 2: NetworkX loads the edge graph into memory for traversal operations. Personalized PageRank over the graph powers multi-hop retrieval in the HippoRAG pipeline (ADR-011). Graph is rebuilt periodically or on significant edge changes.

Future: Neo4j migration via a `GraphAdapter` Protocol when memory count exceeds NetworkX's in-memory capacity (estimated threshold: 500k edges).

### 3.6 Consequences

**Positive:**

- HippoRAG retrieval pipeline has the graph data it needs in Phase 2
- Consolidation Engine can traverse relationships to find merge candidates
- Librarian can detect contradictions via `contradicts` edges
- NetworkX is zero-infrastructure -- no additional database to operate
- Neo4j migration path is clean via adapter interface
- Schema is deployed in Phase 1, reducing Phase 2 risk

**Negative:**

- Phase 1 scope increases slightly (schema deployment plus basic edge creation); mitigated by the schema being already designed in ADR-006
- NetworkX holds the full graph in memory; mitigated by the fact that Phase 2 memory counts will be well within RAM capacity
- Graph rebuild latency on edge changes; mitigated by periodic rebuild rather than real-time

**Follow-up actions:**

- Include `memory_edges` in Phase 1 database migration
- Implement basic edge creation in the Librarian write path (`supersedes`, `relates_to`)
- Define `GraphAdapter` Protocol for future Neo4j migration
- Integrate NetworkX graph loading with the retrieval pipeline in Phase 2

### 3.7 Notes and Links

- Superseded decision: [ADR-006 Knowledge Graph](./ADR-006-knowledge-graph.md)
- HippoRAG retrieval: [ADR-011 HippoRAG Retrieval](./ADR-011-hipporag-retrieval.md)
- Storage backend: [ADR-003 Storage Backend](./ADR-003-storage-backend.md)
- Expanded agents: [ADR-008 Expanded Agent Architecture](./ADR-008-expanded-agent-architecture.md)

## 4. Implementation Notes

- The `memory_edges` table migration is included in the Phase 1 Alembic migration set
- Edge type is defined as a Postgres enum type and a Python `StrEnum`
- NetworkX graph is loaded at startup and refreshed on a configurable interval (`ENGRAM_GRAPH_REFRESH_INTERVAL`, default 300 seconds)
- Personalized PageRank parameters: `alpha=0.85`, `max_iter=100`, `tol=1e-6` (tunable via configuration)
- The `GraphAdapter` Protocol defines `load()`, `query_neighbors()`, `pagerank()`, and `shortest_path()` methods
- Edge weight defaults to 1.0; the Librarian adjusts weight based on confidence and recency

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Edge creation success rate | > 99% | Continuous monitoring |
| Graph load time (NetworkX) | < 5 seconds for 100k edges | Per rebuild |
| Multi-hop retrieval precision improvement | > 15% over vector-only | Quarterly evaluation |
| Memory usage for in-memory graph | < 500MB | Continuous monitoring |

Review this ADR when any of these signals appear:

- Edge count exceeds 500k and NetworkX memory usage becomes problematic
- Graph rebuild latency exceeds 30 seconds
- Multi-hop retrieval quality plateaus and Neo4j's native traversal would help
- Apache AGE reaches stable compatibility with pgvector

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-047 (Architecture Decision Workflow) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted knowledge graph in Phase 2 scope with NetworkX, superseding ADR-006
