---
id: 3NGRAM-SLI-001
title: "3ngram SLI/SLO Targets"
version: 0.1.0
category: project
status: draft
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-13
extends: [STD-001, STD-043]
tags: [sli, slo, reliability, operations, 3ngram]
---

# 3ngram SLI/SLO Targets

# Purpose

Define measurable service level indicators (SLIs) and objectives (SLOs)
for 3ngram's critical paths. These targets guide Phase 1 instrumentation
and provide early quality signals for a development-environment system
with no formal SLA.

# Scope

Covers all Phase 1 critical paths: write path (Librarian Gate), read
path (retrieval pipeline), embedding generation, application health,
and data integrity. Consolidation SLOs activate in Phase 2 when the
CLS engine is deployed.

# Standard

## SLI/SLO definitions

### 1. Write path — Gate approval latency

**SLI definition**:

| Field | Value |
|---|---|
| Name | `gate_approval_latency` |
| Description | Time from Gate entry to write decision (approve/reject) |
| Unit | Milliseconds |
| Numerator | Count of Gate decisions completed within threshold |
| Denominator | Total Gate decisions in window |
| Data source | structlog timer (`engram.memory.gate`) |
| Aggregation window | 30-day rolling |
| Sampling cadence | Every Gate invocation (100% sampling) |

**SLO target**:

| Field | Value |
|---|---|
| Target | 99% of auto-approve decisions complete in < 200ms (p99) |
| Compliance window | 30 days |
| Error budget | 1% of Gate decisions may exceed 200ms (~300 over 30K writes/month) |
| Owner | sh4i-yurei |

**Alerting**:

- Warn: 50% of error budget consumed at day 15
- Critical: 2x burn rate over 24 hours OR 1x burn rate over 7 days
- Action: Investigate Gate rule complexity; check PostgreSQL query plans

### 2. Read path — Retrieval latency

**SLI definition**:

| Field | Value |
|---|---|
| Name | `retrieval_latency` |
| Description | Time from query receipt to validated result delivery |
| Unit | Milliseconds |
| Numerator | Count of retrievals completing within threshold |
| Denominator | Total retrieval requests in window |
| Data source | structlog timer (`engram.retrieval.pipeline`) |
| Aggregation window | 30-day rolling |
| Sampling cadence | Every retrieval request (100% sampling) |

**SLO target**:

| Field | Value |
|---|---|
| Target | 95% of retrievals return results in < 2000ms (p95) |
| Compliance window | 30 days |
| Error budget | 5% of retrievals may exceed 2000ms |
| Owner | sh4i-yurei |

**Alerting**:

- Warn: 50% of error budget consumed at day 15
- Critical: 2x burn rate over 24 hours OR 1x burn rate over 7 days
- Action: Check pgvector index health; review query complexity

**Latency budget breakdown** (Phase 1 targets):

| Stage | Budget | Notes |
|---|---|---|
| Query routing | < 10ms | Heuristic classifier |
| Candidate retrieval (vector) | < 200ms | pgvector cosine similarity |
| Candidate retrieval (BM25) | < 100ms | Postgres full-text search |
| Validation and filtering | < 100ms | In-process checks (no LLM) |
| Conflict resolution + assembly | < 50ms | In-process |
| Overhead (serialization, I/O) | < 100ms | Protocol adapter round-trip |
| **Total budget** | **< 560ms** | Well within 2000ms SLO |

### 3. Embedding generation latency

**SLI definition**:

| Field | Value |
|---|---|
| Name | `embedding_latency` |
| Description | Time to generate embedding vector for a single record |
| Unit | Milliseconds |
| Numerator | Count of embeddings generated within threshold |
| Denominator | Total embedding generation requests in window |
| Data source | structlog timer (`engram.infra.embeddings`) |
| Aggregation window | 30-day rolling |
| Sampling cadence | Every embedding request (100% sampling) |

**SLO target**:

| Field | Value |
|---|---|
| Target | 95% of embeddings complete in < 500ms (CPU-only) |
| Compliance window | 30 days |
| Error budget | 5% of embeddings may exceed 500ms |
| Owner | sh4i-yurei |

**Alerting**:

- Warn: 50% of error budget consumed at day 15
- Critical: 2x burn rate over 24 hours OR 1x burn rate over 7 days
- Action: Check CPU load; verify model is loaded; review batch sizes

### 4. Application health and availability

**SLI definition**:

| Field | Value |
|---|---|
| Name | `application_uptime` |
| Description | Percentage of health probes returning healthy |
| Unit | Percentage |
| Numerator | Successful `/health` responses (HTTP 200) |
| Denominator | Total `/health` probe attempts |
| Data source | Prometheus counter (`engram_health_checks_total`) |
| Aggregation window | 30-day rolling |
| Sampling cadence | Every 30 seconds |

**SLO target**:

| Field | Value |
|---|---|
| Target | 99% uptime (allows ~7.2 hours downtime per 30-day window) |
| Compliance window | 30 days |
| Error budget | 1% of probes may fail |
| Owner | sh4i-yurei |

**Cold start SLI**:

| Field | Value |
|---|---|
| Name | `cold_start_duration` |
| Description | Time from process start to first successful health check |
| Unit | Seconds |
| Target | < 30 seconds (application + migrations) |
| Data source | structlog startup timer |

**Alerting**:

- Warn: 3 consecutive failed health probes
- Critical: 10 consecutive failed health probes (5 minutes)
- Action: Check PostgreSQL connectivity; review application logs

### 5. Data integrity — Gate audit completeness

**SLI definition**:

| Field | Value |
|---|---|
| Name | `gate_audit_completeness` |
| Description | Percentage of writes with a corresponding Gate audit entry |
| Unit | Percentage |
| Numerator | Records with non-null `gate_decision_id` |
| Denominator | Total records in `memory_records` table |
| Data source | PostgreSQL query (scheduled check) |
| Aggregation window | Point-in-time (checked daily) |
| Sampling cadence | Daily batch scan |

**SLO target**:

| Field | Value |
|---|---|
| Target | 100% of records have a Gate audit trail |
| Compliance window | Continuous |
| Error budget | 0 — any record without audit is a P0 incident |
| Owner | sh4i-yurei |

**Alerting**:

- Any non-zero gap triggers immediate alert
- Action: Investigate bypass path; halt writes until resolved

### 6. Consolidation correctness (Phase 2)

**SLI definition**:

| Field | Value |
|---|---|
| Name | `consolidation_retention` |
| Description | Semantic similarity between consolidated and source records |
| Unit | Cosine similarity ratio (0.0-1.0) |
| Numerator | Consolidation operations with retention >= threshold |
| Denominator | Total consolidation operations |
| Data source | structlog (`engram.memory.consolidation`) |
| Aggregation window | 30-day rolling |
| Sampling cadence | Every consolidation operation |

**SLO target**:

| Field | Value |
|---|---|
| Target | 95% of consolidations retain >= 0.85 semantic similarity |
| Compliance window | 30 days |
| Error budget | 5% of consolidations may fall below threshold |
| Owner | sh4i-yurei |
| Activation | Phase 2 (CLS engine deployment) |

**Alerting**:

- Warn: 50% of error budget consumed at day 15
- Critical: 2x burn rate over 24 hours
- Action: Review consolidation prompts; inspect low-similarity cases

## Error budget policy

When an error budget is exhausted within its compliance window:

1. **Feature releases pause** — no new functionality until the SLO is
   restored. Bug fixes and SLO-improving changes are permitted.
2. **Root cause analysis** — investigate the budget exhaustion cause
   within 24 hours.
3. **Remediation plan** — document fix and prevention in the risk
   register.

Exception: The 99% uptime target is appropriate for a development
environment. Extended maintenance windows are acceptable with advance
planning (deducted from error budget).

## Ownership and review cadence

- **Owner**: sh4i-yurei (sole maintainer)
- **Review cadence**: Quarterly, or after any Sev-1/Sev-2 incident
- **Dashboard**: Prometheus metrics exposed at `/metrics`; Grafana
  dashboard (Phase 2)
- **SLO revision**: Tighten targets as the system matures and
  instrumentation improves

## Phase 1 constraints

- All SLIs except consolidation (§6) are measurable from day one using
  structlog timers and Prometheus client counters.
- Consolidation SLO activates when the CLS engine is deployed (Phase 2).
- No external monitoring infrastructure required — metrics are
  self-reported via the `/metrics` endpoint and structured logs.
- Latency measurements use monotonic clocks to avoid time-skew issues.

# Implementation Notes

- Instrument all SLIs using `structlog` with consistent field names:
  `sli_name`, `sli_value`, `sli_unit`, `sli_threshold`.
- Prometheus metrics follow naming convention:
  `engram_{subsystem}_{metric}_{unit}` (e.g.,
  `engram_gate_approval_duration_milliseconds`).
- Use histogram metrics for latency SLIs (not summaries) to support
  aggregation.
- Health check endpoint (`/health`) returns component-level status
  (PostgreSQL, embedding model, event bus).
- Error budget tracking is computed from Prometheus counters; no
  separate budget storage needed.

# Continuous Improvement and Compliance Metrics

- Track SLO compliance percentage per 30-day window.
- Track error budget burn rate trends.
- Track SLI definition changes (version history in this document).
- Review SLO appropriateness when Phase 2 or Phase 3 features activate
  — targets may need adjustment for increased system complexity.

# Compliance

This document complies with:

- **STD-001** (Documentation Standard): All mandatory sections present.
- **STD-043** (SLI/SLO Standard): SLI definitions include all required
  fields (name, description, unit, numerator, denominator, data source,
  aggregation window, sampling cadence). SLO definitions include target,
  compliance window, error budget, ownership, and alerting thresholds.

Referenced by:

- System design: `docs/design/system-design.md` §§ Non-Functional
  Requirements, Success Metrics

# Changelog

## 0.1.0 — 2026-02-13

**Added:**

- Initial SLI/SLO definitions for 6 critical paths
- Write path Gate latency (p95 < 200ms, 99% compliance)
- Read path retrieval latency (p95 < 2000ms, 95% compliance)
- Embedding generation latency (p95 < 500ms, 95% compliance)
- Application uptime (99%) and cold start (< 30s)
- Gate audit completeness (100%, zero error budget)
- Consolidation retention (Phase 2 activation, 95% compliance)
- Error budget policy, alerting thresholds per STD-043
- Latency budget breakdown for retrieval pipeline stages

**Status**: Draft — pending review
