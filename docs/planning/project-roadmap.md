---
id: 3NGRAM-ROADMAP-001
title: "3ngram: Agentic RAG Memory System — Project Roadmap"
version: 0.1.0
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-003, STD-032]
tags: [roadmap, planning, 3ngram, milestones]
---

# Purpose

Define the phased delivery plan for 3ngram, mapping milestones to
work sessions and tracking progress toward v0.1.0 (MVP).

# Scope

Covers the full Tier 3 lifecycle from planning through MVP release.
Post-MVP phases (knowledge graph, additional agent roles, workspace
adapters) are acknowledged but not scheduled.

# Standard

## Roadmap snapshot

| Field | Value |
| ------- | ------- |
| Project | 3ngram |
| Owner | Mark (sh4i-yurei) |
| Tier | 3 (Architecture) |
| Current phase | Planning |
| Target horizon | 6 months to MVP |

## Goals and outcomes

**Primary goal:** A running local memory system where Claude Code can
store/retrieve memories via MCP and external agents can delegate tasks
via A2A.

**Outcomes:**

1. Typed, versioned memory with Librarian-gated durability.
2. Hybrid retrieval with validation and citation.
3. MCP tool interface for Claude Code integration.
4. A2A endpoint for agent-to-agent interoperability.
5. Full governance trail (design artifacts, ADRs, Quint decisions).

## Milestones and releases

### M1: Planning Complete

**Target:** Session 2
**Status:** Complete

| Deliverable | Status |
| ------------- | -------- |
| Project Intake (3NGRAM-INTAKE-001) | Done |
| Project Proposal (3NGRAM-PROP-001) | Done |
| Project Charter (3NGRAM-CHARTER-001) | Done |
| PRD (3NGRAM-PRD-001) | Done |
| Project Roadmap (this document) | Done |
| Backlog and Milestones | Done |

**Exit criteria:** All planning docs merged to main, PLANS.md updated.

---

### M2: Architecture Decisions Complete

**Target:** Session 3

| Deliverable | Status |
| ------------- | -------- |
| Options Analysis: Architecture Style | Pending |
| Options Analysis: Protocol Strategy | Pending |
| ADR-001: Monolith-first architecture | Pending |
| ADR-002: Dual protocol (MCP + A2A) | Pending |
| ADR-003: Storage backend (Postgres + Qdrant) | Pending |
| ADR-004: Embedding model selection | Pending |
| ADR-005: Agent role architecture | Pending |
| ADR-006: Knowledge graph approach | Pending |
| Quint decisions recorded | Pending |

**Exit criteria:** All ADRs accepted, options analyses completed,
Quint decisions at L2+.

---

### M3: Design Complete

**Target:** Sessions 4-5

| Deliverable | Status |
| ------------- | -------- |
| System Design (15 mandatory sections) | Pending |
| Module: Memory Kernel | Pending |
| Module: Retrieval Engine | Pending |
| Module: Librarian Gate | Pending |
| Module: MCP Endpoint | Pending |
| Module: A2A Endpoint | Pending |
| Threat Model | Pending |
| SLI/SLO Targets | Pending |
| Risk Register | Pending |
| Design Review (AI red-team pass) | Pending |

**Exit criteria:** System design approved, all module designs complete,
threat model reviewed, risk register populated.

---

### M4: Specification Complete

**Target:** Session 6

| Deliverable | Status |
| ------------- | -------- |
| Technical Specification | Pending |
| Schema: Memory Types | Pending |
| Schema: API Contracts | Pending |
| Test Requirements | Pending |
| Design Review Checklist | Pending |
| AI Context Pack finalized | Pending |

**Exit criteria:** Spec approved, 24-hour cooling period elapsed,
schemas defined, test plan ready.

---

### M5: MVP Implementation Complete

**Target:** Sessions 7-10

| Deliverable | Status |
| ------------- | -------- |
| Memory kernel (Postgres schema, typed CRUD) | Pending |
| Embedding + vector adapter (fastembed + Qdrant) | Pending |
| Retrieval engine (hybrid search, validation) | Pending |
| Librarian gate (policy enforcement) | Pending |
| MCP endpoint (tool exposure) | Pending |
| A2A endpoint (Agent Card, task lifecycle) | Pending |
| Researcher agent role | Pending |
| Docker Compose stack | Pending |
| Unit tests (>80% coverage) | Pending |
| Integration tests (critical paths) | Pending |

**Exit criteria:** All components functional, tests passing, Docker
Compose stack runs end-to-end.

---

### M6: v0.1.0 Release

**Target:** Session 11+

| Deliverable | Status |
| ------------- | -------- |
| Observability checklist | Pending |
| Operational notes | Pending |
| Deployment guide | Pending |
| Release checklist | Pending |
| Release notes | Pending |
| CI gates E-F pass | Pending |
| README finalized | Pending |
| Design post-mortem | Pending |

**Exit criteria:** All CI gates pass, docs complete, v0.1.0 tagged.

## Work streams

| Stream | Description | Active in |
| -------- | ------------- | ----------- |
| Design | Architecture, design artifacts, ADRs | M1-M4 |
| Implementation | Code, tests, Docker stack | M5 |
| Infrastructure | CI/CD, pre-commit, tooling | M1-M6 |
| Documentation | README, ops docs, release notes | M1-M6 |

## Risks and constraints

- **A2A protocol evolution:** Pin SDK version, use adapter pattern.
  Monitor releases between sessions.
- **Scope creep:** Strictly follow MVP boundary from charter. Any
  additions require charter amendment (PR + version bump).
- **Session continuity:** PLANS.md, Quint log, and memory files must
  be updated every session.
- **Solo developer:** No peer review. Compensate with AI red-team pass
  and Quint decision tracking.

## Dependencies

- policies-and-standards KB (v2.0.0) — templates, CI workflows.
- Docker Desktop with WSL2 integration — local dev stack.
- PyPI packages: a2a-sdk, fastapi, qdrant-client, fastembed.
- GitHub Actions — CI/CD pipeline.

## Status updates

| Date | Update |
| ------ | -------- |
| 2026-02-12 | Session 1: Repo scaffolded, Intake + Proposal drafted, PR #1 merged. |
| 2026-02-12 | Session 2: Charter, PRD, Roadmap, Backlog completed. M1 (Planning) complete. |

## Links

- Intake: [project-intake.md](project-intake.md)
- Proposal: [project-proposal.md](project-proposal.md)
- Charter: [project-charter.md](../governance/project-charter.md)
- PRD: [requirements-prd.md](requirements-prd.md)
- Backlog: [backlog-milestones.md](backlog-milestones.md)
- SDLC:
  [SDLC_With_AI](https://github.com/sh4i-yurei/policies-and-standards/blob/main/05_Dev_Workflows/SDLC_With_AI.md)

# Implementation Notes

- Update milestone statuses as sessions complete.
- Add status update rows chronologically.
- Milestone targets are session-based, not calendar-based (long-term
  project, no fixed schedule).

# Continuous Improvement and Compliance Metrics

- Track milestone completion rate vs targets.
- Track artifact drift (docs out of date with implementation).

# Compliance

Tier 3 projects without a roadmap are non-compliant per STD-032.

# Changelog

- 0.1.0 — Initial roadmap for 3ngram project.
