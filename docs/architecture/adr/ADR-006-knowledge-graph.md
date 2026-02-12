---
id: 3NGRAM-ADR-006
title: "ADR-006: Knowledge graph approach"
version: 0.1.0
category: project
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-021]
tags: [adr, architecture, knowledge-graph, 3ngram]
---

## 1. Purpose

Record the decision on whether to integrate a knowledge graph layer in the 3ngram MVP or defer it, and capture the reasoning, alternatives considered, and consequences so that future contributors understand the planned evolution path for relationship-aware retrieval.

## 2. Scope

This decision applies to the data model and retrieval pipeline of 3ngram. It governs how relationships between memories (decisions relate to beliefs, episodes inform skills, etc.) are represented, stored, and queried -- both for MVP and the planned post-MVP evolution.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-006 |
| Status | Accepted |
| Date | 2026-02-12 |
| Deciders | sh4i-yurei |

### 3.2 Context

3ngram's vision includes a knowledge graph layer for representing relationships between memories. The memory type system already implies relationships -- a Decision references the Beliefs that informed it, Episodes contain context that connects to Skills, and memories can supersede or contradict each other.

The question is whether to integrate a knowledge graph in MVP or defer it while designing the schema to support it.

Research findings:

- Microsoft GraphRAG demonstrates the value of graph-augmented retrieval but is heavy (requires LLM-based entity extraction at ingestion time)
- Apache AGE adds graph query capability (Cypher) to Postgres, running on existing tables
- Simple relation tables (`memory_edges` with source_id, target_id, edge_type, metadata JSONB) provide minimum viable graph capability using standard SQL joins
- Full graph databases (Neo4j, etc.) are overkill for MVP scale
- The memory type system already captures implicit relationships (Decision.context references, Episode.related_memories)

### 3.3 Decision Drivers

- **MVP scope discipline** -- avoid implementing features that are not required for core MVP functionality
- **Retrieval quality improvement potential** -- relationship context can significantly improve retrieval relevance
- **Implementation complexity** -- graph integration adds ingestion, storage, and query pipeline complexity
- **Future extensibility** -- the data model must not block graph integration later
- **Data model readiness** -- schema decisions made now affect migration cost later

### 3.4 Options

#### Option A: Defer entirely -- no graph capability in MVP

MVP uses hybrid retrieval only (vector + keyword). No relationship tracking between memories. Simplest to implement. Loses cross-memory relationship context in retrieval.

#### Option B: Lightweight edges table in Postgres -- plan now, implement early post-MVP

Add a `memory_edges` table with the following schema:

- `source_id` -- FK to the originating memory
- `target_id` -- FK to the related memory
- `edge_type` -- enum: supersedes, supports, contradicts, relates_to, derived_from
- `weight` -- float, edge strength
- `metadata` -- JSONB for edge-specific attributes
- `created_at` -- timestamp

Include the table in schema design (M4 milestone) but implement in early post-MVP. Graph-aware retrieval becomes a future pipeline stage. No graph query engine in MVP -- just SQL joins. Apache AGE serves as the future upgrade path for Cypher queries.

#### Option C: Full knowledge graph integration in MVP

Neo4j or Apache AGE from day one. Entity extraction on memory ingestion. Graph-augmented retrieval pipeline. Significant complexity -- contradicts MVP scope discipline.

### 3.5 Decision

**Option B -- Lightweight edges table, planned now, implemented early post-MVP.**

The schema for `memory_edges` is designed during M4 (specification milestone) to ensure the data model supports graph relationships, but implementation is deferred to early post-MVP. This preserves MVP scope discipline while ensuring the path to knowledge graph capabilities is clear and does not require schema migration later.

The memory type system already captures implicit relationships (Decision.context references, Episode.related_memories). The edges table makes these explicit and queryable.

Edge type taxonomy:

- `supersedes` -- newer memory replaces older one
- `supports` -- memory provides evidence for another
- `contradicts` -- memory conflicts with another (triggers Librarian review)
- `relates_to` -- general association
- `derived_from` -- memory was synthesized from another

### 3.6 Consequences

**Positive:**

- MVP stays focused -- no graph implementation complexity in the critical path
- Schema designed for graph extensibility from day one (no painful migrations later)
- Clear upgrade path: edges table with SQL joins, then Apache AGE for Cypher, then full GraphRAG
- Edge types (supersedes, contradicts) support memory governance -- the Librarian can detect contradictions and trigger reviews

**Negative:**

- MVP retrieval lacks relationship context; mitigated by memory type fields that already capture some relationships implicitly
- Schema design effort for a deferred feature; mitigated by the simplicity of the table (single table, five columns plus metadata)

**Follow-up actions:**

- Include `memory_edges` in the schema design during M4 (specification milestone)
- Define the edge type taxonomy and document it in the data model specification
- Plan the post-MVP implementation sprint for graph-aware retrieval
- Evaluate Apache AGE compatibility with pgvector on the target Postgres version

### 3.7 Notes and Links

- Storage backend decision: [ADR-003](./ADR-003-storage-backend.md)
- PRD: [Requirements PRD](../../planning/requirements-prd.md)

## 4. Implementation Notes

- The `memory_edges` table is defined in the schema design but the migration is not applied until the post-MVP sprint
- Edge creation is handled by the Librarian gate during memory write operations (post-MVP)
- Graph-aware retrieval is a pipeline stage added after the existing hybrid retrieval (vector + keyword) stages
- Apache AGE requires Postgres 15+ and is installed as an extension; verify compatibility with pgvector before adoption
- The edge type enum is defined in Python as a `StrEnum` and in Postgres as a custom type

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Schema design completeness for memory_edges | 100% by M4 | Milestone review |
| Implicit relationship coverage in memory types | All memory types define relationship fields | Every CI run (schema validation) |
| Post-MVP graph sprint planned | Sprint defined before MVP release | Pre-release review |

Review this ADR when any of these signals appear:

- MVP retrieval quality is limited by lack of relationship context (user feedback or evaluation metrics)
- Memory count exceeds 10,000 and cross-memory queries become a common pattern
- Apache AGE releases a stable version compatible with the target Postgres and pgvector versions
- A second agent role (Librarian) is implemented that needs contradiction detection

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-020 (Architecture Standards) -- decision recorded with context, options, and consequences
- STD-021 (Decision Records) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted lightweight edges table approach, planned now, implemented early post-MVP
