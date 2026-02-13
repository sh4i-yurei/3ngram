---
id: 3NGRAM-ADR-012
title: "ADR-012: Hybrid Librarian Gate architecture"
version: 0.1.0
category: architecture
status: accepted
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-047]
tags: [adr, architecture, librarian, rl, gate, 3ngram]
---

## 1. Purpose

Record the decision to implement a hybrid Librarian Gate architecture that combines hard rule-based constraints with RL-trained soft decisions, ensuring safety invariants are always enforced while allowing the system to learn user-specific storage patterns over time.

## 2. Scope

This decision applies to the Librarian Gate component of 3ngram -- the write-path gatekeeper that validates, classifies, and routes all memory write operations. It governs the two-layer architecture, the boundary between hard constraints and soft decisions, and the RL training approach.

## 3. Standard

### 3.1 Metadata

| Field | Value |
| --- | --- |
| Decision ID | 3NGRAM-ADR-012 |
| Status | Accepted |
| Date | 2026-02-13 |
| Deciders | sh4i-yurei |

### 3.2 Context

The Librarian Gate is the quality gatekeeper for all memory writes. It must enforce safety invariants (schema validation, access control, PII detection) while also making nuanced storage decisions (ADD vs UPDATE vs NOOP, importance scoring, consolidation routing).

Pure rule-based systems cannot learn user-specific patterns -- what is important to one user may be noise to another. Pure RL systems cannot guarantee safety invariants -- a learned model might bypass PII detection if the reward signal inadvertently encourages it.

The hybrid approach separates concerns: hard constraints are rule-based and never overridden, while soft decisions start as heuristics and are gradually replaced by learned models as interaction data accumulates.

### 3.3 Decision Drivers

- **Safety guarantees** -- PII detection, schema validation, and access control must never be bypassed
- **Personalization** -- storage decisions should adapt to user-specific patterns over time
- **Phased delivery** -- Phase 1 must work without RL; Phase 3 adds learned decisions
- **Auditability** -- every gate decision must be explainable (why was a memory accepted/rejected/modified)
- **Training feasibility** -- RL requires sufficient interaction data; the system must collect this data from Phase 1

### 3.4 Options

#### Option A: Hybrid gate (hard constraints + RL soft decisions)

Two layers: Layer 1 (hard constraints) is always rule-based and runs first. Layer 2 (soft decisions) starts as heuristic rules in Phase 1 and transitions to RL-trained models in Phase 3. Hard constraints cannot be overridden by RL. RL trains on outcome-driven rewards.

#### Option B: Pure rule-based gate

All decisions are rule-based. Simple and predictable but cannot learn user-specific patterns. Storage quality plateaus.

#### Option C: Pure RL gate

All decisions are learned. Maximum adaptability but no safety guarantees. Unacceptable for PII detection and access control.

#### Option D: LLM-based gate (use an LLM for every write decision)

High quality decisions but adds latency and cost to every write operation. External dependency contradicts local-first design. Not feasible for high-throughput scenarios.

### 3.5 Decision

**Option A -- Hybrid gate with hard constraints and RL soft decisions.**

#### Layer 1: Hard constraints (rule-based, never overridden by RL)

- Schema validation -- memory records must conform to the type schema
- Access control enforcement -- write permissions checked against caller identity
- PII detection -- flag or reject memories containing personally identifiable information
- Rate limiting -- prevent memory flooding from a single source
- Classification enforcement -- memory type must be valid and consistent with content

Layer 1 runs first on every write. If Layer 1 rejects, the write is denied regardless of Layer 2 output. Layer 1 rules are defined declaratively in configuration and versioned.

#### Layer 2: Soft decisions (heuristic in Phase 1, RL-trained in Phase 3)

- ADD vs UPDATE vs NOOP -- should this memory be stored as new, merged with existing, or discarded?
- Conflict classification -- is this memory consistent with, contradicting, or superseding existing memories?
- Consolidation routing -- should this memory be flagged for immediate consolidation?
- Confidence calibration -- what confidence score should be assigned to this memory?
- Importance scoring -- how important is this memory relative to others?

**RL training approach (Phase 3):**

1. Phase 1-2: Heuristic rules for Layer 2 decisions. All decisions are logged with full context.
2. Phase 3: Train RL model (GRPO/PPO) on collected interaction data.
3. Reward signal: memories that get retrieved and used successfully by callers reinforce the storage decisions that admitted them. Memories that are never retrieved penalize the decisions that stored them.
4. Gradual transition: RL model predictions are compared against heuristic decisions during a shadow period before RL takes over.
5. Hard constraints (Layer 1) remain rule-based permanently.

**Decision logging:** Every gate decision (Layer 1 and Layer 2) is logged with:

- Input memory record
- Layer 1 check results (pass/fail per check)
- Layer 2 decision and rationale
- Decision source (rule or RL model version)
- Outcome (later: was the memory retrieved? was it useful?)

### 3.6 Consequences

**Positive:**

- Safety invariants are guaranteed -- PII detection and access control cannot be bypassed by RL
- Storage quality improves over time as RL learns user-specific patterns
- Full auditability -- every decision is logged with its rationale and source
- Phased delivery -- Phase 1 works with rules only; RL is additive, not required
- Interaction data collection from Phase 1 provides the training corpus for Phase 3

**Negative:**

- Two-layer architecture adds complexity to the write path; mitigated by clean separation (Layer 1 is a simple pipeline of checks)
- RL training requires sufficient interaction data (estimated minimum: 10k write decisions with outcome feedback); mitigated by Phase 1-2 data collection period
- Shadow period for RL transition adds engineering effort; mitigated by the fact that shadow comparison is a well-understood deployment pattern

**Follow-up actions:**

- Implement Layer 1 hard constraints for Phase 1
- Implement Layer 2 heuristic rules for Phase 1
- Design the decision logging schema
- Define the RL reward function specification for Phase 3
- Integrate conflict classification with knowledge graph edges (ADR-009)

### 3.7 Notes and Links

- Expanded agents: [ADR-008 Expanded Agent Architecture](./ADR-008-expanded-agent-architecture.md)
- Knowledge graph: [ADR-009 Knowledge Graph Phase 2](./ADR-009-knowledge-graph-phase2.md)
- CLS consolidation: [ADR-010 CLS Consolidation](./ADR-010-cls-consolidation.md)
- Retrieval pipeline: [ADR-011 HippoRAG Retrieval](./ADR-011-hipporag-retrieval.md)

## 4. Implementation Notes

- The Librarian Gate is implemented as an agent component (ADR-008) in `src/engram/agents/librarian.py`
- Layer 1 checks are defined as a list of `GateCheck` Protocol implementations in `src/engram/librarian/constraints/`
- Layer 2 decisions are implemented as `GateAdvisor` Protocol implementations in `src/engram/librarian/advisors/`
- The `HeuristicAdvisor` (Phase 1) and `RLAdvisor` (Phase 3) both implement the `GateAdvisor` Protocol
- Decision logs are stored in a `gate_decisions` table with JSONB columns for context and rationale
- PII detection in Phase 1 uses regex-based patterns; Phase 2 may upgrade to a model-based detector
- Rate limiting uses a token bucket algorithm per caller identity
- Configuration for Layer 1 rules lives in `config/gate_constraints.yaml`

## 5. Continuous Improvement and Compliance Metrics

| Metric | Target | Frequency |
| --- | --- | --- |
| Layer 1 false positive rate (valid writes rejected) | < 1% | Weekly review |
| Layer 1 false negative rate (invalid writes accepted) | 0% for PII, 0% for access control | Continuous monitoring |
| Layer 2 decision accuracy (heuristic) | > 80% agreement with expert judgment | Monthly evaluation |
| Decision log completeness | 100% of writes logged | Continuous monitoring |

Review this ADR when any of these signals appear:

- Layer 1 false positive rate exceeds 5% (rules are too aggressive)
- RL training data reaches the 10k decision threshold (Phase 3 readiness)
- PII detection patterns miss a new PII type (upgrade to model-based detection)
- Write latency exceeds SLO targets due to gate processing time

## 6. Compliance

This ADR complies with:

- STD-001 (Documentation Standard) -- seven mandatory sections present
- STD-047 (Architecture Decision Workflow) -- ADR format with metadata, drivers, and follow-up actions

## 7. Changelog

- 0.1.0 -- Initial decision: accepted hybrid Librarian Gate with rule-based hard constraints and RL-trained soft decisions
