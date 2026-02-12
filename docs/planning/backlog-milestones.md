---
id: 3NGRAM-BACKLOG-001
title: "3ngram: Agentic RAG Memory System — Backlog and Milestones"
version: 0.1.0
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-003, STD-032]
tags: [backlog, milestones, planning, 3ngram]
---

# Purpose

Track all work items for the 3ngram project, organized by milestone,
with dependencies and sequencing.

# Scope

Covers MVP (v0.1.0) work items only. Post-MVP items are listed in the
project proposal but not tracked here until a phase 2 backlog is created.

# Standard

## Milestones

### M1: Planning Complete

| ID | Item | Owner | Status | Links |
| ---- | ------ | ------- | -------- | ------- |
| P-01 | Project Intake | sh4i-yurei | Done | [project-intake.md](project-intake.md) |
| P-02 | Project Proposal | sh4i-yurei | Done | [project-proposal.md](project-proposal.md) |
| P-03 | Project Charter | sh4i-yurei | Done | [project-charter.md](../governance/project-charter.md) |
| P-04 | PRD | sh4i-yurei | Done | [requirements-prd.md](requirements-prd.md) |
| P-05 | Project Roadmap | sh4i-yurei | Done | [project-roadmap.md](project-roadmap.md) |
| P-06 | Backlog and Milestones | sh4i-yurei | Done | this document |

---

### M2: Architecture Decisions Complete

| ID | Item | Owner | Status | Depends on |
| ---- | ------ | ------- | -------- | ------------ |
| A-01 | Options Analysis: Architecture Style | sh4i-yurei | Pending | M1 |
| A-02 | Options Analysis: Protocol Strategy | sh4i-yurei | Pending | M1 |
| A-03 | ADR-001: Monolith-first architecture | sh4i-yurei | Pending | A-01 |
| A-04 | ADR-002: Dual protocol (MCP + A2A) | sh4i-yurei | Pending | A-02 |
| A-05 | ADR-003: Storage backend | sh4i-yurei | Pending | A-01 |
| A-06 | ADR-004: Embedding model | sh4i-yurei | Pending | A-01 |
| A-07 | ADR-005: Agent role architecture | sh4i-yurei | Pending | A-01 |
| A-08 | ADR-006: Knowledge graph approach | sh4i-yurei | Pending | A-01 |
| A-09 | Quint decisions recorded (all ADRs) | sh4i-yurei | Pending | A-03 through A-08 |

---

### M3: Design Complete

| ID | Item | Owner | Status | Depends on |
| ---- | ------ | ------- | -------- | ------------ |
| D-01 | System Design (15 sections) | sh4i-yurei | Pending | M2 |
| D-02 | Module: Memory Kernel | sh4i-yurei | Pending | D-01 |
| D-03 | Module: Retrieval Engine | sh4i-yurei | Pending | D-01 |
| D-04 | Module: Librarian Gate | sh4i-yurei | Pending | D-01 |
| D-05 | Module: MCP Endpoint | sh4i-yurei | Pending | D-01 |
| D-06 | Module: A2A Endpoint | sh4i-yurei | Pending | D-01 |
| D-07 | Threat Model | sh4i-yurei | Pending | D-01 |
| D-08 | SLI/SLO Targets | sh4i-yurei | Pending | D-01 |
| D-09 | Risk Register | sh4i-yurei | Pending | D-01 |
| D-10 | Design Review (AI red-team pass) | sh4i-yurei | Pending | D-02 through D-09 |

---

### M4: Specification Complete

| ID | Item | Owner | Status | Depends on |
| ---- | ------ | ------- | -------- | ------------ |
| S-01 | Technical Specification | sh4i-yurei | Pending | M3 |
| S-02 | Schema: Memory Types | sh4i-yurei | Pending | D-02 |
| S-03 | Schema: API Contracts | sh4i-yurei | Pending | D-05, D-06 |
| S-04 | Test Requirements | sh4i-yurei | Pending | S-01 |
| S-05 | Design Review Checklist | sh4i-yurei | Pending | S-01 |
| S-06 | AI Context Pack | sh4i-yurei | Pending | S-01 |
| S-07 | 24-hour cooling period | sh4i-yurei | Pending | S-05 |

---

### M5: MVP Implementation Complete

| ID | Item | Owner | Status | Depends on |
| ---- | ------ | ------- | -------- | ------------ |
| I-01 | Memory kernel (Postgres schema, typed CRUD) | sh4i-yurei | Pending | M4, S-02 |
| I-02 | Embedding + vector adapter (fastembed + Qdrant) | sh4i-yurei | Pending | I-01 |
| I-03 | Retrieval engine (hybrid search, validation) | sh4i-yurei | Pending | I-02 |
| I-04 | Librarian gate (policy enforcement) | sh4i-yurei | Pending | I-01 |
| I-05 | MCP endpoint (tool exposure) | sh4i-yurei | Pending | I-03, I-04 |
| I-06 | A2A endpoint (Agent Card, task lifecycle) | sh4i-yurei | Pending | I-03, I-04 |
| I-07 | Researcher agent role | sh4i-yurei | Pending | I-05, I-06 |
| I-08 | Docker Compose stack | sh4i-yurei | Pending | I-01 |
| I-09 | Unit tests (>80% coverage) | sh4i-yurei | Pending | I-01 through I-07 |
| I-10 | Integration tests (critical paths) | sh4i-yurei | Pending | I-08, I-09 |

---

### M6: v0.1.0 Release

| ID | Item | Owner | Status | Depends on |
| ---- | ------ | ------- | -------- | ------------ |
| R-01 | Observability checklist | sh4i-yurei | Pending | M5 |
| R-02 | Operational notes | sh4i-yurei | Pending | M5 |
| R-03 | Deployment guide | sh4i-yurei | Pending | I-08 |
| R-04 | Release checklist | sh4i-yurei | Pending | R-01 through R-03 |
| R-05 | Release notes | sh4i-yurei | Pending | R-04 |
| R-06 | CI gates E-F pass | sh4i-yurei | Pending | I-10 |
| R-07 | README finalized | sh4i-yurei | Pending | M5 |
| R-08 | Design post-mortem | sh4i-yurei | Pending | R-05 |

## Dependencies and sequencing

```text
M1 (Planning) ──► M2 (Architecture) ──► M3 (Design) ──► M4 (Specification)
                                                              │
                                                              ▼
                                                    [24-hour cooling]
                                                              │
                                                              ▼
                                                    M5 (Implementation)
                                                              │
                                                              ▼
                                                    M6 (Release)
```

**Critical path:** M1 → M2 → M3 → M4 → M5 → M6

No milestone can start until its predecessor is complete, per STD-032
Tier 3 ceremony. The 24-hour cooling period between M4 and M5 is
mandatory per the project charter.

## Notes

- Work items are session-based, not calendar-based. Each session
  advances one or more milestones.
- Item IDs use prefixes: P (planning), A (architecture), D (design),
  S (specification), I (implementation), R (release).
- Update status as work progresses. Valid statuses: Pending, In
  progress, Done, Blocked.
- Post-MVP backlog (knowledge graph, additional agent roles, workspace
  adapters, etc.) will be tracked in a separate document when Phase 2
  planning begins.

# Implementation Notes

- Keep backlog items atomic — one deliverable per row.
- Update this document every session alongside PLANS.md.

# Continuous Improvement and Compliance Metrics

- Track items completed per session.
- Track blocked items and resolution time.

# Compliance

Tier 3 projects without a backlog are non-compliant per STD-032.

# Changelog

- 0.1.0 — Initial backlog for 3ngram project.
