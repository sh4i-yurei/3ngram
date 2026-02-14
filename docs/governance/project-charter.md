---
id: 3NGRAM-CHARTER-001
title: "3ngram: Agentic RAG Memory System — Project Charter"
version: 0.2.1
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-032, STD-054]
tags: [charter, governance, 3ngram, tier-3]
---

# 3ngram: Agentic RAG Memory System — Project Charter

## Purpose

This charter establishes the governance framework, boundaries, and decision-making authority for the 3ngram project. It defines what will be built, why, and how design and implementation will be governed throughout the SDLC. This is the authoritative source of truth for project scope and constraints.

## Scope

This charter governs the 3ngram project from initiation through MVP delivery. It covers:

- Design governance rules and approval authority
- Problem statement and strategic rationale
- MVP goals, explicit non-goals, and deferred features
- Technical and operational constraints
- Risk register and mitigation strategies
- Artifact sequence and approval gates

It does NOT cover:

- Detailed requirements (see PRD)
- Technical architecture decisions (see ADRs)
- Implementation specifications (see module designs)
- Operational procedures (see runbooks)

## Standard

### 1. Charter Details

**Project Name:** 3ngram
**Project ID:** 3NGRAM
**Charter ID:** 3NGRAM-CHARTER-001
**Tier:** 3 (Architecture — full SDLC ceremony per STD-032)
**Owner:** Mark (sh4i-yurei)
**Status:** Active
**Start Date:** 2026-02-12
**Target MVP Date:** TBD (set in roadmap after PRD approval)

**Artifact Lineage:**

- Intake: `docs/planning/project-intake.md`
- Proposal: `docs/planning/project-proposal.md`
- Charter: `docs/governance/project-charter.md` (this document)
- Downstream: PRD → Roadmap → Backlog → Architecture → System Design → Module Designs → Specification

**Governing Standards:**

- STD-001: Documentation Standard (7-section template, versioning, changelog)
- STD-032: SDLC With AI (Tier 3 workflow, design-first gates)
- STD-054: TPL-PRJ-CHARTER (charter template structure)
- STD-020: Design-First Development Standard (no code before approved design)
- STD-031: Git and Branching Workflow (squash-only PRs)

### 2. Design Governance and Approvals

**Decision Authority:**

- **Sole Approver:** Mark (sh4i-yurei) for all design artifacts, specifications, and architectural decisions
- **AI Red-Team:** Required for system design (failure modes, data integrity, security analysis)
- **Quint (FPF):** All architectural decisions tracked via First Principles Framework in `.quint/` directory

**Approval Gates (STD-032 Tier 3):**

1. **PRD Approval:** Requirements finalized, goals/non-goals locked
2. **Architecture Approval:** Options evaluated, ADRs written, system design drafted
3. **Design Approval:** All module designs complete, interfaces specified
4. **Specification Approval:** Implementation-ready specs pass 24-hour cooling period
5. **Implementation Start:** Code may begin after Specification Approval

**Amendment Process:**

- All scope changes, goal additions, or constraint modifications require charter amendment
- Amendments submitted via PR (squash merge per STD-031)
- Changelog entry required with amendment rationale
- Version bump: patch for clarifications, minor for scope changes, major for goal changes

**Cooling Period:**

- 24-hour mandatory delay between technical specification approval and implementation start
- Allows fresh-eyes review, failure mode consideration, and red-team validation
- Clock starts when specification PR is merged

**Code Prohibition:**

- No implementation code (application logic, services, agents) may be written before Specification Approval
- Infrastructure scaffolding (project structure, CI/CD, tooling) is permitted
- Test harnesses and evaluation frameworks are permitted
- Violation constitutes charter breach and triggers architecture review

### 3. Problem Statement

**The Amnesia Problem:**

Large Language Models are fundamentally amnesic. They operate within fixed context windows, possess no durable state between sessions, and hallucinate when retrieval fails or is omitted. Every conversation starts from scratch. Every agent forgets what it learned yesterday.

**The Bolt-On Failure:**

Existing RAG solutions treat memory as a library add-on — vector store queries wrapped in prompt engineering. This approach fails for agentic systems because:

- No semantic structure (everything is "a document")
- No operational reliability (no retry, no validation, no fallback)
- No authorization model (any code can write anything)
- No protocol integration (REST endpoints, not agent primitives)

**The Naive Architecture Lesson:**

The previous `ai_tech_stack` project proved that naive multi-service architectures fail. Grafana + Neo4j + custom Python glue + no governance = unmaintainable garbage. Reference implementation, not production code.

**The Strategic Need:**

We need a **kernel-governed memory OS for AI agents**. Not a library. Not a service. A memory system with:

- **Typed records** (Decision, Belief, Episode, Skill) that carry semantic meaning
- **Agentic retrieval** (planners, validators, retries) not passive queries
- **Authorization gates** (Librarian role) that prevent corruption
- **Protocol-native interfaces** (MCP for tools, A2A for agents)
- **Operational reliability** (versioning, validation, rollback)

This is the foundation every agentic system needs but doesn't have.

### 4. Goals and Outcomes

**MVP Goals (In Scope):**

1. **Typed Memory Records**
   - Eight record types: Decision, Belief, Episode, Skill, Entity, Preference, Reflection, Resource
   - Postgres+pgvector for unified structured and vector storage (ADR-003)
   - Versioning, metadata, provenance tracking

2. **Agentic Retrieval Pipeline**
   - HippoRAG-inspired architecture with adaptive query routing
   - 6-stage pipeline: Plan → Retrieve (hybrid) → Rerank → Validate → Retry → Assemble
   - Planner agent generates retrieval strategy from query
   - Hybrid search (semantic + keyword) via pgvector + Postgres full-text search
   - Reranker scores and filters results
   - Validator checks relevance and quality
   - Retry logic for low-confidence results
   - Assembler formats final response

3. **Librarian Authorization Gate**
   - No durable write to memory without Librarian approval
   - Hybrid architecture: declarative rules (hard constraints) + RL-trained advisor (Phase 3)
   - Prevents corruption, enforces schema, maintains integrity
   - Authorizes record creation, updates, deletions
   - Rejects malformed or unauthorized requests

4. **MCP Tool Integration**
   - MCP server exposing memory operations as tools
   - Claude Code, Desktop, other MCP clients can read/write memory
   - Standard tool interface: `memory_search`, `memory_write`, `memory_recall`

5. **A2A Agent Communication (v0.3)**
   - Agent-to-Agent protocol endpoint for inter-agent requests
   - Pre-1.0 protocol (v0.3) with adapter pattern for stability
   - Enables agents to query memory autonomously

6. **Researcher Agent Role**
   - End-to-end demonstration of retrieval workflow
   - Receives query → plans retrieval → executes pipeline → returns results
   - Validates entire system integration

**Success Criteria:**

- Researcher agent retrieves relevant records with >80% precision
- Librarian gate rejects 100% of malformed write requests
- MCP tools usable from Claude Code without errors
- A2A endpoint responds to agent requests within 2s (p95)
- All records have valid provenance and version metadata

**Deferred Goals (Post-MVP):**

- Workspace Adapter (filesystem integration)
- GitHub Control Plane (issue/PR memory)
- CLI Gateway (terminal interface)
- Skill mining (code → reusable skill extraction)
- Memory hygiene daemon (staleness detection, cleanup)
- Librarian Console UI (admin interface)
- Multi-user support (Phase 5)
- Production Kubernetes deployment (Phase 5)
- Non-English language support
- Multi-tenant support (isolation, quotas, RBAC)

### 5. Non-Goals and Exclusions

**Explicit Non-Goals (Will NOT Build):**

- **Production knowledge graph:** NetworkX prototyping is in Phase 2 scope; Neo4j production migration is deferred to post-Phase 4.
- **Custom model training:** No fine-tuning, no custom model training. Use pre-trained models only.
- **Production-grade deployment:** No Kubernetes, no Terraform, no monitoring stack. Docker Compose only.
- **Multi-user/multi-tenant:** Single user (Mark), single agent context, no RBAC.
- **Web UI/dashboard:** Terminal and MCP only. No React, no web server.
- **Skill execution engine:** Skill records are data. No runtime, no sandboxing.
- **Memory analytics/insights:** No aggregation, no trend detection, no reports.
- **Distributed consensus:** Single-node Postgres. No replication.
- **Third-party integrations:** No Slack, no Notion, no external APIs beyond A2A/MCP.

**Out of Scope (Not Addressed):**

- Migration from existing systems
- Data export/import tooling
- Backup and disaster recovery
- Performance benchmarking beyond basic latency
- Security hardening beyond development environment
- Documentation for end-users (developer docs only)

### 6. Constraints and Assumptions

**Technical Constraints:**

- **Platform:** WSL2 Ubuntu (Linux 6.6.87.2-microsoft-standard-WSL2)
- **Language:** Python 3.12
- **GPU:** RTX 3070 available. Default to fastembed (CPU) for simplicity;
  GPU-accelerated models (SentenceTransformers/CUDA) viable if needed.
- **Database:** Postgres 16+ with pgvector extension (unified storage per ADR-003)
- **Embedding Model:** fastembed (default); GPU models available behind adapter
- **Protocol Versions:** MCP (stable), A2A v0.3 (pre-1.0, breaking changes possible)
- **Deployment:** Docker Compose (no orchestration, no clustering)

**Operational Constraints:**

- **Solo Developer:** Mark is sole contributor, reviewer, approver
- **Time:** No hard deadline, but MVP target is Q1 2026
- **Budget:** $0 infrastructure (local development only)
- **Availability:** Development environment, no SLA, no uptime requirements

**Governance Constraints:**

- **Knowledge Base:** All standards from `policies-and-standards` v2.0.0 apply
- **SDLC:** STD-032 Tier 3 workflow (full ceremony, design-first)
- **Git Workflow:** STD-031 (squash-only PRs, no direct commits to main)
- **CI/CD:** 7-gate model (Gates A-F via GitHub Actions)
- **Quint Tracking:** All architecture decisions logged via FPF in `.quint/`

**Assumptions:**

- A2A protocol v0.3 is stable enough for MVP (adapter pattern mitigates risk)
- fastembed embedding quality is sufficient for retrieval (evaluation metrics will validate)
- Postgres+pgvector can handle single-user load without optimization
- MCP protocol remains stable through MVP development
- WSL2 performance is adequate (no Windows filesystem bottlenecks)

**Dependency Assumptions:**

- Docker Desktop WSL integration is enabled and functional
- Postgres official Docker image is available (pgvector extension included)
- Python 3.12 and pip3 are installed and working
- GitHub Actions runners (ubuntu-latest) support required tooling

### 7. Risks and Mitigations

| Risk ID | Risk | Impact | Probability | Mitigation |
| ------- | ---- | ------ | ----------- | ---------- |
| R-001 | **A2A protocol breaking changes** (pre-1.0 v0.3) | High (rewrites) | Medium | Adapter pattern isolates protocol layer; pin SDK version; monitor spec changes |
| R-002 | **Scope creep from vault notes** (expansive vision) | High (delays) | High | Strict MVP boundary in charter; explicit deferred list; gate approvals |
| R-003 | **Solo developer bottleneck** (no peer review) | Medium (blind spots) | High | AI red-team for system design; Quint decision tracking; KB governance |
| R-004 | **Embedding model accuracy insufficient** | Medium (poor retrieval) | Medium | Adapter interface for model swaps; evaluation metrics; reranker compensates |
| R-005 | **Postgres+pgvector performance degradation** | Low (slow queries) | Low | Single-user load is minimal; HNSW indexing strategy; monitoring hooks |
| R-006 | **WSL2 instability or filesystem issues** | Medium (dev env) | Low | Regular backups; Docker volume isolation; no Windows path dependencies |
| R-007 | **MCP protocol changes** (rare but possible) | Medium (interface rewrites) | Low | MCP is stable; adapter pattern; monitor SDK releases |
| R-008 | **Librarian gate bypass via bug** | High (data corruption) | Low | Unit tests for auth logic; integration tests; red-team validation |
| R-009 | **Retrieval pipeline complexity** (6 stages) | Medium (hard to debug) | Medium | Structured logging; stage-by-stage metrics; test harness |
| R-010 | **Design-first overhead** (impatience) | Low (frustration) | Medium | 24-hour cooling period; Quint tracking shows value; KB compliance |

**Risk Response Plans:**

- **R-001 (A2A instability):** If breaking changes occur, pause implementation, update adapter, re-validate integration tests.
- **R-002 (Scope creep):** Charter amendment required for any goal addition. Reject feature requests not in deferred list.
- **R-003 (Solo bottleneck):** AI red-team pass is mandatory for system design. Quint audit tree tracks decision quality.
- **R-004 (Embedding accuracy):** If retrieval precision <80%, swap embedding model via adapter interface and re-evaluate.
- **R-008 (Librarian bypass):** If bug allows unauthorized write, rollback database, patch gate, add regression test.

### 8. Next Steps

**Immediate (This Week):**

1. **Draft PRD** (`docs/planning/prd.md`) — Functional and non-functional requirements
2. **Draft Roadmap** (`docs/planning/roadmap.md`) — Milestones, dependencies, timeline
3. **Draft Backlog** (`docs/planning/backlog.md`) — Work breakdown, effort estimates

**Design Phase (Next 2 Weeks):**

1. **Architecture Options** — Evaluate storage, embedding, retrieval strategies
2. **ADRs** — Document architectural decisions (`.quint/decisions/`)
3. **System Design** — High-level components, data flows, interfaces
4. **AI Red-Team Pass** — Failure modes, security, data integrity review

**Specification Phase (Week 4+):**

1. **Module Designs** — Per-component detailed design (Librarian, Retriever, MCP, A2A)
2. **Interface Specifications** — API contracts, data schemas, protocol formats
3. **24-Hour Cooling Period** — Mandatory delay before implementation start
4. **Specification Approval** — Gate opens for implementation

**Implementation (After Spec Approval):**

1. Infrastructure scaffolding (Docker Compose, CI/CD, Quint init)
2. Schema and migrations (Postgres+pgvector)
3. Core modules (Librarian gate, retrieval pipeline)
4. Protocol endpoints (MCP server, A2A adapter)
5. Researcher agent (end-to-end integration)
6. Testing and validation (unit, integration, e2e)

### 9. Links

**Project Artifacts:**

- Intake: [docs/planning/project-intake.md](../planning/project-intake.md)
- Proposal: [docs/planning/project-proposal.md](../planning/project-proposal.md)
- Charter: [docs/governance/project-charter.md](project-charter.md) (this document)
- PRD: `docs/planning/prd.md` (next)
- Roadmap: `docs/planning/roadmap.md` (next)

**Knowledge Base:**

- Policies and Standards Repo: <https://github.com/sh4i-yurei/policies-and-standards>
- STD-001: Documentation Standard
- STD-032: SDLC With AI (Tier 3 workflow)
- STD-054: TPL-PRJ-CHARTER (this template)
- STD-020: Design-First Development Standard
- STD-031: Git and Branching Workflow

**Decision Tracking:**

- Quint (FPF): `.quint/` directory
- ADRs: `.quint/decisions/` (architecture decisions)
- Audit Tree: `quint-code audit-tree <holon-id>`

## Implementation Notes

**Charter Lifecycle:**

- Charter is approved before PRD development begins
- Charter locks project scope, goals, and governance rules
- Amendments require PR + changelog + version bump
- Major changes (goal additions, scope expansions) trigger architecture review

**Governance Enforcement:**

- CI/CD Gate A (Quint): Verifies all ADRs are logged
- CI/CD Gate B (Docs): Validates charter frontmatter and links
- Pre-commit hooks: Lint markdown, check links, validate YAML
- Manual review: Sole approver (Mark) reviews all PRs

**Design Artifacts Sequence:**

Charter → PRD → Roadmap → Backlog → Architecture → System Design → Module Designs → Specification → Implementation

Each artifact requires approval before the next begins. No skipping steps. No parallel development of downstream artifacts until upstream is approved.

**Quint Integration:**

- Initialize FPF: `/q0-init` in project root
- Record bounded context: Architecture domain, memory systems
- Propose hypotheses: `/q1-hypothesize` for each architectural option
- Verify: `/q2-verify` with feasibility checks
- Validate: `/q3-validate` with prototypes or research
- Audit: `/q4-audit` for R_eff scores
- Decide: `/q5-decide` with winner + rejected alternatives

**AI Red-Team Requirement:**

System design must undergo AI red-team analysis covering:

- Failure modes (what breaks, when, how)
- Data integrity (corruption vectors, validation gaps)
- Security (authorization bypass, injection, leakage)
- Operational risks (deadlock, resource exhaustion, cascading failures)

Red-team report is appended to system design document and reviewed before approval.

## Continuous Improvement and Compliance Metrics

**Charter Compliance Metrics:**

- **Scope Adherence:** 0 unauthorized features in implementation (target: 0)
- **Gate Compliance:** 100% of design artifacts approved before downstream work (target: 100%)
- **Amendment Frequency:** <3 charter amendments during MVP (target: <3)
- **Cooling Period Violations:** 0 implementations started before 24-hour delay (target: 0)

**Design Quality Metrics:**

- **ADR Coverage:** 100% of architectural decisions logged in Quint (target: 100%)
- **Red-Team Completion:** 1 red-team pass on system design (target: 1, required)
- **Specification Completeness:** All modules have approved designs before code (target: 100%)

**Process Metrics:**

- **Artifact Sequence Breaks:** 0 skipped steps in SDLC (target: 0)
- **PR Squash Compliance:** 100% of merges use squash (target: 100%, enforced by GitHub)
- **Changelog Coverage:** 100% of amendments have changelog entries (target: 100%)

**Continuous Improvement:**

- Quarterly review of charter effectiveness
- Retrospective after MVP delivery (lessons learned)
- Template improvements fed back to policies-and-standards repo
- Quint audit tree used to evaluate decision quality

## Compliance

**Mandatory Standards (MUST):**

- STD-001: Documentation Standard — 7 sections, frontmatter, changelog
- STD-032: SDLC With AI — Tier 3 workflow, design-first gates
- STD-054: TPL-PRJ-CHARTER — Charter template structure
- STD-020: Design-First Development — No code before approved design
- STD-031: Git and Branching Workflow — Squash-only PRs

**Recommended Standards (SHOULD):**

- STD-030: CI/CD Pipeline Model — 7-gate model (Gates A-F)
- STD-008: Testing and Quality Standard — Unit, integration, e2e tests
- STD-056: KB Integration Standard — Pointer artifacts, retrieval

**Enforcement:**

- Pre-commit hooks: Lint, link-check, frontmatter validation
- CI/CD gates: Quint, docs, code, tests, config, security
- Manual review: Sole approver (Mark) on all PRs
- Quint audits: R_eff scores for architectural decisions

**Deviations:**

None permitted during MVP. Charter governs scope and governance. Deviations require charter amendment via PR.

## Changelog

### [0.2.1] - 2026-02-13

**Changed:**

- Replaced all Qdrant references with Postgres+pgvector per ADR-003
  (unified storage decision). Affected: MVP goals, non-goals, technical
  constraints, assumptions, dependency assumptions, risks, implementation
  steps, and changelog v0.1.0 entry.

**References:**

- ADR-003: docs/architecture/adr/ADR-003-storage-backend.md

### [0.2.0] - 2026-02-13

**Changed:**

- Expanded typed memory from 4 to 8 record types (added Entity, Preference, Reflection, Resource)
- Promoted knowledge graph from non-goal to Phase 2 scope (NetworkX prototyping)
- Expanded agent roles from 2 to full autonomous component architecture
- Added hybrid Librarian Gate architecture (declarative rules + RL advisor)
- Updated deferred goals list to reflect v2 phasing

**References:**

- System Design: docs/design/system-design.md (3NGRAM-SD-001)
- ADRs 007-012: v2 architectural decisions

### [0.1.0] - 2026-02-12

**Added:**

- Initial charter draft
- Design governance and approval rules (sole approver, AI red-team, 24-hour cooling period)
- Problem statement (LLM amnesia, bolt-on RAG failure, naive architecture lesson)
- MVP goals (6 core capabilities: typed records, agentic retrieval, Librarian gate, MCP, A2A, Researcher agent)
- Explicit non-goals and deferred features (knowledge graph, GPU, production, multi-tenant)
- Constraints (WSL2, Python 3.12, Postgres+pgvector, A2A v0.3, solo developer)
- Risk register (10 risks with mitigations)
- Next steps (PRD → Roadmap → Backlog → Architecture → Design → Spec → Implementation)
- Implementation notes (Quint integration, red-team requirement)
- Compliance metrics (scope adherence, gate compliance, ADR coverage)

**References:**

- Intake: docs/planning/project-intake.md
- Proposal: docs/planning/project-proposal.md
- Template: STD-054 (TPL-PRJ-CHARTER v0.2.6)
- SDLC: STD-032 (Tier 3 workflow)
