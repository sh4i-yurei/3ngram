---
id: 3NGRAM-MD-004
title: "Module Design: Infrastructure"
version: 0.1.0
category: project
status: draft
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-022]
tags: [design, module-design, infrastructure, protocols, agents, 3ngram]
---

# Module Design: Infrastructure

# Purpose

This module design defines the infrastructure layer of 3ngram -- the
packages that sit below or alongside the kernel domain layer to provide
external protocol handling, agent role abstractions, persistence and
embedding adapters, and inter-component communication. Together, these
packages form the boundary between the kernel's domain logic and
everything external to it: callers, storage engines, embedding models,
and delivery channels.

# Scope

This is a composite module design covering four Python packages:

1. **`engram.protocols`** -- External protocol adapters (MCP server, A2A
   endpoint)
2. **`engram.agents`** -- Agent role definitions and lifecycle
   management
3. **`engram.infra`** -- Infrastructure adapters (database, embeddings,
   knowledge graph, event bus)
4. **`engram.notifications`** -- Communication layer for user-facing
   messages

Phase 1 scope includes all `protocols`, `agents`, and `infra` packages.
The `notifications` package is Phase 2 (webhook channel) with full
delivery channels in Phase 4.

This document does not cover the domain subsystems (`memory`,
`retrieval`, `autonomy`, `devenv`) -- those are separate module designs.

# Standard

## Module purpose and responsibility

The infrastructure module provides the kernel with four capabilities:

1. **Protocol translation** -- Convert MCP and A2A wire formats into
   domain operations and translate domain responses back to protocol
   format. External callers interact only with this layer.

2. **Agent abstraction** -- Define the `AgentRole` Protocol that all
   agent-like components implement. Provide lifecycle management
   (startup, shutdown, health, scheduling) and base implementations for
   the Phase 1 roles (Researcher, Librarian).

3. **Persistence and compute adapters** -- Abstract PostgreSQL, pgvector,
   embedding models, and the knowledge graph behind Protocol interfaces.
   Domain modules depend on these Protocols, never on concrete
   implementations.

4. **Communication routing** -- Dispatch notifications to the human
   operator through configured channels (CLI, webhook), with batching
   and priority filtering.

Success means: domain modules never import a concrete infrastructure
class, protocol changes never propagate past the adapter boundary, and
all adapter implementations are independently replaceable.

## Inputs and outputs

### Inputs

| Source | Input | Package |
|---|---|---|
| MCP clients | Tool invocations (`memory_write`, `memory_query`, `memory_forget`) | `protocols.mcp` |
| A2A peer agents | Task requests, capability discovery, agent card queries | `protocols.a2a` |
| Domain modules | SQL operations, embedding requests, graph queries, event emissions | `infra` |
| Autonomy subsystem | Notification payloads (approval requests, insight cards, alerts) | `notifications` |
| Configuration | Environment variables, startup settings | All packages |

### Outputs

| Destination | Output | Package |
|---|---|---|
| MCP clients | Tool results, error responses, streaming updates | `protocols.mcp` |
| A2A peer agents | Task results, agent card JSON, status updates | `protocols.a2a` |
| Domain modules | Query results, embedding vectors, graph traversal results | `infra` |
| Human operator | CLI messages, webhook payloads | `notifications` |
| Outbox table | Durable event records (transactional outbox pattern) | `infra.events` |

### Side effects

- Database connection pool lifecycle (creation, health checks, teardown)
- Embedding model loading into memory (CPU/RAM allocation)
- Knowledge graph rebuild (periodic memory allocation for NetworkX)
- Outbox worker background task (reads outbox, dispatches to
  subscribers)

## Public interfaces

### Protocol interfaces (Python Protocols)

**EmbeddingAdapter** (ADR-007) -- defined in `engram.infra.embeddings`:

```text
EmbeddingAdapter:
    embed_one(text: str) -> list[float]
    embed_batch(texts: list[str]) -> list[list[float]]
    dimension: int                    # e.g., 384
    model_name: str                   # e.g., "BAAI/bge-small-en-v1.5"
```

Phase 1 implementation: `FastembedAdapter`. Configuration selects the
active adapter via `ENGRAM_EMBEDDING_ADAPTER` (default: `fastembed`).

**GraphAdapter** (ADR-009) -- defined in `engram.infra.graph`:

```text
GraphAdapter:
    load() -> None                    # rebuild graph from memory_edges
    query_neighbors(node_id: UUID, depth: int) -> list[Edge]
    pagerank(query_node: UUID, alpha: float) -> dict[UUID, float]
    shortest_path(source: UUID, target: UUID) -> list[UUID]
```

Phase 1: stub implementation (no-op). Phase 2: `NetworkXAdapter` backed
by in-memory NetworkX graph.

**AgentRole** (ADR-008) -- defined in `engram.agents.base`:

```text
AgentRole:
    name: str
    on_start() -> None
    on_stop() -> None
    on_health_check() -> HealthStatus
    on_schedule(trigger: ScheduleTrigger) -> None
```

`BaseAgent` abstract class provides default lifecycle implementations
(structured logging, health check scaffolding). Concrete roles extend
`BaseAgent`.

**EventBus** -- defined in `engram.infra.events`:

```text
EventBus:
    publish(event: DomainEvent) -> None   # writes to outbox table
    subscribe(event_type: str, handler: Callable[[DomainEvent], Awaitable[None]]) -> None
    start_worker() -> None                # background outbox reader
    stop_worker() -> None
```

### MCP endpoints (ADR-002)

Mounted at `/mcp/` via FastMCP streamable-http transport.

| Tool | Operation | Phase |
|---|---|---|
| `memory_write` | Create or update a memory record through the Librarian Gate | 1 |
| `memory_query` | Retrieve memories via the retrieval pipeline | 1 |
| `memory_forget` | Mark a record for archival or deletion | 1 |

MCP tools are thin wrappers that validate input, delegate to domain
modules, and format responses. They do not contain business logic.

### A2A endpoints (ADR-002)

Mounted at `/` via `A2AFastAPIApplication.add_routes_to_app()`.

| Endpoint | Purpose | Phase |
|---|---|---|
| `/.well-known/agent-card.json` | Agent capability advertisement | 1 |
| A2A task endpoints | Task delegation, status queries, result retrieval | 4 |

The agent card is generated at startup from an `AgentCard` dataclass
reflecting current kernel capabilities. A2A task handling is Phase 4
scope; Phase 1 exposes the agent card only.

### Shared authentication middleware

Both protocol endpoints share authentication middleware that validates
API key tokens from the `Authorization` header. The middleware:

- Resolves the agent identity from the token
- Attaches the agent's trust level to the request context
- Rejects unauthenticated requests before they reach protocol handlers
- Applies rate limiting based on agent trust tier

## Dependencies

### Upstream dependencies (this module depends on)

| Dependency | Package | Rationale |
|---|---|---|
| `engram.memory` | `protocols`, `agents` | Protocol adapters and agent roles invoke memory operations |
| `engram.retrieval` | `protocols`, `agents` | Query operations delegate to retrieval pipeline |
| `engram.config` | All packages | Centralized settings (Pydantic BaseSettings) |
| FastAPI | `protocols` | ASGI framework for HTTP transport |
| FastMCP SDK | `protocols.mcp` | MCP protocol implementation |
| A2A Python SDK | `protocols.a2a` | A2A protocol implementation |
| asyncpg | `infra.db` | PostgreSQL async driver |
| fastembed | `infra.embeddings` | Phase 1 embedding model |
| NetworkX | `infra.graph` | Phase 2 in-memory graph operations |
| structlog | All packages | Structured logging |
| aiobreaker | `protocols`, `infra` | Circuit breakers at module boundaries |
| tenacity | `infra` | Retry logic for infrastructure adapters |

### Downstream dependents (depend on this module)

| Dependent | Interface consumed |
|---|---|
| `engram.memory` | `EmbeddingAdapter`, `EventBus`, database operations via `infra.db` |
| `engram.retrieval` | `EmbeddingAdapter`, `GraphAdapter`, database operations via `infra.db` |
| `engram.autonomy` | `EventBus`, notification dispatch |

### Import boundary rules (ADR-001)

Enforced by `import-linter`:

- `protocols` depends on `agents` and domain modules; never on `infra`
- `agents` depends on `memory` and `retrieval`; never on `infra`
- `infra` has no upstream dependencies on domain modules
- Domain modules depend on `infra` Protocols, not concrete
  implementations

These rules ensure that protocol and agent code is decoupled from
storage and compute details. Dependency injection at startup wires
concrete adapters to Protocol consumers.

## Internal responsibilities

### `engram.protocols` -- Protocol adapters

**`protocols/mcp/server.py`** -- FastMCP server configuration. Mounts
the MCP streamable-http transport at `/mcp/` on the FastAPI application.
Configures SSE support for streaming responses. Registers all MCP tools
from `tools.py`.

**`protocols/mcp/tools.py`** -- MCP tool definitions. Each tool is a
thin adapter: validate input shape, delegate to the appropriate domain
module, format the response. Error handling translates domain exceptions
into MCP error codes. Tools do not contain business logic.

**`protocols/a2a/handler.py`** -- A2A message handling. Routes incoming
A2A messages to the appropriate domain operation. Phase 1 scope is
limited to agent card serving; full task handling is Phase 4.

**`protocols/a2a/card.py`** -- Agent card generation. Builds the
`/.well-known/agent-card.json` response from an `AgentCard` dataclass at
startup. The card advertises kernel capabilities, supported memory
types, and protocol version.

**Protocol-specific error handling**: Each protocol prefix (`/mcp/`,
`/`) has dedicated error handling middleware. MCP errors follow the MCP
error code specification. A2A errors follow the A2A error model. Domain
exceptions are translated at this layer -- they never leak to callers.

### `engram.agents` -- Agent role implementations

**`agents/base.py`** -- Defines the `AgentRole` Protocol with lifecycle
hooks (`on_start`, `on_stop`, `on_health_check`, `on_schedule`).
Provides `BaseAgent` abstract class with default implementations:
structured logging on lifecycle events, health check scaffolding that
reports component status, and schedule dispatch routing.

**`agents/researcher.py`** -- Researcher role. Orchestrates retrieval
operations: accepts a query, delegates to the retrieval pipeline, and
assembles results with provenance metadata. The Researcher does not
access storage directly -- it calls retrieval interfaces.

**`agents/librarian.py`** -- Librarian role. Orchestrates write gate
operations: receives a write request, evaluates it through the Gate
pipeline (declarative rules in Phase 1, RL advisor in Phase 3), and
returns an approval or rejection with audit trail. The Librarian calls
the memory subsystem's Gate interface.

**Lifecycle management**: All agent components register with the
FastAPI application lifespan. `on_start` runs during application
startup (model loading, connection verification). `on_stop` runs during
shutdown (buffer flushing, resource release). `on_health_check`
contributes to the `/health` endpoint aggregate.

### `engram.infra` -- Infrastructure adapters

**`infra/db.py`** -- PostgreSQL + pgvector connection management.
Creates and manages the asyncpg connection pool. Provides query
execution helpers that handle connection acquisition, release, and error
translation. Pool size is configured via `DB_POOL_SIZE` (default: 10).
Query timeouts prevent runaway operations. Connection health checks run
on a configurable interval.

**`infra/embeddings.py`** -- Embedding adapter implementations. Defines
the `EmbeddingAdapter` Protocol. Phase 1 provides `FastembedAdapter`
wrapping BAAI/bge-small-en-v1.5 (384 dimensions). Embedding calls are
offloaded to `ProcessPoolExecutor` to prevent CPU-bound work from
blocking the async event loop (ADR-001). The `model_version` column
tracks which adapter produced each embedding.

**`infra/graph.py`** -- Knowledge graph adapter. Defines the
`GraphAdapter` Protocol. Phase 1 provides a stub implementation
(methods return empty results). Phase 2 provides `NetworkXAdapter` that
loads the `memory_edges` table into an in-memory NetworkX directed
graph. The graph is rebuilt on a configurable interval
(`ENGRAM_GRAPH_REFRESH_INTERVAL`, default: 300 seconds). Rebuilds use
an atomic swap pattern: a new graph is built in a background task and
swapped into the active reference under a read-write lock, ensuring
concurrent reads see a consistent snapshot. Personalized PageRank
parameters are tunable via configuration.

**`infra/events.py`** -- Internal event bus with transactional outbox
pattern. Events are written to an `outbox` table in the same database
transaction as the domain operation that produced them. A background
worker reads the outbox and dispatches events to registered subscribers.
This prevents event loss if the process crashes between a domain write
and event dispatch. The worker runs as an asyncio task within the
monolith.

### `engram.notifications` -- Communication layer

**`notifications/dispatcher.py`** -- Notification routing. Accepts
notification payloads from the autonomy subsystem, classifies them by
urgency (immediate, batch, digest), and routes them to the appropriate
delivery channel. Batching logic groups low-urgency items into periodic
digest deliveries (target: fewer than 3 push notifications per week).

**`notifications/channels/cli.py`** -- CLI output channel. Formats
notifications for terminal display. Used during development and for
manual operator interaction.

**`notifications/channels/webhook.py`** -- Webhook delivery channel.
Sends notification payloads to a configured webhook URL. Includes retry
logic with exponential backoff for transient failures. Phase 2 scope.

## Error and failure modes

### Protocol layer errors

| Error | Cause | Handling |
|---|---|---|
| Authentication failure | Invalid or expired API key | Reject with 401; log agent identity attempt |
| Rate limit exceeded | Agent exceeds trust-tier rate limit | Reject with 429; include retry-after header |
| Invalid tool input | Malformed MCP tool arguments | Reject with protocol-specific error code; log input shape |
| A2A protocol mismatch | Incompatible A2A version | Reject with version error; log peer agent identity |

### Infrastructure adapter errors

| Error | Cause | Handling |
|---|---|---|
| DB connection failure | PostgreSQL unreachable or pool exhausted | Circuit breaker trips after threshold; retry with exponential backoff; degrade to error response |
| Query timeout | Slow query exceeds configured limit | Cancel query; return timeout error; log query plan |
| Embedding generation failure | Model load failure or OOM | Circuit breaker trips; retry with backoff; log resource state |
| Graph rebuild failure | NetworkX OOM or corrupted edge data | Log error; continue serving stale graph; alert operator |
| Outbox worker failure | Background task crash | Auto-restart via asyncio task supervision (health check detects stopped worker and relaunches); events remain in outbox table until processed; no data loss |

### Resilience patterns

All infrastructure adapters use **aiobreaker** circuit breakers with
configurable thresholds (fail count, recovery timeout). When a circuit
opens, the adapter returns a degraded response rather than cascading the
failure to callers.

**tenacity** retry policies apply to transient infrastructure failures
(connection drops, temporary timeouts). Retries use exponential backoff
with jitter. Maximum retry count and backoff ceiling are configurable
per adapter.

The `/health` endpoint aggregates component-level health checks. If any
infrastructure adapter reports unhealthy, the aggregate health status
reflects the degradation.

## Non-functional considerations

### Performance

- MCP/A2A endpoint response latency target: < 500ms p95 (ADR-002)
- Database query timeout: configurable, default 30 seconds
- Embedding generation: < 500ms per record on CPU (system design target)
- Connection pool: `DB_POOL_SIZE` default 10, tunable per deployment
- Embedding compute offloaded to `ProcessPoolExecutor` (ADR-001) with
  worker count via `EMBEDDING_WORKERS` (default: 2)

### Scalability

- Phase 1 targets < 100K records; pgvector handles this without
  dedicated vector store (ADR-003)
- NetworkX graph holds up to ~1M edges in memory; Neo4j migration path
  via `GraphAdapter` Protocol if exceeded (ADR-009)
- Connection pool and worker pool sizes scale with deployment resources

### Availability

- Development environment; no formal SLA
- Circuit breakers prevent cascading failures across adapter boundaries
- Outbox pattern ensures event durability across process restarts
- Graceful degradation: if embedding adapter fails, writes succeed
  without embeddings (degraded retrieval quality noted in health)

## Observability and signals

| Signal | Type | Name | Owner | Phase |
|---|---|---|---|---|
| MCP request latency | Histogram | `engram_mcp_request_duration_seconds` | `protocols.mcp` | 1 |
| A2A request latency | Histogram | `engram_a2a_request_duration_seconds` | `protocols.a2a` | 1 |
| Auth failure count | Counter | `engram_auth_failures_total` | `protocols` | 1 |
| Rate limit rejections | Counter | `engram_rate_limit_rejections_total` | `protocols` | 1 |
| DB pool utilization | Gauge | `engram_db_pool_active_connections` | `infra.db` | 1 |
| DB query latency | Histogram | `engram_db_query_duration_seconds` | `infra.db` | 1 |
| DB query timeout count | Counter | `engram_db_query_timeouts_total` | `infra.db` | 1 |
| Embedding latency | Histogram | `engram_embedding_duration_seconds` | `infra.embeddings` | 1 |
| Embedding batch size | Histogram | `engram_embedding_batch_size` | `infra.embeddings` | 1 |
| Circuit breaker state | Gauge | `engram_circuit_breaker_state` | `infra` | 1 |
| Graph rebuild duration | Histogram | `engram_graph_rebuild_duration_seconds` | `infra.graph` | 2 |
| Graph edge count | Gauge | `engram_graph_edge_count` | `infra.graph` | 2 |
| Outbox queue depth | Gauge | `engram_outbox_queue_depth` | `infra.events` | 1 |
| Outbox dispatch latency | Histogram | `engram_outbox_dispatch_duration_seconds` | `infra.events` | 1 |
| Notification dispatch count | Counter | `engram_notification_dispatch_total` | `notifications` | 2 |
| Agent health check status | Gauge | `engram_agent_health_status` | `agents` | 1 |

All metrics are emitted via Prometheus client library. Structured logs
use `structlog` with JSON output. Each log entry includes `module`,
`operation`, `duration_ms`, and `agent_id` fields.

## Constraints and assumptions

### Constraints

| ID | Constraint | Source |
|---|---|---|
| C1 | Python 3.12 runtime | Charter |
| C2 | Single FastAPI process; no separate services | ADR-001 |
| C3 | MCP mounted at `/mcp/`; A2A mounted at `/` | ADR-002 |
| C4 | asyncpg for PostgreSQL; pgvector for vectors | ADR-003 |
| C5 | fastembed as Phase 1 embedding default | ADR-007 |
| C6 | NetworkX for Phase 2 graph; Neo4j migration path only | ADR-009 |
| C7 | Import boundaries enforced by `import-linter` | ADR-001 |
| C8 | No external API calls for embeddings (local-first) | System design axiom |

### Assumptions

| ID | Assumption | Validation |
|---|---|---|
| A1 | A2A Python SDK remains compatible with FastAPI mount pattern | Pin SDK version; test on upgrade |
| A2 | FastMCP streamable-http transport supports SSE natively | Validated in SDK documentation |
| A3 | asyncpg connection pool handles Phase 1 concurrency (< 50 concurrent agents) | Load test at Phase 1 completion |
| A4 | ProcessPoolExecutor isolates CPU-bound embedding from async event loop | Benchmark under concurrent load |
| A5 | Outbox worker processes events within acceptable latency (< 5s) | Monitor `engram_outbox_dispatch_duration_seconds` |
| A6 | NetworkX graph fits in memory at Phase 2 scale (< 500K edges, < 500MB) | Monitor `engram_graph_edge_count` and RSS |

## Explicit non-responsibilities

This module does **not**:

- Contain business logic for memory operations, retrieval ranking,
  consolidation, or conflict resolution -- those belong to domain
  modules (`memory`, `retrieval`, `autonomy`)
- Manage database schema migrations -- Alembic migrations are a
  separate operational concern
- Train or evaluate RL models -- the RL Gate Advisor (Phase 3) is an
  agent component but its training pipeline is out of scope for this
  module design
- Implement delivery channel client applications (mobile, desktop) --
  `notifications` dispatches to channels; client apps are separate
  projects
- Handle multi-tenant isolation -- single-user until Phase 5

## Security and threat analysis

Per STD-007, this section documents the threat model specific to the
infrastructure module's assets and trust boundaries.

### Assets

1. **Agent tokens** -- persistent identity credentials stored in the
   `agent_registry` table
2. **Database connection pool** -- shared resource for all kernel
   operations
3. **Memory records** -- all persistent data accessed through `infra.db`
4. **Event bus messages** -- domain events containing operation metadata
5. **Embedding model** -- loaded into process memory

### Trust boundary crossings

The infrastructure module spans the two innermost trust boundaries in
the system design:

- **Protocol layer boundary**: External callers (MCP clients, A2A peers)
  cross into the protocol layer. Authentication and rate limiting are
  enforced here.
- **Infrastructure layer boundary**: Domain modules cross into the
  infrastructure layer via Protocol interfaces. No authentication at
  this boundary -- access is controlled by import boundaries and
  dependency injection.

### Threat vectors and mitigations

### T1: Token theft and replay

An attacker obtains a valid agent token and uses it to impersonate a
trusted agent. Impact: unauthorized writes, data exfiltration.

Mitigations:

- Token rotation: agents must periodically refresh tokens; stale tokens
  are rejected
- Revocation via CLI: operator can immediately revoke any agent token
  via `engram agent revoke <agent-id>`
- Connection auditing: all authentication events (success and failure)
  are logged with source IP and timestamp
- Short-lived session tokens: the persistent identity token is exchanged
  for a short-lived session token on each connection; the session token
  expires after a configurable TTL (default: 1 hour)
- Trust tier ceiling: even with a valid token, the agent's trust tier
  limits accessible operations

### T2: A2A data exfiltration

A malicious agent connects via A2A and queries sensitive records.
Impact: unauthorized access to user-only or sensitive data.

Mitigations:

- Access control levels: every memory record has an `access_level`
  (public, agent-scoped, user-only, system, sensitive); queries filter
  results by the requesting agent's trust tier
- Agent trust tiers: new agents default to Restricted (most limited
  access); elevation requires explicit user approval
- Rate limiting: per-agent rate limits prevent bulk data extraction;
  limits scale with trust tier (Restricted agents have the lowest
  ceiling)
- Query auditing: all retrieval operations are logged with agent
  identity, query content, result count, and access levels of returned
  records
- A2A task scope: Phase 4 A2A task handling will enforce task-scoped
  access -- agents can only access data relevant to the delegated task

### T3: Database connection exhaustion

Slow queries, connection leaks, or a burst of concurrent requests
exhaust the asyncpg connection pool. Impact: kernel-wide unavailability.

Mitigations:

- Connection pool limits: `DB_POOL_SIZE` caps the maximum number of
  connections (default: 10); excess requests queue rather than creating
  unbounded connections
- Query timeouts: all database operations have a configurable timeout
  (default: 30 seconds); timed-out queries are cancelled at the database
  level
- Circuit breakers: `aiobreaker` monitors database call failure rate;
  when the failure threshold is exceeded, the circuit opens and
  subsequent calls fail fast without consuming pool connections
- Connection health checks: periodic keep-alive queries detect and
  replace dead connections before they block callers
- Pool utilization monitoring: `engram_db_pool_active_connections` gauge
  alerts when utilization approaches the limit

### T4: Event bus message loss

Events emitted between a domain write and the event bus dispatch are
lost if the process crashes. Impact: downstream subscribers (e.g.,
embedding generation, consolidation triggers) miss events, causing
data inconsistency.

Mitigation:

- Transactional outbox pattern: events are written to the `outbox` table
  in the same database transaction as the domain operation. The event is
  durable in PostgreSQL before the transaction commits.
- Background outbox worker: reads committed events from the outbox and
  dispatches to subscribers. The worker marks events as processed after
  successful dispatch.
- At-least-once delivery: if the worker crashes after reading but before
  marking processed, the event is re-dispatched on restart. Subscribers
  must be idempotent.
- Outbox queue depth monitoring: `engram_outbox_queue_depth` gauge
  alerts if events accumulate faster than the worker processes them.

### Residual risks

- PII may exist in event bus payloads if the domain write contains PII.
  The outbox table inherits the same database-level access controls as
  memory records, but outbox events are not independently classified.
  Acceptable for Phase 1 (single-user); reassess for multi-user.
- The embedding model runs in-process. A malicious model file could
  execute arbitrary code at load time. Mitigated by using only
  well-known models from Hugging Face Hub with checksum verification.

## Definition of done

- Aligned to approved system design
  (`docs/design/system-design.md`).
- Applicable sections of Design Review Checklist (STD-024) completed.
- All Protocol interfaces (`EmbeddingAdapter`, `GraphAdapter`,
  `AgentRole`, `EventBus`) defined with type signatures.
- MCP tool definitions documented with input/output contracts.
- Import boundary rules specified for `import-linter` configuration.
- Observability signals identified with names, types, and owners.
- Security threat analysis complete with mitigations for all
  identified vectors.
- Error and failure modes enumerated with handling strategy.
- Links to related ADRs and specs captured.

## Links

- System design: `docs/design/system-design.md`
- Related ADRs:
  - ADR-001: Monolith-first architecture
  - ADR-002: Dual protocol (MCP + A2A)
  - ADR-003: Postgres + pgvector
  - ADR-007: Swappable embedding adapter
  - ADR-008: Expanded agent architecture
  - ADR-009: Knowledge graph Phase 2
- ADR directory: `docs/architecture/adr/`
- Schema definitions: `docs/design/schemas/` (separate artifact per
  STD-055, authored during specification phase)
- Technical specification: `docs/specs/technical-specification.md`
  (authored during specification phase per STD-023)

# Implementation Notes

- This is a composite module design covering four packages. Each package
  maps to a directory under `src/engram/` as defined in the system
  design project structure.
- Concrete adapter wiring happens at application startup in
  `engram.main` via dependency injection. Domain modules receive Protocol
  instances, never concrete classes.
- The `ProcessPoolExecutor` for embedding work is created once at startup
  and shared across all embedding calls. Worker count is configured via
  `EMBEDDING_WORKERS` (default: 2).
- Circuit breaker and retry configuration is centralized in a
  `resilience.py` module per ADR-001. Each adapter boundary has its own
  breaker instance with tunable thresholds.
- The agent card at `/.well-known/agent-card.json` is generated once at
  startup and served as a static response. It reflects the kernel's
  current capabilities and supported memory types.

# Continuous Improvement and Compliance Metrics

- Track protocol adapter boundary violations via `import-linter` (target:
  0 violations per CI run)
- Track circuit breaker trip frequency per adapter (target: < 1% per
  hour)
- Track observability signal coverage (target: all signals in the table
  above are instrumented before Phase 1 completion)
- Review adapter interface stability quarterly -- frequent Protocol
  changes indicate design issues
- Monitor outbox queue depth trend -- sustained growth indicates
  worker throughput issues

# Compliance

This document complies with:

- **STD-001** (Documentation Standard): All mandatory sections present
  (Purpose, Scope, Standard, Implementation Notes, Continuous
  Improvement, Compliance, Changelog).
- **STD-022** (Module Design Standard): All required sections populated
  per template (module purpose, inputs/outputs, public interfaces,
  dependencies, internal responsibilities, error modes, non-functional
  considerations, observability, constraints, non-responsibilities,
  definition of done, links).
- **STD-007** (Security and Threat Modeling): Threat analysis embedded
  in module design per system design directive.
- **STD-020** (Design-First Development): Module design precedes
  technical specification and implementation.

Verified by: sh4i-yurei (draft -- pending review)
Date: 2026-02-13

# Changelog

## 0.1.0 -- 2026-02-13

**Added:**

- Initial module design for infrastructure layer (protocols, agents,
  infra, notifications)
- Protocol interfaces: EmbeddingAdapter, GraphAdapter, AgentRole,
  EventBus
- MCP and A2A endpoint definitions with authentication middleware
- Security threat analysis covering token theft, A2A exfiltration,
  connection exhaustion, and event bus message loss
- Observability signal table with 16 metrics across all four packages
- Error and failure mode tables for protocol and infrastructure layers
- Import boundary rules and dependency mapping
- Phase 1 scope delineation from later phases

**Status**: Draft -- pending design review
