---
name: swmf-postproc
type: support
description: "Support skill. Provides deep postprocessing knowledge: IDL visualization, coupling architecture, output artifact inspection. Called by swmf-analyze and swmf-compare."
---

# swmf-postproc (Support)

This is a **support skill**. Entry skills `swmf-analyze` and `swmf-compare`
consult it for IDL visualization, coupling architecture, and output artifacts.

## Purpose

Provide specialized postprocessing knowledge that entry skills need but do not
own directly.

## Scope

* IDL procedure discovery and usage guidance
* IDL snapshot, log, animation, transform, slicing, and graphics-export workflows
* coupling architecture explanation and Mermaid diagrams
* output artifact layout and interpretation context
* `PostProc.pl` and `Restart.pl` command selection and launch-directory guidance
* postprocessing failure triage (before handing off to `swmf-debug`)

Not in scope: general failure diagnosis, PARAM semantics, build/run workflow.

## Immediate Load Rules

If the request mentions IDL plotting, `read_data`, `plot_data`, `plot_func`,
`show_data`, `animate_data`, `plotmode`, `func`, IDL log plotting, graphics
export, or asks to list plotting procedures:
- Read `IDL_VISUALIZATION.md`
- Read `ANSWER_CONTRACTS.md`

If the request mentions coupling, couplers, component relationships, or asks
for a Mermaid diagram:
- Read `COUPLING_ARCHITECTURE.md`
- Read `ANSWER_CONTRACTS.md`

## Tool Protocol

For output inventory:
```bash
swmf inspect --type run_dir --path <run_dir>
```
Call this first for any run-directory or postprocessing task. Treat
`run_dir_layout`, `postproc_state`, `component_artifact_inventory`,
`restart_inventory`, and `component_output_artifacts` as the authority for choosing
artifacts and deciding whether the tree is live, postprocessed, restart-only,
or partial.
Prefer an existing extracted run directory over an archive when both are
present; treat a colocated tarball as a fallback/source archive only.
Run-dir inspection now includes concise PARAM-derived run-intent evidence
(session timeline, control settings, and `#SAVEPLOT` essentials) and should be
used before inferring IDL plotting cadence.
Do not directly read runlogs, `PARAM.in`, or component directories before this
tool evidence unless the result reports missing/unreadable evidence or the user
asks for raw content. Clear runtime failures belong to `swmf-debug`; keep
postprocessing interpretation in this skill.
If deeper runlog investigation is needed, run
`swmf inspect --type runlog --path <runlog>` on a listed runlog.
Never open or parse SWMF output files (`.out`, `.outs`, `.idl`, `.sav`, `.tec`,
`.dat`, etc.) with common command-line tools such as `cat`, `head`, `tail`,
`grep`, or ad hoc Python readers. Use the SWMF/IDL postprocessing scripts and
procedures selected from evidence.

For IDL procedures:
```bash
swmf get-evidence --query <procedure-or-task> --mode keyword --goal "IDL procedure signature and usage"
```
For IDL workflow detail:
```bash
swmf get-evidence --query <func/plotmode/transform/export term> --mode keyword --goal "IDL visualization manual detail"
```
If a run directory or output file is named:
```bash
swmf inspect --type run_dir|result --path <path>
```

Use only the files or procedures named by the swmf CLI result for any direct reads.

For coupling architecture:
```bash
swmf get-context --question <coupling question> --task-type architecture
```
Precision follow-up:
```bash
swmf get-evidence --mode keyword --goal "coupling registry detail"
```
Use only the files or symbols named by the swmf CLI result for any direct reads.

For postprocess failure:
```bash
swmf inspect --type log|run_dir --path ...
```
Do not directly read whole runlogs unless the user explicitly requests raw log
content; after inspection, use only bounded excerpts needed to verify findings.
If conflicting evidence → hand off to `swmf-debug`.

## PostProc.pl and Restart.pl Protocol

Both `PostProc.pl` and `Restart.pl` are copied into an SWMF run directory and
are designed to be executed from that run directory. The correct launch
directory is the live run directory containing `PARAM.in`, copied scripts,
component subdirectories, and restart/output links. Do not run either script
from `RESULTS/<name>/`, a component directory, the SWMF source tree, or
`share/Scripts`.

Before suggesting or running either script:

1. Run `swmf inspect --type run_dir --path <path>`.
2. Use `run_dir_layout` and `status_markers` to identify the live run directory.
3. If the inspected path is `postprocessed_results_tree`, `restart_tree`, or
   `component_dir`, do not treat it as the command cwd. Find the associated live
   run directory from tool evidence or ask for it.
4. Prefer the run-local copied scripts: `./PostProc.pl` and `./Restart.pl`.
   If the script is not present in the live run directory, report that evidence
   and avoid inventing a source-tree command unless the user explicitly asks.

For `PostProc.pl`:

* Basic postprocessing from the live run directory:
  `cd <run_dir> && ./PostProc.pl`
* Repeat mode while the run is active:
  `cd <run_dir> && ./PostProc.pl -r=360 -g >& PostProc.log &`
* Collection mode after or during a run:
  `cd <run_dir> && ./PostProc.pl -M -cat RESULTS/<name>`
* The output `DIR` argument is relative to the live run directory and cannot be
  combined with `-r`. Collection mode can move/copy `PARAM.in`, runlogs,
  component outputs, and restart data into the result tree; original component
  output roots may be empty afterward.

For `Restart.pl`:

* Check restart inputs/outputs without modifying links:
  `cd <run_dir> && ./Restart.pl -c`
* Create a restart tree from current outputs and link input restart paths:
  `cd <run_dir> && ./Restart.pl`
* Create a restart tree without linking input paths:
  `cd <run_dir> && ./Restart.pl -o <restart_tree>`
* Link a new run directory to an existing restart tree:
  `cd <new_run_dir> && ./Restart.pl -i <restart_tree>`
* Repeat restart capture during a live run:
  `cd <run_dir> && ./Restart.pl -o -r=3600 -k=2 -t=date -W >& Restart.log &`

`Restart.pl` links `RESTART.in` and component `restartIN` paths to a restart
tree, and collects `RESTART.out` plus component `restartOUT` contents. It does
not edit `PARAM.in`; restart PARAM changes, such as enabling component restart
or adding includes, remain a separate run-setup step.

## Authority Order

1. Direct tool output tied to source files or runtime artifacts
2. Deterministic IDL catalog evidence returned by `swmf get-evidence`
3. Direct source/doc reads from `share/IDL`, `docs/idl.md`, coupling sources, output artifacts named by the swmf CLI
4. Heuristic source evidence

Never let heuristic search override direct swmf CLI artifact evidence.
For coupling precision follow-up:
```bash
swmf get-evidence --mode keyword --goal "coupling registry detail"
```
Use only the files or symbols named by the swmf CLI result for any direct reads.
