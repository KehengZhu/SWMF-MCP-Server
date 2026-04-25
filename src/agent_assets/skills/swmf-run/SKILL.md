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
   — run directory layout/readiness plus PARAM-derived run intent
   — compact runlog status when logs are present; do not directly read whole
     runlogs unless the user explicitly asks for raw log content
3. `get_evidence(mode="keyword", goal="run environment or job script")`
   — for specific run flags or cluster submission patterns
4. PARAM validation before launch:
   ```
   inspect_artifact(artifact_type="param", path=<PARAM.in>,
                    question="validate structure and component map")
   ```

## Helper skills allowed

* `swmf-params` — for PARAM.in validation before run
* `swmf-exact-lookup` — for specific script flag confirmation

## Outputs

* workflow evidence items from `get_evidence(task_type="run")`
* workflow metadata on returned items:
  * `metadata.kind`
  * `metadata.relative_path`
  * `metadata.why_relevant`
* run directory readiness findings when `inspect_artifact` was called
* PARAM-derived findings from run-dir inspection:
  * session timeline and key commands
  * control settings (`#STOP`, cadence, coupling controls)
  * `#SAVEPLOT` essentials (`StringPlot`, cadence, saved variables)
* DO NOT invent shell commands from heuristic evidence; state affordances only
* if validation has not been done, say so
