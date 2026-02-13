---
id: 3NGRAM-MD-RETRIEVAL-001
title: "Module Design: Retrieval Subsystem"
version: 0.1.0
category: project
status: draft
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-022]
tags: [design, module-design, retrieval, hipporag, 3ngram]
---

# Purpose

Define the module design for `engram.retrieval` -- the Retrieval
subsystem of the 3ngram kernel. This subsystem implements a
HippoRAG-inspired 6-stage retrieval pipeline that transforms an agent's
query into a validated, conflict-resolved, provenance-annotated response
assembled from heterogeneous memory stores.

Success means: agents find what they need more than 90% of the time
(retrieval hit rate), within a 2-second p95 latency budget, with full
provenance metadata and conflict transparency.

# Scope

This module design covers the `engram.retrieval` Python package and its
four constituent modules: `router.py`, `search.py`, `validation.py`, and
`assembly.py`. It governs the full retrieval pipeline from query intake
to result delivery across all implementation phases.

**In scope**: Adaptive query routing, hybrid candidate retrieval (dense
vector, sparse BM25, knowledge graph traversal), validation and
filtering (temporal, access control, confidence, Self-RAG reflection),
memory distillation, conflict resolution and assembly, delivery and
feedback collection, bounded retries, and RRF fusion.

**Out of scope**: Memory storage and write operations (Memory subsystem),
embedding model selection and management (Infrastructure layer via
ADR-007), knowledge graph construction and edge management (Memory
subsystem via ADR-009), Librarian Gate logic (Memory subsystem via
ADR-012), protocol-level rate limiting and authentication (Protocol
layer).

# Standard

## Module purpose and responsibility

The Retrieval subsystem is the read path of the 3ngram kernel. It is
responsible for transforming an agent's query into a ranked, validated
set of memory records with provenance metadata, conflict annotations,
and citation references.

The subsystem implements the 6-stage HippoRAG-inspired pipeline defined
in ADR-011:

| Stage | Name | Phase | Responsibility |
|-------|------|-------|---------------|
| 1 | Adaptive query routing | 1 (heuristic), 3 (learned) | Classify query complexity and select retrieval strategy |
| 2 | Hybrid candidate retrieval | 1 (vector+BM25), 2 (+KG) | Run parallel retrieval strategies and merge via RRF |
| 3 | Validation and filtering | 1 (basic), 2 (+Self-RAG) | Apply temporal, access control, confidence, and relevance filters |
| 4 | Memory distillation | 3 (RL) | Select optimal candidate subset via learned ranking |
| 5 | Conflict resolution and assembly | 1 (basic), 2 (full) | Detect contradictions, resolve conflicts, assemble response |
| 6 | Delivery and feedback loop | 3 | Return results with provenance and collect usage feedback |

Each stage is a discrete async function with defined inputs and outputs.
Stages can be skipped or simplified based on query classification and
phase availability.

## Inputs and outputs

### Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `RetrievalQuery` | Protocol layer (MCP/A2A) | Query text, optional filters (type, time range, agent scope), result limit (default 10) |
| Agent identity | Protocol layer | Authenticated agent ID and trust level for access control |
| Embedding vector | Infrastructure layer (ADR-007) | Query text embedded via the active `EmbeddingAdapter` |
| Knowledge graph | Infrastructure layer (ADR-009) | In-memory NetworkX graph for PageRank traversal (Phase 2+) |

### Outputs

| Output | Consumer | Description |
|--------|----------|-------------|
| `RetrievalResult` | Protocol layer | Ranked list of `ScoredMemory` records with provenance metadata |
| Retrieval metrics | Autonomy subsystem | Latency, hit rate, candidate counts, route classification (emitted as structured log events) |
| Feedback signals | Autonomy subsystem | Implicit usage feedback for RL training (Phase 3+, emitted asynchronously) |

### Side effects

- Structured log entries per stage (latency, candidate counts, decisions)
- Prometheus counter and histogram updates
- Cache reads and writes (for `skip` route)
- Feedback records persisted asynchronously (Phase 3+)

## Public interfaces

### `RetrievalPipeline`

The primary entry point for all retrieval operations.

```python
class RetrievalPipeline:
    """Orchestrates the 6-stage HippoRAG retrieval pipeline."""

    async def query(
        self,
        query: RetrievalQuery,
        agent_context: AgentContext,
    ) -> RetrievalResult:
        """Execute the full retrieval pipeline.

        Runs stages 1-6 in sequence, with stage 2 strategies
        executing in parallel. Applies bounded retries on failure.

        Args:
            query: The retrieval query with text, filters, and limit.
            agent_context: Authenticated agent identity and trust level.

        Returns:
            RetrievalResult with ranked records, provenance, and metadata.

        Raises:
            RetrievalTimeoutError: Pipeline exceeded the per-query timeout.
            RetrievalCircuitOpenError: Circuit breaker is open for a
                required stage.
        """
```

### `RetrievalQuery`

```python
@dataclass(frozen=True)
class RetrievalQuery:
    text: str
    memory_types: list[MemoryType] | None = None
    time_range: TimeRange | None = None
    agent_scope: list[str] | None = None
    limit: int = 10
    include_consolidated: bool = False
    include_historical: bool = False
    min_confidence: float = 0.0
```

### `RetrievalResult`

```python
@dataclass(frozen=True)
class RetrievalResult:
    records: list[ScoredMemory]
    query_route: QueryRoute
    total_candidates: int
    retrieval_confidence: float
    conflicts: list[ConflictPair]
    retry_count: int
    skip_reason: str | None = None
    latency_ms: float = 0.0
```

### `ScoredMemory`

```python
@dataclass(frozen=True)
class ScoredMemory:
    record: MemoryRecord
    score: float
    rank: int
    provenance: Provenance
```

### `Provenance`

```python
@dataclass(frozen=True)
class Provenance:
    retrieval_strategies: list[str]
    rrf_score: float
    validation_passed: list[str]
    confidence: float
    citation: str
```

### `ConflictPair`

```python
@dataclass(frozen=True)
class ConflictPair:
    record_a: UUID
    record_b: UUID
    edge_type: str  # "contradicts"
    resolution: str  # "recency" | "confidence" | "unresolved"
    winner: UUID | None
```

### Error types

| Error | Condition | Consumer action |
|-------|-----------|-----------------|
| `RetrievalTimeoutError` | Pipeline exceeded per-query timeout | Caller receives partial results if available |
| `RetrievalCircuitOpenError` | Circuit breaker open for a required stage | Caller receives degraded result set |
| `RetrievalEmptyError` | No candidates found after all retry attempts | Caller receives empty result with diagnostic metadata |

## Dependencies

### Upstream modules

| Dependency | Package | Purpose | Trust boundary |
|------------|---------|---------|---------------|
| Embedding adapter | `engram.infra.embeddings` | Query text embedding via `EmbeddingAdapter` Protocol (ADR-007) | Infrastructure layer -- adapter isolates model details |
| Database | `engram.infra.db` | PostgreSQL connection for vector search (pgvector) and BM25 (full-text search) (ADR-003) | Infrastructure layer -- accessed via async connection pool |
| Knowledge graph | `engram.infra.graph` | NetworkX graph for PageRank traversal (ADR-009, Phase 2+) | Infrastructure layer -- accessed via `GraphAdapter` Protocol |
| Memory types | `engram.memory.types` | `MemoryRecord` schema, `MemoryType` enum, `AccessLevel` enum | Domain layer -- same kernel, typed interface |
| Temporal engine | `engram.memory.temporal` | Bi-temporal queries (`as_of_event`, `as_of_ingestion`), version chain lookups | Domain layer -- read-only access to temporal state |
| Agent identity | `engram.types` | `AgentContext` with authenticated identity and trust level | Shared types -- protocol layer authenticates, retrieval consumes |

### External libraries

| Library | Purpose | Phase |
|---------|---------|-------|
| `asyncio` | Parallel execution of retrieval strategies in Stage 2 | 1 |
| `aiobreaker` | Circuit breakers per stage (ADR-001) | 1 |
| `tenacity` | Retry with backoff at infrastructure boundaries (ADR-001) | 1 |
| `structlog` | Structured logging per stage | 1 |
| `prometheus_client` | Metrics emission (counters, histograms, gauges) | 1 |
| `networkx` | Personalized PageRank for KG traversal (ADR-009) | 2 |
| Cross-encoder model | Self-RAG relevance scoring (local inference) | 2 |

### Import boundary rules

Per ADR-001 and the system design import-linter configuration:

- `engram.retrieval` MAY import from `engram.types` (shared types
  including `AgentContext`)
- `engram.retrieval` MAY import from `engram.memory.types` (type
  definitions) and `engram.memory.temporal` (bi-temporal queries,
  version chain lookups)
- `engram.retrieval` MAY import from `engram.infra` (via Protocol
  interfaces)
- `engram.retrieval` MUST NOT import from `engram.memory.gate`,
  `engram.autonomy`, `engram.devenv`, or `engram.protocols`
- `engram.protocols` and `engram.agents` depend on `engram.retrieval`,
  not the reverse

## Internal responsibilities

### `router.py` -- Adaptive query router (Stage 1)

Classifies the incoming query into one of four route types and selects
the retrieval strategy:

| Route | Criteria | Retrieval strategy | Phase |
|-------|----------|--------------------|-------|
| `simple` | Single-hop factual query, no relationship indicators | Vector search only | 1 |
| `multi_hop` | Relationship-spanning query (indicators: "why", "influenced", "related to", "because of") | Vector + KG traversal | 2 |
| `exploratory` | Broad discovery query (indicators: "everything about", "all", "history of") | Vector + BM25 + KG | 2 |
| `skip` | Cache hit, context-sufficient, or no-retrieval-needed | Return cached/empty result | 1 |

**Phase 1 implementation**: Heuristic keyword detection. A dictionary of
indicator phrases maps to route classifications. Queries without
indicators default to `simple`.

**Phase 3 implementation**: Learned classifier trained on accumulated
routing data and downstream quality feedback.

**Skip route behavior**:

- **Cache hit**: An identical or semantically similar query (cosine
  similarity above threshold) was executed recently. Return the cached
  result with `skip_reason = "cache_hit"`.
- **Context sufficient**: The query can be answered from the request's
  own context (e.g., a follow-up that references information already in
  the conversation). Return empty result with
  `skip_reason = "context_sufficient"`.
- **No retrieval**: The router determines no memory retrieval is needed
  (e.g., greeting, meta-question). Return empty result with
  `skip_reason = "no_retrieval_needed"`.

### `search.py` -- Hybrid search (Stage 2)

Executes retrieval strategies in parallel and merges results via
Reciprocal Rank Fusion (RRF).

**Retrieval strategies**:

| Strategy | Backend | Method | Phase |
|----------|---------|--------|-------|
| Dense vector | pgvector (ADR-003) | Cosine similarity via HNSW index | 1 |
| Sparse BM25 | PostgreSQL full-text search | `ts_rank_cd` with `tsvector`/`tsquery` | 1 |
| KG traversal | NetworkX (ADR-009) | Personalized PageRank seeded from query entities | 2 |

**RRF fusion formula**:

```text
score(d) = sum over strategies S of: 1 / (k + rank_S(d))
```

Where `k = 60` (standard RRF constant per ADR-011). Each strategy
produces a ranked list of candidates. RRF merges these lists into a
single score per candidate. Higher scores indicate broader agreement
across strategies.

**Parallel execution**: Stage 2 strategies run concurrently via
`asyncio.gather()`. The stage latency is bounded by the slowest
strategy. Individual strategy timeouts prevent a single slow path from
blocking the pipeline.

**KG traversal specifics (Phase 2+)**:

1. Extract entity mentions from the query text
2. Locate corresponding nodes in the NetworkX graph
3. Run Personalized PageRank seeded from those nodes
   (`alpha=0.85`, `max_iter=100`, `tol=1e-6` per ADR-009)
4. Return top-k nodes by PageRank score as candidates
5. Limits: `max_iter=100` iteration cap, top-k result cap of 50 nodes,
   stage-level timeout of 500ms

### `validation.py` -- Validation and filtering (Stage 3)

Applies sequential filters to the candidate set:

1. **Temporal relevance**: Weight candidates by the stored `decay_score`
   field on `MemoryRecord` (computed and refreshed periodically by the
   Autonomy scheduler using the decay function from ADR-010).
   Candidates below a minimum temporal relevance threshold are excluded
   unless the query includes an `include_historical=True` flag (added to
   the `RetrievalQuery` interface for this purpose).
   For bi-temporal queries (`as_of_event` or `as_of_ingestion` filters),
   the `TemporalEngine.query()` is called to retrieve point-in-time
   record snapshots.

2. **Access control**: Filter candidates based on the agent's trust
   level and the record's `access_level`. An agent can only retrieve
   records at or below its authorized access level. Agent identity is
   propagated through the pipeline from the protocol layer.

3. **Confidence threshold**: Exclude candidates below the query's
   `min_confidence` parameter (default 0.0 -- no filtering). The
   confidence value comes from the record's `source_confidence` field.

4. **Self-RAG reflection (Phase 2+)**: Score each remaining candidate
   for relevance to the query using a lightweight local cross-encoder
   model. Candidates below the relevance threshold are excluded.

**Self-RAG model specification**:

| Phase | Approach | Latency target |
|-------|----------|---------------|
| 1 | No Self-RAG -- this filter is skipped | N/A |
| 2 | Local cross-encoder model (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) for relevance scoring. NOT an LLM API call -- must be local inference only. | < 50ms per candidate, < 200ms batch |
| 3 | RL-trained distiller replaces or augments the cross-encoder | < 200ms batch |

The cross-encoder in Phase 2 takes `(query_text, candidate_text)` pairs
and produces a relevance score (0.0 to 1.0). Candidates are scored in
batch to amortize model loading overhead. A configurable threshold
(default 0.3) determines the relevance cutoff.

### `assembly.py` -- Response assembly (Stages 4, 5, 6)

Handles the final pipeline stages: distillation, conflict resolution,
and delivery.

**Stage 4 -- Memory distillation (Phase 3)**:

- RL-trained component selects the optimal subset of validated candidates
- Trained on outcome data: which retrieved memories were actually used
  by the calling agent
- GRPO/PPO reward signal from Stage 6 feedback
- Phase 1-2 fallback: heuristic ranking by composite score
  (RRF score x temporal relevance x confidence)

**Stage 5 -- Conflict resolution**:

1. Query the knowledge graph for `contradicts` edges between any
   candidates in the result set (ADR-009)
2. For each conflict pair, apply resolution strategy:
   - **Recency**: The more recent record wins (by `event_time`)
   - **Confidence**: The higher-confidence record wins (by
     `source_confidence`)
   - **Unresolved**: Both records are included with a conflict
     annotation when recency and confidence disagree
3. Assemble `ConflictPair` metadata for each detected conflict
4. Generate provenance metadata for each result: which retrieval
   strategies contributed, the RRF score, which validation checks
   passed, and a citation string

**Stage 6 -- Delivery and feedback (Phase 3)**:

- Return the assembled `RetrievalResult` with full provenance
- Collect implicit feedback asynchronously (not on the critical path):
  - Was the memory used by the calling agent?
  - Was the memory marked as helpful?
  - Was the retrieval result sufficient (no follow-up query needed)?
- Feed signals to Stage 4 (RL distiller) and the Librarian Gate
  (storage quality feedback per ADR-012)

## Error and failure modes

### Bounded retries

Maximum 3 attempts with escalating strategies per ADR-011:

| Attempt | Strategy | Modification |
|---------|----------|-------------|
| 1 | Standard retrieval | Original query, original filters |
| 2 | Broaden | Relax filters: expand time window to 2x, lower `min_confidence` by 0.2, include consolidated records |
| 3 | Alternative route | Switch routing class: `simple` becomes `multi_hop`, `multi_hop` becomes `exploratory` with broadened filters |
| Final | Partial results | Return whatever candidates exist with `retrieval_confidence` reflecting degraded quality |

Retries are tracked per query. The `RetrievalResult.retry_count` field
indicates how many attempts were needed.

### Circuit breakers

Each pipeline stage is wrapped in an aiobreaker circuit breaker
(ADR-001). A stage failure triggers the breaker, which prevents
cascading failures:

| Stage | Breaker behavior on open | Degraded behavior |
|-------|------------------------|-------------------|
| Router (Stage 1) | Default to `simple` route | Functional but suboptimal routing |
| Vector search (Stage 2) | Skip vector candidates | BM25 and KG results only |
| BM25 search (Stage 2) | Skip BM25 candidates | Vector and KG results only |
| KG traversal (Stage 2) | Skip KG candidates | Vector and BM25 results only |
| Validation (Stage 3) | Skip Self-RAG, apply basic filters only | Lower precision, same recall |
| Assembly (Stage 5) | Skip conflict detection | Results without conflict metadata |

A retrieval pipeline invocation fails only if all Stage 2 strategies
are circuit-broken simultaneously. In that case,
`RetrievalCircuitOpenError` is raised.

### Stage-level timeouts

Each stage has an independent timeout to prevent unbounded execution:

| Stage | Timeout | Rationale |
|-------|---------|-----------|
| Stage 1 (routing) | 50ms | Simple classification, should be near-instant |
| Stage 2 (vector) | 300ms | pgvector HNSW is fast at target scale |
| Stage 2 (BM25) | 200ms | Postgres FTS is fast at target scale |
| Stage 2 (KG) | 500ms | PageRank iteration has variable cost |
| Stage 3 (validation) | 300ms | Batch cross-encoder scoring in Phase 2 |
| Stage 4 (distillation) | 200ms | Phase 3 RL inference |
| Stage 5 (assembly) | 100ms | In-memory operations |
| Pipeline total | 3000ms | Hard ceiling including retries |

A stage timeout triggers the circuit breaker for that stage and the
pipeline continues with degraded results.

### Failure scenarios

| Scenario | Impact | Mitigation |
|----------|--------|------------|
| pgvector connection failure | No vector search candidates | Circuit breaker trips; BM25 and KG provide candidates; retry with backoff |
| FTS index not built | No BM25 candidates | Circuit breaker trips; vector and KG provide candidates; log warning for reindex |
| NetworkX graph not loaded | No KG candidates (Phase 2+) | Circuit breaker trips; vector and BM25 provide candidates; graph rebuild scheduled |
| Embedding model unavailable | Cannot embed query | Pipeline fails with `RetrievalCircuitOpenError`; this is a hard dependency |
| Cross-encoder model unavailable (Phase 2+) | No Self-RAG scoring | Skip Self-RAG filter; lower precision but pipeline continues |
| All strategies return empty | No candidates at all | Bounded retry with broadened filters; final result is empty with diagnostic metadata |

## Non-functional considerations

### Latency budget

Total p95 budget is less than 2 seconds for 10 results at 100K corpus
(per system design NFR). Stage-level breakdown:

| Stage | Budget | Notes |
|-------|--------|-------|
| Stage 1 (routing) | < 10ms | Heuristic classification |
| Stage 2 (retrieval) | < 800ms | Parallel execution; slowest path dominates |
| -- Vector search | < 200ms | pgvector HNSW at 100K scale |
| -- BM25 search | < 100ms | Postgres FTS at 100K scale |
| -- KG traversal | < 500ms | PageRank with iteration limits (Phase 2) |
| Stage 3 (validation) | < 200ms | Batch scoring across candidates |
| Stage 4 (distillation) | < 100ms | Phase 3 RL inference |
| Stage 5 (assembly) | < 50ms | In-memory conflict detection and assembly |
| Stage 6 (feedback) | Async | Not on critical path |
| Buffer | ~640ms | Overhead, serialization, inter-stage transitions |

### Scalability

- Phase 1: pgvector handles up to 500K records (ADR-003 ceiling
  estimate). BM25 via Postgres FTS scales similarly.
- Phase 2: NetworkX graph operates in-memory with up to 500K edges
  (ADR-009). PageRank iteration is bounded by `max_iter=100`.
- If scale exceeds these ceilings, the adapter interfaces (ADR-003,
  ADR-009) allow migration to Qdrant and Neo4j respectively without
  changes to retrieval logic.

### Concurrency

- Stage 2 strategies execute concurrently via `asyncio.gather()`
- Database queries use the shared asyncpg connection pool (`DB_POOL_SIZE`
  default 10, per ADR-003)
- Cross-encoder inference (Phase 2) runs in a dedicated thread via
  `asyncio.to_thread()` to avoid blocking the event loop (per ADR-001
  bulkheading pattern). If model size requires process isolation,
  `ProcessPoolExecutor` is an alternative but adds serialization overhead
- The retrieval pipeline is re-entrant: multiple concurrent queries are
  supported, bounded by connection pool size

### Caching

- Query result cache with configurable TTL (default 60 seconds)
- Cache key: hash of (agent identity, query text, filters)
- Cache is local in-memory (not shared across processes)
- Cache invalidation: on memory write events (via internal event bus)

## Observability and signals

### Metrics

| Metric | Type | Labels | Phase |
|--------|------|--------|-------|
| `engram_retrieval_latency_seconds` | Histogram | `stage`: routing/retrieval/validation/distillation/assembly | 1 |
| `engram_retrieval_e2e_latency_seconds` | Histogram | -- | 1 |
| `engram_retrieval_hit_rate` | Counter | `result`: hit/miss | 1 |
| `engram_retrieval_precision_at_k` | Gauge | -- | 1 |
| `engram_retrieval_route_total` | Counter | `route`: simple/multi_hop/exploratory/skip | 1 |
| `engram_retrieval_retry_total` | Counter | `level`: 1/2/3 | 1 |
| `engram_retrieval_candidates` | Histogram | `stage`: input/output, `strategy`: vector/bm25/kg | 1 |
| `engram_retrieval_conflict_total` | Counter | `resolution`: recency/confidence/unresolved | 2 |
| `engram_retrieval_selfrag_score` | Histogram | -- | 2 |
| `engram_retrieval_feedback_total` | Counter | `signal`: used/helpful/sufficient | 3 |
| `engram_retrieval_circuit_state` | Gauge | `stage`: router/vector/bm25/kg/validation/assembly | 1 |

### Structured logs

Every pipeline execution emits a structured log entry (via `structlog`)
with:

- `query_id`: Unique identifier for the retrieval request
- `agent_id`: Authenticated agent identity
- `route`: Classification result from Stage 1
- `stage_latencies`: Dict of stage name to latency in milliseconds
- `candidate_counts`: Dict of strategy name to candidate count
- `result_count`: Number of records returned
- `retry_count`: Number of retry attempts
- `retrieval_confidence`: Overall confidence of the result set
- `conflicts_detected`: Number of conflict pairs found

### Health checks

The retrieval subsystem exposes component health to the `/health`
endpoint:

| Check | Condition | Degraded behavior |
|-------|-----------|-------------------|
| Vector index responsive | pgvector query returns within 500ms | Flag degraded; retrieval continues with BM25+KG |
| FTS index responsive | Postgres FTS query returns within 200ms | Flag degraded; retrieval continues with vector+KG |
| KG graph loaded | NetworkX graph is populated and queryable | Flag degraded; retrieval continues with vector+BM25 |
| Embedding model loaded | `EmbeddingAdapter.embed_one()` succeeds | Flag unhealthy; retrieval cannot function |
| Cross-encoder loaded (Phase 2+) | Cross-encoder model responds | Flag degraded; Self-RAG skipped |

## Security and threat analysis

This section addresses security concerns specific to the retrieval
subsystem per STD-007. It is integrated into the module design rather
than maintained as a separate document.

### Assets

| Asset | Sensitivity | Location |
|-------|------------|----------|
| Query content | May contain sensitive context from agent conversations | In-memory during pipeline execution; logged (with scrubbing) |
| Retrieved memory records | Varying access levels (public through sensitive) | Fetched from PostgreSQL; filtered by access control |
| Retrieval feedback data | Usage patterns reveal agent behavior | Persisted asynchronously (Phase 3+) |
| Embedding vectors | Can be inverted to approximate source text | Stored in pgvector; same trust boundary as source records |
| Query result cache | Contains previously retrieved records | In-memory; scoped to authenticated identity |

### Trust boundaries

```text
EXTERNAL (untrusted)
  Agent query via MCP/A2A
        |
        | Authenticated token + agent identity
        v
PROTOCOL LAYER (auth + rate limiting)
        |
        | AgentContext (validated identity, trust level)
        v
RETRIEVAL SUBSYSTEM (this module)
        |                    |                    |
        v                    v                    v
   Memory subsystem    Infrastructure       Infrastructure
   (record access)     (pgvector, FTS)      (KG, embedding)
```

Agent identity is propagated through the entire pipeline. Every database
query includes the agent's access level as a filter predicate. No record
is returned to an agent without passing the access control check in
Stage 3.

### Attack vectors and mitigations

| Threat | Vector | Impact | Mitigation |
|--------|--------|--------|------------|
| Adversarial content in results | Poisoned memory records surface in retrieval | Agent behavior manipulation via injected instructions | Confidence thresholds filter low-trust records; Self-RAG validation (Phase 2) scores relevance; access control limits exposure |
| Information leakage across trust boundaries | Agent A retrieves records scoped to Agent B | Unauthorized data access | Access control check in Stage 3 validation; agent identity propagated through pipeline; cache keyed on agent identity |
| Denial of service via expensive queries | Deliberately complex multi-hop or exploratory queries | Resource exhaustion, latency spike | Query complexity limits (max result count, max traversal depth); per-stage timeouts; circuit breakers; rate limiting at protocol layer |
| Graph traversal amplification | Crafted query triggers exponential graph traversal | CPU and memory exhaustion | PageRank iteration limits (`max_iter=100`); max traversal depth (4 hops); max nodes visited (1000); stage-level timeout (500ms) |
| Embedding inversion attack | Attacker with vector access reconstructs source text | Sensitive data disclosure | Vectors stored in same trust boundary as source records; no direct vector API exposure; access control enforced before vector retrieval |
| Feedback loop poisoning (Phase 3) | Manipulated feedback corrupts RL training data | Degraded retrieval quality over time | Feedback accepted only from authenticated agents; anomaly detection on feedback patterns; RL model validated against heuristic baseline before deployment |
| Cache poisoning | Tampered cache returns incorrect results | Incorrect information served to agent | Cache keyed on authenticated identity plus query; cache TTL limits exposure window; cache invalidated on memory write events |
| Query content exfiltration | Logged queries expose sensitive agent context | Privacy violation | Query log retention policy; PII scrubbing in structured logs; access control on log storage; query text not included in metrics |

### Security controls summary

1. **Access control enforcement**: Every candidate passes an access level
   check in Stage 3. No record with an access level above the agent's
   authorization is returned. This is a hard filter -- never bypassed.

2. **Identity propagation**: Agent identity from the protocol layer is
   threaded through every stage. Database queries include agent scope
   predicates. Cache entries are scoped to agent identity.

3. **Input bounds**: Query text length is bounded. Result limits are
   capped. Graph traversal is bounded by depth, node count, and timeout.
   These limits prevent resource exhaustion from malicious input.

4. **Log hygiene**: Query text is scrubbed of potential PII before
   logging. Embedding vectors are never logged. Metrics labels do not
   contain query content.

## Constraints and assumptions

### Constraints

| ID | Constraint | Source |
|----|-----------|--------|
| C1 | Python 3.12, async-first | Charter |
| C2 | Single-node deployment (Docker Compose) | Charter |
| C3 | No external API calls for retrieval (local-first) | System design axiom 1 |
| C4 | Self-RAG must use local model inference, not LLM API calls | ADR-011; latency and cost constraints |
| C5 | Import boundaries enforced by import-linter | ADR-001 |
| C6 | Circuit breakers at all infrastructure boundaries | ADR-001 |
| C7 | All retrieval operations must complete within 3s hard ceiling | System design NFR |

### Assumptions

| ID | Assumption | Validation |
|----|-----------|------------|
| A1 | pgvector HNSW is sufficient for vector search at less than 500K records | Benchmark at Phase 1 completion |
| A2 | Postgres FTS provides adequate BM25 quality without a dedicated search engine | Benchmark at Phase 1 completion |
| A3 | NetworkX handles the knowledge graph at prototype scale (less than 500K edges) | Monitor memory usage in Phase 2 |
| A4 | RRF with `k=60` provides good fusion quality across strategies | Evaluate precision at Phase 1, tune `k` if needed |
| A5 | Cross-encoder model fits in memory alongside the application | Validate model size against 4GB RSS target |
| A6 | Heuristic routing in Phase 1 is good enough for basic retrieval | Track routing accuracy via metrics; improve in Phase 3 |
| A7 | 60-second cache TTL is appropriate for memory retrieval | Tune based on write frequency and staleness tolerance |

## Explicit non-responsibilities

The retrieval subsystem does **not** handle:

- **Memory writes or mutations**: All writes go through the Librarian
  Gate in the Memory subsystem (ADR-012). Retrieval is read-only.
- **Embedding model management**: Model loading, swapping, and
  re-embedding are managed by the Infrastructure layer via the
  `EmbeddingAdapter` Protocol (ADR-007). Retrieval consumes embeddings.
- **Knowledge graph construction**: Edge creation and graph maintenance
  are managed by the Memory subsystem (ADR-009). Retrieval traverses
  the graph read-only.
- **Authentication and rate limiting**: These are protocol-layer concerns
  handled before the query reaches the retrieval subsystem. Retrieval
  receives an already-authenticated `AgentContext`.
- **Memory consolidation**: The CLS consolidation engine (ADR-010) is
  part of the Memory subsystem. Retrieval queries consolidated records
  but does not trigger or manage consolidation.
- **Notification dispatch**: If retrieval detects conditions worth
  reporting (e.g., persistent low hit rates), it emits metrics. The
  Autonomy subsystem monitors those metrics and dispatches notifications.

## Definition of done

- [ ] Aligned to approved system design (3NGRAM-SD-001), specifically
  the Data flow: read path section and Performance and scalability targets
- [ ] All four constituent modules (`router.py`, `search.py`,
  `validation.py`, `assembly.py`) have clear interfaces and
  responsibilities
- [ ] 6-stage pipeline documented with inputs, outputs, and phase
  availability per stage
- [ ] Latency budget allocated per stage with measurable targets
- [ ] Bounded retry strategy defined with escalation levels
- [ ] RRF fusion formula specified with configurable constant
- [ ] Circuit breaker and timeout strategy defined per stage
- [ ] Security and threat analysis embedded per STD-007
- [ ] All observability signals defined with metric names, types, labels,
  and phases
- [ ] Health checks defined for all infrastructure dependencies
- [ ] Import boundary rules documented and aligned with import-linter
  configuration
- [ ] Applicable sections of Design Review Checklist (STD-024) completed
- [ ] Links to related ADRs, system design, and specs captured

## Links

- **System design**: [3NGRAM-SD-001](./system-design.md) -- Data flow:
  read path, Non-Functional Requirements (Performance and scalability),
  HippoRAG Index, Adaptive Query Router, Self-RAG Reflection sections
- **ADR-011**: [HippoRAG retrieval pipeline](../architecture/adr/ADR-011-hipporag-retrieval.md) --
  primary input for this module design
- **ADR-009**: [Knowledge graph Phase 2](../architecture/adr/ADR-009-knowledge-graph-phase2.md) --
  KG traversal, edge types, Personalized PageRank
- **ADR-007**: [Embedding adapter](../architecture/adr/ADR-007-embedding-adapter.md) --
  `EmbeddingAdapter` Protocol for query embedding
- **ADR-003**: [Storage backend](../architecture/adr/ADR-003-storage-backend.md) --
  Postgres+pgvector, HNSW indexing, hybrid search via RRF
- **ADR-001**: [Monolith-first](../architecture/adr/ADR-001-monolith-first.md) --
  circuit breakers, retries, import boundaries
- **ADR-010**: [CLS consolidation](../architecture/adr/ADR-010-cls-consolidation.md) --
  temporal decay function, consolidation path field
- **ADR-012**: [Hybrid Librarian Gate](../architecture/adr/ADR-012-hybrid-librarian-gate.md) --
  feedback signal consumer for RL training
- **Schema definitions**: `docs/design/schemas/` (pending)
- **Technical specification**: `docs/specs/` (pending)

# Implementation Notes

- Keep this module design focused on the `engram.retrieval` package.
  Avoid specifying internal implementation details beyond what is needed
  to clarify intent and enforce boundaries.
- The pipeline is implemented as a chain of async functions, not a class
  hierarchy. Each stage is a function that takes the previous stage's
  output and returns the next stage's input.
- Stage 2 parallelism uses `asyncio.gather()` with
  `return_exceptions=True` so that a single strategy failure does not
  abort the others.
- The Self-RAG cross-encoder in Phase 2 must be a local model loaded at
  startup, not an LLM API call. The latency budget of less than 50ms
  per candidate rules out any network-based inference.
- Phase 3 RL components (distiller, learned router) are additive. The
  Phase 1-2 heuristics remain as fallback and are not removed.
- Retry budget is tracked per query invocation. Partial results include
  a `retrieval_confidence` score reflecting degraded quality.

# Continuous Improvement and Compliance Metrics

## Module quality metrics

| Metric | Target | Frequency |
|--------|--------|-----------|
| End-to-end retrieval latency (p95) | < 500ms (Phase 1), < 1s (Phase 2), < 2s (Phase 2 + KG) | Continuous monitoring |
| Retrieval hit rate | > 90% | Continuous monitoring |
| Retrieval precision at k=10 | > 0.80 (Phase 1), > 0.90 (Phase 2) | Quarterly evaluation |
| Multi-hop query success rate | > 70% (Phase 2) | Quarterly evaluation |
| Retry rate | < 10% of queries | Continuous monitoring |
| Circuit breaker trip rate | < 1% per hour | Continuous monitoring |
| Self-RAG inference latency (Phase 2) | < 50ms per candidate | Continuous monitoring |

## Review triggers

Review this module design when any of these signals appear:

- Retrieval latency consistently exceeds SLO targets
- Hit rate drops below 80%
- Retry rate exceeds 20%
- A new retrieval strategy (e.g., improved GraphRAG) shows significant
  quality gains in benchmarks
- Scale exceeds pgvector or NetworkX ceilings (500K records, 500K edges)
- Phase 3 RL components are ready for integration

# Compliance

This module design complies with:

- **STD-001** (Documentation Standard) -- seven mandatory sections
  present (Purpose, Scope, Standard, Implementation Notes, Continuous
  Improvement, Compliance, Changelog)
- **STD-022** (Module Design Standard) -- all 13 required subsections
  within Standard section populated per template
- **STD-007** (Security and Threat Modeling) -- security and threat
  analysis embedded in section 3 rather than maintained as a separate
  artifact
- **STD-020** (Design-First Development) -- module design precedes
  specification and implementation

Verified by: sh4i-yurei (draft -- pending review)
Date: 2026-02-13

# Changelog

## 0.1.0 -- 2026-02-13

**Added:**

- Initial module design for the `engram.retrieval` subsystem
- 6-stage HippoRAG pipeline with stage-level inputs, outputs, and phase
  availability
- Public interfaces: `RetrievalPipeline`, `RetrievalQuery`,
  `RetrievalResult`, `ScoredMemory`, `Provenance`, `ConflictPair`
- Latency budget allocation per stage with measurable targets
- Bounded retry strategy (3 attempts with escalating modifications)
- RRF fusion specification (`k=60`)
- Circuit breaker and timeout strategy per stage
- Security and threat analysis with 8 attack vectors and mitigations
- Observability signals: 11 metrics, structured log schema, 5 health
  checks
- Self-RAG specification: local cross-encoder in Phase 2, RL distiller
  in Phase 3
- Skip route definition with three skip reasons
- Import boundary rules aligned with import-linter configuration

**Status**: Draft -- pending design review and approval
