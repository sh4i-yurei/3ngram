---
id: 3NGRAM-OA-001
title: "Options Analysis: Architecture Style"
version: 0.1.0
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-021]
tags: [architecture, options-analysis, 3ngram, monolith]
---

# Options Analysis: Architecture Style

> **Scope notice**: This analysis predates ADR-003 (Postgres+pgvector). Storage references reflect the evaluation context, not the accepted architecture. See system design v0.1.3 for current state.

## Purpose

This document evaluates architecture style options for the 3ngram agentic
RAG memory system and records the decision rubric that drives selection.
It provides a structured comparison of three candidate architectures so
the chosen approach is traceable, evidence-backed, and aligned with
project constraints.

## Scope

This analysis covers the top-level runtime architecture for the 3ngram
MVP (v1.0.0). It decides how the system's modules (memory kernel,
retrieval pipeline, Librarian gate, MCP endpoint, A2A endpoint, agent
roles) are packaged and deployed at runtime.

It does NOT cover:

- Storage architecture (Postgres vs. alternatives, Qdrant configuration)
- Embedding model selection
- Protocol-level design (MCP tool schemas, A2A message formats)
- Module-internal design (class hierarchies, function signatures)

Those decisions are addressed in separate options analyses and ADRs.

## Standard

### Decision context

The 3ngram project needs a runtime architecture that supports six
internal modules (memory_kernel, retrieval, librarian, mcp_endpoint,
a2a_endpoint, agents) communicating with two external data stores
(Postgres, Qdrant). The decision is triggered now because architecture
style is the first structural choice in the design phase (M2) and all
downstream artifacts (system design, module designs, specifications)
depend on it.

Key factors driving this decision:

- **Solo developer**: Mark is the sole contributor, reviewer, and
  operator. Operational overhead directly reduces development velocity.
- **Lessons learned**: The previous ai_tech_stack project failed with a
  7-service Docker architecture that produced no working product.
  Premature service decomposition is an identified anti-pattern.
- **Design-first governance**: STD-032 Tier 3 requires full SDLC
  ceremony. Architecture must be simple enough to design, specify, and
  test thoroughly before implementation begins.
- **MVP scope**: Local development only, single user, Docker Compose
  deployment. No production scaling requirements.

### Requirements and constraints

**From the PRD (3NGRAM-PRD-001):**

- NFR-06 mandates a single FastAPI process with no inter-service
  communication (other than Postgres and Qdrant clients)
- FR-05 requires zero-bypass Librarian gate enforcement for all durable
  writes
- FR-03 requires hybrid retrieval combining vector (Qdrant) and keyword
  (Postgres full-text) search
- FR-06 and FR-07/FR-08 require both MCP and A2A protocol endpoints in
  the same system

**From the Charter (3NGRAM-CHARTER-001):**

- Solo developer constraint (no team to distribute service ownership)
- Docker Compose deployment target (no orchestration, no clustering)
- 24-hour cooling period between specification and implementation
- A2A v0.3 is pre-release (adapter pattern required for stability)

**From the Knowledge Base:**

- STD-020 (Design-First Development): Architecture must be fully
  designed before code
- STD-008 (Testing and Quality): Unit tests MUST, integration tests
  MUST, e2e tests MAY
- STD-030 (CI/CD Pipeline Model): 7-gate model applies to all artifacts

**Key constraints summary:**

- Single developer, single user, local dev only
- Python 3.12, FastAPI framework
- Must support both MCP (stdio/SSE) and A2A (HTTP) protocols
- Must enforce Librarian gate with zero bypass paths
- Must handle CPU-bound embedding work without blocking async event loop

### Options overview

- **Option A: Monolith-first** -- Single FastAPI service with
  well-defined internal module boundaries, enforced by import-linter.
  Extract to services only when justified by measured bottlenecks.

- **Option B: Microservices from day one** -- Separate containers for
  each concern (memory, retrieval, librarian, MCP gateway, A2A gateway)
  orchestrated via Docker Compose with HTTP/gRPC inter-service
  communication.

- **Option C: Modular monolith with internal message bus** -- Single
  process with async internal event bus (asyncio queues). Modules
  communicate via events rather than direct function calls, preparing
  for future extraction.

### Evaluation criteria (decision rubric)

Criteria are weighted to reflect project realities: a solo developer
building an MVP on a local workstation, with a failed multi-service
predecessor as cautionary evidence.

| Criteria | Weight | Option A | Option B | Option C |
| --- | --- | --- | --- | --- |
| Operational simplicity | 25% | 9 | 3 | 7 |
| Development velocity (solo developer) | 25% | 9 | 2 | 6 |
| Lessons learned from ai_tech_stack | 20% | 10 | 1 | 7 |
| Extraction readiness (future scaling) | 15% | 6 | 10 | 9 |
| Self-healing capability | 15% | 7 | 8 | 7 |
| **Weighted total** | **100%** | **8.45** | **4.15** | **7.05** |

**Scoring methodology:** Each option scored 1-10 per criterion (10 =
best fit). Weighted total = sum of (score x weight) for each criterion.

**Weighted total calculation:**

- **Option A:** (9 x 0.25) + (9 x 0.25) + (10 x 0.20) + (6 x 0.15) + (7 x 0.15) = 2.25 + 2.25 + 2.00 + 0.90 + 1.05 = **8.45**
- **Option B:** (3 x 0.25) + (2 x 0.25) + (1 x 0.20) + (10 x 0.15) + (8 x 0.15) = 0.75 + 0.50 + 0.20 + 1.50 + 1.20 = **4.15**
- **Option C:** (7 x 0.25) + (6 x 0.25) + (7 x 0.20) + (9 x 0.15) + (7 x 0.15) = 1.75 + 1.50 + 1.40 + 1.35 + 1.05 = **7.05**

### Option analysis

#### Option A: Monolith-first (single FastAPI service, internal module boundaries)

A single Python FastAPI process hosts all six modules as Python packages
under `src/engram/`. Module boundaries are enforced at the import level
using import-linter (or equivalent static analysis). CPU-bound embedding
work runs in a ProcessPoolExecutor to prevent blocking the async event
loop.

**Architecture:**

```text
Docker Compose
  engram (single FastAPI process)
    src/engram/
      memory_kernel/    -- typed records, CRUD, Postgres client
      retrieval/        -- hybrid search, RRF fusion, validation
      librarian/        -- gate enforcement, policy engine, audit trail
      mcp_endpoint/     -- MCP tool definitions, stdio/SSE transport
      a2a_endpoint/     -- A2A agent card, task lifecycle, SSE streaming
      agents/           -- Researcher role, query planner
    ProcessPoolExecutor -- bulkheading for CPU-bound embeddings
  postgres (external)
  qdrant (external)
```

- Strengths:

  - Minimal operational overhead (one container, one process, one log
    stream)
  - Fastest development velocity for solo developer (no serialization,
    no network calls between modules, no service discovery)
  - Direct function calls between modules enable simple debugging (stack
    traces span full request path)
  - Librarian gate enforcement trivially verified (single process, single
    write path, no network bypass)
  - Aligns directly with PRD NFR-06 (single FastAPI process mandate)
  - ProcessPoolExecutor provides CPU bulkheading without service overhead

- Risks:

  - Module boundary violations possible without discipline (mitigated by
    import-linter CI check)
  - Single process failure takes down entire system (mitigated by
    container restart policy and health checks)
  - Cannot independently scale hot modules (acceptable for MVP single-user
    load)

- Trade-offs:

  - Extraction to services requires refactoring later (but modules are
    already package-isolated, and Strangler Fig pattern provides a
    proven migration path)
  - All modules share the same Python dependency tree (acceptable since
    all are Python 3.12 and FastAPI)

- Open questions:

  - None. This option aligns with PRD NFR-06 which already mandates
    single-process architecture.

#### Option B: Microservices from day one

Five separate containers, each owning a single concern. Services
communicate via HTTP or gRPC. Docker Compose orchestrates startup order
and networking.

**Architecture:**

```text
Docker Compose
  memory-service      -- CRUD operations, Postgres client
  retrieval-service   -- vector + keyword search, Qdrant client
  librarian-service   -- gate enforcement, approval queue
  mcp-gateway         -- MCP protocol adapter, routes to services
  a2a-gateway         -- A2A protocol adapter, routes to services
  postgres (external)
  qdrant (external)
```

- Strengths:

  - Maximum extraction readiness (already extracted)
  - Independent scaling per service
  - Technology heterogeneity possible (different languages per service)
  - Clear network-level boundaries enforce module isolation

- Risks:

  - **Operational complexity is prohibitive for a solo developer.** Five
    services require five Dockerfiles, five health checks, five log
    streams, network configuration, service discovery, and distributed
    tracing.
  - **The ai_tech_stack project used exactly this pattern and failed.**
    Seven Docker services with no integration tests produced
    unmaintainable garbage. This is documented evidence of the approach
    failing in identical conditions (same developer, same toolchain,
    same constraints).
  - Distributed Librarian gate enforcement is harder to verify (network
    calls can be bypassed, timeouts create inconsistent state)
  - Integration testing requires all services running (slow CI, flaky
    tests)
  - Serialization overhead for every module-to-module call (JSON/protobuf
    encode/decode on localhost)

- Trade-offs:

  - Pays the full cost of distribution upfront with no users to justify
    it
  - Designed for a team that does not exist and scale that is not needed

- Open questions:

  - How would Librarian gate zero-bypass be verified across network
    boundaries? (No satisfactory answer identified.)

#### Option C: Modular monolith with internal message bus

A single process (like Option A) but modules communicate via an async
internal event bus (asyncio queues) instead of direct function calls.
aiobreaker provides circuit breakers between modules. This is a
middle-ground that prepares for future extraction by decoupling module
interfaces at the messaging level.

**Architecture:**

```text
Docker Compose
  engram (single FastAPI process)
    src/engram/
      memory_kernel/    -- publishes MemoryCreated, MemoryUpdated events
      retrieval/        -- subscribes to query events, publishes results
      librarian/        -- subscribes to write requests, publishes verdicts
      mcp_endpoint/     -- translates MCP calls to internal events
      a2a_endpoint/     -- translates A2A messages to internal events
      agents/           -- orchestrates event sequences
      bus/              -- asyncio queue-based event dispatcher
    aiobreaker          -- circuit breakers between module boundaries
  postgres (external)
  qdrant (external)
```

- Strengths:

  - Stronger module boundaries than Option A (event contracts instead
    of function signatures)
  - Extraction to services is simpler (replace in-process queue with
    external message broker)
  - Circuit breakers provide self-healing at module boundaries
  - Single process retains operational simplicity of a monolith

- Risks:

  - Event bus adds indirection that complicates debugging (event traces
    instead of stack traces)
  - Event schema evolution requires discipline (versioned event contracts)
  - Async event ordering can introduce subtle bugs (race conditions,
    lost events)
  - Overhead of event serialization/deserialization within a single
    process provides no performance benefit

- Trade-offs:

  - More complex than Option A for marginal extraction readiness gains
  - Event bus is infrastructure that must be designed, tested, and
    maintained before any business logic can use it
  - Debugging requires event correlation tooling (tracing, logging) that
    does not exist yet

- Open questions:

  - Is the extraction readiness benefit worth the complexity cost for an
    MVP with no identified scaling requirements?
  - How does the event bus interact with ProcessPoolExecutor for
    CPU-bound embedding work?

### Recommendation and rationale

Selected: Option A (Monolith-first).

Option A wins on weighted score (8.45 vs. 7.05 for Option C and 4.15
for Option B) and aligns with three converging lines of evidence:

1. **PRD mandate.** NFR-06 already requires a single FastAPI process
   with no inter-service communication. Option A is the only option
   that directly satisfies this requirement without workarounds.

2. **Empirical evidence.** The ai_tech_stack project (same developer,
   same Python stack, same WSL2 environment) failed with premature
   microservices. Industry data supports this: 42% of organizations are
   consolidating back to monoliths (CNCF Survey 2025), and Amazon Prime
   Video reduced infrastructure costs by 90% by collapsing a
   microservices pipeline into a monolith.

3. **Solo developer economics.** Every hour spent on service
   orchestration, distributed tracing, and network debugging is an hour
   not spent on the core value proposition (typed memory, validated
   retrieval, Librarian gate). Option A minimizes operational overhead
   and maximizes development velocity.

**Why not Option C?** While the modular monolith with event bus scores
well on extraction readiness (9 vs. 6 for Option A), the extraction
readiness difference is insufficient to justify the added complexity.
Option A achieves adequate extraction readiness through Python package
boundaries, import-linter enforcement, and the Strangler Fig pattern.
The event bus adds infrastructure that must be designed and maintained
before any business logic benefits from it.

**Extraction signals (when to reconsider):**

Option A should be reconsidered if any of the following occur:

- A module needs to be written in a different language
- A module needs independent deployment (different release cadence)
- A module needs independent horizontal scaling (measured, not assumed)
- ProcessPoolExecutor bulkheading proves insufficient for CPU-bound work

At that point, apply the Strangler Fig pattern: extract the specific
module behind an internal API boundary, deploy as a separate service,
and route traffic through a proxy.

**Risks to mitigate:**

- **Boundary erosion**: import-linter enforced in CI (Gate C). Modules
  may only depend on explicitly declared imports.
- **Single-process failure**: Docker restart policy (`restart: unless-stopped`),
  health check endpoint, structured logging for post-mortem analysis.
- **Self-healing**: aiobreaker circuit breakers at module boundaries
  (Qdrant client, embedding calls), tenacity retry decorators for
  transient failures, component-level health checks exposed via
  `/health` endpoint.
- **CPU-bound blocking**: ProcessPoolExecutor for embedding generation.
  Prevents CPU-intensive fastembed calls from blocking the async event
  loop.

### Links and evidence

**Project artifacts:**

- System Design: [docs/design/system-design.md](../design/system-design.md) (pending)
- ADR: [docs/architecture/adr/ADR-001-monolith-first.md](adr/ADR-001-monolith-first.md) (pending)
- Charter: [docs/governance/project-charter.md](../governance/project-charter.md)
- PRD: [docs/planning/requirements-prd.md](../planning/requirements-prd.md)

**Knowledge base standards:**

- STD-001: Documentation Standard
- STD-020: Design-First Development Standard
- STD-021: Architecture Standard
- STD-032: SDLC With AI (Tier 3 workflow)

**External evidence:**

- [CNCF Annual Survey 2025](https://www.cncf.io/reports/cncf-annual-survey-2024/) --
  42% of organizations consolidating microservices back to monoliths
- Amazon Prime Video case study: reduced costs 90% by collapsing
  distributed video monitoring pipeline to a monolith
  ([Amazon Prime Video Tech Blog](https://www.primevideotech.com/video-quality/scaling-up-the-prime-video-audio-video-monitoring-service-and-reducing-costs-by-90))
- ai_tech_stack project (deprecated, this repo) -- 7 Docker services,
  no integration tests, no working product. Direct evidence of premature
  service decomposition failure under identical project constraints.

**Tools referenced:**

- [import-linter](https://import-linter.readthedocs.io/) -- static
  analysis for Python import boundary enforcement
- [aiobreaker](https://pypi.org/project/aiobreaker/) -- async circuit
  breaker for Python
- [tenacity](https://pypi.org/project/tenacity/) -- retry library for
  Python

## Implementation Notes

- Keep one decision per analysis to maintain traceability.
- Update this analysis if constraints or requirements change (e.g., if
  multi-developer team is added, Option B or C should be re-evaluated).
- The corresponding ADR (ADR-001-monolith-first) should be created after
  this analysis is approved, referencing the weighted rubric and
  evidence presented here.
- import-linter contract configuration should be defined during the
  module design phase and enforced in CI Gate C.

## Continuous Improvement and Compliance Metrics

- Track whether the monolith architecture decision holds through MVP
  delivery or requires amendment.
- Monitor for extraction signals (listed in Recommendation section)
  during implementation.
- If extraction occurs, create a new options analysis for the specific
  module being extracted and a superseding ADR.
- Record decision reversal rate across all options analyses in the
  project.

## Compliance

This document complies with:

- **STD-001 (Documentation Standard)**: All 7 mandatory sections present
  (Purpose, Scope, Standard, Implementation Notes, Continuous
  Improvement, Compliance, Changelog).
- **STD-021 (Architecture Standard)**: Options evaluated with weighted
  rubric, evidence cited, rationale documented.
- **TPL-PRJ-ARCH-OPTIONS (v0.1.2)**: All template sections populated
  (Decision context, Requirements and constraints, Options overview,
  Evaluation criteria, Option analysis, Recommendation, Links).

Verified by: sh4i-yurei
Date: 2026-02-12

## Changelog

- 0.1.0 - Initial architecture style options analysis with three options evaluated, weighted rubric, and monolith-first recommendation.
