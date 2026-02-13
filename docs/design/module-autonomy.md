---
id: 3NGRAM-MD-003
title: "Module Design: Autonomy Subsystem"
version: 0.1.0
category: project
status: draft
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-022]
tags: [design, module-design, autonomy, 3ngram]
---

# Module Design: Autonomy Subsystem

# Purpose

This module design defines the responsibilities, boundaries, and
interfaces of the `engram.autonomy` package -- the subsystem responsible
for continuous self-evaluation, self-healing, background task scheduling,
and research-driven self-improvement within the 3ngram kernel.

# Scope

This design covers the five files within the `engram.autonomy` package:

| File | Responsibility | Phase |
|---|---|---|
| `loop.py` | Runtime loop with 3-tier priority scheduling | 1 (stub), 2 (operational) |
| `metrics.py` | Self-evaluation metric computation | 1 (stub), 2 (basic), 3 (full) |
| `healing.py` | Autonomous corrective actions | 3 |
| `scheduler.py` | Background task scheduling | 1 (skeleton), 2 (consolidation triggers) |
| `scanner.py` | Research scanner for self-improvement | 3 |

Phase 1 delivers stubs and skeletons only -- health check integration,
basic metric collection scaffolding, and a scheduler skeleton. Full
autonomy capabilities arrive in Phases 2 and 3.

This design maps to the Autonomy Subsystem section of the approved
system design (`docs/design/system-design.md`, section "Major components
and responsibilities").

# Standard

## Module purpose and responsibility

The autonomy subsystem is the kernel's self-awareness and self-repair
layer. Its single responsibility is to **monitor kernel health, detect
degradation, and take corrective action** -- without human intervention
when safe, and with escalation when not.

Success means the kernel maintains its own performance targets (retrieval
hit rate >90%, memory pressure <80%, agent satisfaction >0.8) through
continuous observation and bounded autonomous correction, reducing
operator intervention to approval-only actions.

## Inputs and outputs

### Inputs

| Input | Source | Description |
|---|---|---|
| Retrieval metrics | `engram.retrieval` | Hit rate, precision, latency histograms |
| Memory metrics | `engram.memory` | Record counts by type, consolidation path distribution, pressure index |
| Gate metrics | `engram.memory` (Gate) | Approval/rejection rates, queue depth, decision latency |
| Agent feedback | `engram.protocols` | Useful/partial/miss signals from agent interactions |
| Health status | All subsystems | Component-level `HealthStatus` responses via `on_health_check()` |
| Configuration | `engram.config` | Metric thresholds, schedule intervals, healing policy |
| Schedule triggers | Internal clock / event bus | Timer-based and event-driven triggers |

### Outputs

| Output | Consumer | Description |
|---|---|---|
| Computed metrics | Prometheus exporter, `/health` endpoint | Gauge and counter values for all tracked metrics |
| Healing actions | `engram.memory` (Gate) | Write operations routed through the Librarian Gate |
| Health aggregation | `/health` endpoint | Aggregated component health for the kernel |
| Notifications | `engram.notifications` | Escalation alerts when auto-repair fails or is unsafe |
| Scheduling commands | `engram.memory` (Consolidation) | Consolidation trigger signals |
| Research findings | `engram.memory` (Gate) | New knowledge records from research scanning (Phase 3) |

### Side effects

- Healing actions modify stored records (re-embedding, re-indexing,
  archiving) -- always through the Librarian Gate.
- Scheduler triggers consolidation in the memory subsystem.
- Notifications are dispatched to the user when escalation is required.

## Public interfaces

The autonomy subsystem exposes its capabilities through Python Protocol
interfaces. Schema definitions for shared data shapes will be linked per
STD-055 when the schema artifact is authored.

### `AutonomyLoop` Protocol

Manages the runtime lifecycle of the autonomy subsystem.

```text
AutonomyLoop:
    start() -> None
        Start the runtime loop and all scheduled tasks.

    stop() -> None
        Gracefully shut down. Drain in-flight tasks, flush metrics.

    health() -> HealthStatus
        Return aggregated health across all autonomy components.
```

### `MetricsCollector` Protocol

Computes and exposes self-evaluation metrics.

```text
MetricsCollector:
    collect() -> MetricsSnapshot
        Compute current metric values across all three categories
        (retrieval quality, memory health, agent satisfaction).

    get_metric(name: str) -> MetricValue
        Retrieve a single named metric.

    register_source(name: str, source: MetricSource) -> None
        Register a metric data source from another subsystem.
```

### `HealingEngine` Protocol (Phase 3)

Executes autonomous corrective actions.

```text
HealingEngine:
    diagnose(snapshot: MetricsSnapshot) -> list[Diagnosis]
        Match current metrics against the critical failure scenarios table.
        Return ranked diagnoses.

    heal(diagnosis: Diagnosis) -> HealingResult
        Execute the prescribed corrective action.
        All writes route through the Librarian Gate.

    dry_run(diagnosis: Diagnosis) -> HealingPlan
        Describe what heal() would do without executing.
```

### `TaskScheduler` Protocol

Manages background task execution.

```text
TaskScheduler:
    schedule(task: ScheduledTask) -> TaskHandle
        Register a task with its trigger (cron, interval, event).

    cancel(handle: TaskHandle) -> None
        Cancel a scheduled task.

    list_active() -> list[TaskInfo]
        Return metadata for all active scheduled tasks.
```

### `ResearchScanner` Protocol (Phase 3)

Periodic search for self-improvement techniques.

```text
ResearchScanner:
    scan() -> list[ResearchFinding]
        Execute a research scan cycle. Findings are candidate
        knowledge records to be submitted through the Gate.

    configure(topics: list[str]) -> None
        Update the scanner's topic list.
```

### Error contracts

All public methods raise:

- `AutonomyError` -- base exception for autonomy subsystem failures.
- `HealingRejectedError` -- raised when the Librarian Gate rejects a
  healing action.
- `SchedulerFullError` -- raised when the scheduler has reached its
  maximum concurrent task limit.

## Dependencies

| Dependency | Type | Rationale |
|---|---|---|
| `engram.memory` | Domain (Protocol) | Metrics source for memory health; healing actions routed through Gate |
| `engram.retrieval` | Domain (Protocol) | Metrics source for retrieval quality |
| `engram.config` | Internal | Threshold values, schedule intervals, feature flags |
| `engram.notifications` | Domain (Protocol) | Escalation when auto-repair fails |
| `asyncio` | Standard library | Task scheduling, event loop |
| `aiobreaker` | Third-party | Circuit breakers at module boundaries (ADR-001) |
| `tenacity` | Third-party | Retry with backoff for healing actions |
| `structlog` | Third-party | Structured logging |
| `prometheus_client` | Third-party | Metric exposition |

### Trust boundaries

The autonomy subsystem sits within the kernel domain layer. It does
**not** cross the protocol-layer trust boundary -- it never receives
direct external input. All external data reaches autonomy indirectly
through metrics collected from other subsystems.

The autonomy subsystem never imports from `engram.infra` or
`engram.protocols` directly. All infrastructure access is mediated
through domain interfaces (ADR-001, system design import boundaries).

## Internal responsibilities

The autonomy subsystem has five internal components, each mapped to a
source file.

### Runtime loop (`loop.py`)

Orchestrates all autonomy activities across three priority tiers:

| Tier | Priority | Activities | Interval |
|---|---|---|---|
| Critical | 1 | Health checks, circuit breaker monitoring | 10 seconds |
| Normal | 2 | Metric collection, consolidation scheduling | 1 minute |
| Background | 3 | Research scanning, meta-optimization | 1 hour |

The loop runs as a long-lived asyncio task started during kernel
initialization. Each tier has independent error isolation -- a failure
in a background task does not affect critical-tier operations.

### Self-evaluation metrics (`metrics.py`)

Computes three categories of metrics from data provided by other
subsystems:

- **Retrieval quality**: hit rate, precision, latency percentiles,
  conflict rate, miss rate.
- **Memory health**: pressure index, staleness index, consolidation
  ratio, write quality, gate enforcement percentage.
- **Agent satisfaction**: feedback score, context relevance trend,
  progressive feeding time.

Metric computation is read-only. It queries other subsystems through
Protocol interfaces and never modifies state.

### Self-healing (`healing.py`)

Maps metric degradation to corrective actions using the critical failure
scenarios table defined in the system design (§ Failure Scenarios and
Mitigations). Each action is a structured
operation submitted through the Librarian Gate with
`gate_decision_type = self_healing`.

Healing actions are bounded:

- Maximum concurrent healing actions (configurable, default 3).
- Circuit breaker prevents repeated healing attempts for the same
  symptom within a cooldown window.
- Dry-run mode allows inspection before execution.

### Background scheduler (`scheduler.py`)

Manages periodic and event-driven background tasks using asyncio task
scheduling within the monolith (ADR-001). Tasks include:

- Consolidation triggers (Phase 2).
- Metric collection cycles.
- Research scan cycles (Phase 3).
- PII batch rescan (system design § PII screening model).

The scheduler enforces a maximum concurrent task limit and provides
task lifecycle management (register, cancel, list).

### Research scanner (`scanner.py`)

Periodically searches for techniques to improve kernel performance
(Phase 3). Findings are submitted as candidate knowledge records through
the Librarian Gate -- the scanner never writes directly to storage.

## Error and failure modes

| Error condition | Handling | Propagation |
|---|---|---|
| Metric source unavailable | Return last-known values with staleness flag; log warning | Health status degrades to `degraded` |
| Healing action rejected by Gate | Log rejection reason; do not retry the same action | `HealingRejectedError` surfaced to caller; notification dispatched |
| Healing action fails at infrastructure | Circuit breaker trips after threshold; tenacity retries with backoff | Escalate to user via notification after circuit breaker opens |
| Scheduler task exceeds timeout | Cancel task; log timeout event | Task reported as `failed` in scheduler status |
| Scheduler at capacity | Reject new task registration | `SchedulerFullError` raised to caller |
| Runtime loop crash | Restart loop with backoff; notify user if repeated | Health endpoint reports `unhealthy` |
| Research scanner network failure | Skip scan cycle; retry at next scheduled interval | Log warning; no escalation |

### Failure isolation

Each priority tier in the runtime loop runs in its own asyncio task
group. A crash in tier 3 (background) does not propagate to tier 1
(critical). Circuit breakers at the module boundary (ADR-001) prevent
cascading failures from reaching other subsystems.

## Non-functional considerations

### Performance

- Metric collection must complete within 500ms per cycle (Normal tier
  runs every 60 seconds).
- Healing actions are asynchronous -- they do not block the runtime
  loop.
- Scheduler overhead must be negligible relative to the tasks it
  manages.

### Scalability

- Phase 1-3: Single-node, in-process scheduling. No external scheduler
  required.
- If task volume exceeds asyncio capacity, the scheduler enforces its
  maximum concurrent limit and drops lower-priority tasks.

### Availability

- The autonomy subsystem is non-critical for kernel operation. If it
  fails entirely, the kernel continues to serve reads and writes -- it
  simply loses self-monitoring and self-repair capabilities.
- Graceful degradation: if metric sources are unavailable, the system
  operates on last-known values rather than failing.

### Resource constraints

- Research scanner (Phase 3) performs network I/O; must be rate-limited
  to avoid bandwidth consumption.
- Healing actions that involve re-embedding consume CPU; they must be
  submitted to the `ProcessPoolExecutor` bulkhead (ADR-001), not run
  on the main event loop.

## Observability and signals

| Signal | Type | Name | Owner | Description |
|---|---|---|---|---|
| Metric | Gauge | `engram_retrieval_hit_rate` | metrics.py | Current retrieval hit rate |
| Metric | Gauge | `engram_retrieval_precision` | metrics.py | Current retrieval precision |
| Metric | Histogram | `engram_retrieval_latency_seconds` | metrics.py | Retrieval latency distribution |
| Metric | Gauge | `engram_memory_pressure` | metrics.py | Memory pressure index (0.0-1.0) |
| Metric | Gauge | `engram_memory_staleness` | metrics.py | Staleness index (0.0-1.0) |
| Metric | Gauge | `engram_consolidation_ratio` | metrics.py | Consolidation compression ratio |
| Metric | Gauge | `engram_agent_feedback_score` | metrics.py | Aggregated agent feedback (0.0-1.0) |
| Metric | Counter | `engram_healing_actions_total` | healing.py | Total healing actions attempted (label: status) |
| Metric | Counter | `engram_healing_rejections_total` | healing.py | Healing actions rejected by Gate |
| Metric | Gauge | `engram_scheduler_active_tasks` | scheduler.py | Currently active scheduled tasks |
| Metric | Counter | `engram_scheduler_tasks_total` | scheduler.py | Total tasks executed (label: status) |
| Metric | Counter | `engram_scanner_findings_total` | scanner.py | Research findings submitted |
| Log | Event | `autonomy.loop.started` | loop.py | Runtime loop started |
| Log | Event | `autonomy.loop.tier_error` | loop.py | Error in a priority tier (includes tier, error) |
| Log | Event | `autonomy.healing.action` | healing.py | Healing action attempted (includes diagnosis, action) |
| Log | Event | `autonomy.healing.rejected` | healing.py | Gate rejected healing action (includes reason) |
| Log | Event | `autonomy.healing.escalated` | healing.py | Auto-repair failed, escalating to user |
| Log | Event | `autonomy.scheduler.capacity` | scheduler.py | Scheduler at maximum concurrent tasks |
| Log | Event | `autonomy.metrics.stale` | metrics.py | Metric source unavailable, using last-known value |

All logs are emitted via `structlog` in JSON format. All metrics are
exposed via `prometheus_client`.

## Constraints and assumptions

### Constraints

| ID | Constraint | Source |
|---|---|---|
| C1 | Healing actions must route through the Librarian Gate | System design (write path) |
| C2 | No direct imports from `engram.infra` or `engram.protocols` | System design (import boundaries) |
| C3 | Scheduling uses asyncio within the monolith -- no external scheduler | ADR-001 |
| C4 | Phase 1 delivers stubs only -- no operational autonomy | System design (phase scoping) |
| C5 | Circuit breakers (aiobreaker) at all module boundary calls | ADR-001 |
| C6 | CPU-bound healing work (re-embedding) must use ProcessPoolExecutor | ADR-001 |

### Assumptions

| ID | Assumption | Validation |
|---|---|---|
| A1 | Other subsystems expose metrics through stable Protocol interfaces | Validated at module integration |
| A2 | asyncio task scheduling is sufficient for Phase 1-3 task volumes | Monitor scheduler capacity metrics |
| A3 | Metric collection latency stays within 500ms budget | Benchmark at Phase 2 delivery |
| A4 | Healing actions through the Gate complete within reasonable time | Monitor healing action latency |
| A5 | Research scanner network access is available (Phase 3) | Feature flag disables scanner if unavailable |

## Explicit non-responsibilities

- **Storage operations**: The autonomy subsystem never writes directly
  to PostgreSQL, pgvector, or the knowledge graph. All mutations go
  through the Librarian Gate.
- **Retrieval execution**: Query processing belongs to `engram.retrieval`.
  Autonomy only reads retrieval metrics.
- **Gate policy decisions**: Write authorization logic belongs to
  `engram.memory` (Gate). Autonomy submits healing writes as a regular
  client of the Gate.
- **Consolidation execution**: The consolidation engine lives in
  `engram.memory`. Autonomy only triggers consolidation via scheduling
  signals.
- **Notification routing**: Delivery channel selection and message
  formatting belong to `engram.notifications`. Autonomy dispatches
  escalation requests with structured payloads.
- **Agent lifecycle management**: Agent registration, authentication,
  and trust assignment belong to `engram.protocols` and `engram.agents`.
- **Infrastructure management**: Database connections, embedding model
  loading, and graph database operations belong to `engram.infra`.

## Security and threat analysis

Per STD-007, this section documents the threat model specific to the
autonomy subsystem.

### Assets owned or managed

| Asset | Classification | Description |
|---|---|---|
| Computed metrics | System | Derived health indicators -- no raw user data |
| Healing action log | System | Audit trail of autonomous corrective actions |
| Scheduler task registry | System | Active task metadata |
| Research findings | System | Candidate knowledge records (pre-Gate) |

### Trust boundaries crossed

The autonomy subsystem operates entirely within the kernel domain
layer. It does not cross the external protocol boundary. However, it
crosses internal trust boundaries when:

- Reading metrics from other subsystems (input trust boundary).
- Submitting healing writes to the Librarian Gate (write trust
  boundary).
- Dispatching notifications to the notification subsystem (output trust
  boundary).

### Threat vectors and mitigations

### T1: Self-healing actions that bypass normal write paths

- **Threat**: A bug or misconfiguration in the healing engine could
  write directly to storage, bypassing the Librarian Gate and its audit
  trail. This would violate the system's 100% gate enforcement
  invariant.
- **Impact**: Data corruption, loss of audit trail, potential
  inconsistency.
- **Mitigations**:
  - Healing actions use the same Gate Protocol interface as external
    agents, with `gate_decision_type = self_healing`.
  - The `healing.py` module has no direct dependency on `engram.infra`.
    Import-linter rules enforce this boundary statically.
  - Integration tests verify that all healing actions produce
    corresponding `librarian_audit` records.
  - Circuit breaker wraps all Gate submissions from the healing engine.

### T2: Runaway scheduling causing resource exhaustion

- **Threat**: A misconfigured schedule or bug in the scheduler could
  spawn unbounded concurrent tasks, exhausting CPU, memory, or database
  connections.
- **Impact**: Kernel-wide resource exhaustion, cascading failures across
  all subsystems.
- **Mitigations**:
  - Maximum concurrent task limit enforced by the scheduler (default
    configurable, hard ceiling at startup).
  - `SchedulerFullError` raised when the limit is reached -- no silent
    overflow.
  - Circuit breaker on the scheduler itself -- if tasks are failing at
    a high rate, the scheduler pauses new task creation.
  - Each task has a mandatory timeout. Tasks exceeding the timeout are
    cancelled.
  - Scheduler active task count is a Prometheus gauge with alerting
    threshold.

### T3: Metric manipulation triggering malicious self-healing

- **Threat**: If an adversarial or compromised agent can influence the
  metrics that the autonomy subsystem reads (e.g., by flooding bad
  feedback signals), it could trigger unnecessary or harmful healing
  actions.
- **Impact**: Unwarranted re-indexing, weight resets, or archive
  operations degrading kernel performance.
- **Mitigations**:
  - Metrics are computed from aggregated system state, not from
    individual agent submissions. A single agent's feedback is weighted
    by its trust level (system design, agent trust tiers).
  - Healing actions require metric degradation to persist across
    multiple collection cycles before triggering (debounce window).
  - Dry-run mode allows operator review before healing execution.
  - Healing cooldown prevents repeated actions for the same symptom
    within a configurable window.
  - All healing actions are logged with full diagnosis context for
    post-hoc audit.

### T4: Research scanner ingesting adversarial content

- **Threat**: The research scanner (Phase 3) performs network I/O to
  search for improvement techniques. Adversarial content could be
  retrieved and, if stored, could influence kernel behavior.
- **Impact**: Poisoned knowledge records affecting future decisions.
- **Mitigations**:
  - Scanner findings are submitted through the Librarian Gate as
    regular write operations. Gate Layer 1 (schema validation, PII
    screen) and Layer 2 (confidence scoring) apply.
  - Scanner-originated records receive a lower source confidence
    (inferred: 0.6) and are tagged with provenance indicating external
    research origin.
  - Scanner topics and source domains are configurable and restricted
    by default.

## Definition of done

- Aligned to the approved system design
  (`docs/design/system-design.md`).
- All 10 STD-022 required sections populated.
- Security and threat analysis covers T1-T4 with mitigations.
- Observability signals table includes all metrics and log events with
  owners.
- Phase boundaries (1, 2, 3) are explicit for every component.
- Applicable sections of the design review checklist (STD-024)
  completed.
- Links to related issues and specs captured.

## Links

- System design: `docs/design/system-design.md`
- Related ADRs:
  - ADR-001 (Monolith-first): `docs/architecture/adr/ADR-001-monolith-first.md`
  - ADR-008 (Expanded agent architecture): `docs/architecture/adr/ADR-008-expanded-agent-architecture.md`
  - ADR-010 (CLS consolidation): `docs/architecture/adr/ADR-010-cls-consolidation.md`
  - ADR-012 (Hybrid Librarian Gate): `docs/architecture/adr/ADR-012-hybrid-librarian-gate.md`
- Related specs: Technical specification (pending)
- Schema definitions: `docs/design/schemas/` (pending)

# Implementation Notes

- Phase 1 delivers stubs: `loop.py` starts and stops, `metrics.py`
  collects basic counters, `scheduler.py` accepts task registrations
  but runs only health check tasks, `healing.py` and `scanner.py` are
  no-ops.
- Phase 2 activates the scheduler for consolidation triggers and
  extends metric collection to all three categories.
- Phase 3 activates the full healing engine and research scanner.
- Feature flags gate Phase 2 and Phase 3 components. Disabling a flag
  reverts the subsystem to its previous phase behavior.
- Avoid implementation detail in Protocol definitions -- keep contracts
  focused on shape and semantics.

# Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
|---|---|---|
| Module boundary violations (import-linter) | 0 | Every CI run |
| Healing actions through Gate (percentage) | 100% | Continuous |
| Metric collection cycle latency | < 500ms | Continuous |
| Scheduler task timeout rate | < 5% | Weekly review |
| Healing escalation rate | Trending down | Monthly review |

Findings from these metrics inform updates to healing policies,
scheduler limits, and metric thresholds.

# Compliance

This document complies with:

- **STD-001** (Documentation Standard): All mandatory sections present
  (Purpose, Scope, Standard, Implementation Notes, Continuous
  Improvement, Compliance, Changelog).
- **STD-022** (Module Design Standard): All 10 required sections
  populated per clause 2.2-2.11 plus security and threat analysis.
- **STD-007** (Security and Threat Modeling Standard): Threat analysis
  embedded in module design with assets, trust boundaries, threat
  vectors, and mitigations.
- **STD-020** (Design-First Development): Module design precedes
  technical specification and implementation.

Verified by: sh4i-yurei (draft -- pending review)
Date: 2026-02-13

# Changelog

## 0.1.0 -- 2026-02-13

**Added:**

- Initial module design for the autonomy subsystem.
- Five-component internal structure: runtime loop, metrics, healing,
  scheduler, research scanner.
- Public interface Protocols: AutonomyLoop, MetricsCollector,
  HealingEngine, TaskScheduler, ResearchScanner.
- Observability signals table with 12 metrics and 7 log events.
- Security and threat analysis covering 4 threat vectors (T1-T4).
- Phase scoping: Phase 1 (stub), Phase 2 (scheduler + basic metrics),
  Phase 3 (full healing + scanner).

**Status**: Draft -- pending review
