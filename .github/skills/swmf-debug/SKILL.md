---
name: swmf-debug
description: Use for SWMF debugging across PARAM input, build/config, startup, runtime crashes, MPI/coupling layout, numerical anomalies, restart/output issues, and source-change validation.
---

# SWMF Debug

## Purpose
Own the evidence-first debugging protocol for SWMF.
This skill exists to stop premature patching and force the model to move from
observations to competing mechanisms to the cheapest discriminating check.

## Required State Machine
Every debugging session must move through these states in order:
1. `intake`
2. `classification`
3. `evidence_collection`
4. `normalization`
5. `hypothesis_staging`
6. `discriminating_experiment`
7. `patch_readiness`
8. `validation`

Rules:
- Do not skip states.
- Do not move into `patch_readiness` without invariant context for source edits.
- If new evidence breaks an assumption, move back only as far as needed.

## Failure Families
- `input_schema`
- `build_config`
- `startup_initialization`
- `runtime_crash_stop`
- `hang_stall_performance`
- `coupling_mpi_layout`
- `numerical_physics_anomaly`
- `postprocess_restart_output`
- `source_change_validation`

State the failure family before proposing fixes.

## Mandatory First Output
Before proposing edits, produce:
- failure family
- required context pack checklist
- missing artifacts list
- observation report
- mechanism candidates
- cheapest discriminating next check

## Evidence Discipline
Always separate:
- `observations`: literal facts from tools, files, plots, logs, or source
- `mechanism_candidates`: competing explanations with confidence and required checks

Never infer mechanism from a plot when raw files or logs disagree.

## MCP Evidence Map
- `swmf_collect_param_context`
- `swmf_resolve_param_includes`
- `swmf_extract_component_map`
- `swmf_collect_build_context`
- `swmf_collect_run_context`
- `swmf_extract_first_error`
- `swmf_extract_stacktrace`
- `swmf_collect_source_context`
- `swmf_collect_invariant_context`
- `swmf_compare_run_artifacts`
- `swmf_validate_param`
- `swmf_run_testparam`
- `swmf_search_source`
- `swmf_get_knowledge_index_status`
- `swmf_lookup_source_symbol`

## Patch Guardrails
Never patch when any of the following is true:
- evidence pack is incomplete
- version/source path mismatch is unresolved
- invariant block is missing for source changes
- no discriminating check has been proposed

Stop conditions:
- plot and raw-file evidence conflict
- first failing artifact has not been located
- authoritative validation has not been run where applicable

## Invariant Checklist
For source-level debugging, require:
- `data_structure`
- `invariants_before_change`
- `operations_that_can_violate`
- `diagnostics_to_collect`
- `runtime_checks`

Patch readiness can be true only when the invariant block exists and runtime checks can confirm or refute at least one mechanism candidate.

## Output Contract
Always include:
- `protocol_version`
- `protocol_state`
- `failure_family`
- `observation_report`
- `mechanism_candidates`
- `unresolved_conflicts`
- `next_discriminating_checks`
- `patch_readiness`
- `invariant_block` for source-change cases

## Collaboration Rules
- Accept handoffs from any other SWMF skill when a request becomes ambiguous or failure-driven.
- Hand back to `swmf-param-specialist` once the issue is narrowed to PARAM semantics.
- Hand back to `swmf-build-run` once the issue is narrowed to reproducible environment/setup steps.
- Hand back to `swmf-postproc` when the problem is isolated to output inspection or visualization behavior.
- Hand off to `swmf-implementation` only after patch readiness is satisfied.