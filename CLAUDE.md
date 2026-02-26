# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

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

## Knowledge base

KB pinned to `v2.1.0` via `.kb/ai-context.yaml`. See `kb-navigation`
rule for retrieval commands and standards lookup. See `AI_CONTEXT.md`
for applicable standards and current phase context.

### Applicable rule packs (STD-048)

Based on 3ngram's scope (API service + data storage + auth/trust boundaries):

- **STD-050** `rules-api` — API contracts, service interfaces, observability
- **STD-051** `rules-data` — Data models, storage, migrations
- **STD-053** `rules-security` — Authentication, secrets, trust boundaries

Frontend rules (STD-049) do not apply — 3ngram has no UI.

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

Project-level scripts (issue #21):

- `scripts/validate-version-refs.sh` — version consistency across docs
- `scripts/check-frontmatter.py` — governed doc frontmatter validation
- `scripts/vulture_whitelist.py` — vulture false positive suppression

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
