---
id: 3NGRAM-ADR-003
title: "ADR-003: Storage backend selection"
version: 0.1.0
category: project
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-021]
tags: [adr, architecture, storage, postgres, pgvector, qdrant, 3ngram]
---

## 1. Purpose

Record the storage backend decision for 3ngram and capture why Postgres with pgvector (unified storage) was chosen over the originally proposed Postgres plus Qdrant split, based on research into pgvector's maturation and 3ngram's target scale.

## 2. Scope

This decision applies to all durable storage in the 3ngram system: typed memory records (relational), vector embeddings for semantic search, and audit logs. It governs the database architecture for the MVP and determines the Docker Compose service topology.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-003 |
| Status | Accepted |
| Date | 2026-02-12 |
| Deciders | sh4i-yurei |

### 3.2 Context

3ngram needs durable storage for typed memory records (relational) and vector embeddings for semantic search. The original proposal assumed Postgres for relational state and Qdrant for vectors. Research shows pgvector now has HNSW indexing, iterative scans (v0.8.0), halfvec support, and performs nearly identically to Qdrant at scales under 100K records.

This ADR represents a change from the original proposal. The proposal said "Postgres + Qdrant". Research reveals pgvector has matured dramatically and at 3ngram's scale (target: under 100K records for MVP), pgvector eliminates the need for a separate vector database.

### 3.3 Decision Drivers

- **Operational simplicity** -- a solo developer cannot sustain multi-database operations
- **Data consistency** -- cross-store consistency between relational data and vector embeddings
- **Query capability** -- hybrid search combining relational filters with vector similarity
- **Performance at target scale** -- under 100K records for MVP, growing to hundreds of thousands
- **Self-healing** -- fewer failure points means fewer partial-failure scenarios to handle

### 3.4 Options

#### Option A: Postgres + pgvector (unified storage)

Single database for both relational data and vector embeddings. HNSW indexing for approximate nearest neighbor search. Native hybrid search via reciprocal rank fusion (SQL-based). Transactional consistency -- memory record and its embedding are in the same transaction. One backup strategy, one connection pool, one monitoring target. At less than 100K records, performance matches dedicated vector databases.

#### Option B: Postgres + Qdrant (original proposal -- split storage)

Postgres for typed records, audit logs, and relational queries. Qdrant for vector search as a dedicated vector database. Requires cross-database consistency management (what if Qdrant write fails after Postgres commit?). Two systems to monitor, back up, and upgrade. Qdrant has richer vector-specific features (filtering, payload indexing). Better at very large scale (millions of vectors).

#### Option C: Postgres + LanceDB (embedded vector store)

LanceDB is embedded (no separate server), with built-in versioning. Columnar format, good for batch operations. Less mature ecosystem than pgvector or Qdrant. An interesting alternative but newer and less battle-tested.

### 3.5 Decision

**Option A -- Postgres + pgvector (unified storage).**

At 3ngram's target scale (under 100K records for MVP), pgvector provides equivalent performance to Qdrant while eliminating an entire class of cross-database consistency bugs. Hybrid search via reciprocal rank fusion works natively in SQL. This is a change from the original proposal based on research findings.

All vector operations go through an embedding adapter interface (Python Protocol), allowing a future backend swap to Qdrant if scale demands it.

### 3.6 Consequences

**Positive:**

- Eliminates Qdrant from Docker Compose (two services instead of three)
- Transactional consistency -- no partial writes across databases
- Single backup and restore strategy
- Fewer operational failure points (self-healing is easier with fewer systems)
- Native SQL for hybrid search -- no cross-database query coordination

**Negative:**

- Scaling ceiling -- pgvector may struggle above one million vectors (mitigated by adapter interface that allows adding Qdrant later if needed)
- Less feature-rich for vector-specific operations such as payload filtering (mitigated by Postgres WHERE clauses handling most filtering needs)

**Follow-up actions:**

- Define embedding adapter interface (Python Protocol) to allow future backend swap
- Plan migration path to Qdrant if scale demands it
- Configure pgvector HNSW index parameters (ef_construction, m) based on embedding dimensions

### 3.7 Notes and Links

- PRD: [Requirements PRD](../../planning/requirements-prd.md)
- Embedding model decision: [ADR-004 Embedding Model](./ADR-004-embedding-model.md)
- Architecture overview: [ADR-001 Monolith-First](./ADR-001-monolith-first.md)
- pgvector HNSW indexing and iterative scan documentation

## 4. Implementation Notes

- pgvector extension is enabled via `CREATE EXTENSION vector` in the Postgres initialization
- HNSW index creation: `CREATE INDEX ON memory_embeddings USING hnsw (embedding vector_cosine_ops)` with tunable `m` and `ef_construction` parameters
- Hybrid search uses reciprocal rank fusion: combine BM25-style text search scores with vector cosine similarity scores in a single SQL query
- Connection pooling via asyncpg with pool size configured by environment variable (`DB_POOL_SIZE`, default 10)
- Embedding dimension is set by the chosen model (384 for bge-small-en-v1.5, see ADR-004)

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Vector search p95 latency | < 50ms | Continuous monitoring |
| Hybrid search p95 latency | < 100ms | Continuous monitoring |
| Index build time (full reindex) | < 5 minutes at 100K records | Monthly |
| Storage size vs record count ratio | Track trend | Monthly |

Review this ADR when any of these signals appear:

- Vector search latency exceeds 100ms p95 at current scale
- Record count approaches 500K (halfway to the estimated scaling ceiling)
- A use case requires vector-specific features not available in pgvector (multi-tenancy filtering, payload indexing)

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-020 (Architecture Standards) -- decision recorded with context, options, and consequences
- STD-021 (Decision Records) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted Postgres + pgvector unified storage, replacing original Postgres + Qdrant proposal
