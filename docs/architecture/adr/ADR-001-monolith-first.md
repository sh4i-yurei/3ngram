---
id: 3NGRAM-ADR-001
title: "ADR-001: Monolith-first architecture"
version: 0.1.0
category: project
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-021]
tags: [adr, architecture, monolith, 3ngram]
---

## 1. Purpose

Record the architectural style decision for the 3ngram MVP and capture the reasoning, alternatives considered, and consequences so that future contributors understand why a monolith-first approach was chosen over microservices.

## 2. Scope

This decision applies to the entire 3ngram system at the service-deployment level. It governs how modules (memory kernel, retrieval engine, librarian gate, MCP endpoint, A2A endpoint, agents) are packaged and deployed for the MVP and near-term iterations.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-001 |
| Status | Accepted |
| Date | 2026-02-12 |
| Deciders | sh4i-yurei |

### 3.2 Context

3ngram needs an architecture style for its MVP. The predecessor project (ai_tech_stack) used seven Docker services from day one and failed -- complexity grew faster than value, no integration tests existed, and silent failures across service boundaries went undetected for days.

3ngram is built by a solo developer. Operational overhead must be minimized to preserve development velocity. Industry data supports this direction: 42% of organizations are consolidating back to monoliths according to the CNCF 2025 survey.

### 3.3 Decision Drivers

- **Operational simplicity** -- a solo developer cannot sustain multi-service operations
- **Development velocity** -- fast iteration on a single codebase with one test suite
- **Lessons from ai_tech_stack** -- seven-service architecture failed; complexity outpaced value
- **Extraction readiness** -- module boundaries must be clean enough to extract later if needed
- **Self-healing capability** -- resilience patterns (circuit breakers, retries) at module boundaries

### 3.4 Options

#### Option A: Monolith-first (single FastAPI, internal module boundaries)

A single Python FastAPI service with clearly defined module boundaries enforced by import-linter. CPU-bound embedding work is bulkheaded via ProcessPoolExecutor. Modules communicate through direct function calls and typed interfaces.

#### Option B: Microservices from day one (separate containers per concern)

Each concern (memory, retrieval, librarian, protocols) runs as an independent Docker container with its own API. Communication over HTTP or gRPC. Requires service discovery, distributed tracing, and per-service CI/CD pipelines.

#### Option C: Modular monolith with event bus (single process, async events)

A single process with an internal async event bus decoupling modules. Modules communicate exclusively through published events rather than direct calls.

### 3.5 Decision

**Option A -- Monolith-first.**

Single Python FastAPI service with clear module boundaries:

- `memory_kernel` -- storage and embedding management
- `retrieval` -- search and ranking
- `librarian` -- quality gate and curation
- `mcp_endpoint` -- MCP protocol surface
- `a2a_endpoint` -- A2A protocol surface
- `agents` -- agent definitions and orchestration

Boundary enforcement via import-linter rules. ProcessPoolExecutor for CPU-bound embedding bulkheading. Self-healing via aiobreaker (circuit breakers) and tenacity (retries) at module boundaries. Extract to separate services only when measured bottlenecks justify it.

### 3.6 Consequences

**Positive:**

- Minimal operational overhead for a solo developer
- Fast iteration with a single test suite and deployment unit
- Easy debugging -- one process, one log stream, standard profiling tools
- Simple CI/CD pipeline -- single build, single deploy
- Self-healing via aiobreaker circuit breakers and tenacity retries at module boundaries

**Negative:**

- Cannot scale modules independently (acceptable at MVP scale where all modules share similar load profiles)
- Single failure domain -- mitigated with health checks and graceful degradation at module boundaries

**Follow-up actions:**

- Define module boundary contracts (typed interfaces per module)
- Configure import-linter rules to enforce boundary discipline
- Establish extraction signals: document the metrics (latency, throughput, resource contention) that would justify breaking out a service

### 3.7 Notes and Links

- Options analysis: [Architecture Options Analysis](../options-analysis-architecture.md)
- Project charter: [Project Charter](../../governance/project-charter.md)
- CNCF 2025 Annual Survey on monolith consolidation trends

## 4. Implementation Notes

- import-linter configuration lives in `pyproject.toml` under `[tool.importlinter]`
- ProcessPoolExecutor pool size should be set via environment variable (`EMBEDDING_WORKERS`, default 2)
- Circuit breaker thresholds (aiobreaker) and retry policies (tenacity) are configured per module boundary in a shared `resilience.py` module
- Health check endpoint at `/health` aggregates module-level health status

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| import-linter violations | 0 | Every CI run |
| Module boundary test coverage | >= 90% | Weekly |
| Circuit breaker trip rate | < 1% per hour | Continuous monitoring |
| Time to extract a module (estimate) | < 2 days | Quarterly review |

Review this ADR when any of these signals appear:

- A single module consumes more than 60% of total CPU or memory
- Request latency for one module degrades others by more than 200ms p95
- Team size grows beyond two developers working on the same module

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-020 (Architecture Standards) -- decision recorded with context, options, and consequences
- STD-021 (Decision Records) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted monolith-first architecture for 3ngram MVP
