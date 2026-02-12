---
id: TPL-PRJ-PROP
title: Project proposal template
version: 0.1.7
category: project
status: active
owner: sh4i-yurei
reviewer: sh4i-yurei
approver: sh4i-yurei
last_updated: 2026-02-12
extends: [STD-001, STD-032, STD-033, STD-054]
tags: [template, proposal, planning, architecture]
---
# Purpose

Provide a reusable project proposal template for governed Tier 3 work. This document captures intent, constraints, and architectural direction before a repository, PRD, and design artifacts exist.

# Scope

Use when an idea requires structured review and must enter the Tier 3 pipeline defined in [SDLC_With_AI](../../../05_Dev_Workflows/SDLC_With_AI.md). A completed proposal is required before Tier 3 design artifacts are drafted.

# Standard

## Project proposal template

Use placeholders like `{PROJECT_NAME}` and `{PROJECT_OWNER}`. Replace all placeholders with project-specific values.

### Metadata

- Project name: {PROJECT_NAME}
- Owner/decision maker: {PROJECT_OWNER}
- Stakeholders: {STAKEHOLDERS}
- Target change tier: Tier 3
- Status: draft | review | active
- Source link(s): {SOURCE_LINKS}

### Purpose / concept summary

- Summarize the proposed system concept and how it advances the current stack.
- List primary use cases or user journeys: {PRIMARY_USE_CASES}
- State the key outcomes the project should deliver.

<!-- Example (illustrative only): Summarize the system concept, key architectural ideas, and how it improves current capabilities. -->

### Landscape and limitations

- Describe the current state and why it is insufficient.
- List known constraints (technical, organizational, regulatory).
- Summarize existing alternatives or prior attempts.

### Proposed architecture (high level)

- Provide a high-level architecture overview and core design principles.
- List major subsystems and their responsibilities: {KEY_COMPONENTS}
- Identify key integrations and external dependencies.
- Call out decisions that require options analysis and ADRs.

<!-- Example (illustrative only): List the major subsystems and briefly describe responsibilities. -->

### Deliverables (required before implementation)

- Project intake and classification: [project-intake_tpl](project-intake_tpl.md)
- PRD: [requirements-prd_tpl](requirements-prd_tpl.md)
- Project roadmap: [project-roadmap_tpl](project-roadmap_tpl.md)
- Backlog/milestones: [backlog-milestones_tpl](backlog-milestones_tpl.md)
- System design: [system_design_tpl](../design/system_design_tpl.md)
- Module design: [module_design_tpl](../design/module_design_tpl.md)
- Architecture options analysis: [architecture-options-analysis_tpl](../architecture/architecture-options-analysis_tpl.md)
- ADRs: [adr_tpl](../architecture/adr_tpl.md)
- Technical specification: [technical_specification_tpl](../design/technical_specification_tpl.md)
- Optional schema definitions: [schema-definition_tpl](../design/schema-definition_tpl.md)
- Operations artifacts (if applicable): [operational_notes_tpl](../operations/operational_notes_tpl.md),
  [runbooks_tpl](../operations/runbooks_tpl.md)

### Risks and dependencies

- Risks: {RISKS}
- Dependencies: {DEPENDENCIES}
- Mitigations: {MITIGATIONS}

### Success criteria and metrics

- Success criteria: {SUCCESS_CRITERIA}
- Metrics and signals to validate success: {SUCCESS_METRICS}
- SLI/SLO alignment (if applicable): {SLI_SLO_LINKS}

### Next steps

- Follow [project_repo_initialization_workflow](../../../05_Dev_Workflows/project_repo_initialization_workflow.md) when creating the repo.
- Draft Tier 3 artifacts per [SDLC_With_AI](../../../05_Dev_Workflows/SDLC_With_AI.md) and the approved templates.
- Coordinate AI-assisted red-team review (approved CLI agent + KB retrieval) and capture decisions in ADRs.
- Use [documentation_change_workflow](../../../05_Dev_Workflows/documentation_change_workflow.md) for updates to this template or derived artifacts.
- Reference applicable standards such as [AI_Assisted_Development_Standard](../../../03_Engineering_Standards/AI_Assisted_Development_Standard.md) and [Documentation_Standard](../../../02_Documentation_Standards/Documentation_Standard.md).

# Implementation Notes

- Keep this proposal high-level; detailed architecture lives in downstream artifacts.
- Do not include implementation details in this template.
- Use placeholders consistently and remove them once filled.

# Continuous Improvement and Compliance Metrics

- Track how many proposals complete required downstream artifacts before implementation.
- Capture feedback on missing sections to improve the template.

# Compliance

Proposals that omit required sections, links, or metadata are non-compliant until corrected.

# Changelog

- 0.1.7 - Generalized Codex reference to "approved CLI agent".
- 0.1.6 - Set owner/reviewer/approver values.
- 0.1.5 - Added owner/reviewer/approver frontmatter fields.

- 0.1.4 - Removed remaining project-specific reference.
- 0.1.3 - Clarified proposal requirement and standardized links.
- 0.1.2 - Generalized template and removed project-specific content.
- 0.1.1 - Updated red-team guidance to use KB retrieval.
- 0.1.0 - Initial template.
