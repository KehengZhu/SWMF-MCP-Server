---
name: swmf-diagnose
description: "Use when debugging SWMF PARAM input, build/config, startup, runtime crashes, MPI/coupling layout, numerical anomalies, restart/postprocess issues, or source-change regressions. Enforces evidence-first protocol, invariant checks, and no-early-patch guardrails."
---

# SWMF Diagnose Protocol Skill

## Purpose
Use a universal debugging protocol for SWMF that is process-oriented, evidence-first, and extensible.
The goal is to prevent early patching and force structured narrowing from observations to mechanism.

## Required State Machine
Every debugging session must move through these states in order:

1. intake
2. classification
3. evidence_collection
4. normalization
5. hypothesis_staging
6. discriminating_experiment
7. patch_readiness
8. validation

Rules:
- Do not skip states.
- Do not move backward unless new evidence invalidates a prior assumption.
- Do not enter patch_readiness unless invariant context exists for source-level changes.

## Mandatory First Output
Before proposing edits, produce:
- failure family classification
- required context pack checklist
- missing artifacts list
- explicit observation report
- candidate mechanisms (only after evidence pack is complete)
- cheapest discriminating next check

## Routing
Use taxonomy in taxonomy.yaml to classify into one family:
- input_schema
- build_config
- startup_initialization
- runtime_crash_stop
- hang_stall_performance
- coupling_mpi_layout
- numerical_physics_anomaly
- postprocess_restart_output
- source_change_validation

## Evidence Discipline
Always separate outputs into:
- observations: factual, source-grounded, no causal claims
- mechanism_candidates: competing explanations with confidence + required checks

Never infer mechanism from plots only when raw files or logs disagree.

## Patch Guardrails
Never patch when any of the following is true:
- evidence pack is incomplete
- version/source path mismatch is unresolved
- invariant block is missing for source changes
- discriminating check has not been proposed

For source edits, require invariant context with:
- data structure under modification
- invariants_before_change
- operations_that_can_violate
- diagnostics_to_collect
- runtime_checks

## Tooling Strategy
Prefer reusable evidence primitives:
- swmf_collect_param_context
- swmf_resolve_param_includes
- swmf_extract_component_map
- swmf_collect_build_context
- swmf_collect_run_context
- swmf_extract_first_error
- swmf_extract_stacktrace
- swmf_collect_source_context
- swmf_collect_invariant_context
- swmf_compare_run_artifacts

Use existing authoritative tools after evidence collection:
- swmf_run_testparam
- swmf_diagnose_param
- swmf_diagnose_error
- swmf_infer_job_layout

## Output Contract
Always include:
- protocol_version
- protocol_state
- failure_family
- observation_report
- mechanism_candidates
- unresolved_conflicts
- next_discriminating_checks
- patch_readiness
- invariant_block (required for source_change_validation)

## Distillation Update Loop
When adding lessons from new SWMF community chats:
- Distill to structured case schema in distillation/case_schema.yaml
- Update only one of: taxonomy, context pack, guardrail, routing rule, playbook, or examples
- Add new MCP tools only when the same evidence gap repeats across 2-3 unrelated cases
