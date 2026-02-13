---
id: 3NGRAM-PRD-001
title: "3ngram: Agentic RAG Memory System — Product Requirements Document"
version: 0.1.0
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-020, STD-032]
tags: [prd, requirements, planning, 3ngram]
---

> **Scope notice**: This PRD reflects the original M1 scope (4 memory
> types, Postgres+Qdrant). For the current architecture, see System
> Design v0.1.2 (8 memory types, Postgres+pgvector, ADRs 007-012
> supersede 004-006).

# 3ngram: Agentic RAG Memory System — Product Requirements Document

## Purpose

This Product Requirements Document (PRD) defines the functional and non-functional requirements for **3ngram**, an agentic RAG (Retrieval-Augmented Generation) memory system designed to serve as a kernel-governed memory operating system for AI agents. It establishes the contractual baseline for what the system must do, how well it must perform, and what constraints it must operate within.

This document is the authoritative source for implementation decisions during the architecture, design, and specification phases. It translates the strategic vision from the project charter into concrete, testable requirements.

## Scope

### In Scope

- Complete functional requirements for memory types, CRUD operations, hybrid retrieval, validation, Librarian gate, MCP tools, A2A agent card, task lifecycle, and Researcher agent role
- Non-functional requirements for performance, durability, enforcement, compliance, and resource constraints
- User stories and stakeholder analysis
- Technical constraints and environmental assumptions
- Risk analysis and dependency mapping
- Milestone definitions and success criteria

### Out of Scope

- Detailed API specifications (covered in API Design document)
- Database schema details (covered in Data Model Design document)
- Code-level implementation details (covered in Technical Specification)
- Deployment and infrastructure beyond local Docker Compose stack
- Multi-user authentication and authorization (deferred to post-MVP)
- Advanced features listed in Non-Goals section

## Standard

### 1. Background and Context

#### Problem Statement

Modern AI agents, including Claude Code and other LLM-powered assistants, suffer from a critical limitation: they cannot reliably retain and recall structured knowledge across sessions. Each interaction starts with a clean slate, forcing users to repeatedly provide context, explain decisions, and reconstruct mental models. This manifests in several concrete failures:

1. **Decision Amnesia**: Architectural decisions made in session N are forgotten by session N+1, leading to contradictory recommendations or repeated debates over settled questions.
2. **Context Reconstruction Overhead**: Users spend 20-30% of each session re-explaining project structure, coding standards, and past decisions.
3. **Inconsistent Behavior**: Agents cannot maintain stable beliefs or behavioral patterns across sessions, making them unreliable for long-running projects.
4. **Lost Institutional Knowledge**: Valuable insights, lessons learned, and problem-solving patterns discovered during one session vanish when the session ends.

The intake problem statement (3NGRAM-INTAKE-001) documents a specific instance where Claude Code failed to recall a previously established branching strategy, resulting in a 15-minute context re-establishment cycle. This is not an isolated incident—it represents a systemic deficiency in agent memory architecture.

#### Prior Art and Lessons Learned

The **ai_tech_stack** project (now deprecated) was a first attempt at building an AI development infrastructure. It failed due to:

- **Over-engineering**: Tried to solve too many problems at once (memory + orchestration + deployment + monitoring)
- **Premature Distribution**: Multi-service architecture before understanding single-service requirements
- **Tool Fragmentation**: Too many overlapping tools with unclear responsibilities
- **Lack of Governance**: No enforcement mechanism for memory integrity, leading to inconsistent state

Key lessons applied to 3ngram:

- **Start Monolithic**: Single FastAPI process, prove the memory model works before distributing
- **Governance First**: Librarian gate is non-negotiable, zero bypass paths
- **Clear Protocols**: MCP for tool invocation, A2A for agent collaboration, no custom protocols
- **Validation Built-In**: Retrieval validation (provenance, temporal, contradiction) is not optional

#### Strategic Context

3ngram is the **foundational infrastructure** for a broader vision of agent-driven development. It is the first production project following the completion of the policies-and-standards knowledge base (93 governed documents, Tier 1 rigor). This project validates:

- The SDLC_With_AI workflow (STD-032) in practice
- The CI/CD 7-gate model (STD-030) with real code
- The Documentation Standard (STD-001) applied to technical artifacts
- The Testing and Quality Standard (STD-008) with agent-parseable diagnostics

Success here proves the knowledge base works. Failure here identifies gaps in the governance framework.

### 2. Goals and Success Criteria

#### Primary Goals

#### G1: Durable Agent Memory

Provide a persistence layer that allows AI agents to reliably store and retrieve structured knowledge across sessions, eliminating context reconstruction overhead.

#### Success Criteria

- Agent can recall a decision made 30 days prior with correct rationale and metadata
- Zero data loss on clean shutdown/restart (verified by integration tests)
- Superseded beliefs correctly marked with replacement links

#### G2: Governed Memory Writes

Enforce 100% gate compliance for all durable memory writes through the Librarian role, preventing corruption and ensuring auditability.

#### Success Criteria

- Integration tests verify zero bypass paths (attempt direct DB write, expect failure)
- Audit trail logs every approve/reject decision with timestamp and reason
- Manual approval queue processes high-risk writes (new beliefs, supersessions)

#### G3: Validated Retrieval

Return retrieval results with provenance, temporal validity, contradiction detection, and confidence scoring, ensuring agents can trust the information they receive.

#### Success Criteria

- Every retrieved record includes citation to source UUID
- Expired or superseded records automatically filtered out
- Contradictory results flagged with explanation
- Confidence scores correlate with retrieval accuracy (validation dataset TBD)

#### G4: Protocol Compliance

Implement MCP and A2A v0.3 protocols to specification, enabling interoperability with Claude Code and other agent ecosystems.

#### Success Criteria

- MCP tools pass Claude Code integration tests (manual verification)
- A2A agent card validates against schema
- A2A TCK (Test Compatibility Kit) passes with zero failures

#### G5: Local Dev Excellence

Provide a frictionless Docker Compose stack for local development, with < 2 minute cold start and clear health check feedback.

#### Success Criteria

- `docker-compose up` starts all services (engram, Postgres, Qdrant) in < 2 minutes
- Health check endpoint returns 200 when all dependencies ready
- Example queries in README execute successfully on first run

#### Secondary Goals

#### G6: Performance Baseline

Establish performance benchmarks for hybrid retrieval on local hardware (WSL2, RTX 3070 available).

#### Success Criteria

- p95 retrieval latency < 2 seconds for hybrid search (10 results, 100k memory corpus)
- Embedding generation < 500ms per record (fastembed default; GPU models available)
- Memory footprint < 4GB RSS under normal load (1000 records, 10 concurrent queries)

#### G7: Documentation Completeness

Produce governance-compliant documentation following STD-001, enabling future developers (including AI agents) to understand and extend the system.

#### Success Criteria

- All 7 mandatory sections present in every governed document
- API documentation includes examples for every endpoint
- Runbook covers startup, health checks, common failures, and shutdown

### 3. Non-Goals

The following are explicitly **out of scope** for the MVP (v1.0.0) release. They may be considered for future iterations but will not block the initial launch.

#### NG1: Knowledge Graph

No explicit knowledge graph structure (nodes, edges, semantic relationships). Memories are stored as typed records with metadata, not as a graph database.

#### NG2: Additional Agent Roles

Only the Researcher and Librarian roles are implemented. The following are deferred:

- Archivist (retention policy enforcement)
- Curator (deduplication, summarization)
- Guardian (access control, audit reporting)
- Judge (multi-agent memory conflict resolution)

#### NG3: Multi-Workspace Support

No concept of separate memory workspaces or namespaces. All memories share a single global store. Filtering by metadata must be handled at query time.

#### NG4: Workspace Adapters

No integrations with external workspaces (Git repos, Notion, Obsidian, file systems). All memory input is via MCP tools or A2A messages.

#### NG5: Vector Database Alternatives

Qdrant is the only supported vector store. No pluggable abstraction for Pinecone, Weaviate, etc.

#### NG6: Embedding Model Configurability

fastembed with a single default model (BAAI/bge-small-en-v1.5 or similar). No runtime model switching.

#### NG7: Multi-User Authentication

No OAuth2, no user sessions, no RBAC. Single API key for all access. Deferred to post-MVP.

#### NG8: Distributed Deployment

No Kubernetes manifests, no cloud deployment guides, no horizontal scaling. Docker Compose local dev only.

#### NG9: Real-Time Synchronization

No push notifications, no WebSocket updates, no live memory invalidation across agents. Agents must poll for changes.

#### NG10: Advanced Retrieval

No semantic reranking, no query expansion, no multi-hop reasoning. Hybrid retrieval (vector + keyword + fusion) is the limit.

### 4. Users and Stakeholders

#### Primary Users

#### U1: Mark (Solo Developer)

- **Role**: Project owner, primary developer, first user
- **Needs**: Local dev environment, clear documentation, fast iteration cycles
- **Success Metric**: Can implement a new feature and test it end-to-end in < 30 minutes
- **Interaction**: Direct Docker Compose usage, manual testing, API exploration

#### U2: Claude Code (AI Agent)

- **Role**: Primary AI agent consumer, MCP client
- **Needs**: Reliable memory persistence, validated retrieval, clear error messages
- **Success Metric**: Can store a decision in session N and recall it accurately in session N+10
- **Interaction**: MCP tool invocation (memory.store, memory.retrieve, memory.search)

#### U3: A2A-Compatible Agents

- **Role**: External AI agents discovering 3ngram via agent card
- **Needs**: A2A v0.3 compliance, streaming task responses, clear capability declaration
- **Success Metric**: Can invoke research task and receive cited results via A2A message
- **Interaction**: HTTP POST to /a2a/v1/message/send, SSE streaming via /a2a/v1/message/stream

#### Secondary Stakeholders

#### S1: Future Contributors

- **Role**: Developers extending 3ngram post-MVP
- **Needs**: Comprehensive documentation, clear architecture, testable components
- **Success Metric**: Can understand the Librarian gate invariant from docs alone
- **Interaction**: Code reading, documentation review, local dev setup

#### S2: Governance Framework

- **Role**: The policies-and-standards knowledge base
- **Needs**: Proof that STD-032 (SDLC_With_AI) works in practice
- **Success Metric**: 3ngram project artifacts (PRD, TDD, API Design) validate the template structure
- **Interaction**: Passive compliance validation via CI/CD gates

### 5. Requirements

#### 5.1 Functional Requirements

##### FR-01: Memory Types

#### Description

The system SHALL support four distinct memory types, each with a specific semantic purpose and lifecycle.

#### Memory Types

1. **Decision** (type: "decision")
   - Records architectural, design, or behavioral choices with rationale
   - Examples: "Use Pydantic v2 for data validation", "Reject GraphQL, use REST"
   - Immutable once created (updates create new versions)
   - Typically superseded rather than updated

2. **Belief** (type: "belief")
   - Represents current understanding of facts, assumptions, or models
   - Examples: "User prefers squash-merge workflow", "Project uses Python 3.12"
   - Can be superseded when understanding changes
   - Temporal validity enforced (valid_from → valid_to)

3. **Episode** (type: "episode")
   - Captures interaction sequences, events, or session logs
   - Examples: "Implemented feature X with challenges Y", "Debugged issue Z"
   - Immutable (historical record)
   - May reference other memories via metadata

4. **Skill** (type: "skill")
   - Reusable procedural knowledge (how-to, patterns, templates)
   - Examples: "How to scaffold a new FastAPI service", "Git commit message format"
   - Can be composite (skill references other skills)
   - Versioned to track improvements

#### Record Schema

All memory types share the following fields:

```python
{
    "id": UUID,                          # Unique identifier
    "type": str,                         # One of: decision, belief, episode, skill
    "content": str,                      # Primary text content (unlimited length)
    "metadata": dict,                    # Arbitrary JSON metadata
    "version": int,                      # Version number (starts at 1, increments on update)
    "created_at": datetime,              # ISO 8601 timestamp
    "updated_at": datetime,              # ISO 8601 timestamp (set on every version)
    "superseded_by": UUID | None,        # Points to replacement record if superseded
    "temporal_valid_from": datetime,     # When this memory becomes valid
    "temporal_valid_to": datetime | None # When this memory expires (None = indefinite)
}
```

#### Acceptance Criteria

- [ ] Postgres schema includes all fields for all types
- [ ] Pydantic models enforce type safety and validation
- [ ] Create operation rejects invalid types
- [ ] Retrieve operation filters by type correctly
- [ ] Metadata field accepts arbitrary JSON (tested with nested objects, arrays)

##### FR-02: Memory CRUD Operations

#### Description

The system SHALL provide create, read, update, supersede, and archive operations for all memory types, with consistency guarantees across Postgres and Qdrant.

#### Operations

#### Create

- Input: Memory type, content, metadata, temporal validity range
- Process:
  1. Validate input against Pydantic model
  2. Submit write request to Librarian gate (FR-05)
  3. On approval: insert into Postgres (transactional)
  4. Generate embedding via fastembed
  5. Upsert embedding + metadata to Qdrant (point ID = memory UUID)
- Output: Created memory record with UUID
- Error Conditions: Validation failure, Librarian rejection, Postgres constraint violation, Qdrant timeout

#### Read

- By ID: Fetch single record by UUID
- By type: Fetch all records of a given type (paginated, default limit 100)
- By time range: Filter by created_at or updated_at (inclusive range)
- By metadata filter: JSONPath query on metadata field
- Output: List of memory records matching criteria
- Error Conditions: Invalid UUID, malformed JSONPath query

#### Update

- Input: Existing memory UUID, new content or metadata
- Process:
  1. Fetch current version from Postgres
  2. Increment version number
  3. Create new record (same UUID, new version)
  4. Submit to Librarian gate
  5. On approval: insert new version, update updated_at
  6. Regenerate embedding, upsert to Qdrant
- Output: Updated memory record with incremented version
- Error Conditions: UUID not found, Librarian rejection
- **Invariant**: Old versions are preserved (append-only log)

#### Supersede

- Input: Old memory UUID, new memory UUID
- Process:
  1. Validate both UUIDs exist
  2. Set old_memory.superseded_by = new_memory.id
  3. Set old_memory.temporal_valid_to = now()
  4. Submit update to Librarian gate
  5. On approval: commit Postgres transaction
- Output: Confirmation of supersession
- Error Conditions: UUID not found, circular supersession (A supersedes B supersedes A)

#### Archive

- Input: Memory UUID, retention policy metadata
- Process:
  1. Set temporal_valid_to = now()
  2. Add metadata flag: {"archived": true, "archived_at": "ISO8601"}
  3. Submit to Librarian gate
  4. On approval: commit Postgres transaction
  5. Do NOT delete from Qdrant (soft delete only)
- Output: Archived memory record
- Error Conditions: UUID not found, Librarian rejection

#### Acceptance Criteria

- [ ] All operations pass Librarian gate (integration test verifies)
- [ ] Postgres transactions rollback on Qdrant failure
- [ ] Append-only guarantee: old versions queryable by version number
- [ ] Supersession chain: A → B → C correctly resolves to C
- [ ] Archive operation sets temporal_valid_to and metadata flag

##### FR-03: Hybrid Retrieval

#### Description

The system SHALL support hybrid retrieval combining vector similarity search (Qdrant) and keyword search (Postgres full-text search), with configurable fusion strategies.

#### Retrieval Modes

1. **Vector-Only Search:**
   - Input: Query text, top-k (default 10), score threshold (default 0.7)
   - Process:
     1. Generate query embedding via fastembed
     2. Search Qdrant using cosine similarity
     3. Return top-k results above threshold
   - Output: List of (memory_id, score) tuples

2. **Keyword-Only Search:**
   - Input: Query text, top-k (default 10)
   - Process:
     1. Convert query to tsquery (Postgres full-text search syntax)
     2. Search tsvector column on content field
     3. Return top-k results ranked by ts_rank
   - Output: List of (memory_id, rank) tuples

3. **Hybrid Search (Default):**
   - Input: Query text, top-k (default 10), vector_weight (default 0.6), keyword_weight (default 0.4)
   - Process:
     1. Execute vector search → results_v
     2. Execute keyword search → results_k
     3. Apply Reciprocal Rank Fusion (RRF):
        - For each result r: score_r = Σ(weight_i / (k + rank_i)) for all sources i
        - k = 60 (RRF constant)
     4. Re-rank combined results by fused score
     5. Return top-k
   - Output: List of (memory_id, fused_score) tuples
   - **Alternative Fusion**: Weighted average of normalized scores (configurable via metadata flag)

#### Token Budget Awareness

- Input parameter: max_tokens (default 8000, Claude 3.5 Sonnet safe limit)
- Process:
  1. Retrieve results as normal
  2. Estimate token count for each result (content.length / 4 heuristic)
  3. Include results until cumulative tokens approach max_tokens
  4. Return subset + metadata flag if budget exceeded
- Output: Results list + {"token_budget_exceeded": true/false, "excluded_count": N}

#### Acceptance Criteria

- [ ] Vector search returns results ranked by cosine similarity
- [ ] Keyword search returns results ranked by ts_rank
- [ ] Hybrid search combines both with RRF formula
- [ ] Configurable weights affect result ranking (test with 0.9/0.1 vs 0.1/0.9)
- [ ] Token budget truncates results before overflow
- [ ] Empty query returns empty results (no crash)

##### FR-04: Retrieval Validation

#### Description

The system SHALL validate all retrieval results for provenance, temporal validity, contradiction detection, and confidence scoring before returning to the caller.

#### Validation Steps

1. **Provenance Check:**
   - Verify each result UUID exists in Postgres
   - Verify Qdrant metadata matches Postgres record (type, version, created_at)
   - Flag any orphaned records (in Qdrant but not Postgres)
   - **Invariant**: Every returned result traces to a source record

2. **Temporal Validity Filter:**
   - Current time: now = datetime.utcnow()
   - For each result: check temporal_valid_from <= now < temporal_valid_to (or valid_to is None)
   - Exclude expired records
   - Exclude superseded records (superseded_by is not None)
   - **Invariant**: No expired or superseded records in final results

3. **Contradiction Detection:**
   - Identify belief pairs that assert opposite facts (heuristic: cosine similarity > 0.9 but sentiment opposite)
   - Flag as contradictory if both in result set
   - Return warning: {"contradiction_detected": true, "conflicting_ids": [uuid1, uuid2]}
   - **Note**: This is a heuristic, not a logical solver. False positives acceptable.

4. **Confidence Scoring:**
   - For each result, compute confidence score (0.0-1.0):
     - Base score = retrieval score (cosine similarity or fused score)
     - Penalty if version > 1 (older versions less confident): -0.05 * (version - 1)
     - Penalty if temporal_valid_to set (expiring belief): -0.1
     - Penalty if metadata.source = "inferred" vs "explicit": -0.1
     - Clamp to [0.0, 1.0]
   - Sort results by confidence (descending)

5. **Citation Generation:**
   - For each result, produce citation:
     ```json
     {
         "id": "uuid",
         "type": "decision",
         "excerpt": "First 200 chars of content...",
         "created_at": "ISO8601",
         "confidence": 0.87,
         "source_url": "memory://uuid"
     }
     ```
   - Aggregate citations in response metadata

#### Acceptance Criteria

- [ ] Orphaned Qdrant records detected and flagged (integration test seeds orphan)
- [ ] Expired records filtered out (test with temporal_valid_to in past)
- [ ] Superseded records filtered out (test with superseded_by set)
- [ ] Contradiction detection flags conflicting beliefs (manual test case)
- [ ] Confidence scores decrease with version number (test with v1 vs v5 record)
- [ ] Citations include all required fields

##### FR-05: Librarian Gate

#### Description

The system SHALL enforce 100% gate compliance for all durable memory writes through the Librarian role, with zero bypass paths. All write operations (create, update, supersede, archive) MUST be approved before persisting to Postgres.

#### Approval Policies

1. **Auto-Approval (Low-Risk):**
   - Episode creation (historical record, no governance impact)
   - Skill updates (procedural knowledge, low risk)
   - Decision creation if metadata.impact = "low"
   - Configurable via policy file: `.engram/librarian-policy.yaml`

2. **Manual Approval Queue (High-Risk):**
   - Belief creation (new understanding, may contradict existing)
   - Belief supersession (changing established facts)
   - Decision creation if metadata.impact = "high" or "critical"
   - Any operation flagged by validation rules (e.g., duplicate content hash)

#### Approval Flow

1. **Write Request Submitted:**
   - Caller invokes memory.store or equivalent
   - Request serialized and sent to Librarian queue

2. **Policy Evaluation:**
   - Librarian loads policy file
   - Matches request against auto-approval rules
   - If match: approve immediately, proceed to step 4
   - If no match: enqueue for manual review, proceed to step 3

3. **Manual Review (Blocking):**
   - Request sits in approval queue (Postgres table: librarian_queue)
   - Admin reviews via CLI tool: `engram librarian review <request_id>`
   - Admin approves or rejects with reason
   - Approval: proceed to step 4
   - Rejection: return error to caller with reason

4. **Commit to Storage:**
   - Insert into Postgres (transactional)
   - Generate embedding, upsert to Qdrant
   - Log approval event to audit trail

#### Audit Trail

All approval/rejection events logged to `librarian_audit` table:

```python
{
    "id": UUID,
    "request_id": UUID,
    "action": str,                # "approve" | "reject"
    "reason": str,                # Human-readable explanation
    "policy_matched": str | None, # Auto-approval policy name if applicable
    "reviewer": str | None,       # Admin username for manual reviews
    "timestamp": datetime
}
```

#### Rejection Feedback

Rejection response includes:

- Reason (from reviewer or policy rule)
- Suggested fixes (if available)
- Example: "Rejected: Duplicate content detected. Hash ABC123 matches existing record XYZ. Consider updating existing record instead."

#### Enforcement Invariant

Zero bypass paths. The following MUST NOT be possible:

- Direct SQL insert into memory tables
- Direct Qdrant upsert without Postgres record
- API endpoint that skips Librarian (integration test verifies)

#### Acceptance Criteria

- [ ] Auto-approval policy correctly matches episode creation (test with policy file)
- [ ] High-risk belief creation enqueued for manual review
- [ ] Manual review blocks write until approval (test with locked queue)
- [ ] Rejection returns error with reason to caller
- [ ] Audit trail logs all approve/reject events with timestamp
- [ ] Integration test verifies zero bypass paths (attempt direct DB write, expect failure)

##### FR-06: MCP Tools

#### Description

The system SHALL expose memory operations as standard MCP (Model Context Protocol) tools compatible with Claude Code and other MCP clients.

#### Tool Definitions

1. **memory.store**
   - Description: Create a new memory record (goes through Librarian gate)
   - Input Schema:
     ```json
     {
         "type": "decision" | "belief" | "episode" | "skill",
         "content": "string (required)",
         "metadata": {"key": "value", ...},
         "temporal_valid_from": "ISO8601 (optional, defaults to now)",
         "temporal_valid_to": "ISO8601 (optional, defaults to null)"
     }
     ```
   - Output Schema:
     ```json
     {
         "id": "uuid",
         "status": "approved" | "pending" | "rejected",
         "reason": "string (if rejected or pending)"
     }
     ```

2. **memory.retrieve**
   - Description: Hybrid search with validation
   - Input Schema:
     ```json
     {
         "query": "string (required)",
         "top_k": 10,
         "vector_weight": 0.6,
         "keyword_weight": 0.4,
         "max_tokens": 8000,
         "include_archived": false
     }
     ```
   - Output Schema:
     ```json
     {
         "results": [
             {
                 "id": "uuid",
                 "type": "decision",
                 "content": "string",
                 "metadata": {},
                 "confidence": 0.87,
                 "citation": {...}
             },
             ...
         ],
         "metadata": {
             "token_budget_exceeded": false,
             "excluded_count": 0,
             "contradiction_detected": false
         }
     }
     ```

3. **memory.search**
   - Description: Simple search (vector only, keyword only, or combined)
   - Input Schema:
     ```json
     {
         "query": "string (required)",
         "mode": "vector" | "keyword" | "hybrid",
         "top_k": 10
     }
     ```
   - Output Schema: Same as memory.retrieve but without validation metadata

4. **memory.get**
   - Description: Get specific record by ID
   - Input Schema:
     ```json
     {
         "id": "uuid (required)"
     }
     ```
   - Output Schema: Single memory record or error

5. **memory.list**
   - Description: List records by type, time range, or metadata filter
   - Input Schema:
     ```json
     {
         "type": "decision" | "belief" | "episode" | "skill" | null,
         "created_after": "ISO8601 (optional)",
         "created_before": "ISO8601 (optional)",
         "metadata_filter": "JSONPath query (optional)",
         "limit": 100,
         "offset": 0
     }
     ```
   - Output Schema: Paginated list of memory records

6. **memory.validate**
   - Description: Check a set of records for contradictions/staleness
   - Input Schema:
     ```json
     {
         "ids": ["uuid1", "uuid2", ...]
     }
     ```
   - Output Schema:
     ```json
     {
         "valid": true | false,
         "issues": [
             {"type": "contradiction", "ids": ["uuid1", "uuid2"], "reason": "..."},
             {"type": "expired", "id": "uuid3", "reason": "..."}
         ]
     }
     ```

#### MCP Server Configuration

- Server name: "3ngram"
- Transport: stdio (local process) or SSE (HTTP)
- Tools exposed via standard MCP list_tools, call_tool methods
- Error handling: MCP-compliant error responses with code + message

#### Acceptance Criteria

- [ ] All 6 tools listed in MCP list_tools response
- [ ] memory.store submits to Librarian gate (verified by audit log)
- [ ] memory.retrieve performs hybrid search + validation
- [ ] memory.get returns 404 error for non-existent UUID
- [ ] memory.list pagination works correctly (test with limit=10, offset=20)
- [ ] memory.validate detects expired records
- [ ] Claude Code can invoke tools successfully (manual integration test)

##### FR-07: A2A Agent Card

#### Description

The system SHALL serve an A2A v0.3 compliant agent card at `/.well-known/agent-card.json`, declaring capabilities, skills, and connection information.

#### Agent Card Schema

```json
{
    "name": "3ngram",
    "description": "Agentic RAG memory system with kernel-governed writes and validated retrieval",
    "provider": {
        "name": "sh4i-yurei",
        "url": "https://github.com/sh4i-yurei/3ngram"
    },
    "version": "1.0.0",
    "protocolVersion": "0.3.0",
    "capabilities": {
        "streaming": true,
        "pushNotifications": false
    },
    "skills": [
        {
            "name": "research",
            "description": "Execute hybrid retrieval with provenance, temporal validity, and contradiction detection. Returns cited results with confidence scores.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 10},
                    "max_tokens": {"type": "integer", "default": 8000}
                },
                "required": ["query"]
            }
        },
        {
            "name": "remember",
            "description": "Store a new memory record (Decision, Belief, Episode, Skill) with Librarian gate enforcement.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["decision", "belief", "episode", "skill"]},
                    "content": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["type", "content"]
            }
        },
        {
            "name": "recall",
            "description": "Simple search (vector, keyword, or hybrid) without validation overhead. Faster than research for low-stakes queries.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "mode": {"type": "string", "enum": ["vector", "keyword", "hybrid"], "default": "hybrid"},
                    "top_k": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    ],
    "auth": {
        "methods": ["apiKey"],
        "details": {
            "apiKey": {
                "headerName": "Authorization",
                "headerFormat": "Bearer {token}"
            }
        }
    },
    "endpoints": {
        "message": "http://localhost:8000/a2a/v1/message/send",
        "stream": "http://localhost:8000/a2a/v1/message/stream",
        "tasks": "http://localhost:8000/a2a/v1/tasks"
    }
}
```

#### Acceptance Criteria

- [ ] Agent card served at /.well-known/agent-card.json
- [ ] JSON validates against A2A v0.3 agent card schema
- [ ] All three skills declared with correct input schemas
- [ ] Auth details specify Bearer token format
- [ ] Endpoints point to correct local URLs

##### FR-08: A2A Task Lifecycle

#### Description

The system SHALL implement the A2A v0.3 task lifecycle for receiving, processing, and responding to agent messages.

#### Endpoints

1. **POST /a2a/v1/message/send**
   - Description: Receive a task, process it synchronously, return result
   - Input: A2A Message (JSON)
     ```json
     {
         "id": "uuid",
         "role": "user",
         "parts": [
             {
                 "kind": "text",
                 "text": "Research: What decisions have been made about database choice?"
             }
         ],
         "skill": "research"
     }
     ```
   - Process:
     1. Parse message, extract skill and parameters
     2. Route to appropriate handler (research → FR-09)
     3. Execute task, collect results
     4. Construct A2A response message
   - Output: A2A Message (JSON)
     ```json
     {
         "id": "uuid",
         "role": "assistant",
         "status": "completed",
         "parts": [
             {
                 "kind": "text",
                 "text": "Found 2 relevant decisions: ..."
             },
             {
                 "kind": "data",
                 "data": {
                     "results": [...],
                     "metadata": {...}
                 }
             }
         ],
         "artifacts": [
             {
                 "id": "uuid",
                 "name": "research-results.json",
                 "mimeType": "application/json",
                 "content": "base64-encoded-json"
             }
         ]
     }
     ```

2. **POST /a2a/v1/message/stream**
   - Description: Receive a task, stream incremental results via Server-Sent Events (SSE)
   - Input: Same as /message/send
   - Output: SSE stream
     ```text
     event: status
     data: {"status": "working", "message": "Executing hybrid search..."}

     event: part
     data: {"kind": "text", "text": "Found 2 relevant decisions..."}

     event: status
     data: {"status": "completed"}
     ```
   - Close stream on completion or error

3. **GET /a2a/v1/tasks/{task_id}**
   - Description: Check task status by ID
   - Output:
     ```json
     {
         "id": "uuid",
         "status": "working" | "completed" | "failed" | "canceled" | "input_required",
         "created_at": "ISO8601",
         "updated_at": "ISO8601",
         "result": {...} // Only if completed
     }
     ```

4. **POST /a2a/v1/tasks/{task_id}/cancel**
   - Description: Cancel a running task
   - Output:
     ```json
     {
         "id": "uuid",
         "status": "canceled",
         "reason": "User requested cancellation"
     }
     ```

#### Task State Machine

- Initial: **working** (task received, processing started)
- Terminal states: **completed** (success), **failed** (error), **canceled** (user abort)
- Special state: **input_required** (not used in MVP, reserved for future interactive tasks)

#### Message Parts

- **TextPart**: Human-readable text response
  ```json
  {"kind": "text", "text": "string"}
  ```
- **DataPart**: Structured data (JSON object)
  ```json
  {"kind": "data", "data": {...}}
  ```

#### Artifacts

- Deliverable outputs (research reports, memory dumps)
- Base64-encoded content
- MIME type declaration
- Example: research-results.json with all retrieved records + citations

#### Acceptance Criteria

- [ ] POST /message/send processes task and returns completed status
- [ ] POST /message/stream emits SSE events (status, part)
- [ ] GET /tasks/{id} returns correct task state
- [ ] POST /tasks/{id}/cancel transitions task to canceled state
- [ ] Response includes TextPart and DataPart
- [ ] Artifacts correctly base64-encoded and typed

##### FR-09: Researcher Agent Role

#### Description

The system SHALL implement a Researcher agent role that receives natural language research queries, plans retrieval strategies, executes hybrid retrieval, validates results, and assembles cited responses.

#### Workflow

1. **Receive Query:**
   - Input: Natural language query (via MCP tool or A2A message)
   - Example: "What decisions have been made about database schema versioning?"

2. **Plan Retrieval Strategy:**
   - Analyze query to identify:
     - Relevant memory types (decision, belief, episode, skill)
     - Key terms for keyword search
     - Temporal constraints (recent decisions? historical context?)
   - Generate search plan:
     ```json
     {
         "primary_query": "database schema versioning",
         "memory_types": ["decision", "belief"],
         "time_range": {"created_after": "2025-01-01"},
         "top_k": 10
     }
     ```

3. **Execute Hybrid Retrieval (FR-03):**
   - Run hybrid search with planned parameters
   - Retrieve top-k results

4. **Validate Results (FR-04):**
   - Apply provenance check
   - Filter expired/superseded records
   - Detect contradictions
   - Compute confidence scores
   - Generate citations

5. **Refine if Needed:**
   - If results.count < 3 and confidence < 0.7:
     - Relax search parameters (increase top_k, broaden query)
     - Retry retrieval (max 3 attempts)
   - If contradictions detected:
     - Flag for user review
     - Do NOT auto-resolve (requires human judgment)

6. **Assemble Response:**
   - Synthesize natural language summary:
     - "Found 2 relevant decisions regarding database schema versioning:"
     - "1. Decision DEC-001 (2025-01-15, confidence 0.92): Use Alembic for migrations..."
     - "2. Decision DEC-003 (2025-01-20, confidence 0.88): Reject Flyway due to..."
   - Include citations with links to source records
   - Attach structured data (DataPart or artifact) with full results

7. **Return Response:**
   - Via MCP tool: Return JSON with summary + results
   - Via A2A: Send message with TextPart (summary) + DataPart (structured results) + artifact (full JSON)

#### Bounded Retries

- Max 3 retrieval attempts per query
- Retry triggers:
  - Result count < 3
  - Average confidence < 0.7
  - Empty results (no matches)
- Retry strategy:
  - Attempt 1: Original query, hybrid search
  - Attempt 2: Expand top_k to 20, relax score threshold to 0.6
  - Attempt 3: Keyword-only search (fallback)
- After 3 attempts: Return partial results with warning

#### Acceptance Criteria

- [ ] Researcher correctly identifies memory types from query (test: "recent decisions" → filter type=decision, created_after=7 days ago)
- [ ] Hybrid retrieval executed with planned parameters
- [ ] Validation filters expired records (test with seeded expired belief)
- [ ] Retry logic triggers on low confidence (test with intentionally sparse corpus)
- [ ] Max 3 retries enforced (test with query guaranteed to fail)
- [ ] Response includes natural language summary + citations + structured data
- [ ] Contradictions flagged but not auto-resolved (test with seeded conflicting beliefs)

##### FR-10: Docker Compose Local Dev Stack

#### Description

The system SHALL provide a single `docker-compose.yml` file that starts all required services (engram, Postgres, Qdrant) for local development.

#### Services

1. **engram:**
   - Image: Built from local Dockerfile
   - Ports: 8000:8000 (FastAPI), 3000:3000 (MCP stdio bridge, optional)
   - Environment:
     - DATABASE_URL=postgresql://engram:password@postgres:5432/engram
     - QDRANT_URL=`http://qdrant:6333`
     - API_KEY=dev-key-12345
     - EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
   - Depends on: postgres, qdrant
   - Health check: `curl http://localhost:8000/health`

2. **postgres:**
   - Image: postgres:16-alpine
   - Ports: 5432:5432
   - Environment:
     - POSTGRES_USER=engram
     - POSTGRES_PASSWORD=password
     - POSTGRES_DB=engram
   - Volume: postgres-data:/var/lib/postgresql/data
   - Health check: pg_isready -U engram

3. **qdrant:**
   - Image: qdrant/qdrant:v1.8.0
   - Ports: 6333:6333 (HTTP), 6334:6334 (gRPC)
   - Volume: qdrant-data:/qdrant/storage
   - Health check: `curl http://localhost:6333/healthz`

#### Volume Mounts

- postgres-data: Persist Postgres database
- qdrant-data: Persist Qdrant vector index
- .env file: Mounted into engram service for configuration

#### Startup Sequence

1. Start postgres and qdrant in parallel
2. Wait for health checks to pass
3. Start engram service
4. Run database migrations (Alembic) on engram startup
5. Create Qdrant collection if not exists
6. Serve FastAPI app on port 8000

#### Cold Start Time Target

< 2 minutes from `docker-compose up` to all health checks passing

#### Acceptance Criteria

- [ ] `docker-compose up` starts all three services without error
- [ ] Health checks pass within 2 minutes
- [ ] Postgres data persists across container restarts
- [ ] Qdrant data persists across container restarts
- [ ] Example query in README executes successfully (manual test)
- [ ] .env file correctly loaded into engram service (verify via /health endpoint showing config)

#### 5.2 Non-Functional Requirements

##### NFR-01: Retrieval Latency

#### Requirement

Hybrid retrieval (FR-03) SHALL achieve p95 latency < 2 seconds for queries returning 10 results from a corpus of 100k memory records, measured on local Docker Compose stack running on WSL2 (RTX 3070 available).

#### Measurement

- Benchmark script: `scripts/benchmark-retrieval.py`
- Corpus: 100k synthetic memory records (distribution: 40% episodes, 30% skills, 20% decisions, 10% beliefs)
- Query set: 100 diverse queries covering all memory types
- Metric: p95 latency from query submission to validated results returned
- Baseline: Measured on WSL2, 16GB RAM, AMD Ryzen 7 (representative dev hardware)

#### Acceptance Criteria

- [ ] Benchmark script reports p95 < 2s with 100k corpus
- [ ] No query exceeds 5s (p100 threshold)
- [ ] Latency breakdown logged (embedding generation, Qdrant search, Postgres fetch, validation)

##### NFR-02: Memory Durability

#### Requirement

The system SHALL guarantee zero data loss on clean shutdown and restart. All committed memory records MUST be recoverable after container restart.

#### Mechanisms

- Postgres WAL (Write-Ahead Logging) enabled
- Qdrant snapshots configured (auto-snapshot every 1 hour)
- Docker volume persistence for postgres-data and qdrant-data

#### Test Procedure

1. Start stack, create 1000 memory records
2. Verify all records retrievable
3. Shutdown stack (`docker-compose down`)
4. Restart stack (`docker-compose up`)
5. Verify all 1000 records still retrievable with correct content

#### Acceptance Criteria

- [ ] Integration test verifies zero data loss after clean restart
- [ ] Postgres WAL replay completes successfully on startup
- [ ] Qdrant collection recovered from snapshot

##### NFR-03: Librarian Gate 100% Enforcement

#### Requirement

The Librarian gate (FR-05) SHALL enforce 100% approval for all durable memory writes, with zero bypass paths. No write operation SHALL reach Postgres without Librarian approval.

#### Verification

- Integration test attempts direct SQL insert → expect failure (connection rejected or insufficient permissions)
- Integration test attempts API endpoint bypass → expect 403 Forbidden
- Code review: All write paths route through Librarian service
- Static analysis: No raw Postgres insert outside Librarian module

#### Acceptance Criteria

- [ ] Integration test suite includes bypass attempt tests (all fail as expected)
- [ ] Librarian audit log contains 100% of write operations (verified by comparing log count to Postgres row count)
- [ ] Manual code review confirms single write path

##### NFR-04: A2A TCK Compliance

#### Requirement

The system SHALL pass the A2A Test Compatibility Kit (TCK) with zero failures, demonstrating full compliance with A2A v0.3 specification.

#### TCK Coverage

- Agent card schema validation
- Message/send endpoint conformance
- Message/stream SSE format
- Task lifecycle state transitions
- Error response format
- Authentication (API key)

#### Acceptance Criteria

- [ ] TCK test suite runs without errors
- [ ] All TCK assertions pass
- [ ] TCK report generated and committed to docs/compliance/

##### NFR-05: Embedding Performance

#### Requirement

Embedding generation SHALL complete in < 500ms per record using the
configured model. Default: fastembed (CPU). GPU-accelerated models
(SentenceTransformers/CUDA on RTX 3070) available behind the embedding
adapter interface.

#### Configuration

- Default model: fastembed BAAI/bge-small-en-v1.5 (CPU)
- Optional: SentenceTransformers with CUDA (RTX 3070 available)
- Batch size: 1 (no batching in MVP)
- Hardware: WSL2, RTX 3070 GPU available

#### Measurement

- Benchmark: Generate embeddings for 1000 records
- Metric: Average time per record
- Threshold: < 500ms per record (CPU); faster with GPU

#### Acceptance Criteria

- [ ] Benchmark reports < 500ms per record with default model
- [ ] Embedding adapter interface supports swapping models
- [ ] System works with both CPU-only and GPU-accelerated models

##### NFR-06: Single-Process Monolith

#### Requirement

The system SHALL run as a single FastAPI process with no inter-service communication (other than Postgres and Qdrant clients). All components (MCP server, A2A handlers, Librarian, Researcher) SHALL be modules within one process.

#### Architecture

- Single FastAPI app at `src/engram/main.py`
- MCP tools: FastAPI routes + MCP protocol adapter
- A2A endpoints: FastAPI routes
- Librarian: Python module with queue backed by Postgres table
- Researcher: Python module with retrieval logic

#### Acceptance Criteria

- [ ] Only one process running in engram container (verified by `ps aux` in container)
- [ ] No HTTP calls between components (verified by network trace)
- [ ] All communication via in-process function calls

### 6. Constraints and Assumptions

#### 6.1 Technical Constraints

#### C1: WSL2 Environment

- Development and testing restricted to WSL2 (Ubuntu on Windows)
- No native Windows or macOS validation required
- Docker Desktop WSL integration assumed available

#### C2: Python 3.12

- No support for Python < 3.12
- Standard library features from 3.12 may be used (e.g., new type hints)

#### C3: GPU Available (RTX 3070)

- RTX 3070 available for GPU-accelerated embeddings if needed
- Default to fastembed (CPU) for simplicity and portability
- Embedding adapter must support both CPU and GPU backends

#### C4: Solo Developer

- All design decisions made by single person (Mark)
- No multi-stakeholder consensus process
- Fast iteration prioritized over committee design

#### C5: A2A Pre-1.0

- A2A v0.3 is pre-release, subject to breaking changes
- Must tolerate spec evolution (pin version in code, document migration path)

#### C6: Local Development Only

- No production deployment in MVP
- No cloud infrastructure, no Kubernetes, no TLS
- Docker Compose on localhost is the deployment target

#### 6.2 Assumptions

#### A1: Postgres Sufficient

- Single Postgres instance can handle 100k records without sharding
- Full-text search performance acceptable for keyword retrieval
- No need for dedicated search engine (Elasticsearch, Meilisearch) in MVP

#### A2: Qdrant Sufficient

- Single Qdrant instance can handle 100k vectors without clustering
- Cosine similarity search adequate for semantic retrieval
- No need for alternative distance metrics (L2, dot product) in MVP

#### A3: API Key Auth Acceptable

- Single API key for all access sufficient for local dev
- No multi-user auth required
- OAuth2, JWT, session management deferred to post-MVP

#### A4: English-Only Content

- Memory content assumed to be English language
- Embedding model optimized for English
- No i18n, no multi-language retrieval

#### A5: Manual Librarian Review

- Human (Mark) available to review manual approval queue
- No SLA for approval turnaround time
- CLI tool for review is sufficient (no web UI)

#### A6: MCP Clients Exist

- Claude Code or other MCP client available for testing
- MCP protocol stable enough for integration
- stdio transport sufficient (no HTTP SSE transport required initially)

### 7. Risks and Dependencies

#### 7.1 Risks

#### R1: A2A Specification Instability (High Impact, Medium Likelihood)

- **Description**: A2A v0.3 is pre-release. Breaking changes could invalidate implementation.
- **Mitigation**: Pin a2a-sdk version in requirements.txt. Monitor spec repo for changes. Budget 1 week for migration if spec breaks.
- **Contingency**: If A2A becomes non-viable, fall back to MCP-only interface. A2A is nice-to-have, not critical path.

#### R2: Scope Creep (Medium Impact, High Likelihood)

- **Description**: Feature requests (knowledge graph, additional agents, workspace adapters) could delay MVP.
- **Mitigation**: Strict adherence to Non-Goals list. New features require explicit charter amendment and replanning.
- **Contingency**: Time-box MVP to 6 weeks. Cut features if necessary to hit M6 (Release).

#### R3: Embedding Accuracy (Medium Impact, Low Likelihood)

- **Description**: fastembed model may produce low-quality embeddings, harming retrieval recall.
- **Mitigation**: Validate with test corpus (50 known queries → expected results). Benchmark recall@10 metric.
- **Contingency**: Swap embedding model (fastembed supports multiple). Budget 3 days for re-embedding corpus.

#### R4: Librarian Gate Performance Bottleneck (Low Impact, Medium Likelihood)

- **Description**: Manual approval queue could grow faster than Mark can review, blocking writes.
- **Mitigation**: Tune auto-approval policies aggressively. Monitor queue depth. Add CLI bulk-approve command if needed.
- **Contingency**: If queue exceeds 100 items, pause memory writes until cleared. This is acceptable for local dev.

#### R5: Postgres Full-Text Search Insufficient (Low Impact, Low Likelihood)

- **Description**: Postgres ts_rank may not provide adequate keyword search quality.
- **Mitigation**: Benchmark keyword search recall vs. known queries. Compare to vector-only search.
- **Contingency**: If keyword search recall < 50%, disable keyword mode and use vector-only for hybrid retrieval. Defer keyword search to post-MVP.

#### 7.2 Dependencies

#### D1: External Libraries

- **Critical**: FastAPI, Pydantic, SQLAlchemy, psycopg2, qdrant-client, fastembed, a2a-sdk
- **Risk**: Breaking changes in dependencies
- **Mitigation**: Pin all versions in requirements.txt. Use Dependabot for security updates only.

#### D2: Docker Compose

- **Critical**: Docker Desktop WSL integration must work
- **Risk**: Docker Desktop updates break WSL integration
- **Mitigation**: Document tested Docker Desktop version. Avoid auto-update during project.

#### D3: Postgres 16

- **Critical**: Postgres 16 features assumed (e.g., improved full-text search)
- **Risk**: Postgres Docker image changes behavior
- **Mitigation**: Pin to postgres:16-alpine in docker-compose.yml.

#### D4: Qdrant v1.8.0

- **Critical**: Qdrant API stability
- **Risk**: Qdrant updates break client library
- **Mitigation**: Pin to qdrant/qdrant:v1.8.0 in docker-compose.yml. Pin qdrant-client in requirements.txt.

#### D5: Claude Code (for MCP Testing)

- **Non-Critical**: Needed for manual integration testing
- **Risk**: Claude Code unavailable or broken
- **Mitigation**: Test with mock MCP client. Claude Code validation is manual, not automated.

#### D6: policies-and-standards Knowledge Base

- **Critical**: Templates (TPL-PRJ-PRD, TPL-PRJ-TDD, etc.) must be stable
- **Risk**: Template changes mid-project require rework
- **Mitigation**: Lock to policies-and-standards v2.0.0 tag. Resist updates until post-MVP.

### 8. Milestones

The project follows a 6-milestone structure aligned with STD-032 (SDLC_With_AI) for Tier 2 projects.

#### M1: Planning (COMPLETED: 2026-02-12)

- Intake: Problem statement and project proposal ✓
- Charter: Vision, team, scope, success criteria ✓
- PRD: This document ✓
- Duration: 1 week
- Gate: Quint Gate A (all planning artifacts pass FPF validation)

#### M2: Architecture (Target: 2026-02-19)

- Architecture Decision Records (ADRs) for:
  - Monolith vs. microservices (decision: monolith)
  - Postgres + Qdrant vs. alternatives (decision: hybrid Postgres/Qdrant)
  - MCP + A2A protocol integration
  - Librarian gate enforcement mechanism
- Component diagram (engram, Librarian, Researcher, MCP adapter, A2A handler)
- Data flow diagrams (write path, read path, approval flow)
- Duration: 1 week
- Deliverables: docs/architecture/adr-*.md, docs/architecture/components.md
- Gate: Quint Gate A (all ADRs pass FPF L2 validation)

#### M3: Design (Target: 2026-02-26)

- API Design: FastAPI route specs, request/response schemas (OpenAPI 3.1)
- Data Model Design: Postgres schema (Alembic migrations), Qdrant collection config
- Librarian Policy DSL: YAML schema for auto-approval rules
- Researcher Query Planner: Algorithm pseudocode
- Duration: 1 week
- Deliverables: docs/design/api-spec.md, docs/design/data-model.md, docs/design/librarian-policy.md
- Gate: Docs Gate B (all design docs pass STD-001 compliance)

#### M4: Specification (Target: 2026-03-05)

- Technical Specification: Module breakdown, class diagrams, sequence diagrams
- Test Plan: Unit test strategy, integration test cases, benchmark definitions
- Runbook: Startup, health checks, troubleshooting, shutdown
- Duration: 1 week
- Deliverables: docs/specification/tech-spec.md, docs/specification/test-plan.md, docs/operations/runbook.md
- Gate: Docs Gate B (all specs pass STD-001 compliance)

#### M5: Implementation (Target: 2026-03-19)

- Core implementation:
  - Memory CRUD (FR-02): 3 days
  - Hybrid retrieval (FR-03) + validation (FR-04): 4 days
  - Librarian gate (FR-05): 3 days
  - MCP tools (FR-06): 2 days
  - A2A endpoints (FR-07, FR-08): 3 days
  - Researcher agent (FR-09): 2 days
  - Docker Compose stack (FR-10): 1 day
- Testing:
  - Unit tests (concurrent with implementation)
  - Integration tests: 2 days
  - Benchmarks (NFR-01, NFR-05): 1 day
- Duration: 2 weeks
- Deliverables: src/engram/*, tests/*, docker-compose.yml, Dockerfile, requirements.txt
- Gate: Code Gate C (linting, type checking) + Test Gate D (all tests pass)

#### M6: Release (Target: 2026-03-26)

- Documentation finalization: README, CONTRIBUTING, LICENSE
- A2A TCK compliance validation (NFR-04)
- Benchmark report publication (NFR-01, NFR-05, NFR-06)
- Tag v1.0.0, publish to GitHub
- Duration: 1 week
- Deliverables: Tag v1.0.0, docs/compliance/a2a-tck-report.md, docs/benchmarks/retrieval-performance.md
- Gate: Security Gate F (dependency audit) + Config Gate E (docker-compose validated)

### 9. Links

#### Project Documents

- Intake: `/home/mark/3ngram/docs/planning/intake.md` (3NGRAM-INTAKE-001)
- Proposal: `/home/mark/3ngram/docs/planning/proposal.md` (3NGRAM-PROPOSAL-001)
- Charter: `/home/mark/3ngram/docs/planning/charter.md` (3NGRAM-CHARTER-001)
- PRD: This document (3NGRAM-PRD-001)

#### Knowledge Base Standards

- STD-001: Documentation Standard (`/home/mark/policies-and-standards/01_Standards/STD-001_Documentation_Standard.md`)
- STD-008: Testing and Quality Standard (`/home/mark/policies-and-standards/01_Standards/STD-008_Testing_and_Quality_Standard.md`)
- STD-020: Project Management Standard (`/home/mark/policies-and-standards/01_Standards/STD-020_Project_Management_Standard.md`)
- STD-030: CI/CD Pipeline Model (`/home/mark/policies-and-standards/01_Standards/STD-030_CICD_Pipeline_Model.md`)
- STD-031: Git and Branching Workflow (`/home/mark/policies-and-standards/01_Standards/STD-031_Git_and_Branching_Workflow.md`)
- STD-032: SDLC_With_AI (`/home/mark/policies-and-standards/01_Standards/STD-032_SDLC_With_AI.md`)

#### Templates

- TPL-PRJ-PRD: Product Requirements Document Template (`/home/mark/policies-and-standards/06_Projects/Templates/TPL-PRJ-PRD.md`)
- TPL-PRJ-TDD: Technical Design Document Template (`/home/mark/policies-and-standards/06_Projects/Templates/TPL-PRJ-TDD.md`)

#### External References

- MCP Protocol: <https://modelcontextprotocol.io/>
- A2A Specification v0.3: <https://github.com/anthropics/a2a-spec>
- a2a-sdk: <https://github.com/anthropics/a2a-sdk-python>
- FastAPI: <https://fastapi.tiangolo.com/>
- Qdrant: <https://qdrant.tech/>
- fastembed: <https://github.com/qdrant/fastembed>

## Implementation Notes

### Prioritization

High-priority requirements (critical path for MVP):

- FR-01, FR-02: Memory types and CRUD (foundation)
- FR-03, FR-04: Retrieval and validation (core value proposition)
- FR-05: Librarian gate (governance invariant)
- FR-06: MCP tools (primary interface for Claude Code)
- NFR-03: Librarian 100% enforcement (non-negotiable)

Medium-priority requirements (important but not blocking):

- FR-07, FR-08: A2A agent card and task lifecycle (nice-to-have, demonstrates protocol compliance)
- FR-09: Researcher agent (adds intelligence layer, can be basic in MVP)
- NFR-01, NFR-05: Performance benchmarks (validate but don't over-optimize)

Low-priority requirements (can ship without):

- NFR-04: A2A TCK compliance (best-effort, not blocking release)
- FR-10: Docker Compose polish (must work, but UX can be rough)

### Implementation Order

Recommended implementation sequence:

1. **Week 1 (M2: Architecture)**: Settle foundational decisions (monolith, Postgres+Qdrant, Librarian enforcement). Produce ADRs.

2. **Week 2 (M3: Design)**: Design API routes, Postgres schema, Qdrant collection config, Librarian policy YAML. Produce OpenAPI spec.

3. **Week 3 (M4: Specification)**: Write detailed tech spec with class diagrams, sequence diagrams, test plan. Finalize runbook.

4. **Week 4-5 (M5: Implementation, Part 1)**:
   - Day 1-3: Memory CRUD + Postgres schema + Alembic migrations
   - Day 4-7: Hybrid retrieval (vector + keyword + RRF)
   - Day 8-10: Retrieval validation (provenance, temporal, contradiction, confidence)

5. **Week 5-6 (M5: Implementation, Part 2)**:
   - Day 11-13: Librarian gate (queue, policy engine, audit trail)
   - Day 14-15: MCP tools (wrap CRUD + retrieval in MCP protocol)
   - Day 16-18: A2A endpoints (agent card, message/send, message/stream)
   - Day 19-20: Researcher agent (query planner, retry logic, citation assembly)
   - Day 21: Docker Compose stack integration

6. **Week 6 (M5: Testing)**:
   - Day 22-23: Integration tests (Librarian bypass attempts, end-to-end retrieval)
   - Day 24: Benchmarks (retrieval latency, embedding generation)

7. **Week 7 (M6: Release)**:
   - Day 25-26: Documentation (README, runbook, API examples)
   - Day 27: A2A TCK validation
   - Day 28: Tag v1.0.0, publish

### Testing Strategy

#### Unit Tests

- Pydantic model validation (memory types, schemas)
- Retrieval scoring functions (RRF, confidence calculation)
- Librarian policy matching (auto-approval rules)
- Researcher query planning (memory type detection, time range parsing)
- Target: > 80% code coverage (pytest-cov)

#### Integration Tests

- End-to-end memory write → Librarian approval → Postgres insert → Qdrant upsert
- End-to-end retrieval → validation → citation generation
- Librarian bypass attempts (expect failure)
- Docker Compose stack health checks
- Data durability (shutdown → restart → verify)
- Target: All critical paths covered

#### Benchmarks

- Retrieval latency (100k corpus, 100 queries, p95 metric)
- Embedding generation (1000 records, average time per record)
- Memory footprint (RSS under load)
- Output: Markdown report with charts (docs/benchmarks/retrieval-performance.md)

#### Manual Tests

- Claude Code MCP integration (invoke memory.store, memory.retrieve)
- A2A agent discovery (fetch agent card, send message)
- Librarian manual approval (CLI review workflow)

### Deviation Handling

If requirements cannot be met:

1. Document deviation in changelog with rationale
2. Update success criteria to reflect reality
3. If critical requirement (e.g., NFR-03 Librarian enforcement), escalate to project owner (Mark) for charter amendment
4. If non-critical requirement (e.g., NFR-04 A2A TCK), defer to post-MVP and log as known limitation

## Continuous Improvement and Compliance Metrics

### Metrics

#### M1: Requirements Traceability

- Metric: % of functional requirements with corresponding integration tests
- Target: 100% of FR-01 through FR-10
- Measurement: Manual checklist in test plan

#### M2: Gate Enforcement Coverage

- Metric: % of write operations logged in Librarian audit trail
- Target: 100%
- Measurement: Compare audit log row count to Postgres memory table row count (must match)

#### M3: Retrieval Performance

- Metric: p95 latency for hybrid retrieval
- Target: < 2 seconds (NFR-01)
- Measurement: Benchmark script output (automated)

#### M4: Documentation Completeness

- Metric: % of governed documents with all 7 mandatory sections
- Target: 100%
- Measurement: CI/CD Docs Gate B (automated frontmatter check)

### Improvement Process

#### Post-MVP Retrospective (2026-04-01)

- Review all deviations and known limitations
- Collect feedback from Mark (primary user) and Claude Code (AI agent user)
- Identify top 3 pain points for v1.1.0
- Propose requirement amendments for next iteration

#### Quarterly Requirements Review

- Re-validate assumptions (A1-A6) every 3 months
- Check for external changes (A2A spec updates, dependency breaking changes)
- Update risk register (R1-R5) with new threats
- Revise Non-Goals list if scope expands

## Compliance

This document complies with:

- **STD-001 (Documentation Standard)**: All 7 mandatory sections present (Purpose, Scope, Standard, Implementation Notes, Continuous Improvement, Compliance, Changelog)
- **STD-020 (Project Management Standard)**: Milestones aligned with project phases, risks and dependencies documented
- **TPL-PRJ-PRD (PRD Template v0.1.3)**: All required sections included (Background, Goals, Non-Goals, Users, Requirements, Constraints, Risks, Milestones, Links)

Verified by: sh4i-yurei
Date: 2026-02-12

## Changelog

### v0.1.0 (2026-02-12)

- **Added**: Initial PRD creation with complete functional and non-functional requirements
- **Added**: All 10 functional requirements (FR-01 through FR-10) with acceptance criteria
- **Added**: All 6 non-functional requirements (NFR-01 through NFR-06) with measurement criteria
- **Added**: Users and stakeholders analysis (3 primary users, 2 secondary stakeholders)
- **Added**: Constraints and assumptions (6 technical constraints, 6 assumptions)
- **Added**: Risks and dependencies (5 risks with mitigations, 6 dependencies)
- **Added**: 6 milestones (M1-M6) with duration estimates and gate definitions
- **Added**: Background context referencing ai_tech_stack lessons learned
- **Added**: Goals and success criteria with measurable outcomes
- **Added**: Non-goals list (10 items explicitly out of scope)
- **Added**: Links to project documents and knowledge base standards
- **Added**: Implementation notes with prioritization and implementation order
- **Added**: Compliance section confirming adherence to STD-001, STD-020, TPL-PRJ-PRD
- **Status**: Draft pending Quint Gate A validation
