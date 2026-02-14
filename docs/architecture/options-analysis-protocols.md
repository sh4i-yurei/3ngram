---
id: 3NGRAM-OA-002
title: "Options Analysis: Protocol Strategy"
version: 0.1.0
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-021]
tags: [architecture, options-analysis, 3ngram, mcp, a2a, protocols]
---

# Options Analysis: Protocol Strategy

> **Scope notice**: This analysis predates ADR-003 (Postgres+pgvector). Storage references reflect the evaluation context, not the accepted architecture. See system design v0.1.3 for current state.

# Purpose

Evaluate protocol integration strategies for exposing 3ngram's memory
operations over both MCP (Model Context Protocol) and A2A (Google
Agent-to-Agent Protocol, v0.3). This analysis provides the evidence base
for ADR-002 (Dual Protocol) and ensures the chosen approach satisfies
PRD goals G4 (Protocol Compliance) and NFR-06 (Single-Process Monolith)
while preserving development velocity for a solo developer.

# Scope

This analysis covers the integration architecture for serving two
protocol surfaces from a single codebase:

- **MCP** -- vertical integration (agent-to-tools/context)
- **A2A** -- horizontal integration (agent-to-agent)

It evaluates three options for combining these protocols, scores them
against weighted criteria, and recommends a winner. It does NOT cover:

- Protocol wire-format details (see SDK documentation)
- Individual endpoint design (see module designs D-05 and D-06)
- Authentication mechanisms beyond shared middleware feasibility

# Standard

## Decision context

3ngram must expose its memory kernel through two distinct protocols that
serve fundamentally different interaction patterns:

1. **MCP (Model Context Protocol)** provides tool-calling semantics for
   Claude Code and other MCP clients. The agent invokes discrete
   operations -- `memory.store`, `memory.retrieve`, `memory.search` --
   and receives structured JSON responses. MCP is the primary interface
   for the solo developer's workflow where Claude Code acts as the
   memory consumer.

2. **A2A (Google Agent-to-Agent Protocol, v0.3)** provides task-based
   interaction for external AI agents. An agent discovers 3ngram via its
   Agent Card at `/.well-known/agent-card.json`, sends a research task
   as a JSON-RPC message, and receives streaming results via SSE. A2A
   demonstrates interoperability and positions 3ngram as a participant in
   multi-agent ecosystems.

The PRD (3NGRAM-PRD-001) mandates both protocols:

- FR-06 defines six MCP tools
- FR-07 and FR-08 define the A2A agent card and task lifecycle
- NFR-06 requires a single-process monolith with no inter-service
  communication

The project charter established a monolith-first constraint, and the
existing roadmap (M2, item A-02) requires this analysis before
ADR-002 can be written.

### Driving constraints

- **Single FastAPI process** -- NFR-06 mandates all components in one
  process. Any option requiring multiple processes contradicts a
  settled requirement.
- **A2A v0.3 is pre-release** -- Risk R1 in the PRD. The integration
  must tolerate breaking changes without catastrophic rework.
- **Solo developer** -- Operational overhead matters. Fewer moving parts
  means faster iteration.
- **Docker Compose local dev only** -- No Kubernetes, no service mesh,
  no cloud load balancers.

## Requirements and constraints

### Functional requirements (from PRD)

- FR-06: Expose six MCP tools (`memory.store`, `memory.retrieve`,
  `memory.search`, `memory.get`, `memory.list`, `memory.validate`)
- FR-07: Serve A2A v0.3 agent card at `/.well-known/agent-card.json`
- FR-08: Implement A2A task lifecycle (`message/send`,
  `message/stream`, `tasks/get`, `tasks/cancel`)
- FR-09: Researcher agent role accessible via both protocols

### Non-functional requirements (from PRD)

- NFR-04: A2A TCK compliance (zero failures)
- NFR-06: Single-process monolith (no inter-service HTTP calls)

### Technical constraints

- Python 3.12, FastAPI, Pydantic v2
- `a2a-sdk` provides `A2AFastAPIApplication` with `add_routes_to_app()`
  for mounting on existing FastAPI apps
- `mcp` SDK provides `MCPServer` with `streamable_http_app()` returning
  a Starlette sub-application mountable via `Mount()`
- Both SDKs are FastAPI/Starlette-native

### Architectural constraints

- ADR-001 (monolith-first) is a settled decision -- separate services
  require explicit charter amendment
- Shared domain layer: memory kernel, retrieval engine, Librarian gate

## Options overview

| Option | Summary | Process model |
| --- | --- | --- |
| A | Dual protocol on shared FastAPI service | Single process |
| B | Separate services per protocol | Multiple processes |
| C | Protocol gateway pattern | Single gateway + backend |

## Evaluation criteria (decision rubric)

| # | Criteria | Weight | Description |
| --- | --- | --- | --- |
| C1 | Operational simplicity | 25% | Fewer processes, simpler deployment, lower cognitive overhead for a solo developer |
| C2 | Protocol compliance fidelity | 25% | Ability to pass A2A TCK and MCP integration tests without workarounds or protocol deviations |
| C3 | SDK compatibility | 20% | How naturally the option works with the official SDK classes and methods (no forks, no monkey-patching) |
| C4 | Development velocity | 15% | Time from zero to working dual-protocol endpoint, including testing overhead |
| C5 | Future protocol evolution | 15% | Ability to absorb breaking changes in A2A (pre-1.0) or MCP without architectural rework |

**Scoring scale:** 1 (poor) through 5 (excellent).

## Option analysis

### Option A: Dual protocol -- separate endpoints on shared FastAPI service

#### Description

A single FastAPI application hosts both protocol surfaces as mounted
sub-applications on distinct route prefixes. The A2A SDK's
`A2AFastAPIApplication` mounts its JSON-RPC handler and agent card
endpoint onto the main app via `add_routes_to_app()`. The MCP SDK's
`MCPServer` produces a Starlette ASGI sub-application via
`streamable_http_app()` that is mounted at a separate path using
Starlette's `Mount()`.

Both protocol endpoints call the same domain layer (memory kernel,
retrieval engine, Librarian gate) through in-process function calls.
There is no HTTP hop between protocols and domain logic.

#### Architecture

```text
                 FastAPI Application (single process)
                 ================================
                 |                              |
   /.well-known/agent-card.json     /mcp/ (streamable-http)
   / (JSON-RPC POST)                     |
   /agent/authenticatedExtendedCard      MCPServer.streamable_http_app()
                 |                              |
   A2AFastAPIApplication                MCPServer
   .add_routes_to_app(app)              @mcp.tool() decorators
                 |                              |
                 +--------+  +---------+
                          |  |
                    Domain Layer
                 (memory kernel, retrieval,
                  Librarian gate)
                          |
              +-----------+-----------+
              |                       |
         Postgres               Qdrant
```

#### Route mapping

- `/.well-known/agent-card.json` -- A2A agent card (GET)
- `/` -- A2A JSON-RPC endpoint (POST)
- `/agent/authenticatedExtendedCard` -- A2A extended card (POST)
- `/mcp/` -- MCP streamable-http endpoint (POST/GET/DELETE)
- `/health` -- shared health check (GET)

#### SDK integration details

**A2A SDK** (`a2a-sdk`):

The `A2AFastAPIApplication` class is explicitly designed for this
pattern. Its `add_routes_to_app(app)` method takes an existing FastAPI
(or Starlette) application and adds the A2A routes directly. The SDK
handles JSON-RPC request parsing, method routing (`message/send`,
`message/stream`, `tasks/get`, `tasks/cancel`), SSE streaming, and
agent card serving. The developer implements `AgentExecutor` with
domain-specific logic.

```python
# Pseudocode -- A2A mounting
from a2a.server.apps import A2AFastAPIApplication

a2a_app = A2AFastAPIApplication(
    agent_card=agent_card,
    http_handler=request_handler,
)
a2a_app.add_routes_to_app(app)  # mounts on existing FastAPI app
```

**MCP SDK** (`mcp`):

The `MCPServer` class provides `streamable_http_app()` which returns a
Starlette ASGI application. This sub-application is mounted at a
route prefix using Starlette's `Mount()`. Setting
`streamable_http_path="/"` ensures the MCP endpoint is accessible
directly at the mount point (e.g., `/mcp/` rather than `/mcp/mcp`).

```python
# Pseudocode -- MCP mounting
from starlette.routing import Mount
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("3ngram")

@mcp.tool()
def memory_store(...): ...

# Mount as sub-application
app = Starlette(routes=[
    Mount("/mcp", app=mcp.streamable_http_app(
        json_response=True,
        streamable_http_path="/",
    )),
])
```

A combined lifespan manager handles both the MCP session manager and
any A2A background tasks.

#### A2A error handling

- **Transient errors** (database timeout, Qdrant unavailable): Return
  A2A JSON-RPC error with appropriate code, allow client retry.
- **Fatal errors** (invalid skill, malformed request): Return
  JSON-RPC error with descriptive message.
- **SSE recovery**: If streaming connection drops, clients can
  resubscribe via `tasks/resubscribe` to resume from last event.

#### Strengths

- Single process satisfies NFR-06 with zero deviation
- Both SDKs are designed for this exact integration pattern
- Shared authentication middleware (e.g., API key validation on all
  routes)
- No cross-service coordination, no service discovery, no network
  partition handling
- Domain layer called via in-process function calls (fast, testable)
- Aligns with ADR-001 monolith-first decision

#### Weaknesses

- Protocol coupling: upgrading one SDK may require testing the other
- Single failure domain: a crash takes down both protocol surfaces
- Route conflicts possible if A2A or MCP SDKs claim overlapping paths
  (mitigated by distinct prefixes)

#### Score

| Criteria | Score | Rationale |
| --- | --- | --- |
| C1: Operational simplicity | 5 | Single process, single deploy, single log stream |
| C2: Protocol compliance | 4 | Both SDKs run natively; minor risk of route collision |
| C3: SDK compatibility | 5 | Uses `add_routes_to_app()` and `streamable_http_app()` as designed |
| C4: Development velocity | 5 | Minimal boilerplate, both SDKs mount in < 20 lines |
| C5: Future evolution | 3 | SDK upgrades may require coordinated testing; adapter layer helps |

Weighted score: 4.45.

### Option B: Separate services per protocol

#### Description

Each protocol runs as an independent service in its own process. The
MCP server runs as a standalone FastAPI application on one port. The
A2A server runs as another FastAPI application on a different port. Both
services call a shared backend service (or shared library) for memory
operations. Docker Compose runs three application containers (MCP, A2A,
backend) plus Postgres and Qdrant.

#### Architecture

```text
   MCP Client              A2A Client
       |                       |
   MCP Service             A2A Service
   (port 8001)             (port 8002)
       |                       |
       +------- HTTP/gRPC -----+
                   |
            Backend Service
             (port 8000)
                   |
         +---------+---------+
         |                   |
    Postgres             Qdrant
```

#### SDK integration details

Each service uses its respective SDK in standalone mode:

- MCP service: `MCPServer.run(transport="streamable-http")`
- A2A service: `A2AFastAPIApplication.build()` returns a standalone app

The backend service exposes a REST or gRPC API for memory operations.
Both protocol services translate their respective protocol semantics
into backend API calls.

#### Strengths

- Independent scaling (scale A2A without affecting MCP)
- Independent deployment (upgrade A2A SDK without touching MCP service)
- Fault isolation (A2A crash does not affect MCP)
- Clear separation of concerns

#### Weaknesses

- **Directly contradicts NFR-06** (single-process monolith requirement)
  and ADR-001 (monolith-first). Requires charter amendment.
- Three application processes to manage, monitor, and debug
- Cross-service latency for every memory operation
- Service discovery needed (even if just Docker DNS)
- Distributed error handling, distributed tracing, distributed logging
- State synchronization challenges (if any in-memory state exists)
- Significantly more Docker Compose complexity (5 containers vs 3)
- Overkill for a solo developer with a local dev stack

#### Score

| Criteria | Score | Rationale |
| --- | --- | --- |
| C1: Operational simplicity | 1 | Three app containers, cross-service coordination, distributed debugging |
| C2: Protocol compliance | 5 | Each SDK runs in isolation, zero interference |
| C3: SDK compatibility | 4 | Standalone mode is supported but requires backend API layer |
| C4: Development velocity | 2 | Must build and maintain backend API + two protocol services |
| C5: Future evolution | 5 | SDK upgrades are fully independent |

Weighted score: 3.35.

### Option C: Protocol gateway pattern

#### Description

A single gateway service accepts requests in either MCP or A2A format
and translates them into a normalized internal API. Clients speak their
native protocol; the gateway handles all protocol-specific parsing,
validation, and response formatting. The internal API is protocol-
agnostic. This is conceptually similar to the
[Agent Gateway](https://agentgateway.dev/) project (Linux Foundation),
which provides a unified gateway for MCP and A2A traffic.

#### Architecture

```text
   MCP Client              A2A Client
       |                       |
       +------- Gateway -------+
               (port 8000)
                   |
           Protocol Translation
           (MCP <-> Internal)
           (A2A <-> Internal)
                   |
            Internal API
                   |
            Domain Layer
         (memory kernel, etc.)
                   |
         +---------+---------+
         |                   |
    Postgres             Qdrant
```

#### SDK integration details

The gateway would need custom protocol translators that map between
each SDK's request/response types and the internal API. This means:

- MCP requests parsed by the MCP SDK, then translated to internal calls
- A2A requests parsed by the A2A SDK, then translated to internal calls
- Responses translated back to protocol-specific formats

This is effectively Option A with an additional abstraction layer
between the SDK handlers and the domain logic.

#### Strengths

- Clean protocol abstraction (domain layer never sees protocol details)
- Adding a third protocol requires only a new translator, not new
  domain code
- agentgateway.dev validates the pattern for production use at scale
- Protocol-agnostic internal testing (test domain layer once)

#### Weaknesses

- **Premature abstraction** for an MVP with exactly two protocols
- Translation layer adds latency and complexity
- Must maintain translation mappings for every protocol operation
- agentgateway.dev is nascent (early-stage Linux Foundation project);
  building a custom gateway is significant effort
- The abstraction only pays off when adding a third or fourth protocol,
  which is not on the 3ngram roadmap
- Both SDKs already provide clean handler interfaces (`AgentExecutor`
  for A2A, `@mcp.tool()` for MCP) that naturally call domain logic

#### Score

| Criteria | Score | Rationale |
| --- | --- | --- |
| C1: Operational simplicity | 3 | Single process, but translation layer adds cognitive overhead |
| C2: Protocol compliance | 3 | Translation layer risks protocol fidelity loss |
| C3: SDK compatibility | 2 | Requires wrapping SDK handlers in custom translators |
| C4: Development velocity | 2 | Must build and maintain protocol translation layer |
| C5: Future evolution | 4 | Adding protocols is cleaner, but unlikely for MVP scope |

Weighted score: 2.80.

## Score summary

| Option | C1 (25%) | C2 (25%) | C3 (20%) | C4 (15%) | C5 (15%) | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| A: Dual protocol, shared service | 5 | 4 | 5 | 5 | 3 | **4.45** |
| B: Separate services | 1 | 5 | 4 | 2 | 5 | **3.35** |
| C: Protocol gateway | 3 | 3 | 2 | 2 | 4 | **2.80** |

## Recommendation and rationale

**Recommended: Option A -- Dual protocol on shared FastAPI service.**

Option A is the clear winner across all criteria except future protocol
evolution, where it loses to Option B's full isolation. The reasoning:

1. **SDK design intent.** The A2A SDK's `A2AFastAPIApplication` class
   provides `add_routes_to_app()` specifically to mount on an existing
   FastAPI app. The MCP SDK's `MCPServer` provides
   `streamable_http_app()` specifically to produce a mountable Starlette
   sub-application. Both SDKs are designed for co-hosting. Using them
   this way is not a workaround -- it is the documented integration
   pattern.

2. **NFR-06 compliance.** The PRD requires a single-process monolith.
   Option B violates this outright and would require a charter
   amendment. Option C satisfies it but adds unnecessary abstraction.
   Option A satisfies it naturally.

3. **Monolith-first alignment.** ADR-001 establishes monolith-first as
   the architectural principle. Option A is the direct expression of
   that principle for protocol integration. If protocol isolation
   becomes necessary in the future, refactoring Option A into Option B
   is straightforward -- extract the domain layer into a shared library,
   split the route handlers into separate services.

4. **Solo developer reality.** One process means one log stream, one
   debugger session, one set of health checks. For a solo developer on
   a local Docker Compose stack, this matters more than theoretical
   scalability benefits.

5. **A2A volatility management.** A2A v0.3 is pre-release. When
   breaking changes arrive, Option A confines the blast radius to the
   A2A route handlers and the `AgentExecutor` implementation. The domain
   layer is unaffected. An adapter layer between the A2A handlers and
   the domain logic (thin, not a full gateway) provides the necessary
   insulation without Option C's overhead.

6. **Shared authentication.** FastAPI middleware can enforce API key
   validation on all routes regardless of protocol, avoiding duplicated
   auth logic.

### Risk mitigations for Option A

- **Route collision risk:** A2A defaults to `/` for JSON-RPC and
  `/.well-known/agent-card.json` for discovery. MCP mounts at `/mcp/`.
  No overlap exists with default paths. Integration tests will verify
  no 404/405 regressions when both are mounted.

- **Coupled SDK upgrades:** Pin both SDK versions in `requirements.txt`.
  Test both protocol surfaces in CI. Upgrade one SDK at a time with
  protocol-specific integration tests gating the merge.

- **Single failure domain:** Acceptable for local dev. Health check
  endpoint verifies both Postgres and Qdrant connectivity. Container
  restart policy handles crashes.

## Links and evidence

### Project documents

- PRD: [requirements-prd.md](../planning/requirements-prd.md)
  (3NGRAM-PRD-001)
- Roadmap: [project-roadmap.md](../planning/project-roadmap.md)
  (3NGRAM-ROADMAP-001)
- Charter: [project-charter.md](../governance/project-charter.md)
  (3NGRAM-CHARTER-001)
- Backlog item: A-02 in
  [backlog-milestones.md](../planning/backlog-milestones.md)
- ADR-002 (downstream):
  [ADR-002-dual-protocol.md](adr/ADR-002-dual-protocol.md) (pending)
- System Design (downstream):
  [system-design.md](../design/system-design.md) (pending)

### SDK references

- A2A Python SDK -- `A2AFastAPIApplication.add_routes_to_app()`:
  [A2A server apps API](https://a2a-protocol.org/latest/sdk/python/api/a2a.server.apps)
- MCP Python SDK -- `MCPServer.streamable_http_app()`:
  [MCP Python SDK README](https://github.com/modelcontextprotocol/python-sdk)
- MCP multi-server mounting (Starlette `Mount()`):
  [MCP SDK multiple servers example](https://github.com/modelcontextprotocol/python-sdk/blob/main/README.v2.md)

### External references

- A2A Protocol Specification v0.3:
  <https://google.github.io/A2A/>
- MCP Protocol Specification:
  <https://spec.modelcontextprotocol.io/>
- Agent Gateway (Linux Foundation):
  <https://agentgateway.dev/>
- FastAPI documentation:
  <https://fastapi.tiangolo.com/>

# Implementation Notes

- This analysis feeds directly into ADR-002. The ADR should reference
  this document for detailed scoring and rationale.
- Route prefix assignments (`/` for A2A, `/mcp/` for MCP) are
  recommendations. Final paths will be confirmed in the module design
  for each endpoint (D-05, D-06).
- The adapter layer between protocol handlers and domain logic should
  be thin -- a function call boundary, not a service boundary. It
  exists to insulate the domain from protocol-specific types, not to
  provide full gateway functionality.
- When A2A v1.0 ships with breaking changes, the migration scope is
  limited to the A2A route handlers and the `AgentExecutor`
  implementation. The domain layer and MCP surface remain untouched.

# Continuous Improvement and Compliance Metrics

- Track protocol-specific test coverage (A2A TCK pass rate, MCP
  integration test pass rate) as separate metrics.
- Monitor SDK version currency -- flag when pinned versions are more
  than one minor version behind upstream.
- Re-evaluate this decision if a third protocol surface is proposed
  (triggers consideration of Option C gateway pattern).

# Compliance

This document complies with:

- **STD-001 (Documentation Standard):** All 7 mandatory sections
  present.
- **STD-021 (Architecture Standard):** Options analysis follows
  weighted scoring methodology with explicit criteria.
- **TPL-PRJ-ARCH-OPTIONS:** Decision context, requirements, options
  with scoring, recommendation with rationale, links and evidence.

Verified by: sh4i-yurei
Date: 2026-02-12

# Changelog

- 0.1.0 - Initial protocol strategy options analysis with three options evaluated and Option A recommended.
