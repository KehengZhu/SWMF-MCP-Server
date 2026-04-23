---
name: swmf-debug
description: "Use when something is broken or suspicious: run crash, wrong results, initialization failure, hang/stall, coupling error, build succeeded but behavior is incorrect, or any request that starts from failure evidence."
---

# swmf-debug

## When to use
- Run crashed or aborted
- Output is wrong or physically implausible
- Coupling is missing or silent
- Build succeeded but behavior is incorrect
- MPI error, rank mismatch, or layout problem
- Initialization failure in any component
- Any request where the user says "it failed" or "something went wrong"

## Do not use when
- User only wants conceptual explanation → `swmf-explain`
- User is configuring a case from scratch (no failure) → `swmf-configure`
- User wants to understand outputs (no failure) → `swmf-analyze`

## Evidence order

1. **Inspect artifact first** — always start from the failure artifact:
   ```
   inspect_artifact(artifact_type="log",     path=<log>)      # crashes, runtime errors
   inspect_artifact(artifact_type="param",   path=<PARAM.in>) # input failures
   inspect_artifact(artifact_type="run_dir", path=<run_dir>)  # layout/startup
   ```
   Read `findings`. Identify the failure family.

2. **Cross-component orientation** (only if failure spans components):
   ```
   get_context(question=<failure summary>, scope=[<components>], task_type="debug")
   ```

3. **Source grounding** after failure family is known:
   ```
   get_evidence(query=<symbol or error token>, mode="hybrid", goal="root cause of <family>")
   ```

4. **Regression comparison** (when user says "it worked before"):
   ```
   compare_artifacts(left=<baseline>, right=<modified>, comparison_type="log"|"param")
   ```

## Failure families

* `input_schema` — PARAM.in invalid or mismatched
* `build_config` — environment or compile issue
* `startup_initialization` — component init failure
* `runtime_crash_stop` — abort, segfault, or stop during run
* `hang_stall_performance` — no progress, timeout
* `coupling_mpi_layout` — rank mismatch, missing coupler message
* `numerical_physics_anomaly` — NaN, overflow, implausible output
* `postprocess_restart_output` — restart or output format problem
* `source_change_validation` — regression after a code change

State the failure family before proposing any fix.

## Required state machine

Every session must move in order: `intake` → `classification` → `evidence_collection`
→ `normalization` → `hypothesis_staging` → `discriminating_experiment`
→ `patch_readiness` → `validation`

Do not skip states. Do not move to `patch_readiness` without:
- failure family classified
- invariant block for source changes
- at least one discriminating check proposed

## Patch guardrails

Never patch when:
- evidence pack is incomplete
- invariant block is missing for source changes
- no discriminating check has been proposed

## Helper skills allowed

* `swmf-implementation` — for source patch preparation and invariant context
* `swmf-exact-lookup` — when findings name a specific symbol
* `swmf-params` — when narrowed to PARAM semantics

## Outputs (required)

* `protocol_state`
* `failure_family`
* `observation_report` (literal facts from artifacts, not interpretations)
* `mechanism_candidates` (competing explanations with confidence)
* `unresolved_conflicts`
* `next_discriminating_check`
* `patch_readiness` (true/false)
* `invariant_block` for source-change cases
