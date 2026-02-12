---
id: 3NGRAM-ADR-005
title: "ADR-005: Agent role architecture"
version: 0.1.0
category: project
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-021]
tags: [adr, architecture, agents, roles, 3ngram]
---

## 1. Purpose

Record the decision on how 3ngram defines and orchestrates agent roles (Researcher for MVP, plus future Planner, Memorizer, Evaluator/Sentinel) -- whether to adopt an agent framework or build lightweight role definitions internally -- and capture the reasoning, alternatives considered, and consequences.

## 2. Scope

This decision applies to the agent role layer of 3ngram. It governs how agent roles are defined, registered, tested, and integrated with the A2A (AgentExecutor) and MCP (tool registration) protocol surfaces within the monolith.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-005 |
| Status | Accepted |
| Date | 2026-02-12 |
| Deciders | sh4i-yurei |

### 3.2 Context

3ngram has agent roles -- Researcher for MVP, with Planner, Memorizer, and Evaluator/Sentinel planned for future iterations. These roles need an internal architecture that defines how they receive tasks, execute domain logic, handle errors, and report results.

The question is whether to adopt an agent framework (LangGraph, CrewAI, Pydantic AI, etc.) or build lightweight role definitions internally using Python Protocol classes.

### 3.3 Decision Drivers

- **Complexity budget** -- solo developer; framework overhead must be justified by proportional value
- **Framework lock-in risk** -- agent frameworks are evolving rapidly; coupling to one constrains future choices
- **MVP scope** -- only 1-2 agents needed for MVP (Researcher, possibly Librarian)
- **Self-healing and agent learning readiness** -- roles must support circuit breakers, bounded retries, and data collection for future learning
- **Testability** -- agent roles must be easy to test in isolation with mock dependencies

### 3.4 Options

#### Option A: No framework -- Python Protocol classes

Define an `AgentRole` Protocol with `execute()`, `cancel()`, and `health_check()` methods. Each role (Researcher, future Planner, etc.) is a Python class implementing the Protocol. Follow patterns from Pydantic AI (structured inputs/outputs, tool registration) without the dependency. Roles are registered with the A2A AgentExecutor as skills. Direct control over error handling, retries, and observability. Easy to test -- just Python classes with known interfaces.

#### Option B: Pydantic AI framework

The most aligned framework -- lightweight, structured IO, tool use. Good agent patterns to follow. Adds a framework dependency for 1-2 agents. May constrain how agents interact with the memory kernel.

#### Option C: LangGraph / CrewAI

Rich multi-agent orchestration. Heavy dependencies (LangChain ecosystem or CrewAI abstractions). Overkill for 1-2 agents. Framework lock-in risk.

#### Option D: A2A SDK AgentExecutor directly

Use the AgentExecutor abstract class as the role interface. Tightly coupled to the A2A protocol. Does not address MCP tool exposure, which requires a different interface.

### 3.5 Decision

**Option A -- No framework, Python Protocol classes.**

For MVP with 1-2 agent roles, a framework adds dependency and abstraction overhead without proportional value. Define a lightweight `AgentRole` Protocol that each role implements. Follow Pydantic AI's patterns (structured inputs, tool registration, structured outputs) without the dependency. Roles integrate with both A2A (via AgentExecutor) and MCP (via tool registration).

Self-healing at the role level:

- Circuit breakers per role via aiobreaker
- Bounded retries with escalation via tenacity
- Health checks exposed through the Protocol interface

Agent learning readiness:

- Log all retrieval queries, results, and feedback from day one
- Data collection enables future learning (cross-encoder reranking, relevance feedback, confidence calibration)
- Structured logging schema defined as part of the role interface

### 3.6 Consequences

**Positive:**

- Minimal dependencies -- just Python standard library + Pydantic for typed IO
- Full control over agent lifecycle, error handling, and observability
- Easy testing -- Protocol classes with mock dependencies
- No framework lock-in -- can adopt Pydantic AI later if agent count grows
- Agent learning data collection built into the role interface from day one

**Negative:**

- More boilerplate than a framework provides; mitigated by creating a shared base class with common lifecycle logic
- Multi-agent orchestration patterns must be built manually if needed; mitigated by the fact that MVP requires only the Researcher role

**Follow-up actions:**

- Define the `AgentRole` Protocol with `execute()`, `cancel()`, and `health_check()` methods
- Implement the Researcher role as the first concrete implementation
- Establish the structured logging schema for learning data
- Define the health check interface and integrate with the `/health` endpoint from ADR-001

### 3.7 Notes and Links

- Monolith-first decision: [ADR-001](./ADR-001-monolith-first.md)
- Dual protocol strategy: [ADR-002](./ADR-002-dual-protocol.md)
- PRD: [Requirements PRD](../../planning/requirements-prd.md)

## 4. Implementation Notes

- The `AgentRole` Protocol is defined in `src/engram/agents/protocol.py`
- Each role implementation lives in its own module under `src/engram/agents/roles/` (e.g., `researcher.py`)
- Roles register their capabilities as A2A skills via the AgentExecutor and as MCP tools via the MCP server
- Structured logging uses Python's `structlog` with a JSON schema that captures query, results, latency, and feedback fields
- Circuit breaker and retry configuration is per-role, following the shared `resilience.py` pattern from ADR-001

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Role unit test coverage | >= 90% | Every CI run |
| Role health check pass rate | 100% | Continuous monitoring |
| Circuit breaker trip rate per role | < 1% per hour | Continuous monitoring |
| Learning data log completeness | 100% of retrieval queries logged | Weekly review |

Review this ADR when any of these signals appear:

- Agent count grows beyond three distinct roles
- Multi-agent orchestration becomes a requirement (roles need to delegate to each other)
- Pydantic AI stabilizes at 1.0+ and framework value proposition changes
- Learning data volume justifies a dedicated training pipeline

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-020 (Architecture Standards) -- decision recorded with context, options, and consequences
- STD-021 (Decision Records) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted Python Protocol classes for agent role architecture
