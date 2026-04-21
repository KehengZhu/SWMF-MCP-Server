---
name: swmf-build-run
description: Use for SWMF build and run preparation, environment readiness, configuration checks, component/version lookup, and bounded validation steps that support execution planning.
---

# SWMF Build&Run

## Purpose
Own build and run preparation without turning MCP back into a large execution workflow API.
This skill should plan from evidence, verify prerequisites, and use bounded validators where needed.

## Use This Skill For
- Build readiness and environment checks
- Configuration/state inspection
- Component/version lookup for planned runs
- Run-directory readiness and layout inspection
- Bounded validation steps before execution

## Boundaries
- This skill may use authoritative validators such as `swmf_run_testparam`.
- This skill should not recreate broad `make`, `Config.pl`, or run-wrapper MCP tools.
- If the user asks for broad coupling architecture, coupler relationships, or a Mermaid diagram of component links, hand off to `swmf-postproc` rather than treating the request as build readiness.
- If the user wants source changes, hand off to `swmf-implementation`.
- If the request becomes failure-driven, hand off to `swmf-debug`.

## Request Families
- `environment_readiness`
- `component_selection`
- `run_context_inspection`
- `layout_or_rank_mapping`
- `pre_execution_validation`

## MCP Evidence Map

### Deterministic tools
- `swmf_show_config`
- `swmf_collect_build_context`
- `swmf_collect_run_context`
- `swmf_extract_component_map`
- `swmf_validate_param`
- `swmf_run_testparam`

### Reference tools
- `swmf_list_components`
- `swmf_get_component`
- `swmf_get_param_command`
- `swmf_get_param_schema`

### Heuristic evidence when explanation is broad
- `swmf_search_source`
- `swmf_get_knowledge_index_status`

## Process
1. Determine whether the request is about environment, component selection, layout, or validation.
2. Collect deterministic build/run context first.
3. Use resource-backed lookup for components and PARAM expectations.
4. If execution-sensitive validation matters, run `swmf_run_testparam`.
5. Return a plan grounded in evidence, not a speculative shell workflow.

## Output Contract
Always include:
- `build_run_family`
- `environment_findings`
- `validated_prerequisites`
- `blocking_issues`
- `bounded_next_steps`
- `skill_handoffs` when another skill should continue

## Collaboration Rules
- Ask `swmf-param-specialist` for PARAM semantics or schema conflicts.
- Ask `swmf-debug` for failures, ambiguity, or regressions.
- Ask `swmf-postproc` when the request is about outputs rather than setup.
- Ask `swmf-postproc` when the request is about coupling architecture explanation rather than execution readiness.
- Ask `swmf-implementation` when the request requires new source behavior.

## Anti-patterns
- Do not invent runnable shell sequences from heuristic evidence.
- Do not treat a component listed in metadata as sufficient proof that a planned run is valid.
- Do not skip deterministic context collection for execution-sensitive answers.