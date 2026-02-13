---
id: 3NGRAM-RISK-001
title: "3ngram Risk Register"
version: 0.1.0
category: project
status: draft
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-003, STD-007]
tags: [risk, register, governance, 3ngram]
---

# 3ngram Risk Register

# Purpose

Document and track project risks for 3ngram across security,
reliability, delivery, and compliance categories. This register is
required for Tier 3 projects per STD-032 and must be reviewed at each
milestone and before release approval.

# Scope

Covers risks identified during M3 (system design phase) from the system
design artifact, ADRs 001-012, the AI red-team review, and delivery
planning. Risks apply across all five implementation phases.

# Standard

## Risk register

### Security risks

- Risk ID: RSK-001
  - Description: PII screening limitations — Phase 1 regex-based PII
    detection is best-effort and will miss contextual PII embedded in
    narrative text (e.g., names in episode content). Records with
    undetected PII could be stored at incorrect access levels.
  - Category: security
  - Likelihood: medium
  - Impact: medium
  - Mitigation plan: Quarantine-by-default (flagged records get
    `sensitive` access level). Periodic batch rescan. PII propagation
    tracking through consolidation chains. Upgrade to NER-based
    detector in Phase 2+. See system design § PII Screening Model.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-002
  - Description: Librarian Gate bypass via implementation bugs — any
    code path that writes to storage without Gate approval is a
    critical vulnerability. The v0.1.1 design routes all writes
    (external and internal) through the Gate, but untested code paths
    remain a risk during implementation.
  - Category: security
  - Likelihood: low
  - Impact: high
  - Mitigation plan: Integration tests covering all write paths
    (external, consolidation, self-healing). Static analysis to detect
    raw SQL inserts outside Gate. Database-level permissions restricting
    direct table writes. Red-team review of implementation code.
  - Owner: sh4i-yurei
  - Status: monitoring
  - Review date: 2026-05-13

- Risk ID: RSK-003
  - Description: Token theft or replay for agent identity — token-based
    persistent identity allows replay attacks if tokens are intercepted.
    No token expiration mechanism is defined for Phase 1.
  - Category: security
  - Likelihood: medium
  - Impact: high
  - Mitigation plan: Token rotation support. Revocation via CLI.
    Connection auditing. Phase 2: add token expiration and
    challenge-response verification.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-004
  - Description: Prompt injection via stored memory content —
    adversarial content in memory records could manipulate downstream
    agents during retrieval. Content sanitization in the Gate is
    partial (Layer 1 schema validation only).
  - Category: security
  - Likelihood: medium
  - Impact: high
  - Mitigation plan: Content sanitization in Gate Layer 1.
    Type-specific validation rules per memory type. Agent trust scoping
    limits what untrusted agents can write. Phase 2: content analysis
    for injection patterns.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-005
  - Description: Data exfiltration via A2A protocol — malicious agents
    could exploit A2A endpoints to query sensitive records across trust
    boundaries. Rate limiting and access control are mitigations but
    may be insufficient against sophisticated attacks.
  - Category: security
  - Likelihood: low
  - Impact: high
  - Mitigation plan: Access control levels enforced on all read paths.
    Agent trust tiers restrict query scope. Rate limiting per agent.
    A2A is Phase 4; threat model will be updated before activation.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-08-13

### Reliability risks

- Risk ID: RSK-006
  - Description: NetworkX in-memory graph is a single point of failure
    — Phase 2 knowledge graph runs entirely in process memory.
    Process crash loses the graph until rebuild from PostgreSQL. The
    300-second refresh window means up to 5 minutes of graph
    inconsistency. Memory usage could exceed estimates for large
    edge counts.
  - Category: reliability
  - Likelihood: high
  - Impact: medium
  - Mitigation plan: Incremental graph updates instead of full periodic
    rebuilds. Memory budget with circuit breaker. Read-write lock for
    atomic graph swap during rebuild. Degraded-mode retrieval that
    works without the graph. See ADR-009.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-007
  - Description: No backup or recovery strategy — no documented backup
    schedule, retention policy, or recovery procedure for PostgreSQL
    data. Single-node deployment with no replication. WSL2 filesystem
    layer adds durability risk.
  - Category: reliability
  - Likelihood: medium
  - Impact: high
  - Mitigation plan: Define backup strategy before Phase 1
    implementation: automated `pg_dump` schedule, WAL archiving for
    point-in-time recovery, backup verification in health checks.
    Store backups outside WSL2 filesystem.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-008
  - Description: Embedding model migration consistency gap — swapping
    embedding models requires re-embedding all existing records. During
    the migration window, mixed-model vectors produce meaningless
    cosine similarity scores. Re-embedding 100K records could take up
    to 1 hour on CPU.
  - Category: reliability
  - Likelihood: medium
  - Impact: medium
  - Mitigation plan: Store `model_version` per embedding (ADR-007).
    During migration, query only records matching current model version,
    falling back to BM25 for un-migrated records. Define migration
    state machine with rollback path. See ADR-007.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-009
  - Description: Self-RAG LLM dependency in retrieval read path —
    Phase 2 retrieval validation stage depends on an LLM call for
    relevance reflection. LLM latency (500ms-2s) or unavailability
    directly impacts retrieval SLO. Model source (local vs API) is
    unspecified.
  - Category: reliability
  - Likelihood: medium
  - Impact: medium
  - Mitigation plan: Specify model in module design (prefer local
    cross-encoder reranker). Make Self-RAG optional and degradable —
    retrieval must work without it. Allocate latency budget per
    pipeline stage. Circuit breaker on Self-RAG with fallback to
    unvalidated results.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-010
  - Description: Event bus has no durability guarantee — asyncio
    in-process event bus has no persistence. If the process crashes
    after a PostgreSQL commit but before event consumption, downstream
    subscribers miss the event permanently. No replay mechanism exists.
  - Category: reliability
  - Likelihood: medium
  - Impact: medium
  - Mitigation plan: Implement PostgreSQL-backed outbox pattern
    (LISTEN/NOTIFY or polling an outbox table) for Phase 1. Events
    are only deleted after successful consumption. Provides durability
    without requiring Kafka.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-011
  - Description: Concurrent write race conditions — optimistic
    concurrency control (v0.1.1) mitigates the critical scenario, but
    implementation bugs in `expected_version` checks or
    `SELECT ... FOR UPDATE` usage could still cause version chain
    corruption under concurrent load.
  - Category: reliability
  - Likelihood: low
  - Impact: high
  - Mitigation plan: Comprehensive integration tests for concurrent
    write scenarios. Property-based testing for version chain
    integrity. Audit trail verification (Gate completeness SLO = 100%).
  - Owner: sh4i-yurei
  - Status: monitoring
  - Review date: 2026-05-13

- Risk ID: RSK-012
  - Description: pgvector scaling ceiling — pgvector performance
    degrades above approximately 500K records. No automated migration
    path to a dedicated vector database exists. ADR-003 estimates the
    ceiling but it has not been verified empirically.
  - Category: reliability
  - Likelihood: low
  - Impact: medium
  - Mitigation plan: Adapter interface (ADR-007) enables future Qdrant
    migration. Monitor vector search latency as corpus grows.
    Benchmark at 100K, 250K, 500K record counts. Trigger migration
    planning if p95 latency exceeds 200ms.
  - Owner: sh4i-yurei
  - Status: monitoring
  - Review date: 2026-08-13

- Risk ID: RSK-013
  - Description: Decay score has no recovery mechanism — temporal decay
    is monotonically decreasing. Combined with consolidation (which
    marks decayed records as `consolidated`), important but
    infrequently accessed memories could decay permanently. No `pinned`
    flag or per-type decay rates are defined.
  - Category: reliability
  - Likelihood: medium
  - Impact: medium
  - Mitigation plan: Add `pinned` flag for durable knowledge
    (decisions, policies). Differentiate access types (retrieval resets
    decay, consolidation does not). Implement per-type decay rates.
    Add decay floor so records never decay below a minimum threshold.
    Address in Memory module design.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

### Delivery risks

- Risk ID: RSK-014
  - Description: Solo developer — bus factor of 1. All design,
    implementation, review, and operations depend on a single person.
    Extended unavailability halts the project entirely.
  - Category: delivery
  - Likelihood: high
  - Impact: high
  - Mitigation plan: AI red-team review compensates for single-reviewer
    blind spots. Governance framework (KB standards, design-first
    model) ensures decisions are documented and recoverable. All design
    artifacts are self-contained per PLANS.md requirements.
  - Owner: sh4i-yurei
  - Status: accepted
  - Review date: 2026-05-13

- Risk ID: RSK-015
  - Description: Tier 3 timeline pressure — 5-phase implementation
    plan spans 12+ months. Scope creep, estimation errors, or
    competing priorities could delay delivery significantly. Phase
    boundaries may shift as implementation reveals complexity.
  - Category: delivery
  - Likelihood: high
  - Impact: medium
  - Mitigation plan: Each phase is independently valuable (no big-bang
    delivery). Phased delivery allows scope adjustment between phases.
    Quarterly roadmap review. Track cycle time per milestone.
  - Owner: sh4i-yurei
  - Status: monitoring
  - Review date: 2026-05-13

- Risk ID: RSK-016
  - Description: A2A v0.3 pre-1.0 instability — A2A specification may
    introduce breaking changes before reaching 1.0. Adapter pattern
    mitigates but significant rewrites may be needed.
  - Category: delivery
  - Likelihood: medium
  - Impact: low
  - Mitigation plan: Adapter pattern isolates A2A protocol details
    (ADR-002). A2A implementation deferred to Phase 4. Pin spec version
    when implementation begins. Monitor A2A releases for breaking
    changes.
  - Owner: sh4i-yurei
  - Status: monitoring
  - Review date: 2026-08-13

- Risk ID: RSK-017
  - Description: Consolidation quality unmeasured until Phase 3 — CLS
    dual-path consolidation engine operates without quality metrics
    until Phase 3 RL feedback infrastructure is deployed. Poor
    consolidation could silently degrade memory store quality for
    months.
  - Category: delivery
  - Likelihood: medium
  - Impact: medium
  - Mitigation plan: Implement post-consolidation validation in
    Phase 2: compare consolidated record against sources using
    embedding similarity. Flag consolidations below 0.85 similarity
    threshold for review. See SLI/SLO § consolidation retention target.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

### Compliance risks

- Risk ID: RSK-018
  - Description: Design artifact synchronization — as scope evolves,
    system design, module designs, ADRs, and specs may diverge.
    Unsynchronized artifacts lead to implementation contradictions and
    compliance gaps.
  - Category: compliance
  - Likelihood: medium
  - Impact: medium
  - Mitigation plan: Design amendments must increment version metadata
    and update changelogs (STD-020 §7.4). Cross-reference checks in
    design review (STD-024). Pre-commit hooks enforce documentation
    structure. Version all design artifacts with frontmatter.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-05-13

- Risk ID: RSK-019
  - Description: KB standards may update — policies-and-standards repo
    updates could require design amendments, adding rework to the
    project timeline. Currently pinned to v2.0.0 but upstream changes
    must be tracked.
  - Category: compliance
  - Likelihood: low
  - Impact: low
  - Mitigation plan: Pin KB version in `.kb/ai-context.yaml`. Review
    upstream changes quarterly. Only adopt breaking changes between
    milestones. Document deviations as exceptions per STD-032
    escalation process.
  - Owner: sh4i-yurei
  - Status: monitoring
  - Review date: 2026-08-13

- Risk ID: RSK-020
  - Description: RL training data accumulation assumption — Phase 3 RL
    components (Gate Advisor, Memory Distiller) assume sufficient
    training data accumulated from Phases 1-2. If interaction volume is
    too low, RL training may produce models worse than the heuristic
    baselines they replace.
  - Category: compliance
  - Likelihood: medium
  - Impact: medium
  - Mitigation plan: Collect feedback data from Phase 1 onward (log
    all retrievals, results, implicit feedback). Define minimum data
    volume threshold before activating RL training. Heuristic baselines
    remain the fallback — RL must demonstrably outperform them before
    deployment. See system design assumption A8.
  - Owner: sh4i-yurei
  - Status: open
  - Review date: 2026-08-13

## Risk acceptance

- **RSK-014** (Solo developer): Accepted. This is a solo practice
  project by design. The governance framework (KB standards,
  design-first model, AI red-team review, Quint tracking) compensates
  for the lack of human peer review. Approval: sh4i-yurei, 2026-02-13.

# Implementation Notes

- Review this register at each milestone (M3 completion, M4
  specification, Phase 1 implementation start, each phase completion)
  and before any release approval.
- Link risks to issues, ADRs, or specs where applicable. Each risk
  above cites its source (system design section, ADR, or red-team
  finding ID).
- New risks discovered during module design, specification, or
  implementation should be added immediately, not deferred to the next
  scheduled review.
- Risks with `monitoring` status have mitigations in place but require
  ongoing observation.

# Continuous Improvement and Compliance Metrics

- Track risk closure rate and recurrence across milestones.
- Track count of risks by status (open/monitoring/mitigated/accepted)
  at each review.
- Review cadence: quarterly or at each milestone, whichever comes
  first.
- Risks that remain `open` for two consecutive review cycles should be
  escalated to `high` priority and require explicit mitigation timeline.

# Compliance

This document complies with:

- **STD-001** (Documentation Standard): All mandatory sections present.
- **STD-003** (Risk Management): Risk register format with required
  fields (ID, description, category, likelihood, impact, mitigation,
  owner, status, review date).
- **STD-007** (Security and Threat Modeling): Security risks linked to
  threat considerations in system design.
- **STD-032** (SDLC With AI, Tier 3): Risk register is a required
  artifact for Tier 3 projects.

# Changelog

## 0.1.0 — 2026-02-13

**Added:**

- Initial risk register with 20 risks across 4 categories
- Security (5): PII screening, Gate bypass, token theft, prompt
  injection, A2A exfiltration
- Reliability (8): NetworkX SPOF, no backups, embedding migration,
  Self-RAG dependency, event bus durability, concurrent writes,
  pgvector ceiling, decay score
- Delivery (4): solo developer, timeline pressure, A2A instability,
  consolidation quality
- Compliance (3): artifact sync, KB updates, RL data assumption
- Risk acceptance for RSK-014 (solo developer)

**Status**: Draft — pending review
