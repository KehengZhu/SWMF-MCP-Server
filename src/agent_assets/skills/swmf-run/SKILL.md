---
name: swmf-run
description: "Use when the task is about how to execute a SWMF simulation: launch sequence, run scripts, run environment, job submission, or pre-run checks."
---

# swmf-run

## When to use
- "How do I submit this job?"
- "What scripts do I run before launching?"
- "How do I set up a restart run?"
- "What does the run directory need to contain?"
- "How do I check if the run is ready to start?"
- Any task about execution procedure and run environment

## Do not use when
- User wants to configure PARAM → `swmf-configure`
- User wants to build → `swmf-build`
- Something failed during a run → `swmf-debug`
- User wants to interpret outputs → `swmf-analyze`

## Evidence order

1. `get_evidence(query=<run goal>, task_type="run", goal=<run goal>)`
   — launch scripts, restart scripts, pre-run entrypoints
2. `inspect_artifact(artifact_type="run_dir", path=<run_dir>)`
   — run directory layout/readiness, PARAM-structure summary, and
     `component_output_artifacts` (saveplot intent → discovered output files)
   — for run intent (session purpose, control cadence, save-plot meaning),
     read the run-local `PARAM.in` directly after this step
   — compact runlog status when logs are present; do not directly read whole
     runlogs unless the user explicitly asks for raw log content
3. `get_evidence(mode="keyword", goal="run environment or job script")`
   — for specific run flags or cluster submission patterns
4. PARAM validation before launch:
   ```
   inspect_artifact(artifact_type="param", path=<PARAM.in>,
                    check_rules=True,
                    question="validate structure and component map")
   ```
   The param inspector returns structural primitives only (sessions, includes,
   component map, external refs, parser errors, rule violations). Read the
   PARAM.in file directly for intent (control cadence, save-plot meaning,
   session purpose). Authoritative validation is `Scripts/TestParam.pl` from
   the SWMF root, called outside MCP.

## Helper skills allowed

* `swmf-params` — for PARAM.in validation before run
* `swmf-exact-lookup` — for specific script flag confirmation
* `swmf-jobscript` — when a candidate job script is named or a cluster template is needed.
  Call `inspect_artifact(artifact_type="jobscript", path=<file>)` whenever the user
  references a specific job file rather than relying on filename heuristics.

## Outputs

* workflow evidence items from `get_evidence(task_type="run")`
* workflow metadata on returned items:
  * `metadata.kind`
  * `metadata.relative_path`
  * `metadata.why_relevant`
* run directory readiness findings when `inspect_artifact` was called
* PARAM-derived findings — sourced by the agent reading the run-local `PARAM.in`
  directly (not from the param inspector, which is structural-only):
  * session timeline and key commands
  * control settings (`#STOP`, cadence, coupling controls)
  * `#SAVEPLOT` essentials (`StringPlot`, cadence, saved variables)
* DO NOT invent shell commands from heuristic evidence; state affordances only
* if validation has not been done, say so
