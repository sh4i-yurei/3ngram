---
id: 3NGRAM-ADR-008
title: "ADR-008: Expanded agent architecture"
version: 0.1.0
category: architecture
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-047]
tags: [adr, architecture, agents, rl, lifecycle, 3ngram]
---

## 1. Purpose

Record the decision to expand the agent architecture from two roles (ADR-005) to a multi-phase component model with lifecycle hooks, supporting the v2 vision of autonomous memory management with RL-driven optimization.

## 2. Scope

This decision applies to the agent role layer of 3ngram. It supersedes ADR-005 by extending the AgentRole Protocol with lifecycle hooks and defining the full component roadmap across three phases. The Protocol pattern itself (no framework) remains valid.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-008 |
| Status | Accepted |
| Date | 2026-02-13 |
| Deciders | sh4i-yurei |
| Supersedes | ADR-005 |

### 3.2 Context

ADR-005 chose Python Protocol classes over agent frameworks and defined two MVP roles (Researcher, Librarian). The v2 system design introduces autonomous memory consolidation, conflict resolution, RL-trained gate advisors, and meta-optimization -- capabilities that require additional agent-like components beyond the original two roles.

The Protocol pattern from ADR-005 scales well. What needs to change is the scope of components and the Protocol surface area (lifecycle hooks for startup, shutdown, health, and periodic maintenance).

### 3.3 Decision Drivers

- **v2 vision** -- autonomous memory management requires more than two roles
- **Protocol scalability** -- the no-framework approach must prove it scales to 6+ components
- **Phased delivery** -- components must be deliverable incrementally without breaking existing roles
- **RL readiness** -- some components will have RL-trained decision logic; the Protocol must accommodate this
- **Testability** -- all components must remain independently testable

### 3.4 Options

#### Option A: Extend AgentRole Protocol with lifecycle hooks and phased component roadmap

Keep the Protocol pattern from ADR-005. Add lifecycle hooks (`on_start`, `on_stop`, `on_health_check`, `on_schedule`) to the base Protocol. Define a phased rollout of components that implement the Protocol or specialized subprotocols.

#### Option B: Adopt an agent framework now that component count is growing

Revisit the framework decision from ADR-005. Pydantic AI or a similar lightweight framework could reduce boilerplate as component count grows.

#### Option C: Separate orchestration layer with plugin architecture

Build an internal orchestration framework that manages component lifecycle, scheduling, and inter-component communication as a plugin system.

### 3.5 Decision

**Option A -- Extend AgentRole Protocol with lifecycle hooks and phased component roadmap.**

The `AgentRole` Protocol is extended with:

- `on_start()` -- initialization logic (model loading, connection setup)
- `on_stop()` -- graceful shutdown (flush buffers, release resources)
- `on_health_check() -> HealthStatus` -- component-level health reporting
- `on_schedule(trigger: ScheduleTrigger)` -- periodic maintenance tasks

Component roadmap by phase:

1. **Phase 1** -- Researcher (retrieval agent), Librarian (write gate agent)
2. **Phase 2** -- Consolidation Engine (memory compaction), Conflict Resolver (contradiction detection and resolution)
3. **Phase 3** -- RL Gate Advisor (learned storage decisions), Research Scanner (proactive memory maintenance), Meta-Optimizer (system-level tuning)

Each component implements `AgentRole` or a specialized subprotocol (e.g., `RLComponent` extends `AgentRole` with `train()` and `predict()` methods). Inter-component communication uses direct function calls within the monolith (per ADR-001).

### 3.6 Consequences

**Positive:**

- Protocol pattern validated at scale -- 7 components, no framework dependency
- Lifecycle hooks provide consistent startup, shutdown, and health semantics across all components
- Phased delivery means Phase 1 code is not affected by Phase 2+ additions
- RL components use the same Protocol pattern with a thin extension, keeping the architecture uniform
- Each component remains independently testable via Protocol mocking

**Negative:**

- More boilerplate than a framework as component count grows; mitigated by a shared `BaseAgent` class implementing common lifecycle logic
- Inter-component dependencies must be managed manually; mitigated by dependency injection at startup
- Phase 3 RL components may need training infrastructure not covered by this decision

**Follow-up actions:**

- Extend the `AgentRole` Protocol with lifecycle hooks in `src/engram/agents/protocol.py`
- Implement Researcher and Librarian roles for Phase 1
- Define the `RLComponent` subprotocol for Phase 3 components
- Document component dependency graph (which components depend on which)

### 3.7 Notes and Links

- Superseded decision: [ADR-005 Agent Roles](./ADR-005-agent-roles.md)
- Monolith-first: [ADR-001 Monolith-First](./ADR-001-monolith-first.md)
- Dual protocol: [ADR-002 Dual Protocol](./ADR-002-dual-protocol.md)
- Librarian gate: [ADR-012 Hybrid Librarian Gate](./ADR-012-hybrid-librarian-gate.md)

## 4. Implementation Notes

- The extended `AgentRole` Protocol lives in `src/engram/agents/protocol.py`
- `BaseAgent` abstract class in `src/engram/agents/base.py` provides default lifecycle implementations (logging, health check scaffolding)
- Each component lives in its own module under `src/engram/agents/` (e.g., `researcher.py`, `librarian.py`, `consolidation.py`)
- Scheduling uses `asyncio` task scheduling within the monolith; no external scheduler needed for Phase 1-2
- Circuit breaker and retry configuration remains per-component, following `resilience.py` from ADR-001

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Component unit test coverage | >= 90% | Every CI run |
| Lifecycle hook compliance | All components implement all hooks | Every CI run (Protocol check) |
| Component health check pass rate | 100% | Continuous monitoring |
| Inter-component call latency | < 10ms within monolith | Continuous monitoring |

Review this ADR when any of these signals appear:

- Component count exceeds 10 and boilerplate becomes a significant maintenance burden
- Inter-component communication patterns require async messaging (event bus)
- RL training infrastructure decisions need their own ADR
- A framework reaches maturity that would reduce boilerplate without lock-in risk

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-047 (Architecture Decision Workflow) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted expanded agent architecture with lifecycle hooks, superseding ADR-005
