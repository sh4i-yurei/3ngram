---
id: 3NGRAM-MD-MEMORY-001
title: "Module Design: Memory Subsystem"
version: 0.1.0
category: project
status: draft
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-022]
tags: [design, module-design, memory, 3ngram]
---

# Module Design: Memory Subsystem

# Purpose

This module design defines the internal architecture, interfaces, and
responsibilities of `engram.memory` -- the Memory subsystem of the 3ngram
kernel. The Memory subsystem is the most critical subsystem: it owns all
typed memory storage, the Librarian Gate (write authorization), bi-temporal
versioning, conflict detection, and CLS-inspired consolidation.

This document is the authoritative reference for all implementation work
within `engram.memory`. It decomposes the system design (3NGRAM-SD-001)
memory components into module-level detail per STD-022.

# Scope

This design covers all modules within the `engram.memory` Python package:

| Module | File | Phase | Responsibility |
|---|---|---|---|
| Type Registry | `types.py` | 1 | 8 memory type schemas, MemoryRecord envelope, validation |
| Librarian Gate | `gate.py` | 1 | Write authorization: Layer 1 hard constraints + Layer 2 soft decisions |
| Gate Advisor | `gate_advisor.py` | 1 (stub), 3 (RL) | Heuristic then RL-trained soft decision advisor |
| Temporal Engine | `temporal.py` | 1 (basic), 2 (full) | Bi-temporal versioning, temporal queries, decay scoring |
| Conflict Resolver | `conflict.py` | 2 | Conflict detection, classification, and resolution |
| Consolidation Engine | `consolidation.py` | 1 (schema), 2 (full) | CLS dual-path memory consolidation |

**Out of scope**: Retrieval pipeline (`engram.retrieval`), agent role
definitions (`engram.agents`), protocol adapters (`engram.protocols`),
and infrastructure adapters (`engram.infra`). These are covered by their
own module designs.

# Standard

## 1. Module Purpose and Responsibility

The Memory subsystem is the **single owner of all memory state** in the
3ngram kernel. Every memory record -- regardless of origin (external agent,
internal consolidation, self-healing) -- is created, validated, versioned,
and stored exclusively through this subsystem.

Core responsibilities:

- **Type enforcement**: Define and validate the 8 memory types (Belief,
  Decision, Episode, Skill, Entity, Preference, Reflection, Resource)
  with type-specific schemas and the common MemoryRecord envelope.
- **Write authorization**: Enforce 100% write authorization through the
  Librarian Gate -- a two-layer policy engine with hard constraints
  (Layer 1) and soft decisions (Layer 2) per ADR-012.
- **Versioning**: Maintain bi-temporal version chains with optimistic
  concurrency control per system design section "Concurrency model".
- **Conflict detection**: Identify contradictions between memory records
  and classify them for resolution or escalation.
- **Consolidation**: Manage the CLS-inspired dual-path lifecycle (fast
  path and slow path) with scheduled, event-driven, and pressure-driven
  triggers per ADR-010.
- **Audit**: Log every Gate decision with full context for accountability
  and RL training data collection.

## 2. Inputs and Outputs

### Inputs

| Source | Input | Via |
|---|---|---|
| External agents | Memory write requests (CREATE, UPDATE) | Protocol adapter calling `gate.evaluate()` |
| External agents | Memory forget requests (soft-delete) | Protocol adapter calling `gate.evaluate()` with `FORGET` action |
| Consolidation Engine | Consolidated records, status transitions | Internal call to `gate.evaluate()` with `decision_type=consolidation` |
| Self-healing (Autonomy) | Corrective writes (re-index, refresh) | Internal call to `gate.evaluate()` with `decision_type=self_healing` |
| Retrieval subsystem | Temporal queries, version lookups | Direct call to `temporal.query()` |
| Scheduler (Autonomy) | Consolidation trigger events | Call to `consolidation.run()` |

### Outputs

| Target | Output | Via |
|---|---|---|
| Infrastructure (PostgreSQL) | Persisted memory records, version chains | `engram.infra.db` adapter |
| Infrastructure (pgvector) | Embedding vectors | `engram.infra.embeddings` adapter |
| Infrastructure (KG) | Knowledge graph edges | `engram.infra.graph` adapter (Phase 2) |
| Event bus | `memory.created`, `memory.updated`, `memory.consolidated`, `memory.conflict_detected` | `engram.infra.events` |
| Retrieval subsystem | Temporal query results, version chain data | Return values from `temporal.query()` |
| Protocol adapters | Gate decision results (approved, rejected, conflict) | Return values from `gate.evaluate()` |
| Audit log | Gate decision records | Append to `librarian_audit` table |

## 3. Public Interfaces

### 3.1 Librarian Gate (`gate.py`)

The Gate is the single entry point for all write operations. No memory
record reaches storage without passing through `gate.evaluate()`.

```python
@dataclass
class GateRequest:
    """Input to the Librarian Gate."""
    action: GateAction              # CREATE | UPDATE | FORGET
    record: MemoryRecord            # proposed record
    caller_identity: CallerIdentity # agent token + trust level
    decision_type: GateDecisionType # external | consolidation | self_healing
    expected_version: int | None    # required for UPDATE

@dataclass
class GateResult:
    """Output from the Librarian Gate."""
    decision: GateDecision          # APPROVED | REJECTED | CONFLICT
    decision_id: UUID               # audit reference
    reason: str                     # human-readable explanation
    layer1_checks: list[CheckResult]
    layer2_decision: AdvisorDecision | None
    modified_record: MemoryRecord | None  # record with Gate modifications

class LibrarianGate:
    async def evaluate(self, request: GateRequest) -> GateResult: ...
```

**Internal write path**: Both external writes (from agents via protocol
adapters) and internal writes (from consolidation and self-healing) call
`gate.evaluate()`. Internal writes are distinguished by
`decision_type = consolidation | self_healing` and follow a modified
Layer 1 pipeline:

- **Schema validation**: Always applied (all origins).
- **PII screening**: Always applied (all origins).
- **Classification enforcement**: Always applied (all origins).
- **Access control**: Skipped for internal origins -- consolidation and
  self-healing operate with system-level authority.
- **Rate limiting**: Skipped for internal origins -- internal processes
  are self-throttled by the scheduler.

Layer 2 soft decisions are applied to all origins. For consolidation
writes, the advisor evaluates consolidation routing and conflict
classification rather than ADD/UPDATE/NOOP decisions.

### 3.2 Type Registry (`types.py`)

```python
class MemoryType(StrEnum):
    BELIEF = "belief"
    DECISION = "decision"
    EPISODE = "episode"
    SKILL = "skill"
    ENTITY = "entity"
    PREFERENCE = "preference"
    REFLECTION = "reflection"
    RESOURCE = "resource"

class AccessLevel(StrEnum):
    PUBLIC = "public"
    AGENT = "agent"
    USER = "user"
    SYSTEM = "system"
    SENSITIVE = "sensitive"

class GateDecisionType(StrEnum):
    EXTERNAL = "external"
    CONSOLIDATION = "consolidation"
    SELF_HEALING = "self_healing"

@dataclass
class MemoryRecord:
    id: UUID
    type: MemoryType
    content: str
    metadata: dict
    version: int                        # starts at 1
    superseded_by: UUID | None

    # Provenance
    source_agent: str
    source_confidence: float            # observed: 0.9, told: 0.75, inferred: 0.6
    evidence_links: list[UUID]

    # Bi-temporal versioning
    event_time: datetime                # when true in real world
    ingestion_time: datetime            # when kernel learned it

    # Governance
    access_level: AccessLevel
    classification: str | None
    gate_decision_id: UUID
    gate_decision_type: GateDecisionType

    # Concurrency
    expected_version: int | None        # optimistic lock (required on UPDATE)

    # Lifecycle
    created_at: datetime
    updated_at: datetime
    decay_score: float                  # relevance decay (0.0-1.0)
    consolidation_path: str             # "fast" or "slow"
```

Each memory type has a type-specific validation schema (Pydantic model)
that extends the common envelope. Type-specific rules are enforced in
the Gate Layer 1 schema validation check.

### 3.3 Temporal Engine (`temporal.py`)

```python
class TemporalEngine:
    async def query(
        self,
        *,
        record_id: UUID | None = None,
        as_of_event: datetime | None = None,
        as_of_ingestion: datetime | None = None,
        include_superseded: bool = False,
    ) -> list[MemoryRecord]: ...

    async def get_version_chain(self, record_id: UUID) -> list[MemoryRecord]: ...

    async def compute_decay(self, record_id: UUID) -> float: ...
```

Bi-temporal queries support two time dimensions:

- **Event time** (`as_of_event`): "What did we know was true at this
  real-world time?"
- **Ingestion time** (`as_of_ingestion`): "What did the kernel know at
  this system time?"

### 3.4 Conflict Resolver (`conflict.py`)

```python
class ConflictClassification(StrEnum):
    CONTRADICTION = "contradiction"     # mutually exclusive claims
    SUPERSESSION = "supersession"       # newer replaces older
    REFINEMENT = "refinement"           # newer adds detail to older
    UNRESOLVABLE = "unresolvable"       # requires human judgment

class ConflictResolver:
    async def detect(
        self, record: MemoryRecord, existing: list[MemoryRecord]
    ) -> list[ConflictResult]: ...

    async def resolve(
        self, conflict: ConflictResult
    ) -> ResolutionResult: ...
```

Conflict detection runs as part of Gate Layer 2 evaluation. When
conflicts are classified as `UNRESOLVABLE`, they are escalated to the
notification dispatcher for human review.

### 3.5 Consolidation Engine (`consolidation.py`)

```python
class ConsolidationTrigger(StrEnum):
    SCHEDULED_DEEP = "scheduled_deep"       # nightly full sweep
    SCHEDULED_LIGHT = "scheduled_light"     # hourly recent-only
    EVENT_DRIVEN = "event_driven"           # related memories past threshold
    PRESSURE_DRIVEN = "pressure_driven"     # fast path count exceeded

class ConsolidationEngine:
    async def run(self, trigger: ConsolidationTrigger) -> ConsolidationReport: ...
    async def evaluate_candidates(self) -> list[ConsolidationCandidate]: ...
```

Consolidation writes flow through the Gate with
`decision_type = consolidation`. The engine creates new consolidated
records, sets `derived_from` edges on sources, and transitions source
record status to `consolidated` via `superseded_by`. All operations
within a single consolidation batch execute in one PostgreSQL
transaction.

### 3.6 Gate Advisor (`gate_advisor.py`)

```python
class GateAdvisor(Protocol):
    """Layer 2 soft decision advisor."""
    async def advise(
        self, record: MemoryRecord, context: AdvisorContext
    ) -> AdvisorDecision: ...

class HeuristicAdvisor:
    """Phase 1: rule-based heuristic advisor."""
    async def advise(
        self, record: MemoryRecord, context: AdvisorContext
    ) -> AdvisorDecision: ...

class RLAdvisor:
    """Phase 3: RL-trained advisor (GRPO on accumulated decision data)."""
    async def advise(
        self, record: MemoryRecord, context: AdvisorContext
    ) -> AdvisorDecision: ...
    async def train(self, batch: list[TrainingExample]) -> TrainResult: ...
```

The `GateAdvisor` Protocol allows hot-swapping between heuristic and
RL-trained implementations. Both implementations are called through the
same Gate Layer 2 interface. The RL advisor is trained on accumulated
interaction data where the reward signal comes from downstream retrieval
feedback -- memories that get retrieved and rated useful reinforce
the storage decisions that admitted them (per ADR-012).

## 4. Dependencies

### Internal dependencies (within engram)

| Dependency | Usage | Interface |
|---|---|---|
| `engram.infra.db` | PostgreSQL read/write, transactions | `DatabaseAdapter` Protocol |
| `engram.infra.embeddings` | Embedding generation on write | `EmbeddingAdapter` Protocol (ADR-007) |
| `engram.infra.graph` | KG edge creation (Phase 2) | `GraphAdapter` Protocol (ADR-009) |
| `engram.infra.events` | Event emission post-write | `EventBus` Protocol |
| `engram.config` | Gate policy configuration, thresholds | `Settings` (Pydantic BaseSettings) |

### External dependencies

| Dependency | Usage | Resilience |
|---|---|---|
| PostgreSQL + pgvector | Record storage, vector storage, full-text search | Circuit breaker (aiobreaker), retry (tenacity) per ADR-001 |
| fastembed (Phase 1 default) | Embedding generation | `ProcessPoolExecutor` bulkhead, timeout, fallback to degraded mode |

### Import boundary rules (import-linter)

Per ADR-001 and system design section "Module/package mapping":

- `engram.memory` MUST NOT import from `engram.protocols`
- `engram.memory` MUST NOT import from `engram.agents` (agents depend
  on memory, not the reverse)
- `engram.memory` depends on `engram.infra` only through Protocol
  interfaces (no concrete class imports)
- `engram.memory` MUST NOT import from `engram.retrieval` (retrieval
  depends on memory, not the reverse)
- `engram.retrieval` MAY import from `engram.memory.types` (type
  definitions) and `engram.memory.temporal` (bi-temporal queries,
  version chain lookups) -- but MUST NOT import from `engram.memory.gate`
  or `engram.memory.consolidation`

## 5. Internal Responsibilities

### 5.1 Gate Layer 1: Hard Constraints

Layer 1 runs first on every write. If any check fails, the write is
rejected regardless of Layer 2 output. These checks are **never
overridden by RL** (per ADR-012).

| Check | Description | Applies to |
|---|---|---|
| Schema validation | Record conforms to MemoryRecord envelope + type-specific schema | All origins |
| Access control | Caller has write permission for this memory type and access level | External only |
| PII screening | Best-effort regex detection (Phase 1); flag as `sensitive` if detected | All origins |
| Rate limiting | Per-agent write rate within configured threshold | External only |
| Classification enforcement | Memory type is valid and consistent with content indicators | All origins |

**PII screening detail**: PII detection is best-effort, not a hard
constraint on record acceptance. Phase 1 uses regex patterns for
structured PII (emails, phone numbers, government IDs, financial account
numbers, API keys/secrets). Detection triggers quarantine -- the record
is stored with `access_level = sensitive` rather than rejected. This
acknowledges that regex will miss contextual PII in narrative text.

Compensating controls (per system design section "PII screening model"):

1. **Quarantine by default**: Flagged records stored as `sensitive`
   pending review.
2. **Periodic batch rescan**: Scheduled job re-scans stored records with
   the current detector. Retroactive flags promote records to `sensitive`.
3. **PII propagation**: If a source record contains PII, all
   `derived_from` descendants in the consolidation chain are also
   promoted to `sensitive`.
4. **Scoped definition**: For this single-user system, PII covers email
   addresses, phone numbers, government IDs, financial account numbers,
   and API keys/secrets. Names and locations in project context are not
   treated as PII unless the user configures stricter rules.

### 5.2 Gate Layer 2: Soft Decisions

Layer 2 produces advisory decisions that are always logged but may be
overridden by future RL training. Phase 1 uses the `HeuristicAdvisor`;
Phase 3 transitions to the `RLAdvisor`.

| Decision | Description |
|---|---|
| ADD / UPDATE / NOOP | Should this memory be stored as new, merged with existing, or discarded? |
| Conflict classification | Is this memory consistent with, contradicting, or superseding existing records? |
| Consolidation routing | Should this memory be flagged for immediate consolidation? |
| Confidence calibration | What confidence score should be assigned? |
| Importance scoring | How important is this memory relative to others? |

### 5.3 Optimistic Concurrency Control

All write operations use optimistic concurrency to prevent version chain
corruption (per system design section "Concurrency model"):

- **UPDATE operations**: Require `expected_version` matching the current
  record version. If the version has changed since the caller read it,
  the Gate returns a `CONFLICT` result. The caller must re-read and
  retry -- the Gate does not auto-merge.
- **Consolidation status transitions**: Use
  `SELECT ... FOR UPDATE` within the transaction to lock source records
  during status change. This prevents an agent update from racing with
  consolidation marking.
- **Version chain atomicity**: Inserting a new version and setting
  `superseded_by` on the previous version happen within a single
  PostgreSQL transaction at `READ COMMITTED` isolation.

### 5.4 CLS Dual-Path Consolidation

Per ADR-010, memory records exist on one of two paths:

**Fast path (hippocampal)**:

- All new records land here immediately at full fidelity.
- Subject to temporal decay -- relevance score decreases over time
  unless reinforced by retrieval access.
- Queryable immediately. High recall, low precision.
- Decay function: `relevance = base_relevance * exp(-lambda * days_since_last_access)`
  where `lambda` is configurable per memory type.

**Slow path (neocortical)**:

- Populated by the Consolidation Engine from promoted fast-path records.
- Generalized, compressed, cross-referenced. High precision, lower recall.
- Extremely durable -- not subject to aggressive decay.

**Consolidation triggers**:

1. **Scheduled deep** (nightly): Full sweep of fast-path records.
   Configurable hour (`ENGRAM_CONSOLIDATION_HOUR`, default 03:00 UTC).
2. **Scheduled light** (hourly): Recent fast-path records only.
3. **Event-driven**: When related memories accumulate past a threshold
   (default: 5+ records about the same topic, detected via
   `relates_to` edges).
4. **Pressure-driven**: When fast-path active record count exceeds a
   configured limit (default: 10,000).

**Consolidation actions**:

- Merge related episodes into narrative summaries.
- Promote repeated observations to beliefs (with confidence scores).
- Extract skills from episode patterns.
- Compress verbose records while preserving key information.
- Create `derived_from` edges from consolidated records to sources.
- Create `supersedes` edges when a consolidated record replaces older
  versions.
- Mark source records with `consolidated` status.

**Reversibility**: Original records are never deleted during
consolidation. They are marked `consolidated` and linked via edges.
Rollback follows `derived_from` edges back to sources.

### 5.5 Audit Trail

Every Gate decision is recorded in the `librarian_audit` table:

- Input record (full snapshot)
- Layer 1 check results (pass/fail per check, with details)
- Layer 2 decision and rationale
- Decision source (heuristic rule version or RL model version)
- Caller identity and decision type
- Timestamp

The audit table is **append-only** -- no UPDATE or DELETE operations are
permitted. This is enforced at the database permission level (separate
role for audit writes).

## 6. Error and Failure Modes

| Failure | Detection | Response | Recovery |
|---|---|---|---|
| Schema validation failure | Layer 1 check | Reject write, return validation errors | Caller fixes and resubmits |
| Version conflict (optimistic lock) | `expected_version` mismatch | Return `CONFLICT` result | Caller re-reads current version and retries |
| Consolidation race | `SELECT ... FOR UPDATE` blocked or version mismatch | Consolidation batch item skipped | Re-evaluated in next consolidation run |
| PostgreSQL connection failure | Circuit breaker trip (aiobreaker) | Writes queued or rejected with retry hint | Automatic retry with exponential backoff (tenacity) |
| Embedding generation timeout | Timeout on `EmbeddingAdapter.embed_one()` | Record stored without embedding (degraded mode) | Background job re-embeds on adapter recovery |
| PII detector error | Exception in regex engine | Record proceeds with `sensitive` classification (fail-safe) | Log error for investigation |
| Consolidation job timeout | Job exceeds configured duration limit | Job terminates, partial progress committed | Remaining items picked up in next run |
| Audit log write failure | Exception on `librarian_audit` insert | Primary write still proceeds; audit failure logged to stderr | Compensating audit backfill job |
| Gate Advisor failure (Phase 3) | RL model prediction error | Fall back to `HeuristicAdvisor` | Log error, retrain on next cycle |

**Circuit breaker configuration** (per ADR-001):

- Failure threshold: 5 consecutive failures
- Recovery timeout: 30 seconds
- Half-open probes: 1 request

**Retry configuration** (per ADR-001):

- Max retries: 3
- Backoff: exponential (1s, 2s, 4s)
- Retry on: connection errors, transient database errors
- Do not retry on: validation errors, conflict errors

## 7. Non-Functional Considerations

### Performance targets (Phase 1, < 100K records)

| Metric | Target | Source |
|---|---|---|
| Gate evaluation latency (p95) | < 200ms (auto-approve path) | System design NFR |
| Write latency end-to-end (p95) | < 500ms (Gate + persist + embed) | System design NFR |
| Embedding generation (p95) | < 500ms per record (CPU) | System design NFR |
| Version chain lookup | < 50ms for chains up to 100 versions | Derived |
| Consolidation batch (nightly) | < 30 minutes for 10K candidates | ADR-010 |

### Scalability

- Single PostgreSQL instance handles up to ~500K records (ADR-003
  ceiling estimate).
- Consolidation batch size configurable
  (`ENGRAM_CONSOLIDATION_BATCH_SIZE`, default 100).
- Embedding generation bulkheaded via `ProcessPoolExecutor` (ADR-001)
  to prevent blocking the async event loop.
- Version chains are bounded in practice by consolidation -- deep chains
  indicate records that should be consolidated.

### Data integrity

- All write operations are wrapped in PostgreSQL transactions at
  `READ COMMITTED` isolation.
- Version chain mutations (insert new + set `superseded_by` on old) are
  atomic within a single transaction.
- Consolidation batch operations (create consolidated + mark sources +
  create edges) are atomic within a single transaction.
- The audit table uses a separate database role with INSERT-only
  permissions.

## 8. Observability and Signals

### Metrics (Prometheus client)

| Metric | Type | Labels | Description |
|---|---|---|---|
| `engram_gate_decisions_total` | Counter | `decision` (approved/rejected/conflict), `decision_type` (external/consolidation/self_healing) | Gate approval/rejection rate |
| `engram_gate_evaluation_seconds` | Histogram | `decision_type` | Gate evaluation latency |
| `engram_write_seconds` | Histogram | `decision_type` | End-to-end write latency by decision type |
| `engram_memory_records_total` | Gauge | `type` (8 memory types), `consolidation_path` (fast/slow) | Record count by type and path |
| `engram_version_chain_depth` | Histogram | -- | Version chain depth distribution |
| `engram_pii_flags_total` | Counter | `detector` (regex/ner) | PII detection flags per period |
| `engram_consolidation_duration_seconds` | Histogram | `trigger` (scheduled_deep/scheduled_light/event_driven/pressure_driven) | Consolidation job duration |
| `engram_conflicts_detected_total` | Counter | `classification` (contradiction/supersession/refinement/unresolvable) | Conflict detection rate |
| `engram_decay_score` | Histogram | `type` | Decay score distribution across memory types |
| `engram_gate_layer1_failures_total` | Counter | `check` (schema/access/pii/rate_limit/classification) | Layer 1 check failure breakdown |

### Structured logging (structlog, JSON)

All Gate decisions are logged with structured fields:

- `event`: `gate.evaluate`, `gate.layer1`, `gate.layer2`
- `decision_id`: UUID
- `decision_type`: external/consolidation/self_healing
- `action`: CREATE/UPDATE/FORGET
- `memory_type`: one of 8 types
- `decision`: approved/rejected/conflict
- `duration_ms`: evaluation time
- `caller`: agent identity (redacted in logs above `agent` access level)

Consolidation events:

- `event`: `consolidation.started`, `consolidation.completed`,
  `consolidation.item_processed`, `consolidation.error`
- `trigger`: trigger type
- `batch_size`: number of candidates
- `duration_ms`: total duration
- `items_consolidated`: count of records processed

### Health checks

| Check | Method | Healthy condition |
|---|---|---|
| Database connectivity | `SELECT 1` on primary connection | Response within 5 seconds |
| Gate responsiveness | Gate processes a synthetic no-op request | Response within 200ms |
| Pending consolidation backlog | Count of fast-path records past decay threshold | Below 2x configured limit |
| Audit log writability | Test INSERT to `librarian_audit` | INSERT succeeds within 1 second |

## 9. Constraints and Assumptions

### Constraints

| ID | Constraint | Source |
|---|---|---|
| C1 | All writes -- external and internal -- must pass through the Librarian Gate | System design, ADR-012 |
| C2 | Layer 1 hard constraints are never overridden by RL | ADR-012 |
| C3 | Python 3.12 runtime | Charter |
| C4 | PostgreSQL + pgvector as sole persistence backend (Phase 1-2) | ADR-003 |
| C5 | Local-first embedding -- no external API calls | System design axiom |
| C6 | Single-user deployment (Phase 1-4) | Charter |
| C7 | Design-first -- no implementation before approved spec | STD-020 |
| C8 | Import boundaries enforced by import-linter | ADR-001 |

### Assumptions

| ID | Assumption | Validation |
|---|---|---|
| A1 | PostgreSQL transactions at `READ COMMITTED` provide sufficient isolation for the optimistic concurrency model | Integration tests with concurrent write scenarios |
| A2 | Regex-based PII detection catches >80% of structured PII patterns in development context | Evaluation against test corpus at Phase 1 completion |
| A3 | Fast-path record count stays below 10K during Phase 1 (consolidation not yet active) | Monitoring via `engram_memory_records_total` gauge |
| A4 | Consolidation batch sizes of 100 records are processable within the nightly window | Benchmark at Phase 2 completion |
| A5 | Heuristic advisor produces >80% agreement with expert judgment | Monthly evaluation per ADR-012 |
| A6 | Embedding generation at <500ms CPU is achievable with fastembed and bge-small-en-v1.5 | Benchmark at Phase 1 |

## 10. Explicit Non-Responsibilities

The Memory subsystem does NOT:

- **Execute retrieval queries**: The Retrieval subsystem
  (`engram.retrieval`) owns query routing, candidate scoring, and result
  assembly. The Memory subsystem provides temporal queries and version
  chain lookups as inputs to retrieval, but does not rank or score
  results.
- **Manage agent identity or authentication**: Agent registration, token
  management, and trust level assignment are owned by the Protocol
  layer. The Memory subsystem receives a validated `CallerIdentity` and
  enforces access control based on it.
- **Schedule consolidation jobs**: The Autonomy subsystem
  (`engram.autonomy.scheduler`) owns job scheduling. The Consolidation
  Engine provides `run(trigger)` and the scheduler calls it at the
  appropriate times.
- **Generate notifications**: Conflict escalations and consolidation
  reports are emitted as events on the internal bus. The Notification
  subsystem (`engram.notifications`) decides delivery.
- **Own embedding model selection**: The Embedding Adapter
  (`engram.infra.embeddings`) owns model lifecycle per ADR-007. The
  Memory subsystem calls `embed_one()` / `embed_batch()` through the
  adapter interface.
- **Build or traverse the knowledge graph**: The Graph Adapter
  (`engram.infra.graph`) owns graph operations per ADR-009. The Memory
  subsystem creates edges during writes; graph traversal for retrieval
  is owned by `engram.retrieval`.

## 11. Security and Threat Analysis

This section provides the embedded threat analysis for the Memory
subsystem per STD-007. It replaces a standalone threat model for this
module's scope.

### Assets

| Asset | Sensitivity | Description |
|---|---|---|
| Memory records (8 types) | Varies by type and access level | Core knowledge store; Belief and Decision types may contain strategic information |
| Version chains | High integrity | Supersession links form the audit trail of knowledge evolution |
| Gate decision audit log | High integrity | Append-only accountability record for all write decisions |
| PII-containing records | High confidentiality | Records flagged as `sensitive` containing personal or credential data |
| Consolidation lineage | Medium integrity | `derived_from` edges linking consolidated records to their sources |

### Trust boundaries

```text
EXTERNAL (untrusted until authenticated)
  MCP clients / A2A peer agents
         |
         | validated CallerIdentity
         v
PROTOCOL LAYER (auth + rate limiting)
         |
         | GateRequest with decision_type=external
         v
MEMORY SUBSYSTEM (this module)
  Librarian Gate --> Layer 1 --> Layer 2
         |
         | GateRequest with decision_type=consolidation|self_healing
         |
  INTERNAL SUBSYSTEMS (consolidation, self-healing)
         |
         | Infrastructure adapter calls
         v
INFRASTRUCTURE LAYER (PostgreSQL, pgvector)
```

Three trust boundaries cross the Memory subsystem:

1. **External agent to Memory subsystem**: Crosses via Protocol layer.
   The Memory subsystem receives validated tokens but must still enforce
   access control and rate limiting in Gate Layer 1.
2. **Internal subsystems to Memory subsystem**: Consolidation and
   self-healing call the Gate with elevated authority
   (`decision_type != external`). These skip access control and rate
   limiting but must pass schema validation and PII screening.
3. **Memory subsystem to Infrastructure**: All database operations go
   through adapter interfaces. The Memory subsystem trusts the database
   for durability but not for authorization logic.

### Attack vectors and mitigations

| Threat | Vector | Impact | Mitigation |
|---|---|---|---|
| Gate bypass | Bug in write path allows direct DB insert bypassing Gate | Data corruption, audit gap, PII leakage | Integration tests asserting all writes route through Gate; `import-linter` rules preventing `engram.infra.db` imports from `engram.protocols`; static analysis for raw SQL inserts outside Gate |
| Prompt injection via memory content | Adversarial text stored in memory, later retrieved and interpreted by agents | Agent behavior manipulation, information exfiltration | Content sanitization in Gate Layer 1; type-specific validation (e.g., Belief content must be declarative, not imperative); agent trust scoping limits read access |
| Version chain corruption | Race condition on concurrent version updates | Inconsistent version history, lost updates | Optimistic concurrency control with `expected_version`; atomic transactions for version chain mutations; `SELECT ... FOR UPDATE` on consolidation status transitions |
| PII screening bypass | Contextual PII not caught by regex patterns | Sensitive data stored at wrong access level, potential exposure | Quarantine-by-default (`sensitive` classification on detection); periodic batch rescan with improving detectors; PII propagation tracking through consolidation chains; NER upgrade path in Phase 2 |
| Consolidation data integrity | Consolidation produces incorrect summaries or loses key information | Knowledge corruption, degraded retrieval quality | Reversibility -- source records preserved, never deleted; `derived_from` edges for full audit trail; consolidation quality metrics; manual rollback via edge traversal |
| Decay score manipulation | Malicious agent repeatedly accesses records to artificially prevent decay | Storage bloat, stale records persist indefinitely | Decay scoring uses access frequency with diminishing returns, not raw count; access-based reinforcement capped per period; decay floor ensures eventual consolidation pressure |
| Audit log tampering | Modify or delete Gate decision records to hide unauthorized writes | Loss of accountability, inability to retrain RL advisor | Append-only audit table enforced by database permissions (INSERT-only role); no UPDATE or DELETE granted on `librarian_audit`; separate connection credentials for audit writes |
| Memory flooding | High-volume writes from a single agent to exhaust storage or degrade performance | Denial of service, storage exhaustion | Rate limiting in Gate Layer 1 (token bucket per agent); per-agent write quotas configurable in Gate policy; storage pressure monitoring triggers pressure-driven consolidation |
| Type confusion | Submit a record with mismatched type and content to bypass type-specific validation | Weakened validation, inconsistent knowledge store | Layer 1 schema validation enforces type-content consistency; type-specific Pydantic models validate content structure |
| Privilege escalation via decision_type | External caller sets `decision_type=consolidation` to bypass access control | Unauthorized writes with elevated authority | `decision_type` is set by the protocol adapter based on call origin, never from caller-supplied input; internal-only code paths validated by import-linter boundaries |

### Residual risks

| Risk | Severity | Acceptance rationale |
|---|---|---|
| Contextual PII missed by regex | Medium | Compensated by quarantine-by-default and batch rescan; NER upgrade in Phase 2 reduces residual risk |
| Consolidation quality (LLM-free summarization in Phase 1-2) | Low | Simple merge strategies only; reversibility preserves originals; quality metrics flag degradation |
| Single database as both data store and audit store | Low | Acceptable for single-user development tool; separate roles provide logical isolation; physical separation is a Phase 5 concern |

## 12. Definition of Done

The Memory subsystem module design is complete when:

1. **Type Registry**: All 8 memory type schemas defined as Pydantic
   models with type-specific validation rules. MemoryRecord envelope
   implemented with all fields from system design.
2. **Librarian Gate**: Layer 1 hard constraints implemented (schema,
   access control, PII screen, rate limiting, classification). Layer 2
   heuristic advisor implemented. Internal write path documented and
   tested (consolidation and self-healing origins).
3. **Temporal Engine**: Basic version chain support (create version,
   lookup chain, `superseded_by` linkage). Optimistic concurrency
   control enforced on UPDATE operations.
4. **Conflict Detection**: Basic contradiction detection between records
   of the same type. Conflict classification enum defined. Escalation
   path to notification dispatcher.
5. **Consolidation Engine**: Schema foundations in Phase 1
   (`consolidation_path` field, `memory_status` enum). Full
   implementation deferred to Phase 2.
6. **Gate Advisor**: `GateAdvisor` Protocol defined. `HeuristicAdvisor`
   implemented for Phase 1. `RLAdvisor` stub present for Phase 3.
7. **Audit Trail**: All Gate decisions logged to `librarian_audit`.
   Append-only enforcement verified.
8. **Observability**: All metrics from section 8 instrumented.
   Structured logging for Gate decisions and consolidation events.
   Health checks operational.
9. **Tests**: Unit tests for each module (>= 90% coverage). Integration
   tests for the full write path (external and internal). Concurrency
   tests for optimistic locking scenarios.
10. **Security**: All mitigations from section 11 implemented or
    tracked as explicit residual risks with compensating controls.

## 13. Links

### Parent artifacts

- System design: `docs/design/system-design.md` (3NGRAM-SD-001)

### Architecture decisions

- ADR-001: Monolith-first -- `docs/architecture/adr/ADR-001-monolith-first.md`
- ADR-003: Postgres + pgvector -- `docs/architecture/adr/ADR-003-storage-backend.md`
- ADR-007: Embedding adapter -- `docs/architecture/adr/ADR-007-embedding-adapter.md`
- ADR-008: Expanded agent architecture -- `docs/architecture/adr/ADR-008-expanded-agent-architecture.md`
- ADR-009: Knowledge graph Phase 2 -- `docs/architecture/adr/ADR-009-knowledge-graph-phase2.md`
- ADR-010: CLS consolidation -- `docs/architecture/adr/ADR-010-cls-consolidation.md`
- ADR-011: HippoRAG retrieval -- `docs/architecture/adr/ADR-011-hipporag-retrieval.md`
- ADR-012: Hybrid Librarian Gate -- `docs/architecture/adr/ADR-012-hybrid-librarian-gate.md`

### Downstream artifacts (pending)

- Technical specification: `docs/specs/memory-spec.md`
- Schema definitions: `docs/design/schemas/memory-schema.md`
- Module designs for dependent subsystems: `docs/design/module-retrieval.md`,
  `docs/design/module-autonomy.md`

### Standards

- STD-001: Documentation Standard
- STD-007: Security and Threat Modeling Standard
- STD-020: Design-First Development Model
- STD-022: Module Design Standard
- STD-055: Schema Definition Standard

# Implementation Notes

- Phase 1 delivers: Type Registry (full), Librarian Gate (Layer 1 +
  heuristic Layer 2), Temporal Engine (basic versioning), Gate Advisor
  (heuristic stub), audit trail, and consolidation schema foundations.
- Phase 2 delivers: Consolidation Engine (full), Conflict Resolver
  (full), Temporal Engine (bi-temporal queries, decay scoring),
  KG edge creation during writes.
- Phase 3 delivers: RL Gate Advisor (trained on Phase 1-2 interaction
  data), improved PII detection (NER-based).
- The `GateAdvisor` Protocol is the seam between Phase 1 heuristics and
  Phase 3 RL. Both implementations are tested against the same
  evaluation suite.
- All infrastructure access goes through adapter Protocols. No module in
  `engram.memory` imports concrete infrastructure classes.
- Circuit breaker and retry policies are configured in a shared
  `resilience.py` module per ADR-001.

# Continuous Improvement and Compliance Metrics

## Module quality metrics

| Metric | Target | Frequency |
|---|---|---|
| Unit test coverage (`engram.memory`) | >= 90% | Every CI run |
| Integration test coverage (write path) | >= 85% | Every CI run |
| Gate Layer 1 false positive rate | < 1% | Weekly review |
| Gate Layer 1 false negative rate (PII, access control) | 0% | Continuous monitoring |
| Layer 2 heuristic decision accuracy | > 80% agreement with expert judgment | Monthly evaluation |
| Audit log completeness | 100% of writes logged | Continuous monitoring |
| Consolidation information retention | > 95% key facts preserved | Monthly evaluation (Phase 2) |

## Review triggers

Review this module design when any of these signals appear:

- Gate evaluation latency exceeds 200ms p95 consistently
- Layer 1 false positive rate exceeds 5%
- Consolidation job duration exceeds 1 hour
- A new memory type is proposed (requires Type Registry extension)
- RL training data reaches 10K decision threshold (Phase 3 readiness)
- PII detection patterns miss a class of sensitive data

# Compliance

This document complies with:

- **STD-001** (Documentation Standard): All seven mandatory sections
  present (Purpose, Scope, Standard, Implementation Notes, Continuous
  Improvement, Compliance, Changelog).
- **STD-022** (Module Design Standard): All 13 required subsections
  within section 3 (Standard) populated per template.
- **STD-007** (Security and Threat Modeling Standard): Embedded threat
  analysis in section 11 covering assets, trust boundaries, attack
  vectors, mitigations, and residual risks.
- **STD-020** (Design-First Development): Module design precedes
  technical specification and implementation.

Verified by: sh4i-yurei (draft -- pending review)
Date: 2026-02-13

# Changelog

## 0.1.0 -- 2026-02-13

**Added:**

- Initial module design for `engram.memory` subsystem
- Type Registry with 8 memory types and MemoryRecord envelope
- Librarian Gate two-layer architecture (hard constraints + soft
  decisions) with internal write path for consolidation and self-healing
- Temporal Engine with bi-temporal versioning and optimistic concurrency
- Conflict Resolver with classification taxonomy
- CLS dual-path Consolidation Engine with trigger types and actions
- Gate Advisor Protocol with heuristic and RL implementations
- Embedded security and threat analysis per STD-007
- Observability signals (10 metrics, structured logging, 4 health checks)
- Definition of done with 10 acceptance criteria

**Status**: Draft -- pending review and approval
