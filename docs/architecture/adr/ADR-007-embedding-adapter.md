---
id: 3NGRAM-ADR-007
title: "ADR-007: Swappable embedding adapter interface"
version: 0.1.0
category: architecture
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-047]
tags: [adr, architecture, embedding, adapter, 3ngram]
---

## 1. Purpose

Record the decision to replace the fixed embedding model selection (ADR-004) with a swappable adapter interface, so that the kernel can autonomously swap embedding models at runtime without changes to retrieval logic.

## 2. Scope

This decision applies to all vector embedding generation in 3ngram. It supersedes ADR-004 by elevating the adapter pattern from a follow-up action to the primary architectural decision. The default model (fastembed with BAAI/bge-small-en-v1.5) remains unchanged for Phase 1; what changes is the contract that governs how models are loaded, invoked, and replaced.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-007 |
| Status | Accepted |
| Date | 2026-02-13 |
| Deciders | sh4i-yurei |
| Supersedes | ADR-004 |

### 3.2 Context

ADR-004 selected fastembed with BAAI/bge-small-en-v1.5 as the embedding library and model. The v2 system design expands retrieval to include multi-hop queries, knowledge graph traversal, and RL-driven quality feedback. These capabilities require model flexibility -- the kernel must be able to swap to a higher-quality model (or a domain-tuned model) when retrieval quality degrades, without code changes to the retrieval pipeline.

ADR-004 already identified an adapter pattern as a follow-up action. This ADR promotes that pattern to a first-class architectural decision and defines the contract.

### 3.3 Decision Drivers

- **Model flexibility** -- v2 retrieval quality depends on being able to upgrade models without pipeline changes
- **Zero-config for users** -- model swaps should be transparent to callers of the retrieval API
- **Autonomous operation** -- the kernel should be able to swap models when quality metrics degrade
- **Backward compatibility** -- existing embeddings must remain queryable after a model swap (re-embedding strategy required)
- **Phase 1 simplicity** -- the adapter must not add complexity beyond what fastembed already provides

### 3.4 Options

#### Option A: EmbeddingAdapter Protocol with runtime swap

Define a Python Protocol (`EmbeddingAdapter`) with two methods: `embed_one(text) -> list[float]` and `embed_batch(texts) -> list[list[float]]`. Each implementation (fastembed, sentence-transformers, API-based) provides these methods. The kernel selects the active adapter via configuration. Model metadata (dimension, model name) is exposed as adapter properties for schema validation.

#### Option B: Fixed model with configuration-only swap

Keep the current fastembed-specific code but make the model name configurable. Simpler, but couples the retrieval pipeline to fastembed internals and does not support non-fastembed providers.

#### Option C: Multi-model simultaneous operation

Run multiple embedding models in parallel and merge results. Provides higher quality but doubles compute and memory. Overkill for Phase 1; may be a future optimization.

### 3.5 Decision

**Option A -- EmbeddingAdapter Protocol with runtime swap.**

The `EmbeddingAdapter` Protocol defines:

- `embed_one(text: str) -> list[float]` -- embed a single text
- `embed_batch(texts: list[str]) -> list[list[float]]` -- embed a batch of texts
- `dimension` property -- returns the embedding dimension (e.g., 384)
- `model_name` property -- returns the model identifier for metadata tracking

Phase 1 default: `FastembedAdapter` wrapping BAAI/bge-small-en-v1.5 (384 dimensions). Future adapters: `SentenceTransformerAdapter`, `APIEmbeddingAdapter`, GPU-accelerated variants.

When a model swap occurs, a re-embedding job is queued for existing records. The adapter tracks which model produced each embedding via a `model_version` column in the memories table.

### 3.6 Consequences

**Positive:**

- No code changes to retrieval logic when the embedding model changes
- Kernel can autonomously swap models based on quality metrics
- Clean separation of embedding concerns from retrieval concerns
- Supports CPU, GPU, and API-based providers through the same interface
- Re-embedding strategy prevents stale vector mismatches

**Negative:**

- Adapter abstraction adds one layer of indirection; mitigated by the Protocol being minimal (two methods plus two properties)
- Re-embedding on model swap is expensive for large memory stores; mitigated by background job queue with rate limiting

**Follow-up actions:**

- Define the `EmbeddingAdapter` Protocol in `src/engram/memory_kernel/embedding.py`
- Implement `FastembedAdapter` as the Phase 1 default
- Add `model_version` column to the memories table schema
- Design the re-embedding background job for model swap scenarios

### 3.7 Notes and Links

- Superseded decision: [ADR-004 Embedding Model](./ADR-004-embedding-model.md)
- Storage backend: [ADR-003 Storage Backend](./ADR-003-storage-backend.md)
- Monolith-first: [ADR-001 Monolith-First](./ADR-001-monolith-first.md)

## 4. Implementation Notes

- The Protocol is defined in `src/engram/memory_kernel/embedding.py` using `typing.Protocol`
- `FastembedAdapter.__init__` accepts `model_name` and optional `cache_dir` parameters
- ProcessPoolExecutor bulkheading from ADR-001 applies to all adapter implementations
- The `model_version` column stores the model name string; pgvector index parameters may need reconfiguration if embedding dimensions change between models
- Configuration selects the active adapter via `ENGRAM_EMBEDDING_ADAPTER` environment variable (default: `fastembed`)

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Adapter interface test coverage | >= 95% | Every CI run |
| Embedding latency per adapter | < 20ms (CPU), < 5ms (GPU) | Continuous monitoring |
| Re-embedding job completion time | < 1 hour for 100k records | Per model swap |
| Model version consistency | 100% of records match active model | Weekly audit |

Review this ADR when any of these signals appear:

- A third embedding provider is needed (validates the adapter pattern at scale)
- Re-embedding costs become prohibitive (consider incremental or lazy re-embedding)
- Multi-model simultaneous operation becomes desirable (Option C revisit)

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-047 (Architecture Decision Workflow) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted swappable EmbeddingAdapter Protocol, superseding ADR-004
