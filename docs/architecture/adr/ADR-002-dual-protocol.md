---
id: 3NGRAM-ADR-002
title: "ADR-002: Dual protocol strategy (MCP + A2A)"
version: 0.1.0
category: project
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-021]
tags: [adr, architecture, mcp, a2a, protocols, 3ngram]
---

## 1. Purpose

Record the decision on how 3ngram exposes its capabilities through two complementary protocols -- MCP (Model Context Protocol) for vertical agent-to-tools/context integration and A2A (Agent-to-Agent) for horizontal agent interoperability -- and how these protocols coexist at the transport and application layer.

## 2. Scope

This decision applies to the protocol integration layer of 3ngram. It governs the transport configuration, route structure, authentication strategy, and error handling for both MCP and A2A endpoints within the FastAPI application.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-002 |
| Status | Accepted |
| Date | 2026-02-12 |
| Deciders | sh4i-yurei |

### 3.2 Context

3ngram must expose its capabilities through two complementary protocols:

- **MCP (Model Context Protocol)** -- vertical integration: agent-to-tools and agent-to-context. This is the primary interface for Claude Code and other MCP-compatible clients to invoke 3ngram tools and retrieve context.
- **A2A (Agent-to-Agent)** -- horizontal integration: agent-to-agent interoperability. This allows external agents to discover 3ngram capabilities, negotiate tasks, and exchange structured results.

The question is how these two protocols coexist at the transport and application layer without creating unnecessary operational complexity or logic duplication.

### 3.3 Decision Drivers

- **Protocol compliance fidelity** -- each protocol has specific SDK expectations and spec requirements that must be met without compromise
- **SDK compatibility** -- both the A2A Python SDK and the MCP Python SDK are designed to mount onto existing ASGI/FastAPI applications
- **Operational simplicity** -- consistent with ADR-001 monolith-first approach
- **Development velocity** -- shared domain logic, single test harness, one deployment
- **Future protocol evolution** -- both protocols are actively evolving (A2A is pre-1.0); the architecture must accommodate breaking changes without full rewrites

### 3.4 Options

#### Option A: Dual protocol -- separate endpoints on shared FastAPI service

Both protocols mount on the same FastAPI application at distinct route prefixes. They share the domain layer (memory kernel, retrieval engine, librarian gate) and authentication middleware. Each protocol has its own error handling and serialization.

#### Option B: Separate services per protocol

Each protocol runs as an independent service with its own FastAPI instance. Communication to shared domain logic happens over internal HTTP or a shared library. Requires inter-service networking and separate deployments.

#### Option C: Protocol gateway pattern (translate between protocols)

A single gateway service translates incoming requests from either protocol into a canonical internal format, then dispatches to the domain layer. Outgoing responses are translated back to the originating protocol format.

### 3.5 Decision

**Option A -- Dual protocol with separate endpoints on a shared FastAPI service.**

Route structure:

- A2A via `A2AFastAPIApplication.add_routes_to_app()` mounted at `/` with agent card at `/.well-known/agent-card.json`
- MCP via `MCPServer` with streamable-http transport mounted at `/mcp/`

Both protocol endpoints call the same domain layer:

- `memory_kernel` -- storage and embedding operations
- `retrieval` -- search and ranking operations
- `librarian` -- quality gate and curation logic

Shared authentication middleware handles API key validation for both protocols, with a clear path to OAuth expansion.

### 3.6 Consequences

**Positive:**

- Single deployment aligns with [ADR-001](./ADR-001-monolith-first.md) monolith-first strategy
- Both SDKs are designed for this pattern -- `A2AFastAPIApplication` mounts on existing FastAPI apps, MCP streamable-http runs as a sub-application
- Shared domain layer prevents logic duplication between protocol surfaces
- Shared authentication middleware provides consistent security posture across both protocols

**Negative:**

- Both protocols share a failure domain -- mitigated with separate error handling middleware per endpoint prefix and circuit breakers at the protocol-to-domain boundary
- A2A v0.3 is pre-1.0 -- breaking changes in future versions may require adapter updates; mitigated by pinning SDK version and isolating A2A-specific code in `a2a_endpoint` module

**Follow-up actions:**

- Define route prefix strategy and document it in the developer guide
- Implement protocol-specific error handling middleware for `/mcp/` and `/` (A2A) route groups
- Pin A2A SDK version in `pyproject.toml` with an upper bound
- Plan upgrade path for A2A SDK version bumps (adapter pattern in `a2a_endpoint` module)

### 3.7 Notes and Links

- Options analysis: [Protocol Options Analysis](../options-analysis-protocols.md)
- Monolith-first decision: [ADR-001](./ADR-001-monolith-first.md)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [A2A Protocol Repository](https://github.com/google/A2A)

## 4. Implementation Notes

- A2A routes are added first (mounted at root), then MCP routes (mounted at `/mcp/`) to avoid route conflicts
- The agent card at `/.well-known/agent-card.json` is served as a static JSON response generated from the `AgentCard` dataclass at startup
- MCP streamable-http transport requires SSE (Server-Sent Events) support; FastAPI handles this natively via `StreamingResponse`
- Authentication middleware inspects the `Authorization` header before either protocol handler runs; protocol-specific auth extensions (MCP token exchange, A2A agent credentials) are layered on top
- Domain layer functions are async-first; synchronous embedding operations are offloaded to ProcessPoolExecutor per ADR-001

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| MCP endpoint response latency (p95) | < 500ms | Continuous monitoring |
| A2A endpoint response latency (p95) | < 500ms | Continuous monitoring |
| Protocol compliance test pass rate | 100% | Every CI run |
| Authentication bypass attempts | 0 | Continuous monitoring |
| A2A SDK version drift from latest | <= 1 minor version | Monthly review |

Review this ADR when any of these signals appear:

- A2A specification reaches 1.0 (review adapter pattern and route structure)
- MCP specification introduces breaking transport changes
- A third protocol integration is required (evaluate gateway pattern at that point)
- Protocol-specific load diverges significantly (one endpoint receives 10x the other)

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-020 (Architecture Standards) -- decision recorded with context, options, and consequences
- STD-021 (Decision Records) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted dual protocol strategy with MCP and A2A on shared FastAPI service
