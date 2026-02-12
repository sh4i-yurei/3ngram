# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## What this project is

3ngram is an agentic RAG memory system — a kernel-governed memory OS for
AI agents. It provides typed, versioned memory (Decision, Belief, Episode,
Skill) with temporal awareness, agentic retrieval, and a Librarian gate
for durable memory writes.

**Status**: Tier 3 design phase. No implementation code yet.

## Protocols

- **MCP** (Model Context Protocol) — vertical: agent-to-tools/context
- **A2A** (Google Agent-to-Agent Protocol, v0.3) — horizontal: agent-to-agent

## Language and stack

- Python 3.12, FastAPI, Pydantic
- a2a-sdk, MCP SDK
- Postgres + pgvector (state/audit/vectors), fastembed (embeddings)
- Docker Compose for local dev

## Project structure

```text
docs/
  planning/     — intake, proposal, PRD, roadmap, backlog
  design/       — system design, module designs, schemas
  architecture/ — options analyses, ADRs
  specs/        — technical specifications
  governance/   — charter, risk register, issue log
  operations/   — threat model, SLI/SLO
src/engram/     — Python package (empty until design phase completes)
tests/          — test suite (empty until design phase completes)
plans/          — ExecPlans for complex tasks
```

## Current phase

Design-first per STD-032 Tier 3. Produce all design artifacts before
writing implementation code. The sequence is:

1. Intake + Proposal (current)
2. PRD + Charter + Roadmap
3. Architecture options + ADRs
4. System Design + Threat Model + SLI/SLO
5. Module Designs
6. Technical Specification + Schemas
7. Implementation begins

## Conventions

- Conventional Commits: `type(scope): summary`
- Branch naming: `<type>/<short-name>` (feature/, fix/, chore/, docs/)
- Squash merge only, PR-based workflow
- Secrets in `.env`, never committed
- All design artifacts use KB templates from policies-and-standards

## Governance

- KB source: sh4i-yurei/policies-and-standards (v2.0.0)
- See `.kb/ai-context.yaml` for KB integration config
- See `AGENTS.md` for AI agent behavior rules
- See `PLANS.md` for ExecPlan requirements

## Privileged operations

Use `/usr/local/sbin/codex-helper.sh` for privileged operations.
Do not run raw `sudo`.
