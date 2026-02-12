---
id: 3NGRAM-INTAKE-001
title: "3ngram: Agentic RAG Memory System — Project Intake"
version: 0.1.0
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-003, STD-032]
tags: [intake, planning, 3ngram, memory, rag, a2a]
---

# Purpose

Record the initiation of the 3ngram project — an agentic RAG memory
system and AI technology stack that treats memory as a kernel-governed
operating system for AI agents.

# Scope

This intake document captures the problem, goals, constraints, and
initial classification for the 3ngram project before design artifacts
are produced.

# Standard

## Summary

3ngram is a kernel-governed memory OS for AI agents. It provides typed,
versioned memory (Decision, Belief, Episode, Skill) with temporal
awareness, agentic retrieval with hybrid search, and a Librarian gate
for policy-controlled durable writes. It integrates MCP for agent-to-tool
communication and Google's A2A protocol (v0.3) for agent-to-agent
interoperability.

This project replaces the deprecated `ai_tech_stack` repository,
applying lessons learned from that attempt: start monolithic, test early,
deliver governance operationally rather than aspirationally.

## Requestor and owner

- Requestor: Mark (sh4i-yurei)
- Proposed owner/maintainer: Mark (sh4i-yurei)
- Date opened: 2026-02-12

## Problem statement

LLMs are fundamentally amnesic. Fixed context windows, no durable state,
and hallucinations when retrieval fails make current AI agent systems
unreliable for long-running, multi-session work. Existing RAG solutions
treat memory as a library concern — bolted on after the fact, with no
invariants, no policy gates, and no contradiction handling.

The previous attempt (`ai_tech_stack`) proved that a naive multi-service
approach creates more problems than it solves: 7 Docker services from day
one, fragile embedding layers, untested integrations, and governance that
existed in documents but not in running code.

The problem we are solving now: build a memory system that is
kernel-governed (mandatory invariants), protocol-native (MCP + A2A), and
operationally reliable — starting simple and extracting patterns only
when justified by real usage.

## Goals and success criteria

- Goal 1: Typed, versioned memory records (Decision, Belief, Episode,
  Skill) with temporal awareness, stored in Postgres with vector
  representations in Qdrant.
- Goal 2: Agentic retrieval pipeline — hybrid search (vector + keyword)
  with validation, bounded retries, and provenance tracking.
- Goal 3: Librarian gate — no durable memory write without policy
  authorization. All writes audited.
- Goal 4: MCP endpoint exposing memory operations as tools for Claude
  Code and other MCP clients.
- Goal 5: A2A endpoint enabling agent-to-agent task delegation, Agent
  Card discovery, and streaming communication per Google A2A v0.3.
- Goal 6: Researcher agent role demonstrating end-to-end retrieval from
  query to validated, cited response.
- Success: A running local stack (Docker Compose) where a Claude Code
  session can store memories, retrieve context, and delegate tasks to
  3ngram agents via A2A.

## Non-goals

- Knowledge graph layer (deferred to Phase 2+).
- Multiple agent roles beyond Researcher in v0.1.0.
- Workspace Intelligence Adapter, GitHub Control Plane, CLI Gateway.
- Skill mining or memory hygiene daemon.
- Librarian Console UI.
- Production deployment or multi-tenant support.
- Fine-tuning or training custom embedding models.

## Users and stakeholders

- Primary users: Mark (sole developer), Claude Code (AI agent client),
  future MCP/A2A-compatible agents.
- Stakeholders: Mark (owner, reviewer, approver).

## Constraints and assumptions

- Technical: WSL2 Ubuntu, Python 3.12, Docker Desktop with WSL
  integration. RTX 3070 GPU available — fastembed (CPU) is the default
  for simplicity, but GPU-accelerated models are viable if needed.
  A2A protocol is pre-1.0 (v0.3) and may evolve.
- Timeline: Long-term project. Design phase first, no rush to
  implementation. Quality over speed.
- Budget/compliance: Personal project. No external compliance
  requirements, but self-governed by the policies-and-standards KB.

## Initial change tier

Tier 3 (new system). Full ceremony per
[SDLC_With_AI](https://github.com/sh4i-yurei/policies-and-standards/blob/main/05_Dev_Workflows/SDLC_With_AI.md):
Proposal, PRD, Charter, System Design, Module Designs, ADRs, Tech Spec,
then implementation.

## Risks and dependencies

- Risk: A2A protocol is pre-1.0 and evolving rapidly. API surface may
  change between v0.3 and v1.0.
  Mitigation: Abstract A2A behind an adapter interface. Pin SDK version.
  Monitor release notes.
- Risk: Scope creep repeating ai_tech_stack pattern.
  Mitigation: Strict MVP boundary. Deferred items explicitly listed.
  Monolith-first architecture.
- Risk: Embedding model instability (experienced with SentenceTransformers
  in ai_tech_stack).
  Mitigation: Use fastembed (proven stable). Abstract behind adapter.
- Dependency: policies-and-standards KB (v2.0.0) for governance templates
  and CI/CD workflows.
- Dependency: Docker Desktop with WSL2 integration for local dev stack.

## Proposed next steps

- Draft Project Proposal (docs/planning/project-proposal.md).
- Draft PRD (docs/planning/requirements-prd.md).
- Draft Project Charter (docs/governance/project-charter.md).
- Begin architecture options analyses and ADRs.
- Proceed through Tier 3 design ceremony before implementation.

## Links

- Governing standards:
  [SDLC_With_AI](https://github.com/sh4i-yurei/policies-and-standards/blob/main/05_Dev_Workflows/SDLC_With_AI.md),
  [Issue_and_Change_Management_Policy](https://github.com/sh4i-yurei/policies-and-standards/blob/main/01_Governance/Issue_and_Change_Management_Policy.md)
- Predecessor: [ai_tech_stack](https://github.com/sh4i-yurei/ai_tech_stack) (deprecated)
- A2A Protocol: [a2a-protocol.org](https://a2a-protocol.org/latest/specification/)
- A2A Python SDK: [a2a-sdk on PyPI](https://pypi.org/project/a2a-sdk/)

# Implementation Notes

- This intake record lives in the project repo from day one rather than
  the KB repo, per project decision to co-locate artifacts with code.

# Continuous Improvement and Compliance Metrics

- Track time from intake to first design artifact.
- Review intake completeness during retrospectives.

# Compliance

New projects without an intake record or equivalent are non-compliant
per STD-032.

# Changelog

- 0.1.0 — Initial intake record for 3ngram project.
