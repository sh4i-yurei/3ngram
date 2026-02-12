---
id: 3NGRAM-ADR-004
title: "ADR-004: Embedding model selection"
version: 0.1.0
category: project
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-021]
tags: [adr, architecture, embedding, fastembed, 3ngram]
---

## 1. Purpose

Record the embedding model and inference library selection for 3ngram and capture the reasoning behind choosing fastembed over alternatives, informed by stability failures in the predecessor project.

## 2. Scope

This decision applies to all vector embedding generation in the 3ngram system: converting memory records into vector representations for semantic search, batch embedding of historical records, and real-time embedding of new memory writes. It determines the inference runtime, default model, and GPU acceleration strategy.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-004 |
| Status | Accepted |
| Date | 2026-02-12 |
| Deciders | sh4i-yurei |

### 3.2 Context

3ngram needs an embedding model to convert memory records into vector representations for semantic search. The predecessor project (ai_tech_stack) used SentenceTransformers which crashed silently, forcing an emergency migration to fastembed. Mark has an RTX 3070 GPU (8GB VRAM) available for acceleration.

The chosen model must produce embeddings compatible with the pgvector storage backend (ADR-003). Embedding dimension determines the pgvector column type and HNSW index configuration.

### 3.3 Decision Drivers

- **Stability and reliability** -- embedding failures in ai_tech_stack caused silent data corruption
- **CPU-first with GPU option** -- must work without GPU, but should leverage RTX 3070 when available
- **Model quality for knowledge retrieval** -- embeddings must support high-quality semantic search over typed memory records
- **Adapter pattern** -- must support future model swaps without changing retrieval logic
- **Self-healing** -- embedding failures should not crash the system; graceful degradation required

### 3.4 Options

#### Option A: fastembed (ONNX-based, CPU default, GPU optional)

Over 25 models available, using ONNX Runtime for inference. Default model: BAAI/bge-small-en-v1.5 (384 dimensions, fast, good quality). GPU acceleration via `pip install fastembed-gpu` with CUDAExecutionProvider, compatible with RTX 3070. Proven in ai_tech_stack after the SentenceTransformers failure. Lightweight with no PyTorch dependency for CPU mode. Supports batch processing via `model.embed(documents, batch_size=512)`.

#### Option B: SentenceTransformers (v5.x)

Has stabilized since the v2.x days when ai_tech_stack used it. Larger model ecosystem with more flexibility. Requires PyTorch dependency (heavier runtime). Previous stability issues in ai_tech_stack were severe and caused silent failures.

#### Option C: OpenAI or Anthropic API embeddings

High quality embeddings with no local compute needed. Per-request cost and network dependency. Privacy concern -- all memory content would be sent to an external API. Adds an external dependency that contradicts the local-first design goal.

### 3.5 Decision

**Option A -- fastembed.**

Proven stable in the predecessor project where it replaced SentenceTransformers after critical failures. CPU-first by default (no GPU dependency), with GPU acceleration available via CUDAExecutionProvider when performance demands it. Start with BAAI/bge-small-en-v1.5 (384 dimensions), evaluate bge-m3 or nomic-embed-text if retrieval quality is insufficient.

All embedding operations go through a Python Protocol adapter interface, allowing model swaps without changing retrieval logic.

### 3.6 Consequences

**Positive:**

- Proven stability (replaced SentenceTransformers in ai_tech_stack after critical failure)
- CPU-first means no GPU dependency for basic operation
- GPU path available (RTX 3070) for performance when needed
- ONNX Runtime is lightweight -- no PyTorch required for CPU mode
- Adapter interface allows future model swaps (bge-m3, nomic-embed-text)

**Negative:**

- Smaller ecosystem than SentenceTransformers (mitigated by adapter interface allowing future library swap)
- ONNX conversion needed for non-standard models (mitigated by using pre-converted models from the fastembed catalog)

**Follow-up actions:**

- Define EmbeddingAdapter Protocol with `embed_one` and `embed_batch` methods
- Implement batch embedding pipeline with ProcessPoolExecutor for bulkheading (per ADR-001)
- Set up retrieval quality evaluation metrics for future model comparison
- Document GPU setup instructions (fastembed-gpu, CUDA toolkit, RTX 3070 configuration)

### 3.7 Notes and Links

- Storage backend decision: [ADR-003 Storage Backend](./ADR-003-storage-backend.md)
- Architecture style: [ADR-001 Monolith-First](./ADR-001-monolith-first.md)
- PRD: [Requirements PRD](../../planning/requirements-prd.md)
- fastembed model catalog and ONNX Runtime documentation

## 4. Implementation Notes

- fastembed is installed via `pip install fastembed` (CPU) or `pip install fastembed-gpu` (GPU)
- Default model initialization: `TextEmbedding(model_name="BAAI/bge-small-en-v1.5")`
- Embedding dimension (384) must match the pgvector column: `embedding vector(384)`
- Batch embedding uses `list(model.embed(documents, batch_size=512))` -- fastembed returns a generator
- ProcessPoolExecutor isolates embedding from the async event loop (bulkheading per ADR-001)
- GPU detection: check for CUDAExecutionProvider availability at startup, fall back to CPUExecutionProvider
- Model files are cached in `~/.cache/fastembed` by default; configure via `cache_dir` parameter for Docker deployments

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Single-record embedding latency (CPU) | < 20ms | Continuous monitoring |
| Batch embedding throughput (CPU) | > 100 records/second | Weekly benchmark |
| Embedding failure rate | < 0.1% | Continuous monitoring |
| Retrieval precision at k=10 | > 0.8 | Quarterly evaluation |

Review this ADR when any of these signals appear:

- Retrieval precision drops below 0.7 at k=10 on evaluation set
- Embedding latency exceeds 50ms per record on CPU
- A new model (bge-m3, nomic-embed-text) shows significant quality improvement in benchmarks
- Multi-language memory records require a multilingual model

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-020 (Architecture Standards) -- decision recorded with context, options, and consequences
- STD-021 (Decision Records) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted fastembed with BAAI/bge-small-en-v1.5 as the embedding model and inference library
