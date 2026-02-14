# AI Context Pack — 3ngram

Context pack for AI-assisted work in this repository per STD-056 and
the [ai_context_pack_tpl](https://github.com/sh4i-yurei/policies-and-standards/blob/main/06_Projects/Templates/ai/ai_context_pack_tpl.md).

## Project summary

- **What**: Agentic RAG memory system — kernel-governed memory OS for AI agents.
- **Package**: `engram` (Python 3.12)
- **Current milestone**: M3 complete. Entering Stage 3 (Specification).
- **Phase**: Specification (pre-implementation). No code until specs approved (STD-020).

## Governing standards

Retrieve from `sh4i-yurei/policies-and-standards` (v2.0.0) via:

```bash
gh api repos/sh4i-yurei/policies-and-standards/contents/<path> --jq '.content' | base64 -d
```

### Always applicable

| ID | Standard | Path |
|----|----------|------|
| STD-032 | SDLC with AI | `05_Dev_Workflows/SDLC_With_AI.md` |
| STD-004 | AI Assisted Development | `03_Engineering_Standards/AI_Assisted_Development_Standard.md` |
| STD-020 | Design-First Development Model | `04_Design_Framework/Design_First_Development_Model.md` |
| STD-005 | Coding Standards and Conventions | `03_Engineering_Standards/Coding_Standards_and_Conventions.md` |
| STD-008 | Testing and Quality | `03_Engineering_Standards/Testing_and_Quality_Standard.md` |
| STD-056 | KB Integration | `03_Engineering_Standards/KB_Integration_Standard.md` |

### Current phase (specification)

| ID | Standard | Path |
|----|----------|------|
| STD-023 | Technical Specification Standard | `04_Design_Framework/Technical_Specification_Standard.md` |
| STD-055 | Schema Definition Standard | `04_Design_Framework/schema-definition-standard.md` |
| STD-024 | Design Review Checklist | `04_Design_Framework/Design_Review_Checklist.md` |
| STD-033 | Documentation Change Workflow | `05_Dev_Workflows/documentation_change_workflow.md` |
| STD-034 | Design Review Workflow | `05_Dev_Workflows/design_review_workflow.md` |

### Next phase (implementation)

| ID | Standard | Path |
|----|----------|------|
| STD-005 | Coding Standards and Conventions | `03_Engineering_Standards/Coding_Standards_and_Conventions.md` |
| STD-008 | Testing and Quality | `03_Engineering_Standards/Testing_and_Quality_Standard.md` |
| STD-030 | CI/CD Pipeline Model | `05_Dev_Workflows/cicd_pipeline.md` |

## Rule packs (STD-048)

Load these when starting implementation work. During specification phase,
reference them for interface and data model decisions.

| ID | Pack | Path | Applies because |
|----|------|------|-----------------|
| STD-050 | API rules | `03_Engineering_Standards/AI_Rules/rules-api.md` | MCP + A2A service interfaces |
| STD-051 | Data rules | `03_Engineering_Standards/AI_Rules/rules-data.md` | Postgres+pgvector, memory records, schemas |
| STD-053 | Security rules | `03_Engineering_Standards/AI_Rules/rules-security.md` | Librarian gate, trust boundaries, auth |

Frontend rules (STD-049) and operations rules (STD-052) do not apply
until deployment planning.

## Skills to invoke

| Skill | When |
|-------|------|
| `repo-orientation` | Starting a new task or session |
| `kb-search` | Finding applicable standards by topic |
| `design-review` | Reviewing design artifacts (STD-024, STD-034) |
| `security-review` | Reviewing security-critical designs (STD-007, STD-053) |
| `pr-review` | Before merging PRs (KB compliance audit) |

## Key files

### Governance

- `CLAUDE.md` — agent guidance and KB quick-reference
- `AGENTS.md` — AI agent behavior rules
- `PLANS.md` — ExecPlan requirements and session progress
- `.kb/ai-context.yaml` — KB source and pinning
- `.github/pull_request_template.md` — PR template

### Completed artifacts (M1 + M2 + M3)

- `docs/planning/project-intake.md` — project intake
- `docs/planning/project-proposal.md` — project proposal
- `docs/planning/requirements-prd.md` — PRD
- `docs/governance/project-charter.md` — charter
- `docs/planning/project-roadmap.md` — roadmap
- `docs/planning/backlog-milestones.md` — backlog
- `docs/architecture/options-analysis-architecture.md` — architecture options
- `docs/architecture/options-analysis-protocols.md` — protocol options
- `docs/architecture/adr/ADR-001-monolith-first.md` — monolith-first
- `docs/architecture/adr/ADR-002-dual-protocol.md` — MCP + A2A
- `docs/architecture/adr/ADR-003-storage-backend.md` — Postgres+pgvector
- `docs/architecture/adr/ADR-004-embedding-model.md` — fastembed (superseded by ADR-007)
- `docs/architecture/adr/ADR-005-agent-roles.md` — Protocol classes (superseded by ADR-008)
- `docs/architecture/adr/ADR-006-knowledge-graph.md` — KG deferred (superseded by ADR-009)
- `docs/design/system-design.md` — system design v0.1.3
- `docs/architecture/adr/ADR-007-embedding-adapter.md` — embedding adapter
- `docs/architecture/adr/ADR-008-expanded-agent-architecture.md` — expanded agents
- `docs/architecture/adr/ADR-009-knowledge-graph-phase2.md` — KG Phase 2
- `docs/architecture/adr/ADR-010-cls-consolidation.md` — CLS consolidation
- `docs/architecture/adr/ADR-011-hipporag-retrieval.md` — HippoRAG retrieval
- `docs/architecture/adr/ADR-012-hybrid-librarian-gate.md` — hybrid Gate
- `docs/operations/sli-slo.md` — SLI/SLO targets
- `docs/governance/risk-register.md` — risk register
- `docs/design/module-memory.md` — memory module design
- `docs/design/module-retrieval.md` — retrieval module design
- `docs/design/module-autonomy.md` — autonomy module design
- `docs/design/module-infrastructure.md` — infrastructure module design

### Pending artifacts (Stage 3 — Specification)

- `docs/specs/technical-specification.md` — technical specification
- `docs/design/schemas/` — schema definitions

### Templates (fetch from KB)

| Template | Path |
|----------|------|
| System design | `06_Projects/Templates/design/system_design_tpl.md` |
| Module design | `06_Projects/Templates/design/module_design_tpl.md` |
| Technical specification | `06_Projects/Templates/design/technical_specification_tpl.md` |
| Schema definition | `06_Projects/Templates/design/schema-definition_tpl.md` |
| Risk register | `06_Projects/Templates/risk/risk-register_tpl.md` |
| ExecPlan | `06_Projects/Templates/ai/exec_plan_tpl.md` |
| ADR | `06_Projects/Templates/architecture/adr_tpl.md` |

## Key architecture decisions

- **Monolith-first** (ADR-001): single Python service, clear module boundaries
- **Dual protocol** (ADR-002): MCP (agent-to-tools) + A2A v0.3 (agent-to-agent)
- **Postgres+pgvector** (ADR-003): unified storage (changed from Qdrant)
- **fastembed** (ADR-004): local embedding model
- **Protocol classes** (ADR-005): Python Protocols, no agent framework
- **KG deferred** (ADR-006): knowledge graph is post-MVP
- **Embedding adapter** (ADR-007): swappable embedding interface, fastembed default
- **Expanded agents** (ADR-008): RL Gate Advisor, Research Scanner, Meta-Optimizer
- **KG Phase 2** (ADR-009): NetworkX prototyping, Neo4j migration path
- **CLS consolidation** (ADR-010): dual-path fast/slow memory management
- **HippoRAG retrieval** (ADR-011): 6-stage pipeline with adaptive routing
- **Hybrid Gate** (ADR-012): declarative rules + RL-trained advisor
- **Self-healing**: aiobreaker circuit breakers + tenacity retries
- **Agent learning**: data collection from day one, algorithms post-MVP

## Prompt hygiene

- State goal, constraints, and acceptance criteria.
- Include spec excerpts and file targets.
- Reference the approved design artifact for the work in scope.
- Ask about uncertainties — do not infer requirements.
- Cite KB standards consulted in PR descriptions.

## Output expectations

- Small, focused diffs. No new dependencies unless approved.
- Tests added or updated for changed behavior.
- Summaries suitable for PR description (KB citations + AI disclosure).
- Design artifacts follow KB templates exactly.
