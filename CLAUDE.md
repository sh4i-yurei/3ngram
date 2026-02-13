# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

3ngram is an agentic RAG memory system — a kernel-governed memory OS for
AI agents. It provides typed, versioned memory (Belief, Decision, Episode,
Skill, Entity, Preference, Reflection, Resource) with temporal awareness,
HippoRAG-inspired retrieval, and a hybrid Librarian Gate for durable
memory writes.

**Status**: Tier 3 design phase. No implementation code yet — all design
artifacts must be completed before writing code (STD-020).

**Python package name is `engram`** (not `3ngram`). Source lives in `src/engram/`.

## Current progress

Track session state in `PLANS.md` (last session: Session 6). Key milestones:

- **M1** (Planning): intake, proposal, PRD, charter, roadmap, backlog
- **M2** (Architecture): options analyses + ADRs 001-012

**Current**: M3 complete — system design v0.1.3, 4 module designs,
SLI/SLO, risk register, charter v0.2.1. Design review PASS (45/45).
**Next**: Stage 3 (Specification) — technical specs and schema definitions.

## Architecture decisions (ADRs)

All in `docs/architecture/adr/`. Key decisions:

- **ADR-001**: Monolith-first (single Python service, clear module boundaries)
- **ADR-002**: Dual protocol — MCP (agent-to-tools) + A2A v0.3 (agent-to-agent)
- **ADR-003**: Postgres+pgvector (unified storage, replaced original Qdrant plan)
- **ADR-004**: ~~fastembed for embeddings~~ (superseded by ADR-007)
- **ADR-005**: ~~Agent roles as Python Protocol classes~~ (superseded by ADR-008)
- **ADR-006**: ~~Knowledge graph deferred to post-MVP~~ (superseded by ADR-009)
- **ADR-007**: Embedding adapter (swappable interface, fastembed default)
- **ADR-008**: Expanded agent architecture (RL Gate Advisor, Research Scanner, Meta-Optimizer)
- **ADR-009**: Knowledge graph Phase 2 (NetworkX prototyping, Neo4j migration path)
- **ADR-010**: CLS consolidation (dual-path fast/slow memory management)
- **ADR-011**: HippoRAG retrieval (6-stage pipeline with adaptive routing)
- **ADR-012**: Hybrid Librarian Gate (declarative rules + RL-trained advisor)

Self-healing pattern: aiobreaker circuit breakers + tenacity retries at module boundaries.

## Knowledge base (KB)

The engineering KB is the authoritative source for all standards,
workflows, and templates. **Always consult the KB before design,
specification, or implementation work** (STD-056 section 4).

- **Source**: `sh4i-yurei/policies-and-standards` (pinned to `v2.0.0`)
- **Entry point**: `00_Orientation/Onboarding.md` (STD-015)
- **Full index**: `INDEX.md` at repo root
- **Local pointer**: `.kb/ai-context.yaml`

### How to retrieve KB content

```bash
# Fetch any KB document by path
gh api repos/sh4i-yurei/policies-and-standards/contents/<path> \
  --jq '.content' | base64 -d

# Examples
gh api repos/sh4i-yurei/policies-and-standards/contents/INDEX.md --jq '.content' | base64 -d
gh api repos/sh4i-yurei/policies-and-standards/contents/05_Dev_Workflows/SDLC_With_AI.md --jq '.content' | base64 -d
```

Use the `kb-search` skill for topic-based lookup when the exact path is unknown.

### Standards quick-reference

**Governance and orientation:**

| ID | Standard | When to consult |
|----|----------|----------------|
| STD-000 | Software Engineering Governance Overview | Root governance reference |
| STD-010 | Mission Statement | Understanding practice purpose |
| STD-013 | Core Principles | Values shaping all decisions |
| STD-015 | Onboarding | Starting a new session or onboarding |
| STD-016 | Pipeline Phases Overview | Understanding SDLC phase terminology |
| STD-032 | SDLC with AI | **Authoritative workflow** — consult for any change |

**Design and architecture (current phase):**

| ID | Standard | When to consult |
|----|----------|----------------|
| STD-020 | Design-First Development Model | Before any implementation — design is a mandatory gate |
| STD-021 | System Design Standard | Writing system design artifacts |
| STD-022 | Module Design Standard | Writing module design artifacts |
| STD-023 | Technical Specification Standard | Writing specs that authorize implementation |
| STD-024 | Design Review Checklist | Reviewing any design artifact |
| STD-047 | Architecture Decision Workflow | Capturing ADRs |
| STD-055 | Schema Definition Standard | Documenting data/API schemas |

**Engineering standards:**

| ID | Standard | When to consult |
|----|----------|----------------|
| STD-004 | AI Assisted Development Standard | Constraints on AI-generated work |
| STD-005 | Coding Standards and Conventions | Writing or reviewing code |
| STD-007 | Security and Threat Modeling Standard | Threat model, security design |
| STD-008 | Testing and Quality Standard | Test strategy and quality gates |
| STD-043 | SLI/SLO Standard | Defining service level targets |
| STD-044 | Data Management Standard | Data classification, retention, backups |
| STD-056 | KB Integration Standard | How repos reference the KB |
| STD-058 | Agent Skills Standard | Authoring agent skills |

**Workflows:**

| ID | Standard | When to consult |
|----|----------|----------------|
| STD-030 | CI/CD Pipeline Model | CI gate definitions and requirements |
| STD-031 | Git and Branching Workflow | Branch strategy, PR flow |
| STD-033 | Documentation Change Workflow | Changing governed docs |
| STD-034 | Design Review Workflow | Executing design reviews |
| STD-054 | Repo Initialization Workflow | Setting up new repos |

**Templates (in `06_Projects/Templates/`):**

| Path | Purpose |
|------|---------|
| `design/system_design_tpl.md` | System design artifact |
| `design/module_design_tpl.md` | Module design artifact |
| `design/technical_specification_tpl.md` | Technical specification |
| `design/schema-definition_tpl.md` | Schema definitions |
| `architecture/adr_tpl.md` | Architecture Decision Record |
| `architecture/architecture-options-analysis_tpl.md` | Options analysis |
| `risk/risk-register_tpl.md` | Risk register |
| `ai/exec_plan_tpl.md` | ExecPlan for complex work |
| `ai/ai_context_pack_tpl.md` | AI context pack |

### Applicable rule packs (STD-048)

Based on 3ngram's scope (API service + data storage + auth/trust boundaries):

- **STD-050** `rules-api` — API contracts, service interfaces, observability
- **STD-051** `rules-data` — Data models, storage, migrations
- **STD-053** `rules-security` — Authentication, secrets, trust boundaries

Load these rule packs when starting implementation work. Frontend rules
(STD-049) do not apply — 3ngram has no UI.

## SDLC phases (STD-032 / STD-016)

This project follows the Tier 3 path:

1. **Initiation** — intake, proposal, PRD, charter, roadmap (done)
2. **Design** — system design, module designs, threat model, SLI/SLO, risk register (current)
3. **Specification** — technical specs, schema definitions
4. **Implementation** — code within approved spec boundaries
5. **Verification** — tests, CI gates, staging validation
6. **Release** — release checklist, rollback plan, release notes
7. **Operations** — monitoring, incidents, design postmortems

**Do not skip phases.** Design is a mandatory gate (STD-020 section 2).

## Development commands

Build system: hatchling. Dev dependencies via `pip install -e ".[dev]"`.

```bash
# Linting and formatting
ruff check --fix .          # lint (rules: E,F,I,N,W,UP,B,SIM,RUF)
ruff format .               # format (line-length 88)
mypy src/                   # type checking (strict mode)

# Testing
pytest                      # run all tests (asyncio_mode=auto)
pytest tests/path/test_x.py           # single file
pytest tests/path/test_x.py::test_fn  # single test

# Docs linting
markdownlint-cli2 "docs/**/*.md"      # markdown lint
cspell "**/*.md"                       # spell check (config: .cspell.json)

# Pre-commit (runs trailing-whitespace, end-of-file-fixer, check-yaml,
# check-json, check-merge-conflict, markdownlint-cli2, ruff, ruff-format)
pre-commit run --all-files
```

## CI gates (STD-030)

CI runs on PRs to `main` via reusable workflows from policies-and-standards:

| Gate | Check |
|------|-------|
| A | Quint decision tracking |
| B | Documentation lint |
| C | Code lint + format (Python) |
| D | Tests (Python) |
| E | Config validation |
| F | Security scan |

## Conventions

- Conventional Commits: `type(scope): summary`
- Branch naming: `<type>/<short-name>` (feature/, fix/, chore/, docs/)
- Squash merge only, PR-based workflow
- All design artifacts use KB templates from policies-and-standards
- PRs must include KB citations and AI assistance summary (see `.github/pull_request_template.md`)

## Required governance files

Per STD-056, this repo must maintain:

- `AGENTS.md` — AI agent behavior rules
- `PLANS.md` — ExecPlan requirements and session progress
- `.kb/ai-context.yaml` — KB reference and pinning
- `AI_CONTEXT.md` — context pack (standards, rule packs, key files for current scope)
- `.claude/skills/repo-orientation/SKILL.md` — repo orientation skill
- `.github/pull_request_template.md` — PR template with KB citations

## Privileged operations

Use `/usr/local/sbin/codex-helper.sh` for privileged operations.
Do not run raw `sudo`.
