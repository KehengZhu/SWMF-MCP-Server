---
name: swmf-implementation
description: Use for source-change requests that add or alter SWMF scientific behavior. Phase-1 scope is scaffold only: define required evidence, invariants, collaboration rules, and patch-readiness gates before coding.
---

# SWMF Implementation

## Purpose
Own source-level implementation work for new scientific use cases or behavior changes in SWMF.
This phase is scaffold-only: the skill defines how implementation work must be prepared and guarded before edits begin.

## Current Scope
- Gather requirements and affected source locations
- Build invariant context before changes
- Identify dependent PARAM, build/run, and postprocessing implications
- Define validation expectations and artifact comparisons

Not yet in scope:
- domain-specific scientific playbooks for every physics use case
- broad autonomous feature design without explicit evidence and acceptance checks

## Required Preconditions Before Editing
1. User intent is specific enough to identify the scientific behavior to change.
2. Relevant source files or symbols are identified.
3. Invariant context exists.
4. Validation artifacts are identified.
5. At least one rollback-safe comparison path exists.

## MCP Evidence Map
- `swmf_collect_source_context`
- `swmf_collect_invariant_context`
- `swmf_compare_run_artifacts`
- `swmf_collect_param_context`
- `swmf_collect_build_context`
- `swmf_collect_run_context`
- `swmf_search_source`
- `swmf://knowledge/symbol/{name}`
- `swmf://param-command/{name}`
- `swmf://param-trace/{name}`

## Implementation Preparation Flow
1. Restate the requested behavior change and success condition.
2. Collect exact source context and surrounding interfaces.
3. Build the invariant block.
4. Identify validation evidence: runtime checks, artifact comparisons, or authoritative validators.
5. Only then move into code changes.

## Output Contract
Always include:
- `requested_behavior`
- `affected_symbols_or_files`
- `invariant_block`
- `validation_plan`
- `cross_skill_dependencies`
- `patch_readiness`

## Collaboration Rules
- Ask `swmf-param-specialist` for any PARAM semantics or new input contract implications.
- Ask `swmf-build-run` for configuration or run-environment consequences.
- Ask `swmf-postproc` for output or visualization validation expectations.
- Ask `swmf-debug` whenever the change request is actually a defect investigation rather than a defined feature.

## Guardrails
- Do not patch before invariant context exists.
- Do not accept heuristic search as the only evidence for a source change.
- Do not treat a requested behavior as complete until validation evidence is defined.